# TakeMeter Technical Blog Post

## Overview
TakeMeter is a Reddit text classifier built to distinguish four different "take" styles:

- `analysis`
- `hot_take`
- `reaction`
- `humor_meme`

The project focuses on classifying short Reddit posts and comments from communities like `r/nba`, `r/soccer`, `r/fantasyfootball`, `r/LetsTalkMusic`, and `r/indieheads`.

## Project Goals

- Build a classifier that identifies writing style and intent, not just topic.
- Separate discussion-style analysis from emotional reaction and opinionated hot takes.
- Add a small interface for live testing and demoing.
- Document failure modes and keep the evaluation reproducible.

## Data and Labels

### Dataset
- `labeled_dataset.csv` contains the hand-labeled examples.
- Each row includes the text and one of the four labels.
- The dataset was built from Reddit post titles and top comments.

### Label definitions
- `analysis`: Informative or analytical content — stats, reasoning, explanations, or discussion prompts.
- `hot_take`: Bold, controversial opinion offered as fact, usually with little evidence.
- `reaction`: Emotional, in-the-moment response to an event.
- `humor_meme`: Jokes, sarcasm, memes, and absurd content.

## Baseline Model

The baseline is a zero-shot Groq-hosted model used with a prompt-based classification flow.

### How the baseline is assessed
- Each test example is sent through the prompt classifier.
- The model is instructed to respond with one of the four labels only.
- Predictions are compared to the ground truth.
- Metrics include accuracy, macro F1, and unparseable rate.

## Interface and Demo

### `app.py`
- A Streamlit interface that lets you paste a Reddit post.
- The app shows the predicted label and confidence.
- Demo posts were added to the sidebar to make live demos easy.

### `run_classifier.py`
- A CLI fallback for environments where Streamlit is not available.
- Uses the same classification logic from `app.py`.

## Implementation Notes

### Environment
- Uses `python-dotenv` to load `GROQ_API_KEY` from `.env`.
- `requirements.txt` includes:
  - `streamlit`
  - `groq`
  - `python-dotenv`

### Classification logic
- The model prompt is stored in `app.py`.
- Inference is performed by `classify(text, model)`.
- The response is parsed for JSON containing `label` and `confidence`.

## What to do next

- Add more labeled examples for underrepresented classes (`hot_take`, `humor_meme`).
- Use a fine-tuned classifier or improve the prompt for better minority-class performance.
- Add a proper evaluation notebook that writes `evaluation_results.json`.
- Generate a more detailed error analysis report with `error_analysis.py`.

## Brain refresher notes

- `app.py`: live demo UI
- `run_classifier.py`: CLI demo fallback
- `.env`: place `GROQ_API_KEY=...`
- `README.md`: project overview + baseline prompt
- `blog_post.md`: this quick technical summary

## Quick run commands

```powershell
pip install -r requirements.txt
streamlit run app.py
```

or

```powershell
python run_classifier.py
```
