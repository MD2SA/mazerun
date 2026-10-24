# PHP API

The PHP container serves two APIs from the same document root:

- `web/` — the JSON API used by the React dashboard.
- `android/` — the legacy endpoints used by the Android app.

## Stack

- `php:8.3-apache`
- `mysqli`, `pdo`, `pdo_mysql`
- `mod_rewrite` enabled, `AllowOverride All`
- Wine (`wine`, `wine32:i386`) so the API can launch `mazerun.exe`

## Layout

```text
php/
├── web/
│   ├── api.php                      # Dashboard API
│   ├── jwt.php                      # HS256 JWT helper
│   ├── simulation_finish_watcher.php# CLI score watcher
│   └── .htaccess                    # Passes Authorization header
└── android/
    ├── login.php                    # Email/password/database -> JWT
    ├── auth_check.php               # Bearer-token guard
    ├── get_*.php                    # Data endpoints
    ├── jwt.php                      # Shared JWT helper
    └── test.php                     # Health check
```

## Environment

| Variable | Purpose |
| --- | --- |
| `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` | Local MySQL |
| `JWT_SECRET` | JWT signing key; required |
| `MQTT_BROKER`, `MQTT_PORT` | Broker for handshake/status/start |
| `MAZERUN_EXE_PATH` | Simulator path (default `/game/server/mazerun.exe`) |
| `MAZERUN_DELAY` | Simulator delay flag |
| `CONSULTING_DB_*` | Score watcher source |

Set these in `mysql/.env`; Compose passes them into the `php` service.

## Web API

Base URL: `http://localhost:8000/web/api.php`

Actions are selected with `?action=` or a JSON body. Protected actions require
`Authorization: Bearer <token>`. See [../../docs/api.md](../../docs/api.md) for
the full action table and examples.

## Android API

Base URL: `http://localhost:8000/android/`

`login.php` accepts `username` (email), `password`, and `database`, and returns a
JWT whose `db` claim is used by the data endpoints. `auth_check.php` enforces the
bearer token.

## Starting a simulation

`web/api.php?action=create_simulation`:

1. Creates the row (`sp_create_game`).
2. Publishes the handshake to `pisid/25/game/start`.
3. Waits for the MongoDB ACK.
4. Launches `mazerun.exe` with Wine.
5. Starts `simulation_finish_watcher.php` to wait for the PID and sync the final
   score.

If the simulator is missing or exits immediately, the error includes the log
path (`/tmp/mazerun-<id>.log`).

## Related docs

- [HTTP API](../../docs/api.md)
- [Configuration](../../docs/configuration.md)
- [Troubleshooting](../../docs/troubleshooting.md)
