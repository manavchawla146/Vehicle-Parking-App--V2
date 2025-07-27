# backend/jobs/reminders.py

from celery_app import celery
from celery_app.models import db, User, ParkingSpot, ParkingLot
from datetime import datetime
from celery.utils.log import get_task_logger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import app  # Import Flask app

# Set up logger
logger = get_task_logger(__name__)

def send_email(to_email, subject, message):
    """Send email using SMTP"""
    try:
        # Email configuration - you'll need to update these with your email settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "manavchawla146@gmail.com"  # Update with your email
        sender_password = "nvwj xmrv tzry qbji"   # Update with your app password
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(message, 'plain'))
        
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

@celery.task(name='jobs.reminders.send_reminder')
def send_reminder():
    """Send reminder emails to all users"""
    try:
        logger.info("📧 Starting to send reminder emails to all users...")
        
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
            subject = "🚗 Parking App - Daily Reminder"
            message = f"""
Hello from Parking App!

This is your daily reminder to check your parking status.

📅 Reminder sent on: {current_time}

🔍 Quick Actions:
• Check your current parking sessions
• View your parking history
• Book a new parking spot
• Download your parking report

Thank you for using our parking service!

Best regards,
Parking App Team
            """
            
            # Send emails to all users
            success_count = 0
            failed_count = 0
            
            for user in users:
                if user.email:
                    if send_email(user.email, subject, message):
                        success_count += 1
                    else:
                        failed_count += 1
                else:
                    logger.warning(f"No email address for user: {user.username}")
                    failed_count += 1
            
            result = f"📧 Email reminder sent: {success_count} successful, {failed_count} failed"
            logger.info(result)
            return result
        
    except Exception as e:
        error_msg = f"❌ Error in send_reminder task: {e}"
        logger.error(error_msg)
        return error_msg
