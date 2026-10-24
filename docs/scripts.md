# Scripts

## Service launchers

Each service has a Linux/macOS shell script and a Windows batch equivalent.

| Script | What it does |
| --- | --- |
| `mongo/run.sh`, `mongo/run.bat` | `docker compose down`, then `docker compose up --build` for the MongoDB replica set and the Python orchestrator |
| `mysql/run.sh`, `mysql/run.bat` | Optionally recreates the database from `db/dump.sql`, applies the procedures and roles, then starts all MySQL/PHP services |
| `web-app/run.sh`, `web-app/run.bat` | `docker compose down`, then `docker compose up --build` for the Vite dev server |
| `scripts/generate_dump.sh`, `scripts/generate_dump.bat` | Dumps the `mazerun` database from the `mazerun-mysql-db` container to `mysql/db/dump.sql` |

All scripts `cd` into their own directory first, so they can be launched from
anywhere.

## MySQL launcher

`mysql/run.sh`:

1. Asks whether to recreate the database. Answering `y` applies `dump.sql` and
   deletes existing data.
2. Starts `mysql-db` in the background.
3. Waits for `mysqladmin ping`.
4. Copies and applies `user_procedures.sql`, `simulation_procedures.sql`,
   `persistence_routines.sql`, and `roles.sql`.
5. Runs `docker compose up --build` in the foreground.

`mysql/run.bat` does the same with a fixed 10-second wait instead of a ping
loop.

## MongoDB launcher

`mongo/run.sh` / `run.bat` start the three MongoDB nodes, run the one-shot
`mongo-setup` container to initiate the replica set, and start
`mazerun-mongo-app`.

The setup container is idempotent: it prints a warning if the replica set is
already initialized.

## Web app launcher

`web-app/run.sh` / `run.bat` start the Vite development container on port
`5173`. It mounts the source directory and keeps `node_modules` inside the
container.

## Dump generation

```bash
./scripts/generate_dump.sh
```

```bat
scripts\generate_dump.bat
```

Details:

- The container must be running (`docker ps`).
- The shell version sources `mysql/.env` for `MYSQL_ROOT_PASSWORD`.
- The batch version uses `%MYSQL_ROOT_PASSWORD%` if set, otherwise `root`.
- `mysqldump` runs inside the container, so the client and server versions
  match.
- Output path: `mysql/db/dump.sql`.
- The dump includes `--routines --triggers --events` and
  `--add-drop-database --add-drop-table`.

> The dump is a schema + seed fixture, not a backup of production data. Do not
> commit dumps that contain real user data or password hashes.

## Adding a script

- Put service-specific scripts next to the service (`mongo/`, `mysql/`,
  `web-app/`).
- Put repository-wide helpers in `scripts/`.
- Provide both `.sh` and `.bat` when the operation is expected to work on
  Windows.
- Use `set -euo pipefail` in shell scripts and quote paths.
- Do not hardcode credentials; read them from the environment or `.env`.

## Related docs

- [Getting started](getting-started.md)
- [Configuration](configuration.md)
- [Database](database.md)
