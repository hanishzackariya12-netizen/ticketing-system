from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
import os
import smtplib
import re
import requests
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# =========================
# DATABASE CONNECTION
# =========================

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# =========================
# INIT DATABASE
# =========================

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            description TEXT,
            priority TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()  # Fixed: was init_db()() (double call)

# =========================
# EMAIL FUNCTION
# =========================

def send_email_alert(name, email, issue, priority):
    # Fixed: hardcoded credentials instead of broken os.getenv() calls
    sender_email = "hanishzackariya12@gmail.com"
    sender_password = "zokj mvus eatq byqw"

    if not sender_email or not sender_password:
        print("Email env variables not set")
        return

    subject = f"New Ticket - {priority}"
    body = f"""New Ticket Created
Name: {name}
Email: {email}
Issue: {issue}
Priority: {priority}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = sender_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [sender_email, email], msg.as_string())
        server.quit()
        print("Email sent")
    except Exception as e:
        print("Email failed:", e)

# =========================
# ROUTES
# =========================

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    issue = request.form.get('issue')
    priority = request.form.get('priority')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets (name, email, issue, priority, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, email, issue, priority, 'Open', datetime.now()))

    conn.commit()
    conn.close()

    send_email_alert(name, email, issue, priority)

    return redirect('/?success=1')

@app.route("/fix-db")
def fix_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("ALTER TABLE tickets ADD COLUMN description TEXT;")

        conn.commit()
        conn.close()

        return "✅ Database fixed successfully!"

    except Exception as e:
        return f"❌ Error: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == "mufeed" and request.form.get('password') == "4321":
            session['user'] = "admin"
            return redirect('/admin')
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

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

@app.route('/update_status/<int:id>/<status>')  # Fixed: malformed route syntax
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

@app.route('/delete/<int:id>')  # Fixed: malformed route syntax
def delete_ticket(id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tickets WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

# =========================
# CHATBOT
# =========================

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    lower_msg = user_message.lower()
    priority = "Low"
    reply = None

    # ⚡ FAST SMART RULES (for UX)
    if "login" in lower_msg:
        reply = "Try resetting your password or checking credentials."
        priority = "Medium"

    elif "error" in lower_msg or "bug" in lower_msg:
        reply = "This seems like a technical issue. Set priority HIGH."
        priority = "High"

    elif "slow" in lower_msg:
        reply = "Performance issue. Usually MEDIUM priority."
        priority = "Medium"

    elif "crash" in lower_msg:
        reply = "Crash detected. Set HIGH priority and describe steps."
        priority = "High"

    # 🧠 SMART EXTRACTION
    name = ""
    email = ""
    issue = ""

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_message)
    if email_match:
        email = email_match.group()

    if "my name is" in lower_msg:
        name = lower_msg.replace("my name is", "").strip()

    if not name and not email:
        issue = user_message

    # 🤖 AI FALLBACK (REAL AI)
    if not reply:
        try:
            API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

            response = requests.post(API_URL, json={
                "inputs": f"User: {user_message}\nAI:"
            })

            data = response.json()

            if isinstance(data, list) and "generated_text" in data[0]:
                reply = data[0]["generated_text"]

            else:
                reply = "I understand. Can you give more details?"

        except:
            reply = "AI is temporarily unavailable. Try again."

    # 🎯 SMART RESPONSE OVERRIDE
    if email:
        reply = f"Got your email: {email} 📩"

    elif name:
        reply = f"Nice to meet you, {name}! 👋"

    elif issue and not reply:
        reply = "Got your issue. I'll help you with that 👍"

    return jsonify({
        "reply": reply,
        "autofill": {
            "name": name,
            "email": email,
            "issue": issue,
            "priority": priority
        }
    })

if __name__ == "__main__":
    app.run(debug=True)