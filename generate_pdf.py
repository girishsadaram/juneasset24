from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_pdf(data, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    story.append(Paragraph("Asset Receipt Form", styles['Title']))
    story.append(Spacer(1, 0.25 * inch))
    
    # Employee Info
    employee_info = [
        ["Name:", data['name']],
        ["Employee ID:", data['emp_id']],
        ["Department:", data['department']],
        ["Date:", data['timestamp']]
    ]
    
    emp_table = Table(employee_info, colWidths=[1.5*inch, 4*inch])
    emp_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 0.5 * inch))
    
    # Assets Received
    story.append(Paragraph("Assets Received:", styles['Heading2']))
    assets_list = [f"• {asset}" for asset in data['assets']]
    story.append(Paragraph("<br/>".join(assets_list), styles['BodyText']))
    
    # Headset model if applicable
    if 'Headset' in data['assets'] and data['headset_model'] != 'N/A':
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph(f"Headset Model: {data['headset_model']}", styles['BodyText']))
    
    # Signature
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Employee Signature:", styles['Heading2']))
    story.append(Paragraph(data['signature'], styles['BodyText']))
    
    # Acknowledgement
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("I acknowledge receipt of the assets listed above.", styles['Italic']))
    
    doc.build(story)