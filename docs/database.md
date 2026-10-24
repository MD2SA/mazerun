# Database schema

The system uses MongoDB for raw and processed events and MySQL for the
historical, queryable data used by the API and dashboards.

## MongoDB

The database is `game` (see `mongo/config.yaml`). MongoDB must run as a replica
set because the outbound service uses change streams.

### `active_sessions`

One document per active player session. The inbound service restores this
collection on startup so sessions survive a restart.

```json
{
  "_id": 1,
  "simulation_id": 50,
  "registered_at": "ISODate"
}
```

### `simulation_configs`

Cached simulation configuration fetched from the consulting MySQL. `_id` is the
simulation ID.

```json
{
  "_id": 50,
  "numbermarsamis": 30,
  "numberrooms": 10,
  "numberplayers": 40,
  "normalnoise": 10.0,
  "noisevartoleration": 17.0,
  "normaltemperature": 15,
  "temperaturevarhightoleration": 20,
  "temperaturevarlowtoleration": 1,
  "loaded_at": "ISODate"
}
```

### `moves`

Raw movement events plus processing metadata.

```json
{
  "_id": "ObjectId",
  "Marsami": 123,
  "RoomOrigin": 1,
  "RoomDestiny": 2,
  "timestamp": "ISODate",
  "player_id": 1,
  "simulation_id": 50,
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

### `temperature` and `sound`

Raw sensor payloads. The uppercase fields (`Sensor`, `Value`, `Player`) come
from the simulator; the lowercase fields are added by the pipeline.

```json
{
  "_id": "ObjectId",
  "Sensor": "T1",
  "Value": 25.4,
  "timestamp": "ISODate",
  "player_id": 1,
  "simulation_id": 50,
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

### `actions`

Actuator/action audit events.

```json
{
  "_id": "ObjectId",
  "Action": "OPEN_DOOR",
  "Value": 1,
  "timestamp": "ISODate",
  "player_id": 1,
  "simulation_id": 50,
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

### `rooms`

Aggregated room state, updated by the room worker. One document per room per
simulation/player.

```json
{
  "_id": "ObjectId",
  "room_id": 5,
  "simulation_id": 50,
  "player_id": 1,
  "marsami_count": 3,
  "current_marsamis": [123, 124, 125],
  "last_update": "ISODate",
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

### `alerts`

Dedicated alert collection. The alert worker sends each document to MySQL with
delivery guarantees.

```json
{
  "_id": "ObjectId",
  "collection": "sound",
  "player": 1,
  "game": 1,
  "simulation_id": 50,
  "sensor": "sound",
  "value": 35.0,
  "alertType": "HIGH_SOUND",
  "alert": "High sound level detected (35.0 dB)",
  "timestamp": "ISODate",
  "process_status": "pending | processing | processed",
  "sent_at": "ISODate",
  "processed_at": "ISODate"
}
```

MongoDB is schemaless, so extra fields sent by the simulator are stored as-is.

## MySQL

The schema is created by `mysql/db/dump.sql`; procedures and roles are applied
by `mysql/run.sh`.

### Tables

| Table | Purpose |
| --- | --- |
| `user` | Users, roles (`usr`/`adm`), team assignment, bcrypt password hash |
| `simulation` | Simulation runs, owner, team, player, start date, total score |
| `measure` | Validated movements |
| `invalid_measure` | Rejected movements with a reason |
| `temperature` | Temperature readings |
| `sound` | Sound readings |
| `sound_outlier` | Sound anomalies |
| `alert` | Alerts (score, high/low temperature, high sound) |
| `ocupation` | Aggregated odd/even Marsami counts per room |
| `action` | Actuator/action audit trail |
| `processed_event` | Idempotency ledger keyed by MongoDB document ID |

### Stored procedures

| File | Procedures |
| --- | --- |
| `persistence_routines.sql` | `sp_insert_measure`, `sp_insert_invalid_measure`, `sp_insert_temperature`, `sp_insert_sound`, `sp_insert_sound_outlier`, `sp_insert_alert`, `sp_update_ocupation`, `sp_insert_simulation`, `sp_insert_action` |
| `simulation_procedures.sql` | `sp_create_game`, `sp_update_game` |
| `user_procedures.sql` | `sp_create_user`, `sp_update_user`, `sp_delete_user`, `sp_get_all_users` |

### Roles

`roles.sql` creates four development users with `CHANGE_ME_*` passwords:

| User | Intended access |
| --- | --- |
| `adm_user` | Read/update/delete user, simulation, alert, outlier, invalid measure, processed event; read measures/sensors |
| `migrator_user` | Insert simulation, occupation, sensor, alert, outlier, invalid measure, processed event, measure, action |
| `operational_user` | Read/update user and simulation; insert alerts and outliers; read the rest |
| `app_user` | Application read access |

The application itself connects with the `MYSQL_*` credentials, not these
users. Replace the placeholders before using them.

## Applying the schema

```bash
cd mysql
./run.sh
```

The script prompts before recreating the database from `dump.sql`, then applies:

```text
user_procedures.sql
simulation_procedures.sql
persistence_routines.sql
roles.sql
```

To apply a single file manually:

```bash
docker cp mysql/db/user_procedures.sql mazerun-mysql-db:/tmp/apply.sql
docker exec mazerun-mysql-db bash -c "mysql -uroot -p mazerun < /tmp/apply.sql"
```

## Generating a dump

```bash
./scripts/generate_dump.sh
```

Windows:

```bat
scripts\generate_dump.bat
```

The script:

1. Reads `mysql/.env` (shell version) for `MYSQL_ROOT_PASSWORD`.
2. Checks that the `mazerun-mysql-db` container is running.
3. Runs `mysqldump` inside the container, so the client version matches the
   server (`mysql:8.0`).
4. Writes `mysql/db/dump.sql`.

The committed dump was originally produced by a newer MySQL client. Regenerate
it with the script when you change the schema.

## Admin account

`dump.sql` intentionally contains no usable password hash for the `adm` user.
See [SECURITY.md](../SECURITY.md) for the one-time command to set one.

## Related docs

- [Data flow](data-flow.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)
