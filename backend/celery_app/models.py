from . import db
from datetime import datetime
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'user' or 'admin'

    reservations = relationship('Reservation', backref='user', lazy=True)

    def is_admin(self):
        return self.role == 'admin'


class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'

    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade="all, delete-orphan")


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(1), default='A')  # A = Available, O = Occupied

    reservations = db.relationship('Reservation', backref='spot', lazy=True)


class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)

    parking_cost = db.Column(db.Float, nullable=True)
    remarks = db.Column(db.String(255), nullable=True)


class ExportTask(db.Model):
    __tablename__ = 'export_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, done
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    download_link = db.Column(db.String(255), nullable=True)


class ReminderLog(db.Model):
    __tablename__ = 'reminder_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reminder_type = db.Column(db.String(50))  # daily, monthly
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

