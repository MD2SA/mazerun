# Contributing

Thanks for working on Mazerun. This is an academic team project; keep changes
focused and update the docs with the code.

## Before you start

1. Read [docs/getting-started.md](docs/getting-started.md) and
   [docs/configuration.md](docs/configuration.md).
2. Create the `.env` files from the examples. Never commit them.
3. Run the stack once and confirm the API, MongoDB, and MySQL containers are
   healthy.

## Branches

Use a short descriptive branch:

```text
feat/team-filter
fix/mongo-retry
docs/api-examples
chore/docker-pin
```

Branch from `main` and delete the branch after merging.

## Commit messages

Use Conventional Commits:

```text
<type>(<scope>): <summary>
```

Examples:

```text
feat(web): add team filter to the overview
fix(mongo): retry change-stream inserts on transient errors
docs(api): document the handshake sequence
```

See [docs/development.md](docs/development.md) for the full type/scope list.

## Pull requests

- Keep the change focused.
- Describe the motivation and how you tested it.
- Update the relevant docs.
- Do not include secrets, `.env` files, generated dumps with real data, or
  `game/` binaries.
- Request a review from another team member.

## Local checks

```bash
python -m compileall -q mongo mysql/persistence
find mysql/php -name '*.php' -print0 | xargs -0 -n1 php -l
cd web-app && pnpm lint && pnpm build
cd android && ./gradlew assembleDebug
```

There is no CI at the moment, so these checks are manual.

## Security

Do not open a public issue for a vulnerability. Follow
[SECURITY.md](SECURITY.md).

## Questions

Open an issue with:

- the command you ran
- the relevant container logs
- the expected and actual behavior
