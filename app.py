from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
import os
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

def send_email_alert(name, email, issue, priority):
    sender_email = "yourgmail@gmail.com"
    sender_password = "your_app_password"  # NOT your normal password

    receiver_email = "yourgmail@gmail.com"

    subject = f"New Ticket Submitted - {priority}"
    body = f"""
New Ticket Created

Name: {name}
Email: {email}
Issue: {issue}
Priority: {priority}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
    except:
        print("Email failed")

# ✅ DATABASE CONNECTION
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# ✅ CREATE TABLE
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
    status TEXT DEFAULT 'Pending'
)
""")

    conn.commit()
    conn.close()

init_db()

# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "mufeed" and password == "4321":
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
    
    send_email_alert(name, email, issue, priority)

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
    from flask import jsonify
import requests

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message").lower()

    # Default priority
    priority = "Low"

    #  RULE-BASED RESPONSES
    if "login" in user_message:
        reply = "Login issue? Try resetting your password or check your credentials."
        priority = "Medium"

    elif "error" in user_message or "bug" in user_message:
        reply = "This looks like a technical issue. Please describe it clearly and set priority to HIGH."
        priority = "High"

    elif "slow" in user_message or "performance" in user_message:
        reply = "Performance issue detected. Usually MEDIUM priority. Mention where it's slow."
        priority = "Medium"

    elif "crash" in user_message or "down" in user_message:
        reply = "App crash is serious. Set priority to HIGH and include steps to reproduce."
        priority = "High"

    elif "ticket" in user_message:
        reply = "You can submit a ticket using the form. Fill all details and click submit."

    elif "hello" in user_message or "hi" in user_message:
        reply = "👋 Hey! I'm your AI assistant. Tell me your issue 😊"

    #  FREE AI FALLBACK (HuggingFace)
    else:
        API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

        try:
            response = requests.post(API_URL, json={"inputs": user_message})
            data = response.json()

            if isinstance(data, list) and "generated_text" in data[0]:
                reply = "🤖 " + data[0]["generated_text"]
            elif "error" in data:
                reply = "AI is waking up... try again in a few seconds."
            else:
                reply = "I understand your issue. Please provide more details so I can help better."

        except:
            reply = "AI unavailable. Please try again."

    #  Final response (ONLY ONE RETURN)
    return jsonify({
    "reply": reply,
    "autofill": {
        "issue": user_message,
        "priority": priority
    }
})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)