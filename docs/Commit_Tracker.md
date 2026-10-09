# Weekly Commit Tracker (Capstone Appendix C)

Repository: `sivaneshk23/AI-Dataset-Labeling-Marketplace`
Program: 60-day full-stack capstone · Python / FastAPI track
Day 1 of the programme: **2026-07-31** · Day 60: **2026-09-28** · Last delivery: **2026-09-20**

The table below is filled from `git log --date=short --pretty=format:"%ad %s"` and is kept in the
repository so the guide can compare the commit graph with this tracker.

| Wk | Days | Date range | Target | Actual | Focus & notes | Sign-off |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1–7 | 2026-07-31 → 2026-08-02 | ≥ 3 | 4 | Problem statement, planning docs, repository setup, first PR merges | |
| 2 | 8–14 | 2026-08-03 → 2026-08-09 | ≥ 3 | 6 | Backend scaffold, architecture/ER/module diagrams, database foundation, user & dataset models | |
| 3 | 15–21 | 2026-08-10 → 2026-08-16 | ≥ 3 | 6 | Dataset API + UI, job workflow, assignment workflow, review workflow, Review-I completion | |
| 4 | 22–28 | 2026-08-17 → 2026-08-23 | ≥ 3 | 1 | Role-based permissions committed on 2026-08-17 (branch `feature/review1-completion`) | |
| 5 | 29–35 | 2026-08-24 → 2026-08-30 | ≥ 3 | 0 | Annotation workflow, quality review, analytics and export implemented but not yet committed | |
| 6 | 36–42 | 2026-08-31 → 2026-09-06 | ≥ 3 | 0 | Security baseline, CI pipelines, hosting configuration implemented but not yet committed | |
| 7 | 43–49 | 2026-09-07 → 2026-09-13 | ≥ 3 | 0 | Enhancement research and AI assistant implemented but not yet committed | |
| 8 | 50–56 | 2026-09-14 → 2026-09-20 | ≥ 3 | 15 | Review-II and Review-III work committed and merged through PRs (`feature/review2-full-product`, `feature/ai-annotation-assistant`) | |
| 9 | 57–60 | 2026-09-20 → 2026-09-28 | ≥ 2 | (in Wk 8 count) | Documentation freeze, README v3, demo script, CHANGELOG, final polish | |

Cumulative commits after the Week 8 push: **39** (programme floor is 26).

## Honest note on the cadence gap

Weeks 5–7 contain no commits. The modules built in those weeks (annotation tasks, annotations,
quality review, analytics, export, security baseline, CI/CD and the AI enhancement) were developed
locally and committed together in Weeks 8 on two feature branches. The single-week count of 15
therefore exceeds the weekly floor but does not repair the missing weekly spread of Weeks 5–7.

Actions taken instead of rewriting history:

1. Every commit message follows Conventional Commits and each commit is one logical change
   (feat / fix / test / docs / chore / ci), so the commit graph is reviewable.
2. The work is merged through pull requests rather than direct pushes.
3. This tracker records the real dates, so the gap is visible and can be discussed openly at the
   review instead of being hidden.

## Branch and pull-request log

| Branch | Purpose | Pull request |
| --- | --- | --- |
| `docs/week2-system-design` | Design documents and diagrams v1 | PR #1 |
| `feat/week2-backend-scaffold` | Backend scaffold and module design | PR #2 |
| `feature/review1-mvp` | MVP feature work for Review-I | merged into `main` |
| `feature/review1-completion` | Role-based permissions and Review-I completion | PR (merged) |
| `feature/review2-full-product` | Review-II: annotation workflow, analytics, export, security, CI/CD, docs | PR (merged) |
| `feature/ai-annotation-assistant` | Review-III: AI annotation assistant and quality control | PR (merged) |

## Definition of Done checklist (applied before every merge)

| Check | Status |
| --- | --- |
| Code self-reviewed against the checklist | Done |
| No hardcoded secrets, passwords or API keys | Done — `.env` is git-ignored, only `.env.example` is committed |
| No leftover debug statements | Done — debug prints removed; logging goes through the logger |
| All existing and new tests pass | Done — `pytest -q` green |
| No console errors in the browser | Verified on the seeded local stack |
| UI checked at mobile and desktop widths | Done — responsive layout with breakpoints |
| Conventional Commit messages | Done |
| Merged via pull request | Done |
| README updated when behaviour changed | Done — README v3 |
