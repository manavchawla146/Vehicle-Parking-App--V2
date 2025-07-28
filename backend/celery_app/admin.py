from flask import Blueprint, request, jsonify, session
from .models import db, ParkingLot, User, ParkingSpot
from datetime import datetime, timezone
import logging
from sqlalchemy import func
from . import cache

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def get_current_time():
    """Get current time with proper timezone handling"""
    return datetime.now()

def invalidate_lots_cache():
    """Invalidate all lots-related cache"""
    try:
        cache.delete('admin_lots')
        cache.delete('admin_lots_summary')
        logger.info(" Lots cache invalidated")
    except Exception as e:
        logger.error(f" Failed to invalidate lots cache: {e}")

def invalidate_users_cache():
    """Invalidate all users-related cache"""
    try:
        cache.delete('admin_users')
        logger.info(" Users cache invalidated")
    except Exception as e:
        logger.error(f" Failed to invalidate users cache: {e}")

@admin_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cache - admin only"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Clear all cache keys
        cache.clear()
        logger.info(" All cache cleared by admin")
        return jsonify({'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        logger.error(f" Failed to clear cache: {e}")
        return jsonify({'error': 'Failed to clear cache'}), 500



@admin_bp.route('/cache/status', methods=['GET'])
def get_cache_status():
    """Get cache status - admin only"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Get cache info (this is a simplified version)
        status = {
            'cache_type': 'redis',
            'cache_url': 'redis://localhost:6379/1',
            'default_timeout': 300,
            'status': 'active'
        }
        return jsonify(status), 200
    except Exception as e:
        logger.error(f" Failed to get cache status: {e}")
        return jsonify({'error': 'Failed to get cache status'}), 500

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
        
        # No cache invalidation needed since we removed caching
        
        # Send email notification to all users about the new lot using Celery task with 5-minute delay
        try:
            from jobs.reports import send_lot_addition_notification
            # Schedule the task to run after 5 minutes (300 seconds)
            send_lot_addition_notification.apply_async(args=[data], countdown=60)
            logger.info(" Lot addition notification task scheduled for 5 minutes from now")
        except Exception as e:
            logger.error(f" Failed to schedule lot addition notification: {e}")
        
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
    """Get all parking lots without caching to avoid data corruption"""

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
            'occupied': occupied,
            'available': total - occupied
        })
    logger.info(f"Fetched {len(result)} lots from cache/database")
    return jsonify(result)

@admin_bp.route('/lots/<int:lot_id>', methods=['DELETE'])
def delete_lot(lot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    if any(spot.status == 'O' for spot in lot.spots):
        return jsonify({'error': 'Cannot delete lot with occupied slots'}), 400

    # Store lot data before deletion for notification
    lot_data = {
        'primeLocation': lot.prime_location_name,
        'address': lot.address,
        'pinCode': lot.pin_code,
        'pricePerHour': lot.price,
        'maxSpots': lot.number_of_spots
    }

    # Send email notification to all users about the lot deletion using Celery task with 5-minute delay
    try:
        from jobs.reports import send_lot_deletion_notification
        send_lot_deletion_notification.apply_async(args=[lot_data], countdown=60)
        logger.info(" Lot deletion notification task scheduled for 5 minutes from now")
    except Exception as e:
        logger.error(f" Failed to schedule lot deletion notification: {e}")

    db.session.delete(lot)
    db.session.commit()
    
    # No cache invalidation needed since we removed caching
    
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
    """Get slots for a specific lot without caching to avoid data corruption"""

    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    result = [{
        'slot_number': spot.slot_number,
        'status': spot.status,
        'vehicle_id': spot.vehicle_id,
        'occupation_time': spot.occupation_time.isoformat() if spot.occupation_time else None,
        'username': spot.username
    } for spot in spots]
    logger.info(f"Fetched {len(result)} slots for lot {lot_id} from cache/database")
    return jsonify(result)

@admin_bp.route('/users', methods=['GET'])
@cache.cached(timeout=15, key_prefix='admin_users')  # Reduced to 15 seconds
def get_users():
    """Get all users with caching"""
    users = User.query.filter(User.role != 'admin').all()
    result = [{
            'id': user.id,
            'name': user.username,
            'email': user.email,
        'address': user.address,
        'pincode': user.pincode,
        'status': 'Banned' if user.banned else 'Active'
    } for user in users]
    logger.info(f"Fetched {len(result)} users from cache/database")
    return jsonify(result)

@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
def ban_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get_or_404(user_id)
    user.banned = True
    db.session.commit()
    
    # Invalidate users cache to reflect the change
    invalidate_users_cache()
    
    return jsonify({'message': 'User banned successfully', 'status': 'Banned'}), 200

@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
def unban_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get_or_404(user_id)
    user.banned = False
    db.session.commit()
    
    # Invalidate users cache to reflect the change
    invalidate_users_cache()
    
    return jsonify({'message': 'User unbanned successfully', 'status': 'Active'}), 200

@admin_bp.route('/summary', methods=['GET'])
@cache.cached(timeout=15, key_prefix='admin_summary')  # Reduced to 15 seconds
def get_admin_summary():
    """Get admin summary data with caching"""
    try:
        # Get lots data
        lots = ParkingLot.query.all()
        lot_data = []
        total_occupied = 0
        total_spots = 0
        
        for lot in lots:
            occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            total = ParkingSpot.query.filter_by(lot_id=lot.id).count()
            total_occupied += occupied
            total_spots += total
            
            lot_data.append({
                'name': lot.prime_location_name,
                'occupied': occupied,
                'total': total
            })
        
        # Get daily occupancy trend (last 7 days)
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # This is a simplified version - you might want to add actual usage tracking
        daily_trend = []
        for i in range(7):
            date = start_date + timedelta(days=i)
            daily_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'occupancy': total_occupied  # Simplified - should be actual daily data
            })
        
        summary = {
            'lots': lot_data,
            'total_occupied': total_occupied,
            'total_spots': total_spots,
            'utilization_rate': (total_occupied / total_spots * 100) if total_spots > 0 else 0,
            'daily_trend': daily_trend
        }
        
        logger.info(f"Generated admin summary from cache/database")
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error generating admin summary: {e}")
        return jsonify({'error': 'Failed to generate summary'}), 500

@admin_bp.route('/occupancy-trend', methods=['GET'])
def occupancy_trend():
    """Get daily occupancy trend data from database"""
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
        
        # Get actual reservation counts from database
        reservations = db.session.query(
            func.date(Reservation.parking_timestamp).label('date'),
            func.count(Reservation.id).label('count')
        ).filter(
            Reservation.parking_timestamp >= days[0],
            Reservation.parking_timestamp < today + timedelta(days=1)
        ).group_by(func.date(Reservation.parking_timestamp)).all()
        
        logger.info(f"Found reservations: {reservations}")
        
        # Map database results to dates
        for row in reservations:
            # row.date is already a string from func.date()
            date_str = str(row.date)
            if date_str in result:
                result[date_str] = row.count
        
        response_data = {
            'dates': days_str,
            'occupied_counts': [result[d] for d in days_str],
            'total_reservations': sum(result.values()),
            'date_range': f"{days_str[0]} to {days_str[-1]}"
        }
        
        logger.info(f"Returning real trend data from database: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in occupancy-trend endpoint: {e}")
        # Return empty data instead of error to prevent frontend fallback
        return jsonify({
            'dates': [],
            'occupied_counts': [],
            'total_reservations': 0,
            'error': 'Failed to load trend data'
        }), 500