from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"  # required for login

# Create database
def init_db():
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        issue TEXT,
        priority TEXT,
        status TEXT,
        created_at TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()


# 🔐 LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # simple login (you can change later)
        if username == "Hanish" and password == "4321":
            session['user'] = username
            return redirect('/admin')
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


# 🔓 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# 🏠 HOME
@app.route('/')
def home():
    return render_template('form.html')


# ➕ SUBMIT
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    issue = request.form['issue']
    priority = request.form['priority']

    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO tickets (name, email, issue, priority, status, created_at)
    VALUES (?, ?, ?, ?, 'Open', ?)
    ''', (name, email, issue, priority, datetime.now()))

    conn.commit()
    conn.close()

    return redirect('/?success=1')


# 🧑‍💼 ADMIN (PROTECTED)
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    conn.close()

    return render_template('admin.html', tickets=tickets)


# 🔄 UPDATE STATUS
@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):
    if 'user' not in session:
        return redirect('/login')

    status = status.replace("_", " ")

    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()

    return redirect('/admin')


# 🗑 DELETE
@app.route('/delete/<int:id>')
def delete_ticket(id):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
