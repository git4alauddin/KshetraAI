````markdown
# Crop Expectation Table — Template

## Basic Crop Information

| Field | Value |
|---|---|
| Crop | `<crop_name>` |
| Season | `<season>` |
| Stage | `<stage>` |
| Week Range | `<week_range>` |

---

## Biological Expectations

| Signal | Expected Behavior |
|---|---|
| NDVI | `<low/rising/high/stable/declining>` |
| NDWI | `<low/medium/high/stable/declining>` |
| LST Sensitivity | `<low/medium/high/very_high>` |
| Rainfall Sensitivity | `<low/medium/high>` |

---

## Allowed Statistical Labels

### NDVI

```text
<allowed_ndvi_labels>
```

### NDWI

```text
<allowed_ndwi_labels>
```

### LST

```text
<allowed_lst_labels>
```

### Rainfall

```text
<allowed_rainfall_labels>
```

---

# Example — Rice Vegetative Stage

## Basic Crop Information

| Field | Value |
|---|---|
| Crop | Rice |
| Season | Kharif |
| Stage | Vegetative |
| Week Range | 28–35 |

---

## Biological Expectations

| Signal | Expected Behavior |
|---|---|
| NDVI | Rising / High |
| NDWI | High |
| LST Sensitivity | High |
| Rainfall Sensitivity | High |

---

## Allowed Statistical Labels

### NDVI

```text
Normal
High-Normal
Very High
```

### NDWI

```text
Normal
High-Normal
Very High
```

### LST

```text
Very Low
Low-Normal
Normal
```

### Rainfall

```text
Normal
High-Normal
Very High
```
````
