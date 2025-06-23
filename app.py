from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'assets'
app.config['SIGNATURE_FOLDER'] = 'signatures'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Departments and models
DEPARTMENTS = ['HR', 'Engineering & IT', 'Finance', 'Medical Coding Services', 'Sales & Marketing', 'Medical Billing Services']
HEADSET_MODELS = [
    'Poly 3200 Series Blackwire C3220',
    'Practica SP-USB20',
    'Logitech',
    'Other'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_pdf(data, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Logo
    logo_path = "static/logo.jpg" # Adjust path if needed
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=2*inch, height=0.75*inch)
            story.append(logo)
        except Exception as e:
            print(f"Could not load logo: {e}")

    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Company Asset Receipt Form", styles['Title']))
    story.append(Spacer(1, 0.25 * inch))

    employee_info = [
        ["Name:", data['name']],
        ["Employee ID:", data['emp_id']],
        ["Department:", data['department']],
        ["Date:", data['timestamp']]
    ]
    emp_table = Table(employee_info, colWidths=[1.5*inch, 4*inch])
    story.append(emp_table)
    story.append(Spacer(1, 0.5 * inch))

    story.append(Paragraph("Assets Received:", styles['Heading2']))
    assets_details = []
    for asset in data['assets']:
        detail = f"• {asset}"
        if asset == 'Headset' and 'headset_type' in data:
            detail += f" ({data['headset_type']})"
        if asset == 'UPS' and 'ups_type' in data:
            detail += f" ({data['ups_type']})"
        if asset == 'Monitor' and 'monitor_type' in data:
            detail += f" ({data['monitor_type']})"
        assets_details.append(detail)
    story.append(Paragraph("<br/>".join(assets_details), styles['BodyText']))

    if data.get('monitor_sl_no'):
        story.append(Paragraph(f"Monitor S/N: {data['monitor_sl_no']}", styles['BodyText']))
    if data.get('ups_sl_no'):
        story.append(Paragraph(f"UPS S/N: {data['ups_sl_no']}", styles['BodyText']))

    if 'Headset' in data['assets'] and data['headset_model'] != 'N/A':
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph(f"Headset Model: {data['headset_model']}", styles['BodyText']))

    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Employee Signature:", styles['Heading2']))

    if 'signature_path' in data and data['signature_path']:
        try:
            signature_img = Image(data['signature_path'], width=3*inch, height=1*inch)
            story.append(signature_img)
        except Exception as e:
            print(f"Error loading signature image: {e}")
            story.append(Paragraph(data.get('signature_text', 'Signature uploaded'), styles['BodyText']))
    else:
        story.append(Paragraph(data.get('signature_text', 'Signature uploaded'), styles['BodyText']))

    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("I acknowledge receipt of the assets listed above.", styles['Italic']))
    doc.build(story)

@app.route('/', methods=['GET', 'POST'])
def asset_form():
    if request.method == 'POST':
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['SIGNATURE_FOLDER'], exist_ok=True)

        form_data = {
            'name': request.form['name'],
            'emp_id': request.form['emp_id'],
            'department': request.form['department'],
            'assets': request.form.getlist('assets'),
            'signature_text': request.form.get('signature_text', ''),
            'headset_model': request.form.get('headset_model', 'N/A'),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'headset_type': request.form.get('headset_type', ''),
            'ups_type': request.form.get('ups_type', ''),
            'monitor_type': request.form.get('monitor_type', ''),
            'monitor_sl_no': request.form.get('monitor_sl_no', ''),
            'ups_sl_no': request.form.get('ups_sl_no', '')
        }

        if 'signature' in request.files:
            file = request.files['signature']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"signature_{form_data['emp_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.split('.')[-1]}")
                signature_path = os.path.join(app.config['SIGNATURE_FOLDER'], filename)
                file.save(signature_path)
                form_data['signature_path'] = signature_path

        safe_name = re.sub(r'[^a-zA-Z0-9]+', '_', form_data['name'])
        filename = f"Asset_Receipt_{safe_name}_{form_data['emp_id']}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        generate_pdf(form_data, filepath)

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    return render_template('form.html', departments=DEPARTMENTS, headset_models=HEADSET_MODELS)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SIGNATURE_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
