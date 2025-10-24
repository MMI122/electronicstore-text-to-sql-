-- Insert sample data

-- Insert stores
INSERT INTO stores (store_name, address, city, state, zipcode, phone, manager_name, established_date) VALUES
('TechHub Downtown', '123 Main St', 'New York', 'NY', '10001', '212-555-0101', 'John Smith', '2020-01-15'),
('Gadget Galaxy Mall', '456 Shopping Blvd', 'Los Angeles', 'CA', '90210', '310-555-0102', 'Sarah Johnson', '2019-03-22'),
('Electronics Emporium', '789 Tech Ave', 'Chicago', 'IL', '60601', '312-555-0103', 'Mike Williams', '2021-06-10'),
('Digital Dreams', '321 Innovation Dr', 'Austin', 'TX', '73301', '512-555-0104', 'Emily Davis', '2020-11-05'),
('Circuit City Plus', '654 Electronics Way', 'Seattle', 'WA', '98101', '206-555-0105', 'David Brown', '2018-08-30');

-- Insert employees
INSERT INTO employees (store_id, first_name, last_name, email, phone, position, salary, hire_date, department, manager_id) VALUES
(1, 'John', 'Smith', 'john.smith@techhub.com', '212-555-1001', 'Store Manager', 75000.00, '2020-01-15', 'Management', NULL),
(1, 'Alice', 'Cooper', 'alice.cooper@techhub.com', '212-555-1002', 'Sales Associate', 35000.00, '2020-02-01', 'Sales', 1),
(1, 'Bob', 'Wilson', 'bob.wilson@techhub.com', '212-555-1003', 'Technical Support', 45000.00, '2020-03-15', 'Support', 1),
(2, 'Sarah', 'Johnson', 'sarah.johnson@gadgetgalaxy.com', '310-555-2001', 'Store Manager', 80000.00, '2019-03-22', 'Management', NULL),
(2, 'Tom', 'Anderson', 'tom.anderson@gadgetgalaxy.com', '310-555-2002', 'Sales Lead', 50000.00, '2019-04-01', 'Sales', 4),
(3, 'Mike', 'Williams', 'mike.williams@electronicsemp.com', '312-555-3001', 'Store Manager', 78000.00, '2021-06-10', 'Management', NULL),
(3, 'Lisa', 'Garcia', 'lisa.garcia@electronicsemp.com', '312-555-3002', 'Inventory Manager', 55000.00, '2021-07-01', 'Inventory', 6);

-- Insert suppliers
INSERT INTO suppliers (company_name, contact_person, email, phone, address, city, country, established_year, rating, payment_terms) VALUES
('Apple Inc.', 'Tim Cook', 'supplier@apple.com', '408-996-1010', '1 Apple Park Way', 'Cupertino', 'USA', 1976, 4.9, 'Net 30'),
('Samsung Electronics', 'Jong-Hee Han', 'supplier@samsung.com', '+82-2-2255-0114', 'Samsung Town', 'Seoul', 'South Korea', 1969, 4.8, 'Net 45'),
('Sony Corporation', 'Kenichiro Yoshida', 'supplier@sony.com', '+81-3-6748-2111', 'Sony City', 'Tokyo', 'Japan', 1946, 4.7, 'Net 30'),
('LG Electronics', 'William Cho', 'supplier@lg.com', '+82-2-3777-1114', 'LG Twin Towers', 'Seoul', 'South Korea', 1958, 4.6, 'Net 30'),
('Microsoft Corporation', 'Satya Nadella', 'supplier@microsoft.com', '425-882-8080', 'One Microsoft Way', 'Redmond', 'USA', 1975, 4.8, 'Net 45'),
('Dell Technologies', 'Michael Dell', 'supplier@dell.com', '512-338-4400', 'One Dell Way', 'Round Rock', 'USA', 1984, 4.5, 'Net 30'),
('HP Inc.', 'Enrique Lores', 'supplier@hp.com', '650-857-1501', 'HP Way', 'Palo Alto', 'USA', 1939, 4.4, 'Net 30'),
('Lenovo Group', 'Yang Yuanqing', 'supplier@lenovo.com', '+86-10-5886-8888', 'Lenovo Building', 'Beijing', 'China', 1984, 4.3, 'Net 30');

-- Insert categories
INSERT INTO categories (category_name, parent_category_id, description) VALUES
('Electronics', NULL, 'All electronic devices and accessories'),
('Smartphones', 1, 'Mobile phones and accessories'),
('Laptops', 1, 'Portable computers'),
('Desktop Computers', 1, 'Desktop PCs and workstations'),
('Tablets', 1, 'Tablet computers and e-readers'),
('Audio', 1, 'Headphones, speakers, and audio equipment'),
('Gaming', 1, 'Gaming consoles, accessories, and games'),
('Smart Home', 1, 'Home automation and IoT devices'),
('Wearables', 1, 'Smartwatches and fitness trackers'),
('Accessories', 1, 'Cases, chargers, and other accessories'),
('iPhone', 2, 'Apple smartphones'),
('Android Phones', 2, 'Android-based smartphones'),
('Gaming Laptops', 3, 'High-performance gaming laptops'),
('Business Laptops', 3, 'Professional and business laptops'),
('Gaming Consoles', 7, 'Video game consoles'),
('PC Gaming', 7, 'PC gaming hardware and accessories');

-- Insert customers
INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zipcode, date_of_birth, gender, total_spent, loyalty_points) VALUES
('Emma', 'Thompson', 'emma.thompson@email.com', '555-0201', '123 Elm St', 'New York', 'NY', '10001', '1990-05-15', 'F', 2500.00, 250),
('James', 'Rodriguez', 'james.rodriguez@email.com', '555-0202', '456 Oak Ave', 'Los Angeles', 'CA', '90210', '1985-11-22', 'M', 3200.00, 320),
('Olivia', 'Chen', 'olivia.chen@email.com', '555-0203', '789 Pine Rd', 'Chicago', 'IL', '60601', '1992-08-08', 'F', 1800.00, 180),
('William', 'Johnson', 'william.johnson@email.com', '555-0204', '321 Maple Dr', 'Austin', 'TX', '73301', '1988-03-12', 'M', 4100.00, 410),
('Sophia', 'Williams', 'sophia.williams@email.com', '555-0205', '654 Cedar Ln', 'Seattle', 'WA', '98101', '1995-07-20', 'F', 950.00, 95),
('Alexander', 'Brown', 'alexander.brown@email.com', '555-0206', '987 Birch St', 'Miami', 'FL', '33101', '1993-12-03', 'M', 2750.00, 275),
('Isabella', 'Davis', 'isabella.davis@email.com', '555-0207', '147 Willow Way', 'Denver', 'CO', '80201', '1991-09-14', 'F', 1650.00, 165),
('Michael', 'Miller', 'michael.miller@email.com', '555-0208', '258 Spruce Ave', 'Boston', 'MA', '02101', '1987-04-25', 'M', 3850.00, 385),
('Emily', 'Wilson', 'emily.wilson@email.com', '555-0209', '369 Fir Dr', 'Portland', 'OR', '97201', '1994-01-30', 'F', 2200.00, 220),
('Ethan', 'Moore', 'ethan.moore@email.com', '555-0210', '741 Ash Rd', 'Phoenix', 'AZ', '85001', '1989-10-18', 'M', 1450.00, 145);

-- Insert products
INSERT INTO products (product_name, category_id, supplier_id, brand, model, description, price, cost_price, stock_quantity, weight, warranty_period) VALUES
-- Smartphones
('iPhone 15 Pro', 11, 1, 'Apple', 'A3101', 'Latest iPhone with titanium design and A17 Pro chip', 999.00, 750.00, 50, 0.21, 12),
('iPhone 14', 11, 1, 'Apple', 'A2884', 'Previous generation iPhone with great performance', 799.00, 600.00, 75, 0.17, 12),
('Samsung Galaxy S24 Ultra', 12, 2, 'Samsung', 'SM-S928U', 'Premium Android phone with S Pen', 1299.00, 950.00, 40, 0.23, 12),
('Google Pixel 8 Pro', 12, 2, 'Google', 'GC3VE', 'AI-powered Android phone with advanced camera', 899.00, 675.00, 35, 0.21, 12),
('OnePlus 12', 12, 2, 'OnePlus', 'CPH2573', 'Fast charging flagship Android phone', 799.00, 580.00, 45, 0.22, 12),

-- Laptops
('MacBook Pro 16"', 13, 1, 'Apple', 'MRW13', 'Professional laptop with M3 Pro chip', 2499.00, 1875.00, 25, 2.14, 12),
('MacBook Air 15"', 14, 1, 'Apple', 'MQKR3', 'Lightweight laptop with M2 chip', 1299.00, 975.00, 40, 1.51, 12),
('Dell XPS 15', 14, 6, 'Dell', 'XPS9530', 'Premium Windows laptop for professionals', 1799.00, 1350.00, 30, 2.05, 12),
('ASUS ROG Strix G18', 13, 8, 'ASUS', 'G814JV', 'High-performance gaming laptop', 2199.00, 1650.00, 20, 3.0, 24),
('HP Spectre x360', 14, 7, 'HP', '16-f1023dx', 'Convertible business laptop', 1599.00, 1200.00, 25, 2.45, 12),
('Lenovo ThinkPad X1 Carbon', 14, 8, 'Lenovo', '21HM', 'Ultra-light business laptop', 1899.00, 1425.00, 35, 1.12, 36),

-- Desktop Computers
('iMac 24"', 4, 1, 'Apple', 'MQRQ3', 'All-in-one desktop with M3 chip', 1299.00, 975.00, 20, 4.46, 12),
('Dell OptiPlex 7010', 4, 6, 'Dell', 'N008O7010MT', 'Business desktop computer', 899.00, 675.00, 40, 6.8, 36),
('HP Elite Desktop', 4, 7, 'HP', '290G9', 'Compact business desktop', 749.00, 560.00, 50, 3.9, 36),
('Custom Gaming PC', 4, 6, 'Custom', 'GAMING-001', 'High-end gaming desktop build', 2499.00, 1875.00, 15, 15.0, 24),

-- Tablets
('iPad Pro 12.9"', 5, 1, 'Apple', 'MNXH3', 'Professional tablet with M2 chip', 1099.00, 825.00, 30, 0.68, 12),
('iPad Air', 5, 1, 'Apple', 'MM9F3', 'Versatile tablet for work and play', 599.00, 450.00, 45, 0.46, 12),
('Samsung Galaxy Tab S9+', 5, 2, 'Samsung', 'SM-X816U', 'Premium Android tablet', 899.00, 675.00, 25, 0.57, 12),
('Microsoft Surface Pro 9', 5, 5, 'Microsoft', '5Q4-00001', '2-in-1 tablet with full Windows', 1299.00, 975.00, 20, 0.88, 12),

-- Audio Equipment
('AirPods Pro (2nd Gen)', 6, 1, 'Apple', 'MTJV3', 'Premium noise-canceling earbuds', 249.00, 187.00, 100, 0.05, 12),
('Sony WH-1000XM5', 6, 3, 'Sony', 'WH1000XM5/B', 'Industry-leading noise canceling headphones', 399.00, 300.00, 60, 0.25, 12),
('Bose QuietComfort 45', 6, 3, 'Bose', '866724-0100', 'Comfortable noise-canceling headphones', 329.00, 247.00, 45, 0.24, 12),
('JBL Charge 5', 6, 3, 'JBL', 'JBLCHARGE5BLKAM', 'Portable Bluetooth speaker', 179.00, 135.00, 80, 0.96, 12),

-- Gaming
('PlayStation 5', 15, 3, 'Sony', 'CFI-1215A01', 'Next-gen gaming console', 499.00, 375.00, 25, 4.5, 12),
('Xbox Series X', 15, 5, 'Microsoft', 'RRT-00001', 'Powerful 4K gaming console', 499.00, 375.00, 30, 4.45, 12),
('Nintendo Switch OLED', 15, 4, 'Nintendo', 'HEG-001', 'Hybrid gaming console with OLED screen', 349.00, 262.00, 50, 0.42, 12),
('Meta Quest 3', 16, 5, 'Meta', '899-00582-01', 'VR headset for immersive gaming', 499.00, 375.00, 20, 0.515, 12),

-- Smart Home
('Echo Dot (5th Gen)', 8, 1, 'Amazon', 'B09B8V1LZ3', 'Smart speaker with Alexa', 49.99, 37.50, 150, 0.34, 12),
('Google Nest Hub', 8, 2, 'Google', 'GA00515-US', 'Smart display for home control', 99.99, 75.00, 80, 0.48, 12),
('Ring Video Doorbell', 8, 1, 'Ring', 'B08N5NQ869', 'Smart doorbell with HD video', 179.99, 135.00, 60, 0.34, 12),
('Philips Hue Starter Kit', 8, 3, 'Philips', '548487', 'Smart lighting system', 199.99, 150.00, 40, 1.2, 24),

-- Wearables
('Apple Watch Series 9', 9, 1, 'Apple', 'MR933LL/A', 'Advanced smartwatch with health features', 399.00, 300.00, 70, 0.039, 12),
('Samsung Galaxy Watch 6', 9, 2, 'Samsung', 'SM-R930NZKAXAA', 'Feature-rich Android smartwatch', 299.00, 225.00, 50, 0.033, 12),
('Fitbit Charge 6', 9, 2, 'Fitbit', 'FB422BKBK', 'Advanced fitness tracker', 159.95, 120.00, 90, 0.029, 12),

-- Accessories
('MagSafe Charger', 10, 1, 'Apple', 'MHXH3AM/A', 'Wireless charger for iPhone', 39.00, 29.25, 200, 0.14, 12),
('Anker PowerBank 10000mAh', 10, 8, 'Anker', 'A1263H11', 'Portable battery pack', 29.99, 22.50, 150, 0.18, 18),
('Logitech MX Master 3S', 10, 3, 'Logitech', '910-006556', 'Advanced wireless mouse', 99.99, 75.00, 85, 0.14, 12),
('Apple Magic Keyboard', 10, 1, 'Apple', 'MK2A3LL/A', 'Wireless keyboard for Mac', 99.00, 74.25, 60, 0.23, 12);

-- Insert banking accounts
INSERT INTO banking_accounts (customer_id, account_number, account_type, balance, credit_limit, interest_rate, opened_date) VALUES
(1, 'ACC001234567890', 'CHECKING', 5250.75, NULL, 0.0100, '2023-01-15'),
(1, 'ACC001234567891', 'SAVINGS', 12800.50, NULL, 0.0250, '2023-01-15'),
(2, 'ACC002345678901', 'CHECKING', 3420.25, NULL, 0.0100, '2022-11-20'),
(2, 'ACC002345678902', 'CREDIT', -1250.00, 5000.00, 0.1899, '2022-12-01'),
(3, 'ACC003456789012', 'CHECKING', 7650.80, NULL, 0.0100, '2023-03-10'),
(3, 'ACC003456789013', 'SAVINGS', 25400.00, NULL, 0.0275, '2023-03-10'),
(4, 'ACC004567890123', 'CHECKING', 2180.45, NULL, 0.0100, '2022-08-05'),
(5, 'ACC005678901234', 'CHECKING', 1850.30, NULL, 0.0100, '2024-01-22'),
(6, 'ACC006789012345', 'CHECKING', 4320.60, NULL, 0.0100, '2023-05-18'),
(7, 'ACC007890123456', 'SAVINGS', 8900.75, NULL, 0.0225, '2023-07-14');

-- Insert orders
INSERT INTO orders (customer_id, store_id, employee_id, order_number, order_status, payment_method, payment_status, subtotal, tax_amount, total_amount, shipping_address) VALUES
(1, 1, 2, 'ORD-2024-001', 'DELIVERED', 'CREDIT_CARD', 'PAID', 999.00, 79.92, 1078.92, '123 Elm St, New York, NY 10001'),
(1, 1, 2, 'ORD-2024-002', 'DELIVERED', 'DEBIT_CARD', 'PAID', 249.00, 19.92, 268.92, '123 Elm St, New York, NY 10001'),
(2, 2, 5, 'ORD-2024-003', 'DELIVERED', 'CREDIT_CARD', 'PAID', 1299.00, 103.92, 1402.92, '456 Oak Ave, Los Angeles, CA 90210'),
(2, 2, 5, 'ORD-2024-004', 'SHIPPED', 'BANK_ACCOUNT', 'PAID', 399.00, 31.92, 430.92, '456 Oak Ave, Los Angeles, CA 90210'),
(3, 3, 7, 'ORD-2024-005', 'DELIVERED', 'CREDIT_CARD', 'PAID', 899.00, 71.92, 970.92, '789 Pine Rd, Chicago, IL 60601'),
(3, 3, 7, 'ORD-2024-006', 'PROCESSING', 'DEBIT_CARD', 'PAID', 179.99, 14.40, 194.39, '789 Pine Rd, Chicago, IL 60601'),
(4, 4, 1, 'ORD-2024-007', 'DELIVERED', 'CREDIT_CARD', 'PAID', 2499.00, 199.92, 2698.92, '321 Maple Dr, Austin, TX 73301'),
(4, 4, 1, 'ORD-2024-008', 'DELIVERED', 'BANK_ACCOUNT', 'PAID', 499.00, 39.92, 538.92, '321 Maple Dr, Austin, TX 73301'),
(5, 5, 1, 'ORD-2024-009', 'CANCELLED', 'CREDIT_CARD', 'REFUNDED', 1099.00, 87.92, 1186.92, '654 Cedar Ln, Seattle, WA 98101'),
(6, 1, 2, 'ORD-2024-010', 'DELIVERED', 'DEBIT_CARD', 'PAID', 1799.00, 143.92, 1942.92, '987 Birch St, Miami, FL 33101');

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
-- Order 1 items
(1, 1, 1, 999.00, 999.00),
-- Order 2 items  
(2, 20, 1, 249.00, 249.00),
-- Order 3 items
(3, 3, 1, 1299.00, 1299.00),
-- Order 4 items
(4, 21, 1, 399.00, 399.00),
-- Order 5 items
(5, 4, 1, 899.00, 899.00),
-- Order 6 items
(6, 26, 1, 179.99, 179.99),
-- Order 7 items
(7, 6, 1, 2499.00, 2499.00),
-- Order 8 items
(8, 28, 1, 499.00, 499.00),
-- Order 9 items (cancelled)
(9, 16, 1, 1099.00, 1099.00),
-- Order 10 items
(10, 8, 1, 1799.00, 1799.00);

-- Insert banking transactions
INSERT INTO banking_transactions (account_id, transaction_type, amount, balance_after, description, related_order_id) VALUES
(1, 'DEBIT', 1078.92, 4171.83, 'Payment for Order ORD-2024-001', 1),
(1, 'DEBIT', 268.92, 3902.91, 'Payment for Order ORD-2024-002', 2),
(1, 'CREDIT', 2500.00, 6402.91, 'Salary deposit', NULL),
(1, 'DEBIT', 150.00, 6252.91, 'ATM withdrawal', NULL),
(1, 'DEBIT', 75.50, 6177.41, 'Grocery store purchase', NULL),
(3, 'DEBIT', 1402.92, 2017.33, 'Payment for Order ORD-2024-003', 3),
(4, 'CREDIT', 1402.92, 152.92, 'Purchase - electronics', 3),
(5, 'DEBIT', 970.92, 6679.88, 'Payment for Order ORD-2024-005', 5),
(7, 'DEBIT', 2698.92, -518.47, 'Payment for Order ORD-2024-007', 7),
(8, 'DEBIT', 538.92, 1311.38, 'Payment for Order ORD-2024-008', 8);

-- Insert product reviews
INSERT INTO product_reviews (product_id, customer_id, rating, review_title, review_text, verified_purchase) VALUES
(1, 1, 5, 'Amazing phone!', 'The iPhone 15 Pro is incredible. The titanium build feels premium and the camera quality is outstanding.', TRUE),
(20, 1, 4, 'Great sound quality', 'AirPods Pro sound great with excellent noise cancellation. Battery life could be better.', TRUE),
(3, 2, 5, 'Best Android phone', 'Samsung Galaxy S24 Ultra is the best Android phone I have ever used. The S Pen is very useful.', TRUE),
(4, 3, 4, 'Good value for money', 'Google Pixel 8 Pro has an excellent camera and clean Android experience.', TRUE),
(6, 4, 5, 'Perfect for work', 'MacBook Pro 16 is perfect for professional work. Fast performance and great display.', TRUE),
(28, 4, 5, 'Next-gen gaming', 'PlayStation 5 delivers amazing gaming experience with fast loading times.', TRUE),
(8, 6, 4, 'Solid business laptop', 'Dell XPS 15 is a solid choice for business use with good build quality.', TRUE);

-- Insert inventory logs
INSERT INTO inventory_logs (product_id, store_id, transaction_type, quantity_change, previous_quantity, new_quantity, reason, reference_id, employee_id) VALUES
(1, 1, 'OUT', -1, 51, 50, 'Sale - Order ORD-2024-001', 1, 2),
(20, 1, 'OUT', -1, 101, 100, 'Sale - Order ORD-2024-002', 2, 2),
(3, 2, 'OUT', -1, 41, 40, 'Sale - Order ORD-2024-003', 3, 5),
(21, 2, 'OUT', -1, 61, 60, 'Sale - Order ORD-2024-004', 4, 5),
(4, 3, 'OUT', -1, 36, 35, 'Sale - Order ORD-2024-005', 5, 7),
(6, 4, 'OUT', -1, 26, 25, 'Sale - Order ORD-2024-007', 7, 1),
(28, 4, 'OUT', -1, 26, 25, 'Sale - Order ORD-2024-008', 8, 1),
(8, 1, 'OUT', -1, 31, 30, 'Sale - Order ORD-2024-010', 10, 2),
(1, 1, 'IN', 25, 50, 75, 'New stock arrival', NULL, 1),
(3, 2, 'IN', 30, 40, 70, 'Restock from supplier', NULL, 4);

-- Update customer total_spent based on delivered orders
UPDATE customers SET total_spent = (
    SELECT COALESCE(SUM(o.total_amount), 0)
    FROM orders o 
    WHERE o.customer_id = customers.customer_id 
    AND o.order_status = 'DELIVERED'
);

-- Update loyalty points
UPDATE customers SET loyalty_points = FLOOR(total_spent / 10);