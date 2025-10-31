#!/usr/bin/env python3
"""
Scheduled Invoice Generator
Automatically runs invoice generation on the 5th of each month.
"""

import schedule
import time
from datetime import datetime
from pathlib import Path
from generate_invoices import process_csv_and_generate_invoices
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('invoice_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
CSV_FILE = "POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv"
RUN_DAY = 5  # 5th of each month


def run_monthly_invoicing():
    """Run the invoice generation process."""
    logger.info("="*60)
    logger.info("SCHEDULED INVOICE GENERATION STARTED")
    logger.info("="*60)
    
    try:
        # Check if CSV file exists
        if not Path(CSV_FILE).exists():
            logger.error(f"CSV file not found: {CSV_FILE}")
            logger.error("Please ensure the CSV file is in the correct location.")
            return
        
        # Get current month and year
        now = datetime.now()
        billing_month = now.strftime("%B")
        billing_year = now.year
        
        logger.info(f"Generating invoices for {billing_month} {billing_year}")
        
        # Run invoice generation
        summary = process_csv_and_generate_invoices(CSV_FILE, billing_month, billing_year)
        
        logger.info("✓ Invoice generation completed successfully")
        logger.info(f"Total integrators processed: {len(summary)}")
        
    except Exception as e:
        logger.error(f"Error during invoice generation: {str(e)}", exc_info=True)
    
    logger.info("="*60)


def should_run_today():
    """Check if today is the scheduled day to run."""
    today = datetime.now().day
    return today == RUN_DAY


def check_and_run():
    """Check if it's time to run and execute if needed."""
    if should_run_today():
        # Check if we've already run today
        log_file = Path("last_run.txt")
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        if log_file.exists():
            last_run = log_file.read_text().strip()
            if last_run == today_str:
                logger.info(f"Already ran today ({today_str}). Skipping.")
                return
        
        # Run the invoicing
        run_monthly_invoicing()
        
        # Record that we ran today
        log_file.write_text(today_str)
    else:
        logger.info(f"Not scheduled to run today. Next run: {RUN_DAY}th of the month")


def main():
    """Main scheduler loop."""
    logger.info("Invoice Scheduler Started")
    logger.info(f"Scheduled to run on the {RUN_DAY}th of each month at 9:00 AM")
    logger.info("Press Ctrl+C to stop")
    logger.info("-"*60)
    
    # Schedule the job to run daily at 9:00 AM
    # It will check if it's the 5th and run accordingly
    schedule.every().day.at("09:00").do(check_and_run)
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user")


if __name__ == "__main__":
    # For testing: run immediately
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        logger.info("TEST MODE: Running invoice generation immediately")
        run_monthly_invoicing()
    else:
        main()
