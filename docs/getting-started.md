# Getting started

This guide starts the full stack from a fresh clone. For the architecture, see
[architecture.md](architecture.md).

## 1. Prerequisites

| Tool | Version | Used for |
| --- | --- | --- |
| Git | any recent | Clone |
| Docker Engine + Compose v2 | recent | MongoDB, MySQL, PHP, web app |
| Python | 3.11+ | Running `mongo/` or `mysql/persistence/` outside Docker |
| Node.js | 20+ | Web app development |
| pnpm | 9+ | Web app development |
| Android Studio | recent | Android app |
| `mazerun.exe` | course build | Simulator |

Check Docker:

```bash
docker --version
docker compose version
```

## 2. Clone the repository

```bash
git clone git@personal:MD2SA/mazerun.git
cd mazerun
```

> The remote uses the `personal` SSH alias. If you do not have it, use the HTTPS
> URL or add the alias to `~/.ssh/config`.

## 3. Create the environment files

```bash
cp mysql/.env.example mysql/.env
cp mongo/.env.example mongo/.env
cp mysql/persistence/.env.example mysql/persistence/.env
cp web-app/.env.example web-app/.env
```

Edit the files:

- `mysql/.env`
  - `JWT_SECRET` — generate with `openssl rand -hex 32`
  - `MYSQL_ROOT_PASSWORD`, `MYSQL_USER`, `MYSQL_PASSWORD` — local defaults are
    `root` / `root` / `root`
  - `CONSULTING_DB_*` — credentials for the course consulting MySQL, if used
  - `MQTT_BROKER`, `MQTT_PORT`, `MAZERUN_DELAY`, `MAZERUN_EXE_PATH` — simulator
    launch defaults
- `mongo/.env`
  - `CONSULTING_DB_*` — same consulting database
  - `MONGO_URI` — only needed when running outside Docker
- `mysql/persistence/.env`
  - `MYSQL_*` — local MySQL credentials
  - `CONSULTING_DB_*` — consulting database
- `web-app/.env`
  - `VITE_API_URL` — defaults to `http://127.0.0.1:8000/web/api.php`

All `.env` files are ignored by git. Only the `.env.example` templates are
tracked.

## 4. Start MySQL, PHP, and persistence

```bash
cd mysql
./run.sh
```

Windows:

```bat
cd mysql
run.bat
```

The script:

1. Asks whether to recreate the database from `db/dump.sql`.
2. Starts `mysql-db` in the background.
3. Applies `dump.sql` (optional), `user_procedures.sql`,
   `simulation_procedures.sql`, `persistence_routines.sql`, and `roles.sql`.
4. Starts `mysql-app`, `phpmyadmin`, and `php`.

Verify:

```bash
docker ps
curl "http://localhost:8000/web/api.php?action=get_status"
```

The API should return JSON with the MySQL and MQTT status. If `JWT_SECRET` is
missing, the API returns a 500 until you set it in `mysql/.env` and restart the
`php` service.

## 5. Start MongoDB and the processing services

In a second terminal:

```bash
cd mongo
./run.sh
```

Windows:

```bat
cd mongo
run.bat
```

This starts three MongoDB nodes (`mazerun-mongo-db`, `-replica-1`, `-replica-2`),
runs the replica-set initialization, and starts `mazerun-mongo-app` (inbound +
outbound).

Verify:

```bash
docker logs mazerun-mongo-app --tail 50
docker exec -it mazerun-mongo-db mongosh --eval "rs.status()"
```

The replica set must be `PRIMARY`/`SECONDARY`; change streams do not work
against a standalone MongoDB.

## 6. Start the simulator

The PHP API expects the executable at `/game/server/mazerun.exe` inside the
container, which maps to `game/server/mazerun.exe` in the repository root:

```text
game/
├── server/
│   ├── mazerun.exe
│   └── _internals/
└── analytics/          # optional analytics executables
```

The `game/` directory is ignored by git.

### Start from the web dashboard

Log in, open **Simulations**, and create a simulation. The API:

1. Creates the simulation row.
2. Publishes the handshake to `pisid/25/game/start`.
3. Waits for MongoDB to acknowledge it.
4. Launches `mazerun.exe` through Wine with the team ID and the configured
   broker.
5. Starts `simulation_finish_watcher.php`, which waits for the process to exit
   and syncs the final score.

### Start manually

```bash
cd game/server
./mazerun.exe 25 --flagMessage 1 --delay 2 --broker broker.hivemq.com --portbroker 1883
```

| Flag | Meaning |
| --- | --- |
| `25` | Team/group number |
| `--flagMessage 1` | Publish sound, temperature, movements, and actuators (`2` movements, `3` sound, `4` temperature, `5` actuators) |
| `--delay 2` | Seconds between movements |
| `--broker` | MQTT broker host |
| `--portbroker` | MQTT broker port |

## 7. Start the web dashboard

Docker:

```bash
cd web-app
./run.sh
```

Local development:

```bash
cd web-app
pnpm install
pnpm dev
```

Open <http://localhost:5173>. The first login needs a user. Use the **Register**
form, or create an admin with the instructions in [SECURITY.md](../SECURITY.md).

## 8. Start the Android app

1. Open the `android/` directory in Android Studio.
2. Let Gradle sync (JDK 11+; compile SDK 35).
3. Run the app on an emulator or device.
4. Log in with:
   - **Host:** `10.0.2.2:8000` for the emulator, or the LAN IP of the PHP host
     for a physical device (for example `192.168.1.50:8000`)
   - **Database:** `mazerun`
   - **Email / password:** a user from the `user` table

The app appends `/android/` to the host, so `10.0.2.2:8000` becomes
`http://10.0.2.2:8000/android/`.

## What to run where

| Terminal | Command | Required |
| --- | --- | --- |
| 1 | `cd mysql && ./run.sh` | Yes |
| 2 | `cd mongo && ./run.sh` | Yes |
| 3 | `cd web-app && ./run.sh` (or `pnpm dev`) | For the dashboard |
| External | `mazerun.exe ...` | For data |
| Android Studio | Run the app | For mobile |

## Next steps

- [Configuration](configuration.md)
- [Data flow and MQTT topics](data-flow.md)
- [Troubleshooting](troubleshooting.md)
