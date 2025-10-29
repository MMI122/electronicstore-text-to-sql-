"""Automated database setup script for Gadgets Store.
This script is intended to be safe to run non-interactively in CI/container.

Behavior:
- Creates the database if it does not exist.
- Imports schema and seed files located in backend/db/
- If environment variable DROP_EXISTING=true, existing tables will be dropped.

Notes for Railway / container runs:
- Provide MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE as env vars.
"""

import os
import re
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def _read_sql_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def _normalize_delimiters(sql: str) -> str:
    """Convert DELIMITER blocks (e.g. DELIMITER // ... END //) into semicolon-terminated statements
    so mysql.connector can execute them via multi=True.
    """
    # Remove lines that declare delimiter
    sql = re.sub(r"(?m)^DELIMITER\s+\S+\s*$", "", sql)

    # Replace common 'END //' or 'END %%' style endings with 'END;'
    sql = re.sub(r"END\s+//", "END;", sql)
    sql = re.sub(r"END\s+%%", "END;", sql)

    # Replace any remaining line that is just '//' with ';'
    sql = re.sub(r"(?m)^//\s*$", ";", sql)

    # Sometimes delimiters occur at line ends: replace '//' optionally followed by newline
    sql = re.sub(r"//\s*\n", ";\n", sql)

    return sql


def execute_multi_sql(cursor, sql: str):
    try:
        for result in cursor.execute(sql, multi=True):
            # iterate to ensure statements are sent to server
            pass
    except Error as e:
        # Re-raise to allow caller to handle or log
        raise


def setup_database():
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DATABASE', 'gadgets_store')
    drop_existing = os.getenv('DROP_EXISTING', 'false').lower() in ('1', 'true', 'yes')

    print("Starting database setup...")

    try:
        # Connect without database to create it if necessary
        conn_params = {'host': host, 'user': user, 'password': password}
        conn = mysql.connector.connect(**conn_params)
        cursor = conn.cursor()

        print(f"Ensuring database '{database}' exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{database}`")

        # Optionally drop existing tables
        cursor.execute("SHOW TABLES")
        existing_tables = cursor.fetchall()
        if existing_tables and drop_existing:
            print(f"Dropping {len(existing_tables)} existing tables (DROP_EXISTING=true)")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            for t in existing_tables:
                table_name = t[0]
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            conn.commit()

        # Import schema
        schema_file = os.path.join(os.path.dirname(__file__), 'db', 'schema.sql')
        if os.path.exists(schema_file):
            print(f"Importing schema from {schema_file} ...")
            raw_schema = _read_sql_file(schema_file)
            schema_sql = _normalize_delimiters(raw_schema)
            execute_multi_sql(cursor, schema_sql)
            conn.commit()
            print("Schema imported")
        else:
            print(f"Schema file not found at {schema_file}")

        # Import seed data if present
        seed_file = os.path.join(os.path.dirname(__file__), 'db', 'seed.sql')
        if os.path.exists(seed_file):
            print(f"Importing seed data from {seed_file} ...")
            raw_seed = _read_sql_file(seed_file)
            seed_sql = _normalize_delimiters(raw_seed)
            execute_multi_sql(cursor, seed_sql)
            conn.commit()
            print("Seed data imported")
        else:
            print("No seed file found; skipping seeding")

        # Quick verification
        cursor.execute("SHOW TABLES")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"Database ready. Tables: {len(tables)}")

        cursor.close()
        conn.close()
        return True

    except Error as err:
        print(f"MySQL Error: {err}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == '__main__':
    # If running interactively and .env missing, show a note but do not auto-create secrets in CI
    if not os.path.exists(os.path.join(os.path.dirname(__file__), '.env')):
        print("Note: backend/.env not found. In deployment, provide DB credentials via Railway environment variables.")

    ok = setup_database()
    if ok:
        print("Database setup completed successfully")
    else:
        print("Database setup failed")
