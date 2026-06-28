import os
import smtplib
from email.message import EmailMessage
from typing import List, Union

class MailService:
    """
    A service class to securely manage and send emails via Gmail SMTP
    using system environment variables.
    """
    def __init__(self):
        # 1. Fetch credentials securely from the operating system
        self.smtp_user = os.environ.get("SMTP_USER")
        self.smtp_pass = os.environ.get("SMTP_PASS")
        
        # Fixed Gmail network infrastructure attributes
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

        # 2. Guard rail validation to catch missing configurations early
        if not self.smtp_user or not self.smtp_pass:
            raise ValueError(
                "Missing environment variables! Please configure 'SMTP_USER' "
                "and 'SMTP_PASS' on your system."
            )

    def send_mail(
        self, 
        to_email: Union[str, List[str]], 
        subject: str, 
        body: str, 
        is_html: bool = False
    ) -> bool:
        """
        Constructs and transmits an email.
        
        Args:
            to_email: A single recipient string or a list of recipient emails.
            subject: The email subject line.
            body: The text or HTML message payload content.
            is_html: Set to True if sending rich HTML formatting, default is False.
            
        Returns:
            bool: True if the email sent successfully, False otherwise.
        """
        # Formulate recipient list syntax
        recipients = [to_email] if isinstance(to_email, str) else to_email

        # 3. Assemble message payload structure
        msg = EmailMessage()
        msg["From"] = self.smtp_user
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        if is_html:
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        # 4. Connect, authenticate, and safely dispatch
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enforce transport-level encryption
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            print(f"Mail successfully dispatched to {len(recipients)} recipient(s).")
            return True

        except smtplib.SMTPAuthenticationError:
            print("Authentication failed! Verify your App Password and Email Address.")
            return False
        except Exception as e:
            print(f"Network or SMTP failure encountered: {e}")
            return False
