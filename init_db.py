import sqlite3

# This creates a fresh database with all the required columns
conn = sqlite3.connect('quotes_history.db')
conn.execute('''CREATE TABLE history 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              content TEXT, 
              author TEXT, 
              category TEXT,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.close()
print("Database created successfully with 'category' and 'timestamp' columns!")