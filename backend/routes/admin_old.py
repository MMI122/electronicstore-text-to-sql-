from flask import Blueprint, jsonify, request
from db.db_config import DatabaseConfig
from routes.auth import require_auth
import json
from datetime import datetime

admin_bp = Blueprint('admin', __name__)
db = DatabaseConfig()

@admin_bp.route('/products', methods=['POST'])
@require_auth(['admin', 'employee'])
def add_product():
    """Add a new product (Admin/Employee only)"""
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
            specifications, price, cost_price, stock_quantity, min_stock_level,
            max_stock_level, weight, dimensions, color, warranty_period, featured
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Prepare specifications as JSON
        specifications = data.get('specifications', {})
        if isinstance(specifications, dict):
            specifications = json.dumps(specifications)
        
        params = (
            data['product_name'], data['category_id'], data['supplier_id'],
            data['brand'], data.get('model', ''), data.get('description', ''),
            specifications, price, cost_price, stock_quantity,
            data.get('min_stock_level', 10), data.get('max_stock_level', 1000),
            data.get('weight'), data.get('dimensions', ''), data.get('color', ''),
            data.get('warranty_period', 12), data.get('featured', False)
        )
        
        product_id = db.execute_query(query, params)
        
        if product_id:
            # Log inventory addition
            log_query = """
            INSERT INTO inventory_logs (
                product_id, store_id, transaction_type, quantity_change,
                previous_quantity, new_quantity, reason, employee_id
            ) VALUES (%s, %s, 'IN', %s, 0, %s, 'Initial stock', %s)
            """
            db.execute_query(log_query, (product_id, 1, stock_quantity, stock_quantity, request.user_id))
            
            return jsonify({
                'message': 'Product added successfully',
                'product_id': product_id
            }), 201
        else:
            return jsonify({'error': 'Failed to add product'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@require_auth(['admin', 'employee'])
def update_product(product_id):
    """Update product information (Admin/Employee only)"""
    try:
        data = request.get_json()
        
        # Check if product exists
        existing_product = db.execute_query(
            "SELECT * FROM products WHERE product_id = %s",
            (product_id,), fetch=True
        )
        if not existing_product:
            return jsonify({'error': 'Product not found'}), 404
        
        current_product = existing_product[0]
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        # Fields that can be updated
        updatable_fields = [
            'product_name', 'category_id', 'supplier_id', 'brand', 'model',
            'description', 'specifications', 'price', 'cost_price', 'stock_quantity',
            'min_stock_level', 'max_stock_level', 'weight', 'dimensions',
            'color', 'warranty_period', 'featured', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'specifications' and isinstance(data[field], dict):
                    update_fields.append(f"{field} = %s")
                    params.append(json.dumps(data[field]))
                elif field in ['price', 'cost_price']:
                    # Validate numeric fields
                    try:
                        value = float(data[field])
                        if value <= 0:
                            return jsonify({'error': f'{field} must be positive'}), 400
                        update_fields.append(f"{field} = %s")
                        params.append(value)
                    except ValueError:
                        return jsonify({'error': f'Invalid {field} value'}), 400
                elif field == 'stock_quantity':
                    # Handle stock quantity change separately for logging
                    try:
                        new_quantity = int(data[field])
                        if new_quantity < 0:
                            return jsonify({'error': 'Stock quantity cannot be negative'}), 400
                        
                        old_quantity = current_product['stock_quantity']
                        quantity_change = new_quantity - old_quantity
                        
                        update_fields.append(f"{field} = %s")
                        params.append(new_quantity)
                        
                        # Log inventory change if quantity changed
                        if quantity_change != 0:
                            transaction_type = 'IN' if quantity_change > 0 else 'OUT'
                            log_query = """
                            INSERT INTO inventory_logs (
                                product_id, store_id, transaction_type, quantity_change,
                                previous_quantity, new_quantity, reason, employee_id
                            ) VALUES (%s, %s, %s, %s, %s, %s, 'Admin stock adjustment', %s)
                            """
                            db.execute_query(log_query, (
                                product_id, 1, transaction_type, abs(quantity_change),
                                old_quantity, new_quantity, request.user_id
                            ))
                            
                    except ValueError:
                        return jsonify({'error': 'Invalid stock quantity value'}), 400
                else:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Add updated_at timestamp
        update_fields.append("updated_at = NOW()")
        params.append(product_id)
        
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = %s"
        result = db.execute_query(query, params)
        
        if result:
            return jsonify({'message': 'Product updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update product'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@require_auth(['admin'])
def delete_product(product_id):
    """Soft delete a product (Admin only)"""
    try:
        # Check if product exists
        existing_product = db.execute_query(
            "SELECT product_id, product_name FROM products WHERE product_id = %s",
            (product_id,), fetch=True
        )
        if not existing_product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product has pending orders
        pending_orders = db.execute_query("""
            SELECT COUNT(*) as count FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s AND o.order_status IN ('PENDING', 'PROCESSING')
        """, (product_id,), fetch=True)
        
        if pending_orders and pending_orders[0]['count'] > 0:
            return jsonify({'error': 'Cannot delete product with pending orders. Mark as inactive instead.'}), 400
        
        # Soft delete (mark as inactive)
        query = "UPDATE products SET is_active = FALSE, updated_at = NOW() WHERE product_id = %s"
        result = db.execute_query(query, (product_id,))
        
        if result:
            return jsonify({'message': 'Product deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete product'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>/restore', methods=['PUT'])
@require_auth(['admin'])
def restore_product(product_id):
    """Restore a deleted product (Admin only)"""
    try:
        query = "UPDATE products SET is_active = TRUE, updated_at = NOW() WHERE product_id = %s"
        result = db.execute_query(query, (product_id,))
        
        if result:
            return jsonify({'message': 'Product restored successfully'}), 200
        else:
            return jsonify({'error': 'Failed to restore product or product not found'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/inventory/adjust', methods=['POST'])
@require_auth(['admin', 'employee'])
def adjust_inventory():
    """Adjust product inventory (Admin/Employee only)"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        adjustment = data.get('adjustment')  # Can be positive or negative
        reason = data.get('reason', 'Manual adjustment')
        
        if not product_id or adjustment is None:
            return jsonify({'error': 'product_id and adjustment are required'}), 400
        
        try:
            adjustment = int(adjustment)
        except ValueError:
            return jsonify({'error': 'adjustment must be an integer'}), 400
        
        # Get current stock
        current_stock_result = db.execute_query(
            "SELECT stock_quantity FROM products WHERE product_id = %s AND is_active = TRUE",
            (product_id,), fetch=True
        )
        
        if not current_stock_result:
            return jsonify({'error': 'Product not found or inactive'}), 404
        
        current_stock = current_stock_result[0]['stock_quantity']
        new_stock = current_stock + adjustment
        
        if new_stock < 0:
            return jsonify({'error': 'Adjustment would result in negative stock'}), 400
        
        # Update stock using stored procedure
        try:
            query = "CALL update_product_stock(%s, %s, %s, %s, %s)"
            transaction_type = 'IN' if adjustment > 0 else 'OUT'
            db.execute_query(query, (product_id, adjustment, transaction_type, request.user_id, reason))
            
            return jsonify({
                'message': 'Inventory adjusted successfully',
                'previous_stock': current_stock,
                'adjustment': adjustment,
                'new_stock': new_stock
            }), 200
            
        except Exception as e:
            if "Insufficient stock" in str(e):
                return jsonify({'error': 'Insufficient stock for this adjustment'}), 400
            raise e
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@require_auth(['admin', 'employee'])
def update_order_status(order_id):
    """Update order status (Admin/Employee only)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        valid_statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        # Check if order exists
        order_check = db.execute_query(
            "SELECT order_id, order_status FROM orders WHERE order_id = %s",
            (order_id,), fetch=True
        )
        if not order_check:
            return jsonify({'error': 'Order not found'}), 404
        
        current_status = order_check[0]['order_status']
        
        # Validate status transition
        if current_status == 'DELIVERED' and new_status not in ['RETURNED']:
            return jsonify({'error': 'Cannot change status of delivered order except to returned'}), 400
        
        if current_status == 'CANCELLED':
            return jsonify({'error': 'Cannot change status of cancelled order'}), 400
        
        # Update order status
        query = "UPDATE orders SET order_status = %s, updated_at = NOW() WHERE order_id = %s"
        result = db.execute_query(query, (new_status, order_id))
        
        if result:
            # If order is cancelled, restore stock
            if new_status == 'CANCELLED' and current_status != 'CANCELLED':
                restore_stock_query = """
                UPDATE products p
                INNER JOIN order_items oi ON p.product_id = oi.product_id
                SET p.stock_quantity = p.stock_quantity + oi.quantity
                WHERE oi.order_id = %s
                """
                db.execute_query(restore_stock_query, (order_id,))
                
                # Log inventory restoration
                log_items_query = """
                INSERT INTO inventory_logs (product_id, store_id, transaction_type, quantity_change, 
                                         previous_quantity, new_quantity, reason, reference_id, employee_id)
                SELECT oi.product_id, 1, 'IN', oi.quantity, 
                       p.stock_quantity - oi.quantity, p.stock_quantity, 
                       'Order cancelled - stock restored', %s, %s
                FROM order_items oi
                INNER JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
                """
                db.execute_query(log_items_query, (order_id, request.user_id, order_id))
            
            return jsonify({'message': 'Order status updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update order status'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/dashboard', methods=['GET'])
@require_auth(['admin', 'employee'])
def admin_dashboard():
    """Get admin dashboard analytics"""
    try:
        # Get various analytics data
        analytics = {}
        
        # Product statistics
        product_stats = db.execute_query("""
            SELECT 
                COUNT(*) as total_products,
                COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_products,
                COUNT(CASE WHEN stock_quantity <= min_stock_level THEN 1 END) as low_stock_products,
                COUNT(CASE WHEN stock_quantity = 0 THEN 1 END) as out_of_stock_products,
                SUM(stock_quantity * cost_price) as total_inventory_value
            FROM products
        """, fetch=True)
        
        analytics['products'] = product_stats[0] if product_stats else {}
        
        # Order statistics (last 30 days)
        order_stats = db.execute_query("""
            SELECT 
                COUNT(*) as total_orders,
                COUNT(CASE WHEN order_status = 'PENDING' THEN 1 END) as pending_orders,
                COUNT(CASE WHEN order_status = 'PROCESSING' THEN 1 END) as processing_orders,
                COUNT(CASE WHEN order_status = 'DELIVERED' THEN 1 END) as delivered_orders,
                COUNT(CASE WHEN order_status = 'CANCELLED' THEN 1 END) as cancelled_orders,
                COALESCE(SUM(CASE WHEN order_status = 'DELIVERED' THEN total_amount END), 0) as total_revenue
            FROM orders 
            WHERE order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, fetch=True)
        
        analytics['orders'] = order_stats[0] if order_stats else {}
        
        # Customer statistics
        customer_stats = db.execute_query("""
            SELECT 
                COUNT(*) as total_customers,
                COUNT(CASE WHEN registration_date >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as new_customers_30d,
                COUNT(CASE WHEN last_login >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as active_customers_7d
            FROM customers
            WHERE is_active = TRUE
        """, fetch=True)
        
        analytics['customers'] = customer_stats[0] if customer_stats else {}
        
        # Recent low stock alerts
        low_stock_products = db.execute_query("""
            SELECT product_id, product_name, brand, stock_quantity, min_stock_level
            FROM products 
            WHERE stock_quantity <= min_stock_level AND is_active = TRUE
            ORDER BY stock_quantity ASC
            LIMIT 10
        """, fetch=True)
        
        analytics['low_stock_alerts'] = low_stock_products or []
        
        # Recent orders
        recent_orders = db.execute_query("""
            SELECT o.order_id, o.order_number, o.order_status, o.total_amount, o.order_date,
                   CONCAT(c.first_name, ' ', c.last_name) as customer_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            ORDER BY o.order_date DESC
            LIMIT 10
        """, fetch=True)
        
        analytics['recent_orders'] = recent_orders or []
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/customers', methods=['GET'])
@require_auth(['admin'])
def get_customers():
    """Get all customers (Admin only)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')
        
        offset = (page - 1) * limit
        
        where_clause = "WHERE 1=1"
        params = []
        
        if search:
            where_clause += " AND (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        query = f"""
            SELECT customer_id, first_name, last_name, email, phone, city, state,
                   total_spent, loyalty_points, registration_date, last_login, is_active
            FROM customers
            {where_clause}
            ORDER BY registration_date DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        customers = db.execute_query(query, params, fetch=True)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM customers {where_clause}"
        total_result = db.execute_query(count_query, params[:-2], fetch=True)
        total = total_result[0]['total'] if total_result else 0
        
        return jsonify({
            'customers': customers or [],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500