# KshetraAI

A field force intelligence system for agri input sales in India. It looks at a
sales rep's territory and works out who to visit today, in what order, what to
pitch, and why. Then it measures whether those recommendations were any good and
gets better from the outcomes.

Built around a real problem: a rep covers hundreds of retailers across a
district, the right thing to do changes daily with weather and crop stage and
stock levels, and most of that signal never reaches the person standing at the
counter. This turns the scattered signals into a daily plan with a reason
attached to every stop.

It runs end to end on synthetic data out of the box, so you can clone it and see
the whole thing work in one command. No proprietary dataset needed.

```
python generate_data.py      # make a synthetic season of data
python run_pipeline.py        # clean, train, rank, route, detect, evaluate
open frontend/index.html      # see the dashboard
```

## What is actually interesting here

Most recommendation projects stop at "here is a ranked list". The parts that
took real thought:

**The recommendations explain themselves.** Every stop comes with the top
signals that pushed it up the list, in plain language, from SHAP. A rep does not
trust a black box, and neither should a judge.

**It measures its own quality.** There is a real evaluation suite, not just an
accuracy number. precision at k against actual conversions, whether the SHAP
explanations line up with real outcomes, whether reps who follow the model do
better than reps who do not, and a hand labelled golden set of field situations
the model gets scored against. This is the part that separates "looks like it
works" from "here is the evidence it works".

**Next best action is a grounded LLM agent, not a lookup table.** SALAH takes the
structured signals the pipeline computed and writes the actual pitch a rep can
use, in english, hindi, or hinglish. The grounding matters: the model only ever
sees real signals, so it cannot drift into making things up. Falls back to a rule
based response when no API key is set, so the demo never breaks.

**It is observable.** Every prediction and LLM call can be traced through
Langfuse for latency, cost, and output inspection. Turns off cleanly into a no op
when not configured.

**The feature engineering does not leak.** Training and serving compute features
through the exact same code with an as_of date, so the model sees in production
exactly what it saw in training. This sounds obvious and is the bug in most ML
projects.

## How it fits together

```
generate_data.py        synthetic season, makes the repo self contained
        |
run_pipeline.py
        |
   data_io  ->  signals  ->  features  ->  labels
        |
   ranker (LambdaRank, NDCG@5)  +  scoring (rule + ML blend)
        |
   route (OR-Tools TSP)  +  anomaly (CHETAVANI)  +  explain (SHAP)
        |
   evaluation (precision@k, faithfulness, golden set)
   salah_agent (LLM next best action)
   observability (Langfuse tracing)
        |
   outputs/*.csv  +  *.json
        |
   build_frontend.py  ->  frontend/data.js  ->  index.html
        |
   api/main.py  serves it all over REST
```

## Running it

### Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python generate_data.py
python run_pipeline.py

# serve it
uvicorn api.main:app --reload --port 8000   # then open /docs
# or just open the dashboard
open frontend/index.html
```

### With Docker

```bash
cp .env.example .env         # optional, add API keys to enable SALAH and tracing
docker compose run pipeline  # generate data and train
docker compose up api        # serve on localhost:8000
```

### On Colab

Open run_on_colab.ipynb, runs the whole thing on free compute in about 5 to 8
minutes. Good if your laptop is slow.

## Turning on the optional bits

Everything runs without any keys. To light up the extra features, copy
.env.example to .env and fill in what you have:

  ANTHROPIC_API_KEY or OPENAI_API_KEY   SALAH writes real LLM pitches instead of
                                        the rule based fallback
  LANGFUSE_PUBLIC_KEY + SECRET_KEY      predictions and LLM calls get traced

## Layout

```
generate_data.py      synthetic data generator (run first)
run_pipeline.py        the whole pipeline, end to end
build_frontend.py      wires outputs into the dashboard
run_on_colab.ipynb     cloud run

src/                   all the logic, see src/README.md
data/                  golden_dataset.json, see data/README.md
api/                   FastAPI service, see api/README.md
tests/                 pytest, see tests/README.md
frontend/              brutalist dashboard, see frontend/README.md
docs/                  architecture diagram and the full writeup

Dockerfile, docker-compose.yml, .env.example
```

## What it does not do, honestly

Single season of synthetic data, so do not read the numbers as real performance,
read them as proof the machinery works. Some signals are tehsil level not
retailer level because the source data does not carry retailer attribution. NDVI
is a weather based proxy, not satellite. Competitor pricing is not modelled
because there is no data for it, though the golden set has a case for how it
should be handled. The uplift estimate is a proxy, not causal. All of this is
called out in the code and the docs rather than hidden.

## Where it came from

This started as a submission for a field force intelligence track and grew into a
standalone project. The history is in CHANGELOG.md, including the thirty issues
from the original review and how each was fixed.
