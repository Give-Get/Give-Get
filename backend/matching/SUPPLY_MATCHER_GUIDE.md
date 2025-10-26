# Supply Matcher Guide

## Overview

`supply_matcher.py` matches **donors** (people with items to donate) to **organizations** (shelters/charities that need those items).

---

## Key Differences from People Matcher

| Feature | People Matcher | Supply Matcher |
|---------|---------------|----------------|
| **Input** | Person's needs (housing, food, etc.) | Donor's items (food, clothing, etc.) |
| **Matches To** | Organizations that provide services | Organizations that need donations |
| **Primary Factor** | Fit & Capacity | Urgency & Gap Size |
| **Scoring Focus** | How well shelter fits person | How badly org needs the items |

---

## Data Structures

### Donor Items Format:
```python
donor_items = {
    "location": {"lat": 40.79, "lng": -77.86},
    "items": [
        {"category": "food", "item": "canned beans", "quantity": 100},
        {"category": "clothing", "item": "jackets", "quantity": 30}
    ]
}
```

### Organization Needs Format:
```python
organization = {
    "name": "Centre County Food Bank",
    "location": {"lat": 40.795, "lng": -77.865},
    "needs": {
        "canned_beans": {
            "category": "food",
            "needed": 200,    # Total needed
            "have": 150,      # Current stock
            "urgency": "high" # "high", "medium", or "low"
        },
        "rice": {
            "category": "food",
            "needed": 100,
            "have": 80,
            "urgency": "high"
        }
    }
}
```

---

## Matching Flow

```
1. Donor fills out survey
   ↓
2. Get organizations within radius
   ↓
3. Filter: Does org need donor's item categories?
   ↓
4. Score each match:
   - Urgency (40%): How urgent is the need?
   - Gap (35%): How big is the gap (needed - have)?
   - Distance (25%): How far is the donor?
   ↓
5. Sort by need score (highest first)
   ↓
6. Return ranked dictionary with scores
```

---

## Scoring Components

### 1. Urgency Score (40% weight)

Looks at the organization's urgency level for items in categories the donor has.

```python
Urgency Levels:
- "high":   1.0 (100% score)
- "medium": 0.6 (60% score)
- "low":    0.3 (30% score)

Returns: Highest urgency among matching categories
```

**Example:**
- Food Bank needs `canned_beans` (urgency: "high")
- Donor has `food` category items
- Urgency Score = 1.0

---

### 2. Gap Score (35% weight)

Measures how much the organization needs vs what they have.

```python
Gap = needed - have

Gap Severity = gap / needed  (what % is missing?)
Fill Percentage = min(donor_quantity / gap, 1.0)  (can donor fill it?)

Gap Score = (gap_severity * 0.6) + (fill_percentage * 0.4)
```

**Example:**
- Org needs 200 canned beans, has 150 → gap = 50
- Donor has 100 canned beans
- Gap Severity = 50/200 = 0.25
- Fill Percentage = min(100/50, 1.0) = 1.0 (can fill entire gap!)
- Gap Score = (0.25 * 0.6) + (1.0 * 0.4) = 0.55

---

### 3. Distance Score (25% weight)

Closer donors score higher, but distance is less critical for donations.

```python
Max Distance: 50 miles (more lenient than people matching)

if distance <= 0:      score = 1.0
if distance >= 50:     score = 0.0
else:                  score = 1.0 - (distance / 50)
```

**Example:**
- Donor is 10 miles away
- Distance Score = 1.0 - (10/50) = 0.8

---

## Overall Need Score Formula

```python
Total Score = (
    urgency_score * 0.40 +
    gap_score * 0.35 +
    distance_score * 0.25
) * 100

Range: 0-100 (100 = highest need)
```

---

## Example Scenario

### Donor:
- Location: State College, PA
- Has: 100 canned beans

### Food Bank:
- Location: 0.5 miles away
- Needs: 200 canned beans (has 150, urgency: high)

### Scoring:
```
Urgency Score: 1.0 (high urgency)
Gap Score: 0.55 (gap of 50, donor can fill it)
Distance Score: 0.99 (very close)

Total = (1.0 * 0.40) + (0.55 * 0.35) + (0.99 * 0.25) * 100
      = (0.40 + 0.19 + 0.25) * 100
      = 84 / 100
```

**Result:** Food Bank ranks with score of 84/100

---

## Return Format

```python
{
    1: {
        "name": "Centre County Food Bank",
        "location": {"lat": 40.795, "lng": -77.865},
        "needs": {...},
        "score": 84  # Need score 0-100
    },
    2: {
        "name": "Community Clothing Drive",
        "score": 72
    }
}
```

---

## Function Reference

### Main Function

```python
sort_organizations_by_need(location, radius, donor_items=None) -> dict
```
- **location**: Donor's lat/lng
- **radius**: Search radius in miles
- **donor_items**: Items to donate (optional)
- **Returns**: {rank: organization_with_score}

---

### Helper Functions

```python
_organization_needs_items(donor_items, organization) -> bool
```
Checks if org needs any of donor's item categories

```python
_compute_need_score(donor_items, organization, distance) -> float
```
Calculates overall need score (0-100)

```python
_calculate_urgency_score(donor_items, organization) -> float
```
Returns urgency level (0-1)

```python
_calculate_gap_score(donor_items, organization) -> float
```
Returns gap severity and fill potential (0-1)

```python
_calculate_distance_score(distance_miles) -> float
```
Converts distance to score (0-1)

---

## Testing

Run the test suite:
```bash
cd /Users/arshawn/Desktop/GiveAndGet/Give-Get/backend/matching
python3 test_supply_matcher.py
```

---

## Database Integration

You need to implement:

```python
from backend.database import get_orgs_within_radius

def get_orgs_within_radius(location: dict, radius: int, org_type: dict) -> list[tuple]:
    """
    Returns: [(distance_miles, organization_dict), ...]
    """
    pass
```

---

## Next Steps

1. ✅ Core matching logic complete
2. ⏳ Implement `get_orgs_within_radius` with actual database
3. ⏳ Test with real data
4. ⏳ Tune scoring weights based on real-world feedback
5. ⏳ Add explainability (why this org needs your donation)

---

## Notes

- **No feasibility constraints**: Unlike people matching, we don't have hard "yes/no" filters. Any organization that needs items in the donor's categories is a potential match.
- **Urgency-driven**: Organizations with urgent needs rank higher.
- **Gap-aware**: Bigger gaps (more need) rank higher.
- **Distance-flexible**: 50-mile radius vs 25-mile for people (donors are often willing to drive further).

