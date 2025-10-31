
import os
from flask import Flask, request, redirect, url_for, render_template, flash, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime

from generate_invoices import process_csv_and_generate_invoices

OUTPUT_DIR = os.path.abspath("exports")

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            billing_month = request.form.get('billing_month', datetime.now().strftime("%B"))
            billing_year = request.form.get('billing_year', datetime.now().year)
            
            try:
                summary_df = process_csv_and_generate_invoices(filepath, billing_month, billing_year)
                flash('File processed successfully!')
                return render_template('results.html', summary=summary_df)
            except Exception as e:
                flash(f'An error occurred: {e}')
                return redirect(request.url)

    return render_template('upload.html')

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print("Starting Flask application...")
    app.run(debug=True, port=5001)
