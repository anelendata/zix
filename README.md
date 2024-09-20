# zix: Keeping the indie app development simple, fast, and tidy

Build a mobile friendly web app.
Battery included: Wiring signups, feature subscriptions, and payment.

- FastAPI (API backend)
- Auth0 (Authentication)
- Stripe (Payment)
- SendGrid (Email)

## Introduction

I wanted to build a web app with frontend, backend, database, login,
email services, and paywall very quickly.

Since those are common skeleton for most SaazS apps, I built a plugin
framework to build apps quickly.

## Prereqs

- Python 3.8 or later is installed

## Install

Make and activate a Python environment:

```
python -m venv venv
source ./venv/bin/activate
```

Install zix:

```
pip install -U pip
pip install zixweb
```

## Create an app

```
zix init -w myapp
cd myapp
pip install -r requirement.txt
pip install -r requirement_dev.txt
```

requirement.txt contains the modules required for running the app.
requirement_dev.txt contains the modules required for developing the app.

The rest of the document assumes your project is in `myapp` directory.

## Create tables

By default, it will run Sqlite and creates zix.db file in the project root directory.

```
alembic revision --autogenerate -m "initial models"
alembic upgrade head
```

## Set up env.yml file

From the project root, do:

```
mkdir .env
cp env.yml .env
```

Open .env/env.yml at the root project directory.

To use Auth0 login, sign up (should be free) at https://auth0.com

To try the test app,
1. Go to Applications from the left menu and select Default App.
2. Copy and Domain, Client ID and Client Secret and paste them into env.yml file into the corresponding fields.
3. Set Application Type to "Regular Web Application."
4. Enter "http://localhost:4000" to Allowed Callback URLs, Allowed Logout URLs, and Allowed Web Origins
5. Click Save

## Run app

Go to the project root directory and run:

```
zix -w . -p 4000 -e .env/env.yml serve
```

Point browser to `http://localhost:4000`

## Frontend and static files

Try modifying `myapp/static/compiled/index.html`
and run the server again.

Place frontend and static files under `myapp/static/compiled`
Anything under compiled folder is served under `/`
as long as the path is not taken by the API endpoints you define.


## Vanilla Bootstrap Studio project

Under the myapp directory, you'll find bstudio directory.
If you have an active license of Bootstrap Studio, you can
open this project.

https://bootstrapstudio.io
(I am not affiliated to the company)

Go to Export Settings on Bootstrap Studio and set the export path
to `myapp/static/compiled`. Then export.

Run the server again. Now you have an (empty) webapp UI.

## Add your plugins

```
zix -w . add-plugin
```

It will ask you the name of the plugin.
The plugin (ex. my_plugin) will be created under app/plugins/my_plugin

Take a look and modify at app/plugins/my_plugin/README.md to get started.

## Database

The app will create a Sqlite file (zix.db) under the project root.
This isn't intended for the production use.
app/config/common.py contains the SQLAlchemy settings for PostgreSQL.
All you have to do is to modify the credentials in .env/env.yml.

## Third-party services

### Auth0 (login)

To be written

### Stripe (payment)

To be written

### SendGrid (email)

To be written

## Deployment

zix apps can be deployed to any cloud virtual machines.
While the deployment commands vary among the platforms, Dockerfile under the
app project root will containerize the app.

### Google Cloud Run

To be written

### AWS Lambda

To be written
