from celery_app.models import ParkingLot, ParkingSpot, ParkingUsageLog, User, Reservation
from datetime import datetime
from app import app

with app.app_context():
    print("=== Testing Updated Notification System ===")
    
    # Test with user ID 1
    user_id = 1
    
    # Get current time
    now = datetime.now()
    
    # Get all parking lots
    all_lots = ParkingLot.query.all()
    
    # Get user's parking history from parking_usage_log
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
    
    print(f"📊 User has {len(user_parking_history)} parking records")
    print(f"🏢 Total parking lots: {len(all_lots)}")
    print(f"🚗 Currently using lots: {list(currently_using_lot_ids)}")
    
    # Analyze each parking lot
    for lot in all_lots:
        # Skip if user is currently using this lot
        if lot.id in currently_using_lot_ids:
            print(f"⏭️ Skipping '{lot.prime_location_name}' - user is currently using it")
            continue
            
        # Get all spots in this lot
        lot_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        spot_ids = [spot.id for spot in lot_spots]
        
        # Check if user has ever used any spot in this lot
        lot_usage = [usage for usage in user_parking_history if usage.spot_id in spot_ids]
        
        if lot_usage:
            # User has used this lot before
            # Find the most recent usage
            latest_usage = max(lot_usage, key=lambda x: x.entry_time)
            days_since_last_use = (now - latest_usage.entry_time).days
            
            # Create notification based on how long ago they used it
            if days_since_last_use > 30:  # More than a month
                time_description = "a very long time"
            elif days_since_last_use > 14:  # More than 2 weeks
                time_description = "a long time"
            elif days_since_last_use > 7:  # More than a week
                time_description = "some time"
            else:
                print(f"⏭️ Skipping '{lot.prime_location_name}' - used recently ({days_since_last_use} days ago)")
                continue  # Skip if used recently
            
            notification = {
                'type': 'unused_lot',
                'message': f"You haven't booked '{lot.prime_location_name}' parking lot from {time_description}",
                'timestamp': latest_usage.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                'lot_id': lot.id,
                'lot_name': lot.prime_location_name,
                'days_since_use': days_since_last_use,
                'read': False
            }
            notifications.append(notification)
            print(f"✅ Notification: {notification['message']}")
            
        else:
            # User has never used this lot
            notification = {
                'type': 'never_used_lot',
                'message': f"You haven't tried '{lot.prime_location_name}' parking lot yet. Give it a try!",
                'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
                'lot_id': lot.id,
                'lot_name': lot.prime_location_name,
                'days_since_use': None,
                'read': False
            }
            notifications.append(notification)
            print(f"✅ Notification: {notification['message']}")
    
    # Sort notifications by days since last use (most unused first)
    notifications.sort(key=lambda x: x.get('days_since_use', 0) or 0, reverse=True)
    
    print(f"\n📧 Total notifications: {len(notifications)}")
    print(f"🔔 Unread count: {len([n for n in notifications if not n.get('read', False)])}")
    
    print("\n🎉 Updated notification test completed!") 