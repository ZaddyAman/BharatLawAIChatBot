import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

def test_email():
    try:
        print("Testing SMTP connection...")
        print(f"Server: {SMTP_SERVER}")
        print(f"Port: {SMTP_PORT}")
        print(f"Username: {SMTP_USERNAME}")
        print(f"Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")

        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("ERROR: SMTP_USERNAME or SMTP_PASSWORD not set in .env")
            return

        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = SMTP_USERNAME  # Send to yourself
        msg['Subject'] = "SMTP Test - BharatLaw AI"

        body = "This is a test email from BharatLaw AI SMTP configuration."
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        print("Attempting to send test email...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, SMTP_USERNAME, msg.as_string())
        server.quit()

        print("SUCCESS: Test email sent successfully!")
        print("Check your inbox for the test email")

    except smtplib.SMTPAuthenticationError as e:
        print(f"AUTHENTICATION ERROR: {e}")
        print("Check your app password is correct")
    except smtplib.SMTPConnectError as e:
        print(f"CONNECTION ERROR: {e}")
        print("Check SMTP_SERVER and SMTP_PORT")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_email()