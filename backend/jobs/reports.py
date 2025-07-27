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

logger = logging.getLogger(__name__)

@celery.task(name='jobs.reports.generate_monthly_report')
def generate_monthly_report():
    """Generate monthly parking usage report"""
    try:
        print("📊 Starting monthly report generation...")
        
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
        from flask import session
        current_user_id = session.get('user_id')
        if current_user_id and current_user_id != 'admin':
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
        usage_data = get_parking_usage_data()
        
        # Summary Statistics
        if current_user_id and current_user_id != 'admin':
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
        if current_user_id and current_user_id != 'admin':
            story.append(Paragraph("Your Recent Parking Sessions", styles['Heading2']))
        else:
            story.append(Paragraph("Recent Parking Sessions", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if usage_data['recent_sessions']:
            if current_user_id and current_user_id != 'admin':
                session_headers = ['Location', 'Vehicle', 'Entry Time', 'Duration', 'Cost']
                session_data = [session_headers]
                
                for session in usage_data['recent_sessions']:
                    session_data.append([
                        session['location'],
                        session['vehicle_id'] or 'N/A',
                        session['entry_time'],
                        f"{session['duration']:.1f}h" if session['duration'] else 'N/A',
                        f"${session['cost']:.2f}" if session['cost'] else 'N/A'
                    ])
                
                session_table = Table(session_data, colWidths=[2*inch, 1.2*inch, 1.8*inch, 1*inch, 1*inch])
            else:
                session_headers = ['User', 'Location', 'Vehicle', 'Entry Time', 'Duration', 'Cost']
                session_data = [session_headers]
                
                for session in usage_data['recent_sessions']:
                    session_data.append([
                        session['username'],
                        session['location'],
                        session['vehicle_id'] or 'N/A',
                        session['entry_time'],
                        f"{session['duration']:.1f}h" if session['duration'] else 'N/A',
                        f"${session['cost']:.2f}" if session['cost'] else 'N/A'
                    ])
                
                session_table = Table(session_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1.5*inch, 0.8*inch, 0.8*inch])
            session_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(session_table)
        else:
            story.append(Paragraph("No recent parking sessions found.", styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Location-wise Statistics
        story.append(Paragraph("Location-wise Statistics", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if usage_data['location_stats']:
            location_headers = ['Location', 'Total Sessions', 'Total Revenue', 'Avg Duration']
            location_data = [location_headers]
            
            for location in usage_data['location_stats']:
                location_data.append([
                    location['name'],
                    str(location['sessions']),
                    f"${location['revenue']:.2f}",
                    f"{location['avg_duration']:.1f}h"
                ])
            
            location_table = Table(location_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            location_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            story.append(location_table)
        else:
            story.append(Paragraph("No location statistics available.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        print(f"📊 PDF report generated successfully: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        print(f"❌ Error generating report: {e}")
        return None

def get_parking_usage_data():
    """Get parking usage data for the report"""
    try:
        from flask import session
        
        # Get current user from session
        current_user_id = session.get('user_id')
        
        # Get parking usage logs - filter by current user if logged in
        if current_user_id and current_user_id != 'admin':
            usage_logs = ParkingUsageLog.query.filter_by(user_id=current_user_id).all()
            print(f"Filtering data for user: {current_user_id}")
        else:
            usage_logs = ParkingUsageLog.query.all()
            print("Showing all users data (admin or not logged in)")
        
        if not usage_logs:
            return {
                'total_sessions': 0,
                'total_revenue': 0,
                'avg_duration': 0,
                'popular_location': 'N/A',
                'busiest_day': 'N/A',
                'recent_sessions': [],
                'location_stats': []
            }
        
        # Calculate total sessions and revenue
        total_sessions = len(usage_logs)
        total_revenue = sum(log.cost or 0 for log in usage_logs)
        avg_duration = sum(log.duration or 0 for log in usage_logs) / total_sessions if total_sessions > 0 else 0
        
        # Get recent sessions (last 10)
        recent_sessions = []
        for log in sorted(usage_logs, key=lambda x: x.entry_time, reverse=True)[:10]:
            user = User.query.get(log.user_id)
            spot = ParkingSpot.query.get(log.spot_id)
            lot = ParkingLot.query.get(spot.lot_id) if spot else None
            
            recent_sessions.append({
                'username': user.username if user else 'Unknown',
                'location': lot.prime_location_name if lot else 'Unknown',
                'vehicle_id': log.vehicle_id,
                'entry_time': log.entry_time.strftime('%Y-%m-%d %H:%M'),
                'duration': log.duration,
                'cost': log.cost
            })
        
        # Get location statistics
        location_stats = {}
        for log in usage_logs:
            spot = ParkingSpot.query.get(log.spot_id)
            lot = ParkingLot.query.get(spot.lot_id) if spot else None
            if lot:
                location_name = lot.prime_location_name
                if location_name not in location_stats:
                    location_stats[location_name] = {
                        'sessions': 0,
                        'revenue': 0,
                        'durations': []
                    }
                location_stats[location_name]['sessions'] += 1
                location_stats[location_name]['revenue'] += log.cost or 0
                if log.duration:
                    location_stats[location_name]['durations'].append(log.duration)
        
        # Convert location stats to list format
        location_stats_list = []
        for name, stats in location_stats.items():
            avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
            location_stats_list.append({
                'name': name,
                'sessions': stats['sessions'],
                'revenue': stats['revenue'],
                'avg_duration': avg_duration
            })
        
        # Sort by revenue
        location_stats_list.sort(key=lambda x: x['revenue'], reverse=True)
        
        # Find popular location and busiest day
        popular_location = location_stats_list[0]['name'] if location_stats_list else 'N/A'
        
        # Simple busiest day calculation (you can enhance this)
        busiest_day = 'Monday'  # Placeholder
        
        return {
            'total_sessions': total_sessions,
            'total_revenue': total_revenue,
            'avg_duration': avg_duration,
            'popular_location': popular_location,
            'busiest_day': busiest_day,
            'recent_sessions': recent_sessions,
            'location_stats': location_stats_list
        }
        
    except Exception as e:
        logger.error(f"Error getting parking usage data: {e}")
        return {
            'total_sessions': 0,
            'total_revenue': 0,
            'avg_duration': 0,
            'popular_location': 'N/A',
            'busiest_day': 'N/A',
            'recent_sessions': [],
            'location_stats': []
        }
