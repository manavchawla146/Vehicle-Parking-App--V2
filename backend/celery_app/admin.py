from flask import Blueprint, request, jsonify, session
from .models import db, ParkingLot, User
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/lots', methods=['POST'])
def add_lot():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    lot = ParkingLot(
        prime_location_name=data['primeLocation'],
        price=data['pricePerHour'],
        address=data['address'],    
        pin_code=data['pinCode'],
        number_of_spots=data['maxSpots'],
        created_at=datetime.utcnow()
    )
    db.session.add(lot)
    db.session.commit()
    return jsonify({'message': 'Lot added successfully', 'id': lot.id}), 201

@admin_bp.route('/lots', methods=['GET'])
def get_lots():
    lots = ParkingLot.query.all()
    return jsonify([
        {
            'id': lot.id,
            'primeLocation': lot.prime_location_name,
            'address': lot.address,
            'pinCode': lot.pin_code,
            'pricePerHour': lot.price,
            'total': lot.number_of_spots,
            'createdAt': lot.created_at.isoformat(),
            'occupiedSpots': [spot.id for spot in getattr(lot, 'spots', []) if getattr(spot, 'status', 'A') == 'O'],
            'slotDetails': {
                spot.id: {
                    'status': spot.status,
                }
                for spot in getattr(lot, 'spots', [])
            }
        }
        for lot in lots
    ])

@admin_bp.route('/lots/<int:lot_id>', methods=['DELETE'])
def delete_lot(lot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    db.session.delete(lot)
    db.session.commit()
    return jsonify({'message': 'Lot deleted successfully'}), 200

@admin_bp.route('/lots/<int:lot_id>/slots', methods=['POST'])
def add_slot(lot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    if len(lot.slots) >= lot.number_of_spots:
        return jsonify({'error': 'Maximum slots reached'}), 400

    new_slot_number = len(lot.slots) + 1
    slot = ParkingSpot(lot_id=lot_id, slot_number=new_slot_number, status='A')  # Using ParkingSpot
    db.session.add(slot)
    db.session.commit()
    return jsonify({'message': 'Slot added successfully', 'slotNumber': new_slot_number}), 201

@admin_bp.route('/lots/<int:lot_id>/slots/<int:slot_number>', methods=['DELETE'])
def delete_slot(lot_id, slot_number):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    slot = next((s for s in lot.spots if s.slot_number == slot_number), None)  # Using spots
    if not slot:
        return jsonify({'error': 'Slot not found'}), 404
    if slot.status == 'O':  # Check occupied status
        return jsonify({'error': 'Cannot delete occupied slot'}), 400

    db.session.delete(slot)
    for i, s in enumerate(sorted(lot.spots, key=lambda x: x.slot_number), 1):
        s.slot_number = i
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
    slot.occupation_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Slot occupied successfully', 'vehicleId': slot.vehicle_id, 'occupationTime': slot.occupation_time.isoformat()}), 200

@admin_bp.route('/lots/<int:lot_id>', methods=['PUT'])
def update_lot(lot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.json
    lot.prime_location_name = data.get('primeLocation', lot.prime_location_name)
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pinCode', lot.pin_code)
    lot.price = data.get('pricePerHour', lot.price)
    lot.number_of_spots = data.get('maxSpots', lot.number_of_spots)
    db.session.commit()
    return jsonify({
        'id': lot.id,
        'primeLocation': lot.prime_location_name,
        'address': lot.address,
        'pinCode': lot.pin_code,
        'pricePerHour': lot.price,
        'total': lot.number_of_spots,
        'createdAt': lot.created_at.isoformat(),
        'occupiedSpots': [],
        'slotDetails': {}
    }), 200

@admin_bp.route('/users', methods=['GET'])
def get_users():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    users = User.query.all()
    print(f"Users fetched: {[user.username for user in users]}")  # Debug log
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
