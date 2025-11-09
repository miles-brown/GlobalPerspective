#!/usr/bin/env python3
"""
JWT Authentication System and Security Enhancements
For GlobalPerspective News Platform
"""

from flask import Flask, request, jsonify, current_app
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import hashlib
import time
from functools import wraps
import re
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Security Configuration
class SecurityConfig:
    # JWT Configuration
    JWT_SECRET_KEY = secrets.token_urlsafe(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Password Requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com; connect-src 'self'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

# Initialize security components
def init_security(app):
    """Initialize security components for Flask app"""
    
    # JWT Manager
    jwt = JWTManager(app)
    
    # Rate Limiter
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[SecurityConfig.RATELIMIT_DEFAULT]
    )
    
    # Blacklisted tokens storage (in production, use Redis)
    blacklisted_tokens = set()
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload['jti'] in blacklisted_tokens
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has been revoked'}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Authorization token is required'}), 401
    
    # Security headers middleware
    @app.after_request
    def add_security_headers(response):
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response
    
    return jwt, limiter, blacklisted_tokens

# Password validation
def validate_password(password):
    """Validate password against security requirements"""
    errors = []
    
    if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters long")
    
    if SecurityConfig.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if SecurityConfig.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if SecurityConfig.REQUIRE_NUMBERS and not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if SecurityConfig.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return errors

# Email validation
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Secure token generation
def generate_secure_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

# Password reset token
def generate_password_reset_token(user_id):
    """Generate password reset token"""
    timestamp = int(time.time())
    data = f"{user_id}:{timestamp}"
    token = hashlib.sha256(data.encode()).hexdigest()
    return f"{token}:{timestamp}"

def verify_password_reset_token(token, user_id, max_age=3600):
    """Verify password reset token"""
    try:
        token_hash, timestamp = token.split(':')
        timestamp = int(timestamp)
        
        # Check if token is expired
        if time.time() - timestamp > max_age:
            return False
        
        # Verify token
        expected_data = f"{user_id}:{timestamp}"
        expected_token = hashlib.sha256(expected_data.encode()).hexdigest()
        
        return token_hash == expected_token
    except:
        return False

# Authentication routes
def create_auth_routes(app, db, User, limiter, blacklisted_tokens):
    """Create authentication routes"""
    
    @app.route('/api/auth/register', methods=['POST'])
    @limiter.limit("5 per minute")
    def register():
        """User registration with validation"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'error': f'{field} is required'}), 400
            
            username = data['username'].strip()
            email = data['email'].strip().lower()
            password = data['password']
            
            # Validate email format
            if not validate_email(email):
                return jsonify({'success': False, 'error': 'Invalid email format'}), 400
            
            # Validate password
            password_errors = validate_password(password)
            if password_errors:
                return jsonify({'success': False, 'error': password_errors}), 400
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                return jsonify({'success': False, 'error': 'Username already exists'}), 400
            
            if User.query.filter_by(email=email).first():
                return jsonify({'success': False, 'error': 'Email already registered'}), 400
            
            # Create new user
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                first_name=data['first_name'].strip(),
                last_name=data['last_name'].strip(),
                role=data.get('role', 'author'),
                is_active=False,  # Require email verification
                email_verification_token=generate_secure_token()
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Send verification email (implement email sending)
            send_verification_email(user.email, user.email_verification_token)
            
            return jsonify({
                'success': True,
                'message': 'Registration successful. Please check your email to verify your account.',
                'user_id': user.id
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    @limiter.limit("10 per minute")
    def login():
        """User login with JWT token generation"""
        try:
            data = request.get_json()
            
            if not data.get('username') or not data.get('password'):
                return jsonify({'success': False, 'error': 'Username and password are required'}), 400
            
            username = data['username'].strip()
            password = data['password']
            
            # Find user by username or email
            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user or not check_password_hash(user.password_hash, password):
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
            if not user.is_active:
                return jsonify({'success': False, 'error': 'Account not verified. Please check your email.'}), 401
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create JWT tokens
            access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'username': user.username,
                    'role': user.role,
                    'email': user.email
                }
            )
            refresh_token = create_refresh_token(identity=user.id)
            
            return jsonify({
                'success': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        """Refresh JWT access token"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return jsonify({'success': False, 'error': 'User not found or inactive'}), 404
            
            new_access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'username': user.username,
                    'role': user.role,
                    'email': user.email
                }
            )
            
            return jsonify({
                'success': True,
                'access_token': new_access_token
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    @jwt_required()
    def logout():
        """Logout and blacklist token"""
        try:
            jti = get_jwt()['jti']
            blacklisted_tokens.add(jti)
            
            return jsonify({
                'success': True,
                'message': 'Successfully logged out'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/verify-email/<token>', methods=['GET'])
    def verify_email(token):
        """Verify email address"""
        try:
            user = User.query.filter_by(email_verification_token=token).first()
            
            if not user:
                return jsonify({'success': False, 'error': 'Invalid verification token'}), 400
            
            user.is_active = True
            user.email_verification_token = None
            user.email_verified_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Email verified successfully. You can now log in.'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/forgot-password', methods=['POST'])
    @limiter.limit("3 per minute")
    def forgot_password():
        """Request password reset"""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            
            if not email:
                return jsonify({'success': False, 'error': 'Email is required'}), 400
            
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Generate reset token
                reset_token = generate_password_reset_token(user.id)
                user.password_reset_token = reset_token
                user.password_reset_requested_at = datetime.utcnow()
                db.session.commit()
                
                # Send reset email
                send_password_reset_email(user.email, reset_token)
            
            # Always return success to prevent email enumeration
            return jsonify({
                'success': True,
                'message': 'If an account with that email exists, a password reset link has been sent.'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/reset-password', methods=['POST'])
    @limiter.limit("5 per minute")
    def reset_password():
        """Reset password with token"""
        try:
            data = request.get_json()
            token = data.get('token')
            new_password = data.get('password')
            
            if not token or not new_password:
                return jsonify({'success': False, 'error': 'Token and new password are required'}), 400
            
            # Validate new password
            password_errors = validate_password(new_password)
            if password_errors:
                return jsonify({'success': False, 'error': password_errors}), 400
            
            # Find user with reset token
            user = User.query.filter_by(password_reset_token=token).first()
            
            if not user:
                return jsonify({'success': False, 'error': 'Invalid or expired reset token'}), 400
            
            # Verify token is not expired (1 hour expiry)
            if not verify_password_reset_token(token, user.id, max_age=3600):
                return jsonify({'success': False, 'error': 'Reset token has expired'}), 400
            
            # Update password
            user.password_hash = generate_password_hash(new_password)
            user.password_reset_token = None
            user.password_reset_requested_at = None
            user.password_changed_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Password reset successfully. You can now log in with your new password.'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/change-password', methods=['POST'])
    @jwt_required()
    def change_password():
        """Change password for authenticated user"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            
            if not current_password or not new_password:
                return jsonify({'success': False, 'error': 'Current and new passwords are required'}), 400
            
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Verify current password
            if not check_password_hash(user.password_hash, current_password):
                return jsonify({'success': False, 'error': 'Current password is incorrect'}), 400
            
            # Validate new password
            password_errors = validate_password(new_password)
            if password_errors:
                return jsonify({'success': False, 'error': password_errors}), 400
            
            # Update password
            user.password_hash = generate_password_hash(new_password)
            user.password_changed_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Password changed successfully'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        """Get current user profile"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'bio': user.bio,
                    'avatar_url': user.avatar_url,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# Email sending functions (implement with your email service)
def send_verification_email(email, token):
    """Send email verification email"""
    # Implement with your email service (SendGrid, Mailgun, etc.)
    subject = "Verify your GlobalPerspective account"
    verification_url = f"https://your-domain.com/verify-email/{token}"
    
    body = f"""
    Welcome to GlobalPerspective!
    
    Please click the link below to verify your email address:
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you didn't create this account, please ignore this email.
    
    Best regards,
    The GlobalPerspective Team
    """
    
    # TODO: Implement actual email sending
    print(f"Verification email would be sent to {email} with token {token}")

def send_password_reset_email(email, token):
    """Send password reset email"""
    # Implement with your email service
    subject = "Reset your GlobalPerspective password"
    reset_url = f"https://your-domain.com/reset-password/{token}"
    
    body = f"""
    You requested a password reset for your GlobalPerspective account.
    
    Click the link below to reset your password:
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request this reset, please ignore this email.
    
    Best regards,
    The GlobalPerspective Team
    """
    
    # TODO: Implement actual email sending
    print(f"Password reset email would be sent to {email} with token {token}")

# Role-based access decorators
def role_required(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            role_hierarchy = {'admin': 3, 'editor': 2, 'author': 1}
            
            if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
                return jsonify({'message': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Admin only decorator
def admin_required(f):
    """Decorator to require admin role"""
    return role_required('admin')(f)

# Editor or admin decorator
def editor_required(f):
    """Decorator to require editor or admin role"""
    return role_required('editor')(f)

# Security audit logging
def log_security_event(event_type, user_id=None, details=None):
    """Log security events for audit trail"""
    logging.info(f"SECURITY_EVENT: {event_type} | User: {user_id} | Details: {details}")

# Example usage in main application
def setup_security_for_app(app, db, User):
    """Setup security for the main Flask application"""
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = SecurityConfig.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = SecurityConfig.JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = SecurityConfig.JWT_REFRESH_TOKEN_EXPIRES
    
    # Initialize security components
    jwt, limiter, blacklisted_tokens = init_security(app)
    
    # Create authentication routes
    create_auth_routes(app, db, User, limiter, blacklisted_tokens)
    
    return jwt, limiter, blacklisted_tokens

if __name__ == "__main__":
    print("JWT Authentication System and Security Enhancements")
    print("This module provides comprehensive authentication and security features:")
    print("- JWT token-based authentication")
    print("- Password validation and hashing")
    print("- Email verification")
    print("- Password reset functionality")
    print("- Rate limiting")
    print("- Security headers")
    print("- Role-based access control")
    print("- Security audit logging")

