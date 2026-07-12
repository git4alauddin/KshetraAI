"""
salah_agent.py

SALAH is the next best action piece. The old version was a lookup table:
crop maps to product, done. This version is an LLM agent that takes the
structured context the rest of the pipeline already computed (the SHAP
signals, crop stage, weather, recent outcomes) and turns it into an actual
recommendation a rep can use at the door: what to pitch, how to pitch it,
what to say if the retailer pushes back on price.

The interesting bit is the grounding. This is not a chatbot answering from
thin air. The retrieval step here is feature engineering, not semantic search.
The model only ever sees real signals the pipeline produced, so the output
stays tied to the data. The generation is structured JSON, not free text, so
it is checkable.

It works in three modes:
  - if ANTHROPIC_API_KEY is set, it calls Claude
  - if OPENAI_API_KEY is set instead, it calls OpenAI
  - if neither is set, it falls back to a deterministic rule based response
    so the pipeline never breaks and the demo always runs

Language can be english, hindi, or hinglish. Same structured context, the
model just writes the pitch lines in the requested language.
"""

import os
import json
import logging

from src import config

log = logging.getLogger("kshetra.salah")

# Crop to product affinity, used by the fallback and as a hint to the LLM.
CROP_PRODUCT_HINT = {
    "wheat": "Topik 15 WP",
    "mustard": "Score 250 EC",
    "chickpea": "Actara 25 WG",
    "potato": "Kavach 75 WP",
    "barley": "Tilt 250 EC",
    "lentil": "Score 250 EC",
}

SYSTEM_PROMPT = """You are SALAH, a field advisor for an agri input company in India.
You help a sales rep decide what to pitch at a specific retailer, grounded only
in the signals provided. Do not invent data. If a signal is missing, say so.
Reply ONLY with a JSON object, no preamble, with these keys:
  product: the single product to lead with
  pitch_line: one or two sentences the rep can say, in the requested language
  counter_if_competitor: what to say if the retailer mentions a cheaper competitor
  agronomic_note: one practical agronomy point tied to the crop stage
  confidence: a number 0 to 1
Keep it short and practical. The rep is standing at the counter."""


def build_context(retailer):
    """
    Turn a retailer record (a dict or Series) into the compact context the model
    sees. This is the grounding. Only real signals go in.
    """
    def g(k, default=None):
        try:
            return retailer[k]
        except (KeyError, TypeError):
            return getattr(retailer, k, default)

    return {
        "retailer_id": g("retailer_id"),
        "district": g("district"),
        "tehsil": g("tehsil"),
        "dominant_crop": g("dominant_crop"),
        "final_score_100": g("final_score_100"),
        "top_signals": g("top_signals", []),
        "crop_stage": g("crop_stage"),
        "weather_humidity": g("weather_humidity"),
        "days_since_visit": g("days_since_visit"),
        "recent_outcomes": g("recent_outcomes", []),
    }


def _fallback(context, language):
    """Deterministic response when no LLM is available. Keeps the demo alive."""
    crop = (context.get("dominant_crop") or "wheat").lower()
    product = CROP_PRODUCT_HINT.get(crop, "Score 250 EC")
    if language in ("hi", "hindi"):
        pitch = f"{crop} ke is stage par {product} sahi rahega, stock check kar lijiye."
        counter = "Daam se zyada result dekhiye, yeh molecule yahan proven hai."
        note = "Spray ka sahi time crop stage dekhkar choose karein."
    elif language in ("hinglish", "hi-en"):
        pitch = f"{crop} abhi critical stage par hai, {product} pitch karo, stock low dikh raha hai."
        counter = f"Competitor sasta hai par result {product} ka proven hai is area mein."
        note = "Weather dekhte hue spray window plan karo."
    else:
        pitch = f"Lead with {product} for {crop} at this stage, stock looks low."
        counter = f"Compete on results not price, {product} is proven in this district."
        note = "Match the spray timing to the crop stage."
    return {
        "product": product,
        "pitch_line": pitch,
        "counter_if_competitor": counter,
        "agronomic_note": note,
        "confidence": 0.5,
        "source": "fallback_rule_based",
    }


def _call_anthropic(context, language):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    user = f"Language: {language}\nSignals:\n{json.dumps(context, indent=2, default=str)}"
    msg = client.messages.create(
        model=os.environ.get("SALAH_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    return _parse(text, source="anthropic")


def _call_openai(context, language):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    user = f"Language: {language}\nSignals:\n{json.dumps(context, indent=2, default=str)}"
    resp = client.chat.completions.create(
        model=os.environ.get("SALAH_MODEL", "gpt-4o-mini"),
        max_tokens=400,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": user}],
    )
    return _parse(resp.choices[0].message.content, source="openai")


def _parse(text, source):
    """Pull the JSON object out of the model reply, tolerant of stray text."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].replace("json", "", 1).strip()
    try:
        obj = json.loads(text)
        obj["source"] = source
        return obj
    except json.JSONDecodeError:
        log.warning("could not parse LLM JSON, returning raw text")
        return {"product": None, "pitch_line": text[:200], "counter_if_competitor": None,
                "agronomic_note": None, "confidence": None, "source": source + "_unparsed"}


def recommend(retailer, language="english", trace=None):
    """
    Main entry point. Pass a retailer record and a language. Returns a dict with
    product, pitch_line, counter_if_competitor, agronomic_note, confidence, source.

    If a tracer is passed (see observability.py) the call is traced for latency,
    cost, and output inspection.
    """
    context = build_context(retailer)
    language = language.lower()

    span = trace.start("salah_recommend", {"retailer": context.get("retailer_id"),
                                            "language": language}) if trace else None
    try:
        if os.environ.get("ANTHROPIC_API_KEY"):
            out = _call_anthropic(context, language)
        elif os.environ.get("OPENAI_API_KEY"):
            out = _call_openai(context, language)
        else:
            out = _fallback(context, language)
    except Exception as exc:
        log.warning("LLM call failed (%s), using fallback", exc)
        out = _fallback(context, language)

    if span:
        span.end({"product": out.get("product"), "source": out.get("source"),
                  "confidence": out.get("confidence")})
    return out


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo = {
        "retailer_id": "RTL_00045", "district": "Akola", "tehsil": "Akola_T027",
        "dominant_crop": "mustard", "final_score_100": 92.4,
        "top_signals": ["low stock", "weather risk", "long visit gap"],
        "crop_stage": "flowering", "weather_humidity": 87, "days_since_visit": 18,
        "recent_outcomes": ["sold 8 units", "no sale"],
    }
    for lang in ["english", "hindi", "hinglish"]:
        print(f"\n--- {lang} ---")
        print(json.dumps(recommend(demo, lang), indent=2, ensure_ascii=False))
