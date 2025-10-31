#!/usr/bin/env python3
"""
Test script to verify GrubTech special deduplication logic
"""

import pandas as pd
from generate_invoices import BranchDeduplicator

# Read CSV
csv_path = "POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv"
df = pd.read_csv(csv_path)

print("\n" + "="*70)
print("GRUBTECH DEDUPLICATION TEST")
print("="*70 + "\n")

# Test both GrubTech integrators
grubtech_integrators = ['HS GrubTech', 'TLBT GrubTech Plugin']

for integrator_name in grubtech_integrators:
    print(f"\n{'='*70}")
    print(f"Testing: {integrator_name}")
    print(f"{'='*70}\n")
    
    # Filter for this integrator
    integrator_df = df[df['Integration Name'] == integrator_name].copy()
    branches = integrator_df[['vendor_code', 'Branch Name', 'Delivery Type']].copy()
    
    print(f"Total branches in CSV: {len(branches)}")
    
    # Count by delivery type
    delivery_counts = branches['Delivery Type'].value_counts()
    print(f"\nBreakdown by delivery type:")
    for dtype, count in delivery_counts.items():
        print(f"  {dtype}: {count}")
    
    # Show some examples with both delivery types
    print(f"\nLooking for branches with both delivery types...")
    branch_names = branches['Branch Name'].value_counts()
    duplicates = branch_names[branch_names > 1]
    
    if len(duplicates) > 0:
        print(f"Found {len(duplicates)} branch names appearing multiple times:")
        for branch_name, count in duplicates.head(10).items():
            matching = branches[branches['Branch Name'] == branch_name]
            print(f"\n  '{branch_name}' appears {count} times:")
            for idx, row in matching.iterrows():
                print(f"    - {row['vendor_code']} | {row['Delivery Type']}")
    else:
        print("No exact duplicate branch names found.")
    
    # Test deduplication
    deduplicator = BranchDeduplicator(similarity_threshold=85)
    
    print(f"\n{'='*70}")
    print("STANDARD DEDUPLICATION (delivery type matters):")
    unique_standard = deduplicator.deduplicate_branches(branches, ignore_delivery_type=False)
    print(f"  Original: {len(branches)}")
    print(f"  Unique: {len(unique_standard)}")
    print(f"  Removed: {len(branches) - len(unique_standard)}")
    
    print(f"\nGRUBTECH SPECIAL DEDUPLICATION (delivery type ignored):")
    unique_grubtech = deduplicator.deduplicate_branches(branches, ignore_delivery_type=True)
    print(f"  Original: {len(branches)}")
    print(f"  Unique: {len(unique_grubtech)}")
    print(f"  Removed: {len(branches) - len(unique_grubtech)}")
    
    difference = len(unique_standard) - len(unique_grubtech)
    print(f"\n💰 BILLING IMPACT:")
    print(f"  Standard method: {len(unique_standard)} branches × $15 = ${len(unique_standard) * 15:,}")
    print(f"  GrubTech method: {len(unique_grubtech)} branches × $15 = ${len(unique_grubtech) * 15:,}")
    print(f"  Difference: {difference} branches = ${difference * 15:,}")

print("\n" + "="*70 + "\n")
