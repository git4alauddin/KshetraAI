# tests

Not exhaustive. Just the things that would actually break the product if they
regressed, which is the useful 20 percent.

    pytest tests/

What is covered:

  test_scoring.py
    scores stay in range, the blend respects its weights, the final score uses
    the full 0 to 100 range (it used to compress to 17 to 53 which made the
    tiers meaningless), tiers fall on the right side of the thresholds.

  test_evaluation.py
    precision at k counts converters correctly and handles empty input, the rep
    acceptance split works, the golden dataset loads, and SALAH always returns a
    complete recommendation even with no API key set (the fallback path), in
    every language.

The SALAH test deliberately unsets the API keys so it exercises the fallback,
then restores them. That way the test suite passes whether or not you have keys
configured, which matters for CI.
