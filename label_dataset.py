import argparse
import csv
import os

LABEL_OPTIONS = ["analysis", "hot_take", "reaction", "humor_meme", "skip"]
FIELDNAMES = ["text", "label", "source_url", "source_type", "notes"]


def load_examples(input_path):
    examples = []
    with open(input_path, "r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            examples.append(row)
    return examples


def save_examples(examples, output_path):
    with open(output_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for example in examples:
            writer.writerow(example)


def prompt_label(example, index, total):
    print(f"\nExample {index + 1}/{total}")
    print("Source:", example.get("source_url", ""))
    print("Type:", example.get("source_type", ""))
    print("Text:")
    print(example.get("text", ""))
    print("\nChoose label:")
    print("  ", ", ".join(LABEL_OPTIONS))

    while True:
        selected = input("label> ").strip().lower()
        if selected in LABEL_OPTIONS:
            return selected
        print(f"Invalid label. Choose one of: {', '.join(LABEL_OPTIONS)}")


def prompt_notes():
    notes = input("notes (optional)> ").strip()
    return notes


def main():
    parser = argparse.ArgumentParser(description="Label raw examples for the TakeMeter dataset.")
    parser.add_argument("--input", default="raw_dataset.csv", help="CSV with raw examples")
    parser.add_argument("--output", default="labeled_dataset.csv", help="CSV file to write labeled examples")
    parser.add_argument("--start", type=int, default=0, help="Start labeling at row index")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the input file with labeled results")
    args = parser.parse_args()

    examples = load_examples(args.input)
    total = len(examples)
    print(f"Loaded {total} examples from {args.input}")

    for index in range(args.start, total):
        example = examples[index]
        current_label = example.get("label", "").strip()
        if current_label:
            continue
        selected = prompt_label(example, index, total)
        if selected == "skip":
            example["label"] = ""
            example["notes"] = input("skip notes (optional)> ").strip()
            continue
        example["label"] = selected
        example["notes"] = prompt_notes()
        save_examples(examples, args.output)
        print(f"Saved progress to {args.output}")

    output_path = args.output if not args.overwrite else args.input
    save_examples(examples, output_path)
    print(f"Labeling complete. Results saved to {output_path}")


if __name__ == "__main__":
    main()
