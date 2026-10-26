# Repository Guidelines

## Project Structure & Module Organization

Warble uses Python 3.12+, Django 5.2, SQLite, Django templates, and HTMX 2. No frontend build step is required.

- `config/`: settings, root URLs, WSGI/ASGI entry points.
- `core/`: forms, views, app routes, and `tests.py`.
- `templates/base.html`: shared shell; `templates/core/partials/`: HTMX fragments.
- `static/`: CSS, JavaScript, and optimized WebP artwork.
- `docs/art-direction.md`: visual direction, asset details, and generation prompt.

## Build, Test, and Development Commands

- `uv sync`: install locked runtime and development dependencies.
- `uv run python manage.py migrate`: initialize or update the local database.
- `uv run python manage.py runserver`: start the development server.
- `uv run python manage.py check`: validate Django configuration.
- `uv run python manage.py test`: run Django tests.
- `uv run ruff check .` and `uv run ruff format .`: lint and format Python.
- `uv run python manage.py collectstatic --noinput`: collect deployment assets.
- `uv run python manage.py export_static`: build `_site/` for GitHub Pages.

## Coding Style & Naming Conventions

Use four-space Python indentation, snake_case functions, PascalCase classes, and Ruff’s 88-character line limit. Keep templates server-rendered and JavaScript small and framework-free. Preserve full-page form submission alongside HTMX fragment responses, including CSRF protection and `Vary: HX-Request` where responses differ.

## Join Flow

The top-right Join control is currently disabled; the native dialog flow remains implemented. `POST /join/` stores a validated Wartally nickname as the Django username. New users are inactive with unusable passwords; joining does not authenticate them. Verification is deferred. Preserve duplicate handling, including database uniqueness races, and the non-JavaScript redirect flow.

## Visual Direction & Accessibility

Use a Warcry-inspired aesthetic: ruined fortresses, charcoal, rust, aged brass, smoke, and embers. Retain system sans-serif fonts and the text-only `warble` wordmark. Serve artwork locally as optimized WebP. Preserve mobile layouts, keyboard focus, Escape dismissal, motion controls, and reduced-motion support.

## Testing Guidelines

Use Django `TestCase` and `test_*` methods in app test modules. Cover account creation, validation, duplicates, escaping, CSRF, and HTMX/full-page behavior. No coverage threshold is configured. Check visible changes at desktop and mobile sizes when browser preview is available; report verification limits.

## Static Export

Preserve `export_static` support for both languages, all seasons, and player profiles. Use relative links for GitHub Pages project paths. Static search runs in the browser; omit POST forms and database access. Rebuild `_site/` after changes; never edit generated files. `.github/workflows/pages.yml` publishes from `main`.

## Commits, Pull Requests & Configuration

No Git history is available here. Use focused, imperative commit subjects. PRs should describe behavior, verification, relevant issues, and screenshots for visual changes.

Commit `uv.lock`; exclude credentials, `.env`, and local databases. `.env.example` is documentation, not automatically loaded. Deployment requires `DJANGO_DEBUG=false`, a unique `DJANGO_SECRET_KEY`, configured `DJANGO_ALLOWED_HOSTS`, and HTTPS.
