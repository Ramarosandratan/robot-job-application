import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

async def send_application_email(recipient_email, job_title, company_name, cover_letter_text, cv_path=None):
    """
    Sends an application email with the provided details and an optional CV attachment.

    Args:
        recipient_email (str): The email address of the recipient.
        job_title (str): The title of the job being applied for.
        company_name (str): The name of the company.
        cover_letter_text (str): The content of the cover letter to be used as the email body.
        cv_path (str, optional): The path to the CV file to be attached. Defaults to None.

    Returns:
        bool: True if the email is sent successfully, False otherwise.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587)) # Default to 587 if not set

    if not all([sender_email, sender_password, smtp_server]):
        print("Error: Missing environment variables for email credentials.")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Application for {job_title} at {company_name}"

    msg.attach(MIMEText(cover_letter_text, 'plain'))

    if cv_path:
        try:
            with open(cv_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(cv_path)}",
            )
            msg.attach(part)
        except FileNotFoundError:
            print(f"Error: CV file not found at {cv_path}")
            return False
        except Exception as e:
            print(f"Error attaching CV: {e}")
            return False

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

if __name__ == "__main__":
    # Example usage (for testing purposes)
    # You would typically call send_application_email from another script
    # For local testing, ensure you have .env file with SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT
    import asyncio

    async def main():
        # Replace with actual values for testing
        test_recipient = "test@example.com"
        test_job_title = "Software Engineer"
        test_company_name = "Tech Solutions Inc."
        test_cover_letter = "Dear Hiring Manager, I am writing to express my interest in the Software Engineer position..."
        test_cv_path = "path/to/your/cv.pdf" # Make sure this file exists for testing attachment

        print(f"Attempting to send email to {test_recipient} for {test_job_title} at {test_company_name}...")
        success = await send_application_email(
            test_recipient,
            test_job_title,
            test_company_name,
            test_cover_letter,
            cv_path=None # Set to test_cv_path to test attachment
        )

        if success:
            print("Email sent successfully!")
        else:
            print("Failed to send email.")

    # asyncio.run(main()) # Uncomment to run the example