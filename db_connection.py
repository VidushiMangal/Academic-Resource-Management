import sqlite3
import pandas as pd

def connect_and_query_sqlite(db_path, query):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

#create a database file
db_file = "my_database.db"

#create a connection
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

#create a table
cursor.execute('''CREATE TABLE IF NOT EXISTS students
               (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')

#insert some data
cursor.execute("INSERT INTO students (name, age) VALUES ('Alice', 20)")
cursor.execute("INSERT INTO students (name, age) VALUES ('Bob', 22)")
conn.commit()
conn.close()

sql_query = "SELECT * FROM students;"
result_df = connect_and_query_sqlite(db_file, sql_query)

if result_df is not None:
    print(result_df)