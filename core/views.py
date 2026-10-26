from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.vary import vary_on_headers

from .achievements import ACHIEVEMENTS, GROUPS
from .forms import DUPLICATE_NICKNAME, JoinForm
from .rankings import get_snapshot, historical_ranking


def ranking_context(request):
    context = historical_ranking(request)
    query = request.GET.get("q", "").strip()[:100]
    rows = context.pop("ranking")
    if query:
        rows = [row for row in rows if query.casefold() in row["nickname"].casefold()]
    page_size = max(len(rows), 1) if getattr(request, "static_export", False) else 20
    page = Paginator(rows, page_size).get_page(request.GET.get("page"))
    params = {"season": context["season"], "q": query}
    context.update(
        {
            "query": query,
            "ranking_page": page,
            "achievement_total": len(ACHIEVEMENTS),
            "previous_url": "?"
            + urlencode({**params, "page": page.previous_page_number()})
            if page.has_previous()
            else None,
            "next_url": "?" + urlencode({**params, "page": page.next_page_number()})
            if page.has_next()
            else None,
        }
    )
    return context


@require_GET
def home(request):
    return render(
        request,
        "core/home.html",
        {
            **ranking_context(request),
            "form": JoinForm(),
            "join_open": request.GET.get("join") == "1",
            "active_page": "ranking",
        },
    )


def achievement_groups(player=None):
    groups = []
    for key, name, description in GROUPS:
        badges = []
        for badge in ACHIEVEMENTS:
            if badge["group"] != key:
                continue
            if player is None:
                badges.append(badge)
            else:
                current = min(int(player[badge["metric"]]), badge["threshold"])
                badges.append(
                    {
                        **badge,
                        "progress": current,
                        "unlocked": current >= badge["threshold"],
                    }
                )
        groups.append(
            {
                "key": key,
                "name": name,
                "description": description,
                "badges": badges,
                "unlocked_count": sum(badge.get("unlocked", False) for badge in badges),
            }
        )
    return groups


@require_GET
def player_detail(request, nickname):
    dataset = get_snapshot()
    player_years = sorted(
        {
            event["date"][:4]
            for event in dataset["events"]
            if event["status"] == "Finished"
            and event["participants"] is not None
            and any(
                p["nickname"] == nickname and p["played"] for p in event["participants"]
            )
        },
        reverse=True,
    )
    if not player_years:
        raise Http404(_("Player not found."))
    requested = request.GET.get("season")
    available = {event["date"][:4] for event in dataset["events"]}
    season = requested if requested in available else player_years[0]
    context = historical_ranking(request, requested_season=season)
    player = next(
        (row for row in context.pop("ranking") if row["nickname"] == nickname), None
    )
    if player is None:
        player = {
            "nickname": nickname,
            "rank": None,
            "achievement_count": 0,
            "earned": [],
            **{badge["metric"]: 0 for badge in ACHIEVEMENTS},
            "matches": 0,
        }
    return render(
        request,
        "core/player_detail.html",
        {
            **context,
            "player": player,
            "achievement_groups": achievement_groups(player),
            "achievement_total": len(ACHIEVEMENTS),
            "form": JoinForm(),
            "join_open": request.GET.get("join") == "1",
            "active_page": "ranking",
        },
    )


@require_GET
def achievements(request):
    return render(
        request,
        "core/achievements.html",
        {
            "achievement_groups": achievement_groups(),
            "achievement_total": len(ACHIEVEMENTS),
            "form": JoinForm(),
            "join_open": request.GET.get("join") == "1",
            "active_page": "achievements",
        },
    )


@require_GET
def trophies(request):
    return render(
        request,
        "core/trophies.html",
        {
            "trophy_year": 2026,
            "achievement_total": len(ACHIEVEMENTS),
            "form": JoinForm(),
            "join_open": request.GET.get("join") == "1",
            "active_page": "trophies",
        },
    )


@require_POST
@vary_on_headers("HX-Request")
def join(request):
    form = JoinForm(request.POST)
    confirmation = None
    if form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()
        except IntegrityError:
            # The unique constraint also protects simultaneous submissions.
            if (
                not get_user_model()
                .objects.filter(username=form.cleaned_data["nickname"])
                .exists()
            ):
                raise
            form.add_error("nickname", DUPLICATE_NICKNAME)
        else:
            confirmation = _(
                "Thanks for joining, %(nickname)s! "
                "Your account has been created. Verification is coming soon."
            ) % {"nickname": user.username}
            if request.headers.get("HX-Request") != "true":
                messages.success(request, confirmation)
                return redirect(f"{reverse('core:home')}?join=1")
            form = JoinForm()

    template = (
        "core/partials/join.html"
        if request.headers.get("HX-Request") == "true"
        else "core/home.html"
    )
    return render(
        request,
        template,
        {
            **(ranking_context(request) if template == "core/home.html" else {}),
            "form": form,
            "confirmation": confirmation,
            "join_open": True,
            "active_page": "ranking",
        },
    )
