# Enhancement Proposal — AI Annotation Assistant & Quality Control

**Project:** AI Dataset Labeling Marketplace
**Phase:** Day 42–59 (Review-III enhancement)
**Branch:** `feature/ai-annotation-assistant`
**Author:** Sivanesh K

## 1. Problem

The base product (Review-I/II) lets dataset owners create datasets, upload source records, configure labeling jobs, assign records
to annotators, review submitted labels and export the approved dataset. Using it end-to-end revealed
three concrete gaps:

1. **Annotators start from a blank field.** Every label must be typed from scratch even when the
   record is almost identical to a record already labeled in the same job. This is the slowest part
   of a labeling round and the main source of inconsistent label wording (`refund` vs
   `refund request` vs `Refund Request`).
2. **Reviewers have no quality signal.** A reviewer opening the quality screen sees a label and a
   comment box, but nothing tells them which of the fifty submitted labels deserve attention first,
   whether an annotator is repeating the same label, or whether the label distribution has become
   unrealistic.
3. **Owner-level quality is invisible.** The dashboard reported volume (tasks, annotations, pending
   reviews) but not quality: no agreement rate, no AI coverage, no flagged records. A dataset could
   therefore be exported while still containing doubtful labels.

The capstone brief requires the enhancement to be a *new component integrated into the same live
product*, not a separate demo app, and to support the project's specialisation (AI-assisted
annotation).

## 2. Solution Approach

One pipeline is added to the existing workflow, using the data already stored in the platform:

```text
Annotator opens a task
      |
      v
AIService.suggest_label()  --> provider registry --> Gemini API (when GEMINI_API_KEY is set)
      |                                          \-> offline similarity engine (always available)
      |                                 learns from labels already produced in the same job
      v
Suggestion shown in the workspace (label + confidence + alternatives) - annotator accepts or edits
      |
      v
Annotation saved with ai_suggested_label / ai_confidence (used later for agreement metrics)
      |
      v
AIService.evaluate_annotation()  --> rule-based quality engine (score 0-100, flags, recommendation)
      |
      v
AIService.job_insights()  --> agreement rate, AI coverage, distribution, duplicates,
                              flagged records, per-annotator stats, written recommendations
```

Three integration points, all inside the existing modules:

| Integration point | Existing module extended | What it adds |
| --- | --- | --- |
| Pre-labelling | `services/annotation_service.py`, annotator workspace page | Suggestion stored on the annotation for agreement measurement |
| Annotation quality | `api/ai.py`, quality review page | Quality score, flags, severity, recommendation per annotation |
| Job insights | `api/ai.py`, dashboard/analytics | Job-level quality report with flagged records and recommendations |

### Design decisions

- **Graceful degradation first.** Providers implement one small protocol
  (`suggest(input_text, candidate_labels, examples)`). If the external provider fails or no API key is
  configured, the registry silently falls back to the offline engine, so the labeling workflow can
  never be blocked by a third-party outage.
- **Learn from the job, not from a global model.** Training signal = the labels already submitted or
  approved in the *same* job. That keeps suggestions domain-accurate, needs no model training
  infrastructure and works on the free hosting tier.
- **Rule-based quality scoring, not a black box.** The quality engine is a pure function over
  aggregates (label length, confidence vs threshold, AI agreement, distribution dominance,
  repetition). Every rule is deterministic, unit-testable and explainable to a reviewer.
- **Nothing is auto-approved.** AI only *suggests* and *flags*; a human reviewer always makes the
  final decision, keeping the platform consistent with the problem statement ("AI assists, it does
  not replace annotators").


## 3. Technology Choice

| Option | Decision | Reason |
| --- | --- | --- |
| Gemini API (`google-genai`) | **Chosen as the optional external provider** | Free tier, simple JSON prompting, no model hosting; enabled purely by setting `GEMINI_API_KEY` |
| Offline TF-based similarity engine | **Chosen as the default and fallback** | Deterministic, zero cost, no network, fully unit-testable in CI, always available |
| Scikit-learn / sentence-transformers | Rejected | Heavy dependencies and model files for little gain over the lexical baseline on short records |
| Fine-tuning a classifier | Rejected | Needs curated training data the platform does not have yet |
| Separate microservice for AI | Rejected | Would break the "clean integration into the same live product" requirement |

Configuration is environment-driven, so switching providers requires no code change:

```env
AI_PROVIDER=auto            # auto | local | gemini
GEMINI_API_KEY=             # empty -> offline engine
GEMINI_MODEL=gemini-2.0-flash
AI_MIN_CONFIDENCE=0.55      # suggestions below this confidence are flagged for review
```

## 4. Scope of Work

In scope (delivered):

- `services/ai/` package: `base.py` (protocol + DTOs), `local_provider.py`, `gemini_provider.py`,
  `quality.py` (rule engine), `__init__.py` (provider registry with caching and fallback)
- `services/ai_service.py`: `suggest_label`, `candidate_label_set`, `approved_examples`,
  `evaluate_annotation`, `count_repetitions`, `job_insights`, `build_recommendations`
- REST endpoints under `/api/ai/`: provider status, label suggestion, job insights, annotation quality
- Annotation schema additions: `ai_suggested_label`, `ai_confidence`
  (migration `database/migrations/002_annotation_workflow.sql`)
- Dataset upload and source-record persistence integrated before task creation
  (migration `database/migrations/003_dataset_upload_and_job_labels.sql`)
- Frontend: AI suggestion panel in the annotation workspace, quality review panel, analytics tiles
- Export columns: `ai_suggested_label`, `ai_confidence`, `ai_agreement`

Out of scope (recorded as future work): active-learning queues, multi-annotator agreement scoring,
image/audio record support, model fine-tuning, per-project custom label taxonomies.

## 5. Success Criteria

| Criterion | Target | Result |
| --- | --- | --- |
| Suggestion available for a record with label history | Under 200 ms, no network needed | Offline engine answers in-process |
| Workflow never blocked by an AI failure | Fallback always returns a suggestion object | Covered by `test_provider_failures_degrade_to_the_offline_engine` |
| Quality score explainable | Score + flags with severity + recommendation | Delivered in the review panel and API response |
| Enhancement test coverage | Unit tests for each component | Provider, registry, engine and service tests all pass |
| Integrated, not bolted on | Same tables, same pages, same API envelope | AI fields live on existing annotations; exports include AI agreement |
| Reviewer value visible | Flagged records and recommendations on the job screen | `GET /api/ai/jobs/{id}/insights` |

## 6. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| External AI quota or outage | Registry falls back to the offline engine and logs a warning |
| Biased suggestions from few examples | `AI_MIN_CONFIDENCE` threshold, alternatives shown, human approval mandatory |
| Cost of external calls | Suggestions reuse the job's own label set; `AI_PROVIDER=local` disables calls entirely |
| Reviewers trusting the score blindly | Score, flags and recommendation are always shown next to the raw label and its history |
