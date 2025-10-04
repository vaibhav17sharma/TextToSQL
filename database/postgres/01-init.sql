-- PostgreSQL Sample Database for Text-to-SQL Testing
-- This script creates a sample e-commerce database with realistic data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    customer_type VARCHAR(20) DEFAULT 'regular',
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_category_id INTEGER REFERENCES categories(category_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(category_id),
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),
    stock_quantity INTEGER DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,
    weight DECIMAL(8,3),
    dimensions VARCHAR(50),
    brand VARCHAR(100),
    model VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    shipping_cost DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    payment_method VARCHAR(50),
    shipping_address TEXT,
    billing_address TEXT,
    notes TEXT,
    shipped_date TIMESTAMP,
    delivered_date TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_suppliers (
    product_id INTEGER REFERENCES products(product_id),
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    supplier_price DECIMAL(10,2),
    lead_time_days INTEGER,
    minimum_order_quantity INTEGER DEFAULT 1,
    is_preferred BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (product_id, supplier_id)
);

-- Insert sample data
INSERT INTO categories (category_name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Computers', 'Computers and computer accessories'),
('Smartphones', 'Mobile phones and accessories'),
('Home & Garden', 'Home improvement and garden supplies'),
('Books', 'Books and educational materials'),
('Clothing', 'Apparel and fashion accessories'),
('Sports', 'Sports equipment and accessories'),
('Toys', 'Toys and games for all ages');

-- Update some categories to have parent relationships
UPDATE categories SET parent_category_id = 1 WHERE category_name IN ('Computers', 'Smartphones');

INSERT INTO customers (first_name, last_name, email, phone, date_of_birth, customer_type) VALUES
('John', 'Doe', 'john.doe@email.com', '+1-555-0101', '1985-03-15', 'premium'),
('Jane', 'Smith', 'jane.smith@email.com', '+1-555-0102', '1990-07-22', 'regular'),
('Mike', 'Johnson', 'mike.johnson@email.com', '+1-555-0103', '1982-11-08', 'premium'),
('Sarah', 'Williams', 'sarah.williams@email.com', '+1-555-0104', '1995-01-30', 'regular'),
('David', 'Brown', 'david.brown@email.com', '+1-555-0105', '1988-09-12', 'regular'),
('Emily', 'Davis', 'emily.davis@email.com', '+1-555-0106', '1992-04-18', 'premium'),
('Chris', 'Miller', 'chris.miller@email.com', '+1-555-0107', '1987-12-03', 'regular'),
('Lisa', 'Wilson', 'lisa.wilson@email.com', '+1-555-0108', '1991-06-25', 'regular'),
('Tom', 'Moore', 'tom.moore@email.com', '+1-555-0109', '1983-10-14', 'premium'),
('Anna', 'Taylor', 'anna.taylor@email.com', '+1-555-0110', '1989-08-07', 'regular');

INSERT INTO products (product_name, description, category_id, price, cost, stock_quantity, brand, model) VALUES
('MacBook Pro 16"', 'High-performance laptop with M2 chip', 2, 2499.00, 1800.00, 15, 'Apple', 'MBP16-M2'),
('iPhone 14 Pro', 'Latest iPhone with advanced camera system', 3, 999.00, 700.00, 50, 'Apple', 'iPhone14Pro'),
('Dell XPS 13', 'Ultrabook laptop for professionals', 2, 1299.00, 900.00, 25, 'Dell', 'XPS13-2023'),
('Samsung Galaxy S23', 'Premium Android smartphone', 3, 799.00, 550.00, 40, 'Samsung', 'GalaxyS23'),
('iPad Air', 'Versatile tablet for work and play', 1, 599.00, 420.00, 30, 'Apple', 'iPadAir5'),
('Sony WH-1000XM5', 'Noise-canceling wireless headphones', 1, 399.00, 280.00, 60, 'Sony', 'WH1000XM5'),
('Gaming Chair Pro', 'Ergonomic gaming chair with lumbar support', 4, 299.00, 180.00, 20, 'GameMax', 'ChairPro2023'),
('Mechanical Keyboard', 'RGB mechanical keyboard for gaming', 2, 149.00, 80.00, 45, 'Corsair', 'K95RGB'),
('4K Monitor 27"', 'Ultra HD monitor for professionals', 2, 449.00, 320.00, 18, 'LG', '27UK850'),
('Wireless Mouse', 'Precision wireless mouse', 2, 79.00, 45.00, 80, 'Logitech', 'MX3Master');

INSERT INTO suppliers (company_name, contact_name, email, phone, city, country, rating) VALUES
('Tech Distributors Inc', 'Robert Chen', 'robert@techdist.com', '+1-800-555-0201', 'San Francisco', 'USA', 4.5),
('Global Electronics Ltd', 'Maria Garcia', 'maria@globalelec.com', '+1-800-555-0202', 'New York', 'USA', 4.2),
('Asian Tech Supply', 'Yuki Tanaka', 'yuki@asiantech.com', '+81-3-5555-0203', 'Tokyo', 'Japan', 4.7),
('European Components', 'Hans Mueller', 'hans@eurocomp.de', '+49-30-555-0204', 'Berlin', 'Germany', 4.3),
('Quality Parts Co', 'Linda Thompson', 'linda@qualityparts.com', '+1-800-555-0205', 'Chicago', 'USA', 4.1);

-- Link products with suppliers
INSERT INTO product_suppliers (product_id, supplier_id, supplier_price, lead_time_days, minimum_order_quantity, is_preferred) VALUES
(1, 1, 1750.00, 7, 1, TRUE),
(2, 1, 680.00, 5, 1, TRUE),
(3, 2, 880.00, 10, 1, FALSE),
(4, 3, 520.00, 12, 1, TRUE),
(5, 1, 400.00, 6, 1, TRUE),
(6, 4, 260.00, 14, 5, FALSE),
(7, 5, 160.00, 21, 2, TRUE),
(8, 2, 70.00, 8, 3, FALSE),
(9, 4, 300.00, 15, 1, TRUE),
(10, 2, 40.00, 7, 10, TRUE);

INSERT INTO orders (order_number, customer_id, status, total_amount, tax_amount, shipping_cost, payment_method, shipping_address) VALUES
('ORD-2023-001', 1, 'delivered', 2598.00, 199.92, 0.00, 'credit_card', '123 Main St, Anytown, CA 90210'),
('ORD-2023-002', 2, 'shipped', 1048.00, 80.76, 9.99, 'paypal', '456 Oak Ave, Somewhere, NY 10001'),
('ORD-2023-003', 3, 'delivered', 448.00, 34.52, 15.99, 'credit_card', '789 Pine Rd, Elsewhere, TX 75001'),
('ORD-2023-004', 4, 'processing', 599.00, 46.17, 12.99, 'debit_card', '321 Elm St, Nowhere, FL 33101'),
('ORD-2023-005', 5, 'delivered', 228.00, 17.56, 8.99, 'credit_card', '654 Maple Dr, Someplace, WA 98001'),
('ORD-2023-006', 1, 'pending', 799.00, 61.52, 0.00, 'credit_card', '123 Main St, Anytown, CA 90210'),
('ORD-2023-007', 6, 'shipped', 1747.00, 134.65, 19.99, 'paypal', '987 Cedar Ln, Anywhere, OR 97001'),
('ORD-2023-008', 7, 'delivered', 79.00, 6.09, 5.99, 'debit_card', '147 Birch St, Wherever, CO 80001');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
-- Order 1: MacBook Pro
(1, 1, 1, 2499.00, 2499.00),
(1, 10, 1, 79.00, 79.00),
-- Order 2: iPhone + accessories  
(2, 2, 1, 999.00, 999.00),
(2, 6, 1, 399.00, 399.00),
-- Order 3: Monitor
(3, 9, 1, 449.00, 449.00),
-- Order 4: iPad
(4, 5, 1, 599.00, 599.00),
-- Order 5: Keyboard + Mouse
(5, 8, 1, 149.00, 149.00),
(5, 10, 1, 79.00, 79.00),
-- Order 6: Samsung phone
(6, 4, 1, 799.00, 799.00),
-- Order 7: Dell laptop + accessories
(7, 3, 1, 1299.00, 1299.00),
(7, 8, 1, 149.00, 149.00),
(7, 9, 1, 449.00, 449.00),
-- Order 8: Mouse
(8, 10, 1, 79.00, 79.00);

-- Update customer totals
UPDATE customers SET 
    total_orders = (SELECT COUNT(*) FROM orders WHERE orders.customer_id = customers.customer_id),
    total_spent = (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE orders.customer_id = customers.customer_id);

-- Create indexes for better performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_type ON customers(customer_type);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- Create some views for common queries
CREATE VIEW customer_summary AS
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS full_name,
    c.email,
    c.customer_type,
    c.total_orders,
    c.total_spent,
    c.registration_date
FROM customers c
WHERE c.is_active = TRUE;

CREATE VIEW product_inventory AS
SELECT 
    p.product_id,
    p.product_name,
    c.category_name,
    p.price,
    p.stock_quantity,
    p.min_stock_level,
    CASE 
        WHEN p.stock_quantity <= p.min_stock_level THEN 'Low Stock'
        WHEN p.stock_quantity = 0 THEN 'Out of Stock'
        ELSE 'In Stock'
    END AS stock_status
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE p.is_active = TRUE;

CREATE VIEW order_details AS
SELECT 
    o.order_id,
    o.order_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    o.order_date,
    o.status,
    o.total_amount,
    COUNT(oi.order_item_id) AS item_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.order_number, customer_name, o.order_date, o.status, o.total_amount;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;