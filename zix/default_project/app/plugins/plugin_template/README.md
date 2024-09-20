# Devloping a plugin

A plugin direcotry contains:
- README.md (This file)
- models.py (Plugin specific models)
- crud.py (Functions to create, read, update, and deletion of the records)
- routers.py (Endpoint definitions)
- schemas.py (Schema definitions)

# Routing

You can set any path to invoke an endpoint, but it's good to follow a consistent pattern.

The typical format in the default endpoints look like this:

```
POST/GET/PUT/DELETE {DOMAIN}/api/v1/users
```

- The value of the `/api/v1/` can be changed (including blank "") at app/config/common.py.
- `users` represents the model as most API endpoints are create (POST), read (GET), update (PUT), or delete (DELETE)
