"""Check the actual artifact, including links beneath a project-site prefix."""

from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

from django.core.management import call_command
from django.test import SimpleTestCase

from core.management.commands.export_static import page_path, player_slug


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src", "data-fire-source"} and value:
                self.links.append(value)


class StaticExportTests(SimpleTestCase):
    def test_export_is_database_free_and_all_local_links_resolve(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            call_command("export_static", output=str(root), stdout=StringIO())
            self.assertTrue((root / ".nojekyll").exists())
            polish = (root / "index.html").read_text()
            self.assertIn('<html lang="pl">', polish)
            self.assertIn("data-static-search", polish)
            self.assertNotIn("csrfmiddlewaretoken", polish)
            self.assertNotIn('id="join-dialog"', polish)
            self.assertNotIn('method="post"', polish)
            self.assertEqual(polish.count('class="player-name player-link"'), 46)
            english = (root / "en/index.html").read_text()
            self.assertIn('<html lang="en">', english)
            self.assertIn("pl/players/", polish)
            self.assertTrue((root / "pl/seasons/2025/index.html").exists())
            self.assertTrue((root / "pl/achievements/index.html").exists())
            self.assertTrue((root / "pl/trophies/index.html").exists())
            profile = root / f'pl/players/{player_slug("jtrochim")}/2026/index.html'
            self.assertTrue(profile.exists())
            self.assertIn("../../../../en/players/", profile.read_text())
            for page in root.rglob("*.html"):
                parser = LinkCollector()
                parser.feed(page.read_text())
                for link in parser.links:
                    url = urlsplit(link)
                    if url.scheme or url.netloc or link.startswith("#"):
                        continue
                    self.assertFalse(link.startswith("/"), (page, link))
                    target = (page.parent / unquote(url.path)).resolve()
                    self.assertTrue(target.is_relative_to(root), (page, link))
                    if target.is_dir():
                        target /= "index.html"
                    self.assertTrue(target.is_file(), (page, link))

    def test_profile_paths_handle_special_characters_and_case(self):
        nickname = "Żółć/a?b#c/"
        path = page_path(
            "pl", "/players/%C5%BB%C3%B3%C5%82%C4%87%2Fa%3Fb%23c%2F/", "2026", "2026"
        )
        self.assertEqual(path, f"pl/players/{player_slug(nickname)}/2026/index.html")
        self.assertNotEqual(player_slug("Player"), player_slug("player"))
