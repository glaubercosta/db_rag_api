#!/usr/bin/env python3
"""
Create sample database for testing the DB RAG API
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_sample_database():
    """Create a sample SQLite database with test data"""
    
    # Ensure data directory exists
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    db_path = os.path.join(data_dir, "test_database.db")
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            city TEXT,
            country TEXT,
            created_date DATE,
            total_revenue DECIMAL(10,2) DEFAULT 0
        )
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price DECIMAL(10,2),
            cost DECIMAL(10,2),
            stock_quantity INTEGER DEFAULT 0,
            description TEXT,
            created_date DATE
        )
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_date DATE,
            total_amount DECIMAL(10,2),
            status TEXT,
            shipping_address TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    # Create order_items table
    cursor.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price DECIMAL(10,2),
            total_price DECIMAL(10,2),
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Insert sample customers
    customers_data = [
        ("Acme Corporation", "contact@acme.com", "555-0101", "123 Business St", "New York", "USA"),
        ("TechCorp Solutions", "info@techcorp.com", "555-0102", "456 Tech Ave", "San Francisco", "USA"),
        ("Global Industries", "sales@global.com", "555-0103", "789 Industrial Blvd", "Chicago", "USA"),
        ("Innovation Labs", "hello@innovation.com", "555-0104", "321 Innovation Dr", "Austin", "USA"),
        ("Future Dynamics", "contact@future.com", "555-0105", "654 Future Ln", "Seattle", "USA"),
        ("Alpha Enterprises", "info@alpha.com", "555-0106", "987 Alpha St", "Boston", "USA"),
        ("Beta Systems", "sales@beta.com", "555-0107", "147 Beta Ave", "Denver", "USA"),
        ("Gamma Tech", "support@gamma.com", "555-0108", "258 Gamma Rd", "Phoenix", "USA"),
        ("Delta Solutions", "contact@delta.com", "555-0109", "369 Delta Blvd", "Miami", "USA"),
        ("Omega Group", "info@omega.com", "555-0110", "741 Omega Way", "Portland", "USA")
    ]
    
    for i, (name, email, phone, address, city, country) in enumerate(customers_data):
        created_date = datetime.now() - timedelta(days=random.randint(30, 365))
        revenue = random.randint(5000, 100000)
        cursor.execute("""
            INSERT INTO customers (name, email, phone, address, city, country, created_date, total_revenue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, address, city, country, created_date.date(), revenue))
    
    # Insert sample products
    products_data = [
        ("Laptop Pro", "Electronics", 1299.99, 800.00, 50, "High-performance laptop for professionals"),
        ("Wireless Mouse", "Electronics", 29.99, 15.00, 200, "Ergonomic wireless mouse"),
        ("Standing Desk", "Furniture", 499.99, 300.00, 25, "Adjustable height standing desk"),
        ("Office Chair", "Furniture", 299.99, 180.00, 40, "Ergonomic office chair with lumbar support"),
        ("Monitor 27\"", "Electronics", 349.99, 220.00, 60, "4K Ultra HD 27-inch monitor"),
        ("Keyboard Mechanical", "Electronics", 129.99, 70.00, 80, "RGB mechanical gaming keyboard"),
        ("Desk Lamp", "Furniture", 79.99, 40.00, 100, "LED desk lamp with adjustable brightness"),
        ("Notebook Set", "Stationery", 24.99, 10.00, 300, "Premium notebook set with pen"),
        ("Coffee Mug", "Accessories", 12.99, 5.00, 150, "Insulated coffee mug"),
        ("Plant Pot", "Accessories", 19.99, 8.00, 75, "Decorative plant pot for office")
    ]
    
    for name, category, price, cost, stock, description in products_data:
        created_date = datetime.now() - timedelta(days=random.randint(10, 200))
        cursor.execute("""
            INSERT INTO products (name, category, price, cost, stock_quantity, description, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, category, price, cost, stock, description, created_date.date()))
    
    # Insert sample orders
    for i in range(50):  # Create 50 orders
        customer_id = random.randint(1, 10)
        order_date = datetime.now() - timedelta(days=random.randint(1, 180))
        status = random.choice(["pending", "processing", "shipped", "delivered", "cancelled"])
        
        cursor.execute("""
            INSERT INTO orders (customer_id, order_date, status, shipping_address)
            VALUES (?, ?, ?, ?)
        """, (customer_id, order_date.date(), status, f"Address {i+1}"))
        
        order_id = cursor.lastrowid
        
        # Add 1-5 items per order
        total_amount = 0
        num_items = random.randint(1, 5)
        
        for _ in range(num_items):
            product_id = random.randint(1, 10)
            quantity = random.randint(1, 3)
            
            # Get product price
            cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            unit_price = cursor.fetchone()[0]
            total_price = unit_price * quantity
            total_amount += total_price
            
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, product_id, quantity, unit_price, total_price))
        
        # Update order total
        cursor.execute("""
            UPDATE orders SET total_amount = ? WHERE id = ?
        """, (total_amount, order_id))
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX idx_customers_email ON customers(email)")
    cursor.execute("CREATE INDEX idx_orders_customer_id ON orders(customer_id)")
    cursor.execute("CREATE INDEX idx_orders_date ON orders(order_date)")
    cursor.execute("CREATE INDEX idx_order_items_order_id ON order_items(order_id)")
    cursor.execute("CREATE INDEX idx_order_items_product_id ON order_items(product_id)")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"✅ Sample database created successfully at: {db_path}")
    print("📊 Database contains:")
    print("   - 10 customers")
    print("   - 10 products")
    print("   - 50 orders with order items")
    print("   - Proper relationships and indexes")
    
    return db_path

if __name__ == "__main__":
    create_sample_database()
