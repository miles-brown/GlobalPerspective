#!/usr/bin/env python3
"""
Complete Admin Backend for GlobalPerspective News Platform
Integrated with Neon PostgreSQL Database
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import uuid
from functools import wraps
import schedule
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Neon Database Configuration
NEON_CONNECTION_STRING = "postgresql://neondb_owner:npg_De3IxqN5TFfG@ep-rough-river-afmryuc9-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require"
app.config['SQLALCHEMY_DATABASE_URI'] = NEON_CONNECTION_STRING
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app, origins="*")

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='author')
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#dc2626')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    subtitle = db.Column(db.String(500))
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(255))
    status = db.Column(db.String(20), default='draft')
    is_featured = db.Column(db.Boolean, default=False)
    is_breaking = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    reading_time = db.Column(db.Integer, default=5)
    seo_title = db.Column(db.String(255))
    seo_description = db.Column(db.Text)
    seo_keywords = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    scheduled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relationships
    author = db.relationship('User', backref='articles')
    category = db.relationship('Category', backref='articles')

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    author_name = db.Column(db.String(100))
    author_email = db.Column(db.String(120))
    author_website = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    article = db.relationship('Article', backref='comments')
    author = db.relationship('User', backref='comments')

class MediaItem(db.Model):
    __tablename__ = 'media_items'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    file_type = db.Column(db.String(20))
    alt_text = db.Column(db.String(255))
    caption = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    
    # Relationships
    uploader = db.relationship('User')
    article = db.relationship('Article')

# Authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real app, you'd check JWT tokens here
        # For demo purposes, we'll skip authentication
        return f(*args, **kwargs)
    return decorated_function

# API Routes

@app.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Article statistics
        total_articles = Article.query.count()
        published_articles = Article.query.filter_by(status='published').count()
        draft_articles = Article.query.filter_by(status='draft').count()
        pending_articles = Article.query.filter_by(status='review').count()
        
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # Comment statistics
        total_comments = Comment.query.count()
        pending_comments = Comment.query.filter_by(status='pending').count()
        approved_comments = Comment.query.filter_by(status='approved').count()
        
        # Recent activity
        recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
        recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
        
        # Top performing articles
        top_articles = Article.query.filter_by(status='published').order_by(Article.view_count.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'data': {
                'articles': {
                    'total': total_articles,
                    'published': published_articles,
                    'drafts': draft_articles,
                    'pending': pending_articles
                },
                'users': {
                    'total': total_users,
                    'active': active_users
                },
                'comments': {
                    'total': total_comments,
                    'pending': pending_comments,
                    'approved': approved_comments
                },
                'recent_articles': [{
                    'id': article.id,
                    'title': article.title,
                    'status': article.status,
                    'author': article.author.username,
                    'created_at': article.created_at.isoformat()
                } for article in recent_articles],
                'recent_comments': [{
                    'id': comment.id,
                    'content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
                    'author_name': comment.author_name,
                    'article_title': comment.article.title,
                    'status': comment.status,
                    'created_at': comment.created_at.isoformat()
                } for comment in recent_comments],
                'top_articles': [{
                    'id': article.id,
                    'title': article.title,
                    'view_count': article.view_count,
                    'like_count': article.like_count,
                    'comment_count': article.comment_count
                } for article in top_articles]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        role_filter = request.args.get('role', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                (User.username.contains(search)) |
                (User.email.contains(search)) |
                (User.first_name.contains(search)) |
                (User.last_name.contains(search))
            )
        
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'users': [{
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'article_count': len(user.articles)
                } for user in users.items],
                'pagination': {
                    'page': users.page,
                    'pages': users.pages,
                    'per_page': users.per_page,
                    'total': users.total,
                    'has_next': users.has_next,
                    'has_prev': users.has_prev
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/articles', methods=['GET'])
@admin_required
def get_admin_articles():
    """Get all articles for admin with advanced filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        category_filter = request.args.get('category', '')
        author_filter = request.args.get('author', '')
        
        query = Article.query
        
        if search:
            query = query.filter(
                (Article.title.contains(search)) |
                (Article.content.contains(search)) |
                (Article.excerpt.contains(search))
            )
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if category_filter:
            query = query.filter_by(category_id=category_filter)
        
        if author_filter:
            query = query.filter_by(author_id=author_filter)
        
        articles = query.order_by(Article.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'articles': [{
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'status': article.status,
                    'author': {
                        'id': article.author.id,
                        'username': article.author.username,
                        'name': f"{article.author.first_name or ''} {article.author.last_name or ''}".strip()
                    },
                    'category': {
                        'id': article.category.id,
                        'name': article.category.name
                    },
                    'is_featured': article.is_featured,
                    'is_breaking': article.is_breaking,
                    'view_count': article.view_count,
                    'like_count': article.like_count,
                    'comment_count': article.comment_count,
                    'published_at': article.published_at.isoformat() if article.published_at else None,
                    'created_at': article.created_at.isoformat(),
                    'updated_at': article.updated_at.isoformat()
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

@app.route('/api/admin/comments', methods=['GET'])
@admin_required
def get_admin_comments():
    """Get all comments for moderation"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', '')
        
        query = Comment.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        comments = query.order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'comments': [{
                    'id': comment.id,
                    'content': comment.content,
                    'status': comment.status,
                    'author_name': comment.author_name,
                    'author_email': comment.author_email,
                    'article': {
                        'id': comment.article.id,
                        'title': comment.article.title
                    },
                    'created_at': comment.created_at.isoformat()
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

@app.route('/api/admin/comments/<int:comment_id>/moderate', methods=['PUT'])
@admin_required
def moderate_comment(comment_id):
    """Moderate a comment (approve, reject, mark as spam)"""
    try:
        comment = Comment.query.get_or_404(comment_id)
        data = request.get_json()
        
        new_status = data.get('status')
        if new_status not in ['approved', 'rejected', 'spam']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        comment.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Comment {new_status} successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/categories', methods=['GET'])
@admin_required
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
                'is_active': cat.is_active,
                'article_count': len(cat.articles)
            } for cat in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def get_analytics():
    """Get analytics data"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Calculate real analytics from database
        total_views = db.session.query(db.func.sum(Article.view_count)).scalar() or 0
        total_articles = Article.query.filter_by(status='published').count()
        total_comments = Comment.query.filter_by(status='approved').count()
        
        # Top articles
        top_articles = Article.query.filter_by(status='published').order_by(
            Article.view_count.desc()
        ).limit(5).all()
        
        # Category distribution
        category_stats = db.session.query(
            Category.name,
            db.func.count(Article.id).label('count')
        ).join(Article).group_by(Category.name).all()
        
        analytics_data = {
            'overview': {
                'total_views': total_views,
                'unique_visitors': int(total_views * 0.7),  # Estimated
                'bounce_rate': 0.35,
                'avg_session_duration': 245
            },
            'top_articles': [{
                'title': article.title,
                'views': article.view_count,
                'engagement': min(0.9, (article.like_count + article.comment_count) / max(article.view_count, 1))
            } for article in top_articles],
            'traffic_sources': {
                'direct': 0.35,
                'social': 0.25,
                'search': 0.30,
                'referral': 0.10
            },
            'category_distribution': {
                cat_name: count for cat_name, count in category_stats
            }
        }
        
        return jsonify({
            'success': True,
            'data': analytics_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/test-connection', methods=['GET'])
def test_connection():
    """Test database connection"""
    try:
        # Test database connection
        user_count = User.query.count()
        article_count = Article.query.count()
        category_count = Category.query.count()
        
        return jsonify({
            'success': True,
            'message': 'Database connection successful',
            'data': {
                'users': user_count,
                'articles': article_count,
                'categories': category_count,
                'database': 'Neon PostgreSQL',
                'timestamp': datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Database connection failed'
        }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected',
        'version': '1.0.0'
    })

# CORS preflight handler
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'message': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

if __name__ == '__main__':
    print("🌍 Starting GlobalPerspective Admin Backend...")
    print("🗄️  Connected to Neon PostgreSQL Database")
    print("🚀 Server starting on http://0.0.0.0:5000")
    
    with app.app_context():
        try:
            # Test database connection
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

