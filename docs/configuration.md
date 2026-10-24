# Configuration and secrets

Configuration is split by service. YAML files hold non-secret defaults and
`${VAR}` references; secrets live in untracked `.env` files.

## Variable expansion

Both Python config loaders expand `${NAME}` and `${NAME:-default}` in every
string value:

- `mongo/common/config_loader.py`
- `mysql/persistence/common/config_loader.py`

An empty environment variable falls back to the default when one is provided.
A missing variable without a default raises `KeyError` at startup.

Each loader also loads the `.env` file next to its `config.yaml`:

- `mongo/.env`
- `mysql/persistence/.env`

Variables already exported in the process take precedence over `.env`.

## Environment files

| File | Read by | Purpose |
| --- | --- | --- |
| `mongo/.env` | `mongo/` services and `mongo/docker-compose.yml` | MongoDB URI, MQTT broker, consulting DB |
| `mysql/.env` | `mysql/docker-compose.yml` | MySQL root/app credentials, JWT secret, MQTT, simulator launch |
| `mysql/persistence/.env` | `mysql/persistence/` outside Docker | MySQL saving + consulting DB |
| `web-app/.env` | Vite | `VITE_API_URL` |

Templates: `mongo/.env.example`, `mysql/.env.example`,
`mysql/persistence/.env.example`, `web-app/.env.example`.

## Variables

### MongoDB and processing (`mongo/.env`)

| Variable | Default | Used by |
| --- | --- | --- |
| `MONGO_URI` | `mongodb://localhost:27017` | `mongo/config.yaml`; Docker overrides it with the replica-set URI |
| `MQTT_BROKER` | `broker.hivemq.com` | Inbound and outbound MQTT clients |
| `CONSULTING_DB_HOST` | `consulting-db.example.edu` | Simulation configuration lookup |
| `CONSULTING_DB_USER` | empty | Simulation configuration lookup |
| `CONSULTING_DB_PASSWORD` | empty | Simulation configuration lookup |
| `CONSULTING_DB_NAME` | `maze` | Simulation configuration lookup |

The MQTT topics, team ID, internal prefix, and ACK topic are in
`mongo/config.yaml` and are not secrets.

### MySQL and PHP (`mysql/.env`)

| Variable | Default | Used by |
| --- | --- | --- |
| `MYSQL_ROOT_PASSWORD` | `root` | `mysql-db` container, `scripts/generate_dump.*` |
| `MYSQL_USER` | `root` | Persistence app, PHP API |
| `MYSQL_PASSWORD` | `root` | Persistence app, PHP API |
| `MYSQL_DATABASE` | `mazerun` | Persistence app, PHP API |
| `JWT_SECRET` | none | `mysql/php/web/jwt.php` and `mysql/php/android/jwt.php` |
| `MQTT_BROKER` | `broker.hivemq.com` | PHP API status/start functions |
| `MQTT_PORT` | `1883` | PHP API |
| `MAZERUN_DELAY` | `2` | Delay passed to `mazerun.exe` |
| `MAZERUN_EXE_PATH` | `/game/server/mazerun.exe` | Executable path inside the PHP container |
| `CONSULTING_DB_HOST` | `consulting-db.example.edu` | Score watcher |
| `CONSULTING_DB_USER` | empty | Score watcher |
| `CONSULTING_DB_PASSWORD` | empty | Score watcher |
| `CONSULTING_DB_NAME` | `maze` | Score watcher |

### Persistence outside Docker (`mysql/persistence/.env`)

| Variable | Default | Used by |
| --- | --- | --- |
| `MYSQL_HOST` | `localhost` | Saving database |
| `MYSQL_USER` | `root` | Saving database |
| `MYSQL_PASSWORD` | empty | Saving database |
| `MYSQL_DATABASE` | `mazerun` | Saving database |
| `CONSULTING_DB_*` | as above | Consulting database |
| `MQTT_BROKER` | `broker.hivemq.com` | MQTT client |

### Web app (`web-app/.env`)

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | `http://127.0.0.1:8000/web/api.php` | Base URL of the PHP web API |

### Android

The Android app has no `.env` file. The login screen asks for the host, database
name, email, and password; the values are kept in memory only. See
[android.md](android.md).

## YAML files

| File | Contents |
| --- | --- |
| `mongo/config.yaml` | Team ID, MQTT topics/broker, MongoDB URI/database, consulting DB |
| `mysql/persistence/config.yaml` | Team ID, MQTT internal topics, saving and consulting DB |
| `mysql/docker-compose.yml` | Container definitions; reads `mysql/.env` |
| `mongo/docker-compose.yml` | Replica set and orchestrator; reads `mongo/.env` |
| `web-app/docker-compose.yml` | Vite dev server |

## Secrets policy

1. Never commit `.env`, `.env.*`, or real credentials. The root `.gitignore`
   ignores them and only un-ignores `.env.example`.
2. Keep templates in `.env.example` with empty or obvious placeholder values.
3. `JWT_SECRET` has no default. If it is missing, the PHP API throws and
   returns a 500 instead of signing tokens with a known key.
4. `mysql/db/dump.sql` intentionally contains no usable admin password hash.
   Set one before using the `adm` account; see [SECURITY.md](../SECURITY.md).
5. `mysql/db/roles.sql` uses `CHANGE_ME_*` placeholders. The application does not
   use those users by default; it connects with `MYSQL_*`.
6. Rotate any credential that was ever committed before the history rewrite.
   See [history-rewrite.md](history-rewrite.md).
7. The default MQTT broker is public. Anyone can subscribe to the `pisid_*`
   topics; use a private broker or payload encryption for real data.

## Related docs

- [Getting started](getting-started.md)
- [Database schema](database.md)
- [Troubleshooting](troubleshooting.md)
