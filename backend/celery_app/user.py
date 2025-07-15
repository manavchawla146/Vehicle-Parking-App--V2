from flask import Blueprint, jsonify, session, request
from .models import db, User

user_bp = Blueprint('user', __name__, url_prefix='/api')

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
