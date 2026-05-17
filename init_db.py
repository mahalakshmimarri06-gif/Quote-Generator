import sqlite3

def setup_database():
    conn = sqlite3.connect('quotes_history.db')
    cursor = conn.cursor()
    # Drop table if it exists to clean out previous column schema errors
    cursor.execute('DROP TABLE IF EXISTS history')
    # Build complete modern column structure
    cursor.execute('''CREATE TABLE history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  content TEXT, 
                  author TEXT, 
                  category TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    print("Database schema built with content, author, and category columns!")

if __name__ == '__main__':
    setup_database()