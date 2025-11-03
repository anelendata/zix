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

- [Currently supported Python versions](https://devguide.python.org/versions/) installed.

## Install

Make and activate a Python environment. uv is recommended:

```
pip install uv
mkdir zix_projects
cd zix_projects
uv init
```

Install zix:

```
uv add zixweb
```

## Create an app

```
zix init -w myapp
cd myapp
uv sync
```

Read myapp/README.md to continue developing your app.
