````markdown id="74gqsb"
# Rice — Crop Intelligence Table v1

# 1. Crop Profile

| Field | Value |
|---|---|
| Crop | Rice / Paddy |
| Common Season | Kharif |
| Water Demand | High |
| Typical Behavior | Dense green canopy during vegetative and reproductive stages |
| Major Stress Risks | Rainfall deficit, standing water shortage, heat stress during flowering, delayed transplanting/sowing |

---

# 2. Rice Growth Stages

| Stage | Meaning |
|---|---|
| Sowing / Transplanting | Crop establishment starts |
| Vegetative | Leaf and tiller growth |
| Flowering / Reproductive | Panicle initiation, flowering, grain formation |
| Maturity | Crop starts yellowing/drying |
| Harvest | Crop is ready or already cut |

---

# 3. Rice Crop Calendar — Kharif

| Stage | Week Range | Approx Timeline |
|---|---|---|
| Sowing / Transplanting | 24–27 | Jun – early Jul |
| Vegetative | 28–35 | Jul – Aug |
| Flowering / Reproductive | 36–40 | Sep – early Oct |
| Maturity | 41–45 | Oct – early Nov |
| Harvest | 46–48 | Nov |

---

# 4. Stage Expectation Tables

## A. Sowing / Transplanting

### Biological Expectations

| Signal | Expected Behavior |
|---|---|
| NDVI | Low / Rising |
| NDWI | Medium-High |
| LST Sensitivity | Medium |
| Rainfall Sensitivity | High |

### Allowed Statistical Labels

#### NDVI

```text
Very Low
Low-Normal
Normal
```

#### NDWI

```text
Low-Normal
Normal
High-Normal
```

#### LST

```text
Very Low
Low-Normal
Normal
High-Normal
```

#### Rainfall

```text
Normal
High-Normal
Very High
```

### Interpretation Logic

```text
Low NDVI is normal during establishment.
Low rainfall or low NDWI may indicate poor establishment risk.
```

---

## B. Vegetative Stage

### Biological Expectations

| Signal | Expected Behavior |
|---|---|
| NDVI | Rising / High |
| NDWI | High |
| LST Sensitivity | High |
| Rainfall Sensitivity | High |

### Allowed Statistical Labels

#### NDVI

```text
Normal
High-Normal
Very High
```

#### NDWI

```text
Normal
High-Normal
Very High
```

#### LST

```text
Very Low
Low-Normal
Normal
```

#### Rainfall

```text
Normal
High-Normal
Very High
```

### Interpretation Logic

```text
NDVI should rise strongly.
NDWI should remain adequate/high.
LST should not rise abnormally.
If NDVI falls + NDWI falls + LST rises
→ likely crop stress.
```

---

## C. Flowering / Reproductive Stage

### Biological Expectations

| Signal | Expected Behavior |
|---|---|
| NDVI | Stable-High |
| NDWI | High |
| LST Sensitivity | Very High |
| Rainfall Sensitivity | High |

### Allowed Statistical Labels

#### NDVI

```text
High-Normal
Very High
```

#### NDWI

```text
Normal
High-Normal
Very High
```

#### LST

```text
Very Low
Low-Normal
Normal
```

#### Rainfall

```text
Normal
High-Normal
Very High
```

### Interpretation Logic

```text
NDVI should remain high/stable.
High LST is dangerous because flowering is heat-sensitive.
Moisture deficit is also serious.
```

---

## D. Maturity Stage

### Biological Expectations

| Signal | Expected Behavior |
|---|---|
| NDVI | Declining |
| NDWI | Declining |
| LST Sensitivity | Medium-Low |
| Rainfall Sensitivity | Medium |

### Allowed Statistical Labels

#### NDVI

```text
Low-Normal
Normal
High-Normal
```

#### NDWI

```text
Low-Normal
Normal
```

#### LST

```text
Very Low
Low-Normal
Normal
High-Normal
```

#### Rainfall

```text
Low-Normal
Normal
High-Normal
```

### Interpretation Logic

```text
NDVI decline is expected.
NDWI decline is expected.
Do not wrongly mark this as stress unless decline is unusually early or severe.
```

---

## E. Harvest Stage

### Biological Expectations

| Signal | Expected Behavior |
|---|---|
| NDVI | Low / Declining |
| NDWI | Low / Declining |
| LST Sensitivity | Low |
| Rainfall Sensitivity | Low |

### Allowed Statistical Labels

#### NDVI

```text
Very Low
Low-Normal
```

#### NDWI

```text
Very Low
Low-Normal
```

#### LST

```text
Very Low
Low-Normal
Normal
High-Normal
Very High
```

#### Rainfall

```text
Very Low
Low-Normal
Normal
High-Normal
Very High
```

### Interpretation Logic

```text
Low NDVI is expected.
Stress inference should mostly be disabled or treated as low priority.
```

---

# 5. Rice Trend Logic

## Healthy Vegetative Trend

```text
NDVI → Rising
NDWI → Stable / High
LST → Stable
Rainfall → Adequate
```

---

## Stress Trend Pattern

```text
NDVI → Falling
NDWI → Falling
LST → Rising
Rainfall → Deficient
```

Meaning:

```text
Possible moisture + heat stress progression.
```

---

# 6. Rice MVP Stress Rule Example

```text
IF crop = rice
AND stage = vegetative
AND NDVI label ∉ allowed_ndvi_labels
AND NDWI label ∉ allowed_ndwi_labels
AND LST label ∉ allowed_lst_labels
AND rainfall label ∉ allowed_rainfall_labels
AND trend_status = worsening
THEN stress_level = High
```

---

# 7. Final Rice Insight

The strongest rice stress signature is:

```text
NDVI decline
+
NDWI decline
+
LST rise
+
rainfall deficit
```

especially during:

```text
Vegetative
or
Flowering / Reproductive stage
```
````
