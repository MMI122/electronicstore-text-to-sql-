from flask import Blueprint, jsonify, request
from db.db_config import DatabaseConfig
import json
from datetime import datetime

cart_bp = Blueprint('cart', __name__)
db = DatabaseConfig()

@cart_bp.route('/<int:customer_id>', methods=['GET'])
def get_cart(customer_id):
    try:
        print(f"Getting cart for customer: {customer_id}")
        query = """
        SELECT 
            c.cart_id,
            c.customer_id,
            c.product_id,
            c.quantity,
            c.added_at,
            p.product_name,
            p.brand,
            p.price,
            p.stock_quantity,
            p.warranty_period,
            cat.category_name,
            (c.quantity * p.price) as total_price
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        LEFT JOIN categories cat ON p.category_id = cat.category_id
        WHERE c.customer_id = %s AND p.is_active = TRUE
        ORDER BY c.added_at DESC
        """
        
        print(f"Executing cart query for customer {customer_id}")
        cart_items = db.execute_query(query, (customer_id,), fetch=True)
        print(f"Cart items found: {cart_items}")
        
        # Calculate totals
        subtotal = sum(float(item['total_price']) for item in cart_items) if cart_items else 0
        tax_rate = 0.08  # 8% tax
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        result = {
            'cart_items': cart_items,
            'summary': {
                'item_count': len(cart_items),
                'subtotal': round(subtotal, 2),
                'tax_amount': round(tax_amount, 2),
                'total_amount': round(total_amount, 2)
            }
        }
        print(f"Cart result: {result}")
        
        return jsonify(result)

    except Exception as e:
        print(f"Error getting cart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        print(f"Cart add request data: {data}")
        
        # Validate required fields
        required_fields = ['customer_id', 'product_id', 'quantity']
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400

        customer_id = data['customer_id']
        product_id = data['product_id']
        quantity = int(data['quantity'])

        print(f"Adding to cart: customer={customer_id}, product={product_id}, quantity={quantity}")

        if quantity <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400

        # Check if product exists and has enough stock
        product_query = """
        SELECT product_id, product_name, price, stock_quantity 
        FROM products 
        WHERE product_id = %s AND is_active = TRUE
        """
        product = db.execute_query(product_query, (product_id,), fetch=True)
        print(f"Product found: {product}")
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if product[0]['stock_quantity'] < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400

        # Check if item already exists in cart
        existing_query = """
        SELECT cart_id, quantity 
        FROM cart 
        WHERE customer_id = %s AND product_id = %s
        """
        existing_item = db.execute_query(existing_query, (customer_id, product_id), fetch=True)
        print(f"Existing cart item: {existing_item}")

        if existing_item:
            # Update existing item
            new_quantity = existing_item[0]['quantity'] + quantity
            
            if product[0]['stock_quantity'] < new_quantity:
                return jsonify({'error': 'Not enough stock for this quantity'}), 400
            
            update_query = """
            UPDATE cart 
            SET quantity = %s, updated_at = CURRENT_TIMESTAMP
            WHERE cart_id = %s
            """
            result = db.execute_query(update_query, (new_quantity, existing_item[0]['cart_id']))
            print(f"Updated cart item, result: {result}")
        else:
            # Add new item
            insert_query = """
            INSERT INTO cart (customer_id, product_id, quantity)
            VALUES (%s, %s, %s)
            """
            result = db.execute_query(insert_query, (customer_id, product_id, quantity))
            print(f"Inserted new cart item, result: {result}")

        return jsonify({'message': 'Item added to cart successfully'})

    except Exception as e:
        print(f"Cart add error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/update/<int:cart_id>', methods=['PUT'])
def update_cart_item(cart_id):
    try:
        data = request.get_json()
        
        if 'quantity' not in data:
            return jsonify({'error': 'Quantity is required'}), 400

        quantity = int(data['quantity'])
        
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400

        # Get cart item and check stock
        cart_query = """
        SELECT c.cart_id, c.product_id, p.stock_quantity
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.cart_id = %s
        """
        cart_item = db.execute_query(cart_query, (cart_id,), fetch=True)
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        if cart_item[0]['stock_quantity'] < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400

        # Update quantity
        update_query = """
        UPDATE cart 
        SET quantity = %s, updated_at = CURRENT_TIMESTAMP
        WHERE cart_id = %s
        """
        db.execute_query(update_query, (quantity, cart_id))

        return jsonify({'message': 'Cart item updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/remove/<int:cart_id>', methods=['DELETE'])
def remove_cart_item(cart_id):
    try:
        query = "DELETE FROM cart WHERE cart_id = %s"
        result = db.execute_query(query, (cart_id,))
        
        if result is not None:
            return jsonify({'message': 'Item removed from cart successfully'})
        else:
            return jsonify({'error': 'Cart item not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/clear/<int:customer_id>', methods=['DELETE'])
def clear_cart(customer_id):
    try:
        query = "DELETE FROM cart WHERE customer_id = %s"
        db.execute_query(query, (customer_id,))
        
        return jsonify({'message': 'Cart cleared successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/checkout', methods=['POST'])
def checkout():
    try:
        data = request.get_json()
        print(f"Checkout request data: {data}")
        
        # Validate required fields
        required_fields = ['customer_id', 'payment_method', 'shipping_address']
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400

        customer_id = data['customer_id']
        payment_method = data['payment_method']
        shipping_address = data['shipping_address']
        store_id = data.get('store_id', 1)  # Default store
        employee_id = data.get('employee_id', 1)  # Default employee

        print(f"Checkout for customer {customer_id}")

        # Get cart items
        cart_query = """
        SELECT 
            c.cart_id,
            c.product_id,
            c.quantity,
            p.product_name,
            p.price,
            p.stock_quantity,
            (c.quantity * p.price) as total_price
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.customer_id = %s AND p.is_active = TRUE
        """
        cart_items = db.execute_query(cart_query, (customer_id,), fetch=True)
        print(f"Cart items for checkout: {cart_items}")
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400

        # Check stock availability
        for item in cart_items:
            if item['stock_quantity'] < item['quantity']:
                return jsonify({
                    'error': f'Insufficient stock for {item["product_name"]}. Available: {item["stock_quantity"]}'
                }), 400

        # Calculate totals
        subtotal = sum(float(item['total_price']) for item in cart_items)
        tax_rate = 0.08  # 8% tax
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount

        print(f"Order totals: subtotal={subtotal}, tax={tax_amount}, total={total_amount}")

        # Generate order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{customer_id}-{int(datetime.now().timestamp())}"
        print(f"Generated order number: {order_number}")

        # Create order
        order_query = """
        INSERT INTO orders (
            customer_id, store_id, employee_id, order_number, 
            payment_method, subtotal, tax_amount, total_amount, 
            shipping_address, order_status, payment_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', 'PENDING')
        """
        order_params = (
            customer_id, store_id, employee_id, order_number,
            payment_method, subtotal, tax_amount, total_amount, shipping_address
        )
        
        print(f"Creating order with params: {order_params}")
        order_id = db.execute_query(order_query, order_params)
        print(f"Order created with ID: {order_id}")

        # Create order items and update stock
        for item in cart_items:
            print(f"Processing cart item: {item}")
            # Insert order item
            order_item_query = """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
            VALUES (%s, %s, %s, %s, %s)
            """
            db.execute_query(order_item_query, (
                order_id, item['product_id'], item['quantity'], 
                item['price'], item['total_price']
            ))

            # Update product stock using stored procedure
            stock_update_query = "CALL update_product_stock(%s, %s, %s, %s, %s)"
            db.execute_query(stock_update_query, (
                item['product_id'], -item['quantity'], 'OUT', 
                employee_id, f'Sale - Order {order_number}'
            ))

        # Clear cart
        clear_cart_query = "DELETE FROM cart WHERE customer_id = %s"
        db.execute_query(clear_cart_query, (customer_id,))
        print(f"Cart cleared for customer {customer_id}")

        # Update order status to processing
        update_order_query = """
        UPDATE orders 
        SET order_status = 'PROCESSING', payment_status = 'PAID'
        WHERE order_id = %s
        """
        db.execute_query(update_order_query, (order_id,))
        print(f"Order {order_id} status updated to PROCESSING")

        return jsonify({
            'message': 'Order placed successfully',
            'order_id': order_id,
            'order_number': order_number,
            'total_amount': round(total_amount, 2)
        }), 201

    except Exception as e:
        print(f"Checkout error: {str(e)}")
        return jsonify({'error': str(e)}), 500