import os
from flask import Flask, render_template, request, jsonify
import razorpay
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret')

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")

SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/payment')
def payment():
    return render_template('payment.html', key_id=RAZORPAY_KEY_ID)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    payment_id = data.get('razorpay_payment_id')
    email = data.get('email', '')

    try:
        payment = client.payment.fetch(payment_id)
        if payment['status'] == 'captured':
            with open("paid_emails.txt", "a") as f:
                f.write(email + "\n")
            send_success_email(email)
            return jsonify({'status': 'success'})
    except Exception as e:
        print("Payment verification failed:", e)
    return jsonify({'status': 'failed'})

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

def send_success_email(to_email):
    subject = "✅ EnglishPro Course Access - Payment Successful"
    body = '''
Dear Student,

✅ Your payment was successful!

Here are your course access links:
📘 PDF Books: https://drive.google.com/drive/folders/1HNWohGqjIiy_TVEk_y710OrbDb0g-ae3
🎥 Video Lessons: https://drive.google.com/drive/folders/1EBzBgWNDUwv-gPvHZFO9pMP0Cs-e6hYU
📚 IELTS Pack: https://drive.google.com/drive/folders/1iqee_2QBbODOu8xis9BqPTOT0FHogzCi

Thanks for joining EnglishPro!
'''

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_EMAIL
    msg['To'] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
