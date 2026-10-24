# History rewrite (2026-10-24)

The repository history was rewritten once to:

- Normalize commit subjects to Conventional Commits.
- Remove credentials that had been committed in configuration files, SQL
  fixtures, PHP endpoints, and helper scripts.
- Delete stale branches and recreate the `stable` tag on the new history.

Every commit SHA changed. Commit authors and committers were preserved exactly;
no co-authorship trailers were added. The commit count and the final source tree
are unchanged except for the scrubbed files.

## What to do

If you have no local work:

```bash
git fetch --all --prune
git reset --hard origin/main
git clean -fd
```

Or simply re-clone:

```bash
git clone git@personal:MD2SA/mazerun.git
```

If you have local work, rebase it onto the new `main`:

```bash
git fetch origin
git rebase --onto origin/main <old-base> <your-branch>
```

Because the old commits no longer exist, Git cannot always find the old base.
The safest option is to copy your changes to a patch, re-clone, and re-apply:

```bash
git diff > my-work.patch
# re-clone
git apply my-work.patch
```

## Branches

The following remote branches were fully contained in `main` and were deleted:

- `feat-session-termination-mqtt-score`
- `feature/actuators`
- `feature/mongo-mysql-delivery-guarantee`
- `feature/mqtt-bridge`
- `feature/start-maze`
- `feature/userSP`
- `handshake-fix`
- `master`
- `sound-temperature`

Only `main` remains. The `stable` tag was recreated on the new history.

## Secrets

The rewrite removed:

- MySQL consulting credentials (the former shared host, user, and password).
- Local MySQL passwords.
- SQL role passwords.
- The default JWT secret.
- The default admin bcrypt hash and the plaintext hint.
- Hardcoded PHP database credentials.
- Hardcoded dump-script passwords.
- The placeholder student email.

The current tree uses `.env` files and `getenv()` instead. See
[configuration.md](configuration.md).

> **Rotate any credential that was ever committed.** Scrubbing history does not
> invalidate a password that someone already saw. In particular, rotate the
> consulting database password and any shared broker credentials.

## Backups

Local pre-rewrite backups were created outside the repository:

```text
/tmp/opencode/mazerun-backup/mazerun-pre-rewrite.bundle
/tmp/opencode/mazerun-backup/mazerun-mirror.git
```

These are temporary. Do not push them to the remote. If you need to keep them,
move them to secure offline storage.

## Why the old SHAs may still appear

GitHub may keep unreachable objects and pull-request refs for a while. They are
not part of `main` and will be garbage-collected eventually. If you need them
purged immediately, contact GitHub support or delete and recreate the repository
(only with team approval).

## Rules for the future

- Never commit real credentials. Use `.env` and `.env.example`.
- Use Conventional Commits.
- Keep branches short-lived and delete them after merging.
- Do not move published tags.

See [development.md](development.md) for the full conventions.
