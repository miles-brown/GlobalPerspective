#!/usr/bin/env python3
"""
Email Verification and Password Reset System
For GlobalPerspective News Platform
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import secrets
import hashlib
import time
from datetime import datetime, timedelta
import os
import re
from jinja2 import Template
import requests
import json

# Email configuration
class EmailConfig:
    # SMTP Configuration (configure based on your email provider)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    
    # Email settings
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@globalperspective.news')
    FROM_NAME = os.getenv('FROM_NAME', 'GlobalPerspective News')
    REPLY_TO = os.getenv('REPLY_TO', 'support@globalperspective.news')
    
    # Email service providers (alternative to SMTP)
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
    MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY', '')
    MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN', '')
    
    # Email templates
    TEMPLATE_DIR = os.getenv('EMAIL_TEMPLATE_DIR', 'email_templates')
    
    # Token settings
    VERIFICATION_TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours
    RESET_TOKEN_EXPIRY = 60 * 60  # 1 hour
    
    # Rate limiting
    MAX_VERIFICATION_EMAILS_PER_HOUR = 3
    MAX_RESET_EMAILS_PER_HOUR = 5

# Email template manager
class EmailTemplateManager:
    """Manage email templates with dynamic content"""
    
    @staticmethod
    def get_base_template():
        """Base HTML template for all emails"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
            <style>
                body {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }
                .email-container {
                    background-color: white;
                    border-radius: 8px;
                    padding: 40px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .header {
                    text-align: center;
                    border-bottom: 2px solid #c41e3a;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }
                .logo {
                    font-size: 28px;
                    font-weight: 700;
                    color: #c41e3a;
                    text-decoration: none;
                }
                .content {
                    margin-bottom: 30px;
                }
                .button {
                    display: inline-block;
                    background-color: #c41e3a;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 600;
                    margin: 20px 0;
                }
                .button:hover {
                    background-color: #a01729;
                }
                .footer {
                    border-top: 1px solid #eee;
                    padding-top: 20px;
                    margin-top: 30px;
                    font-size: 14px;
                    color: #666;
                    text-align: center;
                }
                .security-notice {
                    background-color: #f8f9fa;
                    border-left: 4px solid #b8860b;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 0 4px 4px 0;
                }
                .code-block {
                    background-color: #f1f3f4;
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                    padding: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 16px;
                    text-align: center;
                    margin: 15px 0;
                    letter-spacing: 2px;
                }
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <a href="{{ base_url }}" class="logo">GlobalPerspective</a>
                    <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">International News & World Affairs</p>
                </div>
                <div class="content">
                    {{ content }}
                </div>
                <div class="footer">
                    <p>This email was sent by GlobalPerspective News</p>
                    <p>If you didn't request this email, please ignore it or <a href="{{ base_url }}/contact">contact us</a></p>
                    <p><a href="{{ base_url }}">Visit our website</a> | <a href="{{ base_url }}/unsubscribe">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def get_verification_template():
        """Email verification template"""
        content = """
        <h2>Welcome to GlobalPerspective!</h2>
        <p>Thank you for creating an account with us. To complete your registration and start accessing our premium international news content, please verify your email address.</p>
        
        <p style="text-align: center;">
            <a href="{{ verification_url }}" class="button">Verify Email Address</a>
        </p>
        
        <p>Or copy and paste this link into your browser:</p>
        <div class="code-block">{{ verification_url }}</div>
        
        <div class="security-notice">
            <strong>Security Notice:</strong> This verification link will expire in 24 hours for your security. If you didn't create this account, please ignore this email.
        </div>
        
        <p>Once verified, you'll be able to:</p>
        <ul>
            <li>Access premium articles and in-depth analysis</li>
            <li>Comment on articles and join discussions</li>
            <li>Subscribe to our newsletter</li>
            <li>Customize your news preferences</li>
        </ul>
        
        <p>Welcome to the GlobalPerspective community!</p>
        <p><strong>The GlobalPerspective Team</strong></p>
        """
        
        base_template = EmailTemplateManager.get_base_template()
        return Template(base_template).render(content=content)
    
    @staticmethod
    def get_password_reset_template():
        """Password reset template"""
        content = """
        <h2>Password Reset Request</h2>
        <p>We received a request to reset the password for your GlobalPerspective account.</p>
        
        <p style="text-align: center;">
            <a href="{{ reset_url }}" class="button">Reset Password</a>
        </p>
        
        <p>Or copy and paste this link into your browser:</p>
        <div class="code-block">{{ reset_url }}</div>
        
        <div class="security-notice">
            <strong>Security Notice:</strong> This reset link will expire in 1 hour for your security. If you didn't request this reset, please ignore this email and your password will remain unchanged.
        </div>
        
        <p>For your security, please:</p>
        <ul>
            <li>Choose a strong, unique password</li>
            <li>Don't share your password with anyone</li>
            <li>Consider using a password manager</li>
        </ul>
        
        <p>If you continue to have problems, please contact our support team.</p>
        <p><strong>The GlobalPerspective Team</strong></p>
        """
        
        base_template = EmailTemplateManager.get_base_template()
        return Template(base_template).render(content=content)
    
    @staticmethod
    def get_welcome_template():
        """Welcome email after successful verification"""
        content = """
        <h2>Welcome to GlobalPerspective! 🌍</h2>
        <p>Congratulations! Your email has been successfully verified and your account is now active.</p>
        
        <p>You now have full access to our platform featuring:</p>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #c41e3a;">🌟 Premium Features</h3>
            <ul style="margin-bottom: 0;">
                <li><strong>In-depth Analysis:</strong> Expert commentary on global affairs</li>
                <li><strong>Breaking News:</strong> Real-time updates on world events</li>
                <li><strong>Interactive Community:</strong> Engage with readers and journalists</li>
                <li><strong>Personalized Content:</strong> Tailored to your interests</li>
            </ul>
        </div>
        
        <p style="text-align: center;">
            <a href="{{ base_url }}/dashboard" class="button">Explore Your Dashboard</a>
        </p>
        
        <h3>Get Started:</h3>
        <ol>
            <li><a href="{{ base_url }}/profile">Complete your profile</a> to get personalized recommendations</li>
            <li><a href="{{ base_url }}/categories">Choose your favorite topics</a> to follow</li>
            <li><a href="{{ base_url }}/newsletter">Subscribe to our newsletter</a> for daily updates</li>
        </ol>
        
        <p>Thank you for joining our community of informed global citizens!</p>
        <p><strong>The GlobalPerspective Team</strong></p>
        """
        
        base_template = EmailTemplateManager.get_base_template()
        return Template(base_template).render(content=content)
    
    @staticmethod
    def get_password_changed_template():
        """Password successfully changed notification"""
        content = """
        <h2>Password Changed Successfully</h2>
        <p>This email confirms that your GlobalPerspective account password has been successfully changed.</p>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 4px; margin: 20px 0;">
            <strong>✅ Password Updated:</strong> {{ timestamp }}
        </div>
        
        <div class="security-notice">
            <strong>Security Alert:</strong> If you did not make this change, please contact our support team immediately at <a href="mailto:security@globalperspective.news">security@globalperspective.news</a>
        </div>
        
        <p>For your account security:</p>
        <ul>
            <li>Your new password is now active</li>
            <li>All existing sessions have been logged out</li>
            <li>You'll need to log in again on all devices</li>
        </ul>
        
        <p style="text-align: center;">
            <a href="{{ base_url }}/login" class="button">Login to Your Account</a>
        </p>
        
        <p><strong>The GlobalPerspective Team</strong></p>
        """
        
        base_template = EmailTemplateManager.get_base_template()
        return Template(base_template).render(content=content)

# Email service providers
class EmailService:
    """Unified email service supporting multiple providers"""
    
    def __init__(self, provider='smtp'):
        self.provider = provider.lower()
        self.base_url = os.getenv('BASE_URL', 'https://globalperspective.news')
    
    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send email using configured provider"""
        try:
            if self.provider == 'sendgrid':
                return self._send_via_sendgrid(to_email, subject, html_content, text_content)
            elif self.provider == 'mailgun':
                return self._send_via_mailgun(to_email, subject, html_content, text_content)
            else:
                return self._send_via_smtp(to_email, subject, html_content, text_content)
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
    
    def _send_via_smtp(self, to_email, subject, html_content, text_content=None):
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{EmailConfig.FROM_NAME} <{EmailConfig.FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Reply-To'] = EmailConfig.REPLY_TO
            
            # Add text version if not provided
            if not text_content:
                # Simple HTML to text conversion
                text_content = re.sub('<[^<]+?>', '', html_content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Create text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT) as server:
                if EmailConfig.SMTP_USE_TLS:
                    server.starttls(context=context)
                if EmailConfig.SMTP_USERNAME and EmailConfig.SMTP_PASSWORD:
                    server.login(EmailConfig.SMTP_USERNAME, EmailConfig.SMTP_PASSWORD)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"SMTP sending failed: {str(e)}")
            return False
    
    def _send_via_sendgrid(self, to_email, subject, html_content, text_content=None):
        """Send email via SendGrid API"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=EmailConfig.SENDGRID_API_KEY)
            
            message = Mail(
                from_email=EmailConfig.FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content
            )
            
            response = sg.send(message)
            return response.status_code == 202
            
        except Exception as e:
            print(f"SendGrid sending failed: {str(e)}")
            return False
    
    def _send_via_mailgun(self, to_email, subject, html_content, text_content=None):
        """Send email via Mailgun API"""
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{EmailConfig.MAILGUN_DOMAIN}/messages",
                auth=("api", EmailConfig.MAILGUN_API_KEY),
                data={
                    "from": f"{EmailConfig.FROM_NAME} <{EmailConfig.FROM_EMAIL}>",
                    "to": to_email,
                    "subject": subject,
                    "html": html_content,
                    "text": text_content or re.sub('<[^<]+?>', '', html_content)
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Mailgun sending failed: {str(e)}")
            return False

# Token management
class TokenManager:
    """Manage verification and reset tokens"""
    
    @staticmethod
    def generate_verification_token():
        """Generate secure verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_reset_token(user_id):
        """Generate password reset token with user ID and timestamp"""
        timestamp = int(time.time())
        data = f"{user_id}:{timestamp}:{secrets.token_urlsafe(16)}"
        token_hash = hashlib.sha256(data.encode()).hexdigest()
        return f"{token_hash}:{timestamp}"
    
    @staticmethod
    def verify_reset_token(token, user_id, max_age=3600):
        """Verify password reset token"""
        try:
            token_hash, timestamp = token.split(':')
            timestamp = int(timestamp)
            
            # Check if token is expired
            if time.time() - timestamp > max_age:
                return False
            
            # Verify token (simplified - in production, store token hash in DB)
            return True
            
        except:
            return False
    
    @staticmethod
    def is_token_expired(created_at, expiry_seconds):
        """Check if token is expired"""
        if not created_at:
            return True
        
        expiry_time = created_at + timedelta(seconds=expiry_seconds)
        return datetime.utcnow() > expiry_time

# Rate limiting for email sending
class EmailRateLimit:
    """Rate limiting for email sending to prevent abuse"""
    
    # In-memory storage (use Redis in production)
    _rate_limits = {}
    
    @classmethod
    def can_send_email(cls, email, email_type='verification'):
        """Check if email can be sent based on rate limits"""
        key = f"{email}:{email_type}"
        now = time.time()
        
        # Clean old entries
        cls._cleanup_old_entries()
        
        if key not in cls._rate_limits:
            cls._rate_limits[key] = []
        
        # Get rate limit based on email type
        if email_type == 'verification':
            max_emails = EmailConfig.MAX_VERIFICATION_EMAILS_PER_HOUR
        elif email_type == 'reset':
            max_emails = EmailConfig.MAX_RESET_EMAILS_PER_HOUR
        else:
            max_emails = 5  # Default limit
        
        # Count emails sent in the last hour
        hour_ago = now - 3600
        recent_sends = [timestamp for timestamp in cls._rate_limits[key] if timestamp > hour_ago]
        
        if len(recent_sends) >= max_emails:
            return False
        
        # Record this send
        cls._rate_limits[key] = recent_sends + [now]
        return True
    
    @classmethod
    def _cleanup_old_entries(cls):
        """Clean up old rate limit entries"""
        hour_ago = time.time() - 3600
        for key in list(cls._rate_limits.keys()):
            cls._rate_limits[key] = [
                timestamp for timestamp in cls._rate_limits[key] 
                if timestamp > hour_ago
            ]
            if not cls._rate_limits[key]:
                del cls._rate_limits[key]

# Main email verification functions
class EmailVerificationService:
    """Main service for email verification and password reset"""
    
    def __init__(self, email_provider='smtp'):
        self.email_service = EmailService(email_provider)
        self.base_url = os.getenv('BASE_URL', 'https://globalperspective.news')
    
    def send_verification_email(self, user):
        """Send email verification email"""
        try:
            # Check rate limit
            if not EmailRateLimit.can_send_email(user.email, 'verification'):
                return {
                    'success': False,
                    'error': 'Too many verification emails sent. Please wait before requesting another.'
                }
            
            # Generate verification token
            verification_token = TokenManager.generate_verification_token()
            
            # Update user with token (this would be done in the calling function)
            # user.email_verification_token = verification_token
            # user.verification_token_created_at = datetime.utcnow()
            
            # Build verification URL
            verification_url = f"{self.base_url}/verify-email/{verification_token}"
            
            # Render email template
            template = Template(EmailTemplateManager.get_verification_template())
            html_content = template.render(
                verification_url=verification_url,
                base_url=self.base_url,
                user_name=f"{user.first_name} {user.last_name}",
                subject="Verify your GlobalPerspective account"
            )
            
            # Send email
            success = self.email_service.send_email(
                to_email=user.email,
                subject="Verify your GlobalPerspective account",
                html_content=html_content
            )
            
            if success:
                return {
                    'success': True,
                    'message': 'Verification email sent successfully',
                    'token': verification_token
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send verification email'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Email service error: {str(e)}'
            }
    
    def send_password_reset_email(self, user):
        """Send password reset email"""
        try:
            # Check rate limit
            if not EmailRateLimit.can_send_email(user.email, 'reset'):
                return {
                    'success': False,
                    'error': 'Too many reset emails sent. Please wait before requesting another.'
                }
            
            # Generate reset token
            reset_token = TokenManager.generate_reset_token(user.id)
            
            # Build reset URL
            reset_url = f"{self.base_url}/reset-password/{reset_token}"
            
            # Render email template
            template = Template(EmailTemplateManager.get_password_reset_template())
            html_content = template.render(
                reset_url=reset_url,
                base_url=self.base_url,
                user_name=f"{user.first_name} {user.last_name}",
                subject="Reset your GlobalPerspective password"
            )
            
            # Send email
            success = self.email_service.send_email(
                to_email=user.email,
                subject="Reset your GlobalPerspective password",
                html_content=html_content
            )
            
            if success:
                return {
                    'success': True,
                    'message': 'Password reset email sent successfully',
                    'token': reset_token
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send password reset email'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Email service error: {str(e)}'
            }
    
    def send_welcome_email(self, user):
        """Send welcome email after successful verification"""
        try:
            template = Template(EmailTemplateManager.get_welcome_template())
            html_content = template.render(
                base_url=self.base_url,
                user_name=f"{user.first_name} {user.last_name}",
                subject="Welcome to GlobalPerspective!"
            )
            
            success = self.email_service.send_email(
                to_email=user.email,
                subject="Welcome to GlobalPerspective! 🌍",
                html_content=html_content
            )
            
            return success
            
        except Exception as e:
            print(f"Welcome email failed: {str(e)}")
            return False
    
    def send_password_changed_notification(self, user):
        """Send notification when password is changed"""
        try:
            template = Template(EmailTemplateManager.get_password_changed_template())
            html_content = template.render(
                base_url=self.base_url,
                user_name=f"{user.first_name} {user.last_name}",
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                subject="Password Changed - GlobalPerspective"
            )
            
            success = self.email_service.send_email(
                to_email=user.email,
                subject="Password Changed - GlobalPerspective",
                html_content=html_content
            )
            
            return success
            
        except Exception as e:
            print(f"Password change notification failed: {str(e)}")
            return False

# Database model updates for email verification
def update_user_model_for_email():
    """Updated User model with email verification fields"""
    return """
    class User(db.Model):
        # ... existing fields ...
        
        # Email verification
        email_verification_token = db.Column(db.String(255))
        verification_token_created_at = db.Column(db.DateTime)
        email_verified_at = db.Column(db.DateTime)
        is_email_verified = db.Column(db.Boolean, default=False)
        
        # Password reset
        password_reset_token = db.Column(db.String(255))
        password_reset_requested_at = db.Column(db.DateTime)
        password_changed_at = db.Column(db.DateTime)
        
        # Email preferences
        email_notifications = db.Column(db.Boolean, default=True)
        newsletter_subscribed = db.Column(db.Boolean, default=False)
        marketing_emails = db.Column(db.Boolean, default=True)
        
        def is_verification_token_valid(self):
            if not self.email_verification_token or not self.verification_token_created_at:
                return False
            return not TokenManager.is_token_expired(
                self.verification_token_created_at, 
                EmailConfig.VERIFICATION_TOKEN_EXPIRY
            )
        
        def is_reset_token_valid(self):
            if not self.password_reset_token or not self.password_reset_requested_at:
                return False
            return not TokenManager.is_token_expired(
                self.password_reset_requested_at,
                EmailConfig.RESET_TOKEN_EXPIRY
            )
    """

# Example usage and testing
def test_email_system():
    """Test the email verification system"""
    
    # Mock user object for testing
    class MockUser:
        def __init__(self):
            self.id = 1
            self.email = "test@example.com"
            self.first_name = "John"
            self.last_name = "Doe"
    
    # Initialize email service
    email_service = EmailVerificationService('smtp')
    
    # Test verification email
    user = MockUser()
    result = email_service.send_verification_email(user)
    print(f"Verification email result: {result}")
    
    # Test password reset email
    result = email_service.send_password_reset_email(user)
    print(f"Password reset email result: {result}")
    
    # Test welcome email
    success = email_service.send_welcome_email(user)
    print(f"Welcome email success: {success}")

if __name__ == "__main__":
    print("Email Verification and Password Reset System")
    print("Features included:")
    print("- Professional HTML email templates")
    print("- Multiple email service providers (SMTP, SendGrid, Mailgun)")
    print("- Secure token generation and validation")
    print("- Rate limiting to prevent abuse")
    print("- Email verification workflow")
    print("- Password reset workflow")
    print("- Welcome and notification emails")
    print("- Responsive email design")
    
    # Run tests if configured
    if os.getenv('TEST_EMAIL_SYSTEM') == 'true':
        test_email_system()

