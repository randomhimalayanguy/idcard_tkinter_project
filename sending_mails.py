import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import os
import mimetypes

# Email configuration
SENDER_EMAIL = "healthmonitoring00@gmail.com"
RECEIVER_EMAIL = "baliyanvdit@gmail.com"
PASSWORD = ""  # Replace with your actual email password
SUBJECT = "Subject of the Email"

def send_email(receiver_email,subject="College_id_card", body="hi this is your id card", sender_email=SENDER_EMAIL, password=PASSWORD, attachment_path=None):
    """
    Send an email using the SMTP protocol with an optional attachment.

    Args:
        subject (str): Subject of the email.
        body (str): Body content of the email.
        sender_email (str): Sender's email address.
        receiver_email (str): Receiver's email address.
        password (str): Password for the sender's email account.
        attachment_path (str, optional): Path to the file to attach. Defaults to None.
    """
    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add the email body
    message.attach(MIMEText(body, "plain"))

    # Add the attachment
    if attachment_path and os.path.isfile(attachment_path):
        with open(attachment_path, "rb") as attachment_file:
            # Determine the MIME type of the attachment
            mime_type, _ = mimetypes.guess_type(attachment_path)
            mime_type = mime_type or "application/octet-stream"
            main_type, sub_type = mime_type.split("/", 1)

            if main_type == "image":
                attachment = MIMEImage(attachment_file.read(), _subtype=sub_type)
            else:
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(attachment_file.read())
                encoders.encode_base64(attachment)
            
            attachment.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
            message.attach(attachment)
    else:
        print(f"Attachment not found: {attachment_path}")

    try:
        # Connect to the SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()  # Identify ourselves to smtp.gmail.com
            server.starttls()  # Secure the connection
            server.ehlo()  # Re-identify ourselves after TLS
            server.login(sender_email, password)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

