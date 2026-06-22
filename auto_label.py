#!/usr/bin/env python3
"""Auto-label empty-label rows in raw_dataset.csv -> labeled_dataset.csv."""
import csv
from collections import Counter

IN = "raw_dataset.csv"
OUT = "labeled_dataset.csv"
LABELS = {"analysis", "hot_take", "reaction", "humor_meme"}


def classify(text: str) -> str:
    t = text.strip()
    low = t.lower()

    humor = [
        "no condom", "thumb in", "forbidden place", "shirtless", "no english",
        "air ball", "airball", "knock you", "rocky curse", "selfie",
        "snake in", "panini store", "home office", "11 pel", "pitch invader",
        "key to the city", "elmo", "trash can", "burner", "lost on his way",
        "wandering around lost", "you are haiti", "you're welcome", "left us",
        "useless", "doesn't understand", "guarani", "yoga to get into the zone",
        "unplayable family", "punch anybody", "no condom", "diet de",
        "art ball", "wearing a sign", "key to the city", "ferran torres",
        "grandfather", "force a team to sign",
    ]
    if any(m in low for m in humor):
        return "humor_meme"
    if '“no.”' in low or '"no."' in low:
        return "humor_meme"

    reaction = [
        "[highlight", "highlights]", "highlight]", "years ago", "anniversary",
        "in tears", "emotional", "fell on his knees", "saved his life",
        "passed out", "confetti", "parade", "singing", "sings", "crowd sings",
        "chant", "speech", "we are the champions", "country roads",
        "empire state of mind", "trophy", "championship chains", "flowers",
        "lifts the larry", "touched the larry", "i touched", "congratulate",
        "dribble against", "ball handling", "near perfect defense", "block on",
        "perfect defense", "100 percent accuracy", "completed all",
        "first to score", "scored twice", "first-ever", "seismic",
        "tied for the most", "back-to-back games", "fueled them",
        "best shape of my life", "all for one", "born to play",
        "(live", "live at", "live on", "live session", "full performance",
        "full set", "banner seen", "in tears at", "down with muscle cramps",
        "muscle cramps", "three yellow cards", "challenged reporters",
        "talks about his absent", "took joy in his failure", "fresh performance",
        "fresh video", "fresh album", "fresh ep", "fresh reissue", "fresh]",
    ]
    if any(m in low for m in reaction):
        return "reaction"
    if low.startswith("[fresh"):
        return "reaction"

    hot = [
        "overrated", "underrated", "criminally", "goat", "better than",
        "would beat", "much better", "way better", "biggest trap", "trap in",
        "too broad", "isn't realistically possible", "crazy take",
        "i do not understand wanting", "my problem with",
        "i don't really understand", "first home office", "still the best",
        "are much better", "is too", "the term", "i don't even know why",
    ]
    if any(m in low for m in hot):
        return "hot_take"

    if t.endswith("?"):
        return "analysis"

    return "analysis"


def main():
    with open(IN, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    for r in rows:
        if not r["label"].strip():
            lab = classify(r["text"])
            assert lab in LABELS, lab
            r["label"] = lab

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    total = len(rows)
    labeled = sum(1 for r in rows if r["label"].strip() in LABELS)
    dist = Counter(r["label"] for r in rows)
    print(f"Total rows: {total}")
    print(f"Labeled (valid): {labeled}")
    for lab in ["analysis", "hot_take", "reaction", "humor_meme"]:
        c = dist.get(lab, 0)
        print(f"  {lab:12s}: {c:4d}  ({100*c/total:5.1f}%)")
    extra = set(dist) - LABELS
    if extra:
        print("UNEXPECTED:", extra)
    print(f"Max share: {max(dist[l] for l in LABELS)/total*100:.1f}%")


if __name__ == "__main__":
    main()
