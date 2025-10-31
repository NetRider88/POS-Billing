#!/usr/bin/env python3
"""
POS Billing Invoice Generator
Automatically generates monthly invoices for integrators based on branch count.
Rate: $15 per branch per month
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import re
import sys
from fuzzywuzzy import fuzz
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from collections import defaultdict


BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "exports"

ALLOWED_COLUMNS = [
    "Entity ID",
    "vendor_code",
    "remote_id",
    "Branch Name",
    "Integration Name",
    "Chain ID",
    "Chain Name",
    "Delivery Type",
    "Orders",
]

COUNTRY_MAP = {
    "TB_KW": "Kuwait",
    "TB_AE": "UAE",
    "TB_OM": "Oman",
    "TB_BH": "Bahrain",
    "TB_QA": "Qatar",
    "TB_JO": "Jordan",
    "HF_EG": "Egypt",
    "HS_SA": "Saudi Arabia",
}


def normalize_name(value):
    """Return a simplified string for case/format insensitive comparisons."""
    if pd.isna(value):
        return ""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def normalize_series(series):
    """Vectorised normalisation matching normalize_name."""
    return (
        series.fillna("")
        .str.lower()
        .str.replace(r"[^a-z0-9]", "", regex=True)
    )


def slugify(value):
    """Create a filesystem-safe slug."""
    return re.sub(r"[^A-Za-z0-9]+", "_", str(value)).strip("_").lower()


URBAN_PIPER_UAE_EXCLUSION_NAMES = {
    "Edo Sushi and Poke",
    "Else Burger",
}

LIMETRAY_UAE_EXCLUSION_NAMES = {
    "Toss & Co.",
    "World of Asia",
    "Biryani Boy",
    "Tim Hortons",
    "Chef Lanka",
    "Steers",
    "Debonairs Pizza , Dibba",
    "Tim Hortons home select",
    "The Kebab Shop",
}

URBAN_PIPER_UAE_EXCLUSIONS = {normalize_name(name) for name in URBAN_PIPER_UAE_EXCLUSION_NAMES}
LIMETRAY_UAE_EXCLUSIONS = {normalize_name(name) for name in LIMETRAY_UAE_EXCLUSION_NAMES}

INTEGRATOR_RULES = {
    # Grubtech
    slugify("HS GrubTech"): {"grubtech"},
    slugify("TLBT GrubTech Plugin"): {"grubtech"},
    slugify("Grubtech"): {"grubtech"},

    # Limetray
    slugify("Limetray [UAE]"): {"limetray_uae"},
    slugify("TLBT LimeTray"): {"limetray_uae"},
    slugify("Limetray"): {"limetray_uae"},

    # Urban Piper
    slugify("Urban Piper [UAE]"): {"urbanpiper_uae"},
    slugify("HS-UrbanPiper"): {"urbanpiper_uae"},
    slugify("TLBT UrbanPiper Plugin"): {"urbanpiper_uae"},
    slugify("Urban Piper"): {"urbanpiper_uae"},
    slugify("urbanpiper"): {"urbanpiper_uae"},
}


def remove_snap_rows(df, entity_ids=None):
    """Remove rows whose branch or chain include 'snap'."""
    snap_mask = (
        df["Branch Name"].str.contains("snap", case=False, na=False)
        | df["Chain Name"].str.contains("snap", case=False, na=False)
    )
    if entity_ids:
        entity_mask = df["Entity ID"].isin(set(entity_ids))
        snap_mask = snap_mask & entity_mask
    return df[~snap_mask].copy()


def exclude_named_locations(df, entity_id, exclusions):
    """Exclude rows for a specific entity whose branch/chain match block list."""
    if df.empty:
        return df
    entity_mask = df["Entity ID"] == entity_id
    if not entity_mask.any():
        return df
    branch_norm = normalize_series(df["Branch Name"])
    chain_norm = normalize_series(df["Chain Name"])
    block_mask = entity_mask & (
        branch_norm.isin(exclusions) | chain_norm.isin(exclusions)
    )
    return df[~block_mask].copy()


def apply_integrator_exclusions(df, integrator_name, rules):
    """Apply integrator-specific exclusion rules."""
    if df.empty or not rules:
        return df

    result = df.copy()

    if "grubtech" in rules:
        result = remove_snap_rows(result)

    if "urbanpiper_uae" in rules:
        result = remove_snap_rows(result, entity_ids={"TB_AE"})
        result = exclude_named_locations(result, "TB_AE", URBAN_PIPER_UAE_EXCLUSIONS)

    if "limetray_uae" in rules:
        result = remove_snap_rows(result, entity_ids={"TB_AE"})
        result = exclude_named_locations(result, "TB_AE", LIMETRAY_UAE_EXCLUSIONS)

    return result


def apply_business_rules(integrator_name, integrator_df, deduplicator):
    """Apply all business rules for a given integrator."""
    slug = slugify(integrator_name)
    rules = INTEGRATOR_RULES.get(slug, set())

    print(f"Processing integrator: {integrator_name} ({len(integrator_df)} rows)")

    # Apply integrator-specific exclusions
    filtered_df = apply_integrator_exclusions(integrator_df, integrator_name, rules)
    removed_due_to_rules = len(integrator_df) - len(filtered_df)
    if removed_due_to_rules:
        print(f"  • Excluded {removed_due_to_rules} rows due to integrator-specific rules")

    if filtered_df.empty:
        print("  • No data left after exclusions, skipping\n")
        return pd.DataFrame()

    # Deduplicate branches
    # For Grubtech, we ignore delivery type to handle TGO vs TMP duplicates (assumed to be own delivery vs restaurant delivery)
    ignore_delivery_type = "grubtech" in rules
    unique_keys = deduplicator.deduplicate_branches(
        filtered_df, ignore_delivery_type=ignore_delivery_type
    )

    if unique_keys.empty:
        print("  • No unique branches identified, skipping\n")
        return pd.DataFrame()

    # Merge to get final unique branches
    deduped_df = filtered_df.merge(
        unique_keys,
        on=list(unique_keys.columns),
        how="inner",
    )

    print(
        f"  • Unique branches after dedupe: {len(deduped_df)} (from {len(filtered_df)})"
        + (" [delivery type ignored]" if ignore_delivery_type else "")
    )
    
    return deduped_df


class BranchDeduplicator:
    """Handles fuzzy matching to identify duplicate branches with similar names."""
    
    def __init__(self, similarity_threshold=85):
        """
        Args:
            similarity_threshold: Minimum similarity score (0-100) to consider branches as duplicates
        """
        self.similarity_threshold = similarity_threshold
    
    def are_similar(self, name1, name2):
        """Check if two branch names are similar using fuzzy matching."""
        # Use token sort ratio to handle word order differences
        similarity = fuzz.token_sort_ratio(name1.lower(), name2.lower())
        return similarity >= self.similarity_threshold
    
    def deduplicate_branches(self, branches_df, ignore_delivery_type=False):
        """
        Deduplicate branches based on vendor_code and similar branch names.
        
        Args:
            branches_df: DataFrame with branch information
            ignore_delivery_type: If True, treat same branch with different delivery types as one
        
        Returns:
            DataFrame with unique branches
        """
        if branches_df.empty:
            return pd.DataFrame(columns=branches_df.columns)

        unique_branches = []
        seen_groups = {}

        for _, row in branches_df.iterrows():
            branch_name = row["Branch Name"]
            key = normalize_name(branch_name) if ignore_delivery_type else row["vendor_code"]

            if key not in seen_groups:
                seen_groups[key] = [row]
                unique_branches.append(row)
                continue

            is_duplicate = False
            for seen_branch in seen_groups[key]:
                if self.are_similar(branch_name, seen_branch["Branch Name"]):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_groups[key].append(row)
                unique_branches.append(row)

        return pd.DataFrame(unique_branches) if unique_branches else pd.DataFrame(columns=branches_df.columns)


class InvoiceGenerator:
    """Generates PDF invoices for integrators."""
    
    RATE_PER_BRANCH = 15  # EUR per branch per month
    
    # Tax rates by country (Entity ID prefix)
    TAX_RATES = {
        'TB_KW': 0.00,   # Kuwait - No VAT
        'TB_AE': 0.05,   # UAE - 5% VAT
        'TB_OM': 0.05,   # Oman - 5% VAT
        'TB_BH': 0.10,   # Bahrain - 10% VAT
        'TB_QA': 0.00,   # Qatar - No VAT
        'TB_JO': 0.16,   # Jordan - 16% VAT
        'HF_EG': 0.14,   # Egypt - 14% VAT
        'HS_SA': 0.15,   # Saudi Arabia - 15% VAT (excluded anyway)
    }
    
    def __init__(self, output_dir="invoices"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the invoice."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
    
    def generate_invoice(self, integrator_name, branches_df, billing_month, billing_year):
        """
        Generate a PDF invoice for a specific integrator.
        
        Args:
            integrator_name: Name of the integrator
            branches_df: DataFrame containing branch details
            billing_month: Month name (e.g., "October")
            billing_year: Year (e.g., 2025)
        """
        # Create filename
        filename = f"{integrator_name.replace(' ', '_')}_{billing_year}_{billing_month}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add invoice header
        elements.extend(self._create_header(integrator_name, billing_month, billing_year))
        
        # Add branch details table
        elements.extend(self._create_branch_table(branches_df))
        
        # Add summary section
        entity_breakdown = branches_df.groupby("Entity ID").size().to_dict()
        elements.extend(self._create_summary(branches_df, entity_breakdown))
        
        # Build PDF
        doc.build(elements)
        
        return filepath
    
    def _create_header(self, integrator_name, billing_month, billing_year):
        """Create invoice header section."""
        elements = []
        
        # Title
        title = Paragraph(
            "MONTHLY INTEGRATION INVOICE",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Invoice details
        invoice_date = datetime.now().strftime("%B %d, %Y")
        invoice_number = f"INV-{billing_year}{datetime.now().month:02d}-{integrator_name.replace(' ', '')[:10].upper()}"
        
        details_data = [
            ['Invoice Number:', invoice_number],
            ['Invoice Date:', invoice_date],
            ['Billing Period:', f"{billing_month} {billing_year}"],
            ['Integrator:', integrator_name],
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(details_table)
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_branch_table(self, branches_df):
        """Create table with branch details."""
        elements = []
        
        # Section header
        header = Paragraph("Branch Details", self.styles['SectionHeader'])
        elements.append(header)
        
        # Prepare table data
        table_data = [['#', 'Vendor Code', 'Branch Name', 'Delivery Type', 'Rate (EUR)']]
        
        for idx, row in branches_df.iterrows():
            table_data.append([
                str(idx + 1),
                str(row['vendor_code']),
                row['Branch Name'],
                row['Delivery Type'],
                f"€{self.RATE_PER_BRANCH}"
            ])
        
        # Create table
        col_widths = [0.5*inch, 1*inch, 3*inch, 1.2*inch, 1*inch]
        branch_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        branch_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # # column
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Vendor Code
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Delivery Type
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # Rate
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(branch_table)
        elements.append(Spacer(1, 0.4*inch))
        
        return elements
    
    def _create_summary(self, branches_df, entity_breakdown):
        """Create invoice summary section with tax calculation."""
        elements = []
        
        # Calculate totals
        branch_count = len(branches_df)
        subtotal = branch_count * self.RATE_PER_BRANCH
        
        # Calculate tax by entity
        tax_by_entity = {}
        total_tax = 0
        
        for entity_id, count in entity_breakdown.items():
            tax_rate = self.TAX_RATES.get(entity_id, 0.00)
            entity_subtotal = count * self.RATE_PER_BRANCH
            entity_tax = entity_subtotal * tax_rate
            total_tax += entity_tax
            if tax_rate > 0:
                tax_by_entity[entity_id] = {
                    'rate': tax_rate,
                    'amount': entity_tax,
                    'branches': count
                }
        
        total_amount = subtotal + total_tax
        
        # Summary table
        summary_data = [
            ['Total Branches:', str(branch_count)],
            ['Rate per Branch:', f'€{self.RATE_PER_BRANCH} EUR'],
            ['Subtotal:', f'€{subtotal:,.2f} EUR'],
        ]
        
        # Add tax breakdown if applicable
        if tax_by_entity:
            summary_data.append(['', ''])
            summary_data.append(['Tax Breakdown:', ''])
            for entity_id, tax_info in sorted(tax_by_entity.items()):
                entity_name = entity_id.replace('_', ' ')
                summary_data.append([
                    f'  {entity_name} ({tax_info["branches"]} branches @ {tax_info["rate"]*100:.0f}% VAT):',
                    f'€{tax_info["amount"]:,.2f} EUR'
                ])
            summary_data.append(['Total Tax:', f'€{total_tax:,.2f} EUR'])
        
        summary_data.append(['', ''])
        summary_data.append(['TOTAL AMOUNT DUE:', f'€{total_amount:,.2f} EUR'])
        
        summary_table = Table(summary_data, colWidths=[4.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            # Regular rows
            ('FONT', (0, 0), (0, 1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, 1), 'Helvetica', 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            
            # Total row (last row)
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 14),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2c3e50')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4f8')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2c3e50')),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer note
        footer_text = Paragraph(
            "<i>Payment terms: Net 30 days from invoice date</i>",
            self.styles['Normal']
        )
        elements.append(footer_text)
        
        return elements


def generate_integrator_csv(integrator_name, country_name, branches_df, output_root, billing_month, billing_year):
    """Generate a CSV file for a specific integrator/country combination."""
    period_dir = Path(output_root) / f"{billing_year}_{slugify(billing_month)}"
    integrator_dir = period_dir / slugify(integrator_name)
    integrator_dir.mkdir(parents=True, exist_ok=True)

    filename = (
        f"{slugify(integrator_name)}_{slugify(country_name)}_{billing_year}_{slugify(billing_month)}.csv"
    )
    filepath = integrator_dir / filename

    ordered_columns = [col for col in ALLOWED_COLUMNS if col in branches_df.columns]
    if "Country" in branches_df.columns:
        ordered_columns.append("Country")

    export_df = branches_df.loc[:, ordered_columns]
    sort_columns = [col for col in ("Branch Name", "vendor_code") if col in export_df.columns]
    if sort_columns:
        export_df = export_df.sort_values(sort_columns)

    export_df.to_csv(filepath, index=False)
    return filepath


def process_uploaded_csv(csv_path):
    """Load, validate, and filter the uploaded CSV."""
    raw_df = pd.read_csv(csv_path)
    print(f"📄 Loaded {len(raw_df)} total records from {csv_path}")

    missing_columns = [col for col in ALLOWED_COLUMNS if col not in raw_df.columns]
    if missing_columns:
        print(f"⚠️  Missing columns in source CSV: {', '.join(missing_columns)} (will be created as empty)")
    for col in missing_columns:
        raw_df[col] = pd.NA

    df = raw_df[ALLOWED_COLUMNS].copy()
    df["Integration Name"] = df["Integration Name"].fillna("").astype(str)
    df = df[df["Integration Name"].str.strip() != ""].copy()

    df["Orders"] = pd.to_numeric(df["Orders"], errors="coerce")
    df["Country"] = df["Entity ID"].map(COUNTRY_MAP)

    # Exclude KSA rows
    pre_filter_count = len(df)
    df = df[df["Entity ID"] != "HS_SA"].copy()
    print(f"✓ Removed {pre_filter_count - len(df)} KSA rows (Entity ID HS_SA)")

    # Drop rows with no valid country
    df = df.dropna(subset=["Entity ID", "Country"])
    if df.empty:
        print("❌ No usable rows after initial filtering")
        return pd.DataFrame()
    
    return df


def process_csv_and_generate_invoices(csv_path, billing_month=None, billing_year=None):
    """Process the source CSV, enforce business rules, and export per-country CSVs."""

    if billing_month is None:
        billing_month = datetime.now().strftime("%B")
    if billing_year is None:
        billing_year = datetime.now().year

    print(f"\n{'='*70}")
    print("POS BILLING DATA EXPORTER")
    print(f"{'='*70}")
    print(f"Billing Period : {billing_month} {billing_year}")
    print(f"Source CSV    : {csv_path}")
    print(f"Output Folder : {OUTPUT_DIR.resolve()}")
    print(f"{'='*70}\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = process_uploaded_csv(csv_path)
    if df.empty:
        return pd.DataFrame(columns=["Integrator", "Country", "Branches", "CSV"])

    allowed_integrators = list(INTEGRATOR_RULES.keys())
    df["IntegratorSlug"] = df["Integration Name"].apply(slugify)
    df = df[df["IntegratorSlug"].isin(allowed_integrators)]

    deduplicator = BranchDeduplicator(similarity_threshold=85)

    exports = []
    integrator_groups = df.groupby("Integration Name", sort=True)

    for integrator_name, integrator_df in integrator_groups:
        # Apply business rules and get the cleaned DataFrame
        cleaned_df = apply_business_rules(integrator_name, integrator_df, deduplicator)

        if cleaned_df.empty:
            continue

        # Generate per-country CSVs from the cleaned data
        for country_name, country_df in cleaned_df.groupby("Country", sort=True):
            if not country_name or country_df.empty:
                continue

            csv_output_path = generate_integrator_csv(
                integrator_name,
                country_name,
                country_df,
                OUTPUT_DIR,
                billing_month,
                billing_year,
            )

            print(
                f"    - {country_name}: {len(country_df)} branches -> {csv_output_path.relative_to(OUTPUT_DIR)}"
            )

            exports.append(
                {
                    "Integrator": integrator_name,
                    "Country": country_name,
                    "Branches": len(country_df),
                    "CSV": str(csv_output_path.relative_to(OUTPUT_DIR)),
                }
            )
        
        print()

    summary_df = pd.DataFrame(exports, columns=["Integrator", "Country", "Branches", "CSV"])

    if summary_df.empty:
        print("❗ No exports were generated. Check input data and rules.\n")
        return summary_df

    print(f"\n{'='*70}")
    print("EXPORT SUMMARY")
    print(f"{'='*70}")
    print(summary_df.to_string(index=False))
    print(f"{'='*70}\n")

    return summary_df


if __name__ == "__main__":
    # Default CSV file path
    default_csv = "POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv"
    
    # Check if CSV path provided as argument
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = default_csv
    
    # Check if file exists
    if not Path(csv_path).exists():
        print(f"❌ Error: CSV file not found: {csv_path}")
        print(f"\nUsage: python generate_invoices.py [csv_file_path]")
        sys.exit(1)
    
    # Optional: specify billing month and year
    billing_month = None  # Will default to current month
    billing_year = None   # Will default to current year
    
    # You can override these:
    # billing_month = "October"
    # billing_year = 2025
    
    # Generate invoices
    try:
        summary = process_csv_and_generate_invoices(csv_path, billing_month, billing_year)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
