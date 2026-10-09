# Deployment Guide — Review-II / Final

## Target topology

```text
Vercel React frontend
        |
        | HTTPS / JSON / multipart
        v
Render FastAPI backend
        |
        v
Managed PostgreSQL
```

Optional external AI:

```text
FastAPI AI service -> Google Gemini
                  \-> local similarity fallback
```

## Render

1. Push the repository to the real public GitHub repository.
2. Create a Render Blueprint from `render.yaml`.
3. Confirm the managed PostgreSQL database is provisioned.
4. Set `CORS_ORIGINS` to the exact Vercel frontend origin.
5. Set a strong generated `SECRET_KEY`.
6. Keep `AI_PROVIDER=local` for deterministic zero-cost operation, or use `auto` with a Gemini key.
7. Confirm `/health` and `/docs` return successfully.

## Vercel

1. Import `frontend/` as the Vercel project.
2. Set `VITE_API_URL` to the public Render API URL.
3. Build with `npm run build`.
4. Confirm the SPA routes and login flow work from a clean browser.

## GitHub Actions secrets

Configure:

- `RENDER_DEPLOY_HOOK`
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

Never put any of these values in YAML or source files.

## Production smoke test

After every deployment:

1. `GET /health` returns HTTP 200 and `data.status=healthy`.
2. `/docs` loads.
3. Owner registration/login works.
4. Dataset creation works.
5. CSV upload works and the record count changes.
6. Labeling job creation and label vocabulary work.
7. Uploaded records become tasks.
8. Annotator sees only assigned tasks.
9. AI suggestion works for the assigned task.
10. Annotation submission works.
11. Owner review works.
12. Approved export downloads successfully.
13. Browser console has no unhandled errors.

## External dependency note

The codebase and deployment configuration can be prepared without account access. The actual public deployment, secret configuration and live smoke test must be performed by the project owner.
