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

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/NetRider88/POS-Billing.git
    cd POS-Billing
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the web application:

1.  Start the Flask development server:
    ```bash
    python app.py
    ```

2.  Open your web browser and navigate to `http://127.0.0.1:5001/`.

3.  On the web interface, upload your CSV file, specify the billing month and year (optional), and click "Upload and Process".

4.  After processing, a summary table will be displayed with links to download the generated CSV files per integrator and country.

## How It Works

### 1. Data Upload and Processing
- Users upload a CSV file through the web interface.
- The application reads the uploaded CSV, validates its columns, and performs initial filtering (e.g., removing KSA rows).

### 2. Integrator-Specific Exclusions
- The system applies specific exclusion rules for integrators like Urban Piper [UAE], Limetray [UAE], and Grubtech [all markets]. These rules include:
    - **Urban Piper [UAE]:** Excludes "Edo Sushi and Poke", "Else Burger", and all "Snap" branches.
    - **Limetray [UAE]:** Excludes all "Snap" branches, "Toss & Co.", "World of Asia", "Biryani Boy", "Tim Hortons", "Chef Lanka", "Steers", "Debonairs Pizza , Dibba", "Tim Hortons home select", and "The Kebab Shop".
    - **Grubtech [all markets]:** Excludes all "Snap" branches and handles "TGO vs TMP duplicates" (assumed to be own delivery vs restaurant delivery, counting as one branch).

### 3. Deduplication
The system uses **fuzzy matching** (85% similarity threshold) to identify duplicate branches based on vendor code and similar branch names. For Grubtech, delivery type is ignored during deduplication to correctly count branches with both OWN_DELIVERY and VENDOR_DELIVERY as one.

### 4. Output Generation
- For each processed integrator and country combination, a separate CSV file is generated.
- These CSV files contain the filtered and deduplicated branch data.
- The generated files are available for download directly from the web interface.

## File Structure

```
POS Billing/
├── app.py                                                    # Flask web application
├── generate_invoices.py                                      # Core logic for processing and exclusions
├── requirements.txt                                          # Python dependencies
├── README.md                                                 # This file
├── templates/                                                # HTML templates for the web interface
│   ├── base.html
│   ├── upload.html
│   └── results.html
├── uploads/                                                  # Directory for uploaded CSV files
├── exports/                                                  # Directory for generated CSV files
│   └── 2025_september/                                       # Example output structure
│       ├── integrator_name_1/
│       │   └── integrator_name_1_country_1_2025_september.csv
│       └── integrator_name_2/
│           └── integrator_name_2_country_2_2025_september.csv
```

## Troubleshooting

### Application not starting or port conflict
- Ensure no other application is using port `5001`.
- Check the console output for any error messages when running `python app.py`.

### Missing dependencies
```bash
pip install -r requirements.txt
```

### Integrators not showing or incorrect exclusions
- Verify the "Integration Name" column in your uploaded CSV matches one of the expected variations (e.g., "Urban Piper [UAE]", "Limetray [UAE]", "HS GrubTech").
- Review the `generate_invoices.py` file for the `INTEGRATOR_RULES` dictionary and exclusion logic.

### Download links not working (404 error)
- Ensure the `exports` directory exists in the project root.
- Check the Flask application console for any errors related to file serving.
