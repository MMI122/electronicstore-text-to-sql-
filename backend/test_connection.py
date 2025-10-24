"""
Test database connection for Gadgets Store
Run this to verify MySQL is properly configured
"""

import os
from dotenv import load_dotenv
from db.db_config import DatabaseConfig

# Load environment variables
load_dotenv()

print("=" * 50)
print("Testing Database Connection")
print("=" * 50)

# Display configuration (hide password)
print(f"\n📋 Configuration:")
print(f"   Host: {os.getenv('MYSQL_HOST')}")
print(f"   User: {os.getenv('MYSQL_USER')}")
print(f"   Password: {'*' * len(os.getenv('MYSQL_PASSWORD', ''))}")
print(f"   Database: {os.getenv('MYSQL_DATABASE')}")

# Test connection
print("\n🔌 Attempting to connect...")
db = DatabaseConfig()
connection = db.get_connection()

if connection:
    print("✅ Connection successful!")
    
    # Test query
    print("\n📊 Testing database queries...")
    
    # Count tables
    tables_query = "SHOW TABLES"
    tables = db.execute_query(tables_query, fetch=True)
    print(f"   Tables found: {len(tables)}")
    
    if tables:
        print("\n📋 Tables in database:")
        for table in tables:
            table_name = list(table.values())[0]
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = db.execute_query(count_query, fetch=True)
            count = result[0]['count'] if result else 0
            print(f"   ✓ {table_name}: {count} rows")
    
    # Test a sample query
    print("\n🧪 Testing sample query...")
    sample_query = """
        SELECT 
            COUNT(*) as total_products,
            SUM(stock_quantity) as total_inventory
        FROM products
        WHERE is_active = TRUE
    """
    result = db.execute_query(sample_query, fetch=True)
    
    if result:
        print(f"   ✓ Total active products: {result[0]['total_products']}")
        print(f"   ✓ Total inventory units: {result[0]['total_inventory']}")
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Database is ready to use.")
    print("=" * 50)
    
    connection.close()
else:
    print("❌ Connection failed!")
    print("\n🔍 Troubleshooting:")
    print("   1. Check if MySQL is running in XAMPP")
    print("   2. Verify credentials in .env file")
    print("   3. Ensure database 'gadgets_store' exists")
    print("   4. Check if schema.sql was imported")