# GrubTech Special Billing Rule

## Overview

**GrubTech integrators have a unique billing rule:** If the same branch appears with both `OWN_DELIVERY` and `VENDOR_DELIVERY`, it counts as **ONE branch** (not two).

This is different from all other integrators where each delivery type is billed separately.

---

## How It Works

### Standard Integrators (All Others)
```
Branch: "McDonald's, Sabah Al Ahmed"
├── OWN_DELIVERY    → Billed as 1 branch ($15)
└── VENDOR_DELIVERY → Billed as 1 branch ($15)
Total: 2 branches = $30
```

### GrubTech Integrators (HS GrubTech & TLBT GrubTech Plugin)
```
Branch: "Papa Kanafa, Al Warqa 1"
├── OWN_DELIVERY    → 
└── VENDOR_DELIVERY → Combined into 1 branch ($15)
Total: 1 branch = $15
```

---

## Technical Implementation

The system uses **fuzzy matching** (85% similarity threshold) to identify the same branch with different delivery types:

1. Compares branch names using token sort ratio
2. Ignores delivery type for GrubTech
3. Treats similar names as the same branch

### Examples Detected as Same Branch:
- "Papa Kanafa,Al Warqa 1" (OWN) + "Papa Kanafa, Al Warqa 1" (VENDOR)
- "Slice, Mishrif" (OWN) + "Slice, Mishrif" (VENDOR)
- "Kcal, Business Bay" (OWN) + "Kcal, Business Bay" (VENDOR)

---

## Impact on Billing

### HS GrubTech
- **Without special rule:** 2,490 branches = $37,350/month
- **With special rule:** 2,122 branches = $31,830/month
- **Savings:** 368 branches = $5,520/month

### TLBT GrubTech Plugin
- **Without special rule:** 7,503 branches = $112,545/month
- **With special rule:** 6,102 branches = $91,530/month
- **Savings:** 1,401 branches = $21,015/month

### Total GrubTech Impact
- **Combined savings:** 1,769 branches = **$26,535/month**

---

## Test Results

From the actual data analysis:

### HS GrubTech
- Total entries: 2,495
- All are OWN_DELIVERY (no VENDOR_DELIVERY in this dataset)
- Duplicates removed: 373 (same branch, different vendor codes)
- **Final billable:** 2,122 branches

### TLBT GrubTech Plugin
- Total entries: 7,506
  - OWN_DELIVERY: 6,880
  - VENDOR_DELIVERY: 626
- Found 115 branch names appearing with both delivery types
- Duplicates removed: 1,404
- **Final billable:** 6,102 branches

---

## Code Location

The special logic is implemented in `generate_invoices.py`:

**Line 38-92:** `BranchDeduplicator.deduplicate_branches()` method with `ignore_delivery_type` parameter

**Line 404-414:** Detection and application of GrubTech special rule:
```python
# Check if this is a GrubTech integrator (special deduplication rule)
is_grubtech = 'grubtech' in integrator.lower()

# Deduplicate branches
if is_grubtech:
    # For GrubTech: Same branch with OWN_DELIVERY and VENDOR_DELIVERY counts as ONE
    unique_branches = deduplicator.deduplicate_branches(branches, ignore_delivery_type=True)
    print(f"  • GrubTech special rule: Same branch with different delivery types = 1 branch")
else:
    # Standard deduplication
    unique_branches = deduplicator.deduplicate_branches(branches, ignore_delivery_type=False)
```

---

## Testing

To verify the GrubTech logic:

```bash
python3 test_grubtech.py
```

This will show:
- Breakdown by delivery type
- Examples of branches with both delivery types
- Comparison of standard vs GrubTech deduplication
- Billing impact

---

## Important Notes

1. ⚠️ **Only applies to GrubTech** (HS GrubTech and TLBT GrubTech Plugin)
2. Uses fuzzy matching to handle slight name variations
3. Automatically detected by checking if "grubtech" is in the integrator name
4. Reduces billing by ~18% for GrubTech integrators
5. All other integrators bill each delivery type separately

---

**Last Updated:** October 20, 2025
