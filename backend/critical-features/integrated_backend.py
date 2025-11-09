#!/usr/bin/env python3
"""
Simplified Integrated Backend for GlobalPerspective News Platform
Core features without external dependencies that cause installation issues
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import secrets
import re
import time
import hashlib
from sqlalchemy import or_, and_, func

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///globalperspective.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(32)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
cors = CORS(app)
jwt = JWTManager(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='author')
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    
    # Account status
    is_active = db.Column(db.Boolean, default=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    
    # Email verification
    email_verification_token = db.Column(db.String(255))
    verification_token_created_at = db.Column(db.DateTime)
    email_verified_at = db.Column(db.DateTime)
    
    # Password reset
    password_reset_token = db.Column(db.String(255))
    password_reset_requested_at = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    articles = db.relationship('Article', backref='author', lazy=True)
    comments = db.relationship('Comment', foreign_keys='Comment.author_id', backref='user', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#c41e3a')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    articles = db.relationship('Article', backref='category', lazy=True)

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    
    # SEO and metadata
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    tags = db.Column(db.Text)  # Comma-separated tags
    
    # Media
    featured_image = db.Column(db.String(255))
    featured_image_alt = db.Column(db.String(255))
    
    # Engagement metrics
    view_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    # Publishing
    is_featured = db.Column(db.Boolean, default=False)
    is_breaking = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='article', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, spam
    
    # Author information (for guest comments)
    author_name = db.Column(db.String(100))
    author_email = db.Column(db.String(120))
    author_website = db.Column(db.String(255))
    
    # Threading
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    reply_count = db.Column(db.Integer, default=0)
    
    # Engagement
    like_count = db.Column(db.Integer, default=0)
    report_count = db.Column(db.Integer, default=0)
    
    # Spam detection
    spam_score = db.Column(db.Float, default=0.0)
    
    # Moderation
    moderated_at = db.Column(db.DateTime)
    moderated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    moderator_notes = db.Column(db.Text)
    
    # Technical info
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Null for guest comments
    
    # Self-referential relationship for threading
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))

# Simple rate limiting
class SimpleRateLimit:
    _requests = {}
    
    @classmethod
    def is_allowed(cls, key, limit=10, window=60):
        """Simple in-memory rate limiting"""
        now = time.time()
        
        # Clean old entries
        cls._requests = {k: v for k, v in cls._requests.items() if now - v[-1] < window}
        
        if key not in cls._requests:
            cls._requests[key] = []
        
        # Remove old requests outside window
        cls._requests[key] = [t for t in cls._requests[key] if now - t < window]
        
        if len(cls._requests[key]) >= limit:
            return False
        
        cls._requests[key].append(now)
        return True

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration with email verification"""
    try:
        # Simple rate limiting
        client_ip = request.remote_addr
        if not SimpleRateLimit.is_allowed(f"register:{client_ip}", limit=5, window=3600):
            return jsonify({'success': False, 'error': 'Too many registration attempts'}), 429
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Basic validation
        if len(password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
        # Create user
        verification_token = secrets.token_urlsafe(32)
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            role=data.get('role', 'author'),
            email_verification_token=verification_token,
            verification_token_created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        
        # In production, send actual email
        print(f"Verification email would be sent to {email} with token {verification_token}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful. Please check your email to verify your account.',
            'user_id': user.id,
            'verification_token': verification_token  # Only for testing
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login with JWT token"""
    try:
        # Simple rate limiting
        client_ip = request.remote_addr
        if not SimpleRateLimit.is_allowed(f"login:{client_ip}", limit=10, window=300):
            return jsonify({'success': False, 'error': 'Too many login attempts'}), 429
        
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        # Find user
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        if not user.is_email_verified:
            return jsonify({'success': False, 'error': 'Please verify your email first'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        user.is_active = True
        db.session.commit()
        
        # Create JWT token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'username': user.username,
                'role': user.role,
                'email': user.email
            }
        )
        
        return jsonify({
            'success': True,
            'access_token': access_token,
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

@app.route('/api/auth/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify email address"""
    try:
        user = User.query.filter_by(email_verification_token=token).first()
        
        if not user:
            return jsonify({'success': False, 'error': 'Invalid verification token'}), 400
        
        # Check token expiry (24 hours)
        if user.verification_token_created_at:
            expiry_time = user.verification_token_created_at + timedelta(hours=24)
            if datetime.utcnow() > expiry_time:
                return jsonify({'success': False, 'error': 'Verification token expired'}), 400
        
        # Verify user
        user.is_email_verified = True
        user.is_active = True
        user.email_verification_token = None
        user.email_verified_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Email verified successfully! You can now log in.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Search Routes
@app.route('/api/search', methods=['GET'])
def search_articles():
    """Search articles"""
    try:
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        category_id = request.args.get('category_id', type=int)
        
        if not query or len(query) < 2:
            return jsonify({'success': False, 'error': 'Search query too short'}), 400
        
        # Build search query
        search_query = Article.query.filter(Article.status == 'published')
        
        # Simple text search
        search_term = f"%{query}%"
        search_query = search_query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.content.ilike(search_term),
                Article.excerpt.ilike(search_term),
                Article.tags.ilike(search_term)
            )
        )
        
        # Category filter
        if category_id:
            search_query = search_query.filter(Article.category_id == category_id)
        
        # Paginate results
        results = search_query.order_by(Article.published_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'results': [{
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'excerpt': article.excerpt,
                    'featured_image': article.featured_image,
                    'published_at': article.published_at.isoformat() if article.published_at else None,
                    'author': {
                        'id': article.author.id,
                        'name': f"{article.author.first_name} {article.author.last_name}",
                        'username': article.author.username
                    },
                    'category': {
                        'id': article.category.id,
                        'name': article.category.name,
                        'slug': article.category.slug
                    },
                    'view_count': article.view_count,
                    'comment_count': article.comment_count
                } for article in results.items],
                'pagination': {
                    'page': results.page,
                    'pages': results.pages,
                    'per_page': results.per_page,
                    'total': results.total,
                    'has_next': results.has_next,
                    'has_prev': results.has_prev
                },
                'query': query
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Comment Routes
@app.route('/api/articles/<int:article_id>/comments', methods=['GET'])
def get_comments(article_id):
    """Get comments for an article"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        
        # Verify article exists
        article = Article.query.get_or_404(article_id)
        
        # Get approved comments
        comments = Comment.query.filter_by(
            article_id=article_id,
            status='approved'
        ).order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'comments': [{
                    'id': comment.id,
                    'content': comment.content,
                    'author_name': comment.author_name or (f"{comment.user.first_name} {comment.user.last_name}" if comment.user else "Anonymous"),
                    'created_at': comment.created_at.isoformat(),
                    'like_count': comment.like_count,
                    'reply_count': comment.reply_count,
                    'parent_id': comment.parent_id
                } for comment in comments.items],
                'pagination': {
                    'page': comments.page,
                    'pages': comments.pages,
                    'per_page': comments.per_page,
                    'total': comments.total,
                    'has_next': comments.has_next,
                    'has_prev': comments.has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/articles/<int:article_id>/comments', methods=['POST'])
def create_comment(article_id):
    """Create a new comment"""
    try:
        # Rate limiting
        client_ip = request.remote_addr
        if not SimpleRateLimit.is_allowed(f"comment:{client_ip}", limit=5, window=300):
            return jsonify({'success': False, 'error': 'Too many comments. Please wait.'}), 429
        
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content or len(content) < 3:
            return jsonify({'success': False, 'error': 'Comment too short'}), 400
        
        if len(content) > 5000:
            return jsonify({'success': False, 'error': 'Comment too long'}), 400
        
        # Verify article exists
        article = Article.query.get_or_404(article_id)
        
        # Get user info if authenticated
        user_id = None
        author_name = data.get('author_name', '').strip()
        author_email = data.get('author_email', '').strip()
        
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
                if user:
                    author_name = f"{user.first_name} {user.last_name}"
                    author_email = user.email
        except:
            pass
        
        # Simple spam detection
        spam_keywords = ['viagra', 'casino', 'lottery', 'click here', 'free money']
        is_spam = any(keyword in content.lower() for keyword in spam_keywords)
        
        # Create comment
        comment = Comment(
            content=content,
            article_id=article_id,
            author_id=user_id,
            author_name=author_name,
            author_email=author_email,
            parent_id=data.get('parent_id'),
            status='spam' if is_spam else 'approved',  # Auto-approve non-spam
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        
        db.session.add(comment)
        
        # Update article comment count if approved
        if comment.status == 'approved':
            article.comment_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': comment.id,
                'status': comment.status,
                'message': 'Comment posted successfully' if comment.status == 'approved' else 'Comment flagged for review'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Article Routes
@app.route('/api/articles', methods=['GET'])
def get_articles():
    """Get articles with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status', 'published')
        featured = request.args.get('featured', type=bool)
        
        query = Article.query.filter_by(status=status)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if featured is not None:
            query = query.filter_by(is_featured=featured)
        
        articles = query.order_by(Article.published_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'articles': [{
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'excerpt': article.excerpt,
                    'featured_image': article.featured_image,
                    'published_at': article.published_at.isoformat() if article.published_at else None,
                    'author': {
                        'id': article.author.id,
                        'name': f"{article.author.first_name} {article.author.last_name}",
                        'username': article.author.username
                    },
                    'category': {
                        'id': article.category.id,
                        'name': article.category.name,
                        'slug': article.category.slug
                    },
                    'view_count': article.view_count,
                    'comment_count': article.comment_count,
                    'is_featured': article.is_featured,
                    'is_breaking': article.is_breaking
                } for article in articles.items],
                'pagination': {
                    'page': articles.page,
                    'pages': articles.pages,
                    'per_page': articles.per_page,
                    'total': articles.total,
                    'has_next': articles.has_next,
                    'has_prev': articles.has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Get single article by ID"""
    try:
        article = Article.query.get_or_404(article_id)
        
        # Increment view count
        article.view_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'content': article.content,
                'excerpt': article.excerpt,
                'featured_image': article.featured_image,
                'featured_image_alt': article.featured_image_alt,
                'meta_title': article.meta_title,
                'meta_description': article.meta_description,
                'tags': article.tags.split(',') if article.tags else [],
                'published_at': article.published_at.isoformat() if article.published_at else None,
                'updated_at': article.updated_at.isoformat(),
                'author': {
                    'id': article.author.id,
                    'name': f"{article.author.first_name} {article.author.last_name}",
                    'username': article.author.username,
                    'bio': article.author.bio,
                    'avatar_url': article.author.avatar_url
                },
                'category': {
                    'id': article.category.id,
                    'name': article.category.name,
                    'slug': article.category.slug,
                    'color': article.category.color
                },
                'view_count': article.view_count,
                'comment_count': article.comment_count,
                'like_count': article.like_count,
                'share_count': article.share_count,
                'is_featured': article.is_featured,
                'is_breaking': article.is_breaking
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Category Routes
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'description': cat.description,
                'color': cat.color,
                'article_count': len(cat.articles)
            } for cat in categories]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Dashboard Routes
@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        current_user_id = get_jwt_identity()
        
        # Basic stats
        total_articles = Article.query.filter_by(author_id=current_user_id).count()
        published_articles = Article.query.filter_by(author_id=current_user_id, status='published').count()
        draft_articles = Article.query.filter_by(author_id=current_user_id, status='draft').count()
        
        # Recent articles
        recent_articles = Article.query.filter_by(author_id=current_user_id)\
            .order_by(Article.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'data': {
                'stats': {
                    'total_articles': total_articles,
                    'published_articles': published_articles,
                    'draft_articles': draft_articles,
                    'total_views': sum(article.view_count for article in Article.query.filter_by(author_id=current_user_id).all()),
                    'total_comments': sum(article.comment_count for article in Article.query.filter_by(author_id=current_user_id).all())
                },
                'recent_articles': [{
                    'id': article.id,
                    'title': article.title,
                    'status': article.status,
                    'created_at': article.created_at.isoformat(),
                    'view_count': article.view_count,
                    'comment_count': article.comment_count
                } for article in recent_articles]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'GlobalPerspective API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'features': [
            'JWT Authentication',
            'Comment System',
            'Search Functionality',
            'Email Verification',
            'Article Management',
            'User Management'
        ]
    })

# Initialize database and create sample data
def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create sample categories
        if not Category.query.first():
            categories = [
                Category(name='World Affairs', slug='world-affairs', description='International news and global politics'),
                Category(name='Business', slug='business', description='Business news and economic analysis'),
                Category(name='Technology', slug='technology', description='Technology trends and innovations'),
                Category(name='Culture', slug='culture', description='Arts, culture, and society'),
                Category(name='Science', slug='science', description='Scientific discoveries and research')
            ]
            
            for category in categories:
                db.session.add(category)
            
            db.session.commit()
            print("✅ Sample categories created")
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            # Use environment variable for admin password, with secure default
            admin_password = os.getenv('ADMIN_PASSWORD')
            if not admin_password:
                # Generate secure random password if not provided
                import string
                admin_password = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(16))
                print("⚠️  SECURITY WARNING: Generated random admin password. Please set ADMIN_PASSWORD environment variable.")
                print(f"   Generated password: {admin_password}")
            
            admin_user = User(
                username=os.getenv('ADMIN_USERNAME', 'admin'),
                email=os.getenv('ADMIN_EMAIL', 'admin@globalperspective.news'),
                password_hash=generate_password_hash(admin_password),
                first_name=os.getenv('ADMIN_FIRST_NAME', 'Admin'),
                last_name=os.getenv('ADMIN_LAST_NAME', 'User'),
                role='admin',
                is_active=True,
                is_email_verified=True,
                email_verified_at=datetime.utcnow()
            )
            
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created with secure password from environment variables")
        
        # Create sample article
        if not Article.query.first():
            admin_user = User.query.filter_by(username='admin').first()
            world_affairs = Category.query.filter_by(slug='world-affairs').first()
            
            if admin_user and world_affairs:
                sample_article = Article(
                    title='Welcome to GlobalPerspective',
                    slug='welcome-to-globalperspective',
                    excerpt='Your premier source for international news and world affairs analysis.',
                    content='''
                    <h2>Welcome to GlobalPerspective</h2>
                    <p>GlobalPerspective is your premier destination for comprehensive international news coverage and in-depth world affairs analysis. Our mission is to provide you with the insights you need to understand our interconnected world.</p>
                    
                    <h3>What We Offer</h3>
                    <ul>
                        <li><strong>Breaking News:</strong> Real-time updates on global events</li>
                        <li><strong>Expert Analysis:</strong> In-depth commentary from seasoned journalists</li>
                        <li><strong>Multiple Perspectives:</strong> Balanced coverage from various viewpoints</li>
                        <li><strong>Interactive Community:</strong> Engage with readers and experts</li>
                    </ul>
                    
                    <p>Join our community of informed global citizens and stay ahead of the curve with GlobalPerspective.</p>
                    ''',
                    status='published',
                    author_id=admin_user.id,
                    category_id=world_affairs.id,
                    published_at=datetime.utcnow(),
                    is_featured=True,
                    meta_title='Welcome to GlobalPerspective - International News & Analysis',
                    meta_description='Your premier source for international news and world affairs analysis.',
                    tags='welcome, news, international, world affairs'
                )
                
                db.session.add(sample_article)
                db.session.commit()
                print("✅ Sample article created")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# Main application entry point
if __name__ == '__main__':
    init_database()
    
    print("🌍 GlobalPerspective Backend Starting...")
    print("Features enabled:")
    print("✅ JWT Authentication & Security")
    print("✅ Comment System")
    print("✅ Search Functionality")
    print("✅ Email Verification (simulated)")
    print("✅ Article Management")
    print("✅ User Dashboard")
    print("✅ Rate Limiting")
    print("\n🚀 Server running on http://0.0.0.0:5000")
    print("\n📝 Admin credentials:")
    print("   Username: Set via ADMIN_USERNAME environment variable (default: admin)")
    print("   Password: Set via ADMIN_PASSWORD environment variable (secure random if not set)")
    print("   Email: Set via ADMIN_EMAIL environment variable")
    print("\n⚠️  SECURITY: Always set environment variables in production!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

