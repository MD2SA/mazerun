# Scripts

Repository-wide helper scripts.

| Script | Purpose |
| --- | --- |
| `generate_dump.sh` | Dump the `mazerun` database from `mazerun-mysql-db` to `mysql/db/dump.sql` |
| `generate_dump.bat` | Windows version of the dump script |

## Dump generation

```bash
./scripts/generate_dump.sh
```

```bat
scripts\generate_dump.bat
```

Both scripts load `mysql/.env` when present and require
`MYSQL_ROOT_PASSWORD`. The container must be running.

See [../docs/scripts.md](../docs/scripts.md) for the full list of service
launchers and conventions.
