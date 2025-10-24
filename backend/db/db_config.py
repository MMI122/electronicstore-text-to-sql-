import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DATABASE', 'gadgets_store')
        self.pool_name = "gadgets_pool"
        self.pool_size = 10

    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def execute_query(self, query, params=None, fetch=False):
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                
                if fetch:
                    if query.strip().upper().startswith('SELECT'):
                        result = cursor.fetchall()
                    else:
                        result = cursor.fetchone()
                    return result
                else:
                    connection.commit()
                    return cursor.rowcount
            except Error as e:
                print(f"Error executing query: {e}")
                return None
            finally:
                cursor.close()
                connection.close()
        return None

    def execute_multiple_queries(self, queries):
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                results = []
                for query, params in queries:
                    cursor.execute(query, params or ())
                    if query.strip().upper().startswith('SELECT'):
                        results.append(cursor.fetchall())
                    else:
                        results.append(cursor.rowcount)
                connection.commit()
                return results
            except Error as e:
                connection.rollback()
                print(f"Error executing multiple queries: {e}")
                return None
            finally:
                cursor.close()
                connection.close()
        return None