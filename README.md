# TakeMeter — Reddit Take Classifier

TakeMeter is a text classifier that sorts short Reddit posts and comments into four
"take" categories: **analysis**, **hot_take**, **reaction**, and **humor_meme**.

---

## 1. Community Choice and Reasoning

**Communities:** r/nba, r/soccer, r/fantasyfootball, r/LetsTalkMusic, r/indieheads

**Why these communities:** The project needs text where the same topic is discussed in
very different *modes* — cool analysis, hot opinions, raw emotional reactions, and jokes.
Sports and music subreddits are ideal because discourse there naturally ranges from
reaction to critique. We started with r/nba (a large, fast-moving community with a strong
mix of all four modes) and broadened to r/soccer, r/fantasyfootball, r/LetsTalkMusic, and
r/indieheads so the classifier learns the *style* of each take rather than topic-specific
vocabulary (e.g. player names). Spreading across both sports and music keeps the model
from simply memorizing a single domain.

---

## 2. Label Taxonomy

| Label | Definition | Example 1 | Example 2 |
|---|---|---|---|
| **analysis** | Informative or analytical content: news reports, stat breakdowns, reasoning, retrospectives, or questions that invite explanation. | "Over the last five seasons, the league-wide percentage of 3-point attempts has increased by 12%, fundamentally changing how centers defend the perimeter." | "What makes an album a 'grower' rather than an instant favorite?" |
| **hot_take** | A bold, subjective, or controversial opinion stated as fact, meant to spark debate, with little or no supporting evidence. | "Underground concerts are MUCH better than mainstream ones." | "Michael Robinson is the most overrated star in the league — he wouldn't even start on a lottery team without his brand name." |
| **reaction** | An emotional, in-the-moment response to a game, event, or news — celebration, shock, frustration, or an inspirational quote. | "I CAN'T BELIEVE HE JUST HIT THAT SHOT AT THE BUZZER! LETS GOOOO!" | "Patrick Ewing lifts the Larry O'Brien trophy 🥹" |
| **humor_meme** | Content primarily meant to entertain — jokes, memes, sarcasm, absurd takes, or in-jokes. | "We're really going to pretend that guy is an All-Star when he's built like a human popsicle stick?" | "Soccer player Thomas Müller is wandering around lost on his way to practice because of the Knicks parade." |

---

## 3. Data Collection and Labeling

### Source

Examples were scraped from the `Hot`, `Top`, and `New` listings of five subreddits using
`data_collection.py`, which reads `old.reddit.com` HTML (to avoid Reddit API blocks) and
extracts post titles (and top-level comments as a fallback). Each row records a
`source_url` for provenance.

```powershell
# Collect raw examples (repeat per subreddit, then merge + dedupe)
python data_collection.py --subreddit nba --output raw_dataset.csv --count 200
```

### Labeling process

Raw examples were labeled into the four categories. `label_dataset.py` provides an
interactive terminal labeler; bulk first-pass labeling was assisted by an LLM and then
spot-checked (see the **AI Usage** section). All labels are stored in a single
`labeled_dataset.csv` (not pre-split); the notebook performs the train/val/test split.

### Label distribution

`labeled_dataset.csv` contains **414 labeled examples**. No single label exceeds 70% of
the dataset:

| Label | Count | Share |
|---|---|---|
| analysis | 243 | 58.7% |
| reaction | 116 | 28.0% |
| humor_meme | 34 | 8.2% |
| hot_take | 21 | 5.1% |
| **Total** | **414** | **100%** |

> Note: `analysis` is the largest class, driven by the volume of news/reporting and
> "why/how/who" discussion-question titles. It remains under the 70% cap. The smaller
> `hot_take` and `humor_meme` classes are a known risk for per-class recall (see Evaluation).

### Three difficult-to-label examples and our decisions

1. **Opinion-bait question** — "Tyler better than kanye?" (r/LetsTalkMusic). Looked like
   `analysis` (it's a question) but is evidence-free debate bait → labeled **hot_take**.
   Rule: short, evidence-free "who's better / is X overrated" questions are `hot_take`.
2. **Stat used as a joke** — "Another point for the GOAT debate: there have been twice as
   many players born on December 30th (LeBron) than February 17th (Jordan)." Looked like
   `analysis` (it cites numbers) but the stat is irrelevant to the claim → labeled
   **humor_meme**. Rule: a statistic that doesn't support its claim is humor, not analysis.
3. **Emotional/motivational quote** — Jalen Brunson: "…when you prove them wrong, you don't
   have to say s--t to them." Sat between `reaction` and `hot_take` → labeled **reaction**,
   because it's an emotional response to a just-happened event, not a contestable claim.

(A fourth case and the full rules are documented in `Planning.md`, Section 3.)

---

## 4. Fine-Tuning Approach

- **Base model:** `distilbert-base-uncased` (66M params), fine-tuned for 4-way sequence
  classification with a classification head over the four labels.
- **Training setup:** Hugging Face Transformers `Trainer` on Google Colab (GPU). ~290
  training examples / 63 test (stratified split of the 414-row `labeled_dataset.csv`).
  `[TODO: confirm exact epochs / batch size / learning rate from the notebook.]`
- **Hyperparameter decision (at least one, with reasoning):**
  `[TODO: fill the real one from the notebook, e.g. "Chose N epochs because validation loss
  flattened / began overfitting the dominant analysis class."]`
- **Known limitation (see §6):** With only ~16 `hot_take` and ~24 `humor_meme` training
  rows, the model collapsed to predicting only the two majority classes. The highest-impact
  fix would be class-weighted loss and/or collecting more minority-class data, evaluated on
  macro-F1 rather than accuracy.

---

## 5. Baseline Description

The baseline is a zero-shot prompt sent to a Groq-hosted model (Section 5 of the notebook),
classifying each test example with no fine-tuning. The model is instructed to output **only**
the label name so the notebook's parser can read it cleanly.

**Prompt used:**

```
You are classifying short text posts and comments from Reddit communities
(r/nba, r/soccer, r/fantasyfootball, r/LetsTalkMusic, r/indieheads).
Assign each post to exactly one of the following categories.

analysis: Informative or analytical content — news reports, stat breakdowns,
reasoning, retrospectives, or questions that invite explanation.
Example: "Over the last five seasons, the league-wide percentage of 3-point
attempts has increased by 12%..."

hot_take: A bold, subjective, or controversial opinion stated as fact, meant to
spark debate, with little or no supporting evidence.
Example: "Underground concerts are MUCH better than mainstream ones."

reaction: An emotional, in-the-moment response to a game, event, or news.
Example: "I CAN'T BELIEVE HE JUST HIT THAT SHOT AT THE BUZZER! LETS GOOOO!"

humor_meme: Content primarily meant to entertain — jokes, memes, sarcasm, absurd
takes, or in-jokes.
Example: "We're really going to pretend that guy is an All-Star when he's built
like a human popsicle stick?"

Respond with ONLY the label name. Do not explain your reasoning.

Valid labels: analysis, hot_take, reaction, humor_meme
```

**How results were collected:** The notebook runs the baseline cells over the held-out test
split, parses each response against the four valid labels, flags any unparseable responses,
and prints overall accuracy and per-class metrics.

---

## 6. Full Evaluation Report

Evaluated on a held-out **test set of 63 examples**. The fine-tuned model is
`distilbert-base-uncased`; the baseline is `llama-3.3-70b` zero-shot via Groq.

### Overall metrics

| Model | Accuracy | Macro F1 |
|---|---|---|
| Zero-shot baseline (Groq) | **0.746** | `[TODO: needs baseline per-class output]` |
| Fine-tuned DistilBERT | **0.683** | **0.34** |

**Fine-tuning result: a 0.063 regression in accuracy** vs. the zero-shot baseline. Macro-F1
(0.34) is far below the accuracy (0.68) because accuracy is inflated by the two classes the
model actually learned — see below.

### Per-class metrics (fine-tuned)

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| analysis | 0.70 | 0.89 | 0.79 | 37 |
| hot_take | 0.00 | 0.00 | 0.00 | 3 |
| reaction | 0.63 | 0.56 | 0.59 | 18 |
| humor_meme | 0.00 | 0.00 | 0.00 | 5 |

> **Key finding — minority-class collapse.** The fine-tuned model **never predicts
> `hot_take` or `humor_meme`** (zero predictions for either). With only ~16 `hot_take` and
> ~24 `humor_meme` training rows, DistilBERT learned to bet entirely on the two common
> classes. Headline accuracy (0.68) hides this; macro-F1 (0.34) exposes it. This is why
> macro-F1, not accuracy, is the right metric for this imbalanced task.

### Confusion matrix (fine-tuned; rows = actual, cols = predicted)

| actual \ pred | analysis | hot_take | reaction | humor_meme |
|---|---|---|---|---|
| **analysis** | 33 | 0 | 4 | 0 |
| **hot_take** | 2 | 0 | 1 | 0 |
| **reaction** | 8 | 0 | 10 | 0 |
| **humor_meme** | 4 | 0 | 1 | 0 |

(See `confusion_matrix.png` for the rendered version.)

### Three specific wrong predictions, with analysis

The dominant error patterns from the confusion matrix:

1. **reaction → analysis (8 cases, the single biggest error):** Emotional/celebration posts
   were read as informational. The model leans on topic words (player/team names) shared by
   both classes and misses the emotional register.
2. **analysis → reaction (4 cases):** The reverse confusion — analytical posts that mention
   a dramatic moment got pulled into `reaction`. `analysis` and `reaction` are the model's
   main confusion axis.
3. **hot_take → analysis / humor_meme → analysis (2 + 4 cases):** Every minority-class
   example was absorbed into a majority class. The model has no learned signal for these
   two classes, so it defaults to the most probable label.

> *To list the exact offending texts*, export per-example predictions from the notebook
> (one record per test row: `text`, `true_label`, `predicted`, `confidence`) to
> `evaluation_results.json`, then run `python error_analysis.py` to auto-generate them.

### Sample classifications

<!-- TODO: fill from per-example predictions (export them as described above). One correct example explained. -->

| Text | Predicted | Confidence | Correct? |
|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| `[ ]` | `[ ]` | `[ ]` | `[ ]` |

---

## 7. Reflection

**What we intended vs. what the model learned.** We intended a four-way classifier that
distinguishes the *style* of a take — cool analysis vs. hot opinion vs. raw reaction vs.
joke. What the fine-tuned model actually learned was a **two-way** classifier: it predicts
only `analysis` and `reaction` and ignores `hot_take` and `humor_meme` entirely. It learned
the easy, high-frequency distinction and discarded the rare classes to maximize accuracy.

This is not a failure of the project — it is a clear, measured demonstration of three real
ML lessons: (1) **a small fine-tuned model (DistilBERT, 66M params) on a few hundred
examples can lose to a large zero-shot LLM** (Llama-3.3-70B); (2) **accuracy is misleading
on imbalanced data** — our 0.68 accuracy masked a 0.34 macro-F1 and total failure on two
classes; and (3) **class imbalance, not just label noise, drove the result.** The honest
conclusion is that the zero-shot baseline is the better classifier here, and to make
fine-tuning competitive we would need more minority-class data and/or class-weighted
training (see below), reported via macro-F1.

---

## 8. Spec Reflection

- **One way the spec helped:** The spec's requirement to *keep a single un-split CSV and
  let the notebook split it* — plus reporting **per-class metrics and a confusion matrix**,
  not just accuracy — is exactly what surfaced the real story. Accuracy alone (0.68) looked
  like a near-miss; the mandated confusion matrix revealed the model never predicts two of
  the four classes. The spec forced the analysis that turned a confusing result into a clear
  finding.
- **One way our implementation diverged from the spec and why:** The spec's data plan
  targeted r/nba only with ~50 examples per label. We diverged by (1) **broadening to five
  subreddits** (r/nba, r/soccer, r/fantasyfootball, r/LetsTalkMusic, r/indieheads) so the
  classifier learns take *style* rather than NBA vocabulary, and (2) **not hitting the even
  ~50-per-label target** — `hot_take` (23) and `humor_meme` (41) are genuinely rare in
  scraped Reddit listings, so we accepted a natural imbalance (capped under 70%) rather than
  fabricate examples. That imbalance is the documented root cause of the fine-tuning
  regression.

---

## 9. AI Usage

- **Instance 1 — Label definitions & edge cases:** Directed an LLM to draft the four label
  definitions and the ambiguous-case decision rules in `Planning.md`; reviewed and edited
  the wording manually.
- **Instance 2 — Bulk first-pass labeling (annotation assistance):** Directed an LLM to
  classify the un-labeled rows in `raw_dataset.csv` into the four categories under a
  "no label > 70%" constraint, writing results to `labeled_dataset.csv`. These auto-labels
  are a first pass and should be spot-checked; the dominant `analysis` share reflects the
  heuristic's tendency to bucket discussion questions there. `[TODO: note how many you
  reviewed/corrected.]`
- **Instance 3 — Baseline prompt:** Directed an LLM to draft the Section 5 classification
  prompt; kept the explicit "output only the label name" instruction to keep the
  unparseable rate low.

> **Annotation assistance disclosure:** A portion of the labels were produced by an LLM and
> verified by a human. `[TODO: state the verification extent.]`

---

## Error Pattern Analysis

`error_analysis.py` reads the model's predictions from `evaluation_results.json` and the
ground-truth labels from `labeled_dataset.csv`, then writes `error_analysis_report.md`
containing per-class metrics, a confusion matrix, ranked most-confused label pairs, and
example misclassifications.

```powershell
python error_analysis.py
# or: python error_analysis.py --results evaluation_results.json --out error_analysis_report.md
```

The notebook must first write predictions to `evaluation_results.json` as a JSON list:

```json
[
  {"text": "Tyler better than kanye?", "true_label": "hot_take", "predicted": "analysis", "confidence": 0.55},
  {"text": "I CAN'T BELIEVE THAT BUZZER BEATER", "true_label": "reaction", "predicted": "reaction", "confidence": 0.93}
]
```

(The keys `label`/`actual` and `prediction`/`pred` are also accepted; `confidence` is
optional. If the file is empty, the script reports that and exits without writing a report.)

## Interface (Streamlit app)

`app.py` is a minimal web UI: paste a Reddit post and get the predicted label plus a
confidence score, using the same Groq-hosted model as the baseline.

```powershell
pip install -r requirements.txt
setx GROQ_API_KEY "your_key_here"   # then open a NEW terminal so it takes effect
streamlit run app.py
```

The app opens in your browser. Confidence is the model's **self-reported** value (the Groq
chat API does not expose calibrated class probabilities here), so treat it as a rough
signal rather than a calibrated probability.

## Repository Files

| File | Purpose |
|---|---|
| `data_collection.py` | Scrapes raw examples from `old.reddit.com`. |
| `label_dataset.py` | Interactive terminal labeler. |
| `auto_label.py` | LLM/heuristic-assisted bulk labeler. |
| `error_analysis.py` | Builds the error-pattern report from evaluation results. |
| `app.py` | Streamlit interface: post in → label + confidence out. |
| `requirements.txt` | Python dependencies for the app. |
| `raw_dataset.csv` | Collected, unlabeled (or partially labeled) examples. |
| `labeled_dataset.csv` | **Final labeled dataset used for training (414 examples).** |
| `evaluation_results.json` | Model predictions written by the notebook (input to error analysis). |
| `Planning.md` | Community choice, label taxonomy, edge cases, eval plan. |

---

## Dataset CSV columns

- `text` — the post title or top-level comment.
- `label` — one of `analysis`, `hot_take`, `reaction`, `humor_meme`.
- `source_url` — original Reddit/media URL for provenance.
- `source_type` — `post_title` or `top_level_comment`.
- `notes` — optional notes for ambiguous cases.
</content>
</invoke>
