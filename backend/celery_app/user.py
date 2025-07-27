from flask import Blueprint, jsonify, session, request
from .models import db, User, ParkingLot, ParkingSpot, Reservation, ParkingUsageLog
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api')

def get_current_time():
    """Get current time with proper timezone handling"""
    return datetime.now(timezone.utc).replace(tzinfo=None)

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'name': user.username,
        'email': user.email,
        'address': user.address,
        'pincode': user.pincode
    })

@user_bp.route('/profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    user.username = data.get('name', user.username)
    user.email = data.get('email', user.email)
    user.address = data.get('address', user.address)
    user.pincode = data.get('pincode', user.pincode)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

@user_bp.route('/parking/search', methods=['GET'])
def search_parking():
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401
    query = request.args.get('query', '').lower()
    lots = ParkingLot.query.all()
    filtered_lots = [
        lot for lot in lots
        if query in lot.address.lower() or query in lot.pin_code.lower()
    ]
    result = [
        {
            'id': lot.id,
            'primeLocation': lot.prime_location_name,
            'address': lot.address,
            'pinCode': lot.pin_code,
            'number_of_spots': lot.number_of_spots,
            'occupiedSpots': [spot.id for spot in lot.spots if spot.status == 'O'],
            'pricePerHour': lot.price,
            'availability': lot.number_of_spots - len([spot for spot in lot.spots if spot.status == 'O'])
        }
        for lot in filtered_lots
    ]
    logger.debug(f"Search results: {result}")
    return jsonify(result)

@user_bp.route('/parking/lot/<int:lot_id>/spots', methods=['GET'])
def get_lot_spots(lot_id):
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    logger.debug(f"Spots for lot {lot_id}: {[spot.id for spot in spots]}")
    logger.debug(f"Available spots for lot {lot_id}: {[spot.id for spot in spots if spot.status == 'A']}")
    return jsonify({
        'spots': [{
            'id': spot.id,
            'lot_name': lot.prime_location_name,
            'username': spot.username if spot.status == 'O' else None,
            'price': lot.price,
            'status': spot.status,
            'vehicle_id': spot.vehicle_id,
            'occupation_time': spot.occupation_time.isoformat() if spot.occupation_time else None
        } for spot in spots]
    })

@user_bp.route('/parking/reserve', methods=['POST'])
def reserve_parking():
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401
    data = request.json
    lot = ParkingLot.query.get(data.get('lotId'))
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    spot = ParkingSpot.query.get(data.get('spotId'))
    if not spot or spot.lot_id != lot.id or spot.status != 'A':
        logger.error(f"Invalid or unavailable spot: spot={spot}, lot_id={lot.id}, status={spot.status if spot else 'None'}")
        return jsonify({'error': 'Invalid or unavailable spot'}), 400

    # Use explicit time handling for correct timestamps
    current_time = get_current_time()
    
    spot.status = 'O'
    spot.vehicle_id = data.get('vehicleNo')
    spot.occupation_time = current_time
    spot.username = User.query.get(user_id).username
    reservation = Reservation(
        spot_id=spot.id,
        user_id=user_id,
        parking_timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    db.session.add(reservation)
    db.session.commit()
    logger.info(f"Successfully reserved spot {spot.id} in lot {lot.id} for user {user_id} at {current_time}")
    return jsonify({'message': 'Parking reserved successfully', 'reservationId': reservation.id, 'spotId': spot.id})

@user_bp.route('/user/parking-history', methods=['GET'])
def get_user_parking_history():
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401

    # 1. Active reservations (not yet released)
    active_reservations = Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).all()
    active_rows = []
    for res in active_reservations:
        spot = res.spot
        lot = spot.lot
        active_rows.append({
            'type': 'active',
            'id': spot.id,
            'location': lot.prime_location_name if hasattr(lot, 'prime_location_name') else lot.address,
            'vehicle_no': spot.vehicle_id,
            'timestamp': res.parking_timestamp.isoformat() if res.parking_timestamp else '',
            'slot_number': spot.slot_number,
        })

    # 2. Completed sessions from ParkingUsageLog
    usage_logs = ParkingUsageLog.query.filter_by(user_id=user_id).order_by(ParkingUsageLog.exit_time.desc()).all()
    parked_out_rows = []
    for log in usage_logs:
        spot = log.spot
        lot = log.lot
        parked_out_rows.append({
            'type': 'parked_out',
            'id': spot.id,
            'location': lot.prime_location_name if hasattr(lot, 'prime_location_name') else lot.address,
            'vehicle_no': log.vehicle_id,
            'timestamp': log.entry_time.isoformat() if log.entry_time else None,
            'releasing_time': log.exit_time.isoformat() if log.exit_time else None,
            'total_cost': log.cost,
            'slot_number': spot.slot_number,
        })

    # Combine and return
    return jsonify(active_rows + parked_out_rows)

@user_bp.route('/user/parking-status-summary', methods=['GET'])
def get_user_parking_status_summary():
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401

    # Count active reservations (not yet released)
    active_count = Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).count()
    # Count completed sessions (from ParkingUsageLog)
    completed_count = ParkingUsageLog.query.filter_by(user_id=user_id).count()

    return jsonify({
        'active': active_count,
        'completed': completed_count
    })

@user_bp.route('/parking/release', methods=['POST'])
def release_parking():
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401

    data = request.json
    spot_id = data.get('spotId')

    if not spot_id:
        return jsonify({'error': 'Missing spotId'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    spot = ParkingSpot.query.get(spot_id)
    if not spot:
        return jsonify({'error': 'Spot not found'}), 404

    if spot.status != 'O':
        return jsonify({'error': 'Spot is not occupied'}), 400

    if spot.username != user.username:
        return jsonify({'error': 'You can only release your own parking spot'}), 403

    try:
        lot = ParkingLot.query.get(spot.lot_id)
        exit_time = datetime.now(timezone.utc).replace(tzinfo=None)
        reservation = Reservation.query.filter_by(spot_id=spot_id, user_id=user_id).order_by(Reservation.id.desc()).first()
        entry_time = reservation.parking_timestamp
        duration_hours = max((exit_time - entry_time).total_seconds() / 3600, 1)  # Minimum 1 hour
        cost = duration_hours * lot.price

        # Log usage
        usage_log = ParkingUsageLog(
            user_id=user_id,
            spot_id=spot_id,
            lot_id=lot.id,
            vehicle_id=spot.vehicle_id,
            entry_time=entry_time,
            exit_time=exit_time,
            duration=duration_hours,
            cost=cost,
            remarks="Auto-logged on release"
        )
        db.session.add(usage_log)

        # Update reservation
        if reservation:
            reservation.leaving_timestamp = exit_time
            reservation.parking_cost = cost

        # Update spot
        spot.status = 'A'
        spot.vehicle_id = None
        spot.occupation_time = None
        spot.username = None

        db.session.commit()

        return jsonify({'message': 'Parking released and usage logged'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to release parking spot'}), 500

@user_bp.route('/user/notifications', methods=['GET'])
def get_user_notifications():
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401
    
    try:
        from datetime import datetime, timedelta
        
        # Get current time
        now = datetime.now()
        
        # Get all parking lots
        all_lots = ParkingLot.query.all()
        
        # Get user's recent parking history (last 30 days)
        thirty_days_ago = now - timedelta(days=30)
        recent_usage = ParkingUsageLog.query.filter(
            ParkingUsageLog.user_id == user_id,
            ParkingUsageLog.entry_time >= thirty_days_ago
        ).all()
        
        # Get all parking spots the user has ever used
        all_user_spots = ParkingUsageLog.query.filter_by(user_id=user_id).all()
        
        notifications = []
        
        # Check for unused lots recently
        used_lot_ids = set()
        for usage in recent_usage:
            spot = ParkingSpot.query.get(usage.spot_id)
            if spot:
                used_lot_ids.add(spot.lot_id)
        
        # Find lots the user hasn't used recently
        for lot in all_lots:
            if lot.id not in used_lot_ids:
                # Check if user has ever used this lot
                lot_ever_used = any(
                    ParkingSpot.query.get(usage.spot_id).lot_id == lot.id 
                    for usage in all_user_spots 
                    if ParkingSpot.query.get(usage.spot_id)
                )
                
                if lot_ever_used:
                    # User has used this lot before but not recently
                    last_usage = None
                    for usage in all_user_spots:
                        spot = ParkingSpot.query.get(usage.spot_id)
                        if spot and spot.lot_id == lot.id:
                            if not last_usage or usage.entry_time > last_usage.entry_time:
                                last_usage = usage.entry_time
                    
                    if last_usage:
                        days_since_last_use = (now - last_usage).days
                        if days_since_last_use > 7:  # More than a week
                            notifications.append({
                                'type': 'unused_lot',
                                'message': f"You haven't used parking lot '{lot.prime_location_name}' for {days_since_last_use} days. Consider trying it again!",
                                'timestamp': last_usage.strftime('%Y-%m-%d %H:%M:%S'),
                                'lot_id': lot.id,
                                'lot_name': lot.prime_location_name,
                                'days_since_use': days_since_last_use,
                                'read': False
                            })
        
        # Check for long parking sessions (more than 2 hours)
        active_reservations = Reservation.query.filter_by(
            user_id=user_id, 
            leaving_timestamp=None
        ).all()
        
        for reservation in active_reservations:
            if reservation.parking_timestamp:
                duration = now - reservation.parking_timestamp
                hours_parked = duration.total_seconds() / 3600
                
                if hours_parked > 2:
                    spot = ParkingSpot.query.get(reservation.spot_id)
                    lot_name = "Unknown Lot"
                    if spot:
                        lot = ParkingLot.query.get(spot.lot_id)
                        if lot:
                            lot_name = lot.prime_location_name
                    
                    notifications.append({
                        'type': 'long_session',
                        'message': f"Your parking session at '{lot_name}' has been active for {hours_parked:.1f} hours",
                        'timestamp': reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'hours_parked': hours_parked,
                        'read': False
                    })
        
        # Sort notifications by timestamp (newest first)
        notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'notifications': notifications,
            'unread_count': len([n for n in notifications if not n.get('read', False)])
        })
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return jsonify({'error': 'Failed to fetch notifications'}), 500

@user_bp.route('/user/generate-pdf-report', methods=['POST'])
def generate_pdf_report():
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401
    
    try:
        logger.info("Starting PDF report generation...")
        
        # Import the report function
        try:
            from jobs.reports import generate_monthly_report
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return jsonify({'error': f'Import error: {e}'}), 500
        
        import os
        
        # Generate the PDF report
        logger.info("Calling generate_monthly_report...")
        pdf_path = generate_monthly_report()
        logger.info(f"PDF path returned: {pdf_path}")
        
        if not pdf_path:
            logger.error("No PDF path returned from generate_monthly_report")
            return jsonify({'error': 'No PDF path returned from report generation'}), 500
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file does not exist at path: {pdf_path}")
            return jsonify({'error': f'PDF file not found at {pdf_path}'}), 500
        
        # Read the PDF file
        logger.info("Reading PDF file...")
        with open(pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        
        logger.info(f"PDF file size: {len(pdf_content)} bytes")
        
        # Clean up the temporary file
        try:
            os.unlink(pdf_path)
            logger.info("Temporary PDF file cleaned up")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temporary file: {cleanup_error}")
        
        # Return the PDF as a download
        from flask import send_file
        import io
        
        pdf_io = io.BytesIO(pdf_content)
        pdf_io.seek(0)
        
        logger.info("Sending PDF file to client...")
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'parking_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to generate PDF report: {str(e)}'}), 500
