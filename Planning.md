# Planning: TakeMeter - r/nba

## 1. Community

**Community:** r/nba

**Why this community:** r/nba is a large and active sports community with a mix of emotional reactions, bold opinions, analytical breakdowns, and meme-based conversation. That variety makes it an ideal source for a classifier that distinguishes reaction-style text from analysis and hot takes.

## 2. Labels

* **analysis:** Structured arguments backed by evidence, stats, advanced metrics, or tactical observation.
  * Example 1: "If you look at the team's defensive rating when [Player Name] is on the floor versus off, it drops by 8 points per 100 possessions, which suggests he is the primary anchor of their scheme."
  * Example 2: "Over the last five seasons, the league-wide percentage of 3-point attempts has increased by 12%, fundamentally changing how centers have to defend the perimeter compared to the early 2000s."

* **hot_take:** A bold, provocative opinion with minimal supporting evidence, meant to spark debate.
  * Example 1: "Michael Robinson is the most overrated star in the league—he wouldn't even start on a lottery team if he didn't have his brand name."
  * Example 2: "Trade Rudy Gobert immediately. He’s never going to win a championship and he’s just taking up cap space at this point."

* **reaction:** Immediate emotional responses to a game event or news headline, usually short and focused on the present moment.
  * Example 1: "I CAN'T BELIEVE HE JUST HIT THAT SHOT AT THE BUZZER! LETS GOOOO!"
  * Example 2: "That was a terrible foul call by the refs, completely ruined the flow of the fourth quarter."

* **humor_meme:** Posts or comments primarily intended to entertain, mock, or reference a subreddit in-joke.
  * Example 1: "We’re really going to pretend [Player Name] is an All-Star when he’s built like a human popsicle stick?"
  * Example 2: "Sources: Oneal is beside himself. Driving around downtown LA begging (thru texts) for address to Bridges's home."

## 3. Hard Edge Cases

These are real examples from the collected dataset that were genuinely difficult to label, the labels they sat between, what we decided, and the general rule we extracted from each.

**Edge Case 1 — A "neutral" discussion question that is really opinion-bait.**

* *Example (from r/LetsTalkMusic):* "Tyler better than kanye?"
* *Why it's hard:* It is phrased as an open question (looks like `analysis`), but it has no evidence, no reasoning, and exists only to provoke a subjective comparison (looks like `hot_take`).
* *Decision:* Label as **hot_take**.
* *Rule:* A short, evidence-free question whose only purpose is to bait a "who's better / is X overrated" debate is a `hot_take`, not `analysis`. Reserve `analysis` for questions that invite explanation or reasoning (e.g. "What makes an album a 'grower' rather than an instant favorite?").

**Edge Case 2 — A statistic used to make a joke, not an argument.**

* *Example (from r/nba):* "Another point for the GOAT debate: there have been twice as many players born on December 30th (LeBron's date of birth) than February 17th (Jordan's)."
* *Why it's hard:* It cites real numbers and frames itself as evidence (looks like `analysis`), but the "evidence" is irrelevant to the actual claim, which makes it a joke (looks like `humor_meme`).
* *Decision:* Label as **humor_meme**.
* *Rule:* Presence of a stat does not make something `analysis`. If the statistic does not actually support the claim and the intent is comedic/absurd, label `humor_meme`.

**Edge Case 3 — An emotional, motivational player quote vs. a bold opinion.**

* *Example (from r/nba):* Jalen Brunson: "There's a lot of people that have a lot of negative stuff to say... but when you prove them wrong, you don't have to say s--t to them."
* *Why it's hard:* It is an emotionally charged, present-moment celebratory quote (looks like `reaction`), but it also asserts a strong stance (looks like `hot_take`).
* *Decision:* Label as **reaction**.
* *Rule:* If the text is an emotional response to a just-happened event (a win, a parade, a clutch moment) rather than a debatable claim about player/team quality, label `reaction`. `hot_take` requires a contestable opinion someone could argue against.

**Edge Case 4 — A subjective preference stated as a universal fact.**

* *Example (from r/LetsTalkMusic):* "Underground concerts are MUCH better than mainstream ones."
* *Why it's hard:* It reads like a topic for discussion (looks like `analysis`), but it is a flat, evidence-free declaration of preference (looks like `hot_take`).
* *Decision:* Label as **hot_take**.
* *Rule:* A declarative opinion presented as fact with no supporting reasoning is a `hot_take`, even when it is about a category (genres, eras, venues) rather than a specific person.

## 4. Data Collection Plan

* **Source:** Collect examples from r/nba using the subreddit "Hot" and "Top" views for the past 24 hours and past week. Use both post titles and top-level comments.
* **Target:** Gather 200 labeled examples in a single CSV file with columns `text`, `label`, and `source_url`.
* **Balance:** Aim for roughly 50 examples per label. If one label is underrepresented, use targeted searches such as "advanced stats," "breakdown," "hot take," or "meme" to collect more.
* **Documentation:** Include a source URL for each example and note difficult labeling decisions in the CSV.
* **Split:** Allow the notebook to split the data automatically into 70% train / 15% validation / 15% test.

## 5. Evaluation Metrics

* **Accuracy:** Overall correctness across all labels.
* **F1-score:** Key metric because the dataset is likely imbalanced and we need both precision and recall.
* **Confusion matrix:** Required to understand where the model confuses `hot_take`, `reaction`, and `analysis`.

## 6. Definition of Success

* **Minimum:** At least **0.70 F1-score** across all labels.
* **Stretch goal:** At least **0.80 accuracy** on the test set while clearly separating `analysis` from `hot_take`.

## 7. AI Tool Plan

* **Label Stress-Testing:** Use an LLM to generate 5 boundary examples for each pair of labels and then verify them manually.
* **Annotation Assistance:** If using an LLM to pre-label, manually verify every example.
* **Failure Analysis:** After evaluation, review misclassifications and ask an LLM to categorize the failure modes (sarcasm, emotional intensity, topic drift).

## 8. AI Usage Disclosure

* Instance 1: Used an LLM to draft label definitions and edge-case rules.
* Instance 2: Will use an LLM to analyze model misclassifications.

---

### Notes

This project is focused on r/nba because it provides a strong mix of reaction, hot take, analysis, and meme content. The next step is to collect the dataset, save it in a CSV, and document at least three hard-edge cases in the data.
