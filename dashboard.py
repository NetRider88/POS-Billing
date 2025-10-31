#!/usr/bin/env python3
"""
POS Billing Dashboard - Web Interface
A simple Flask web application for managing invoices
"""

from flask import Flask, render_template, send_file, request, jsonify, redirect, url_for, flash
from flask_mail import Mail, Message
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import zipfile
import io
from generate_invoices import process_csv_and_generate_invoices, InvoiceGenerator

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Email configuration (update with your SMTP settings)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Update this
app.config['MAIL_PASSWORD'] = 'your-app-password'  # Update this
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'  # Update this

mail = Mail(app)

# Paths
BASE_DIR = Path(__file__).parent
INVOICES_DIR = BASE_DIR / 'invoices'
CSV_FILE = BASE_DIR / 'POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv'


@app.route('/')
def index():
    """Main dashboard page"""
    # Check if invoices exist
    if not INVOICES_DIR.exists() or not list(INVOICES_DIR.glob('*.pdf')):
        return render_template('index.html', invoices=[], has_invoices=False)
    
    # Get all invoice files
    invoices = []
    for pdf_file in sorted(INVOICES_DIR.glob('*.pdf')):
        stat = pdf_file.stat()
        invoices.append({
            'name': pdf_file.stem,
            'filename': pdf_file.name,
            'size': f"{stat.st_size / 1024:.1f} KB",
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            'path': str(pdf_file)
        })
    
    # Calculate summary
    summary = {
        'total_invoices': len(invoices),
        'total_size': sum(Path(inv['path']).stat().st_size for inv in invoices) / (1024 * 1024),
        'last_generated': max((Path(inv['path']).stat().st_mtime for inv in invoices), default=0)
    }
    
    if summary['last_generated']:
        summary['last_generated'] = datetime.fromtimestamp(summary['last_generated']).strftime('%Y-%m-%d %H:%M')
    else:
        summary['last_generated'] = 'Never'
    
    return render_template('index.html', invoices=invoices, summary=summary, has_invoices=True)


@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    """Upload a new CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be a CSV'}), 400
        
        # Save the uploaded file
        file.save(CSV_FILE)
        
        return jsonify({
            'success': True,
            'message': f'CSV file uploaded successfully: {file.filename}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/generate', methods=['POST'])
def generate_invoices():
    """Generate new invoices"""
    try:
        if not CSV_FILE.exists():
            return jsonify({'success': False, 'error': 'CSV file not found. Please upload a CSV first.'}), 400
        
        # Get billing period from request or use current month
        data = request.get_json() or {}
        billing_month = data.get('month', datetime.now().strftime("%B"))
        billing_year = data.get('year', datetime.now().year)
        
        summary_df = process_csv_and_generate_invoices(str(CSV_FILE), billing_month, billing_year)
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(summary_df)} invoices for {billing_month} {billing_year}',
            'count': len(summary_df)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download/<filename>')
def download_invoice(filename):
    """Download a single invoice"""
    file_path = INVOICES_DIR / filename
    if not file_path.exists():
        flash('Invoice not found', 'error')
        return redirect(url_for('index'))
    
    return send_file(file_path, as_attachment=True)


@app.route('/download-all')
def download_all():
    """Download all invoices as a ZIP file"""
    if not INVOICES_DIR.exists():
        flash('No invoices found', 'error')
        return redirect(url_for('index'))
    
    # Create ZIP file in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for pdf_file in INVOICES_DIR.glob('*.pdf'):
            zf.write(pdf_file, pdf_file.name)
    
    memory_file.seek(0)
    
    # Generate filename with current date
    zip_filename = f"invoices_{datetime.now().strftime('%Y%m%d')}.zip"
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )


@app.route('/preview/<filename>')
def preview_invoice(filename):
    """Preview invoice in browser"""
    file_path = INVOICES_DIR / filename
    if not file_path.exists():
        return "Invoice not found", 404
    
    return send_file(file_path, mimetype='application/pdf')


@app.route('/email', methods=['POST'])
def email_invoice():
    """Email invoice(s) to recipient"""
    try:
        data = request.json
        recipient = data.get('recipient')
        filenames = data.get('filenames', [])
        
        if not recipient:
            return jsonify({'success': False, 'error': 'Recipient email required'}), 400
        
        if not filenames:
            return jsonify({'success': False, 'error': 'No invoices selected'}), 400
        
        # Create email
        msg = Message(
            subject=f"POS Integration Invoices - {datetime.now().strftime('%B %Y')}",
            recipients=[recipient],
            body=f"""
Hello,

Please find attached the POS integration invoices for {datetime.now().strftime('%B %Y')}.

Total invoices: {len(filenames)}

Best regards,
POS Billing Team
            """
        )
        
        # Attach invoices
        for filename in filenames:
            file_path = INVOICES_DIR / filename
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    msg.attach(filename, 'application/pdf', f.read())
        
        mail.send(msg)
        
        return jsonify({
            'success': True,
            'message': f'Sent {len(filenames)} invoice(s) to {recipient}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/tax-config')
def tax_config():
    """Show tax configuration"""
    tax_rates = InvoiceGenerator.TAX_RATES
    return render_template('tax_config.html', tax_rates=tax_rates)


@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    if not INVOICES_DIR.exists():
        return jsonify({'total_invoices': 0, 'total_size': 0})
    
    invoices = list(INVOICES_DIR.glob('*.pdf'))
    total_size = sum(f.stat().st_size for f in invoices)
    
    return jsonify({
        'total_invoices': len(invoices),
        'total_size': f"{total_size / (1024 * 1024):.2f} MB"
    })


if __name__ == '__main__':
    # Create invoices directory if it doesn't exist
    INVOICES_DIR.mkdir(exist_ok=True)
    
    print("\n" + "="*60)
    print("POS BILLING DASHBOARD")
    print("="*60)
    print(f"Dashboard URL: http://localhost:5001")
    print(f"Invoices folder: {INVOICES_DIR}")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
