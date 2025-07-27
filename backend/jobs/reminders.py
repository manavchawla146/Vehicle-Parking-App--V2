# backend/jobs/reminders.py

from celery_app import celery
from celery_app.models import db, User, ParkingSpot, ParkingLot
from datetime import datetime
from celery.utils.log import get_task_logger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from app import app  # Import Flask app
import tempfile
import os

# Set up logger
logger = get_task_logger(__name__)

def send_email_with_pdf(to_email, subject, message, pdf_path=None):
    """Send email with optional PDF attachment"""
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "manavchawla146@gmail.com"
        sender_password = "nvwj xmrv tzry qbji"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(message, 'plain'))
        
        # Attach PDF if provided
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename=parking_report_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
            msg.attach(part)
            logger.info(f"📎 PDF attached to email for {to_email}")
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        logger.info(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}")
        return False

def generate_user_pdf_report(user_id):
    """Generate PDF report for a specific user"""
    try:
        from jobs.reports import generate_monthly_report
        
        # Generate PDF with user_id parameter
        pdf_path = generate_monthly_report(user_id)
        
        if pdf_path and os.path.exists(pdf_path):
            logger.info(f"📄 PDF generated for user {user_id}: {pdf_path}")
            return pdf_path
        else:
            logger.error(f"❌ Failed to generate PDF for user {user_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error generating PDF for user {user_id}: {e}")
        return None

@celery.task(name='jobs.reminders.send_reminder')
def send_reminder():
    """Send reminder emails with PDF reports to all users"""
    try:
        logger.info("📧 Starting to send reminder emails with PDF reports to all users...")
        
        # Use Flask application context
        with app.app_context():
            # Get all users (excluding admin)
            users = User.query.filter(User.role != 'admin').all()
            
            if not users:
                logger.info("No users found to send reminders to")
                return "No users found"
            
            # Get current time for the email
            current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            
            # Email content
            subject = "🚗 Parking App - Daily Report & Reminder"
            message = f"""
Hello from Parking App!

This is your daily reminder along with your personalized parking report.

📅 Report generated on: {current_time}

📊 Your Report Includes:
• Summary of your parking sessions
• Total amount spent
• Recent parking history
• Location-wise statistics

🔍 Quick Actions:
• Check your current parking sessions
• View your parking history
• Book a new parking spot

Thank you for using our parking service!

Best regards,
Parking App Team
            """
            
            # Send emails to all users
            success_count = 0
            failed_count = 0
            
            for user in users:
                if user.email:
                    # Generate PDF for this user
                    pdf_path = generate_user_pdf_report(user.id)
                    
                    # Send email with PDF attachment
                    if send_email_with_pdf(user.email, subject, message, pdf_path):
                        success_count += 1
                        logger.info(f"✅ Email with PDF sent to {user.email}")
                    else:
                        failed_count += 1
                        logger.error(f"❌ Failed to send email to {user.email}")
                    
                    # Clean up PDF file
                    if pdf_path and os.path.exists(pdf_path):
                        try:
                            os.unlink(pdf_path)
                            logger.info(f"🗑️ Cleaned up PDF file: {pdf_path}")
                        except Exception as cleanup_error:
                            logger.warning(f"⚠️ Failed to cleanup PDF file: {cleanup_error}")
                else:
                    logger.warning(f"No email address for user: {user.username}")
                    failed_count += 1
            
            result = f"📧 Email reminder with PDF sent: {success_count} successful, {failed_count} failed"
            logger.info(result)
            return result
        
    except Exception as e:
        error_msg = f"❌ Error in send_reminder task: {e}"
        logger.error(error_msg)
        return error_msg
