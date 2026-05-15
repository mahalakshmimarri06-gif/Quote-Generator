import sqlite3
# Connect to the existing database
conn = sqlite3.connect('quotes_history.db')
cursor = conn.cursor()
# Drop the old table to clear the "no column named category" error
cursor.execute('DROP TABLE IF EXISTS history')
# Create the new table with the required columns for Task-4
cursor.execute('''CREATE TABLE history 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              content TEXT, 
              author TEXT, 
              category TEXT,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()
conn.close()
print("Database has been reset successfully!")