from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import json
import sqlite3
import os
from datetime import datetime

PORT = 3000

# ---- DATABASE SETUP ----
def init_db():
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS quotes')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT UNIQUE,
            author TEXT,
            category TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---- SERVER LOGIC ----
class MyServer(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/quote/clear':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            conn = sqlite3.connect('history.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM quotes')
            conn.commit()
            conn.close()
            
            self.wfile.write(json.dumps({'status': 'cleared'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_path = 'templates/index.html' if os.path.exists('templates/index.html') else 'index.html'
            with open(html_path, 'rb') as file:
                self.wfile.write(file.read())
                
        elif '/api/quote/random' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            selected_category = params.get('category', ['Inspirational'])[0]
            
            # Expanded array choices matching all requested drop-down categories
            fallback_options = {
                "Inspirational": [
                    ("Your limitation—it’s only your imagination.", "Unknown"),
                    ("Push yourself, because no one else is going to do it for you.", "Inspirational Quote"),
                    ("Great things never come from comfort zones.", "Motivation Engine")
                ],
                "Success & Life": [
                    ("The only way to do great work is to love what you do.", "Steve Jobs"),
                    ("Success doesn't just find you. You have to go out and get it.", "Anonymous"),
                    ("Dream it. Wish it. Do it.", "Life Guide")
                ],
                "Wisdom": [
                    ("Turn your wounds into wisdom.", "Oprah Winfrey"),
                    ("The only true wisdom is in knowing you know nothing.", "Socrates"),
                    ("Knowledge speaks, but wisdom listens.", "Jimi Hendrix")
                ],
                "Motivation": [
                    ("Action is the foundational key to all success.", "Pablo Picasso"),
                    ("Don't stop when you're tired. Stop when you're done.", "Athlete Mindset"),
                    ("Wake up with determination. Go to bed with satisfaction.", "Unknown")
                ],
                "Discipline & Focus": [
                    ("Discipline is choosing between what you want now and what you want most.", "Abraham Lincoln"),
                    ("Focus is a matter of deciding what things you're not going to do.", "John Carmack"),
                    ("Small daily improvements over time lead to stunning results.", "Robin Sharma")
                ],
                "Leadership": [
                    ("Leadership is not about being in charge. It is about taking care of those in your charge.", "Simon Sinek"),
                    ("An army of sheep led by a lion is better than an army of lions led by a sheep.", "Alexander the Great"),
                    ("Outstanding leaders go out of their way to boost the self-esteem of their personnel.", "Sam Walton")
                ],
                "Creativity": [
                    ("Creativity is intelligence having fun.", "Albert Einstein"),
                    ("You can't use up creativity. The more you use, the more you have.", "Maya Angelou"),
                    ("An essential aspect of creativity is not being afraid to fail.", "Edwin Land")
                ]
            }
            
            pool = fallback_options.get(selected_category, fallback_options["Inspirational"])
            
            conn = sqlite3.connect('history.db')
            cursor = conn.cursor()
            
            quote_text, quote_author = pool[0]
            for text_candidate, author_candidate in pool:
                cursor.execute('SELECT 1 FROM quotes WHERE text = ?', (text_candidate,))
                if not cursor.fetchone():
                    quote_text = text_candidate
                    quote_author = author_candidate
                    break
                    
            current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

            cursor.execute(
                'INSERT OR REPLACE INTO quotes (text, author, category, timestamp) VALUES (?, ?, ?, ?)', 
                (quote_text, quote_author, selected_category, current_time)
            )
            conn.commit()
            conn.close()

            res_obj = {'text': quote_text, 'author': quote_author, 'category': selected_category, 'timestamp': current_time}
            self.wfile.write(json.dumps(res_obj).encode('utf-8'))

        elif self.path == '/api/quote/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            conn = sqlite3.connect('history.db')
            cursor = conn.cursor()
            cursor.execute('SELECT text, author, category, timestamp FROM quotes ORDER BY id DESC LIMIT 10')
            rows = cursor.fetchall()
            conn.close()
            
            history_list = [{'text': row[0], 'author': row[1], 'category': row[2], 'timestamp': row[3]} for row in rows]
            self.wfile.write(json.dumps(history_list).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('', PORT), MyServer)
    print(f"Server successfully running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()