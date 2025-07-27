from flask import Blueprint, request, jsonify, session
from .models import db, ParkingLot, User, ParkingSpot, LotChangeLog
from datetime import datetime, timezone
import logging
from sqlalchemy import func

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def get_current_time():
    """Get current time with proper timezone handling"""
    return datetime.now(timezone.utc)

@admin_bp.route('/lots', methods=['POST'])
def add_lot():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    try:
        lot = ParkingLot(
            prime_location_name=data['primeLocation'],
            price=data['pricePerHour'],
            address=data['address'],
            pin_code=data['pinCode'],
            number_of_spots=data['maxSpots'],
            created_at=get_current_time()
        )
        db.session.add(lot)
        db.session.commit()  # Commit to get the lot.id
        
        # Initialize ParkingSpot records for the new lot
        for i in range(1, data['maxSpots'] + 1):
            spot = ParkingSpot(lot_id=lot.id, slot_number=i, status='A')
            db.session.add(spot)
        
        db.session.commit()
        logger.info(f"Successfully added lot {lot.id} with {data['maxSpots']} spots")
        return jsonify({'message': 'Lot added successfully', 'id': lot.id}), 201
    except KeyError as e:
        logger.error(f"Missing required field: {e}")
        return jsonify({'error': f'Missing required field: {e}'}), 400
    except ValueError as e:
        logger.error(f"Invalid data: {e}")
        return jsonify({'error': f'Invalid data: {e}'}), 400
    except Exception as e:
        logger.error(f"Error adding lot: {e}")
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {e}'}), 500

@admin_bp.route('/lots', methods=['GET'])
def get_lots():
    lots = ParkingLot.query.all()
    result = []
    for lot in lots:
        occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
        total = ParkingSpot.query.filter_by(lot_id=lot.id).count()
        result.append({
            'id': lot.id,
            'primeLocation': lot.prime_location_name,
            'address': lot.address,
            'pinCode': lot.pin_code,
            'pricePerHour': lot.price,
            'total': total,
            'available': total - occupied,
            'occupied': occupied,
            'createdAt': lot.created_at.isoformat(),
        })
    return jsonify(result)

@admin_bp.route('/lots/<int:lot_id>', methods=['DELETE'])
def delete_lot(lot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    if any(spot.status == 'O' for spot in lot.spots):
        return jsonify({'error': 'Cannot delete lot with occupied slots'}), 400
    db.session.delete(lot)
    db.session.commit()
    return jsonify({'message': 'Lot deleted successfully'}), 200

@admin_bp.route('/lots/<int:lot_id>/slots', methods=['POST'])
def add_slot(lot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    new_slot_number = ParkingSpot.query.filter_by(lot_id=lot_id).count() + 1
    slot = ParkingSpot(lot_id=lot_id, slot_number=new_slot_number, status='A')
    db.session.add(slot)
    db.session.commit()

    # Optionally update number_of_spots in ParkingLot
    lot.number_of_spots = ParkingSpot.query.filter_by(lot_id=lot_id).count()
    db.session.commit()

    return jsonify({'message': 'Slot added successfully', 'slotNumber': new_slot_number}), 201

@admin_bp.route('/lots/<int:lot_id>/slots/<int:slot_number>', methods=['DELETE'])
def delete_slot(lot_id, slot_number):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    slot = ParkingSpot.query.filter_by(lot_id=lot_id, slot_number=slot_number).first()
    if not slot:
        return jsonify({'error': 'Slot not found'}), 404
    if slot.status == 'O':
        return jsonify({'error': 'Cannot delete occupied slot'}), 400

    db.session.delete(slot)
    db.session.commit()

    # Optionally update number_of_spots in ParkingLot
    lot = ParkingLot.query.get(lot_id)
    lot.number_of_spots = ParkingSpot.query.filter_by(lot_id=lot_id).count()
    db.session.commit()

    return jsonify({'message': 'Slot deleted successfully'}), 200

@admin_bp.route('/lots/<int:lot_id>/slots/<int:slot_number>/occupy', methods=['POST'])
def occupy_slot(lot_id, slot_number):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    slot = next((s for s in lot.spots if s.slot_number == slot_number), None)
    if not slot:
        return jsonify({'error': 'Slot not found'}), 404
    if slot.status == 'O':
        return jsonify({'error': 'Slot already occupied'}), 400

    data = request.json
    slot.status = 'O'
    slot.vehicle_id = data.get('vehicleId', 'N/A')
    slot.occupation_time = get_current_time()
    db.session.commit()
    return jsonify({'message': 'Slot occupied successfully', 'vehicleId': slot.vehicle_id, 'occupationTime': slot.occupation_time.isoformat()}), 200

@admin_bp.route('/lots/<int:lot_id>', methods=['PUT'])
def update_lot(lot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.json
    old_count = lot.number_of_spots
    new_count = data.get('maxSpots', lot.number_of_spots)
    # Count currently occupied spots
    occupied_count = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
    if new_count < occupied_count:
        return jsonify({'error': f'Cannot reduce slots below number of occupied spots ({occupied_count})'}), 400
    lot.prime_location_name = data.get('primeLocation', lot.prime_location_name)
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pinCode', lot.pin_code)
    lot.price = data.get('pricePerHour', lot.price)
    lot.number_of_spots = new_count
    db.session.commit()

    # Sync parking_spots table
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).order_by(ParkingSpot.slot_number).all()
    current_count = len(spots)

    if new_count > current_count:
        # Add new spots
        for i in range(current_count + 1, new_count + 1):
            spot = ParkingSpot(lot_id=lot_id, slot_number=i, status='A')
            db.session.add(spot)
        db.session.commit()
    elif new_count < current_count:
        # Remove extra spots (preferably those with status 'A')
        removable_spots = [s for s in spots if s.status == 'A']
        to_remove = current_count - new_count
        if len(removable_spots) < to_remove:
            return jsonify({'error': 'Cannot remove slots: not enough available spots'}), 400
        for spot in sorted(removable_spots, key=lambda s: s.slot_number, reverse=True)[:to_remove]:
            db.session.delete(spot)
        db.session.commit()

    # Optionally, re-number slot_number for all spots
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).order_by(ParkingSpot.slot_number).all()
    for idx, spot in enumerate(spots, 1):
        spot.slot_number = idx
    db.session.commit()

    # Return updated lot info
    occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    total = ParkingSpot.query.filter_by(lot_id=lot.id).count()
    return jsonify({
        'id': lot.id,
        'primeLocation': lot.prime_location_name,
        'address': lot.address,
        'pinCode': lot.pin_code,
        'pricePerHour': lot.price,
        'total': total,
        'available': total - occupied,
        'occupied': occupied,
        'createdAt': lot.created_at.isoformat(),
    }), 200

@admin_bp.route('/lots/<int:lot_id>/slots', methods=['GET'])
def get_lot_slots(lot_id):
    slots = ParkingSpot.query.filter_by(lot_id=lot_id).order_by(ParkingSpot.slot_number).all()
    return jsonify([
        {
            "slot_number": slot.slot_number,
            "status": slot.status,
            "vehicle_id": slot.vehicle_id,
            "username": slot.username
        }
        for slot in slots
    ])

@admin_bp.route('/users', methods=['GET'])
def get_users():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    users = User.query.all()
    print(f"Users fetched: {[user.username for user in users]}")
    return jsonify([
        {
            'id': user.id,
            'name': user.username,
            'email': user.email,
            'status': 'Active' if not user.banned else 'Banned'
        }
        for user in users
    ])

@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
def ban_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    user.banned = True
    db.session.commit()
    return jsonify({'message': 'User banned successfully', 'status': 'Banned'})

@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
def unban_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    user.banned = False
    db.session.commit()
    return jsonify({'message': 'User unbanned successfully', 'status': 'Active'})

@admin_bp.route('/occupancy-trend', methods=['GET'])
def occupancy_trend():
    try:
        # Get the last 7 days
        from datetime import datetime, timedelta
        today = datetime.now().date()
        days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        days_str = [d.strftime('%Y-%m-%d') for d in days]

        # Query Reservation table for each day (bookings, not releases)
        from .models import Reservation
        result = {d: 0 for d in days_str}
        
        logger.info(f"Querying reservations for dates: {days_str}")
        
        reservations = db.session.query(
            func.date(Reservation.parking_timestamp).label('date'),
            func.count(Reservation.id).label('count')
        ).filter(
            Reservation.parking_timestamp >= days[0],
            Reservation.parking_timestamp < today + timedelta(days=1)
        ).group_by(func.date(Reservation.parking_timestamp)).all()
        
        logger.info(f"Found reservations: {reservations}")
        
        for row in reservations:
            date_str = row.date.strftime('%Y-%m-%d')
            if date_str in result:
                result[date_str] = row.count
        
        response_data = {
            'dates': days_str,
            'occupied_counts': [result[d] for d in days_str]
        }
        
        logger.info(f"Returning trend data: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in occupancy-trend endpoint: {e}")
        return jsonify({'error': str(e)}), 500