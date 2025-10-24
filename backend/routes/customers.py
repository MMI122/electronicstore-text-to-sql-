from flask import Blueprint, jsonify, request
from db.db_config import DatabaseConfig
import hashlib
import secrets
from datetime import datetime

customers_bp = Blueprint('customers', __name__)
db = DatabaseConfig()

def hash_password(password):
    """Simple password hashing (in production, use bcrypt or similar)"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

@customers_bp.route('/register', methods=['POST'])
def register_customer():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'zipcode']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if email already exists
        check_query = "SELECT customer_id FROM customers WHERE email = %s"
        existing = db.execute_query(check_query, (data['email'],), fetch=True)
        
        if existing:
            return jsonify({'error': 'Email already registered'}), 400

        # Insert new customer
        insert_query = """
        INSERT INTO customers (
            first_name, last_name, email, phone, address, 
            city, state, zipcode, date_of_birth, gender
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['first_name'],
            data['last_name'],
            data['email'],
            data['phone'],
            data['address'],
            data['city'],
            data['state'],
            data['zipcode'],
            data.get('date_of_birth'),
            data.get('gender', 'Other')
        )
        
        customer_id = db.execute_query(insert_query, params)
        
        if customer_id:
            return jsonify({
                'message': 'Customer registered successfully',
                'customer_id': customer_id
            }), 201
        else:
            return jsonify({'error': 'Failed to register customer'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        query = """
        SELECT 
            customer_id,
            first_name,
            last_name,
            email,
            phone,
            address,
            city,
            state,
            zipcode,
            date_of_birth,
            gender,
            total_spent,
            loyalty_points,
            registration_date
        FROM customers 
        WHERE customer_id = %s AND is_active = TRUE
        """
        
        result = db.execute_query(query, (customer_id,), fetch=True)
        
        if not result:
            return jsonify({'error': 'Customer not found'}), 404

        return jsonify({'customer': result[0]})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        data = request.get_json()
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        allowed_fields = [
            'first_name', 'last_name', 'phone', 'address', 
            'city', 'state', 'zipcode', 'date_of_birth', 'gender'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        params.append(customer_id)
        
        query = f"""
        UPDATE customers 
        SET {', '.join(update_fields)}
        WHERE customer_id = %s AND is_active = TRUE
        """
        
        result = db.execute_query(query, params)
        
        if result is not None:
            return jsonify({'message': 'Customer updated successfully'})
        else:
            return jsonify({'error': 'Customer not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id):
    try:
        query = """
        SELECT 
            o.order_id,
            o.order_number,
            o.order_date,
            o.order_status,
            o.payment_method,
            o.payment_status,
            o.total_amount,
            s.store_name,
            COUNT(oi.item_id) as item_count
        FROM orders o
        LEFT JOIN stores s ON o.store_id = s.store_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.customer_id = %s
        GROUP BY o.order_id
        ORDER BY o.order_date DESC
        """
        
        orders = db.execute_query(query, (customer_id,), fetch=True)
        
        return jsonify({'orders': orders or []})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/all', methods=['GET'])
def get_all_customers():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search')
        
        # Build WHERE clause
        where_conditions = ["is_active = TRUE"]
        params = []
        
        if search:
            where_conditions.append("(first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        where_clause = " AND ".join(where_conditions)
        offset = (page - 1) * limit
        
        query = f"""
        SELECT 
            customer_id,
            CONCAT(first_name, ' ', last_name) as full_name,
            email,
            phone,
            city,
            state,
            total_spent,
            loyalty_points,
            registration_date,
            (SELECT COUNT(*) FROM orders WHERE customer_id = customers.customer_id) as order_count
        FROM customers
        WHERE {where_clause}
        ORDER BY registration_date DESC
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        customers = db.execute_query(query, params, fetch=True)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM customers WHERE {where_clause}"
        total_result = db.execute_query(count_query, params[:-2], fetch=True)
        total = total_result[0]['total'] if total_result else 0
        
        return jsonify({
            'customers': customers,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/login', methods=['POST'])
def login_customer():
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        query = """
        SELECT customer_id, first_name, last_name, email, phone
        FROM customers 
        WHERE email = %s AND is_active = TRUE
        """
        
        result = db.execute_query(query, (data['email'],), fetch=True)
        
        if not result:
            return jsonify({'error': 'Customer not found'}), 404

        customer = result[0]
        
        # Update last login
        update_query = "UPDATE customers SET last_login = CURRENT_TIMESTAMP WHERE customer_id = %s"
        db.execute_query(update_query, (customer['customer_id'],))
        
        return jsonify({
            'message': 'Login successful',
            'customer': customer
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500