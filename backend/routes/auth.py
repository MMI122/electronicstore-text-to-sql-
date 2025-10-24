from flask import Blueprint, jsonify, request, session
from db.db_config import DatabaseConfig
import bcrypt
import uuid
from datetime import datetime, timedelta
import re
import functools

auth_bp = Blueprint('auth', __name__)
db = DatabaseConfig()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Check password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_session(user_type, user_id):
    """Create a new session"""
    session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)  # Session expires in 7 days
    
    query = """
    INSERT INTO user_sessions (session_id, user_type, user_id, expires_at)
    VALUES (%s, %s, %s, %s)
    """
    db.execute_query(query, (session_id, user_type, user_id, expires_at))
    return session_id

def validate_session(session_id):
    """Validate and return session info"""
    query = """
    SELECT user_type, user_id FROM user_sessions 
    WHERE session_id = %s AND expires_at > NOW()
    """
    result = db.execute_query(query, (session_id,), fetch=True)
    return result[0] if result else None

def delete_session(session_id):
    """Delete a session"""
    query = "DELETE FROM user_sessions WHERE session_id = %s"
    db.execute_query(query, (session_id,))

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """Register a new customer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check password strength
        password = data['password']
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if email already exists
        existing_user = db.execute_query(
            "SELECT customer_id FROM customers WHERE email = %s",
            (data['email'],), fetch=True
        )
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert new customer
        query = """
        INSERT INTO customers (
            first_name, last_name, email, phone, address, city, state, zipcode,
            date_of_birth, gender, password_hash, role, email_verified
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['first_name'], data['last_name'], data['email'],
            data.get('phone', ''), data.get('address', ''), data.get('city', ''),
            data.get('state', ''), data.get('zipcode', ''), data.get('date_of_birth'),
            data.get('gender'), password_hash, 'customer', True
        )
        
        customer_id = db.execute_query(query, params)
        
        if customer_id:
            # Create session
            session_id = create_session('customer', customer_id)
            
            return jsonify({
                'message': 'Registration successful',
                'session_id': session_id,
                'user': {
                    'id': customer_id,
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'customer'
                }
            }), 201
        else:
            return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login_user():
    """Login user (customer, employee, or admin)"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']
        user_type = data.get('user_type', 'customer')  # Default to customer
        
        user = None
        user_id = None
        user_info = {}
        
        # Check different user types
        if user_type == 'admin':
            user = db.execute_query(
                "SELECT admin_id, email, password_hash, first_name, last_name, role FROM admin_users WHERE email = %s AND is_active = TRUE",
                (email,), fetch=True
            )
            if user:
                user = user[0]
                user_id = user['admin_id']
                user_info = {
                    'id': user_id,
                    'email': user['email'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'role': user['role']
                }
        
        elif user_type == 'employee':
            user = db.execute_query(
                "SELECT employee_id, email, password_hash, first_name, last_name, role FROM employees WHERE email = %s AND is_active = TRUE",
                (email,), fetch=True
            )
            if user:
                user = user[0]
                user_id = user['employee_id']
                user_info = {
                    'id': user_id,
                    'email': user['email'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'role': user['role']
                }
        
        else:  # customer
            user = db.execute_query(
                "SELECT customer_id, email, password_hash, first_name, last_name, role FROM customers WHERE email = %s AND is_active = TRUE",
                (email,), fetch=True
            )
            if user:
                user = user[0]
                user_id = user['customer_id']
                user_info = {
                    'id': user_id,
                    'email': user['email'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'role': user['role']
                }
        
        if not user or not check_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        if user_type == 'admin':
            db.execute_query(
                "UPDATE admin_users SET last_login = NOW() WHERE admin_id = %s",
                (user_id,)
            )
        elif user_type == 'employee':
            db.execute_query(
                "UPDATE employees SET last_login = NOW() WHERE employee_id = %s",
                (user_id,)
            )
        else:
            db.execute_query(
                "UPDATE customers SET last_login = NOW() WHERE customer_id = %s",
                (user_id,)
            )
        
        # Create session
        session_id = create_session(user_type, user_id)
        
        return jsonify({
            'message': 'Login successful',
            'session_id': session_id,
            'user': user_info,
            'user_type': user_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout_user():
    """Logout user"""
    try:
        session_id = request.headers.get('Authorization')
        if session_id and session_id.startswith('Bearer '):
            session_id = session_id[7:]
            delete_session(session_id)
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        if session_id.startswith('Bearer '):
            session_id = session_id[7:]
        
        session_info = validate_session(session_id)
        if not session_info:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        user_type = session_info['user_type']
        user_id = session_info['user_id']
        
        # Get user details based on type
        if user_type == 'admin':
            user = db.execute_query(
                "SELECT admin_id, username, email, first_name, last_name, role, last_login FROM admin_users WHERE admin_id = %s",
                (user_id,), fetch=True
            )
        elif user_type == 'employee':
            user = db.execute_query(
                "SELECT employee_id, email, first_name, last_name, role, position, department, last_login FROM employees WHERE employee_id = %s",
                (user_id,), fetch=True
            )
        else:  # customer
            user = db.execute_query(
                "SELECT customer_id, email, first_name, last_name, phone, address, city, state, total_spent, loyalty_points, last_login FROM customers WHERE customer_id = %s",
                (user_id,), fetch=True
            )
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user[0],
            'user_type': user_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Middleware function to check authentication
def require_auth(allowed_roles=None):
    """Decorator to require authentication for routes"""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            session_id = request.headers.get('Authorization')
            if not session_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Remove "Bearer " prefix if present
            if session_id.startswith('Bearer '):
                session_id = session_id[7:]
            
            session_info = validate_session(session_id)
            if not session_info:
                return jsonify({'error': 'Invalid or expired session'}), 401
            
            # Check role permissions if specified
            if allowed_roles:
                user_type = session_info['user_type']
                if user_type not in allowed_roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Add user info to request
            request.user_id = session_info['user_id']
            request.user_type = session_info['user_type']
            
            return f(*args, **kwargs)
        return wrapper
    return decorator