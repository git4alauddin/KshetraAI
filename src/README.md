# src

All the actual logic lives here. The pipeline is just these modules called in
order. Each file does one thing and the imports between them are kept shallow
so you can read any single file and understand it without chasing five others.

Rough order of how data flows through:

`config.py`
Everything tunable in one place: paths, the rule weights, the blend ratio,
thresholds, the reference date. If you find a magic number anywhere else in the
code it is a bug, it should be here. Paths resolve from KSHETRA_BASE so the same
code runs locally, in Docker, and on Colab.

`data_io.py`
Loads the eight raw CSVs, cleans them, parses the JSON columns (crop calendars
come in as JSON strings). When a JSON field fails to parse it logs how many rows
failed instead of silently returning an empty dict, because silent failures here
were one of the original bugs.

`signals.py`
The nine point in time signals. Each one takes an as_of date and only looks at
data on or before it, so there is no leakage from the future. Some signals are
tehsil level (visit gap, product gap) because the source data does not carry
retailer level attribution, and that is called out honestly rather than faked.

`features.py`
One shared feature builder. `build_training_features` and
`build_inference_features` both call the same internal assembler, just with
different as_of dates. This is the single most important fix in the whole
project: training and serving now compute features the exact same way, so the
model sees in production what it saw in training.

`labels.py`
The training label: did a product specific conversion happen within 14 days.
Also has an experimental uplift proxy, clearly labelled experimental because
real causal uplift needs a control group this data does not have.

`scoring.py`
The rule scorer (readable by eye, weights live in config) and the hybrid blend.
Both the rule score and the model score get normalised to 0 to 1 before
blending, then the final score is scaled to a clean 0 to 100. Tiers (urgent,
important, monitor) come off thresholds.

`ranker.py`
LightGBM with the lambdarank objective, grouped by rep and day, so NDCG at 5 is
actually meaningful. Reports a baseline (rank by recent sales velocity) next to
the model so you can see the model is doing better than the obvious heuristic.
Has expanding window cross validation across the season.

`anomaly.py`
Two detectors. Demand spike compares the recent weekly rate to the trailing
weekly rate (both weekly, which fixed the original units bug that flagged 90
percent of retailers). Price anomaly flags retailer SKUs with a high coefficient
of variation. Output is a priority ranked feed, not a flat dump.

`route.py`
OR-Tools TSP to sequence the top retailers per territory. Distances are
haversine over approximate tehsil coordinates, so they are indicative, not GPS
exact, and the docs say so.

`explain.py`
SHAP over the trained model, turned into plain language reasons a rep can read.
SIGNAL_LABELS maps each raw signal to a human phrase ("days since last visit"
becomes "long gap since last visit").

`feedback.py`
SEEKHO. Logs each visit outcome to a CSV with a fixed schema. This is what
closes the loop: the retraining job reads these outcomes to refresh the model.

`backtest.py`
recall at k against what the reps actually did. The honest check on whether the
ranking beats business as usual.

`weather.py`
Pulls historical weather from Open-Meteo, with retry and an on disk cache so the
pipeline runs offline after the first fetch. The only external API in the whole
project, and it needs no key.

`predict.py`
The serving functions. score_all, beat_plan, score_one_retailer. This is what
the API and the frontend builder call.

The newer modules that make this a portfolio piece rather than a hackathon entry:

`salah_agent.py`
Next best action as an LLM agent. Takes the structured signals the pipeline
already computed and turns them into a real pitch a rep can use, in english,
hindi, or hinglish. Falls back to a rule based response when no API key is set
so it never breaks. The grounding is the interesting part: the model only sees
real signals, never invents data.

`evaluation.py`
The part that actually matters. precision at k, explanation faithfulness, rep
acceptance vs outcome, and scoring against a hand labelled golden dataset. This
answers "are the recommendations any good" instead of hiding behind one accuracy
number.

`observability.py`
Tracing wrapper around Langfuse. Every prediction and LLM call can be inspected
for latency, cost, and output. If Langfuse is not configured every call becomes
a no op, so you never have to guard it with an if statement.
