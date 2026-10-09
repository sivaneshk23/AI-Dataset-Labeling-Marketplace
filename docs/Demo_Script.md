# Demo Video Script (2–4 minutes)

Record with Loom, OBS or a phone screen recorder. Keep the browser at 1440×900, zoom to 100% and
prepare the seeded database (`python -m scripts.seed_demo_data`) before recording.

| Time | Scene | What to show |
| --- | --- | --- |
| 0:00–0:15 | Title | "AI Dataset Labeling Marketplace — a full-stack platform for managing dataset annotation projects." Show the sign-in screen. |
| 0:15–0:35 | Sign in as Dataset Owner | `owner@marketplace.dev` / `Password123`. Point out the JWT login, the role badge and the owner navigation. |
| 0:35–1:00 | Dataset & job | Create a dataset, then a labeling job on it. Open the job and show the status and record count. |
| 1:00–1:25 | Import & assign | Paste five records into the bulk importer (show that duplicates are skipped) and assign them to the annotator. |
| 1:25–2:00 | **AI assistant (enhancement)** | Sign in as `annotator@marketplace.dev`, open the workspace, show the AI suggestion panel: suggested label, confidence and alternatives. Accept the suggestion for one record and type a different label for another. |
| 2:00–2:30 | Quality review | Back as the owner: open Quality Review, show the AI quality score, the flags with severity and the recommendation, then approve one label and request a revision on the other. Point out that the task state changes and that the job completes when everything is approved. |
| 2:30–2:50 | Analytics & export | Show the dashboard tiles (tasks by status, completion %, AI coverage, AI agreement) and download the CSV export; open it to show the AI agreement and review columns. |
| 2:50–3:10 | Engineering evidence | Open the GitHub repository: the Actions tab (green lint + test pipeline), `docs/diagrams/` (architecture, ER, module diagrams), and `pytest -q` output showing the passing suite with coverage. |
| 3:10–3:30 | Close | "AI assists, humans decide" — recap: layered FastAPI backend, React SPA, PostgreSQL, CI/CD to Render and Vercel, and an AI enhancement that plugs into the existing workflow. |

## Recording checklist

- [ ] Backend running on `http://localhost:8000`, frontend on `http://localhost:5173`
- [ ] Database seeded so every screen has data
- [ ] Browser zoom 100%, no other tabs, notifications off
- [ ] Microphone tested; speak the names of the modules as you open them
- [ ] Upload the video (Loom / YouTube unlisted) and paste the link into the README "Live Demo" table
