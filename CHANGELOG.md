# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
The repository uses the `stable` tag for the current known-good snapshot.

## [Unreleased]

### Added

- Architecture, setup, configuration, data-flow, database, API, web, Android,
  scripts, troubleshooting, development, and history-rewrite docs.
- Per-service READMEs for `mongo/`, `mysql/`, `mysql/php/`, `web-app/`,
  `android/`, and `scripts/`.
- `.env.example` templates for the MongoDB, MySQL, and persistence services.
- `${VAR}` / `${VAR:-default}` expansion in the Python config loaders.
- `.gitattributes` and `.editorconfig`.

### Changed

- Moved database, JWT, MQTT, and simulator-launch settings to environment
  variables.
- Replaced hardcoded PHP database credentials with `getenv()` lookups.
- Made `JWT_SECRET` mandatory; the API now fails closed if it is missing.
- Updated `scripts/generate_dump.*` to use `mazerun-mysql-db`, read the password
  from the environment, and write to `mysql/db/dump.sql`.
- Reworked the root README around the actual four-service architecture.
- Replaced the default Vite README in `web-app/`.

### Removed

- Orphan root `requirements.txt` (the old bridge was removed).
- Unused `web-app/src/assets/vite.svg`.
- `mongo/db/collections.md` (content moved to `docs/database.md`).
- Hardcoded credentials from the current tree and from all reachable history.

### Fixed

- Docker Compose now interpolates MySQL, JWT, MQTT, and consulting-database
  values instead of embedding them.
- The dump-generation scripts use the correct container name and output path.

## [stable] - 2026-10-24

### Changed

- Rewrote commit subjects to Conventional Commits and scrubbed committed
  credentials from history.
- Deleted stale remote branches and recreated the `stable` tag.
- Preserved every original commit author and committer; no co-authorship
  trailers were added.

See [docs/history-rewrite.md](docs/history-rewrite.md) for the migration notes.
