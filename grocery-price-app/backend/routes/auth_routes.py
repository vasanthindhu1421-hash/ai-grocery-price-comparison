"""
Authentication routes for user signup and login.
"""
from flask import Blueprint, request, jsonify, make_response
from models import db, User
from datetime import datetime
from utils import generate_token
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength."""
    if len(password) < 6:
        return False, 'Password must be at least 6 characters long'
    return True, None


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    User registration endpoint.
    
    Expected JSON:
    {
        "username": "user123",
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Missing required fields: username, email, password'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Input validation
        if not username or len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate JWT token
        token = generate_token(user.id)
        
        response = make_response(jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'token': token
        }), 201)
        
        # Set HTTP-only cookie
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax',
            max_age=86400  # 24 hours
        )
        
        return response
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        token = generate_token(user.id)
        
        response = make_response(jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }), 200)
        
        # Set HTTP-only cookie
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax',
            max_age=86400  # 24 hours
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint."""
    response = make_response(jsonify({'message': 'Logged out successfully'}), 200)
    response.set_cookie('auth_token', '', expires=0)
    return response


@auth_bp.route('/verify', methods=['GET'])
def verify():
    """Verify token endpoint."""
    from utils import token_required
    from flask import request as req
    
    token = None
    # Check cookie first
    token = req.cookies.get('auth_token')
    
    # Fallback to Authorization header
    if not token:
        auth_header = req.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                pass
    
    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    
    from utils import verify_token
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 401
    
    return jsonify({
        'valid': True,
        'user': user.to_dict()
    }), 200

