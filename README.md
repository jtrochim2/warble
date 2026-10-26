# Warble

A Django 5.2 project with Django templates, SQLite, and HTMX 2. No Node.js or frontend build step is required.

## Quick start

Install Python 3.12+ and [uv](https://docs.astral.sh/uv/), then run:

```sh
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Open http://127.0.0.1:8000/ for the season ranking. Visit `/achievements/` for the 14 badge requirements and counting rules. The top-right **Join with Wartally** button is currently disabled. The Django join endpoint and dialog remain implemented for future activation. Enter a Wartally nickname (for example, `jtrochim`) and submit to create a Django user. Close the dialog with Escape, the close button, or a click on the backdrop. HTMX updates the form in place; without JavaScript, a successful submission redirects to the home page with the dialog open so refreshing does not resubmit it. Values are validated by a Django form, escaped by the template engine, and protected by Django CSRF middleware.

HTMX is loaded from a version-pinned CDN URL with subresource integrity, following the [HTMX installation documentation](https://htmx.org/docs/). An internet connection is required for the enhanced interaction; the standard form works without it.

## Static hosting on GitHub Pages

Generate the complete static site without starting Django or migrating a database:

```sh
uv run python manage.py export_static
python3 -m http.server 8000 --directory _site
```

Open `http://localhost:8000/`. The `_site/` directory contains the Polish landing page,
`pl/` and `en/` versions, both seasonal rankings, every player profile for each
season, achievements, trophies, and local CSS/JavaScript/artwork. Relative links
support both `username.github.io` and `username.github.io/warble/` without a base-path
setting. Use an HTTP server for preview rather than opening HTML as `file://`.

Static rankings include every player in the season, with instant browser search
instead of server pagination. Season buttons retain HTMX navigation and the existing
scroll behavior. Language links preserve the page and season. Animations and motion
controls remain active. Joining stays disabled; no accounts, admin, Celery, or other
server endpoints are exported. Results change only after updating the snapshot and
rebuilding. The Wartally logo and optional HTMX enhancement still use external URLs.

The workflow in `.github/workflows/pages.yml` builds and publishes on pushes to
`main`, or manually from Actions. In the GitHub repository, select **Settings → Pages
→ Build and deployment → Source → GitHub Actions**. If your default branch has a
different name, update the workflow trigger. No Django hosting or database is needed.
GitHub Pages must be available for your repository/account plan.

The exporter also accepts `--output /path/to/build`. Use an empty directory; later
builds recognize their export manifest and remove obsolete generated pages. Never
edit generated HTML directly. `_site/` is ignored by Git; the workflow rebuilds it
from templates, translations, artwork, and `data/wartally/poland-2025-2026.json`.

## Languages

Polish and English are available through the **PL / EN** buttons in the header. The browser's preferred language is detected initially; an explicit choice is saved in Django's language cookie. Switching languages preserves the current page, season, and search. URLs remain unchanged.

Translations cover navigation, the ranking, achievement names and rules, the join form, validation, confirmation messages, and motion controls. Wartally nicknames and source records retain their original spelling. English remains the fallback language.

The Polish gettext catalog is in `locale/pl/LC_MESSAGES/django.po`; its compiled `.mo` file is included for runtime use. After editing translatable strings or the catalog, run:

```sh
uv run python manage.py makemessages -l pl --ignore=.venv --ignore=data
uv run python manage.py compilemessages -l pl --ignore=.venv
```

These maintenance commands require GNU gettext. Catalog labels in `core/achievements.py` are marked for extraction and translated in templates, keeping the research evaluator independent of Django.

## Ranking and achievements

The landing page ranks historical players by achievements earned, with shared places for equal achievement totals (1, 1, 2). Wins determine display order within each shared rank, followed by alphabetical order; neither changes the rank. Switch immediately with the styled 2025 / 2026 season buttons, search a nickname, or browse the paginated results. Season changes use HTMX to update the main content without a full-page reload, preserve scroll position and the submitted search, and reset pagination. The URL and Back/Forward history track the chosen year. Without HTMX, the same links navigate normally. Ranking positions remain global when searching.

`core/achievements.py` is the shared catalog and evaluator used by both the website and the backtest. `core/rankings.py` reads the local research snapshot, with a cache that refreshes when the file changes. Missing research data produces an empty state. The page labels the snapshot as historical and unverified; it does not create account awards or automatically confirm trophy eligibility.

Click a player nickname in the ranking to open `/players/<nickname>/`. The player chronicle shows all 14 badges, earned and unearned states, per-badge progress, seasonal statistics, and matching year buttons for immediate season changes without reloading the page. Players absent from the selected year have an empty collection for that year; unknown nicknames return 404. Profiles share the historical preview and pending-verification status of the ranking.

The Join dialog is shared across the ranking, achievements, and player pages. The artwork, motion control, and reduced-motion behavior remain available throughout the site.

## Trophies

`/trophies/` showcases the 2026 season trophy using the supplied `trophy.png`. The original is preserved; `static/images/trophies/season-2026.webp` is the optimized web asset. Collecting all 14 achievements during the 2026 season makes a player eligible to earn a physical copy, subject to account-ownership and achievement verification. The page supports Polish and English and links to the achievement catalog and 2026 ranking. It does not initiate trophy fulfillment or guarantee delivery.

## Joining and verification

`POST /join/` stores the nickname as the standard Django user's unique `username`. Nicknames are trimmed, Unicode-normalized, and validated with Django's username rules (up to 150 characters). Case is preserved and uniqueness follows Django's case-sensitive username behavior. Duplicate submissions display a validation error and never sign in an existing user.

New accounts have `is_active=False` and an unusable password, following [Django's authentication model](https://docs.djangoproject.com/en/5.2/ref/contrib/auth/). Joining does not authenticate the visitor or verify Wartally ownership. Verification is intentionally deferred; a future flow can verify ownership before activating accounts. Users can be inspected in `/admin/`.

## Visual design

Each achievement has a unique original illustrated trophy in `static/images/badges/`, with iron, bone, brass, and dark red details. The catalog shows full-color artwork; player collections subdue unearned badges in grayscale. The shared card keeps translated names, requirements, and explicit earned states alongside the artwork. See [badge designs and generation prompts](docs/badges.md).

The landing page features original Warcry-inspired ruined-fortress artwork, a stationary background illustration, layered drifting smoke, embers, and flickering fire on the two foreground braziers. The fire overlays stay aligned as the background scales and share the pause and reduced-motion controls. Pause the atmosphere using the footer control; OS reduced-motion settings disable animation automatically. Artwork is served locally as an optimized WebP; typography uses system fonts. See [art direction and generation prompt](docs/art-direction.md) for asset details.

## Layout

- `config/`: settings, root URLs, WSGI and ASGI entry points.
- `core/`: home view, form, routes, and Django tests.
- `templates/base.html`: shared page shell and HTMX script.
- `templates/core/partials/`: HTML fragments for HTMX responses.
- `static/css/`: application styles.
- `static/js/join.js`: native dialog open/close behavior and keyboard focus.
- `static/js/atmosphere.js`: embers and the persistent motion control.
- `static/images/`: optimized fantasy landscape artwork.

## Development commands

```sh
uv run python manage.py check            # Django configuration checks
uv run python manage.py test             # Rendering, validation, CSRF, escaping
uv run ruff check .                      # Python linting
uv run ruff format .                     # Python formatting
uv run python manage.py createsuperuser  # Optional admin user (after migrate)
```

The admin is available at `/admin/`. Keep Python code formatted with Ruff, use four-space indentation and snake_case names, and add behavior tests to `core/tests.py` or the relevant app. No coverage threshold is configured.

## Configuration

Local defaults use SQLite and enable debug mode. `.env.example` lists available settings; it is a reference file and is not automatically loaded. Export variables in your shell or configure them through your process manager.

For deployment, set `DJANGO_DEBUG=false`, a unique `DJANGO_SECRET_KEY`, and comma-separated `DJANGO_ALLOWED_HOSTS`. The application refuses to start without a secret when debug is disabled; secure session and CSRF cookies require HTTPS. Configure an appropriate WSGI/ASGI server, HTTPS/proxy settings, database, and static file serving for your environment. `runserver` is for development.

```sh
uv run python manage.py collectstatic --noinput
uv run python manage.py check --deploy
```

Commit `uv.lock` to make installations reproducible. Do not commit `.env`, local databases, or credentials.

## Tournament research

Downloaded public Wartally JSON snapshots and normalized Polish event results are in `data/wartally/`. See the [historical analysis](docs/poland-warcry-2025-2026.md) and [achievement proposal](docs/achievement-system.md).

```sh
python3 scripts/fetch_wartally.py
python3 scripts/normalize_wartally.py
python3 scripts/analyze_wartally.py
python3 scripts/backtest_achievements.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The research pipeline is separate from application accounts and does not award achievements or create prize entries.
