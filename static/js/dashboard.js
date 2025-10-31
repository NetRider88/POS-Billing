// Dashboard JavaScript

function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function uploadCSV(input) {
    const file = input.files[0];
    if (!file) return;
    
    if (!file.name.endsWith('.csv')) {
        alert('Please select a CSV file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading();
    
    fetch('/upload-csv', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert(data.message + ' - Now click "Generate Invoices"', 'success');
        } else {
            showAlert('Error: ' + data.error, 'error');
        }
        // Reset file input
        input.value = '';
    })
    .catch(error => {
        hideLoading();
        showAlert('Error uploading CSV: ' + error, 'error');
        input.value = '';
    });
}

function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function generateInvoices() {
    const month = document.getElementById('billing-month')?.value || 'October';
    const year = document.getElementById('billing-year')?.value || '2025';
    
    if (!confirm(`Generate invoices for ${month} ${year}? This will process the CSV file and create PDFs for all integrators.`)) {
        return;
    }
    
    showLoading();
    
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            month: month,
            year: parseInt(year)
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showAlert('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('Error generating invoices: ' + error, 'error');
    });
}

function downloadAll() {
    window.location.href = '/download-all';
}

function previewInvoice(filename) {
    window.open(`/preview/${filename}`, '_blank');
}

function toggleSelectAll() {
    const selectAll = document.getElementById('select-all');
    const checkboxes = document.querySelectorAll('.invoice-checkbox');
    checkboxes.forEach(cb => cb.checked = selectAll.checked);
}

function getSelectedInvoices() {
    const checkboxes = document.querySelectorAll('.invoice-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function emailSelected() {
    const selected = getSelectedInvoices();
    
    if (selected.length === 0) {
        alert('Please select at least one invoice to email.');
        return;
    }
    
    const recipient = prompt('Enter recipient email address:');
    if (!recipient) return;
    
    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(recipient)) {
        alert('Please enter a valid email address.');
        return;
    }
    
    showLoading();
    
    fetch('/email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            recipient: recipient,
            filenames: selected
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert(data.message, 'success');
            // Uncheck all checkboxes
            document.querySelectorAll('.invoice-checkbox').forEach(cb => cb.checked = false);
            document.getElementById('select-all').checked = false;
        } else {
            showAlert('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('Error sending email: ' + error, 'error');
    });
}

function emailSingle(filename) {
    const recipient = prompt('Enter recipient email address:');
    if (!recipient) return;
    
    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(recipient)) {
        alert('Please enter a valid email address.');
        return;
    }
    
    showLoading();
    
    fetch('/email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            recipient: recipient,
            filenames: [filename]
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert(data.message, 'success');
        } else {
            showAlert('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('Error sending email: ' + error, 'error');
    });
}

// Auto-refresh stats every 30 seconds
setInterval(() => {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            console.log('Stats updated:', data);
        })
        .catch(error => console.error('Error fetching stats:', error));
}, 30000);
