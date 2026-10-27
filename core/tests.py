from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

User = get_user_model()


class JoinTests(TestCase):
    def setUp(self):
        self.url = reverse("core:join")

    def test_home_renders_join_form(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Wartally nickname")
        self.assertContains(response, 'placeholder="jtrochim"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertEqual(User.objects.count(), 0)

    def test_regular_submission_creates_user_and_redirects(self):
        response = self.client.post(self.url, {"nickname": "jtrochim"}, follow=True)
        self.assertRedirects(response, f"{reverse('core:home')}?join=1")
        self.assertContains(response, "Thanks for joining, jtrochim!")
        self.assertContains(response, "<!doctype html>")
        user = User.objects.get(username="jtrochim")
        self.assertFalse(user.is_active)
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.client.get(reverse("core:home"))
        self.assertEqual(User.objects.count(), 1)

    def test_htmx_submission_creates_user_and_returns_fragment(self):
        response = self.client.post(
            self.url, {"nickname": "jtrochim"}, HTTP_HX_REQUEST="true"
        )
        self.assertContains(response, "Thanks for joining, jtrochim!")
        self.assertContains(response, "Verification is coming soon.")
        self.assertNotContains(response, "<!doctype html>")
        self.assertIn("HX-Request", response.headers["Vary"])
        self.assertEqual(User.objects.get().username, "jtrochim")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_invalid_nicknames_create_no_users(self):
        for nickname in ("", "   ", "two words", "x" * 151, "<script>x</script>"):
            with self.subTest(nickname=nickname):
                response = self.client.post(
                    self.url, {"nickname": nickname}, HTTP_HX_REQUEST="true"
                )
                self.assertTrue(response.context["form"].errors)
                self.assertContains(response, 'id="join-form"')
                self.assertNotContains(response, "<!doctype html>")
        self.assertEqual(User.objects.count(), 0)

    def test_nickname_is_trimmed_and_normalized(self):
        self.client.post(self.url, {"nickname": "  ｊtrochim  "})
        self.assertEqual(User.objects.get().username, "jtrochim")

    def test_duplicate_does_not_change_or_authenticate_existing_user(self):
        existing = User.objects.create_user(username="jtrochim", password="example")
        for headers in ({}, {"HTTP_HX_REQUEST": "true"}):
            with self.subTest(headers=headers):
                response = self.client.post(
                    self.url, {"nickname": "jtrochim"}, **headers
                )
                self.assertContains(response, "This nickname has already joined.")
        self.assertEqual(User.objects.count(), 1)
        existing.refresh_from_db()
        self.assertTrue(existing.is_active)
        self.assertTrue(existing.check_password("example"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_duplicate_race_returns_validation_error(self):
        def insert_then_validate(form):
            # Simulate a competing insert after the uniqueness check.
            User.objects.create_user(username="jtrochim", is_active=False)
            return "jtrochim"

        with patch(
            "core.forms.JoinForm.clean_nickname",
            autospec=True,
            side_effect=insert_then_validate,
        ):
            response = self.client.post(self.url, {"nickname": "jtrochim"})
        self.assertContains(response, "This nickname has already joined.")
        self.assertEqual(User.objects.count(), 1)

    def test_unrelated_database_error_is_not_hidden(self):
        with patch("core.views.JoinForm.save", side_effect=IntegrityError("failure")):
            with self.assertRaises(IntegrityError):
                self.client.post(self.url, {"nickname": "jtrochim"})

    def test_invalid_user_input_is_escaped(self):
        response = self.client.post(
            self.url,
            {"nickname": "<script>alert(1)</script>"},
            HTTP_HX_REQUEST="true",
        )
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_csrf_required_and_valid_token_accepted(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            self.url, {"nickname": "jtrochim"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.count(), 0)
        client.get(reverse("core:home"))
        response = client.post(
            self.url,
            {
                "nickname": "jtrochim",
                "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Thanks for joining, jtrochim!")
        self.assertEqual(User.objects.count(), 1)

    def test_join_requires_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertEqual(self.client.delete(self.url).status_code, 405)
        self.assertEqual(User.objects.count(), 0)


class SeasonPageTests(SimpleTestCase):
    def test_home_displays_latest_historical_ranking(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Season ranking")
        self.assertContains(response, "Historical standings")
        self.assertEqual(response.context["season"], "2026")
        self.assertEqual(response.context["player_count"], 46)
        self.assertEqual(response.context["event_count"], 7)
        self.assertEqual(len(response.context["ranking_page"]), 20)
        self.assertContains(response, reverse("core:achievements"))

    def test_rank_depends_on_achievements_and_wins_only_order_ties(self):
        response = self.client.get(reverse("core:home"))
        rows = response.context["ranking_page"].paginator.object_list
        scores = [(row["achievement_count"], row["wins"]) for row in rows]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(rows[0]["achievement_count"], 15)
        self.assertEqual([row["rank"] for row in rows[:3]], [1, 2, 2])
        self.assertNotEqual(rows[0]["wins"], rows[1]["wins"])
        rank = 0
        previous = None
        for row in rows:
            score = row["achievement_count"]
            if score != previous:
                rank += 1
            self.assertEqual(row["rank"], rank)
            previous = score

    def test_search_retains_global_rank(self):
        response = self.client.get(reverse("core:home"))
        all_rows = response.context["ranking_page"].paginator.object_list
        expected = next(row for row in all_rows if row["nickname"] == "jtrochim")
        response = self.client.get(reverse("core:home"), {"q": "JTROCHIM"})
        rows = list(response.context["ranking_page"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["rank"], expected["rank"])
        self.assertEqual(rows[0]["achievement_count"], expected["achievement_count"])

    def test_season_selection_and_pagination(self):
        response = self.client.get(
            reverse("core:home"), {"season": "2025", "page": "2"}
        )
        self.assertEqual(response.context["player_count"], 74)
        self.assertEqual(response.context["ranking_page"].number, 2)
        self.assertIn("season=2025", response.context["next_url"])
        self.assertIn("page=3", response.context["next_url"])

    def test_invalid_season_uses_available_season_and_empty_search_is_escaped(self):
        response = self.client.get(
            reverse("core:home"), {"season": "9999", "q": "<script>"}
        )
        self.assertEqual(response.context["season"], "2026")
        self.assertContains(response, "No players match")
        self.assertNotContains(response, "<script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_achievements_page_contains_complete_catalog_and_shared_dialog(self):
        from .achievements import ACHIEVEMENTS

        response = self.client.get(reverse("core:achievements"))
        for badge in ACHIEVEMENTS:
            self.assertContains(response, badge["name"])
        self.assertEqual(
            sum(
                len(group["badges"]) for group in response.context["achievement_groups"]
            ),
            15,
        )
        self.assertContains(response, 'id="join-dialog"')
        self.assertContains(response, 'aria-current="page">Achievements')
        self.assertContains(response, "Byes account for rounds")

    def test_join_fallback_opens_on_achievements_page(self):
        response = self.client.get(reverse("core:achievements"), {"join": "1"})
        self.assertTrue(response.context["join_open"])
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_missing_snapshot_has_honest_empty_state(self):
        with TemporaryDirectory() as directory:
            with override_settings(BASE_DIR=Path(directory)):
                response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["player_count"], 0)
        self.assertContains(response, "Season standings will appear")


class LocalizationTests(TestCase):
    def test_polish_browser_preference_translates_ranking_and_motion_labels(self):
        response = self.client.get(
            reverse("core:home"), HTTP_ACCEPT_LANGUAGE="pl-PL,pl;q=0.9,en;q=0.8"
        )
        self.assertContains(response, '<html lang="pl">')
        self.assertEqual(response.headers["Content-Language"], "pl")
        self.assertContains(response, "Ranking sezonu")
        self.assertContains(response, "Dołącz")
        self.assertContains(response, 'data-play-label="Włącz animacje"')
        self.assertContains(response, 'data-pause-label="Wstrzymaj animacje"')
        self.assertEqual(response.context["player_count"], 46)
        self.assertIn("Accept-Language", response.headers["Vary"])

    def test_polish_achievements_include_translated_names_rules_and_plural_forms(self):
        response = self.client.get(
            reverse("core:achievements"), HTTP_ACCEPT_LANGUAGE="pl"
        )
        self.assertContains(response, "Pierwsza zbiórka")
        self.assertContains(response, "Zahartowany w boju")
        self.assertContains(response, "Ukończ 3 wydarzenia w sezonie.")
        self.assertContains(response, "Pauzy zaliczają rundę")
        self.assertContains(response, "3 osiągnięcia")
        self.assertContains(response, "5 osiągnięć")
        self.assertNotContains(response, "First Muster")

    def test_language_switch_persists_choice_and_preserves_filters(self):
        next_url = reverse("core:home") + "?season=2025&q=jtrochim"
        response = self.client.post(
            reverse("set_language"), {"language": "pl", "next": next_url}, follow=True
        )
        self.assertRedirects(response, next_url)
        self.assertEqual(self.client.cookies["django_language"].value, "pl")
        self.assertContains(response, '<html lang="pl">')
        self.assertEqual(response.context["season"], "2025")
        self.assertEqual(response.context["query"], "jtrochim")
        response = self.client.get(
            reverse("core:achievements"), HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertContains(response, "Pierwsza zbiórka")
        response = self.client.post(
            reverse("set_language"),
            {"language": "en", "next": reverse("core:achievements")},
            follow=True,
        )
        self.assertContains(response, '<html lang="en">')
        self.assertContains(response, "First Muster")

    def test_polish_htmx_validation_confirmation_and_duplicate(self):
        self.client.cookies["django_language"] = "pl"
        url = reverse("core:join")
        response = self.client.post(url, {"nickname": ""}, HTTP_HX_REQUEST="true")
        self.assertContains(response, "To pole jest wymagane.")
        self.assertContains(response, "Pseudonim w Wartally")
        response = self.client.post(
            url, {"nickname": "jtrochim"}, HTTP_HX_REQUEST="true"
        )
        self.assertContains(response, "Dzięki za dołączenie, jtrochim!")
        self.assertNotContains(response, "Thanks for joining")
        response = self.client.post(
            url, {"nickname": "jtrochim"}, HTTP_HX_REQUEST="true"
        )
        self.assertContains(response, "Ten pseudonim jest już zarejestrowany.")
        self.assertEqual(User.objects.count(), 1)

    def test_polish_integer_plural_forms(self):
        from django.utils.translation import ngettext, override

        with override("pl"):
            for count, expected in (
                (1, "1 osiągnięcie"),
                (3, "3 osiągnięcia"),
                (5, "5 osiągnięć"),
                (12, "12 osiągnięć"),
                (22, "22 osiągnięcia"),
            ):
                with self.subTest(count=count):
                    actual = ngettext(
                        "%(count)s achievement", "%(count)s achievements", count
                    ) % {"count": count}
                    self.assertEqual(actual, expected)


class PlayerDetailTests(SimpleTestCase):
    def test_profile_lists_every_badge_and_matches_the_ranking(self):
        from .achievements import ACHIEVEMENTS

        response = self.client.get(reverse("core:home"), {"q": "Mateusz Górecki"})
        expected = list(response.context["ranking_page"])[0]
        url = reverse("core:player_detail", kwargs={"nickname": "Mateusz Górecki"})
        self.assertContains(response, url + "?season=2026")
        response = self.client.get(url, {"season": "2026"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["player"]["rank"], expected["rank"])
        groups = response.context["achievement_groups"]
        badges = [badge for group in groups for badge in group["badges"]]
        self.assertEqual(len(badges), 15)
        self.assertEqual(
            sum(b["unlocked"] for b in badges), expected["achievement_count"]
        )
        for badge in ACHIEVEMENTS:
            self.assertContains(response, badge["name"])
        for badge in badges:
            self.assertLessEqual(badge["progress"], badge["threshold"])
            self.assertEqual(badge["unlocked"], badge["progress"] == badge["threshold"])
        self.assertContains(response, "badge-earned")
        self.assertContains(response, "badge-locked")
        self.assertContains(response, 'id="join-dialog"')
        self.assertContains(response, "not verified account awards")

    def test_profile_season_changes_progress(self):
        url = reverse("core:player_detail", kwargs={"nickname": "jtrochim"})
        latest = self.client.get(url, {"season": "2026"})
        older = self.client.get(url, {"season": "2025"})
        self.assertEqual(older.context["season"], "2025")
        self.assertNotEqual(
            latest.context["player"]["wins"], older.context["player"]["wins"]
        )

    def test_previous_season_player_gets_empty_state_for_valid_unplayed_season(self):
        from .rankings import get_snapshot

        dataset = get_snapshot()
        latest = {
            p["nickname"]
            for e in dataset["events"]
            if e["date"].startswith("2026")
            for p in e["participants"]
            if p["played"]
        }
        old = {
            p["nickname"]
            for e in dataset["events"]
            if e["date"].startswith("2025")
            for p in e["participants"]
            if p["played"]
        }
        nickname = sorted(old - latest)[0]
        url = reverse("core:player_detail", kwargs={"nickname": nickname})
        response = self.client.get(url)
        self.assertEqual(response.context["season"], "2025")
        response = self.client.get(url, {"season": "2026"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No recorded events for this player")
        self.assertEqual(response.context["player"]["achievement_count"], 0)
        self.assertIsNone(response.context["player"]["rank"])
        self.assertEqual(
            sum(
                len(group["badges"]) for group in response.context["achievement_groups"]
            ),
            15,
        )

    def test_unicode_player_and_unknown_player(self):
        url = reverse("core:player_detail", kwargs={"nickname": 'Michał "Bułka"'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Michał &quot;Bułka&quot;")
        response = self.client.get(
            reverse("core:player_detail", kwargs={"nickname": "missing-player-12345"})
        )
        self.assertEqual(response.status_code, 404)

    def test_polish_profile_and_language_switch_keep_player_and_season(self):
        url = reverse("core:player_detail", kwargs={"nickname": "jtrochim"})
        next_url = url + "?season=2025"
        response = self.client.post(
            reverse("set_language"), {"language": "pl", "next": next_url}, follow=True
        )
        self.assertRedirects(response, next_url)
        self.assertContains(response, "Kronika gracza")
        self.assertContains(response, "Pierwsza zbiórka")
        self.assertContains(response, "Zdobyte")
        self.assertContains(response, "Postęp")
        self.assertContains(response, 'lang="pl"')
        self.assertEqual(response.context["player"]["nickname"], "jtrochim")
        self.assertEqual(response.context["season"], "2025")

    def test_full_badge_collection_has_no_locked_badges(self):
        response = self.client.get(reverse("core:home"))
        nickname = next(
            row["nickname"]
            for row in response.context["ranking_page"].paginator.object_list
            if row["achievement_count"] == 15
        )
        response = self.client.get(
            reverse("core:player_detail", kwargs={"nickname": nickname})
        )
        self.assertEqual(response.context["player"]["achievement_count"], 15)
        self.assertNotContains(response, "badge-locked")


class BadgeArtworkTests(SimpleTestCase):
    def test_every_achievement_has_a_distinct_webp_asset(self):
        import hashlib

        from django.contrib.staticfiles import finders

        from .achievements import ACHIEVEMENTS

        hashes = set()
        for badge in ACHIEVEMENTS:
            with self.subTest(badge=badge["key"]):
                path = finders.find(badge["image"])
                self.assertIsNotNone(path, badge["image"])
                contents = Path(path).read_bytes()
                self.assertEqual(contents[:4], b"RIFF")
                self.assertEqual(contents[8:12], b"WEBP")
                hashes.add(hashlib.sha256(contents).hexdigest())
        self.assertEqual(len(hashes), 15)

    def test_catalog_and_player_profile_render_the_badge_artwork(self):
        from .achievements import ACHIEVEMENTS

        urls = [
            reverse("core:achievements"),
            reverse("core:player_detail", kwargs={"nickname": "jtrochim"}),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                for badge in ACHIEVEMENTS:
                    self.assertContains(response, "/static/" + badge["image"])
                self.assertContains(response, 'alt="" width="160" height="160"')
                self.assertContains(response, 'loading="lazy"')


class TrophyPageTests(SimpleTestCase):
    def test_current_trophy_uses_supplied_image_and_full_collection_requirement(self):
        from django.contrib.staticfiles import finders

        response = self.client.get(reverse("core:trophies"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["trophy_year"], 2026)
        self.assertEqual(response.context["achievement_total"], 15)
        self.assertContains(response, "/static/images/trophies/season-2026.webp")
        self.assertIsNotNone(finders.find("images/trophies/season-2026.webp"))
        self.assertContains(
            response, "Collect all 15 achievements during the 2026 season"
        )
        self.assertContains(response, "eligible to earn a physical copy")
        self.assertContains(response, 'aria-current="page">Trophies')
        self.assertContains(response, 'id="join-dialog"')
        self.assertContains(response, reverse("core:achievements"))

    def test_trophy_page_is_translated_into_polish(self):
        response = self.client.get(reverse("core:trophies"), HTTP_ACCEPT_LANGUAGE="pl")
        self.assertContains(response, '<html lang="pl">')
        self.assertContains(response, "Trofeum sezonu 2026")
        self.assertContains(response, "wszystkie 15 osiągnięć")
        self.assertContains(response, "fizycznego egzemplarza tego trofeum")
        self.assertContains(response, 'aria-current="page">Trofea')
        self.assertNotContains(response, "Collect all")


class RankingTrophyEmblemTests(SimpleTestCase):
    def test_complete_collection_has_trophy_emblem_but_partial_collection_does_not(
        self,
    ):
        response = self.client.get(
            reverse("core:home"), {"season": "2026", "q": "Pan Tulipan"}
        )
        self.assertContains(response, 'class="trophy-emblem"', count=1)
        self.assertContains(response, "eligible for the season trophy")
        self.assertContains(response, 'href="/trophies/" title=')
        response = self.client.get(
            reverse("core:home"), {"season": "2026", "q": "xyzq"}
        )
        self.assertEqual(
            list(response.context["ranking_page"])[0]["achievement_count"], 14
        )
        self.assertNotContains(response, 'class="trophy-emblem"')

    def test_trophy_emblem_label_is_translated(self):
        response = self.client.get(
            reverse("core:home"), {"q": "Pan Tulipan"}, HTTP_ACCEPT_LANGUAGE="pl"
        )
        self.assertContains(
            response, "Wszystkie osiągnięcia zdobyte — prawo do trofeum sezonu"
        )
