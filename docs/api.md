# HTTP API

There are two PHP APIs:

- **Web API:** `mysql/php/web/api.php`, used by the React dashboard.
- **Android API:** `mysql/php/android/*.php`, used by the Android app.

Both share the same JSON conventions and JWT helpers.

## Web API

Base URL:

```text
http://<host>:8000/web/api.php
```

The action can be sent as a query parameter or in a JSON body:

```http
GET /web/api.php?action=get_status
```

```http
POST /web/api.php
Content-Type: application/json

{"action": "login", "email": "user@example.com", "password": "secret"}
```

### Authentication

Protected actions require:

```http
Authorization: Bearer <token>
```

The token is an HS256 JWT signed with `JWT_SECRET` and expires after 8 hours.
The payload contains `sub` (email), `type` (`usr`/`adm`), `team`, and `db`.
`JWT_SECRET` has no default; the endpoint fails with a 500 until it is set.

Public actions: `login`, `register`, `get_status`, `get_teams`,
`check_mazerun`.

### Actions

| Action | Auth | Main parameters | Purpose |
| --- | --- | --- | --- |
| `login` | Public | `email`, `password` | Return a JWT and the user profile |
| `register` | Public | `name`, `phone`, `email`, `birth`, `team`, `password` | Self-service registration |
| `create_user` | Admin | `name`, `phone`, `type`, `email`, `birth`, `team`, `password` | Create a user |
| `get_users` | Yes | `team` (optional) | List users, filtered by team for non-admins |
| `update_user` | Yes | `email`, `name`, `phone`, `type`, `birth`, `team` | Update a user |
| `delete_user` | Admin | `email` | Delete a user |
| `change_password` | Yes | `email`, `current_password`, `new_password` | Change a password |
| `create_simulation` | Yes | `description`, `team` (admin), `owner_email` (admin) | Create a simulation, handshake, start `mazerun.exe` |
| `update_simulation` | Yes | `id`, `description`, `team` | Update a simulation |
| `get_simulations` | Yes | `team` (optional) | List simulations |
| `get_simulation_score` | Yes | `simulation_id` | Final/total score |
| `get_analytics` | Yes | `team` (optional) | Dashboard aggregates |
| `get_sensor_data` | Yes | `simulation_id` | Sensor series for charts |
| `get_unified_logs` | Yes | `simulation_id`, `team`, `limit`, `offset` | Merged event stream |
| `get_teams` | Public | — | Team IDs for the admin filter |
| `get_status` | Public | — | MySQL/MQTT health summary |
| `check_mazerun` | Public | — | Whether `mazerun.exe` is running |

Response shape:

```json
{
  "success": true,
  "message": "optional",
  "data": {}
}
```

Errors use the same shape with `success: false` and an HTTP error code for auth
failures.

### Examples

Login:

```bash
curl -s "http://localhost:8000/web/api.php?action=login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret"}'
```

Create a simulation:

```bash
curl -s "http://localhost:8000/web/api.php?action=create_simulation" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"description":"Demo run"}'
```

`create_simulation` performs the following sequence:

1. Creates the row with `sp_create_game`.
2. Publishes the handshake to `pisid/25/game/start`.
3. Waits for the MongoDB ACK on `pisid/25/game/start/ack`.
4. Launches `mazerun.exe` through Wine.
5. Starts `simulation_finish_watcher.php` to sync the score when the process
   exits.

If the handshake or process launch fails, the simulation row is rolled back.

## Android API

Base URL:

```text
http://<host>:8000/android/
```

| Endpoint | Auth | Purpose |
| --- | --- | --- |
| `test.php` | Public | Health check |
| `login.php` | Public | Exchange email/password/database for a JWT |
| `get_messages.php` | Bearer | Alerts/messages |
| `get_room_data.php` | Bearer | Room occupation |
| `get_sound_data.php` | Bearer | Sound series |
| `get_max_sound_value.php` | Bearer | Maximum sound |
| `get_temperature_data.php` | Bearer | Temperature series |
| `get_min_max_temp_values.php` | Bearer | Min/max temperature |

`login.php` expects `username` (email), `password`, and `database`. The JWT
includes the chosen database in the `db` claim, and the data endpoints use it.

The Android endpoints connect with `MYSQL_HOST`, `MYSQL_USER`,
`MYSQL_PASSWORD`, and `MYSQL_DATABASE`. The data endpoints require a valid
bearer token through `auth_check.php`.

> **Note:** the database name comes from the login request. Only expose these
> endpoints to trusted clients, or restrict the allowed database names.

## Environment variables used by PHP

| Variable | Purpose |
| --- | --- |
| `MYSQL_HOST` | MySQL host (default `mysql-db`) |
| `MYSQL_USER` | MySQL user |
| `MYSQL_PASSWORD` | MySQL password |
| `MYSQL_DATABASE` | MySQL database |
| `JWT_SECRET` | JWT signing key (required) |
| `MQTT_BROKER` | Broker for handshake/status/start |
| `MQTT_PORT` | Broker port |
| `MAZERUN_EXE_PATH` | Simulator path inside the container |
| `MAZERUN_DELAY` | Simulator delay flag |
| `CONSULTING_DB_*` | Score watcher source database |

## Related docs

- [Web app](web-app.md)
- [Android app](android.md)
- [Configuration](configuration.md)
- [Database](database.md)
