# zix: Keeping the indie app development simple, fast, and tidy

Build a mobile friendly web app.
Battery included: Wiring signups, feature subscriptions, and payment.

- FastAPI (API backend)
- fastapi-sso (Authentication — Google, GitHub, LinkedIn, or Auth0)
- Stripe (Payment)
- SendGrid (Email)

## Introduction

I wanted to build a web app with frontend, backend, database, login,
email services, and paywall very quickly.

Since those are common skeleton for most SaaS apps, I built a plugin
framework to build apps quickly.

## Design philosophy

### Plugin architecture

Each feature lives in its own directory under `app/plugins/` and owns its
`models`, `schemas`, `crud`, and `routers` — keeping concerns separated and
making it easy to add, remove, or disable features without touching unrelated
code.

Plugins are discovered automatically at boot time: any subdirectory with an
`__init__.py` is imported. To disable a plugin without deleting it, drop a
`.zixignore` file inside it.

**Performance:** plugin discovery and import happens once at server startup.
Python caches every imported module in `sys.modules`, so there is no
per-request import overhead. Adding more plugins does not affect runtime
performance.

**Cross-plugin dependencies** (e.g. `auth` importing from `users`) are
explicit — you reference the plugin by name. Keep these dependencies
minimal and one-directional to avoid tight coupling.

## Prerequisites

- A supported Python version (see [Python release schedule](https://devguide.python.org/versions/))
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

## Install

Create a project directory and set up a Python environment with uv:

```bash
pip install uv
mkdir zix_projects
cd zix_projects
uv init
```

Install zix:

```bash
uv add zixweb
```

## Create an app

**Important:** run `zix init` from the project root (e.g. `zix_projects/`), not from inside the app folder.

```bash
echo "y" | uv run zix init -w myapp
```

> The CLI prompts for confirmation on stdin. Pipe `echo "y"` to avoid an `EOFError` in non-interactive shells.

## Set up the database

Navigate to the project root and run Alembic to create the schema before starting the server for the first time. Skipping this causes a 500 error on every request because the auth middleware queries the `token` table before it exists.

```bash
cd myapp
uv run alembic revision --autogenerate -m "initial"
uv run alembic upgrade head
cd ..
```

## Compile frontend assets

The `app/static/compiled/` directory is empty until you run the compile script. The server will fail to start without it.

```bash
cd myapp
bash bin/compile
cd ..
```

> `bin/compile` also copies `app/static/assets/js/_config.js` to `compiled/assets/js/config.js`. The Bootstrap Studio export includes an empty `config.js` placeholder — without this copy step the browser throws `Uncaught ReferenceError: Config is not defined`.

## Configure environment

Copy the env template and fill in your credentials:

```bash
mkdir -p myapp/.env
cp myapp/env.yml myapp/.env/env.yml
```

Open `myapp/.env/env.yml` and configure the auth backend (see [Authentication](#authentication) below).

## Run the app

**Important:** always run the server from the project root (e.g. `zix_projects/`), not from inside `myapp/`. Running from inside the app directory causes `ModuleNotFoundError: No module named 'config'`.

```bash
uv run zix serve -w myapp -p 4000
```

Point your browser to `http://localhost:4000`.

---

## Authentication

By default zix uses **fastapi-sso** (open source, no external account required) with Google SSO enabled. You can switch to Auth0 if you prefer a managed identity service.

### fastapi-sso (default)

[fastapi-sso](https://github.com/tomasvotava/fastapi-sso) provides OAuth2 login via Google, GitHub, and LinkedIn without running a separate identity server.

**Supported providers and toggle flags** in `env.yml`:

| Provider | Toggle flag | Default |
|----------|-------------|---------|
| Google | `USE_GOOGLE_SSO` | `"true"` |
| GitHub | `USE_GITHUB_SSO` | `"false"` |
| LinkedIn | `USE_LINKEDIN_SSO` | `"false"` |

Each provider requires its own OAuth app credentials. Example `env.yml` section:

```yaml
local:
  USE_AUTH0: "false"

  USE_GOOGLE_SSO: "true"
  GOOGLE_CLIENT_ID: "your-client-id.apps.googleusercontent.com"
  GOOGLE_CLIENT_SECRET: "your-client-secret"

  USE_GITHUB_SSO: "false"
  GITHUB_CLIENT_ID: "your-github-client-id"
  GITHUB_CLIENT_SECRET: "your-github-client-secret"

  USE_LINKEDIN_SSO: "false"
  LINKEDIN_CLIENT_ID: "your-linkedin-client-id"
  LINKEDIN_CLIENT_SECRET: "your-linkedin-client-secret"
```

**Login routes** when using fastapi-sso:

| URL | Provider |
|-----|----------|
| `/login` or `/login/google` | Google |
| `/login/github` | GitHub |
| `/login/linkedin` | LinkedIn |

**OAuth app setup:** for each enabled provider, register an OAuth app and set the callback URL to `http://localhost:4000/callback/<provider>` (e.g. `/callback/google`).

### Auth0

To use Auth0 instead, set `USE_AUTH0: "true"` in `env.yml` and fill in the Auth0 credentials:

```yaml
local:
  USE_AUTH0: "true"
  AUTH0_CLIENT_ID: "your-auth0-client-id"
  AUTH0_CLIENT_SECRET: "your-auth0-client-secret"
  AUTH0_DOMAIN: "example.us.auth0.com"
```

In your Auth0 dashboard:
1. Go to Applications and select your app.
2. Set Application Type to "Regular Web Application."
3. Add `http://localhost:4000/callback` to Allowed Callback URLs, Allowed Logout URLs, and Allowed Web Origins.
4. Click Save.

When `USE_AUTH0: "true"`, the fastapi-sso provider flags (`USE_GOOGLE_SSO`, etc.) are ignored.

---

## Frontend and static files

Edit `myapp/app/static/compiled/index.html` directly for quick changes, then restart the server.

For structured frontend work, use the Bootstrap Studio project under `myapp/bstudio/`. Set the export path to `myapp/app/static/compiled/` in Bootstrap Studio's Export Settings, then export and run `bash bin/compile` afterward.

Place any static files under `myapp/app/static/compiled/` — they are served from `/` as long as the path does not conflict with an API endpoint.

Edit `myapp/app/static/assets/js/_config.js` to customize the app's navigation pages and settings (this is the source of truth for `config.js`).

## Add plugins

```bash
uv run zix add-plugin -w myapp
```

The CLI will prompt for a plugin name. The plugin skeleton is created at `myapp/app/plugins/<plugin_name>/`. See the generated `README.md` inside the plugin directory to get started.

## Database

SQLite is used by default (creates `myapp/zix.db`). For production, switch to PostgreSQL by setting these variables in `env.yml`:

```yaml
  DATABASE: "your_database_name"
  DB_HOST: "your-db-host"
  DB_USERNAME: "your-db-username"
  DB_PASSWORD: "your-db-password"
```

## Third-party services

### Stripe (payment)

Set `STRIPE_API_KEY` and `STRIPE_API_SECRET` in `env.yml`.

### SendGrid (email)

Set `SENDGRID_KEY`, `SENDGRID_FROM_EMAIL`, and related template IDs in `env.yml`.

## Deployment

zix apps can be deployed to any cloud VM. A `Dockerfile` is included in the generated project root for containerized deployments.

### Google Cloud Run

To be written.

### AWS Lambda

To be written.
