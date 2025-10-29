"""Test database connection for Gadgets Store.
Improved for clear output and robust error handling.
"""

import os
from dotenv import load_dotenv
from db.db_config import DatabaseConfig

load_dotenv()


def mask(s):
    if not s:
        return ""
    return "*" * len(s)


def main():
    print("=" * 50)
    print("Testing Database Connection")
    print("=" * 50)

    # Display configuration (hide password)
    print(f"\n📋 Configuration:")
    print(f"   Host: {os.getenv('MYSQL_HOST')}")
    print(f"   User: {os.getenv('MYSQL_USER')}")
    print(f"   Password: {mask(os.getenv('MYSQL_PASSWORD', ''))}")
    print(f"   Database: {os.getenv('MYSQL_DATABASE')}")

    db = DatabaseConfig()
    conn = db.get_connection()

    if not conn:
        print("\n❌ Connection failed!")
        print("\n🔍 Troubleshooting:")
        print("   1. Check DB host/port and that MySQL server is reachable")
        print("   2. Verify credentials in .env / Railway env vars")
        print("   3. Ensure database exists and user has privileges")
        return

    print("\n✅ Connection successful!")

    try:
        print("\n📊 Testing database queries...")
        tables_query = "SHOW TABLES"
        tables = db.execute_query(tables_query, fetch=True)
        if not tables:
            print("   No tables found in database.")
            return

        print(f"   Tables found: {len(tables)}")
        print("\n📋 Tables in database:")
        for table in tables:
            # SHOW TABLES returns a dict with the column name as key
            table_name = list(table.values())[0]
            count_query = f"SELECT COUNT(*) as count FROM `{table_name}`"
            result = db.execute_query(count_query, fetch=True)
            count = result[0]['count'] if result else 0
            print(f"   ✓ {table_name}: {count} rows")

        # Run a sample query if products table exists
        print("\n🧪 Testing sample query (products)...")
        sample_query = """
            SELECT 
                COUNT(*) as total_products,
                COALESCE(SUM(stock_quantity),0) as total_inventory
            FROM products
            WHERE is_active = TRUE
        """
        result = db.execute_query(sample_query, fetch=True)
        if result:
            print(f"   ✓ Total active products: {result[0].get('total_products', 0)}")
            print(f"   ✓ Total inventory units: {result[0].get('total_inventory', 0)}")

        print("\n" + "=" * 50)
        print("✅ All tests done")
        print("=" * 50)

    except Exception as e:
        print(f"Error running test queries: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()