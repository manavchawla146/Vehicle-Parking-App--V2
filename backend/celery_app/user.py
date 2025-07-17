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

        return jsonify({
            'message': 'Parking released and usage logged',
            'cost': cost,
            'exit_time': exit_time.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to release parking spot'}), 500
