# Approved Integrators for Billing

## Overview
Only the following integrators will have invoices generated. Total: **13 integrators**

⚠️ **IMPORTANT:** KSA (Saudi Arabia - Entity ID: HS_SA) is **EXCLUDED** from all billing.

---

## Integrators List

### 1. **GrubTech** ⚠️ Special Billing Rule
- ~~HS GrubTech~~ (EXCLUDED - KSA only)
- TLBT GrubTech Plugin (6,102 branches)
- **Subtotal:** 6,102 branches | $91,530/month
- **Special Rule:** Same branch with OWN_DELIVERY and VENDOR_DELIVERY = 1 branch (not 2)

### 2. **UrbanPiper**
- ~~HS-UrbanPiper~~ (EXCLUDED - KSA only)
- TLBT UrbanPiper Plugin (2,599 branches)
- **Subtotal:** 2,599 branches | $38,985/month

### 3. **Wi-Q**
- ~~HS-Wi-Q-Alshaya KSA~~ (EXCLUDED - KSA only)
- Wi-Q (226 branches)
- **Subtotal:** 226 branches | $3,390/month

### 4. **LimeTray**
- TLBT LimeTray (338 branches)
- **Subtotal:** 338 branches | $5,070/month

### 5. **PetPooja**
- Petpooja (71 branches)
- **Subtotal:** 71 branches | $1,065/month

### 6. **Posist**
- ~~HS Posist Plugin~~ (EXCLUDED - KSA only)
- Tlbt-Posist (305 branches)
- **Subtotal:** 305 branches | $4,575/month

### 7. **OCIMS** (Kuwait Only)
- MENA-TLB-OCIMS (72 branches - TB_KW only)
- TLBT OCIMS Naif (53 branches - TB_KW only)
- **Subtotal:** 125 branches | $1,875/month
- ⚠️ **Entity Filter:** Only Kuwait (TB_KW) branches

### 8. **iiko**
- TLBT iiko Plugin (214 branches)
- **Subtotal:** 214 branches | $3,210/month

### 9. **OrderKing** (Egypt Only)
- Tlbt-Orderking (9 branches - HF_EG only)
- **Subtotal:** 9 branches | $135/month
- ⚠️ **Entity Filter:** Only Egypt (HF_EG) branches

### 10. **Ishbek** (Jordan Only)
- Tlbt-Ishbek (132 branches - TB_JO only)
- **Subtotal:** 132 branches | $1,980/month
- ⚠️ **Entity Filter:** Only Jordan (TB_JO) branches

### 11. **TMBill**
- ~~HS-TMBill-KSA~~ (EXCLUDED - KSA only)
- TLBT-TMBill (22 branches)
- **Subtotal:** 22 branches | $330/month

### 12. **FeedUs**
- Tlbt-FeedUs (1 branch)
- **Subtotal:** 1 branch | $15/month

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Integrators** | 13 |
| **Total Branches** | 10,144 |
| **Monthly Revenue** | $152,160 USD |
| **Rate per Branch** | $15 USD |

### Notes:
- **KSA EXCLUDED:** All Saudi Arabia (HS_SA) branches are excluded from billing
  - 23,325 KSA branches excluded
  - 5 integrators removed (HS GrubTech, HS-UrbanPiper, HS-Wi-Q-Alshaya KSA, HS Posist Plugin, HS-TMBill-KSA)
- **GrubTech Special Rule:** Branches with both OWN_DELIVERY and VENDOR_DELIVERY are counted as ONE branch
  - This reduced TLBT GrubTech billing by 1,404 branches ($21,015/month)

---

## Entity Codes Reference

- **TB_KW** = Talabat Kuwait
- **HF_EG** = HungerStation Egypt
- **TB_JO** = Talabat Jordan
- **HS_SA** = HungerStation Saudi Arabia ⚠️ **EXCLUDED FROM BILLING**
- **TB_AE** = Talabat UAE
- **TB_OM** = Talabat Oman
- **TB_BH** = Talabat Bahrain
- **TB_QA** = Talabat Qatar

---

## Configuration

The allowed integrators are configured in `generate_invoices.py` at line 346:

```python
ALLOWED_INTEGRATORS = {
    'HS GrubTech': None,
    'TLBT GrubTech Plugin': None,
    'HS-UrbanPiper': None,
    'TLBT UrbanPiper Plugin': None,
    'HS-Wi-Q-Alshaya KSA': None,
    'Wi-Q': None,
    'TLBT LimeTray': None,
    'Petpooja': None,
    'HS Posist Plugin': None,
    'Tlbt-Posist': None,
    'MENA-TLB-OCIMS': ['TB_KW'],  # KW only
    'TLBT OCIMS Naif': ['TB_KW'],  # KW only
    'TLBT iiko Plugin': None,
    'Tlbt-Orderking': ['HF_EG'],  # EG only
    'Tlbt-Ishbek': ['TB_JO'],  # JO only
    'HS-TMBill-KSA': None,
    'TLBT-TMBill': None,
    'Tlbt-FeedUs': None,
}
```

**Note:** `None` means all entities are included. Specific entity codes mean only those regions are billed.

---

**Last Updated:** October 20, 2025
