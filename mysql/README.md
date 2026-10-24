# MySQL, PHP, and persistence

This stack stores the historical data, exposes the HTTP APIs, and runs the
MQTT → MySQL persistence worker.

## Services

| Compose service | Container | Purpose |
| --- | --- | --- |
| `mysql-db` | `mazerun-mysql-db` | MySQL 8.0 with the schema dump |
| `mysql-app` | `mazerun-mysql-persistence` | Python MQTT → MySQL worker |
| `php` | `mazerun-php` | Apache + PHP API + Wine for `mazerun.exe` |
| `phpmyadmin` | `mazerun-phpmyadmin` | Database UI |

## Layout

```text
mysql/
├── db/                       # dump.sql + procedures + roles
├── persistence/              # Python worker
├── php/
│   ├── web/                  # Dashboard API + score watcher
│   └── android/              # Android endpoints
├── docker-compose.yml
├── Dockerfile                # PHP image (installs Wine)
└── run.sh / run.bat
```

## Run

```bash
cp .env.example .env
./run.sh        # Linux/macOS
run.bat         # Windows
```

The script optionally recreates the database, applies the procedures and roles,
and starts all services. See [../docs/scripts.md](../docs/scripts.md).

## Environment

`mysql/.env` is read by Docker Compose:

- `MYSQL_ROOT_PASSWORD`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
- `JWT_SECRET` (required by both JWT helpers)
- `MQTT_BROKER`, `MQTT_PORT`, `MAZERUN_DELAY`, `MAZERUN_EXE_PATH`
- `CONSULTING_DB_*`

The persistence service also reads `persistence/.env` when run outside Docker.

See [../docs/configuration.md](../docs/configuration.md).

## Database

- Schema: `db/dump.sql`
- Procedures: `db/user_procedures.sql`, `db/simulation_procedures.sql`,
  `db/persistence_routines.sql`
- Roles: `db/roles.sql`

See [../docs/database.md](../docs/database.md).

## API

- Web: `http://localhost:8000/web/api.php`
- Android: `http://localhost:8000/android/`
- phpMyAdmin: `http://localhost:8080`

See [php/README.md](php/README.md) and [../docs/api.md](../docs/api.md).

## Logs

```bash
docker logs mazerun-mysql-db --tail 100
docker logs mazerun-mysql-persistence --tail 100
docker logs mazerun-php --tail 100
```
