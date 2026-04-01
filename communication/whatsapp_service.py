import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body, sender_email, sender_password):

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # 🔥 SMTP CONFIG (auto detect)
    if "gmail" in sender_email:
        smtp_server = "smtp.gmail.com"
        port = 587
    elif "outlook" in sender_email or "hotmail" in sender_email:
        smtp_server = "smtp.office365.com"
        port = 587
    elif "yahoo" in sender_email:
        smtp_server = "smtp.mail.yahoo.com"
        port = 587
    else:
        raise Exception("Unsupported email provider")

    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, sender_password)

    server.send_message(msg)
    server.quit()

    print("📩 Email sent successfully")