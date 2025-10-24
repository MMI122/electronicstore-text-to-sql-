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
def register():
    try:
        data = request.get_json()
        required_fields = ['first_name', 'last_name', 'email', 'password', 'phone']
        
        # Validate required fields
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        password = data['password']
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if email already exists
        existing_user = db.execute_query(
            "SELECT email FROM customers WHERE email = %s",
            (data['email'],), fetch=True
        )
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert new customer
        query = """
        INSERT INTO customers (first_name, last_name, email, password_hash, phone, 
                              address, city, state, zipcode, date_of_birth, gender, role, email_verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'customer', TRUE)
        """
        
        params = (
            data['first_name'], data['last_name'], data['email'], password_hash,
            data['phone'], data.get('address', ''), data.get('city', ''),
            data.get('state', ''), data.get('zipcode', ''), 
            data.get('date_of_birth'), data.get('gender', 'Other')
        )
        
        customer_id = db.execute_query(query, params)
        
        if customer_id:
            # Create session
            session_id = create_session('customer', customer_id)
            
            return jsonify({
                'message': 'Registration successful',
                'user': {
                    'id': customer_id,
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'type': 'customer'
                },
                'session_id': session_id
            }), 201
        else:
            return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type', 'customer')  # customer, admin, employee
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        user = None
        user_id = None
        
        # Check different user types
        if user_type == 'admin':
            query = """
            SELECT admin_id, username, email, password_hash, first_name, last_name, role, is_active
            FROM admin_users WHERE email = %s
            """
            result = db.execute_query(query, (email,), fetch=True)
            if result:
                user = result[0]
                user_id = user['admin_id']
                
        elif user_type == 'employee':
            query = """
            SELECT employee_id, first_name, last_name, email, password_hash, role, is_active
            FROM employees WHERE email = %s
            """
            result = db.execute_query(query, (email,), fetch=True)
            if result:
                user = result[0]
                user_id = user['employee_id']
                
        else:  # customer
            query = """
            SELECT customer_id, first_name, last_name, email, password_hash, role, is_active
            FROM customers WHERE email = %s
            """
            result = db.execute_query(query, (email,), fetch=True)
            if result:
                user = result[0]
                user_id = user['customer_id']
                user_type = 'customer'
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if account is active
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Verify password
        if not check_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login for admin users
        if user_type == 'admin':
            db.execute_query(
                "UPDATE admin_users SET last_login = NOW() WHERE admin_id = %s",
                (user_id,)
            )
        
        # Create session
        session_id = create_session(user_type, user_id)
        
        # Prepare user data (exclude password)
        user_data = {
            'id': user_id,
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'type': user_type,
            'role': user.get('role', user_type)
        }
        
        if user_type == 'admin':
            user_data['username'] = user.get('username')
        
        return jsonify({
            'message': 'Login successful',
            'user': user_data,
            'session_id': session_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        session_id = request.headers.get('Authorization')
        if session_id:
            # Remove "Bearer " prefix if present
            if session_id.startswith('Bearer '):
                session_id = session_id[7:]
            delete_session(session_id)
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-session', methods=['GET'])
def verify_session():
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({'error': 'No session provided'}), 401
        
        # Remove "Bearer " prefix if present
        if session_id.startswith('Bearer '):
            session_id = session_id[7:]
        
        session_info = validate_session(session_id)
        if not session_info:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        user_type = session_info['user_type']
        user_id = session_info['user_id']
        
        # Get user details
        if user_type == 'admin':
            query = """
            SELECT admin_id, username, email, first_name, last_name, role
            FROM admin_users WHERE admin_id = %s AND is_active = TRUE
            """
            result = db.execute_query(query, (user_id,), fetch=True)
        elif user_type == 'employee':
            query = """
            SELECT employee_id, first_name, last_name, email, role
            FROM employees WHERE employee_id = %s AND is_active = TRUE
            """
            result = db.execute_query(query, (user_id,), fetch=True)
        else:  # customer
            query = """
            SELECT customer_id, first_name, last_name, email, role
            FROM customers WHERE customer_id = %s AND is_active = TRUE
            """
            result = db.execute_query(query, (user_id,), fetch=True)
        
        if not result:
            return jsonify({'error': 'User not found'}), 404
        
        user = result[0]
        user_data = {
            'id': user_id,
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'type': user_type,
            'role': user.get('role', user_type)
        }
        
        if user_type == 'admin':
            user_data['username'] = user.get('username')
        
        return jsonify({
            'valid': True,
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    try:
        session_id = request.headers.get('Authorization')
        if not session_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Remove "Bearer " prefix if present
        if session_id.startswith('Bearer '):
            session_id = session_id[7:]
        
        session_info = validate_session(session_id)
        if not session_info:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        user_type = session_info['user_type']
        user_id = session_info['user_id']
        
        # Get current password hash
        if user_type == 'admin':
            query = "SELECT password_hash FROM admin_users WHERE admin_id = %s"
            update_query = "UPDATE admin_users SET password_hash = %s WHERE admin_id = %s"
        elif user_type == 'employee':
            query = "SELECT password_hash FROM employees WHERE employee_id = %s"
            update_query = "UPDATE employees SET password_hash = %s WHERE employee_id = %s"
        else:  # customer
            query = "SELECT password_hash FROM customers WHERE customer_id = %s"
            update_query = "UPDATE customers SET password_hash = %s WHERE customer_id = %s"
        
        result = db.execute_query(query, (user_id,), fetch=True)
        if not result:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not check_password(current_password, result[0]['password_hash']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Hash new password and update
        new_password_hash = hash_password(new_password)
        db.execute_query(update_query, (new_password_hash, user_id))
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
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