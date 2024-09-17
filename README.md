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
```

The rest of the document assumes your project is in `myapp` directory.

## Run app

```
zix -w myapp -h 0.0.0.0 -p 4000 serve
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
