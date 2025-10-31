# POS Billing Web Dashboard

A professional web interface for managing POS integration invoices with email capabilities.

## Features

✅ **Beautiful Web Interface**
- Modern, responsive design
- Real-time statistics dashboard
- Easy-to-use controls

✅ **Invoice Management**
- View all invoices in a table
- Preview invoices in browser
- Download individual invoices
- Download all invoices as ZIP

✅ **Email Integration**
- Email single or multiple invoices
- Bulk email selected invoices
- Configurable SMTP settings

✅ **Tax Configuration**
- View VAT rates by country
- See which countries are excluded
- Easy configuration guide

✅ **Automation**
- Generate invoices with one click
- Automatic tax calculation
- Real-time processing feedback

## Installation

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Configure email settings** (optional, for email functionality):
   
   Edit `dashboard.py` lines 20-25:
   ```python
   app.config['MAIL_SERVER'] = 'smtp.gmail.com'
   app.config['MAIL_PORT'] = 587
   app.config['MAIL_USE_TLS'] = True
   app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
   app.config['MAIL_PASSWORD'] = 'your-app-password'
   app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
   ```

   **For Gmail:**
   - Enable 2-factor authentication
   - Generate an App Password: https://myaccount.google.com/apppasswords
   - Use the app password (not your regular password)

## Usage

### Start the Dashboard

```bash
python3 dashboard.py
```

The dashboard will be available at: **http://localhost:5000**

### Access from Other Devices

The dashboard is accessible from other devices on your network:
- Find your computer's IP address
- Access from other devices: `http://YOUR_IP:5000`

### Main Features

#### 1. Generate Invoices
- Click "🔄 Generate New Invoices"
- System processes CSV and creates PDFs
- Invoices appear in the table automatically

#### 2. Download Invoices
- **Single:** Click ⬇️ icon next to invoice
- **All:** Click "📦 Download All (ZIP)" button
- ZIP file includes all invoices with timestamp

#### 3. Preview Invoices
- Click 👁️ icon to open PDF in browser
- View before downloading or emailing

#### 4. Email Invoices
- **Single:** Click ✉️ icon, enter recipient email
- **Multiple:** 
  1. Check boxes next to invoices
  2. Click "✉️ Email Selected"
  3. Enter recipient email

#### 5. View Tax Configuration
- Click "⚙️ Tax Configuration"
- See VAT rates for all countries
- View which entities are excluded

## Dashboard Structure

```
POS Billing/
├── dashboard.py                 ← Main Flask application
├── templates/
│   ├── index.html              ← Main dashboard page
│   └── tax_config.html         ← Tax configuration page
├── static/
│   ├── css/
│   │   └── style.css           ← Dashboard styling
│   └── js/
│       └── dashboard.js        ← Dashboard JavaScript
├── invoices/                    ← Generated PDF invoices
└── generate_invoices.py        ← Invoice generation logic
```

## API Endpoints

### GET `/`
Main dashboard page

### POST `/generate`
Generate new invoices
- Returns: JSON with success status and count

### GET `/download/<filename>`
Download single invoice

### GET `/download-all`
Download all invoices as ZIP

### GET `/preview/<filename>`
Preview invoice in browser

### POST `/email`
Email invoice(s)
- Body: `{"recipient": "email@example.com", "filenames": ["file1.pdf", "file2.pdf"]}`
- Returns: JSON with success status

### GET `/tax-config`
View tax configuration page

### GET `/api/stats`
Get dashboard statistics (JSON)

## Email Configuration

### Gmail Setup

1. **Enable 2-Factor Authentication:**
   - Go to Google Account settings
   - Security → 2-Step Verification

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Update dashboard.py:**
   ```python
   app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
   app.config['MAIL_PASSWORD'] = 'xxxx xxxx xxxx xxxx'  # App password
   ```

### Other Email Providers

**Outlook/Office 365:**
```python
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
```

**Custom SMTP:**
```python
app.config['MAIL_SERVER'] = 'your-smtp-server.com'
app.config['MAIL_PORT'] = 587  # or 465 for SSL
app.config['MAIL_USE_TLS'] = True  # or False for SSL
```

## Security Notes

⚠️ **Important:**
1. Change the `app.secret_key` in `dashboard.py` (line 18)
2. Never commit email passwords to version control
3. Use environment variables for sensitive data in production
4. The dashboard is for local/internal network use

## Troubleshooting

### Dashboard won't start
```bash
# Check if port 5000 is already in use
lsof -i :5000

# Use a different port
# Edit dashboard.py, last line:
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Email not sending
1. Check SMTP settings are correct
2. For Gmail, ensure App Password is used (not regular password)
3. Check firewall allows outbound SMTP connections
4. Look at terminal output for error messages

### Invoices not generating
1. Ensure CSV file exists: `POS Dashboard_Vendor Status Overview(CHECKIN)_Table.csv`
2. Check terminal output for errors
3. Verify Python dependencies are installed

### Can't access from other devices
1. Check firewall allows incoming connections on port 5000
2. Ensure `host='0.0.0.0'` in `dashboard.py`
3. Use your computer's actual IP address, not `localhost`

## Production Deployment

For production use, consider:

1. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 dashboard:app
   ```

2. **Use environment variables:**
   ```python
   import os
   app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
   app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
   ```

3. **Add authentication** (basic auth or OAuth)

4. **Use HTTPS** with SSL certificates

5. **Set up proper logging**

## Features Roadmap

Future enhancements:
- [ ] User authentication
- [ ] Invoice history tracking
- [ ] Automatic email scheduling
- [ ] Google Drive integration
- [ ] Multi-user support
- [ ] Invoice editing/regeneration
- [ ] Custom email templates
- [ ] Analytics dashboard

---

**Need Help?** Check the main README.md or contact support.
