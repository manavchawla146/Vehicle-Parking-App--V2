from flask import Blueprint, jsonify, session, request
from .models import db, User, ParkingLot, ParkingSpot, Reservation
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
        parking_timestamp=current_time
    )
    db.session.add(reservation)
    db.session.commit()
    logger.info(f"Successfully reserved spot {spot.id} in lot {lot.id} for user {user_id} at {current_time}")
    return jsonify({'message': 'Parking reserved successfully', 'reservationId': reservation.id, 'spotId': spot.id})
