# Development

## Repository conventions

- Default branch: `main`.
- Branch names: `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`,
  `chore/<short-name>`, `refactor/<short-name>`.
- Keep branches short-lived and delete them after merging.
- Do not commit `.env`, generated dumps with real data, `game/`, `analytics/`,
  `venv/`, or `node_modules/`.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <summary>
```

- Lowercase type and summary.
- Imperative mood: “add”, not “added”.
- No trailing period.
- Keep the summary under ~72 characters.
- Use the body for *why*, not *what*.
- Reference issues in the footer when relevant.

### Types

| Type | Use |
| --- | --- |
| `feat` | New behavior |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change without new behavior |
| `test` | Tests |
| `chore` | Maintenance, tooling, dependencies |
| `build` | Build system or Docker |
| `ci` | CI configuration |
| `perf` | Performance |

### Scopes

Use the component you touched:

`mongo`, `mysql`, `persistence`, `api`, `web`, `android`, `docker`, `scripts`,
`config`, `docs`, `deps`.

Examples:

```text
feat(web): add team filter to the overview
fix(mongo): retry change-stream inserts on transient errors
docs(api): document the handshake sequence
chore(docker): pin the MySQL image to 8.0
```

### Merge commits

Merge commits created by GitHub keep their `Merge pull request #N ...` message.
They are not subject to the Conventional Commits rule.

## Pull requests

1. Branch from `main`.
2. Make focused commits.
3. Update the relevant docs (`README.md`, `docs/`, service README).
4. Describe the change, the motivation, and how you tested it.
5. Request a review from another team member.
6. Delete the branch after merging.

There is currently **no CI**. Run the checks locally before opening a PR.

## Local checks

Python:

```bash
python -m compileall -q mongo mysql/persistence
```

PHP:

```bash
find mysql/php -name '*.php' -print0 | xargs -0 -n1 php -l
```

Web:

```bash
cd web-app
pnpm lint
pnpm build
```

Docker configuration:

```bash
docker compose -f mongo/docker-compose.yml config
docker compose -f mysql/docker-compose.yml config
docker compose -f web-app/docker-compose.yml config
```

Android:

```bash
cd android
./gradlew assembleDebug
```

## Configuration changes

- Add new secrets to the relevant `.env.example` and to the docs, never to the
  tracked YAML with a real value.
- Use `${VAR}` or `${VAR:-default}` in YAML so the loaders can expand them.
- Keep `.env` out of git.

## Database changes

1. Update `mysql/db/dump.sql` (or the relevant procedure file).
2. Regenerate the dump with `scripts/generate_dump.sh` when the schema changes.
3. Update [database.md](database.md).
4. Test the procedures against `mysql:8.0`.

## Documentation changes

- Keep the docs in English.
- Update the root README index when you add a new document.
- Check internal links and commands.
- Use relative links between files under `docs/`.

## Releases and tags

There is no release automation. `stable` is an annotated tag pointing at the
current known-good `main` snapshot. When you need a new snapshot:

```bash
git tag -a stable -m "Stable snapshot <date>" main
git push --force origin stable
```

Use a new annotated tag (for example `v1.1.0`) for versioned releases. Do not
move published version tags.

## History rewrite

The repository history was rewritten once to normalize commit subjects and
remove committed credentials. See [history-rewrite.md](history-rewrite.md) for
the re-clone instructions and the rules that followed it.

## Related docs

- [Getting started](getting-started.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)
