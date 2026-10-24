# Troubleshooting

## First checks

```bash
docker ps
docker compose ls
```

All containers should be running:

- `mazerun-mongo-db`, `mazerun-mongo-replica-1`,
  `mazerun-mongo-replica-2`, `mazerun-mongo-app`
- `mazerun-mysql-db`, `mazerun-mysql-persistence`, `mazerun-php`,
  `mazerun-phpmyadmin`
- `mazerun-web-app`

If a container exits immediately, check its logs:

```bash
docker logs <container> --tail 100
```

## MongoDB

### Change streams do not fire

The replicas set must be initialized. On a single-node or standalone MongoDB,
change streams fail.

```bash
docker exec -it mazerun-mongo-db mongosh --eval "rs.status()"
```

If the set is not initialized, restart the stack and check the `mongo-setup`
logs:

```bash
docker logs mazerun-mongo-setup
```

### `mongo-app` cannot connect

- Confirm the `MONGO_URI` points at the replica set:
  `mongodb://mongo-db:27017,mongo-replica-1:27017,mongo-replica-2:27017/?replicaSet=rs0`
- Check that `mongo-db` is the primary.
- Make sure the three nodes are on the same Docker network.

### No documents are written

- Is `mazerun.exe` publishing to the expected topics?
- Does the topic contain `mazemov`, `mazetemp`, `mazesound`, or `mazeact`?
- Is an active session registered? The handshake must arrive on
  `pisid/25/game/start` before sensor documents are stamped.
- Check the inbound logs:

```bash
docker logs mazerun-mongo-app --tail 100
```

## MQTT

### No data from the simulator

- Test the broker connection:

```bash
nc -vz broker.hivemq.com 1883
```

- Confirm the simulator flags match the config:
  `--broker broker.hivemq.com --portbroker 1883`.
- Check that the team prefix matches (`25` in the default config).
- On a public broker, another team may be using the same topic. The internal
  prefix isolates processed events, but the raw topics are shared.

### Handshake times out

`create_simulation` waits for the MongoDB ACK on
`pisid/25/game/start/ack`. If it times out:

- Is the inbound service running?
- Is the topic name correct?
- Check the inbound logs for `game/start received` and
  `Published ACK to pisid/25/game/start/ack`.

## MySQL and PHP

### `JWT_SECRET` errors / 500 responses

`jwt.php` throws when `JWT_SECRET` is empty. Set it in `mysql/.env`:

```bash
openssl rand -hex 32
```

Then restart the PHP service:

```bash
docker compose -f mysql/docker-compose.yml up -d --build php
```

### `Access denied` or connection refused

- Check `MYSQL_*` in `mysql/.env`.
- Confirm `mysql-db` is running and initialized:
  `docker logs mazerun-mysql-db --tail 100`.
- Inside Docker the host is `mysql-db`, not `localhost`.
- If you run the persistence service outside Docker, set `MYSQL_HOST=localhost`
  in `mysql/persistence/.env`.

### Admin login fails

`mysql/db/dump.sql` ships without a usable password hash for `adm`. Generate one
and update the row:

```bash
docker compose -f mysql/docker-compose.yml exec php \
  php -r "echo password_hash('your-password', PASSWORD_BCRYPT), PHP_EOL;"
```

```sql
UPDATE user SET password = '<hash>' WHERE email = 'adm';
```

See [SECURITY.md](../SECURITY.md).

### Stored procedures are missing

Re-apply them:

```bash
cd mysql
./run.sh
```

Answer `n` to keep existing data; the script still applies the procedures and
roles.

### phpMyAdmin is empty or cannot connect

- Open <http://localhost:8080>.
- Server: `mysql-db`.
- User: `root`.
- Password: `MYSQL_ROOT_PASSWORD` from `mysql/.env` (default `root`).

## Simulator

### `mazerun.exe not found at /game/server/mazerun.exe`

Place the executable and its `_internals/` folder at:

```text
game/server/mazerun.exe
game/server/_internals/
```

The PHP container mounts the repository's `game/` directory at `/game`. You can
override the path with `MAZERUN_EXE_PATH` in `mysql/.env`.

### `mazerun.exe` exits immediately

- Check `/tmp/mazerun-<simulation_id>.log` inside the PHP container:

```bash
docker exec mazerun-php cat /tmp/mazerun-<id>.log
```

- Run the executable manually to see the missing dependency.
- Confirm the `_internals/` folder is next to the executable.
- Wine is installed in the PHP image, but a missing 32-bit library can still
  break the launch.

### Session never ends

The session ends after 5 minutes, when all Marsamis have `status == 2`, or when
`simulation_finished` is published. Check:

- `mongo/services/inbound/processor.py` logs for the termination reason.
- The `active_sessions` collection in MongoDB.
- `/tmp/mazerun-finish-watcher-<id>.log` in the PHP container.

## Web app

### Dashboard cannot reach the API

- Check `web-app/.env` → `VITE_API_URL`.
- If the API runs on another machine, use its LAN IP, not `127.0.0.1`.
- CORS is open (`Access-Control-Allow-Origin: *`), so a browser error is usually
  a wrong URL or a non-running PHP container.
- Restart the Vite dev server after changing `.env`.

### Login works but every request returns 401

- The token may have expired (8 hours).
- `JWT_SECRET` may have changed since the token was issued.
- Clear `localStorage` and log in again.

### `pnpm` is not installed

```bash
npm install -g pnpm
```

### Port 5173 is already in use

Stop the other process or change the Vite port in `web-app/vite.config.js`.

## Android

### Cannot connect to the API

- Emulator: use `10.0.2.2:8000`.
- Physical device: use the host's LAN IP and ensure both are on the same
  network.
- The app appends `/android/` automatically; do not include it in the host
  field.
- Check that the PHP container's port `8000` is reachable from the device.

### 401 Unauthorized

The token expired or the secret changed. Log out and log in again.

### Login fails for the seeded admin

Set a password hash as described in [SECURITY.md](../SECURITY.md).

### Gradle sync fails

- Install JDK 11+.
- Install Android SDK 35.
- Run `./gradlew --refresh-dependencies`.

## Dumps

### `generate_dump` says the container is not running

```bash
docker ps --filter name=mazerun-mysql-db
```

Start the MySQL stack first.

### `MYSQL_ROOT_PASSWORD is not set`

Add it to `mysql/.env` or export it:

```bash
export MYSQL_ROOT_PASSWORD=root
./scripts/generate_dump.sh
```

### Dump path

The output is always `mysql/db/dump.sql`. The old `./dbs/mysql/dump.sql` path in
older docs was incorrect.

## Port conflicts

Stop the conflicting service or change the host port in the relevant
`docker-compose.yml`:

| Port | Service |
| --- | --- |
| `3306` | MySQL |
| `8000` | PHP API |
| `8080` | phpMyAdmin |
| `5173` | Web app |
| `27017`–`27019` | MongoDB |

## Getting more help

- Check the service logs first; most failures are logged with a clear prefix
  (`[Inbound]`, `[Outbound]`, `[App]`, `[MySQL]`).
- Open an issue with the container logs, the command you ran, and the expected
  result.
