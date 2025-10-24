from flask import Blueprint, jsonify, request
from db.db_config import DatabaseConfig
import os
import re

ai_query_bp = Blueprint('ai_query', __name__)
db = DatabaseConfig()

class TextToSQLConverter:
    def __init__(self):
        # HuggingFace configuration (OPTIONAL)
        self.hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
        
        # Set to True ONLY if you want AI fallback for unrecognized queries
        # Current pattern matching handles 90%+ of queries better/faster
        self.use_ai_model = bool(self.hf_token)  # Auto-enable if token exists
        
        if self.hf_token and self.use_ai_model:
            self.api_url = "https://api-inference.huggingface.co/models/mrm8488/t5-base-finetuned-wikiSQL"
            print("✅ HuggingFace API enabled (fallback mode)")
        else:
            self.api_url = None
            print("ℹ️  Running in pattern-matching mode (recommended)")
        
        # Database schema information
        self.schema_info = self._get_schema_info()
        
    def _get_schema_info(self):
        """Get database schema information for context"""
        return """
        Database Schema for Electronics Store:
        
        TABLES:
        - stores: store_id, store_name, address, city, state, manager_name
        - employees: employee_id, store_id, first_name, last_name, email, position, salary, hire_date
        - customers: customer_id, first_name, last_name, email, phone, total_spent, loyalty_points, registration_date
        - suppliers: supplier_id, company_name, contact_person, email, established_year, rating
        - categories: category_id, category_name, parent_category_id, description
        - products: product_id, product_name, category_id, supplier_id, brand, model, price, cost_price, stock_quantity, warranty_period, created_at
        - orders: order_id, customer_id, store_id, employee_id, order_number, order_date, order_status, payment_method, subtotal, tax_amount, total_amount
        - order_items: item_id, order_id, product_id, quantity, unit_price, total_price
        - banking_accounts: account_id, customer_id, account_number, account_type, balance, credit_limit
        - banking_transactions: transaction_id, account_id, transaction_type, amount, balance_after, description, transaction_date
        - product_reviews: review_id, product_id, customer_id, rating, review_text, created_at
        - inventory_logs: log_id, product_id, store_id, transaction_type, quantity_change, transaction_date
        """

    def convert_to_sql(self, natural_query):
        """
        Convert natural language to SQL
        1. First tries pattern matching (fast, reliable)
        2. Falls back to AI if pattern fails AND token available
        """
        natural_query_lower = natural_query.lower().strip()
        
        # Try pattern matching first (recommended)
        sql_query = self._try_pattern_matching(natural_query_lower)
        
        # If pattern matching found a match, use it
        if sql_query and "Query not recognized" not in sql_query:
            return sql_query
        
        # If pattern failed and AI is enabled, try AI
        if self.use_ai_model and self.hf_token:
            print(f"⚡ Pattern not found, trying AI for: {natural_query}")
            try:
                ai_sql = self._try_huggingface_api(natural_query)
                if ai_sql and self._validate_sql(ai_sql):
                    print(f"✅ AI generated SQL successfully")
                    return ai_sql
                else:
                    print(f"⚠️ AI generated invalid SQL, using fallback")
            except Exception as e:
                print(f"❌ AI API failed: {e}")
        
        # Final fallback
        return self._create_fallback_query(natural_query)
    
    def _try_pattern_matching(self, query):
        """Try all pattern matching templates - improved with better matching"""
        
        # Check for customer queries
        if any(word in query for word in ['customer', 'customers']) and any(word in query for word in ['top', 'best', 'spending', 'spend']):
            return self._get_top_customers_query(query)
        
        # Check for product sales/selling queries
        if any(word in query for word in ['product', 'products']) and any(word in query for word in ['top', 'best', 'selling', 'sold', 'popular']):
            return self._get_top_products_query(query)
        
        # Check for reviews
        if 'review' in query or 'rating' in query:
            return self._get_product_reviews_query(query)
        
        # Check for sales queries
        if ('sales' in query or 'revenue' in query) and 'total' in query:
            return self._get_total_sales_query(query)
        
        # Check for stock queries
        if 'low stock' in query or 'stock' in query and 'low' in query:
            return self._get_low_stock_query(query)
        
        if 'out of stock' in query or ('stock' in query and ('out' in query or 'empty' in query)):
            return self._get_out_of_stock_query(query)
        
        # Check for price queries
        if 'expensive' in query or 'costly' in query or ('price' in query and ('high' in query or 'top' in query)):
            return self._get_expensive_products_query(query)
        
        if 'cheap' in query or 'affordable' in query or ('price' in query and 'low' in query):
            return self._get_cheap_products_query(query)
        
        # Check for correlation/analysis
        if 'correlation' in query or ('price' in query and ('sales' in query or 'volume' in query)):
            return self._get_price_volume_correlation_query(query)
        
        if 'better than average' in query or 'above average' in query:
            return self._get_above_average_sales_query(query)
        
        # Check for banking
        if 'banking' in query or 'transaction' in query:
            return self._get_banking_transactions_query(query)
        
        if 'account' in query and 'balance' in query:
            return self._get_account_balances_query(query)
        
        # Check for employees
        if 'employee' in query or 'staff' in query:
            return self._get_employee_performance_query(query)
        
        if 'store' in query and 'performance' in query:
            return self._get_store_performance_query(query)
        
        # Check for payment methods
        if 'payment' in query:
            return self._get_payment_methods_query(query)
        
        # Check for inventory
        if 'inventory' in query:
            return self._get_inventory_value_query(query)
        
        # Check for categories
        if 'category' in query or 'categories' in query:
            return self._get_sales_by_category_query(query)
        
        # Check for new customers
        if 'new' in query and 'customer' in query:
            return self._get_new_customers_query(query)
        
        # Check for orders
        if 'order' in query and 'customer' in query:
            return self._get_customer_orders_query(query)
        
        # Default patterns (keep existing ones as fallback)
        sql_templates = {
            # Sales queries
            'total sales': self._get_total_sales_query,
            'sales by date': self._get_sales_by_date_query,
            'sales by month': self._get_sales_by_month_query,
            'sales by product': self._get_sales_by_product_query,
            'sales by category': self._get_sales_by_category_query,
            
            # Customer queries  
            'top customers': self._get_top_customers_query,
            'customer orders': self._get_customer_orders_query,
            'customer spending': self._get_customer_spending_query,
            'new customers': self._get_new_customers_query,
            
            # Product queries
            'low stock': self._get_low_stock_query,
            'out of stock': self._get_out_of_stock_query,
            'top products': self._get_top_products_query,
            'selling better': self._get_above_average_sales_query,
            'best selling': self._get_top_products_query,
            'product reviews': self._get_product_reviews_query,
            'expensive products': self._get_expensive_products_query,
            'cheap products': self._get_cheap_products_query,
            'price and sales': self._get_price_volume_correlation_query,
            'correlation': self._get_price_volume_correlation_query,
            
            # Inventory queries
            'inventory value': self._get_inventory_value_query,
            'stock movements': self._get_stock_movements_query,
            
            # Financial queries
            'banking transactions': self._get_banking_transactions_query,
            'account balances': self._get_account_balances_query,
            'payment methods': self._get_payment_methods_query,
            
            # Employee queries
            'employee performance': self._get_employee_performance_query,
            'store performance': self._get_store_performance_query,
        }
        
        # Try to match query patterns
        for pattern, template_func in sql_templates.items():
            if pattern in query:
                return template_func(query)
        
        # If no pattern matches, try advanced matching
        advanced_result = self._advanced_pattern_matching(query)
        return advanced_result
    
    def _try_huggingface_api(self, natural_query):
        """Try to generate SQL using Hugging Face API"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        
        # Provide database context
        prompt = f"""Given this database schema:
{self.schema_info}

Convert this question to SQL:
Question: {natural_query}

SQL:"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.1,
                "do_sample": False
            },
            "options": {
                "wait_for_model": True
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Extract SQL from response
                    sql = self._extract_sql(generated_text, prompt)
                    return sql
            else:
                print(f"API returned status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"HuggingFace API error: {e}")
        
        return None
    
    def _extract_sql(self, generated_text, prompt):
        """Extract SQL from AI-generated text"""
        # Remove the prompt from response
        sql = generated_text.replace(prompt, '').strip()
        
        # Remove markdown code blocks
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        # Extract only the SQL query
        lines = sql.split('\n')
        sql_lines = []
        for line in lines:
            if any(keyword in line.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE', 'JOIN']):
                sql_lines.append(line)
            elif sql_lines:  # Continue if we've started collecting SQL
                sql_lines.append(line)
        
        return '\n'.join(sql_lines).strip()
    
    def _validate_sql(self, sql):
        """Basic SQL validation"""
        if not sql or len(sql) < 10:
            return False
        
        # Must contain at least SELECT, INSERT, UPDATE, or DELETE
        sql_upper = sql.upper()
        if not any(keyword in sql_upper for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
            return False
        
        # Should not contain dangerous operations
        dangerous = ['DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE']
        if any(keyword in sql_upper for keyword in dangerous):
            return False
        
        return True

    def _get_total_sales_query(self, query):
        if 'last' in query and 'days' in query:
            days = self._extract_number(query, 30)
            return f"""
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(AVG(total_amount), 0) as average_order_value
            FROM orders 
            WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
            AND order_status = 'DELIVERED';
            """
        elif 'today' in query:
            return """
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(AVG(total_amount), 0) as average_order_value
            FROM orders 
            WHERE DATE(order_date) = CURDATE()
            AND order_status = 'DELIVERED';
            """
        else:
            return """
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(AVG(total_amount), 0) as average_order_value
            FROM orders 
            WHERE order_status = 'DELIVERED';
            """

    def _get_sales_by_date_query(self, query):
        return """
        SELECT 
            DATE(o.order_date) as sale_date,
            COUNT(*) as orders_count,
            SUM(o.total_amount) as daily_revenue,
            AVG(o.total_amount) as avg_order_value
        FROM orders o
        WHERE o.order_status = 'DELIVERED'
        AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY DATE(o.order_date)
        ORDER BY sale_date DESC;
        """

    def _get_sales_by_month_query(self, query):
        return """
        SELECT 
            YEAR(o.order_date) as year,
            MONTH(o.order_date) as month,
            MONTHNAME(o.order_date) as month_name,
            COUNT(*) as orders_count,
            SUM(o.total_amount) as monthly_revenue,
            AVG(o.total_amount) as avg_order_value
        FROM orders o
        WHERE o.order_status = 'DELIVERED'
        GROUP BY YEAR(o.order_date), MONTH(o.order_date)
        ORDER BY year DESC, month DESC;
        """

    def _get_sales_by_product_query(self, query):
        limit = self._extract_number(query, 10)
        return f"""
        SELECT 
            p.product_name,
            p.brand,
            c.category_name,
            SUM(oi.quantity) as total_sold,
            SUM(oi.total_price) as revenue,
            AVG(oi.unit_price) as avg_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE o.order_status = 'DELIVERED'
        GROUP BY p.product_id, p.product_name, p.brand, c.category_name
        ORDER BY total_sold DESC
        LIMIT {limit};
        """

    def _get_sales_by_category_query(self, query):
        return """
        SELECT 
            c.category_name,
            COUNT(DISTINCT p.product_id) as products_count,
            SUM(oi.quantity) as total_sold,
            SUM(oi.total_price) as category_revenue,
            AVG(p.price) as avg_product_price
        FROM categories c
        LEFT JOIN products p ON c.category_id = p.category_id
        LEFT JOIN order_items oi ON p.product_id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'DELIVERED'
        GROUP BY c.category_id, c.category_name
        HAVING category_revenue > 0
        ORDER BY category_revenue DESC;
        """

    def _get_top_customers_query(self, query):
        limit = self._extract_number(query, 10)
        return f"""
        SELECT 
            c.customer_id,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            c.email,
            COUNT(o.order_id) as total_orders,
            COALESCE(SUM(o.total_amount), 0) as total_spent,
            COALESCE(AVG(o.total_amount), 0) as avg_order_value,
            c.loyalty_points,
            MAX(o.order_date) as last_order_date
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status = 'DELIVERED'
        GROUP BY c.customer_id
        HAVING total_orders > 0
        ORDER BY total_spent DESC
        LIMIT {limit};
        """

    def _get_customer_orders_query(self, query):
        return """
        SELECT 
            o.order_id,
            o.order_number,
            o.order_date,
            o.order_status,
            o.total_amount,
            o.payment_method,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            COUNT(oi.item_id) as items_count
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.order_id
        ORDER BY o.order_date DESC
        LIMIT 50;
        """

    def _get_customer_spending_query(self, query):
        return """
        SELECT 
            c.customer_id,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            c.total_spent,
            c.loyalty_points,
            CASE 
                WHEN c.total_spent >= 5000 THEN 'VIP'
                WHEN c.total_spent >= 2000 THEN 'Premium'
                WHEN c.total_spent >= 500 THEN 'Regular'
                ELSE 'New'
            END as customer_tier,
            DATEDIFF(CURDATE(), c.registration_date) as days_since_registration
        FROM customers c
        ORDER BY c.total_spent DESC;
        """

    def _get_new_customers_query(self, query):
        days = self._extract_number(query, 30)
        return f"""
        SELECT 
            c.customer_id,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            c.email,
            c.registration_date,
            COALESCE(SUM(o.total_amount), 0) as total_spent,
            COUNT(o.order_id) as orders_count
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status = 'DELIVERED'
        WHERE c.registration_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        GROUP BY c.customer_id
        ORDER BY c.registration_date DESC;
        """

    def _get_low_stock_query(self, query):
        return """
        SELECT 
            p.product_id,
            p.product_name,
            p.brand,
            c.category_name,
            p.stock_quantity,
            p.min_stock_level,
            (p.min_stock_level - p.stock_quantity) as shortage,
            p.price,
            s.company_name as supplier
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE p.is_active = TRUE 
        AND p.stock_quantity <= p.min_stock_level
        ORDER BY shortage DESC, p.stock_quantity ASC;
        """

    def _get_out_of_stock_query(self, query):
        return """
        SELECT 
            p.product_id,
            p.product_name,
            p.brand,
            c.category_name,
            p.price,
            p.min_stock_level,
            s.company_name as supplier,
            p.updated_at as last_updated
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE p.is_active = TRUE 
        AND p.stock_quantity = 0
        ORDER BY p.updated_at DESC;
        """

    def _get_top_products_query(self, query):
        limit = self._extract_number(query, 10)
        if 'revenue' in query or 'sales' in query:
            return f"""
            SELECT 
                p.product_name,
                p.brand,
                c.category_name,
                SUM(oi.quantity) as units_sold,
                SUM(oi.total_price) as total_revenue,
                AVG(pr.rating) as avg_rating,
                COUNT(pr.review_id) as review_count
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN product_reviews pr ON p.product_id = pr.product_id
            WHERE o.order_status = 'DELIVERED'
            GROUP BY p.product_id
            ORDER BY total_revenue DESC
            LIMIT {limit};
            """
        else:
            return f"""
            SELECT 
                p.product_name,
                p.brand,
                c.category_name,
                SUM(oi.quantity) as units_sold,
                SUM(oi.total_price) as total_revenue,
                AVG(pr.rating) as avg_rating
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN product_reviews pr ON p.product_id = pr.product_id
            WHERE o.order_status = 'DELIVERED'
            GROUP BY p.product_id
            ORDER BY units_sold DESC
            LIMIT {limit};
            """

    def _get_product_reviews_query(self, query):
        return """
        SELECT 
            p.product_name,
            p.brand,
            AVG(pr.rating) as avg_rating,
            COUNT(pr.review_id) as review_count,
            MAX(pr.created_at) as latest_review
        FROM products p
        LEFT JOIN product_reviews pr ON p.product_id = pr.product_id
        WHERE p.is_active = TRUE
        GROUP BY p.product_id
        HAVING review_count > 0
        ORDER BY avg_rating DESC, review_count DESC;
        """

    def _get_expensive_products_query(self, query):
        limit = self._extract_number(query, 10)
        return f"""
        SELECT 
            p.product_name,
            p.brand,
            c.category_name,
            p.price,
            p.stock_quantity,
            (p.price - p.cost_price) as profit_margin,
            s.company_name as supplier
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE p.is_active = TRUE
        ORDER BY p.price DESC
        LIMIT {limit};
        """

    def _get_cheap_products_query(self, query):
        limit = self._extract_number(query, 10)
        return f"""
        SELECT 
            p.product_name,
            p.brand,
            c.category_name,
            p.price,
            p.stock_quantity,
            AVG(pr.rating) as avg_rating
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN product_reviews pr ON p.product_id = pr.product_id
        WHERE p.is_active = TRUE
        GROUP BY p.product_id
        ORDER BY p.price ASC
        LIMIT {limit};
        """
    
    def _get_above_average_sales_query(self, query):
        """Products selling better than average"""
        return """
        WITH product_sales AS (
            SELECT 
                p.product_id,
                p.product_name,
                p.brand,
                p.price,
                c.category_name,
                COUNT(oi.item_id) as times_sold,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.total_price) as revenue
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'DELIVERED'
            WHERE p.is_active = TRUE
            GROUP BY p.product_id
        ),
        avg_sales AS (
            SELECT AVG(total_quantity) as avg_quantity
            FROM product_sales
            WHERE total_quantity > 0
        )
        SELECT 
            ps.product_name,
            ps.brand,
            ps.category_name,
            ps.price,
            ps.total_quantity,
            ps.revenue,
            ROUND(ps.total_quantity - avg_sales.avg_quantity, 2) as above_average_by
        FROM product_sales ps
        CROSS JOIN avg_sales
        WHERE ps.total_quantity > avg_sales.avg_quantity
        ORDER BY ps.total_quantity DESC;
        """
    
    def _get_price_volume_correlation_query(self, query):
        """Analyze correlation between price and sales volume"""
        return """
        SELECT 
            p.product_id,
            p.product_name,
            p.brand,
            p.price,
            COALESCE(SUM(oi.quantity), 0) as units_sold,
            COALESCE(SUM(oi.total_price), 0) as revenue,
            CASE 
                WHEN p.price < 100 THEN 'Budget ($0-$100)'
                WHEN p.price < 500 THEN 'Mid-Range ($100-$500)'
                WHEN p.price < 1000 THEN 'Premium ($500-$1000)'
                ELSE 'Luxury ($1000+)'
            END as price_category,
            ROUND(p.price / NULLIF(SUM(oi.quantity), 0), 2) as price_per_unit_sold
        FROM products p
        LEFT JOIN order_items oi ON p.product_id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'DELIVERED'
        WHERE p.is_active = TRUE
        GROUP BY p.product_id
        ORDER BY units_sold DESC;
        """

    def _get_inventory_value_query(self, query):
        return """
        SELECT 
            c.category_name,
            COUNT(p.product_id) as product_count,
            SUM(p.stock_quantity) as total_quantity,
            SUM(p.stock_quantity * p.cost_price) as inventory_cost_value,
            SUM(p.stock_quantity * p.price) as inventory_retail_value,
            AVG(p.price) as avg_price
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.is_active = TRUE
        GROUP BY c.category_id, c.category_name
        ORDER BY inventory_retail_value DESC;
        """

    def _get_stock_movements_query(self, query):
        days = self._extract_number(query, 7)
        return f"""
        SELECT 
            il.transaction_date,
            p.product_name,
            p.brand,
            il.transaction_type,
            il.quantity_change,
            il.previous_quantity,
            il.new_quantity,
            il.reason,
            s.store_name
        FROM inventory_logs il
        JOIN products p ON il.product_id = p.product_id
        LEFT JOIN stores s ON il.store_id = s.store_id
        WHERE il.transaction_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        ORDER BY il.transaction_date DESC
        LIMIT 100;
        """

    def _get_banking_transactions_query(self, query):
        days = self._extract_number(query, 30)
        return f"""
        SELECT 
            bt.transaction_date,
            bt.transaction_type,
            bt.amount,
            bt.description,
            ba.account_number,
            ba.account_type,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            o.order_number
        FROM banking_transactions bt
        JOIN banking_accounts ba ON bt.account_id = ba.account_id
        JOIN customers c ON ba.customer_id = c.customer_id
        LEFT JOIN orders o ON bt.related_order_id = o.order_id
        WHERE bt.transaction_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        ORDER BY bt.transaction_date DESC
        LIMIT 50;
        """

    def _get_account_balances_query(self, query):
        return """
        SELECT 
            ba.account_number,
            ba.account_type,
            ba.balance,
            ba.credit_limit,
            CASE 
                WHEN ba.account_type = 'CREDIT' THEN ba.credit_limit + ba.balance
                ELSE ba.balance
            END as available_balance,
            CONCAT(c.first_name, ' ', c.last_name) as customer_name,
            c.email
        FROM banking_accounts ba
        JOIN customers c ON ba.customer_id = c.customer_id
        WHERE ba.account_status = 'ACTIVE'
        ORDER BY ba.balance DESC;
        """

    def _get_payment_methods_query(self, query):
        days = self._extract_number(query, 30)
        return f"""
        SELECT 
            o.payment_method,
            COUNT(*) as transaction_count,
            SUM(o.total_amount) as total_revenue,
            AVG(o.total_amount) as avg_transaction_amount,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders 
                  WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)), 2) as percentage
        FROM orders o
        WHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        AND o.order_status != 'CANCELLED'
        GROUP BY o.payment_method
        ORDER BY total_revenue DESC;
        """

    def _get_employee_performance_query(self, query):
        return """
        SELECT 
            e.employee_id,
            CONCAT(e.first_name, ' ', e.last_name) as employee_name,
            e.position,
            s.store_name,
            COUNT(o.order_id) as orders_handled,
            SUM(o.total_amount) as total_sales,
            AVG(o.total_amount) as avg_order_value,
            DATEDIFF(CURDATE(), e.hire_date) as days_employed
        FROM employees e
        LEFT JOIN orders o ON e.employee_id = o.employee_id AND o.order_status = 'DELIVERED'
        LEFT JOIN stores s ON e.store_id = s.store_id
        WHERE e.is_active = TRUE
        GROUP BY e.employee_id
        ORDER BY total_sales DESC;
        """

    def _get_store_performance_query(self, query):
        return """
        SELECT 
            s.store_id,
            s.store_name,
            s.city,
            s.state,
            COUNT(DISTINCT o.order_id) as total_orders,
            SUM(o.total_amount) as total_revenue,
            AVG(o.total_amount) as avg_order_value,
            COUNT(DISTINCT e.employee_id) as employee_count,
            COUNT(DISTINCT o.customer_id) as unique_customers
        FROM stores s
        LEFT JOIN orders o ON s.store_id = o.store_id AND o.order_status = 'DELIVERED'
        LEFT JOIN employees e ON s.store_id = e.store_id AND e.is_active = TRUE
        GROUP BY s.store_id
        ORDER BY total_revenue DESC;
        """

    def _advanced_pattern_matching(self, query):
        """Handle more complex queries using pattern matching"""
        
        # Join queries
        if any(word in query for word in ['join', 'with', 'along with', 'including']):
            return self._create_join_query(query)
        
        # Aggregate queries
        if any(word in query for word in ['average', 'sum', 'total', 'count', 'max', 'min']):
            return self._create_aggregate_query(query)
        
        # Default fallback query
        return self._create_fallback_query(query)

    def _create_join_query(self, query):
        """Create queries with joins based on entities mentioned"""
        if 'customer' in query and 'order' in query:
            return """
            SELECT 
                c.customer_id,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                o.order_number,
                o.order_date,
                o.total_amount,
                o.order_status
            FROM customers c
            INNER JOIN orders o ON c.customer_id = o.customer_id
            ORDER BY o.order_date DESC
            LIMIT 20;
            """
        elif 'product' in query and 'category' in query:
            return """
            SELECT 
                p.product_name,
                p.brand,
                p.price,
                c.category_name,
                p.stock_quantity
            FROM products p
            INNER JOIN categories c ON p.category_id = c.category_id
            WHERE p.is_active = TRUE
            ORDER BY p.product_name
            LIMIT 20;
            """
        else:
            return self._create_fallback_query(query)

    def _create_aggregate_query(self, query):
        """Create aggregate queries"""
        if 'average' in query and 'price' in query:
            return """
            SELECT 
                c.category_name,
                COUNT(p.product_id) as product_count,
                AVG(p.price) as average_price,
                MIN(p.price) as min_price,
                MAX(p.price) as max_price
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.is_active = TRUE
            GROUP BY c.category_id, c.category_name
            ORDER BY average_price DESC;
            """
        elif 'total' in query and ('sales' in query or 'revenue' in query):
            return """
            SELECT 
                SUM(total_amount) as total_revenue,
                COUNT(*) as total_orders,
                AVG(total_amount) as average_order_value
            FROM orders
            WHERE order_status = 'DELIVERED';
            """
        else:
            return self._create_fallback_query(query)

    def _extract_number(self, text, default=10):
        """Extract number from text, return default if not found"""
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else default

    def _create_fallback_query(self, query):
        """Default query when pattern matching fails"""
        return """
        SELECT 
            'Query not recognized' as message,
            'Try: total sales, top customers, low stock, etc.' as suggestion;
        """

@ai_query_bp.route('/query', methods=['POST'])
def process_natural_query():
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400

        natural_query = data['query'].strip()
        if not natural_query:
            return jsonify({'error': 'Query cannot be empty'}), 400

        # Initialize converter
        converter = TextToSQLConverter()
        
        # Convert natural language to SQL
        sql_query = converter.convert_to_sql(natural_query)
        
        if not sql_query or sql_query.strip() == '':
            return jsonify({'error': 'Could not generate SQL query'}), 400

        # Execute the query
        try:
            results = db.execute_query(sql_query, fetch=True)
            
            return jsonify({
                'natural_query': natural_query,
                'sql_query': sql_query,
                'results': results or [],
                'row_count': len(results) if results else 0
            })

        except Exception as db_error:
            return jsonify({
                'error': 'Database query failed',
                'natural_query': natural_query,
                'sql_query': sql_query,
                'db_error': str(db_error)
            }), 500

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@ai_query_bp.route('/suggestions', methods=['GET'])
def get_query_suggestions():
    """Get sample query suggestions"""
    suggestions = [
        "Show me total sales for last 30 days",
        "What are the top 10 customers by spending?",
        "List products with low stock",
        "Which products are selling better than average?",
        "Show me the best selling products",
        "What are the most expensive products?",
        "Which products have the best reviews?",
        "Show me out of stock products",
        "What's the correlation between price and sales?",
        "Show customer spending patterns",
        "List recent banking transactions",
        "Show employee performance metrics",
        "What's the inventory value by category?",
        "Show payment method usage",
        "List new customers this month",
        "Show store performance comparison",
        "What are sales by category?",
        "Show me cheap products under $100"
    ]
    
    return jsonify({'suggestions': suggestions})

@ai_query_bp.route('/schema', methods=['GET'])
def get_database_schema():
    """Get database schema information"""
    try:
        tables_query = """
        SELECT 
            TABLE_NAME,
            TABLE_COMMENT,
            TABLE_ROWS
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME;
        """
        
        columns_query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_KEY,
            COLUMN_COMMENT
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, ORDINAL_POSITION;
        """
        
        tables = db.execute_query(tables_query, fetch=True)
        columns = db.execute_query(columns_query, fetch=True)
        
        # Group columns by table
        schema_info = {}
        for table in tables or []:
            table_name = table['TABLE_NAME']
            schema_info[table_name] = {
                'table_info': table,
                'columns': []
            }
        
        for column in columns or []:
            table_name = column['TABLE_NAME']
            if table_name in schema_info:
                schema_info[table_name]['columns'].append(column)
        
        return jsonify({'schema': schema_info})

    except Exception as e:
        return jsonify({'error': str(e)}), 500