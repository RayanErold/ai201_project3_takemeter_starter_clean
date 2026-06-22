"""Error-pattern analysis for the TakeMeter classifier.

Reads model predictions from evaluation_results.json and the ground-truth labels
from labeled_dataset.csv, then writes a markdown error-pattern report.

Expected evaluation_results.json format -- a JSON list of records, each with:
    {
        "text":       "<the post text>",          # required
        "true_label": "<analysis|hot_take|...>",   # required (also accepts "label"/"actual")
        "predicted":  "<analysis|hot_take|...>",   # required (also accepts "prediction"/"pred")
        "confidence": 0.87                          # optional (0-1)
    }
A top-level {"results": [...]} wrapper is also accepted.

Usage:
    python error_analysis.py
    python error_analysis.py --results evaluation_results.json --out error_analysis_report.md
"""

import argparse
import csv
import json
import os
from collections import Counter, defaultdict

LABELS = ["analysis", "hot_take", "reaction", "humor_meme"]

TRUE_KEYS = ["true_label", "label", "actual", "y_true", "gold"]
PRED_KEYS = ["predicted", "prediction", "pred", "y_pred"]
TEXT_KEYS = ["text", "post", "input"]


def _first(record, keys, default=None):
    for key in keys:
        if key in record and str(record[key]).strip():
            return record[key]
    return default


def load_results(path):
    if not os.path.exists(path):
        return None, f"'{path}' does not exist."
    if os.path.getsize(path) == 0:
        return None, f"'{path}' is empty (0 bytes) -- no predictions to analyze yet."
    with open(path, "r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as error:
            return None, f"'{path}' is not valid JSON: {error}"
    if isinstance(data, dict) and "results" in data:
        data = data["results"]
    if not isinstance(data, list):
        return None, "Expected a JSON list of prediction records (or a {'results': [...]} object)."

    records = []
    for raw in data:
        if not isinstance(raw, dict):
            continue
        true_label = _first(raw, TRUE_KEYS)
        predicted = _first(raw, PRED_KEYS)
        if true_label is None or predicted is None:
            continue
        records.append(
            {
                "text": _first(raw, TEXT_KEYS, default=""),
                "true_label": str(true_label).strip().lower(),
                "predicted": str(predicted).strip().lower(),
                "confidence": raw.get("confidence"),
            }
        )
    if not records:
        return None, "No usable records found (need 'true_label' and 'predicted' on each row)."
    return records, None


def dataset_distribution(path):
    if not os.path.exists(path):
        return Counter(), 0
    with open(path, "r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    counts = Counter(r.get("label", "").strip() for r in rows if r.get("label", "").strip())
    return counts, len(rows)


def confusion_matrix(records, labels):
    matrix = {a: Counter() for a in labels}
    for r in records:
        if r["true_label"] in matrix:
            matrix[r["true_label"]][r["predicted"]] += 1
    return matrix


def per_class_metrics(records, labels):
    metrics = {}
    for label in labels:
        tp = sum(1 for r in records if r["true_label"] == label and r["predicted"] == label)
        fp = sum(1 for r in records if r["true_label"] != label and r["predicted"] == label)
        fn = sum(1 for r in records if r["true_label"] == label and r["predicted"] != label)
        support = sum(1 for r in records if r["true_label"] == label)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        metrics[label] = dict(precision=precision, recall=recall, f1=f1, support=support)
    return metrics


def build_report(records, labels, dataset_counts, dataset_total):
    total = len(records)
    correct = sum(1 for r in records if r["true_label"] == r["predicted"])
    accuracy = correct / total if total else 0.0

    matrix = confusion_matrix(records, labels)
    metrics = per_class_metrics(records, labels)
    macro_f1 = sum(m["f1"] for m in metrics.values()) / len(labels)

    # Ranked confusion pairs (actual -> predicted), excluding correct.
    pairs = Counter()
    for r in records:
        if r["true_label"] != r["predicted"] and r["true_label"] in labels:
            pairs[(r["true_label"], r["predicted"])] += 1

    lines = []
    lines.append("# TakeMeter — Error Pattern Analysis\n")
    lines.append(f"- Evaluated examples: **{total}**")
    lines.append(f"- Correct: **{correct}**  |  Accuracy: **{accuracy:.1%}**  |  Macro F1: **{macro_f1:.3f}**\n")

    lines.append("## Per-class metrics\n")
    lines.append("| Label | Precision | Recall | F1 | Support |")
    lines.append("|---|---|---|---|---|")
    for label in labels:
        m = metrics[label]
        lines.append(f"| {label} | {m['precision']:.2f} | {m['recall']:.2f} | {m['f1']:.2f} | {m['support']} |")
    lines.append("")

    lines.append("## Confusion matrix (rows = actual, cols = predicted)\n")
    lines.append("| actual \\ pred | " + " | ".join(labels) + " |")
    lines.append("|---" * (len(labels) + 1) + "|")
    for actual in labels:
        row = [f"**{actual}**"] + [str(matrix[actual][p]) for p in labels]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## Top error patterns (most-confused pairs)\n")
    if pairs:
        lines.append("| Actual | Predicted as | Count |")
        lines.append("|---|---|---|")
        for (actual, predicted), count in pairs.most_common(10):
            lines.append(f"| {actual} | {predicted} | {count} |")
    else:
        lines.append("No misclassifications found.")
    lines.append("")

    lines.append("## Example misclassifications\n")
    shown = 0
    for (actual, predicted), _ in pairs.most_common():
        for r in records:
            if r["true_label"] == actual and r["predicted"] == predicted and r["text"]:
                conf = f" (conf {r['confidence']:.2f})" if isinstance(r["confidence"], (int, float)) else ""
                lines.append(f"- **{actual} → {predicted}**{conf}: \"{r['text'][:160]}\"")
                shown += 1
                break
        if shown >= 8:
            break
    if not shown:
        lines.append("No example texts available in the results file.")
    lines.append("")

    if dataset_counts:
        lines.append("## Class-balance context (full labeled_dataset.csv)\n")
        lines.append("| Label | Count | Share |")
        lines.append("|---|---|---|")
        for label, count in dataset_counts.most_common():
            share = count / dataset_total if dataset_total else 0
            lines.append(f"| {label} | {count} | {share:.1%} |")
        lines.append("")
        lines.append(
            "> Interpret per-class recall against these shares: a rare class "
            "(small support) with low recall is the dataset-balance risk to address first."
        )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze TakeMeter classifier errors.")
    parser.add_argument("--results", default="evaluation_results.json")
    parser.add_argument("--dataset", default="labeled_dataset.csv")
    parser.add_argument("--out", default="error_analysis_report.md")
    args = parser.parse_args()

    records, error = load_results(args.results)
    if error:
        print(f"[error_analysis] {error}")
        print(
            "[error_analysis] Once the notebook writes predictions to "
            f"'{args.results}', re-run this script to generate '{args.out}'."
        )
        print("[error_analysis] Expected record shape:")
        print('    {"text": "...", "true_label": "reaction", "predicted": "analysis", "confidence": 0.71}')
        return

    dataset_counts, dataset_total = dataset_distribution(args.dataset)
    report = build_report(records, LABELS, dataset_counts, dataset_total)
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(report)
    print(f"[error_analysis] Analyzed {len(records)} predictions -> wrote '{args.out}'.")


if __name__ == "__main__":
    main()
