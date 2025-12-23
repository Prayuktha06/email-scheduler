from flask import Flask, render_template, request, jsonify
from flask_apscheduler import APScheduler
from email.message import EmailMessage
from datetime import datetime
import smtplib
import uuid

app = Flask(__name__)

# APScheduler configuration
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


def send_email(sender, password, receiver, subject, message):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.set_content(message)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/schedule", methods=["POST"])
def schedule_email():
    try:
        data = request.json

        sender = data.get("sender")
        password = data.get("password")
        receiver = data.get("receiver")
        subject = data.get("subject")
        message = data.get("message")
        schedule_time = datetime.strptime(data.get("datetime"), "%Y-%m-%dT%H:%M")

        # Step 1: Test Gmail login
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
        except Exception:
            return jsonify({
                "status": "error",
                "message": "Invalid Gmail or App Password"
            })

        # Step 2: Schedule email (FIXED ID ISSUE)
        scheduler.add_job(
            id=str(uuid.uuid4()),
            func=send_email,
            trigger="date",
            run_date=schedule_time,
            args=[sender, password, receiver, subject, message]
        )

        return jsonify({
            "status": "success",
            "message": "Email scheduled successfully"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e) if str(e) else "Something went wrong"
        })


if __name__ == "__main__":
    app.run(debug=True)
