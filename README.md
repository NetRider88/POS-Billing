# POS Billing Invoice Generator

Automated system for generating monthly invoices for POS integrators based on branch count.

**Rate:** $15 USD per branch per month

## Features

- ✅ **Automatic deduplication** using fuzzy matching to handle similar branch names
- ✅ **Professional PDF invoices** for each integrator
- ✅ **Detailed branch listings** with vendor codes and delivery types
- ✅ **Scheduled automation** runs on the 5th of each month
- ✅ **Summary reports** with total counts and revenue

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Option 1: Manual Run (Recommended for Testing)

Run the invoice generator manually whenever you have a new CSV file:

```bash
python generate_invoices.py
```

Or specify a custom CSV file:

```bash
python generate_invoices.py "path/to/your/file.csv"
```

### Option 2: Scheduled Automation

Set up automatic monthly invoice generation on the 5th of each month:

```bash
python schedule_invoices.py
```

This will:
- Run daily at 9:00 AM
- Check if it's the 5th of the month
- Generate invoices automatically if it is
- Log all activities to `invoice_scheduler.log`

**To test the scheduler immediately:**
```bash
python schedule_invoices.py --test
```

### Option 3: macOS Automation (LaunchAgent)

To run the scheduler automatically when your Mac starts:

1. **Create a LaunchAgent file:**
   ```bash
   nano ~/Library/LaunchAgents/com.posbilling.invoices.plist
   ```

2. **Add this content** (update paths to match your setup):
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.posbilling.invoices</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/python3</string>
           <string>/Users/jmosaad/Documents/Work Projects/POS Billing/schedule_invoices.py</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/Users/jmosaad/Documents/Work Projects/POS Billing</string>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/Users/jmosaad/Documents/Work Projects/POS Billing/scheduler_output.log</string>
       <key>StandardErrorPath</key>
       <string>/Users/jmosaad/Documents/Work Projects/POS Billing/scheduler_error.log</string>
   </dict>
   </plist>
   ```

3. **Load the LaunchAgent:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.posbilling.invoices.plist
   ```

4. **To stop it:**
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.posbilling.invoices.plist
   ```

## How It Works

### 1. Data Processing
- Reads the CSV export from your POS dashboard
- Groups branches by **Integration Name** (e.g., "Mcd Kuwait", "HS-Shawarma House")

### 2. Deduplication
The system uses **fuzzy matching** (85% similarity threshold) to identify duplicate branches:

**Examples of duplicates that will be caught:**
- "McDonald's, Sabah Al Ahmed" vs "McDonald's, Saba Al Ahmed"
- "McDonald's, Al Ahmed Sabah" vs "McDonald's, Sabah Al Ahmed"
- Minor typos or letter variations

**What counts as unique:**
- Different vendor codes = different branches
- Same vendor code but significantly different names = different branches
- Different delivery types (OWN_DELIVERY vs VENDOR_DELIVERY) = counted separately

### 3. Invoice Generation
For each integrator, generates a PDF invoice containing:
- Invoice number and date
- Billing period (month/year)
- Complete list of branches with:
  - Vendor code
  - Branch name
  - Delivery type
  - Rate per branch
- Summary with:
  - Total branch count
  - Rate per branch ($15)
  - Total amount due

### 4. Output
All invoices are saved to the `invoices/` folder with filenames like:
- `Mcd_Kuwait_2025_October.pdf`
- `HS-Shawarma_House_2025_October.pdf`

## File Structure

```
POS Billing/
├── POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv  # Input CSV
├── generate_invoices.py                                      # Main script
├── schedule_invoices.py                                      # Scheduler
├── requirements.txt                                          # Dependencies
├── README.md                                                 # This file
├── invoices/                                                 # Generated PDFs
│   ├── Mcd_Kuwait_2025_October.pdf
│   ├── Mcd_UAE_2025_October.pdf
│   └── ...
├── invoice_scheduler.log                                     # Scheduler logs
└── last_run.txt                                             # Tracks last run date
```

## Configuration

### Change the Scheduled Day
Edit `schedule_invoices.py` and modify:
```python
RUN_DAY = 5  # Change to any day of the month (1-31)
```

### Change the Scheduled Time
Edit `schedule_invoices.py` and modify:
```python
schedule.every().day.at("09:00").do(check_and_run)  # Change "09:00" to your preferred time
```

### Adjust Fuzzy Matching Sensitivity
Edit `generate_invoices.py` and modify:
```python
deduplicator = BranchDeduplicator(similarity_threshold=85)  # 0-100, higher = stricter
```

### Change the Rate per Branch
Edit `generate_invoices.py` and modify:
```python
RATE_PER_BRANCH = 15  # Change to your desired rate
```

## Workflow

### Monthly Process:
1. **Export CSV** from your POS dashboard (around the 1st-5th of each month)
2. **Save CSV** to the POS Billing folder with the expected filename
3. **Run script** (manual or automatic):
   - Manual: `python generate_invoices.py`
   - Automatic: Scheduler runs on the 5th at 9:00 AM
4. **Review invoices** in the `invoices/` folder
5. **Send to integrators** or forward to finance team

## Troubleshooting

### CSV file not found
- Ensure the CSV file is named exactly: `POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv`
- Or specify the path when running: `python generate_invoices.py "your_file.csv"`

### Missing dependencies
```bash
pip install -r requirements.txt
```

### Scheduler not running
- Check logs: `invoice_scheduler.log`
- Test immediately: `python schedule_invoices.py --test`
- Verify LaunchAgent is loaded: `launchctl list | grep posbilling`

### Invoices not generating
- Check that CSV has required columns: `Integration Name`, `vendor_code`, `Branch Name`, `Delivery Type`
- Review console output for error messages

## Future Enhancements

When you get buy-in from the company:
- [ ] Connect to API data source instead of manual CSV export
- [ ] Automatic email delivery to integrators
- [ ] Integration with finance system
- [ ] Historical tracking and reporting
- [ ] Multi-currency support

## Support

For issues or questions, check the logs:
- `invoice_scheduler.log` - Scheduler activity
- `scheduler_output.log` - Standard output (if using LaunchAgent)
- `scheduler_error.log` - Errors (if using LaunchAgent)

---

**Last Updated:** October 2025
