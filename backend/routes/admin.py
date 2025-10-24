from flask import Blueprint, jsonify, request
from db.db_config import DatabaseConfig
from routes.auth import require_auth
import json
from datetime import datetime

admin_bp = Blueprint('admin', __name__)
db = DatabaseConfig()

@admin_bp.route('/products', methods=['POST'])
@require_auth(['admin', 'manager'])
def admin_add_product():
    """Add a new product (Admin/Manager only)"""
    try:
        data = request.get_json()
        required_fields = ['product_name', 'category_id', 'supplier_id', 'brand', 'price', 'cost_price', 'stock_quantity']
        
        # Validate required fields
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate numeric fields
        try:
            price = float(data['price'])
            cost_price = float(data['cost_price'])
            stock_quantity = int(data['stock_quantity'])
            if price <= 0 or cost_price <= 0 or stock_quantity < 0:
                raise ValueError()
        except ValueError:
            return jsonify({'error': 'Invalid numeric values'}), 400
        
        # Check if category and supplier exist
        category_check = db.execute_query(
            "SELECT category_id FROM categories WHERE category_id = %s",
            (data['category_id'],), fetch=True
        )
        if not category_check:
            return jsonify({'error': 'Invalid category_id'}), 400
        
        supplier_check = db.execute_query(
            "SELECT supplier_id FROM suppliers WHERE supplier_id = %s",
            (data['supplier_id'],), fetch=True
        )
        if not supplier_check:
            return jsonify({'error': 'Invalid supplier_id'}), 400
        
        # Insert new product
        query = """
        INSERT INTO products (
            product_name, category_id, supplier_id, brand, model, description,
            price, cost_price, stock_quantity, weight, warranty_period
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['product_name'], data['category_id'], data['supplier_id'],
            data['brand'], data.get('model', ''), data.get('description', ''),
            price, cost_price, stock_quantity,
            data.get('weight', 0), data.get('warranty_period', 12)
        )
        
        result = db.execute_query(query, params)
        
        if result:
            return jsonify({
                'message': 'Product added successfully',
                'product_id': result
            }), 201
        else:
            return jsonify({'error': 'Failed to add product'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@require_auth(['admin', 'manager'])
def admin_update_product(product_id):
    """Update a product (Admin/Manager only)"""
    try:
        data = request.get_json()
        
        # Build dynamic update query
        update_fields = []
        params = []
        
        allowed_fields = [
            'product_name', 'category_id', 'supplier_id', 'brand', 'model',
            'description', 'price', 'cost_price', 'stock_quantity', 'weight',
            'warranty_period', 'is_active'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Add updated_at timestamp
        update_fields.append("updated_at = NOW()")
        params.append(product_id)
        
        query = f"""
        UPDATE products 
        SET {', '.join(update_fields)}
        WHERE product_id = %s
        """
        
        result = db.execute_query(query, params)
        
        if result:
            return jsonify({'message': 'Product updated successfully'}), 200
        else:
            return jsonify({'error': 'Product not found or update failed'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@require_auth(['admin'])
def admin_delete_product(product_id):
    """Soft delete a product (Admin only)"""
    try:
        query = "UPDATE products SET is_active = FALSE WHERE product_id = %s"
        result = db.execute_query(query, (product_id,))
        
        if result:
            return jsonify({'message': 'Product deactivated successfully'}), 200
        else:
            return jsonify({'error': 'Product not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/inventory/adjust', methods=['POST'])
@require_auth(['admin', 'manager'])
def admin_adjust_inventory():
    """Adjust product inventory (Admin/Manager only)"""
    try:
        data = request.get_json()
        required_fields = ['product_id', 'quantity_change', 'reason']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        product_id = data['product_id']
        quantity_change = int(data['quantity_change'])
        reason = data['reason']
        
        # Get current stock
        current_stock_query = "SELECT stock_quantity FROM products WHERE product_id = %s"
        current_stock_result = db.execute_query(current_stock_query, (product_id,), fetch=True)
        
        if not current_stock_result:
            return jsonify({'error': 'Product not found'}), 404
        
        current_stock = current_stock_result[0]['stock_quantity']
        new_stock = current_stock + quantity_change
        
        if new_stock < 0:
            return jsonify({'error': 'Insufficient stock for this adjustment'}), 400
        
        # Update product stock
        update_query = "UPDATE products SET stock_quantity = %s WHERE product_id = %s"
        db.execute_query(update_query, (new_stock, product_id))
        
        # Log the inventory change
        log_query = """
        INSERT INTO inventory_logs (
            product_id, transaction_type, quantity_change, 
            previous_quantity, new_quantity, reason
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        transaction_type = 'IN' if quantity_change > 0 else 'OUT'
        db.execute_query(log_query, (
            product_id, transaction_type, quantity_change,
            current_stock, new_stock, reason
        ))
        
        return jsonify({
            'message': 'Inventory adjusted successfully',
            'previous_stock': current_stock,
            'new_stock': new_stock
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@require_auth(['admin', 'manager'])
def admin_update_order_status(order_id):
    """Update order status (Admin/Manager only)"""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED']
        if data['status'] not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        query = "UPDATE orders SET order_status = %s, updated_at = NOW() WHERE order_id = %s"
        result = db.execute_query(query, (data['status'], order_id))
        
        if result:
            return jsonify({'message': 'Order status updated successfully'}), 200
        else:
            return jsonify({'error': 'Order not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/dashboard', methods=['GET'])
@require_auth(['admin', 'manager'])
def admin_dashboard_analytics():
    """Get dashboard analytics (Admin/Manager only)"""
    try:
        # Total products
        total_products = db.execute_query(
            "SELECT COUNT(*) as count FROM products WHERE is_active = TRUE",
            fetch=True
        )[0]['count']
        
        # Total customers
        total_customers = db.execute_query(
            "SELECT COUNT(*) as count FROM customers WHERE is_active = TRUE",
            fetch=True
        )[0]['count']
        
        # Total orders today
        total_orders_today = db.execute_query(
            "SELECT COUNT(*) as count FROM orders WHERE DATE(created_at) = CURDATE()",
            fetch=True
        )[0]['count']
        
        # Total revenue today
        revenue_today = db.execute_query(
            "SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders WHERE DATE(created_at) = CURDATE() AND payment_status = 'PAID'",
            fetch=True
        )[0]['revenue']
        
        # Low stock products
        low_stock_products = db.execute_query(
            """
            SELECT p.product_name, p.stock_quantity, p.min_stock_level
            FROM products p 
            WHERE p.stock_quantity <= p.min_stock_level AND p.is_active = TRUE
            ORDER BY p.stock_quantity ASC
            LIMIT 10
            """,
            fetch=True
        )
        
        # Recent orders
        recent_orders = db.execute_query(
            """
            SELECT o.order_id, o.order_number, o.order_status, o.total_amount,
                   c.first_name, c.last_name, o.created_at
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            ORDER BY o.created_at DESC
            LIMIT 10
            """,
            fetch=True
        )
        
        return jsonify({
            'total_products': total_products,
            'total_customers': total_customers,
            'total_orders_today': total_orders_today,
            'revenue_today': float(revenue_today),
            'low_stock_products': low_stock_products,
            'recent_orders': recent_orders
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/customers', methods=['GET'])
@require_auth(['admin'])
def admin_get_customers():
    """Get all customers (Admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '')
        
        offset = (page - 1) * limit
        
        # Build search condition
        search_condition = ""
        search_params = []
        
        if search:
            search_condition = """
            WHERE (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)
            """
            search_term = f"%{search}%"
            search_params = [search_term, search_term, search_term]
        
        # Get customers
        query = f"""
        SELECT customer_id, first_name, last_name, email, phone, city, state,
               registration_date, total_spent, loyalty_points, is_active, last_login
        FROM customers
        {search_condition}
        ORDER BY registration_date DESC
        LIMIT %s OFFSET %s
        """
        
        params = search_params + [limit, offset]
        customers = db.execute_query(query, params, fetch=True)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM customers {search_condition}"
        total_count = db.execute_query(count_query, search_params, fetch=True)[0]['total']
        
        return jsonify({
            'customers': customers,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500