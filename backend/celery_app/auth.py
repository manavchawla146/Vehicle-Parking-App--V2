from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# Hardcoded admin credentials
ADMIN_EMAIL = 'admin@gmail.com'
ADMIN_PASSWORD = 'admin123'

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    username = data.get('fullname') or data.get('username')
    password = data.get('password')
    address = data.get('address')
    pincode = data.get('pincode')
    if not email or not username or not password:
        return jsonify({'error': 'Missing fields'}), 400
    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({'error': 'User already exists'}), 409
    user = User(
        email=email,
        username=username,
        password_hash=generate_password_hash(password),
        role='user',
        address=address,
        pincode=pincode
    )
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    session['role'] = user.role

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session['user_id'] = 'admin'
        session['role'] = 'admin'
        return jsonify({'role': 'admin', 'message': 'Admin login successful'}), 200
    user = User.query.filter_by(email=email).first()
    if user:
        if user.banned:
            return jsonify({'error': 'banned'}), 403
        if check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return jsonify({'role': user.role, 'message': 'User login successful', 'username': user.username}), 200
    return jsonify({'error': 'Invalid email or password'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

@auth_bp.route('/session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'role': session.get('role')}), 200
    return jsonify({'logged_in': False}), 200
