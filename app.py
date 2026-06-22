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
DEFAULT_MODEL = "llama-3.3-70b-versatile"

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


def classify(text, model):
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
        # Fall back to label-name matching if the model didn't return clean JSON.
        for candidate in LABELS:
            if candidate in raw.lower():
                label = candidate
                break

    if label not in LABELS:
        label = None
    return label, confidence, raw


def main():
    st.set_page_config(page_title="TakeMeter", page_icon="📊")
    st.title("📊 TakeMeter")
    st.caption("Classify a Reddit post as analysis, hot_take, reaction, or humor_meme.")

    with st.sidebar:
        model = st.text_input("Groq model", value=DEFAULT_MODEL)
        if not os.environ.get("GROQ_API_KEY"):
            st.warning("GROQ_API_KEY is not set. Set it in your environment, then restart.")

    text = st.text_area("Reddit post / comment", height=140, placeholder="Paste a post or comment...")

    if st.button("Classify", type="primary"):
        if not text.strip():
            st.error("Please enter some text.")
            return
        with st.spinner("Classifying..."):
            try:
                label, confidence, raw = classify(text.strip(), model)
            except Exception as error:  # noqa: BLE001 - surface any API/setup error to the UI
                st.error(f"Classification failed: {error}")
                return

        if label is None:
            st.error("Could not parse a valid label from the model response.")
            st.code(raw)
            return

        st.success(f"Predicted label: **{label}**")
        if confidence is not None:
            st.metric("Confidence (model self-reported)", f"{confidence:.0%}")
            st.progress(min(max(confidence, 0.0), 1.0))
        with st.expander("Raw model output"):
            st.code(raw)


if __name__ == "__main__":
    main()
