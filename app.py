from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests

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

```
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
```

init_db()

# =========================

# EMAIL FUNCTION

# =========================

def send_email_alert(name, email, issue, priority):
sender_email = os.getenv("hanishzackariya12@gmail.com")
sender_password = os.getenv("zokj mvus eatq byqw")

```
receiver_email = sender_email

subject = f"New Ticket - {priority}"
body = f"""
```

New Ticket Created

Name: {name}
Email: {email}
Issue: {issue}
Priority: {priority}
"""

```
msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = sender_email
msg["To"] = f"{receiver_email}, {email}"

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, [receiver_email, email], msg.as_string())
    server.quit()
    print("Email sent")
except Exception as e:
    print("Email failed:", e)
```

# =========================

# ROUTES

# =========================

@app.route('/')
def home():
return render_template('form.html')

# SUBMIT TICKET

@app.route('/submit', methods=['POST'])
def submit():
name = request.form['name']
email = request.form['email']
issue = request.form['issue']
priority = request.form['priority']

```
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""
INSERT INTO tickets (name, email, description, priority, status, created_at)
VALUES (%s, %s, %s, %s, %s, %s)
""", (name, email, issue, priority, 'Open', datetime.now()))

conn.commit()
conn.close()

# SEND EMAIL
send_email_alert(name, email, issue, priority)

return redirect('/?success=1')
```

# LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():
if request.method == 'POST':
if request.form['username'] == "mufeed" and request.form['password'] == "4321":
session['user'] = "admin"
return redirect('/admin')
else:
return render_template('login.html', error="Invalid credentials")

```
return render_template('login.html')
```

# LOGOUT

@app.route('/logout')
def logout():
session.pop('user', None)
return redirect('/login')

# ADMIN PANEL

@app.route('/admin')
def admin():
if 'user' not in session:
return redirect('/login')

```
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
tickets = cursor.fetchall()

conn.close()

return render_template('admin.html', tickets=tickets)
```

# UPDATE STATUS

@app.route('/update_status/[int:id](int:id)/<status>')
def update_status(id, status):
if 'user' not in session:
return redirect('/login')

```
status = status.replace("_", " ")

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("UPDATE tickets SET status=%s WHERE id=%s", (status, id))

conn.commit()
conn.close()

return redirect('/admin')
```

# DELETE TICKET

@app.route('/delete/[int:id](int:id)')
def delete_ticket(id):
if 'user' not in session:
return redirect('/login')

```
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("DELETE FROM tickets WHERE id=%s", (id,))
conn.commit()
conn.close()

return redirect('/admin')
```

# =========================

# CHATBOT

# =========================

@app.route("/chat", methods=["POST"])
def chat():
user_message = request.json.get("message").lower()

```
priority = "Low"

if "login" in user_message:
    reply = "Login issue? Try resetting your password."
    priority = "Medium"

elif "error" in user_message or "bug" in user_message:
    reply = "This looks like a technical issue. Set priority HIGH."
    priority = "High"

elif "slow" in user_message:
    reply = "Performance issue. Set MEDIUM priority."
    priority = "Medium"

elif "crash" in user_message or "down" in user_message:
    reply = "App crash is serious. Set HIGH priority."
    priority = "High"

elif "hello" in user_message or "hi" in user_message:
    reply = "Hey! Tell me your issue 😊"

else:
    reply = "Tell me more about your issue."

# AUTO FILL
name = ""
email = ""

if "@" in user_message:
    email = user_message

elif "my name is" in user_message:
    name = user_message.replace("my name is", "").strip()

if name or email:
    reply = "Got it! I've filled the form for you 👍"

return jsonify({
    "reply": reply,
    "autofill": {
        "name": name,
        "email": email,
        "description": user_message,
        "priority": priority
    }
})
```

# =========================

# RUN

# =========================

if **name** == '**main**':
app.run(debug=True)
