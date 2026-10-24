# Security policy

## Supported versions

Only the current `main` branch is supported. There are no maintained release
branches.

## Reporting a vulnerability

Do not open a public issue for a vulnerability. Contact the project maintainers
privately (team `MD2SA` / the PISID group 25 mailing list) with:

- a description of the issue
- steps to reproduce
- the affected component and commit
- any suggested fix

You will get an acknowledgement as soon as possible. Please give the team time
to fix the issue before disclosing it publicly.

## Secrets

Never commit:

- `.env` files or real credentials
- JWT secrets
- database dumps containing real users or password hashes
- private keys or certificates

Only the `.env.example` templates are tracked. If a secret is committed:

1. Rotate it immediately.
2. Remove it from the current tree.
3. Rewrite history if the repository is shared (see
   [docs/history-rewrite.md](docs/history-rewrite.md)).
4. Tell the team.

## Default credentials

### MySQL

`mysql/db/dump.sql` intentionally contains an unusable password hash for the
seeded `adm` user. Set a password before using that account:

```bash
docker compose -f mysql/docker-compose.yml exec php \
  php -r "echo password_hash('your-password', PASSWORD_BCRYPT), PHP_EOL;"
```

```sql
UPDATE user SET password = '<hash>' WHERE email = 'adm';
```

Alternatively, register a new account from the login screen and update its
`type` to `adm` in MySQL.

`mysql/db/roles.sql` uses `CHANGE_ME_*` placeholders. Replace them before
granting access to those users.

### JWT

`JWT_SECRET` has no default. If it is missing, the PHP API throws instead of
signing tokens with a known value. Generate a secret with:

```bash
openssl rand -hex 32
```

Tokens are valid for 8 hours. Changing the secret invalidates all existing
sessions.

## Network exposure

- The default MQTT broker is public (`broker.hivemq.com`). Anyone can subscribe
  to the `pisid_*` topics. Use a private broker or application-level encryption
  for real data.
- The PHP API enables CORS for all origins (`Access-Control-Allow-Origin: *`).
  Restrict it if the API is exposed beyond a trusted network.
- The Android app allows cleartext HTTP
  (`android:usesCleartextTraffic="true"`). Use HTTPS behind a reverse proxy for
  anything other than local development.
- phpMyAdmin is exposed on port `8080` with the MySQL root account. Do not expose
  it to the public internet.

## Known limitations

- No rate limiting on the API.
- The Android login sends the database name and stores the password in memory.
  The database name is included in the JWT and used by the data endpoints.
- The consulting database credentials are read-only but are shared with the
  course environment.
- No audit log for admin actions beyond the application tables.

## Credential rotation after the history rewrite

The repository history was rewritten on 2026-10-24 to remove committed
credentials. Rotate any credential that was ever committed, even though it is no
longer present in `main`:

- the former consulting MySQL host, user, and password
- any shared local MySQL password
- any MQTT broker credential
- the previous JWT secret

See [docs/history-rewrite.md](docs/history-rewrite.md).
