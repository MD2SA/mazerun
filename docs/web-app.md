# Web app

The dashboard is a React 19 + Vite single-page app in `web-app/`.

## Stack

| Package | Use |
| --- | --- |
| `react`, `react-dom` | UI |
| `react-router-dom` | Routing |
| `recharts` | Charts |
| `lucide-react` | Icons |
| `vite` | Dev server and build |
| `eslint` | Linting |

## Pages

| Route | File | Purpose |
| --- | --- | --- |
| `/` | `src/pages/Overview.jsx` | KPI cards, sensor charts, recent events |
| `/simulations` | `src/pages/Simulations.jsx` | Create/update simulations, start runs |
| `/users` | `src/pages/Users.jsx` | User directory (admin) or team view |
| `/logs` | `src/pages/Logs.jsx` | Unified event stream |
| `/profile` | `src/pages/Profile.jsx` | Profile and password change |
| — | `src/pages/Login.jsx` | Login/register screen |

`src/pages/Dashboard.jsx` is a legacy page and is not currently routed.

## API client

`src/services/api.js`:

- Reads `VITE_API_URL` (default `http://127.0.0.1:8000/web/api.php`).
- Stores the JWT in `localStorage` under `jwt_token`.
- Sends `Authorization: Bearer <token>` when a token is present.
- Uses GET for reads and POST with a JSON body for writes.

## Environment

Copy the example:

```bash
cp web-app/.env.example web-app/.env
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | `http://127.0.0.1:8000/web/api.php` | PHP web API URL |

If the dashboard and API run on different machines, set the API host explicitly,
for example `http://192.168.1.50:8000/web/api.php`.

## Development

```bash
cd web-app
pnpm install
pnpm dev
```

The dev server listens on `5173` and binds to all interfaces (`host: true`).

## Build and lint

```bash
cd web-app
pnpm lint
pnpm build
```

The production build is written to `dist/` (ignored by git).

## Docker

```bash
cd web-app
./run.sh
```

The container runs `pnpm run dev --host` on port `5173` and mounts the source
directory, so changes are picked up without rebuilding. It is a development
container, not a production image.

## Authentication flow

1. `Login.jsx` calls `api.login(email, password)`.
2. The API returns a JWT and the user object.
3. `App.jsx` stores the token and user in `localStorage`.
4. `App.jsx` renders the sidebar, header, and routes.
5. Logout removes both.

Admins can switch the team filter in the header; non-admin users are fixed to
their own team.

## Theme

The app has a light/dark theme toggle. The selected theme is stored in
`localStorage` under `theme` and applied through `data-theme` on the document
element.

## Related docs

- [HTTP API](api.md)
- [Getting started](getting-started.md)
- [Troubleshooting](troubleshooting.md)
