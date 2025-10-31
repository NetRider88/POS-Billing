#!/bin/bash
# Quick script to run monthly billing
# Usage: ./run_monthly_billing.sh

echo "======================================"
echo "POS Monthly Billing - Quick Run"
echo "======================================"
echo ""

# Check if CSV file exists
if [ ! -f "POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv" ]; then
    echo "❌ Error: CSV file not found!"
    echo "Please ensure 'POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv' is in this folder."
    exit 1
fi

echo "✓ CSV file found"
echo ""
echo "Generating invoices..."
echo ""

# Run the invoice generator
python3 generate_invoices.py

echo ""
echo "======================================"
echo "Done! Check the 'invoices' folder for PDFs"
echo "======================================"
