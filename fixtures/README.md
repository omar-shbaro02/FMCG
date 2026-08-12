# Deterministic synthetic scenario fixtures

These fixtures contain no real client data. Regenerate them with:

```bash
python scripts/seed_demo_data.py
```

Each directory contains `weekly_sales.csv` and `truth.json`. The JSON records the
fixed seed, expected later-stage classification, priority, confidence, and the
commercial scenario truth. Classifier and end-to-end tasks must test against this
truth without teaching the runtime classifier to read these labels.

The scenarios cover healthy growth, temporary uplift, pull-forward, loading,
discount dependency, cannibalization, margin/value-quality deterioration, and
insufficient evidence. They use weekly `sku_id + channel + region` grain and the
frozen data dictionary columns.
