# MongoDB services

This service ingests raw MQTT telemetry, validates it, stores it in MongoDB, and
republishes normalized events for the MySQL persistence service.

## Layout

```text
mongo/
├── main.py                       # Multi-process orchestrator
├── config.yaml                   # Topics, replica set, consulting DB
├── docker-compose.yml            # 3-node replica set + app
├── Dockerfile
├── common/
│   ├── config_loader.py          # YAML + ${ENV} expansion
│   ├── mongo_connection.py
│   ├── mysql_connection.py
│   └── simulation_config.py
└── services/
    ├── inbound/                  # MQTT -> MongoDB + handshake
    └── outbound/                 # Change streams -> validation -> MQTT
```

## Run

Docker (recommended):

```bash
cp .env.example .env
./run.sh        # Linux/macOS
run.bat         # Windows
```

This starts `mazerun-mongo-db`, two secondaries, the one-shot replica-set setup,
and `mazerun-mongo-app`.

Outside Docker:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

MongoDB must already be running as a replica set.

## Configuration

- `config.yaml` — team ID, MQTT topics, internal prefix, ACK topic, MongoDB
  database, consulting MySQL host.
- `.env` — `MONGO_URI`, `MQTT_BROKER`, and `CONSULTING_DB_*`.

See [../docs/configuration.md](../docs/configuration.md).

## Data flow

- Inbound: raw topics → `moves`, `temperature`, `sound`, `actions`,
  `active_sessions`.
- Outbound: change streams → `measure`, `invalid_measure`, `temperature`,
  `sound`, `sound_outlier`, `message`, `ocupation`, `actuator/score`.
- ACK: persistence → `pisid/25/persistence/ack` → `processed`.

See [../docs/data-flow.md](../docs/data-flow.md) and
[../docs/database.md](../docs/database.md).

## Health checks

```bash
docker logs mazerun-mongo-app --tail 100
docker exec -it mazerun-mongo-db mongosh --eval "rs.status()"
```

## Related docs

- [Architecture](../docs/architecture.md)
- [Database schema](../docs/database.md)
- [Troubleshooting](../docs/troubleshooting.md)
