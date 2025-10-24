from flask import Blueprint, jsonify, request
from db.db_config import DatabaseConfig
import json

products_bp = Blueprint('products', __name__)
db = DatabaseConfig()

@products_bp.route('/', methods=['GET'])
def get_products():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        category = request.args.get('category')
        brand = request.args.get('brand')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'product_name')
        sort_order = request.args.get('sort_order', 'ASC')

        # Build WHERE clause
        where_conditions = ["p.is_active = TRUE"]
        params = []

        if category:
            where_conditions.append("c.category_name = %s")
            params.append(category)

        if brand:
            where_conditions.append("p.brand = %s")
            params.append(brand)

        if min_price:
            where_conditions.append("p.price >= %s")
            params.append(float(min_price))

        if max_price:
            where_conditions.append("p.price <= %s")
            params.append(float(max_price))

        if search:
            where_conditions.append("(p.product_name LIKE %s OR p.brand LIKE %s OR p.description LIKE %s)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        where_clause = " AND ".join(where_conditions)
        offset = (page - 1) * limit

        # Validate sort column
        allowed_sort_columns = ['product_name', 'price', 'brand', 'stock_quantity', 'created_at']
        if sort_by not in allowed_sort_columns:
            sort_by = 'product_name'

        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'ASC'

        query = f"""
        SELECT 
            p.product_id,
            p.product_name,
            p.brand,
            p.model,
            p.description,
            p.price,
            p.stock_quantity,
            p.weight,
            p.warranty_period,
            p.featured,
            c.category_name,
            s.company_name as supplier_name,
            COALESCE(AVG(pr.rating), 0) as avg_rating,
            COUNT(DISTINCT pr.review_id) as review_count,
            p.created_at
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN product_reviews pr ON p.product_id = pr.product_id
        WHERE {where_clause}
        GROUP BY p.product_id
        ORDER BY {sort_by} {sort_order}
        LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])
        products = db.execute_query(query, params, fetch=True)

        # Get total count
        count_query = f"""
        SELECT COUNT(DISTINCT p.product_id) as total
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE {where_clause}
        """
        
        total_result = db.execute_query(count_query, params[:-2], fetch=True)
        total = total_result[0]['total'] if total_result else 0

        return jsonify({
            'products': products,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        query = """
        SELECT 
            p.*,
            c.category_name,
            s.company_name as supplier_name,
            s.contact_person as supplier_contact,
            COALESCE(AVG(pr.rating), 0) as avg_rating,
            COUNT(DISTINCT pr.review_id) as review_count
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN product_reviews pr ON p.product_id = pr.product_id
        WHERE p.product_id = %s AND p.is_active = TRUE
        GROUP BY p.product_id
        """
        
        result = db.execute_query(query, (product_id,), fetch=True)
        
        if not result:
            return jsonify({'error': 'Product not found'}), 404

        product = result[0]

        # Get reviews
        reviews_query = """
        SELECT 
            pr.*,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name
        FROM product_reviews pr
        JOIN customers c ON pr.customer_id = c.customer_id
        WHERE pr.product_id = %s
        ORDER BY pr.created_at DESC
        LIMIT 10
        """
        
        reviews = db.execute_query(reviews_query, (product_id,), fetch=True)

        return jsonify({
            'product': product,
            'reviews': reviews or []
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        query = """
        SELECT 
            c.*,
            pc.category_name as parent_name,
            COUNT(p.product_id) as product_count
        FROM categories c
        LEFT JOIN categories pc ON c.parent_category_id = pc.category_id
        LEFT JOIN products p ON c.category_id = p.category_id AND p.is_active = TRUE
        WHERE c.is_active = TRUE
        GROUP BY c.category_id
        ORDER BY c.category_name
        """
        
        categories = db.execute_query(query, fetch=True)
        return jsonify({'categories': categories})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/brands', methods=['GET'])
def get_brands():
    try:
        query = """
        SELECT 
            p.brand,
            COUNT(*) as product_count,
            MIN(p.price) as min_price,
            MAX(p.price) as max_price,
            AVG(p.price) as avg_price
        FROM products p
        WHERE p.is_active = TRUE AND p.brand IS NOT NULL
        GROUP BY p.brand
        ORDER BY p.brand
        """
        
        brands = db.execute_query(query, fetch=True)
        return jsonify({'brands': brands})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/featured', methods=['GET'])
def get_featured_products():
    try:
        query = """
        SELECT 
            p.product_id,
            p.product_name,
            p.brand,
            p.price,
            p.stock_quantity,
            c.category_name,
            COALESCE(AVG(pr.rating), 0) as avg_rating,
            COUNT(DISTINCT pr.review_id) as review_count
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN product_reviews pr ON p.product_id = pr.product_id
        WHERE p.is_active = TRUE AND p.featured = TRUE
        GROUP BY p.product_id
        ORDER BY p.created_at DESC
        LIMIT 12
        """
        
        products = db.execute_query(query, fetch=True)
        return jsonify({'featured_products': products})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/search-suggestions', methods=['GET'])
def get_search_suggestions():
    try:
        query_term = request.args.get('q', '').strip()
        
        if not query_term or len(query_term) < 2:
            return jsonify({'suggestions': []})

        query = """
        SELECT DISTINCT p.product_name as suggestion, 'product' as type
        FROM products p
        WHERE p.is_active = TRUE AND p.product_name LIKE %s
        UNION
        SELECT DISTINCT p.brand as suggestion, 'brand' as type
        FROM products p
        WHERE p.is_active = TRUE AND p.brand LIKE %s
        UNION
        SELECT DISTINCT c.category_name as suggestion, 'category' as type
        FROM categories c
        WHERE c.is_active = TRUE AND c.category_name LIKE %s
        ORDER BY suggestion
        LIMIT 10
        """
        
        search_term = f"%{query_term}%"
        suggestions = db.execute_query(query, (search_term, search_term, search_term), fetch=True)
        return jsonify({'suggestions': suggestions or []})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/low-stock', methods=['GET'])
def get_low_stock_products():
    try:
        query = """
        SELECT 
            p.product_id,
            p.product_name,
            p.brand,
            p.stock_quantity,
            p.min_stock_level,
            c.category_name,
            (p.min_stock_level - p.stock_quantity) as shortage
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.is_active = TRUE AND p.stock_quantity <= p.min_stock_level
        ORDER BY shortage DESC, p.stock_quantity ASC
        """
        
        products = db.execute_query(query, fetch=True)
        return jsonify({'low_stock_products': products or []})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/analytics', methods=['GET'])
def get_product_analytics():
    try:
        print("Product analytics request received")
        
        # Get top selling products
        top_selling_query = """
        SELECT 
            p.product_id,
            p.product_name,
            p.brand,
            SUM(oi.quantity) as total_sold,
            SUM(oi.total_price) as revenue
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status IN ('PROCESSING', 'DELIVERED') AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY p.product_id
        ORDER BY total_sold DESC
        LIMIT 10
        """

        # Get category performance
        category_performance_query = """
        SELECT 
            c.category_name,
            COUNT(DISTINCT p.product_id) as product_count,
            SUM(oi.quantity) as total_sold,
            SUM(oi.total_price) as revenue,
            AVG(p.price) as avg_price
        FROM categories c
        JOIN products p ON c.category_id = p.category_id
        LEFT JOIN order_items oi ON p.product_id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status IN ('PROCESSING', 'DELIVERED')
        WHERE p.is_active = TRUE
        GROUP BY c.category_id, c.category_name
        ORDER BY revenue DESC
        """

        # Get inventory status
        inventory_query = """
        SELECT 
            COUNT(*) as total_products,
            SUM(CASE WHEN stock_quantity <= min_stock_level THEN 1 ELSE 0 END) as low_stock_count,
            SUM(CASE WHEN stock_quantity = 0 THEN 1 ELSE 0 END) as out_of_stock_count,
            AVG(stock_quantity) as avg_stock_level,
            SUM(stock_quantity * cost_price) as total_inventory_value
        FROM products 
        WHERE is_active = TRUE
        """

        top_selling = db.execute_query(top_selling_query, fetch=True)
        category_performance = db.execute_query(category_performance_query, fetch=True)
        inventory_stats = db.execute_query(inventory_query, fetch=True)

        print(f"Top selling products: {top_selling}")
        print(f"Category performance: {category_performance}")
        print(f"Inventory stats: {inventory_stats}")

        return jsonify({
            'top_selling_products': top_selling or [],
            'category_performance': category_performance or [],
            'inventory_statistics': inventory_stats[0] if inventory_stats else {}
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    try:
        query = """
        SELECT 
            supplier_id,
            company_name,
            contact_person,
            email,
            phone,
            rating
        FROM suppliers
        ORDER BY company_name
        """
        
        suppliers = db.execute_query(query, fetch=True)
        return jsonify({'suppliers': suppliers})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ADMIN PRODUCT MANAGEMENT ROUTES

@products_bp.route('/admin', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        print(f"Product creation request data: {data}")
        
        # Validate required fields
        required_fields = ['product_name', 'category_id', 'supplier_id', 'price', 'stock_quantity']
        for field in required_fields:
            if field not in data:
                print(f"Missing required field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Convert string values to appropriate types
        try:
            price = float(data['price'])
            cost_price = float(data.get('cost_price', 0)) if data.get('cost_price') else price * 0.75
            stock_quantity = int(data['stock_quantity'])
            weight = float(data.get('weight', 0)) if data.get('weight') else None
            warranty_period = int(data.get('warranty_period', 12))
            category_id = int(data['category_id'])
            supplier_id = int(data['supplier_id'])
        except (ValueError, TypeError) as e:
            print(f"Type conversion error: {e}")
            return jsonify({'error': 'Invalid data types for numeric fields'}), 400

        query = """
        INSERT INTO products (
            product_name, category_id, supplier_id, brand, model, 
            description, price, cost_price, stock_quantity, 
            weight, warranty_period, featured
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['product_name'],
            category_id,
            supplier_id,
            data.get('brand', ''),
            data.get('model', ''),
            data.get('description', ''),
            price,
            cost_price,
            stock_quantity,
            weight,
            warranty_period,
            data.get('featured', False)
        )
        
        print(f"Product creation params: {params}")
        result = db.execute_query(query, params)
        print(f"Product creation result: {result}")
        
        if result:
            return jsonify({
                'message': 'Product created successfully',
                'product_id': result
            }), 201
        else:
            return jsonify({'error': 'Failed to create product'}), 500

    except Exception as e:
        print(f"Product creation error: {e}")
        import traceback
        print(f"Product creation traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@products_bp.route('/admin/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        allowed_fields = [
            'product_name', 'category_id', 'supplier_id', 'brand', 'model',
            'description', 'price', 'cost_price', 'stock_quantity', 
            'weight', 'warranty_period', 'featured', 'is_active'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        params.append(product_id)
        
        query = f"""
        UPDATE products 
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE product_id = %s
        """
        
        result = db.execute_query(query, params)
        
        if result is not None:
            return jsonify({'message': 'Product updated successfully'})
        else:
            return jsonify({'error': 'Product not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/admin/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        # Soft delete - set is_active to FALSE
        query = """
        UPDATE products 
        SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
        WHERE product_id = %s
        """
        
        result = db.execute_query(query, (product_id,))
        
        if result is not None:
            return jsonify({'message': 'Product deleted successfully'})
        else:
            return jsonify({'error': 'Product not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/admin/stock/<int:product_id>', methods=['PUT'])
def update_stock(product_id):
    try:
        data = request.get_json()
        
        if 'quantity_change' not in data:
            return jsonify({'error': 'quantity_change is required'}), 400
        
        quantity_change = int(data['quantity_change'])
        transaction_type = data.get('transaction_type', 'ADJUSTMENT')
        reason = data.get('reason', 'Manual stock adjustment')
        employee_id = data.get('employee_id', 1)  # Default admin employee
        
        # Call stored procedure to update stock
        query = "CALL update_product_stock(%s, %s, %s, %s, %s)"
        params = (product_id, quantity_change, transaction_type, employee_id, reason)
        
        db.execute_query(query, params)
        
        return jsonify({'message': 'Stock updated successfully'})

    except Exception as e:
        if 'Insufficient stock' in str(e):
            return jsonify({'error': 'Insufficient stock'}), 400
        return jsonify({'error': str(e)}), 500