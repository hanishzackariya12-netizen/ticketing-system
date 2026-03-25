from flask import Flask, render_template, request, redirect, session
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ DATABASE CONNECTION
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# ✅ CREATE TABLE
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id SERIAL PRIMARY KEY,
        name TEXT,
        email TEXT,
        issue TEXT,
        priority TEXT,
        status TEXT,
        created_at TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

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

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO tickets (name, email, issue, priority, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    ''', (name, email, issue, priority, 'Open', datetime.now()))

    conn.commit()
    conn.close()

    return redirect('/?success=1')

# 🧑‍💼 ADMIN
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
    tickets = cursor.fetchall()

    conn.close()

    return render_template('admin.html', tickets=tickets)

# 🔄 UPDATE STATUS
@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):
    if 'user' not in session:
        return redirect('/login')

    status = status.replace("_", " ")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE tickets SET status=%s WHERE id=%s", (status, id))

    conn.commit()
    conn.close()

    return redirect('/admin')

# 🗑 DELETE
@app.route('/delete/<int:id>')
def delete_ticket(id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tickets WHERE id=%s", (id,))

    conn.commit()
    conn.close()

    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
