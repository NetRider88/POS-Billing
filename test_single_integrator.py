#!/usr/bin/env python3
"""
Test script to check a single integrator's invoice details
"""

import pandas as pd
from generate_invoices import BranchDeduplicator

# Read CSV
csv_path = "POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv"
df = pd.read_csv(csv_path)

# Test with Mcd Kuwait
integrator_name = "Mcd Kuwait"
print(f"\n{'='*60}")
print(f"Testing: {integrator_name}")
print(f"{'='*60}\n")

# Filter for this integrator
integrator_df = df[df['Integration Name'] == integrator_name].copy()
print(f"Total rows in CSV: {len(integrator_df)}")

# Get branches
branches = integrator_df[['vendor_code', 'Branch Name', 'Delivery Type']].copy()
print(f"Total branches before deduplication: {len(branches)}")

# Show first few branches
print("\nFirst 10 branches:")
for idx, row in branches.head(10).iterrows():
    print(f"  {row['vendor_code']} - {row['Branch Name']} - {row['Delivery Type']}")

# Deduplicate
deduplicator = BranchDeduplicator(similarity_threshold=85)
unique_branches = deduplicator.deduplicate_branches(branches)

print(f"\nUnique branches after deduplication: {len(unique_branches)}")
print(f"Duplicates removed: {len(branches) - len(unique_branches)}")

# Calculate billing
rate = 15
total = len(unique_branches) * rate
print(f"\n{'='*60}")
print(f"BILLING SUMMARY")
print(f"{'='*60}")
print(f"Integrator: {integrator_name}")
print(f"Unique Branches: {len(unique_branches)}")
print(f"Rate per Branch: ${rate} USD")
print(f"Total Amount: ${total:,.2f} USD")
print(f"{'='*60}\n")
