# A webapp powered by [zix](https://pypi.org/project/zixweb)

The rest of the document assumes your project is in `myapp` directory and that
the server is started from the **parent** directory (e.g. `zix_projects/`).

## Install dependencies

```bash
uv sync
```

## Create tables

By default, the app uses SQLite and creates `zix.db` in the project root.
Run Alembic to create the schema **before** starting the server for the first time —
the auth middleware queries the `token` table on every request.

```bash
uv run alembic revision --autogenerate -m "initial"
uv run alembic upgrade head
```

## Compile frontend assets

```bash
bash bin/compile
```

> This also copies `app/static/assets/js/_config.js` to
> `compiled/assets/js/config.js`. Without this step the browser throws
> `Uncaught ReferenceError: Config is not defined`.

## Set up env.yml

```bash
mkdir -p .env
cp env.yml .env/env.yml
```

Open `.env/env.yml` and configure your auth credentials (see [Authentication](#authentication) below).

## Run the app

**Important:** run from the **parent** directory, not from inside the app folder.

```bash
uv run zix serve -w myapp -p 4000 -e myapp/.env/env.yml
```

Point your browser to `http://localhost:4000`.

## Authentication

By default the app uses **fastapi-sso** (open source, no external account needed)
with Google SSO enabled. Set `USE_AUTH0: "true"` in `env.yml` to switch to Auth0.

**fastapi-sso provider toggles:**

| Provider | Flag | Default |
|----------|------|---------|
| Google | `USE_GOOGLE_SSO` | `"true"` |
| GitHub | `USE_GITHUB_SSO` | `"false"` |
| LinkedIn | `USE_LINKEDIN_SSO` | `"false"` |

`/login` redirects to the first enabled provider. Set the OAuth callback URL in
your provider's app settings to `http://localhost:4000/callback/<provider>`
(e.g. `/callback/google`).

**Auth0:** set `USE_AUTH0: "true"` and fill in `AUTH0_CLIENT_ID`,
`AUTH0_CLIENT_SECRET`, `AUTH0_DOMAIN`. Add `http://localhost:4000/callback` to
Allowed Callback URLs in your Auth0 dashboard.

## Frontend and static files

Edit `app/static/compiled/index.html` directly for quick changes.

For structured frontend work, open `bstudio/` in Bootstrap Studio, set the
export path to `app/static/compiled/`, export, then re-run `bash bin/compile`.

Edit `app/static/assets/js/_config.js` to customise navigation pages and
settings — this is the source of truth for `config.js`.

## Add plugins

```bash
uv run zix add-plugin -w myapp
```

The plugin skeleton is created at `app/plugins/<plugin_name>/`.

## Database

SQLite is the default (creates `zix.db`). For production PostgreSQL, set these
in `env.yml`:

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

A `Dockerfile` is included. Dependencies are installed via uv from `pyproject.toml`.

### Google Cloud Run

To be written.

### AWS Lambda

To be written.
