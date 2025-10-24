from flask import Blueprint, jsonify, request
from db.db_config import DatabaseConfig
import json
from datetime import datetime, timedelta
import random
import string

orders_bp = Blueprint('orders', __name__)
db = DatabaseConfig()

def generate_order_number():
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"ORD-{timestamp}-{random_part}"

@orders_bp.route('/', methods=['GET'])
def get_orders():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        customer_id = request.args.get('customer_id')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        where_conditions = []
        params = []

        if customer_id:
            where_conditions.append("o.customer_id = %s")
            params.append(customer_id)

        if status:
            where_conditions.append("o.order_status = %s")
            params.append(status)

        if start_date:
            where_conditions.append("DATE(o.order_date) >= %s")
            params.append(start_date)

        if end_date:
            where_conditions.append("DATE(o.order_date) <= %s")
            params.append(end_date)

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        offset = (page - 1) * limit

        query = f"""
        SELECT 
            o.*,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            c.email as customer_email,
            s.store_name,
            CONCAT(e.first_name, ' ', e.last_name) as employee_name,
            COUNT(oi.item_id) as item_count
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN stores s ON o.store_id = s.store_id
        LEFT JOIN employees e ON o.employee_id = e.employee_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        {where_clause}
        GROUP BY o.order_id
        ORDER BY o.order_date DESC
        LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])
        orders = db.execute_query(query, params, fetch=True)

        # Get total count
        count_query = f"""
        SELECT COUNT(DISTINCT o.order_id) as total
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        {where_clause}
        """
        
        total_result = db.execute_query(count_query, params[:-2], fetch=True)
        total = total_result[0]['total'] if total_result else 0

        return jsonify({
            'orders': orders,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        # Get order details
        order_query = """
        SELECT 
            o.*,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            c.email as customer_email,
            c.phone as customer_phone,
            s.store_name,
            s.address as store_address,
            CONCAT(e.first_name, ' ', e.last_name) as employee_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN stores s ON o.store_id = s.store_id
        LEFT JOIN employees e ON o.employee_id = e.employee_id
        WHERE o.order_id = %s
        """
        
        order_result = db.execute_query(order_query, (order_id,), fetch=True)
        
        if not order_result:
            return jsonify({'error': 'Order not found'}), 404

        order = order_result[0]

        # Get order items
        items_query = """
        SELECT 
            oi.*,
            p.product_name,
            p.brand,
            p.model,
            c.category_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE oi.order_id = %s
        """
        
        items = db.execute_query(items_query, (order_id,), fetch=True)

        # Get related banking transaction
        banking_query = """
        SELECT bt.*, ba.account_number, ba.account_type
        FROM banking_transactions bt
        JOIN banking_accounts ba ON bt.account_id = ba.account_id
        WHERE bt.related_order_id = %s
        """
        
        banking_transaction = db.execute_query(banking_query, (order_id,), fetch=True)

        return jsonify({
            'order': order,
            'items': items or [],
            'banking_transaction': banking_transaction[0] if banking_transaction else None
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_id', 'store_id', 'items', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if not data['items']:
            return jsonify({'error': 'Order must contain at least one item'}), 400

        # Calculate totals
        subtotal = 0
        order_items = []
        
        for item in data['items']:
            if 'product_id' not in item or 'quantity' not in item:
                return jsonify({'error': 'Each item must have product_id and quantity'}), 400
            
            # Get product details
            product_query = "SELECT price, stock_quantity FROM products WHERE product_id = %s AND is_active = TRUE"
            product_result = db.execute_query(product_query, (item['product_id'],), fetch=True)
            
            if not product_result:
                return jsonify({'error': f'Product {item["product_id"]} not found'}), 404
            
            product = product_result[0]
            
            if product['stock_quantity'] < item['quantity']:
                return jsonify({'error': f'Insufficient stock for product {item["product_id"]}'}), 400
            
            unit_price = product['price']
            total_price = unit_price * item['quantity']
            subtotal += total_price
            
            order_items.append({
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'unit_price': unit_price,
                'total_price': total_price
            })

        # Calculate taxes and total
        tax_rate = 0.08  # 8% tax rate
        tax_amount = subtotal * tax_rate
        shipping_cost = data.get('shipping_cost', 0)
        discount_amount = data.get('discount_amount', 0)
        total_amount = subtotal + tax_amount + shipping_cost - discount_amount

        # Generate order number
        order_number = generate_order_number()

        # Create order
        order_query = """
        INSERT INTO orders (
            customer_id, store_id, employee_id, order_number, 
            payment_method, subtotal, tax_amount, shipping_cost, 
            discount_amount, total_amount, shipping_address, billing_address, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        order_params = (
            data['customer_id'],
            data['store_id'],
            data.get('employee_id'),
            order_number,
            data['payment_method'],
            subtotal,
            tax_amount,
            shipping_cost,
            discount_amount,
            total_amount,
            data.get('shipping_address'),
            data.get('billing_address'),
            data.get('notes')
        )

        # Execute order creation
        connection = db.get_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(order_query, order_params)
            order_id = cursor.lastrowid

            # Insert order items and update stock
            for item in order_items:
                # Insert order item
                item_query = """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(item_query, (
                    order_id, item['product_id'], item['quantity'], 
                    item['unit_price'], item['total_price']
                ))

                # Update product stock
                stock_query = """
                UPDATE products 
                SET stock_quantity = stock_quantity - %s 
                WHERE product_id = %s
                """
                cursor.execute(stock_query, (item['quantity'], item['product_id']))

                # Log inventory change
                log_query = """
                INSERT INTO inventory_logs (
                    product_id, transaction_type, quantity_change, 
                    reason, reference_id, employee_id
                ) VALUES (%s, 'OUT', %s, %s, %s, %s)
                """
                cursor.execute(log_query, (
                    item['product_id'], -item['quantity'], 
                    f'Sale - Order {order_number}', order_id, data.get('employee_id')
                ))

            connection.commit()

            # Create banking transaction if payment method requires it
            if data['payment_method'] in ['BANK_ACCOUNT', 'CREDIT_CARD', 'DEBIT_CARD']:
                # Get customer's primary account
                account_query = """
                SELECT account_id, balance FROM banking_accounts 
                WHERE customer_id = %s AND account_status = 'ACTIVE'
                ORDER BY account_id LIMIT 1
                """
                account_result = db.execute_query(account_query, (data['customer_id'],), fetch=True)
                
                if account_result:
                    account = account_result[0]
                    new_balance = account['balance'] - total_amount
                    
                    transaction_query = """
                    INSERT INTO banking_transactions (
                        account_id, transaction_type, amount, balance_after, 
                        description, related_order_id
                    ) VALUES (%s, 'DEBIT', %s, %s, %s, %s)
                    """
                    
                    db.execute_query(transaction_query, (
                        account['account_id'], total_amount, new_balance,
                        f'Payment for Order {order_number}', order_id
                    ))

            return jsonify({
                'message': 'Order created successfully',
                'order_id': order_id,
                'order_number': order_number,
                'total_amount': total_amount
            }), 201

        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status():
    try:
        order_id = int(request.view_args['order_id'])
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400

        valid_statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED']
        if data['status'] not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400

        # Update order status
        update_query = """
        UPDATE orders 
        SET order_status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE order_id = %s
        """
        
        result = db.execute_query(update_query, (data['status'], order_id))
        
        if result == 0:
            return jsonify({'error': 'Order not found'}), 404

        return jsonify({'message': 'Order status updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/analytics', methods=['GET'])
def get_order_analytics():
    try:
        days = int(request.args.get('days', 30))
        print(f"Analytics request for {days} days")
        
        # Daily sales trend
        sales_trend_query = """
        SELECT 
            DATE(order_date) as order_date,
            COUNT(*) as order_count,
            SUM(total_amount) as revenue,
            AVG(total_amount) as avg_order_value
        FROM orders 
        WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        AND order_status != 'CANCELLED'
        GROUP BY DATE(order_date)
        ORDER BY order_date DESC
        """

        # Order status distribution
        status_query = """
        SELECT 
            order_status,
            COUNT(*) as count,
            SUM(total_amount) as total_value
        FROM orders 
        WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY order_status
        """

        # Payment method analysis
        payment_query = """
        SELECT 
            payment_method,
            COUNT(*) as order_count,
            SUM(total_amount) as revenue,
            AVG(total_amount) as avg_amount
        FROM orders 
        WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        AND order_status != 'CANCELLED'
        GROUP BY payment_method
        ORDER BY revenue DESC
        """

        # Top customers by orders
        customers_query = """
        SELECT 
            c.customer_id,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            c.email,
            COUNT(o.order_id) as order_count,
            SUM(o.total_amount) as total_spent,
            AVG(o.total_amount) as avg_order_value
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        AND o.order_status IN ('PROCESSING', 'DELIVERED')
        GROUP BY c.customer_id
        ORDER BY total_spent DESC
        LIMIT 10
        """

        sales_trend = db.execute_query(sales_trend_query, (days,), fetch=True)
        status_distribution = db.execute_query(status_query, (days,), fetch=True)
        payment_methods = db.execute_query(payment_query, (days,), fetch=True)
        top_customers = db.execute_query(customers_query, (days,), fetch=True)

        print(f"Sales trend results: {sales_trend}")
        print(f"Status distribution results: {status_distribution}")
        print(f"Payment methods results: {payment_methods}")
        print(f"Top customers results: {top_customers}")

        return jsonify({
            'sales_trend': sales_trend or [],
            'status_distribution': status_distribution or [],
            'payment_methods': payment_methods or [],
            'top_customers': top_customers or []
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Banking routes
@orders_bp.route('/banking/accounts/<int:customer_id>', methods=['GET'])
def get_customer_accounts(customer_id):
    try:
        query = """
        SELECT 
            ba.*,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name
        FROM banking_accounts ba
        JOIN customers c ON ba.customer_id = c.customer_id
        WHERE ba.customer_id = %s
        ORDER BY ba.opened_date DESC
        """
        
        accounts = db.execute_query(query, (customer_id,), fetch=True)
        return jsonify({'accounts': accounts or []})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/banking/transactions/<int:account_id>', methods=['GET'])
def get_account_transactions(account_id):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit

        query = """
        SELECT 
            bt.*,
            ba.account_number,
            o.order_number
        FROM banking_transactions bt
        JOIN banking_accounts ba ON bt.account_id = ba.account_id
        LEFT JOIN orders o ON bt.related_order_id = o.order_id
        WHERE bt.account_id = %s
        ORDER BY bt.transaction_date DESC
        LIMIT %s OFFSET %s
        """
        
        transactions = db.execute_query(query, (account_id, limit, offset), fetch=True)

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM banking_transactions WHERE account_id = %s"
        total_result = db.execute_query(count_query, (account_id,), fetch=True)
        total = total_result[0]['total'] if total_result else 0

        return jsonify({
            'transactions': transactions or [],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin Order Management Routes
@orders_bp.route('/admin', methods=['GET'])
def get_admin_orders():
    """Get all orders for admin management"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status = request.args.get('status')
        search = request.args.get('search')
        
        where_conditions = []
        params = []
        
        if status:
            where_conditions.append("o.order_status = %s")
            params.append(status)
            
        if search:
            where_conditions.append("(o.order_number LIKE %s OR CONCAT(c.first_name, ' ', c.last_name) LIKE %s OR c.email LIKE %s)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        offset = (page - 1) * limit
        
        query = f"""
        SELECT 
            o.order_id,
            o.order_number,
            o.order_date,
            o.order_status,
            o.payment_method,
            o.subtotal,
            o.tax_amount,
            o.total_amount,
            o.shipping_address,
            o.billing_address,
            c.customer_id,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            c.email as customer_email,
            COUNT(oi.item_id) as item_count
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        {where_clause}
        GROUP BY o.order_id
        ORDER BY o.order_date DESC
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        orders = db.execute_query(query, params, fetch=True)
        
        # Get total count
        count_query = f"""
        SELECT COUNT(DISTINCT o.order_id) as total
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        {where_clause}
        """
        
        count_params = params[:-2] if where_conditions else []
        total_result = db.execute_query(count_query, count_params, fetch=True)
        total = total_result[0]['total'] if total_result else 0
        
        return jsonify({
            'orders': orders or [],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })
        
    except Exception as e:
        print(f"Admin orders error: {e}")
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/admin/<int:order_id>/status', methods=['PUT'])
def admin_update_order_status(order_id):
    """Update order status (admin only)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
            
        # Validate status
        valid_statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        # Update order status
        query = """
        UPDATE orders 
        SET order_status = %s, updated_at = NOW()
        WHERE order_id = %s
        """
        
        result = db.execute_query(query, (new_status, order_id))
        
        if result:
            return jsonify({
                'message': 'Order status updated successfully',
                'order_id': order_id,
                'new_status': new_status
            }), 200
        else:
            return jsonify({'error': 'Failed to update order status'}), 500
            
    except Exception as e:
        print(f"Update order status error: {e}")
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/admin/<int:order_id>', methods=['GET'])
def admin_get_order_details(order_id):
    """Get detailed order information for admin"""
    try:
        # Get order details
        order_query = """
        SELECT 
            o.*,
            c.name as customer_name,
            c.email as customer_email,
            c.phone as customer_phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = %s
        """
        
        order = db.execute_query(order_query, (order_id,), fetch=True)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
            
        # Get order items
        items_query = """
        SELECT 
            oi.*,
            p.product_name,
            p.brand,
            p.model
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = %s
        """
        
        items = db.execute_query(items_query, (order_id,), fetch=True)
        
        return jsonify({
            'order': order[0],
            'items': items or []
        })
        
    except Exception as e:
        print(f"Get order details error: {e}")
        return jsonify({'error': str(e)}), 500