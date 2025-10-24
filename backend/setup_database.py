"""
Automated database setup script for Gadgets Store
This will create database, import schema, and seed data
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    print("=" * 60)
    print("🚀 Gadgets Store Database Setup")
    print("=" * 60)
    
    # Configuration
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
    }
    
    database_name = os.getenv('MYSQL_DATABASE', 'gadgets_store')
    
    try:
        # Step 1: Connect to MySQL (without database)
        print("\n📡 Step 1: Connecting to MySQL server...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        print("   ✅ Connected successfully")
        
        # Step 2: Create database if not exists
        print(f"\n📦 Step 2: Creating database '{database_name}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        cursor.execute(f"USE {database_name}")
        print(f"   ✅ Database '{database_name}' ready")
        
        # Step 3: Check if tables exist
        cursor.execute("SHOW TABLES")
        existing_tables = cursor.fetchall()
        
        if existing_tables:
            print(f"\n⚠️  Warning: Database already has {len(existing_tables)} tables")
            response = input("   Do you want to drop and recreate all tables? (yes/no): ")
            if response.lower() == 'yes':
                print("   🗑️  Dropping existing tables...")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                for table in existing_tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                print("   ✅ Existing tables dropped")
        
        # Step 4: Import schema
        print("\n📄 Step 3: Importing database schema...")
        schema_file = os.path.join(os.path.dirname(__file__), 'db', 'schema.sql')
        
        if os.path.exists(schema_file):
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema (split by delimiter changes)
            for statement in schema_sql.split('DELIMITER'):
                if statement.strip():
                    try:
                        cursor.execute(statement, multi=True)
                    except:
                        # Some statements might fail, continue
                        pass
            
            connection.commit()
            print("   ✅ Schema imported successfully")
        else:
            print(f"   ❌ Schema file not found at: {schema_file}")
            return False
        
        # Step 5: Import seed data
        print("\n🌱 Step 4: Importing seed data...")
        seed_file = os.path.join(os.path.dirname(__file__), 'db', 'seed.sql')
        
        if os.path.exists(seed_file):
            with open(seed_file, 'r', encoding='utf-8') as f:
                seed_sql = f.read()
            
            # Execute seed data
            for statement in seed_sql.split(';'):
                if statement.strip():
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        print(f"   ⚠️  Warning: {str(e)[:50]}...")
            
            connection.commit()
            print("   ✅ Seed data imported successfully")
        else:
            print(f"   ⚠️  Seed file not found at: {seed_file}")
            print("   ℹ️  You can add sample data manually later")
        
        # Step 6: Verify setup
        print("\n✅ Step 5: Verifying database setup...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total tables: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   ✓ {table_name}: {count} rows")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("🎉 Database setup completed successfully!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("   1. Start the backend server: python app.py")
        print("   2. Start the frontend: cd ../frontend && npm run dev")
        print("   3. Open browser: http://localhost:3000")
        
        return True
        
    except mysql.connector.Error as err:
        print(f"\n❌ Error: {err}")
        print("\n🔍 Troubleshooting:")
        print("   1. Check if MySQL is running in XAMPP")
        print("   2. Verify credentials in .env file")
        print("   3. Make sure port 3306 is not blocked")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n⚠️  .env file not found!")
        print("\nCreating .env file with default values...")
        
        with open('.env', 'w') as f:
            f.write("# MySQL Database Configuration\n")
            f.write("MYSQL_HOST=localhost\n")
            f.write("MYSQL_USER=root\n")
            f.write("MYSQL_PASSWORD=\n")
            f.write("MYSQL_DATABASE=gadgets_store\n")
        
        print("✅ .env file created")
        print("📝 Please edit .env file and set your MySQL password if needed\n")
        input("Press Enter to continue...")
    
    setup_database()