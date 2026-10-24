# Web dashboard

React 19 + Vite dashboard for the Mazerun project.

## Quick start

```bash
cp .env.example .env
pnpm install
pnpm dev
```

Open <http://localhost:5173>. The API URL is controlled by `VITE_API_URL`
(default `http://127.0.0.1:8000/web/api.php`).

## Docker

```bash
./run.sh        # Linux/macOS
run.bat         # Windows
```

## Scripts

```bash
pnpm dev       # Dev server
pnpm build     # Production build -> dist/
pnpm lint      # ESLint
pnpm preview   # Preview the production build
```

## Project structure

```text
web-app/
├── src/
│   ├── App.jsx              # Layout, routes, auth state
│   ├── pages/               # Overview, Simulations, Users, Logs, Profile, Login
│   ├── services/api.js      # API client and token storage
│   ├── assets/
│   └── index.css
├── public/
├── vite.config.js
└── package.json
```

## Pages

| Route | Page |
| --- | --- |
| `/` | Overview |
| `/simulations` | Simulations |
| `/users` | Users / team directory |
| `/logs` | Unified event stream |
| `/profile` | Profile and password change |

## Docs

See [../docs/web-app.md](../docs/web-app.md) for the API client, auth flow, and
theme details.
