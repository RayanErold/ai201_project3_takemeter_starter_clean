This is a professional, structured template for your `planning.md`. You can copy and paste this into your GitHub repository and fill in the bracketed information based on the community you choose.

---

# Planning: TakeMeter - [Insert Community Name Here]

## 1. Community

**Community:** [e.g., r/nba, r/frontend, etc.]
**Why this community:** [e.g., The discourse is highly polarized between raw reactions and tactical analysis, making it perfect for a classification task.]

## 2. Labels

* **Analysis:*Structured arguments backed by verifiable evidence (stats, historical comparisons, advanced metrics, or tactical observation).* [One-sentence definition.]
* *Example 1:* "If you look at the team's defensive rating when [Player Name] is on the floor versus off, it drops by 8 points per 100 possessions, which suggests he is the primary anchor of their scheme"

* *Example 2:* "Over the last five seasons, the league-wide percentage of 3-point attempts has increased by 12%, fundamentally changing how centers have to defend the perimeter compared to the early 2000s."


* **hot_take:*A bold, provocative opinion stated with confidence but little-to-no supporting evidence. It is meant to incite debate rather than prove a point.* [One-sentence definition.]
* *Example 1:* "Micheal Robinson is the most overrated star in the league—he wouldn't even start on a lottery team if he didn't have his brand name.."

* *Example 2:* "Trade Rudy Gobert immediately. He’s never going to win a championship and he’s just taking up cap space at this point."


* **reaction:*Immediate, emotional responses to a game event or news headline. Usually brief and focused on the "now" (e.g., "HE'S HIM!", "Worst call ever!").* [One-sentence definition.]
* *Example 1:* "I CAN'T BELIEVE HE JUST HIT THAT SHOT AT THE BUZZER! LETS GOOOO!"
* *Example 2:* "That was a terrible foul call by the refs, completely ruined the flow of the fourth quarter."



* **Hummor_meme:*Posts or comments primarily intended to entertain, mock, or reference a subreddit in-joke.* [One-sentence definition.]
* *Example 1:* "We’re really going to pretend [Player Name] is an All-Star when he’s built like a human popsicle stick?"

* *Example 2:* "Sources: Oneal is beside himself. Driving around downtown LA begging (thru texts) for address to Bridges's home."




## 3. Hard Edge Cases

*Ambiguous Case*: A post made seconds after a massive play that includes tactical observations but is buried in intense emotional language (e.g., "I CAN'T BELIEVE HE HIT THAT!! The way he stepped back created the exact space he needed because of the defender's momentum!)"

*Decision Rule*:** Label as reaction. If a post is characterized by all-caps, multiple exclamation points, and immediate emotional intensity, it is a reaction. Even if it contains a nugget of analysis (like mentioning defender momentum), the primary purpose of the post is to share an emotional experience in the heat of the moment.

*Ambiguous Case*:A post that uses a single statistic to fuel an inflammatory or subjective opinion (e.g., "Player X is trash, look at his shooting percentage tonight!").
*Decision Rule*:** Label as hot_take. Even if a statistic is included, if the primary purpose of the post is to attack a player's reputation or incite an emotional reaction rather than provide a nuanced argument, it defaults to a hot_take. Statistics used as "decorative evidence" for an emotional claim do not qualify as analysis.

## 4. Data Collection Plan

* **Source:** [e.g., Reddit API / Manual copy-paste from subreddit threads.]
* **Target:** 200 total examples. [Define split per label here to ensure balance].
* **Handling Imbalance:** If one label exceeds 70% of the dataset, I will specifically search for examples of the underrepresented category to ensure a 50/50 or 60/40 distribution.

## 5. Evaluation Metrics

* **Accuracy:** To measure overall performance.
* **F1-Score:** [Explain why: e.g., "F1 is crucial because I want to balance precision and recall, ensuring the model doesn't just over-predict the majority class."]
* **Confusion Matrix:** To visualize exactly which labels are being confused.

## 6. Definition of Success

* **Threshold:** A minimum F1-score of [0.70] across all labels.
* **Goal:** A model that can distinguish between "Hot Takes" and "Evidence-Based Analysis" with at least [80%] accuracy on the test set.

## 7. AI Tool Plan

* **Label Stress-Testing:** I will provide these labels to an AI and ask it to generate 5 "boundary-line" examples to verify if my definitions are clear.
* **Annotation Assistance:** [State whether you will use an LLM to pre-label. If yes: "I will use [Tool Name] to pre-label, then I will manually verify every single entry."]
* **Failure Analysis:** After evaluation, I will provide the misclassified examples to an LLM and ask it to categorize the *type* of error (e.g., sarcasm, length, topic drift) to find patterns.

## 8. AI Usage Disclosure

* *[To be updated as you work]* * Instance 1: [Used [Tool] to generate edge-case examples.]
* Instance 2: [Used [Tool] to analyze patterns in errors.]

---

### 💡 Pro-Tip for filling this out:

To get the best results for your **"Hard Edge Cases"**, try this: Once you pick your community, ask me: *"I'm looking at r/[Community]. I'm defining my labels as X and Y. Can you give me 5 examples of posts that would be hard to classify between these two?"*

**What community are you going with?** If you name it, I can help you write those specific label definitions right now.