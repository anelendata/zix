# zix

FastAPI based web app framework.

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

Go to Export Settings on Bootstrap Studio and set the export path
to `myapp/static/compiled`. Then export.

Run the server again. Now you have an (empty) webapp UI.

## Add endpoints

Take a look at `myapp/plugins/core/routers.py` and `myapp/plugins/web/routers.py`.
You can add your service under plugins directory.

## Third-party services

In coming release of zix, I'm going to add the complete code to leverage these third-party services:

### Auth0 (login)

To be written

### Stripe (payment)

To be written

### SendGrid (email)

To be written
