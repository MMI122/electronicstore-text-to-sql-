-- Drop existing tables if they exist
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS banking_transactions;
DROP TABLE IF EXISTS banking_accounts;
DROP TABLE IF EXISTS product_reviews;
DROP TABLE IF EXISTS inventory_logs;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS stores;

-- Create stores table
CREATE TABLE stores (
    store_id INT PRIMARY KEY AUTO_INCREMENT,
    store_name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    zipcode VARCHAR(10),
    phone VARCHAR(20),
    manager_name VARCHAR(100),
    established_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create employees table
CREATE TABLE employees (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    store_id INT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    position VARCHAR(50),
    salary DECIMAL(10,2),
    hire_date DATE,
    department VARCHAR(50),
    manager_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

-- Create customers table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    zipcode VARCHAR(10),
    date_of_birth DATE,
    gender ENUM('M', 'F', 'Other'),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    total_spent DECIMAL(12,2) DEFAULT 0,
    loyalty_points INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create suppliers table
CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50),
    established_year YEAR,
    rating DECIMAL(3,2),
    payment_terms VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    parent_category_id INT,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- Create products table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(200) NOT NULL,
    category_id INT,
    supplier_id INT,
    brand VARCHAR(100),
    model VARCHAR(100),
    description TEXT,
    specifications JSON,
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    stock_quantity INT DEFAULT 0,
    min_stock_level INT DEFAULT 10,
    max_stock_level INT DEFAULT 1000,
    weight DECIMAL(8,2),
    dimensions VARCHAR(100),
    color VARCHAR(50),
    warranty_period INT, -- in months
    is_active BOOLEAN DEFAULT TRUE,
    featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    INDEX idx_category (category_id),
    INDEX idx_brand (brand),
    INDEX idx_price (price),
    INDEX idx_stock (stock_quantity)
);

-- Create inventory logs table
CREATE TABLE inventory_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    store_id INT,
    transaction_type ENUM('IN', 'OUT', 'ADJUSTMENT', 'RETURN'),
    quantity_change INT NOT NULL,
    previous_quantity INT,
    new_quantity INT,
    reason VARCHAR(200),
    reference_id INT, -- order_id or other reference
    employee_id INT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Create product reviews table
CREATE TABLE product_reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    customer_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_title VARCHAR(200),
    review_text TEXT,
    helpful_votes INT DEFAULT 0,
    verified_purchase BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create banking accounts table
CREATE TABLE banking_accounts (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type ENUM('CHECKING', 'SAVINGS', 'CREDIT'),
    balance DECIMAL(15,2) DEFAULT 0,
    credit_limit DECIMAL(15,2),
    interest_rate DECIMAL(5,4),
    account_status ENUM('ACTIVE', 'SUSPENDED', 'CLOSED') DEFAULT 'ACTIVE',
    opened_date DATE,
    last_transaction_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create banking transactions table
CREATE TABLE banking_transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT,
    transaction_type ENUM('DEBIT', 'CREDIT', 'TRANSFER', 'PAYMENT', 'DEPOSIT', 'WITHDRAWAL'),
    amount DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2),
    description VARCHAR(500),
    reference_number VARCHAR(100),
    related_order_id INT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'COMPLETED',
    FOREIGN KEY (account_id) REFERENCES banking_accounts(account_id),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_transaction_type (transaction_type)
);

-- Create orders table
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    store_id INT,
    employee_id INT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_status ENUM('PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED') DEFAULT 'PENDING',
    payment_method ENUM('CASH', 'CREDIT_CARD', 'DEBIT_CARD', 'BANK_ACCOUNT', 'PAYPAL') NOT NULL,
    payment_status ENUM('PENDING', 'PAID', 'FAILED', 'REFUNDED') DEFAULT 'PENDING',
    subtotal DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_cost DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    shipping_address TEXT,
    billing_address TEXT,
    tracking_number VARCHAR(100),
    estimated_delivery DATE,
    actual_delivery_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    INDEX idx_order_date (order_date),
    INDEX idx_customer (customer_id),
    INDEX idx_status (order_status)
);

-- Create order items table
CREATE TABLE order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    discount_applied DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create cart table for shopping cart functionality
CREATE TABLE cart (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    product_id INT,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_customer_product (customer_id, product_id)
);

-- Create stored procedures and functions
DELIMITER //

-- Function to calculate customer lifetime value
CREATE FUNCTION get_customer_lifetime_value(cust_id INT) 
RETURNS DECIMAL(12,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE total_value DECIMAL(12,2) DEFAULT 0;
    SELECT COALESCE(SUM(total_amount), 0) INTO total_value
    FROM orders 
    WHERE customer_id = cust_id AND order_status != 'CANCELLED';
    RETURN total_value;
END //

-- Procedure to update product stock
CREATE PROCEDURE update_product_stock(
    IN p_product_id INT,
    IN p_quantity_change INT,
    IN p_transaction_type VARCHAR(20),
    IN p_employee_id INT,
    IN p_reason VARCHAR(200)
)
BEGIN
    DECLARE current_stock INT DEFAULT 0;
    DECLARE new_stock INT DEFAULT 0;
    
    START TRANSACTION;
    
    SELECT stock_quantity INTO current_stock 
    FROM products 
    WHERE product_id = p_product_id FOR UPDATE;
    
    SET new_stock = current_stock + p_quantity_change;
    
    IF new_stock < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient stock';
    END IF;
    
    UPDATE products 
    SET stock_quantity = new_stock,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = p_product_id;
    
    INSERT INTO inventory_logs (
        product_id, transaction_type, quantity_change, 
        previous_quantity, new_quantity, reason, employee_id
    ) VALUES (
        p_product_id, p_transaction_type, p_quantity_change,
        current_stock, new_stock, p_reason, p_employee_id
    );
    
    COMMIT;
END //

-- Procedure for complex sales analysis
CREATE PROCEDURE get_sales_analysis(
    IN start_date DATE,
    IN end_date DATE,
    IN store_id_param INT
)
BEGIN
    -- Sales summary with ranking
    SELECT 
        p.product_name,
        p.brand,
        c.category_name,
        SUM(oi.quantity) as total_sold,
        SUM(oi.total_price) as revenue,
        AVG(oi.unit_price) as avg_price,
        RANK() OVER (ORDER BY SUM(oi.total_price) DESC) as revenue_rank,
        DENSE_RANK() OVER (PARTITION BY c.category_id ORDER BY SUM(oi.quantity) DESC) as category_rank
    FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN categories c ON p.category_id = c.category_id
    WHERE o.order_date BETWEEN start_date AND end_date
    AND (store_id_param IS NULL OR o.store_id = store_id_param)
    AND o.order_status = 'DELIVERED'
    GROUP BY p.product_id, p.product_name, p.brand, c.category_name, c.category_id
    HAVING revenue > 1000
    ORDER BY revenue DESC;
END //

DELIMITER ;

-- Create triggers
DELIMITER //

-- Trigger to update customer total spent
CREATE TRIGGER update_customer_total_spent
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF NEW.order_status = 'DELIVERED' AND OLD.order_status != 'DELIVERED' THEN
        UPDATE customers 
        SET total_spent = total_spent + NEW.total_amount,
            loyalty_points = loyalty_points + FLOOR(NEW.total_amount / 10)
        WHERE customer_id = NEW.customer_id;
    END IF;
END //

-- Trigger to log banking transactions
CREATE TRIGGER after_banking_transaction
AFTER INSERT ON banking_transactions
FOR EACH ROW
BEGIN
    UPDATE banking_accounts 
    SET balance = NEW.balance_after,
        last_transaction_date = NEW.transaction_date
    WHERE account_id = NEW.account_id;
END //

DELIMITER ;

-- Create views for complex queries
CREATE VIEW customer_summary AS
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) as full_name,
    c.email,
    c.total_spent,
    c.loyalty_points,
    COUNT(DISTINCT o.order_id) as total_orders,
    COALESCE(AVG(o.total_amount), 0) as avg_order_value,
    MAX(o.order_date) as last_order_date,
    COALESCE(AVG(pr.rating), 0) as avg_rating_given,
    DATEDIFF(CURDATE(), c.registration_date) as days_since_registration
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status = 'DELIVERED'
LEFT JOIN product_reviews pr ON c.customer_id = pr.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.total_spent, c.loyalty_points, c.registration_date;

CREATE VIEW product_performance AS
SELECT 
    p.product_id,
    p.product_name,
    p.brand,
    c.category_name,
    p.price,
    p.stock_quantity,
    COALESCE(SUM(oi.quantity), 0) as total_sold,
    COALESCE(SUM(oi.total_price), 0) as total_revenue,
    COALESCE(AVG(pr.rating), 0) as avg_rating,
    COUNT(DISTINCT pr.review_id) as review_count,
    (p.price - p.cost_price) as profit_margin,
    CASE 
        WHEN p.stock_quantity <= p.min_stock_level THEN 'LOW'
        WHEN p.stock_quantity >= p.max_stock_level THEN 'OVERSTOCKED'
        ELSE 'NORMAL'
    END as stock_status
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'DELIVERED'
LEFT JOIN product_reviews pr ON p.product_id = pr.product_id
WHERE p.is_active = TRUE
GROUP BY p.product_id, p.product_name, p.brand, c.category_name, p.price, p.stock_quantity, p.cost_price, p.min_stock_level, p.max_stock_level;