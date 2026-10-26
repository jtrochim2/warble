"""Render the public site without a running Django server or database."""

import hashlib
import html
import json
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import RequestFactory, override_settings
from django.utils import translation

from core import views
from core.achievements import evaluate_season
from core.rankings import get_snapshot


def player_slug(nickname):
    # Stable, filesystem-safe IDs also handle slashes and case-only differences.
    return hashlib.sha256(nickname.encode()).hexdigest()[:20]


def page_path(language, path, season, latest):
    if path.startswith("/players/"):
        nickname = unquote(path[len("/players/") : -1])
        return f"{language}/players/{player_slug(nickname)}/{season}/index.html"
    if path == "/":
        suffix = "" if season == latest else f"seasons/{season}/"
        return f"{language}/{suffix}index.html"
    return f'{language}/{path.strip("/")}/index.html'


def rewrite_links(document, output_path, language, season, latest):
    parent = posixpath.dirname(output_path) or "."

    def replace(match):
        attribute, quote, value = match.groups()
        value = html.unescape(value)
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or value.startswith("#"):
            return match.group(0)
        if parsed.path.startswith("/static/"):
            target = parsed.path.lstrip("/")
        elif parsed.path.startswith("/__language__/"):
            lang = parsed.path.split("/")[2]
            source = parsed.path.split("/", 3)[3]
            target = page_path(lang, "/" + source, season, latest)
        elif parsed.path.startswith("/") or value.startswith("?"):
            path = parsed.path or ("/" if "/players/" not in output_path else "")
            if not path:
                raise CommandError("A player season link needs its source path.")
            year = parse_qs(parsed.query).get("season", [season])[0]
            target = page_path(language, path, year, latest)
        else:
            return match.group(0)
        relative = posixpath.relpath(target, parent)
        # Directory URLs work on GitHub Pages and a local HTTP server.
        if relative.endswith("index.html"):
            relative = relative[:-10] or "./"
        if parsed.fragment:
            relative += "#" + parsed.fragment
        return f"{attribute}={quote}{html.escape(relative, quote=True)}{quote}"

    return re.sub(r'(href|src|data-fire-source)=("|\')([^"\']*)\2', replace, document)


class Command(BaseCommand):
    help = "Export all public pages, both languages and seasons, to GitHub Pages."

    def add_arguments(self, parser):
        parser.add_argument("--output", default="_site")

    def handle(self, *args, **options):
        output = Path(options["output"]).resolve()
        # Never clear a directory supplied by the caller. Copy over generated files.
        if output == settings.BASE_DIR or settings.BASE_DIR.is_relative_to(output):
            raise CommandError("Output must be a separate build directory.")
        manifest = output / ".warble-export.json"
        if output.exists() and any(output.iterdir()) and not manifest.is_file():
            raise CommandError("Output is not empty and is not a Warble export.")
        previous = json.loads(manifest.read_text()) if manifest.exists() else []
        dataset = get_snapshot()
        years = sorted({event["date"][:4] for event in dataset["events"]}, reverse=True)
        if not years:
            raise CommandError("No tournament snapshot found; cannot export rankings.")
        latest = years[0]
        nicknames = sorted(
            {
                row["nickname"]
                for year in years
                for row in evaluate_season(dataset, year)
            }
        )
        output.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            settings.BASE_DIR / "static", output / "static", dirs_exist_ok=True
        )
        factory = RequestFactory()
        count = 0
        generated = []
        with override_settings(STATIC_URL="/static/"):
            for language, _ in settings.LANGUAGES:
                pages = [("/", latest, views.home, {})]
                pages += [
                    ("/", year, views.home, {}) for year in years if year != latest
                ]
                pages += [
                    ("/achievements/", latest, views.achievements, {}),
                    ("/trophies/", latest, views.trophies, {}),
                ]
                for nickname in nicknames:
                    for year in years:
                        pages.append(
                            (
                                f'/players/{quote(nickname, safe="")}/',
                                year,
                                views.player_detail,
                                {"nickname": nickname},
                            )
                        )
                for path, year, view, kwargs in pages:
                    request = factory.get(path, {"season": year})
                    request.LANGUAGE_CODE = language
                    request.static_export = True
                    request.static_source_path = path
                    # Season links normally use a query-only URL. Give the rewriter
                    # the original path explicitly, including unusual nicknames.
                    with translation.override(language):
                        document = view(request, **kwargs).content.decode()
                    document = document.replace(
                        'href="?season=', f'href="{html.escape(path)}?season='
                    )
                    target = page_path(language, path, year, latest)
                    rendered = rewrite_links(document, target, language, year, latest)
                    destination = output / target
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(rendered)
                    generated.append(target)
                    count += 1
                    if language == "pl" and path == "/" and year == latest:
                        (output / "index.html").write_text(
                            rewrite_links(
                                document, "index.html", language, year, latest
                            )
                        )
                        generated.append("index.html")
        # Remove only obsolete pages listed in our previous export manifest.
        for stale in set(previous) - set(generated):
            path = (output / stale).resolve()
            if path.is_relative_to(output) and path.is_file():
                path.unlink()
        manifest.write_text(json.dumps(generated, indent=2))
        (output / ".nojekyll").touch()
        self.stdout.write(self.style.SUCCESS(f"Exported {count + 1} pages to {output}"))
