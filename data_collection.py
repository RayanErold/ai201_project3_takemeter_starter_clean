import argparse
import csv
import html
import re
import time
import urllib.error
import urllib.request
from collections import OrderedDict

BASE_URL = "https://old.reddit.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def fetch_url(url):
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        print(f"HTTP error {error.code} while requesting {url}")
    except urllib.error.URLError as error:
        print(f"URL error {error.reason} while requesting {url}")
    return None


def clean_text(text):
    return " ".join(text.replace("\n", " ").replace("\r", " ").split())


def html_to_text(html_text):
    text = re.sub(r"<br\s*/?>", "\n", html_text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(clean_text(text))


def parse_listing(html_text):
    posts = []
    for match in re.finditer(r'<a[^>]+class="[^"]*title[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html_text, re.S):
        href, title = match.groups()
        title = clean_text(html_to_text(title))
        if not title:
            continue
        if href.startswith("/"):
            href = BASE_URL + href
        posts.append({
            "text": title,
            "label": "",
            "source_url": href,
            "source_type": "post_title",
            "notes": "",
        })
    return posts


def parse_next_page(html_text):
    match = re.search(r'<span class="next-button">\s*<a href="([^"]+)"', html_text)
    return match.group(1) if match else None


def parse_top_level_comments(html_text):
    comments = []
    for match in re.finditer(
        r'<div[^>]+class="thing comment[^"]*"[^>]+data-depth="0"[^>]*>.*?<div class="md">(.*?)</div>',
        html_text,
        re.S,
    ):
        body_html = match.group(1)
        body_text = html_to_text(body_html)
        if not body_text or body_text.lower() in {"[removed]", "[deleted]"}:
            continue
        comments.append(
            {
                "text": body_text,
                "label": "",
                "source_url": "",
                "source_type": "top_level_comment",
                "notes": "",
            }
        )
    return comments


def dedupe_examples(examples):
    unique = OrderedDict()
    for example in examples:
        key = example["text"].lower()
        if key and key not in unique:
            unique[key] = example
    return list(unique.values())


def save_to_csv(examples, output_path):
    fieldnames = ["text", "label", "source_url", "source_type", "notes"]
    with open(output_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for example in examples:
            writer.writerow(example)
    print(f"Saved {len(examples)} examples to {output_path}")


def fetch_posts(subreddit, sort="hot", pages=2):
    url = f"{BASE_URL}/r/{subreddit}/{sort}/"
    posts = []
    for page in range(pages):
        print(f"Fetching {sort} page {page + 1}: {url}")
        html_text = fetch_url(url)
        if not html_text:
            break
        posts.extend(parse_listing(html_text))
        next_page = parse_next_page(html_text)
        if not next_page:
            break
        url = next_page
        time.sleep(1)
    return posts


def fetch_comments(permalink, limit=20):
    url = permalink if permalink.startswith("http") else BASE_URL + permalink
    html_text = fetch_url(url)
    if not html_text:
        return []
    comments = parse_top_level_comments(html_text)
    for comment in comments:
        comment["source_url"] = url
    return comments[:limit]


def collect_raw_examples(subreddit, target_count=200):
    examples = []
    sort_modes = ["hot", "top", "new"]

    for sort in sort_modes:
        examples.extend(fetch_posts(subreddit, sort=sort, pages=2))
        examples = dedupe_examples(examples)
        if len(examples) >= target_count:
            break

    print(f"Collected {len(examples)} unique post titles.")

    if len(examples) < target_count:
        print("Collecting comments to reach the target count...")
        for example in list(examples):
            if len(examples) >= target_count:
                break
            permalink = example["source_url"]
            if "/comments/" not in permalink:
                continue
            comments = fetch_comments(permalink, limit=10)
            examples.extend(comments)
            examples = dedupe_examples(examples)
            if len(examples) >= target_count:
                break
            time.sleep(1)

    examples = dedupe_examples(examples)
    if len(examples) > target_count:
        examples = examples[:target_count]
    return examples


def main():
    parser = argparse.ArgumentParser(description="Collect raw subreddit examples for TakeMeter labeling.")
    parser.add_argument("--subreddit", default="nba", help="Subreddit name to collect from")
    parser.add_argument("--output", default="raw_dataset.csv", help="Output CSV file")
    parser.add_argument("--count", type=int, default=200, help="Target number of examples")
    args = parser.parse_args()

    examples = collect_raw_examples(args.subreddit, target_count=args.count)
    save_to_csv(examples, args.output)


if __name__ == "__main__":
    main()
