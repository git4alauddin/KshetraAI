```markdown id="blv4oq"
# Final MVP Signals + Business Value

## 1. Crop Health Signal

### Built From
- NDVI
- NDWI
- LST
- Rainfall
- Crop stage
- Trend analysis

### Purpose
Identify stressed crop regions and detect abnormal crop behavior.

### Output
- Healthy
- Watchlist
- Moderate Stress
- High Stress

### Business Value
- prioritize field-force visits to stressed territories
- improve timing of agronomic intervention
- increase relevance of product discussion
- reduce wasted visits to low-risk regions

---

## 2. Moisture Stress Signal

### Built From
- NDWI
- Rainfall
- LST

### Purpose
Detect water/moisture stress conditions.

### Output
- Normal
- Emerging Moisture Stress
- Severe Moisture Stress

### Business Value
- prioritize irrigation/moisture-related advisory
- support fungicide/nutrient/water-management campaigns
- identify drought-sensitive territories early
- improve advisory credibility with farmers

---

## 3. Heat Stress Signal

### Built From
- LST
- Crop stage

### Purpose
Detect temperature-related crop risk.

### Output
- Normal
- Heat Risk
- Severe Heat Stress

### Business Value
- prioritize heat-sensitive crop regions
- support stage-sensitive crop protection planning
- guide preventive intervention campaigns
- improve timing of field engagement

---

## 4. Pest / Disease Risk Signal

### Built From
- government pest bulletins
- crop stage
- weather conditions
- unexplained vegetation anomalies

### Purpose
Identify regions with elevated pest/disease risk.

### Output
- Normal
- Pest Watch
- Possible Pest/Disease Risk

### Business Value
- prioritize insecticide/fungicide campaigns
- direct reps toward high-risk regions
- improve responsiveness to emerging outbreaks
- support explainable product recommendation

Important:
This is a risk signal, not confirmed detection.

---

## 5. Campaign Timing Signal

### Built From
- crop stage
- pest advisories
- weather context

### Purpose
Determine whether a campaign/product push is timely.

### Output
- Too Early
- Right Window
- Late Window
- Urgent Window

### Business Value
- avoid premature campaigns
- improve campaign conversion
- improve recommendation relevance
- align field-force effort with actual agronomic timing

---

## 6. Territory Priority Signal

### Built From
- crop health signal
- moisture stress
- heat stress
- pest risk
- campaign timing

### Purpose
Rank territories for field-force prioritization.

### Output
- Low Priority
- Medium Priority
- High Priority
- Urgent Priority

### Business Value
- optimize daily field-force planning
- improve revenue per field day
- improve coverage efficiency
- focus effort where intervention probability is highest
- support explainable AI-driven territory prioritization
```
