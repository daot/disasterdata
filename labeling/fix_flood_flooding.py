import sqlite3

database = './db-files/labeled/merged-labeled-reduced-2.db'

try:
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
except Exception as e:
    print(f"Error connecting to database: {e}")
    exit(0)

print("Connected to database successfully.")
table_name = "posts"

cursor.execute(f"UPDATE {table_name} set label='flood' WHERE label='flooding'")

connect.commit()

connect.close()

print("Completed.")
