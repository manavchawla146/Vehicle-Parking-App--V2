from flask import Blueprint, jsonify, session, request
from .models import db, User, ParkingLot, ParkingSpot, Reservation, ParkingUsageLog
from datetime import datetime, timezone
import logging
from . import cache

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api')

def get_current_time():
    """Get current time with proper timezone handling"""
    return datetime.now(timezone.utc)

def get_user_cache_key(prefix, user_id=None):
    """Generate user-specific cache key"""
    if user_id is None:
        user_id = session.get('user_id')
    return f"{prefix}_{user_id}"

def invalidate_user_cache(user_id=None):
    """Invalidate all user-specific cache"""
    if user_id is None:
        user_id = session.get('user_id')
    
    try:
        cache_keys = [
            get_user_cache_key('user_history', user_id),
            get_user_cache_key('user_notifications', user_id),
            get_user_cache_key('user_summary', user_id)
        ]
        for key in cache_keys:
            cache.delete(key)
        logger.info(f"✅ User {user_id} cache invalidated")
    except Exception as e:
        logger.error(f"❌ Failed to invalidate user {user_id} cache: {e}")

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
@cache.cached(timeout=60, key_prefix='parking_search')
def search_parking():
    """Search parking lots with caching"""
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
    logger.info(f"📊 Search results cached for query: '{query}'")
    return jsonify(result)

@user_bp.route('/parking/lot/<int:lot_id>/spots', methods=['GET'])
@cache.cached(timeout=120, key_prefix='lot_spots')
def get_lot_spots(lot_id):
    """Get spots for a specific lot with caching"""
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401
    
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'error': 'Lot not found'}), 404
    
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    logger.debug(f"Spots for lot {lot_id}: {[spot.id for spot in spots]}")
    logger.debug(f"Available spots for lot {lot_id}: {[spot.id for spot in spots if spot.status == 'A']}")
    
    result = {
        'spots': [{
            'id': spot.id,
            'lot_name': lot.prime_location_name,
            'username': spot.username if spot.status == 'O' else None,
            'price': lot.price,
            'status': spot.status,
            'vehicle_id': spot.vehicle_id,
            'occupation_time': spot.occupation_time.isoformat() if spot.occupation_time else None
        } for spot in spots]
    }
    
    logger.info(f"📊 Fetched {len(result['spots'])} spots for lot {lot_id} from cache/database")
    return jsonify(result)

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
    
    # Invalidate relevant cache after reservation
    invalidate_user_cache(user_id)
    
    logger.info(f"Successfully reserved spot {spot.id} in lot {lot.id} for user {user_id} at {current_time}")
    return jsonify({'message': 'Parking reserved successfully', 'reservationId': reservation.id, 'spotId': spot.id})

@user_bp.route('/user/parking-history', methods=['GET'])
def get_user_parking_history():
    """Get user parking history with user-specific caching"""
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401

    # Use user-specific cache key
    cache_key = get_user_cache_key('user_history', user_id)
    
    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"📊 Returning cached parking history for user {user_id}")
        return jsonify(cached_result)

    # If not in cache, fetch from database
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
            'timestamp': res.parking_timestamp.isoformat() if res.parking_timestamp else None,
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

    # Combine and cache result
    result = active_rows + parked_out_rows
    cache.set(cache_key, result, timeout=120)  # Cache for 2 minutes
    
    logger.info(f"📊 Fetched and cached {len(result)} parking history records for user {user_id}")
    return jsonify(result)

@user_bp.route('/user/parking-status-summary', methods=['GET'])
def get_user_parking_status_summary():
    """Get user parking status summary with caching"""
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401

    # Use user-specific cache key
    cache_key = get_user_cache_key('user_summary', user_id)
    
    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"📊 Returning cached parking summary for user {user_id}")
        return jsonify(cached_result)

    # If not in cache, calculate from database
    try:
        # Get user's parking history
        usage_logs = ParkingUsageLog.query.filter_by(user_id=user_id).all()
        
        # Calculate summary statistics
        total_sessions = len(usage_logs)
        total_cost = sum(log.cost for log in usage_logs if log.cost)
        total_duration = sum(log.duration for log in usage_logs if log.duration)
        
        # Get unique locations used
        locations_used = set()
        for log in usage_logs:
            if log.lot and log.lot.prime_location_name:
                locations_used.add(log.lot.prime_location_name)
        
        # Get active sessions
        active_reservations = Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).count()
        
        summary = {
            'total_sessions': total_sessions,
            'total_cost': round(total_cost, 2) if total_cost else 0,
            'total_duration': round(total_duration, 2) if total_duration else 0,
            'locations_used': list(locations_used),
            'active_sessions': active_reservations,
            'average_cost_per_session': round(total_cost / total_sessions, 2) if total_sessions > 0 else 0
        }
        
        # Cache the result
        cache.set(cache_key, summary, timeout=180)  # Cache for 3 minutes
        
        logger.info(f"📊 Generated and cached parking summary for user {user_id}")
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error generating parking summary: {e}")
        return jsonify({'error': 'Failed to generate summary'}), 500

@user_bp.route('/user/release-parking', methods=['POST'])
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
        exit_time = datetime.now(timezone.utc)
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
        reservation.leaving_timestamp = exit_time
        reservation.parking_cost = cost

        # Update spot
        spot.status = 'A'
        spot.vehicle_id = None
        spot.occupation_time = None
        spot.username = None

        db.session.commit()
        
        # Invalidate user cache after release
        invalidate_user_cache(user_id)
        
        logger.info(f"Successfully released spot {spot_id} for user {user_id}")
        return jsonify({
            'message': 'Parking released successfully',
            'cost': cost,
            'duration': duration_hours
        }), 200

    except Exception as e:
        logger.error(f"Error releasing parking: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to release parking'}), 500

@user_bp.route('/user/notifications', methods=['GET'])
def get_user_notifications():
    """Get user notifications with user-specific caching"""
    user_id = session.get('user_id')
    if not user_id or user_id == 'admin':
        return jsonify({'error': 'Not logged in or admin'}), 401
    
    # Use user-specific cache key
    cache_key = get_user_cache_key('user_notifications', user_id)
    
    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"📊 Returning cached notifications for user {user_id}")
        return jsonify(cached_result)
    
    try:
        from datetime import datetime, timedelta
        
        now = datetime.now()
        all_lots = ParkingLot.query.all()
        user_parking_history = ParkingUsageLog.query.filter_by(user_id=user_id).all()
        
        # Get user's active reservations (currently using)
        active_reservations = Reservation.query.filter_by(
            user_id=user_id, 
            leaving_timestamp=None
        ).all()
        
        # Get lot IDs that user is currently using
        currently_using_lot_ids = set()
        for reservation in active_reservations:
            spot = ParkingSpot.query.get(reservation.spot_id)
            if spot:
                currently_using_lot_ids.add(spot.lot_id)
        
        notifications = []
        
        # Analyze each parking lot
        for lot in all_lots:
            # Skip if user is currently using this lot
            if lot.id in currently_using_lot_ids:
                continue
                
            lot_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
            spot_ids = [spot.id for spot in lot_spots]
            
            lot_usage = [usage for usage in user_parking_history if usage.spot_id in spot_ids]
            
            if lot_usage:
                latest_usage = max(lot_usage, key=lambda x: x.entry_time)
                days_since_last_use = (now - latest_usage.entry_time).days
                
                if days_since_last_use > 30:  # More than a month
                    time_description = "a very long time"
                elif days_since_last_use > 14:  # More than 2 weeks
                    time_description = "a long time"
                elif days_since_last_use > 7:  # More than a week
                    time_description = "some time"
                else:
                    continue  # Skip if used recently
                
                notifications.append({
                    'type': 'unused_lot',
                    'message': f"You haven't booked '{lot.prime_location_name}' parking lot from {time_description}",
                    'timestamp': latest_usage.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'lot_id': lot.id,
                    'lot_name': lot.prime_location_name,
                    'days_since_use': days_since_last_use,
                    'read': False
                })
            else:
                notifications.append({
                    'type': 'never_used_lot',
                    'message': f"You haven't tried '{lot.prime_location_name}' parking lot yet. Give it a try!",
                    'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'lot_id': lot.id,
                    'lot_name': lot.prime_location_name,
                    'days_since_use': None,
                    'read': False
                })
        
        notifications.sort(key=lambda x: x.get('days_since_use', 0) or 0, reverse=True)
        
        result = {
            'notifications': notifications,
            'unread_count': len([n for n in notifications if not n.get('read', False)])
        }
        
        # Cache the result
        cache.set(cache_key, result, timeout=60)  # Cache for 1 minute
        
        logger.info(f"📊 Generated and cached {len(notifications)} notifications for user {user_id}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return jsonify({'error': 'Failed to fetch notifications'}), 500


