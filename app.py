from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3

app = Flask(__name__)

def get_quote(category=""):
    try:
        # Step 2 & 3: Get data from External API
        url = f"https://api.quotable.io/random?tags={category.lower()}" if category else "https://api.quotable.io/random"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['content'], data['author']
    except:
        return "Failure is the opportunity to begin again more intelligently.", "Henry Ford"

@app.route('/')
def index():
    conn = sqlite3.connect('quotes_history.db')
    conn.row_factory = sqlite3.Row
    # Step 5: Refresh History
    history = conn.execute('SELECT content, author, timestamp FROM history ORDER BY timestamp DESC').fetchall()
    conn.close()
    current = history[0] if history else None
    return render_template('index.html', history=history, current=current)

@app.route('/generate', methods=['POST'])
def generate():
    # Step 1: User Request
    interest = request.form.get('interest', '')
    content, author = get_quote(interest)
    
    # Step 4b: Save to Database with the 'category' column
    conn = sqlite3.connect('quotes_history.db')
    conn.execute('INSERT INTO history (content, author, category) VALUES (?, ?, ?)', 
                 (content, author, interest))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)