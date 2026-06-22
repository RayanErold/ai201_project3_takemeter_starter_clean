"""Create a class-balanced version of labeled_dataset.csv by downsampling the
majority classes. Keeps every minority-class row, caps each class at --cap rows.

Deterministic (fixed seed) so results are reproducible.

Usage:
    python balance_dataset.py                # cap=90 -> balanced_dataset.csv
    python balance_dataset.py --cap 80 --out balanced_dataset.csv
"""

import argparse
import csv
import random
from collections import defaultdict, Counter

FIELDNAMES = ["text", "label", "source_url", "source_type", "notes"]
SEED = 42


def main():
    parser = argparse.ArgumentParser(description="Downsample majority classes to balance the dataset.")
    parser.add_argument("--input", default="labeled_dataset.csv")
    parser.add_argument("--out", default="balanced_dataset.csv")
    parser.add_argument("--cap", type=int, default=90, help="Max rows kept per class")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    by_label = defaultdict(list)
    for row in rows:
        by_label[row["label"].strip()].append(row)

    rng = random.Random(SEED)
    kept = []
    for label, group in by_label.items():
        if len(group) > args.cap:
            rng.shuffle(group)
            group = group[: args.cap]
        kept.extend(group)

    rng.shuffle(kept)  # mix classes so the file isn't grouped by label

    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(kept)

    before = Counter(r["label"].strip() for r in rows)
    after = Counter(r["label"].strip() for r in kept)
    total_after = len(kept)
    print(f"Wrote {total_after} rows to {args.out} (cap={args.cap})\n")
    print(f"{'label':12} {'before':>8} {'after':>8} {'after %':>9}")
    for label in sorted(after, key=lambda x: -after[x]):
        print(f"{label:12} {before[label]:>8} {after[label]:>8} {after[label]/total_after*100:>8.1f}%")


if __name__ == "__main__":
    main()
