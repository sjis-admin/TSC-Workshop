"""
Utility functions for the workshop registration system
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import qrcode
from io import BytesIO
from datetime import datetime
import os


def send_confirmation_email(registration):
    """
    Send confirmation email to registered student
    
    Args:
        registration: Registration object
    """
    
    subject = f"Workshop Registration Confirmed - {registration.workshop.name}"
    
    # Prepare email context
    context = {
        'registration': registration,
        'workshop': registration.workshop,
        'student_name': registration.student_name,
    }
    
    # Render email template (we'll use simple text for now)
    message = f"""
Dear {registration.student_name},

Your registration for the workshop "{registration.workshop.name}" has been confirmed!

Registration Details:
- Registration Number: {registration.registration_number}
- Workshop: {registration.workshop.name}
- Date: {registration.workshop.workshop_date}
- Time: {registration.workshop.time}
- Venue: {registration.workshop.venue}
- Fee: {'FREE' if registration.workshop.is_free else f'৳{registration.workshop.fee}'}

Student Information:
- Name: {registration.student_name}
- Grade: {registration.grade}
- School: {registration.school.name if registration.school else registration.school_name}
- Contact: {registration.contact_number}
- Email: {registration.email}

Please save your registration number for future reference.

For any queries, please contact us at info@titanium.sjis.edu.bd

Best regards,
Titanium Science Club
St. Joseph International School
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_payment_confirmation_email(registration, payment):
    """
    Send payment confirmation email
    
    Args:
        registration: Registration object
        payment: Payment object
    """
    
    subject = f"Payment Confirmed - {registration.workshop.name}"
    
    message = f"""
Dear {registration.student_name},

Your payment for the workshop "{registration.workshop.name}" has been successfully processed!

Payment Details:
- Transaction ID: {payment.transaction_id}
- Amount: ৳{payment.amount}
- Status: Completed
- Date: {payment.completed_at.strftime('%Y-%m-%d %H:%M:%S') if payment.completed_at else 'N/A'}

Registration Details:
- Registration Number: {registration.registration_number}
- Workshop: {registration.workshop.name}
- Date: {registration.workshop.workshop_date}
- Time: {registration.workshop.time}
- Venue: {registration.workshop.venue}

You can download your receipt from the website using your registration number.

Best regards,
Titanium Science Club
St. Joseph International School
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def generate_receipt_pdf(registration):
    """
    Generate PDF receipt for registration
    
    Args:
        registration: Registration object
        
    Returns:
        BytesIO: PDF file buffer
    """
    
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.4*inch, bottomMargin=0.4*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    # Header
    story.append(Paragraph("St. Joseph International School", title_style))
    story.append(Paragraph("Titanium Science Club", heading_style))
    story.append(Paragraph("Workshop Registration Receipt", heading_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Registration Number (prominent)
    reg_num_style = ParagraphStyle(
        'RegNum',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#d32f2f'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(f"Registration No: {registration.registration_number}", reg_num_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Workshop Details
    story.append(Paragraph("Workshop Details", heading_style))
    
    workshop_data = [
        ['Workshop Name:', registration.workshop.name],
        ['Date:', registration.workshop.workshop_date],
        ['Time:', registration.workshop.time],
        ['Duration:', registration.workshop.duration],
        ['Venue:', registration.workshop.venue],
        ['Organizer:', registration.workshop.organizer if registration.workshop.organizer else 'Titanium Science Club'],
    ]
    
    workshop_table = Table(workshop_data, colWidths=[2*inch, 4.5*inch])
    workshop_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(workshop_table)
    story.append(Spacer(1, 0.1*inch))
    
    # Student Information
    story.append(Paragraph("Student Information", heading_style))
    
    student_data = [
        ['Student Name:', registration.student_name],
        ['Grade:', str(registration.grade)],
        ['School:', registration.school.name if registration.school else registration.school_name],
        ['Contact Number:', registration.contact_number],
        ['Email:', registration.email],
    ]
    
    student_table = Table(student_data, colWidths=[2*inch, 4.5*inch])
    student_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(student_table)
    story.append(Spacer(1, 0.1*inch))
    
    # Payment Information
    story.append(Paragraph("Payment Information", heading_style))
    
    if registration.workshop.is_free:
        payment_status = "FREE WORKSHOP"
        amount = "৳0.00"
    else:
        payment_status = registration.get_payment_status_display()
        amount = f"৳{registration.workshop.fee}"
    
    payment_data = [
        ['Workshop Fee:', amount],
        ['Payment Status:', payment_status],
        ['Registration Date:', registration.registered_at.strftime('%Y-%m-%d %H:%M:%S')],
    ]
    
    # If there's a payment record, add transaction details
    if hasattr(registration, 'payment'):
        payment_data.append(['Transaction ID:', registration.payment.transaction_id])
        if registration.payment.completed_at:
            payment_data.append(['Payment Date:', registration.payment.completed_at.strftime('%Y-%m-%d %H:%M:%S')])
    
    payment_table = Table(payment_data, colWidths=[2*inch, 4.5*inch])
    payment_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(payment_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Generate QR Code for registration number
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(f"REG:{registration.registration_number}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to buffer
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Add QR code to PDF
    qr_image = Image(qr_buffer, width=1.2*inch, height=1.2*inch)
    qr_table = Table([[qr_image]], colWidths=[6.5*inch])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(qr_table)
    
    # Footer
    story.append(Spacer(1, 0.1*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("This is a computer-generated receipt and does not require a signature.", footer_style))
    story.append(Paragraph("St. Joseph International School | Titanium Science Club", footer_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer


def get_receipt_filename(registration):
    """
    Generate filename for receipt PDF
    
    Args:
        registration: Registration object
        
    Returns:
        str: Filename
    """
    return f"receipt_{registration.registration_number}.pdf"
