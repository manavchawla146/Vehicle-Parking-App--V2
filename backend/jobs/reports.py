from celery_app.celery_worker import celery
from celery_app.models import db, ParkingUsageLog, User, ParkingSpot, ParkingLot
from datetime import datetime, timedelta
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import tempfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import app

logger = logging.getLogger(__name__)

def send_email_to_all_users(subject, message):
    """Send email to all users (excluding admin)"""
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "manavchawla146@gmail.com"
        sender_password = "nvwj xmrv tzry qbji"
        
        # Get all users (excluding admin)
        with app.app_context():
            users = User.query.filter(User.role != 'admin').all()
        
        if not users:
            logger.info("No users found to send notification")
            return
        
        # Send emails to all users
        success_count = 0
        failed_count = 0
        
        for user in users:
            if user.email:
                try:
                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = user.email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(message, 'plain'))
                    
                    # Create SMTP session
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    
                    # Send email
                    text = msg.as_string()
                    server.sendmail(sender_email, user.email, text)
                    server.quit()
                    
                    success_count += 1
                    logger.info(f"Notification sent to {user.email}")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send notification to {user.email}: {e}")
            else:
                logger.warning(f"No email address for user: {user.username}")
                failed_count += 1
        
        result = f"📧 Notifications sent: {success_count} successful, {failed_count} failed"
        logger.info(result)
        return result
        
    except Exception as e:
        logger.error(f"Error sending notifications: {e}")
        return f"Error: {e}"

@celery.task(name='jobs.reports.send_lot_addition_notification')
def send_lot_addition_notification(lot_data):
    """Send email notification to all users when a new parking lot is added"""
    try:
        logger.info("📧 Starting lot addition notification...")
        
        subject = "🚗 New Parking Lot Added - Parking App"
        message = f"""
Hello from Parking App!

Great news! A new parking lot has been added to our system.

📍 New Parking Lot Details:
• Location: {lot_data['primeLocation']}
• Address: {lot_data['address']}
• Pin Code: {lot_data['pinCode']}
• Price: ${lot_data['pricePerHour']}/hour
• Total Spots: {lot_data['maxSpots']}

🎯 What's New:
• More parking options available
• Better accessibility in your area
• Competitive pricing

🔍 Quick Actions:
• Search for this new location
• Book a spot right away
• Check availability

Thank you for using our parking service!

Best regards,
Parking App Team
        """
        
        result = send_email_to_all_users(subject, message)
        logger.info(f"📧 Lot addition notification completed: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Error in lot addition notification: {e}"
        logger.error(error_msg)
        return error_msg

@celery.task(name='jobs.reports.send_lot_deletion_notification')
def send_lot_deletion_notification(lot_data):
    """Send email notification to all users when a parking lot is deleted"""
    try:
        logger.info(" Starting lot deletion notification...")
        
        subject = "Parking Lot Removed - Parking App"
        message = f"""
Hello from Parking App!

Important Update: A parking lot has been removed from our system.

 Removed Parking Lot Details:
• Location: {lot_data['primeLocation']}
• Address: {lot_data['address']}
• Pin Code: {lot_data['pinCode']}

Important Information:
• This location is no longer available for parking
• Please use alternative parking locations
• Your existing bookings at this location may be affected

 Alternative Actions:
• Search for other nearby parking locations
• Check our updated parking lot list
• Contact support if you have questions

We apologize for any inconvenience this may cause.

Thank you for using our parking service!

Best regards,
Parking App Team
        """
        
        result = send_email_to_all_users(subject, message)
        logger.info(f"Lot deletion notification completed: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Error in lot deletion notification: {e}"
        logger.error(error_msg)
        return error_msg

@celery.task(name='jobs.reports.generate_monthly_report')
def generate_monthly_report(user_id=None):
    """Generate monthly parking usage report"""
    try:
        print("Starting monthly report generation...")
        
        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Check if it's user-specific or admin report
        if user_id and user_id != 'admin':
            title = Paragraph("Your Personal Parking Report", title_style)
        else:
            title = Paragraph("Parking Usage Report", title_style)
        
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report metadata
        current_time = datetime.now()
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        meta = Paragraph(f"Generated on: {current_time.strftime('%B %d, %Y at %I:%M %p')}", meta_style)
        story.append(meta)
        story.append(Spacer(1, 30))
        
        # Get parking usage data
        usage_data = get_parking_usage_data(user_id)
        
        # Summary Statistics
        if user_id and user_id != 'admin':
            story.append(Paragraph("Your Parking Summary", styles['Heading2']))
        else:
            story.append(Paragraph("Summary Statistics", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Parking Sessions', str(usage_data['total_sessions'])],
            ['Total Amount Spent', f"${usage_data['total_revenue']:.2f}"],
            ['Average Session Duration', f"{usage_data['avg_duration']:.1f} hours"],
            ['Most Used Location', usage_data['popular_location']]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Recent Parking Sessions
        if user_id and user_id != 'admin':
            story.append(Paragraph("Your Recent Parking Sessions", styles['Heading2']))
        else:
            story.append(Paragraph("Recent Parking Sessions", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if usage_data['recent_sessions']:
            if user_id and user_id != 'admin':
                session_headers = ['Location', 'Vehicle', 'Entry Time', 'Duration', 'Cost']
                session_data = [session_headers]
                for session_item in usage_data['recent_sessions']:
                    session_data.append([
                        session_item['location'],
                        session_item['vehicle_id'] or 'N/A',
                        session_item['entry_time'],
                        f"{session_item['duration']:.1f}h" if session_item['duration'] else 'N/A',
                        f"${session_item['cost']:.2f}" if session_item['cost'] else 'N/A'
                    ])
                session_table = Table(session_data, colWidths=[2*inch, 1.2*inch, 1.8*inch, 1*inch, 1*inch])
            else:
                session_headers = ['User', 'Location', 'Vehicle', 'Entry Time', 'Duration', 'Cost']
                session_data = [session_headers]
                for session_item in usage_data['recent_sessions']:
                    session_data.append([
                        session_item['username'],
                        session_item['location'],
                        session_item['vehicle_id'] or 'N/A',
                        session_item['entry_time'],
                        f"{session_item['duration']:.1f}h" if session_item['duration'] else 'N/A',
                        f"${session_item['cost']:.2f}" if session_item['cost'] else 'N/A'
                    ])
                session_table = Table(session_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1.5*inch, 0.8*inch, 0.8*inch])
            
            session_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(session_table)
        else:
            no_data = Paragraph("No recent parking sessions found.", styles['Normal'])
            story.append(no_data)
        
        story.append(Spacer(1, 30))
        
        # Location-wise Statistics
        if user_id and user_id != 'admin':
            story.append(Paragraph("Your Location-wise Statistics", styles['Heading2']))
        else:
            story.append(Paragraph("Location-wise Statistics", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if usage_data['location_stats']:
            location_headers = ['Location', 'Sessions', 'Total Hours', 'Total Cost']
            location_data = [location_headers]
            for location_item in usage_data['location_stats']:
                location_data.append([
                    location_item['location'],
                    str(location_item['sessions']),
                    f"{location_item['total_hours']:.1f}h",
                    f"${location_item['total_cost']:.2f}"
                ])
            location_table = Table(location_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
            location_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(location_table)
        else:
            no_data = Paragraph("No location statistics available.", styles['Normal'])
            story.append(no_data)
        
        # Build PDF
        doc.build(story)
        
        print(f"PDF report generated successfully: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def get_parking_usage_data(user_id=None):
    """Get parking usage data for report generation"""
    try:
        # Get current user from session or parameter
        if user_id and user_id != 'admin':
            usage_logs = ParkingUsageLog.query.filter_by(user_id=user_id).all()
        else:
            usage_logs = ParkingUsageLog.query.all()
        
        if not usage_logs:
            return {
                'total_sessions': 0,
                'total_revenue': 0.0,
                'avg_duration': 0.0,
                'popular_location': 'N/A',
                'recent_sessions': [],
                'location_stats': []
            }
        
        # Calculate statistics
        total_sessions = len(usage_logs)
        total_revenue = sum(log.cost or 0 for log in usage_logs)
        total_duration = sum(log.duration or 0 for log in usage_logs)
        avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
        
        # Find most popular location
        location_counts = {}
        for log in usage_logs:
            # Get location from ParkingLot through ParkingSpot
            spot = ParkingSpot.query.get(log.spot_id)
            if spot:
                lot = ParkingLot.query.get(spot.lot_id)
                location = lot.prime_location_name if lot else 'Unknown'
            else:
                location = 'Unknown'
            location_counts[location] = location_counts.get(location, 0) + 1
        popular_location = max(location_counts.items(), key=lambda x: x[1])[0] if location_counts else 'N/A'
        
        # Recent sessions (last 10)
        recent_sessions = []
        for log in sorted(usage_logs, key=lambda x: x.entry_time, reverse=True)[:10]:
            user = User.query.get(log.user_id) if log.user_id else None
            # Get location from ParkingLot through ParkingSpot
            spot = ParkingSpot.query.get(log.spot_id)
            if spot:
                lot = ParkingLot.query.get(spot.lot_id)
                location = lot.prime_location_name if lot else 'Unknown'
            else:
                location = 'Unknown'
            
            recent_sessions.append({
                'username': user.username if user else 'Unknown',
                'location': location,
                'vehicle_id': log.vehicle_id,
                'entry_time': log.entry_time.strftime('%Y-%m-%d %H:%M') if log.entry_time else 'N/A',
                'duration': log.duration,
                'cost': log.cost
            })
        
        # Location-wise statistics
        location_stats = {}
        for log in usage_logs:
            # Get location from ParkingLot through ParkingSpot
            spot = ParkingSpot.query.get(log.spot_id)
            if spot:
                lot = ParkingLot.query.get(spot.lot_id)
                location = lot.prime_location_name if lot else 'Unknown'
            else:
                location = 'Unknown'
            
            if location not in location_stats:
                location_stats[location] = {
                    'sessions': 0,
                    'total_hours': 0,
                    'total_cost': 0
                }
            location_stats[location]['sessions'] += 1
            location_stats[location]['total_hours'] += log.duration or 0
            location_stats[location]['total_cost'] += log.cost or 0
        
        location_stats_list = [
            {
                'location': loc,
                'sessions': stats['sessions'],
                'total_hours': stats['total_hours'],
                'total_cost': stats['total_cost']
            }
            for loc, stats in location_stats.items()
        ]
        
        return {
            'total_sessions': total_sessions,
            'total_revenue': total_revenue,
            'avg_duration': avg_duration,
            'popular_location': popular_location,
            'recent_sessions': recent_sessions,
            'location_stats': location_stats_list
        }
        
    except Exception as e:
        print(f"Error getting parking usage data: {e}")
        return {
            'total_sessions': 0,
            'total_revenue': 0.0,
            'avg_duration': 0.0,
            'popular_location': 'N/A',
            'recent_sessions': [],
            'location_stats': []
        }
