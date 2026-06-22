"""Lightweight Streamlit interface for the TakeMeter classifier.

Paste a Reddit post and get a predicted label (analysis / hot_take / reaction /
humor_meme) plus a confidence score, using the same Groq-hosted model as the
notebook baseline.

Run:
    pip install -r requirements.txt
    setx GROQ_API_KEY "your_key_here"      # Windows (new terminal after)
    streamlit run app.py

Note on confidence: Groq's chat API does not expose calibrated class
probabilities here, so the score is the model's *self-reported* confidence
(0-1). Treat it as a rough signal, not a calibrated probability.
"""

import json
import os

from dotenv import load_dotenv
import streamlit as st

load_dotenv()

LABELS = ["analysis", "hot_take", "reaction", "humor_meme"]
MODEL_MODES = ["Fine-tuned DistilBERT", "Groq prompt model", "Both (compare)"]
DEFAULT_MODEL = "llama-3.3-70b-versatile"
# Your fine-tuned model directory (downloaded from Colab). NOT the untrained base model.
DEFAULT_LOCAL_MODEL = "takemeter-model"

DEMO_POSTS = {
    "Hot take about a player": "Hot take: this player is already the most overrated superstar in the league and will never win a Finals MVP.",
    "Analysis of team performance": "If you look at their pace and true shooting percentage over the last five games, it’s clear the defense is the real reason they’re winning.",
    "Emotion-packed reaction": "I can’t believe that buzzer-beater just happened — I screamed so loud I woke up the whole house!",
    "Music thread humor": "That meme about the artist releasing a deluxe edition every two months is peak music Twitter energy.",
    "Controversial roster opinion": "If they don’t trade him before the deadline, this team is throwing away the season."
}

SYSTEM_PROMPT = """You are classifying short text posts and comments from Reddit communities
(r/nba, r/soccer, r/fantasyfootball, r/LetsTalkMusic, r/indieheads).
Assign the post to exactly one of these categories:

analysis: Informative or analytical content - news, stat breakdowns, reasoning,
retrospectives, or questions that invite explanation.
hot_take: A bold, subjective, or controversial opinion stated as fact, meant to
spark debate, with little or no supporting evidence.
reaction: An emotional, in-the-moment response to a game, event, or news.
humor_meme: Content primarily meant to entertain - jokes, memes, sarcasm, absurd takes.

Respond with ONLY a JSON object, no prose, in exactly this form:
{"label": "<one of: analysis, hot_take, reaction, humor_meme>", "confidence": <number 0-1>}
The confidence is how sure you are of the label."""


def classify_groq(text, model):
    """Return (label, confidence, raw) using the Groq chat API."""
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set in the environment or .env file. "
            "Set GROQ_API_KEY in your shell or create a .env file with GROQ_API_KEY=..."
        )

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    raw = response.choices[0].message.content.strip()

    label, confidence = None, None
    try:
        start, end = raw.find("{"), raw.rfind("}")
        parsed = json.loads(raw[start : end + 1])
        label = str(parsed.get("label", "")).strip().lower()
        confidence = float(parsed.get("confidence")) if parsed.get("confidence") is not None else None
    except (ValueError, json.JSONDecodeError):
        for candidate in LABELS:
            if candidate in raw.lower():
                label = candidate
                break

    if label not in LABELS:
        label = None
    return label, confidence, raw


@st.cache_resource(show_spinner="Loading fine-tuned model...")
def load_local(local_model_name):
    """Load and cache the fine-tuned DistilBERT so it isn't reloaded each click."""
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
    except ImportError:
        raise RuntimeError(
            "Local DistilBERT inference requires transformers and torch. "
            "Install them with `pip install transformers torch`."
        )
    tokenizer = AutoTokenizer.from_pretrained(local_model_name)
    model = AutoModelForSequenceClassification.from_pretrained(local_model_name)
    model.eval()
    return tokenizer, model


def classify_local(text, local_model_name):
    """Return (label, confidence, raw) from the local fine-tuned model (real softmax)."""
    import torch

    if not os.path.isdir(local_model_name):
        raise RuntimeError(
            f"Model dir '{local_model_name}' not found. Download your fine-tuned model "
            "from Colab and place it here (see README)."
        )

    tokenizer, model = load_local(local_model_name)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        logits = model(**inputs).logits[0]

    if not hasattr(model.config, "id2label") or len(model.config.id2label) != len(LABELS):
        raise RuntimeError(
            f"Local model '{local_model_name}' must have {len(LABELS)} labels in config.id2label."
        )

    probs = torch.softmax(logits, dim=-1).tolist()
    index = int(torch.argmax(logits).item())
    label = model.config.id2label[index].lower()
    confidence = float(probs[index])
    all_probs = {model.config.id2label[i].lower(): round(float(probs[i]), 3) for i in range(len(probs))}
    raw = json.dumps({"label": label, "confidence": round(confidence, 3), "all_probs": all_probs}, indent=2)

    if label not in LABELS:
        label = None
    return label, confidence, raw


def render_panel(title, conf_caption, classify_fn):
    """Run one classifier and render its result in the current container."""
    st.subheader(title)
    try:
        label, confidence, raw = classify_fn()
    except Exception as error:  # noqa: BLE001 - surface any API/setup error to the UI
        st.error(f"Failed: {error}")
        return
    if label is None:
        st.error("Could not parse a valid label.")
        st.code(raw)
        return
    st.success(f"Predicted: **{label}**")
    if confidence is not None:
        st.metric(conf_caption, f"{confidence:.0%}")
        st.progress(min(max(confidence, 0.0), 1.0))
    with st.expander("Raw model output"):
        st.code(raw)


def main():
    st.set_page_config(page_title="TakeMeter", page_icon="📊", layout="wide")
    st.title("📊 TakeMeter")
    st.caption("Classify a Reddit post as analysis, hot_take, reaction, or humor_meme.")

    with st.sidebar:
        mode = st.selectbox("Model mode", MODEL_MODES)
        local_model_name = st.text_input("Fine-tuned model dir", value=DEFAULT_LOCAL_MODEL)
        groq_model = st.text_input("Groq model", value=DEFAULT_MODEL)

        needs_groq = mode in ("Groq prompt model", "Both (compare)")
        needs_local = mode in ("Fine-tuned DistilBERT", "Both (compare)")
        if needs_groq and not os.environ.get("GROQ_API_KEY"):
            st.warning("GROQ_API_KEY not set — the Groq path will fail.")
        if needs_local and not os.path.isdir(local_model_name):
            st.warning(f"Model dir '{local_model_name}' not found — download it from Colab (see README).")

        st.markdown("### Demo posts")
        for name, demo_text in DEMO_POSTS.items():
            if st.button(name):
                st.session_state["demo_text"] = demo_text

    text = st.text_area(
        "Reddit post / comment",
        height=140,
        value=st.session_state.get("demo_text", ""),
        placeholder="Paste a post or comment...",
    )

    if not st.button("Classify", type="primary"):
        return
    if not text.strip():
        st.error("Please enter some text.")
        return

    clean = text.strip()
    show_local = mode in ("Fine-tuned DistilBERT", "Both (compare)")
    show_groq = mode in ("Groq prompt model", "Both (compare)")
    columns = st.columns(2 if (show_local and show_groq) else 1)
    col_iter = iter(columns)

    if show_local:
        with next(col_iter):
            render_panel(
                "Fine-tuned DistilBERT",
                "Confidence (softmax)",
                lambda: classify_local(clean, local_model_name),
            )
    if show_groq:
        with next(col_iter):
            render_panel(
                "Zero-shot Llama (Groq)",
                "Confidence (self-reported)",
                lambda: classify_groq(clean, groq_model),
            )


if __name__ == "__main__":
    main()
