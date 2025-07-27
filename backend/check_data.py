from celery_app.models import User, ParkingUsageLog
from app import app

with app.app_context():
    print("=== USERS ===")
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {user.role}")
    
    print("\n=== PARKING USAGE LOGS ===")
    logs = ParkingUsageLog.query.all()
    for log in logs:
        print(f"User ID: {log.user_id}, Location: {log.location}, Cost: {log.cost}, Duration: {log.duration}, Entry Time: {log.entry_time}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total Users: {len(users)}")
    print(f"Total Parking Logs: {len(logs)}")
    
    # Check which users have data
    user_ids_with_data = set(log.user_id for log in logs)
    print(f"Users with parking data: {user_ids_with_data}")
    
    # Check for each user
    for user in users:
        user_logs = ParkingUsageLog.query.filter_by(user_id=user.id).all()
        print(f"User {user.username} (ID: {user.id}): {len(user_logs)} parking logs") 