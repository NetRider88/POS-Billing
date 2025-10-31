# Quick Start Guide

## What Was Automated

Your monthly POS billing process is now fully automated! The system:

✅ **Reads your CSV export** from the POS dashboard  
✅ **Identifies all integrators** (72 found in your current data)  
✅ **Deduplicates branches** using fuzzy matching for similar names  
✅ **Generates professional PDF invoices** for each integrator  
✅ **Calculates totals** at $15 per branch per month  

## Test Results from Your Data

**Current Configuration:**
- 13 approved integrators (filtered from 39 non-KSA integrators)
- 10,144 branches processed
- **Total Revenue: $152,160 USD/month**
- All invoices saved to `invoices/` folder

**Top Integrators:**
- TLBT GrubTech Plugin: 6,102 branches ($91,530) ⚠️
- TLBT UrbanPiper Plugin: 2,599 branches ($38,985)
- Tlbt-Posist: 305 branches ($4,575)

**Exclusions & Special Rules:**
- **KSA EXCLUDED:** All Saudi Arabia (HS_SA) branches excluded (23,325 branches)
- **GrubTech:** Same branch with OWN_DELIVERY + VENDOR_DELIVERY = 1 branch (not 2)
- **OCIMS:** Kuwait only (125 branches)
- **OrderKing:** Egypt only (9 branches)
- **Ishbek:** Jordan only (132 branches)

## How to Use (3 Simple Steps)

### Monthly Process:

1. **Export CSV** from your POS dashboard
   - Save as: `POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv`
   - Place in this folder

2. **Run the script:**
   ```bash
   ./run_monthly_billing.sh
   ```
   
   Or:
   ```bash
   python3 generate_invoices.py
   ```

3. **Get your invoices:**
   - All PDFs are in the `invoices/` folder
   - One PDF per integrator
   - Ready to send!

## What Each Invoice Contains

✓ Invoice number and date  
✓ Billing period (month/year)  
✓ Integrator name  
✓ Complete branch list with:
  - Vendor codes
  - Branch names
  - Delivery types
  - Rate per branch
✓ Summary with total count and amount due  

## Files Created

```
POS Billing/
├── generate_invoices.py          ← Main script
├── schedule_invoices.py           ← Auto-scheduler (runs 5th of month)
├── run_monthly_billing.sh         ← Quick run script
├── test_single_integrator.py      ← Test individual integrators
├── requirements.txt               ← Python dependencies
├── README.md                      ← Full documentation
├── QUICK_START.md                 ← This file
├── INTEGRATORS_LIST.md            ← List of approved integrators
├── GRUBTECH_SPECIAL_RULE.md       ← GrubTech billing documentation
└── invoices/                      ← Generated PDFs (13 files)
    ├── TLBT_GrubTech_Plugin_2025_October.pdf
    ├── TLBT_UrbanPiper_Plugin_2025_October.pdf
    ├── Tlbt-Posist_2025_October.pdf
    └── ... (10 more)
```

## Advanced: Automatic Scheduling

To run automatically on the 5th of each month:

```bash
python3 schedule_invoices.py
```

This will:
- Run daily at 9:00 AM
- Check if it's the 5th
- Generate invoices automatically
- Log everything to `invoice_scheduler.log`

## Need Help?

**Test a specific integrator:**
```bash
# Edit test_single_integrator.py and change integrator_name
python3 test_single_integrator.py
```

**Check what integrators exist:**
```bash
python3 -c "import pandas as pd; df = pd.read_csv('POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv'); print(sorted(df['Integration Name'].dropna().unique()))"
```

**Regenerate all invoices:**
```bash
rm -rf invoices/
python3 generate_invoices.py
```

## Customization

### Change the rate per branch:
Edit `generate_invoices.py`, line 138:
```python
RATE_PER_BRANCH = 15  # Change to your rate
```

### Change fuzzy matching sensitivity:
Edit `generate_invoices.py`, line 341:
```python
deduplicator = BranchDeduplicator(similarity_threshold=85)  # 0-100
```
- Higher = stricter (fewer duplicates detected)
- Lower = looser (more duplicates detected)

### Change scheduled day:
Edit `schedule_invoices.py`, line 21:
```python
RUN_DAY = 5  # Change to any day (1-31)
```

## Next Steps (When You Get Buy-In)

Once approved by your company:
- [ ] Connect to API instead of manual CSV export
- [ ] Auto-email invoices to integrators
- [ ] Integrate with finance system
- [ ] Add historical tracking
- [ ] Multi-currency support

## Support

Check the logs if something goes wrong:
- Console output shows progress
- `invoice_scheduler.log` for scheduled runs
- All errors are logged with details

---

**Ready to use!** Just run `./run_monthly_billing.sh` whenever you have a new CSV file.
