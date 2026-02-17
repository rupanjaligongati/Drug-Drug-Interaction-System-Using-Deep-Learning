"""
Email Service
Handles sending OTP verification emails to users
"""

import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
FROM_NAME = os.getenv("FROM_NAME", "DDI System")

# OTP configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10


class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def generate_otp(length: int = OTP_LENGTH) -> str:
        """
        Generate a random OTP code
        
        Args:
            length: Length of OTP (default: 6)
            
        Returns:
            Random OTP string
        """
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Check if email is configured
            if not SMTP_USERNAME or not SMTP_PASSWORD:
                logger.warning("Email not configured. OTP: Check console for development mode.")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
            msg['To'] = to_email
            
            # Attach text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_otp_email(to_email: str, otp: str, user_name: str) -> bool:
        """
        Send OTP verification email
        
        Args:
            to_email: Recipient email address
            otp: OTP code
            user_name: User's name
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Verify Your Email - DDI System"
        
        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f7fa;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background-color: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #333;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    color: #555;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .otp-box {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-size: 36px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px;
                    margin: 30px 0;
                }}
                .expiry {{
                    text-align: center;
                    color: #e74c3c;
                    font-size: 14px;
                    margin-top: 15px;
                    font-weight: 500;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px 30px;
                    text-align: center;
                    font-size: 13px;
                    color: #777;
                    border-top: 1px solid #e9ecef;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .warning p {{
                    margin: 0;
                    color: #856404;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Drug-Drug Interaction System</h1>
                </div>
                <div class="content">
                    <p class="greeting">Hello {user_name},</p>
                    <p class="message">
                        Thank you for registering with the Drug-Drug Interaction System! 
                        To complete your registration and verify your email address, please use the following One-Time Password (OTP):
                    </p>
                    <div class="otp-box">
                        {otp}
                    </div>
                    <p class="expiry">⏰ This OTP will expire in {OTP_EXPIRY_MINUTES} minutes</p>
                    <div class="warning">
                        <p>
                            <strong>⚠️ Security Notice:</strong> If you did not request this verification, 
                            please ignore this email. Never share your OTP with anyone.
                        </p>
                    </div>
                </div>
                <div class="footer">
                    <p>© 2026 Drug-Drug Interaction System | Healthcare Decision Support</p>
                    <p style="margin-top: 10px; font-size: 12px;">
                        This is an automated email. Please do not reply to this message.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        Hello {user_name},
        
        Thank you for registering with the Drug-Drug Interaction System!
        
        Your OTP verification code is: {otp}
        
        This OTP will expire in {OTP_EXPIRY_MINUTES} minutes.
        
        If you did not request this verification, please ignore this email.
        
        © 2026 Drug-Drug Interaction System
        """
        
        return EmailService.send_email(to_email, subject, html_content, text_content)
    
    @staticmethod
    def send_welcome_email(to_email: str, user_name: str) -> bool:
        """
        Send welcome email after successful verification
        
        Args:
            to_email: Recipient email address
            user_name: User's name
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Welcome to DDI System - Email Verified!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f7fa;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background-color: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .success-icon {{
                    text-align: center;
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    color: #555;
                    line-height: 1.6;
                    margin-bottom: 20px;
                }}
                .features {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .features h3 {{
                    color: #333;
                    margin-top: 0;
                }}
                .features ul {{
                    list-style: none;
                    padding: 0;
                }}
                .features li {{
                    padding: 8px 0;
                    color: #555;
                }}
                .features li:before {{
                    content: "✓ ";
                    color: #38ef7d;
                    font-weight: bold;
                    margin-right: 8px;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px 30px;
                    text-align: center;
                    font-size: 13px;
                    color: #777;
                    border-top: 1px solid #e9ecef;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Welcome to DDI System!</h1>
                </div>
                <div class="content">
                    <div class="success-icon">✅</div>
                    <p class="message">
                        <strong>Congratulations, {user_name}!</strong><br><br>
                        Your email has been successfully verified. You now have full access to the 
                        Drug-Drug Interaction System.
                    </p>
                    <div class="features">
                        <h3>What you can do:</h3>
                        <ul>
                            <li>Predict drug-drug interactions using AI</li>
                            <li>Get explainable AI insights</li>
                            <li>Receive alternative drug recommendations</li>
                            <li>Track your interaction history</li>
                            <li>Access analytics dashboard</li>
                            <li>Upload and analyze prescription images</li>
                        </ul>
                    </div>
                    <p class="message">
                        <strong>⚠️ Medical Disclaimer:</strong><br>
                        This system is for educational and decision-support purposes only. 
                        Always consult with healthcare professionals before making medical decisions.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2026 Drug-Drug Interaction System | Healthcare Decision Support</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Congratulations, {user_name}!
        
        Your email has been successfully verified. You now have full access to the Drug-Drug Interaction System.
        
        What you can do:
        - Predict drug-drug interactions using AI
        - Get explainable AI insights
        - Receive alternative drug recommendations
        - Track your interaction history
        - Access analytics dashboard
        - Upload and analyze prescription images
        
        Medical Disclaimer: This system is for educational purposes only. 
        Always consult with healthcare professionals.
        
        © 2026 Drug-Drug Interaction System
        """
        
        return EmailService.send_email(to_email, subject, html_content, text_content)


# Create singleton instance
email_service = EmailService()
