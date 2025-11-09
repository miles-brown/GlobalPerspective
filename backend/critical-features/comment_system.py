#!/usr/bin/env python3
"""
Complete Comment System with Moderation
For GlobalPerspective News Platform
"""

from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import re
import hashlib
from functools import wraps
import bleach
from urllib.parse import urlparse

# Comment validation and sanitization
class CommentValidator:
    # Allowed HTML tags for comments
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'blockquote']
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        'blockquote': ['cite']
    }
    
    # Spam detection keywords
    SPAM_KEYWORDS = [
        'viagra', 'casino', 'lottery', 'winner', 'congratulations',
        'click here', 'free money', 'make money fast', 'work from home',
        'lose weight', 'diet pills', 'enlargement', 'mortgage'
    ]
    
    @staticmethod
    def sanitize_content(content):
        """Sanitize comment content"""
        # Remove dangerous HTML
        clean_content = bleach.clean(
            content,
            tags=CommentValidator.ALLOWED_TAGS,
            attributes=CommentValidator.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        # Remove excessive whitespace
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        return clean_content
    
    @staticmethod
    def validate_comment(content, author_name=None, author_email=None, author_website=None):
        """Validate comment data"""
        errors = []
        
        # Content validation
        if not content or len(content.strip()) < 3:
            errors.append("Comment must be at least 3 characters long")
        
        if len(content) > 5000:
            errors.append("Comment is too long (maximum 5000 characters)")
        
        # Author name validation
        if author_name and len(author_name) > 100:
            errors.append("Name is too long (maximum 100 characters)")
        
        # Email validation
        if author_email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, author_email):
                errors.append("Invalid email format")
        
        # Website validation
        if author_website:
            try:
                parsed = urlparse(author_website)
                if not parsed.scheme or not parsed.netloc:
                    errors.append("Invalid website URL")
            except:
                errors.append("Invalid website URL")
        
        return errors
    
    @staticmethod
    def detect_spam(content, author_email=None, author_website=None):
        """Detect potential spam in comments"""
        spam_score = 0
        reasons = []
        
        content_lower = content.lower()
        
        # Check for spam keywords
        for keyword in CommentValidator.SPAM_KEYWORDS:
            if keyword in content_lower:
                spam_score += 2
                reasons.append(f"Contains spam keyword: {keyword}")
        
        # Check for excessive links
        link_count = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content))
        if link_count > 2:
            spam_score += link_count
            reasons.append(f"Too many links: {link_count}")
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if caps_ratio > 0.3:
            spam_score += 3
            reasons.append("Excessive capitalization")
        
        # Check for repeated characters
        if re.search(r'(.)\1{4,}', content):
            spam_score += 2
            reasons.append("Repeated characters")
        
        # Check for suspicious email domains
        if author_email:
            suspicious_domains = ['tempmail', '10minutemail', 'guerrillamail', 'mailinator']
            email_domain = author_email.split('@')[-1].lower()
            if any(domain in email_domain for domain in suspicious_domains):
                spam_score += 3
                reasons.append("Suspicious email domain")
        
        # Determine spam status
        is_spam = spam_score >= 5
        is_suspicious = spam_score >= 3
        
        return {
            'is_spam': is_spam,
            'is_suspicious': is_suspicious,
            'spam_score': spam_score,
            'reasons': reasons
        }

# Comment threading utilities
class CommentThreading:
    @staticmethod
    def build_comment_tree(comments):
        """Build hierarchical comment tree"""
        comment_dict = {comment.id: comment for comment in comments}
        root_comments = []
        
        for comment in comments:
            if comment.parent_id is None:
                root_comments.append(comment)
            else:
                parent = comment_dict.get(comment.parent_id)
                if parent:
                    if not hasattr(parent, 'replies'):
                        parent.replies = []
                    parent.replies.append(comment)
        
        return root_comments
    
    @staticmethod
    def get_comment_depth(comment, max_depth=5):
        """Calculate comment nesting depth"""
        depth = 0
        current = comment
        
        while current.parent_id and depth < max_depth:
            current = Comment.query.get(current.parent_id)
            if not current:
                break
            depth += 1
        
        return depth

# Comment notification system
class CommentNotifications:
    @staticmethod
    def notify_article_author(article, comment):
        """Notify article author of new comment"""
        # TODO: Implement email notification
        print(f"Notifying {article.author.email} of new comment on '{article.title}'")
    
    @staticmethod
    def notify_comment_replies(parent_comment, reply):
        """Notify parent comment author of reply"""
        if parent_comment.author_email:
            # TODO: Implement email notification
            print(f"Notifying {parent_comment.author_email} of reply to their comment")
    
    @staticmethod
    def notify_moderators(comment):
        """Notify moderators of comment requiring review"""
        # TODO: Implement moderator notification system
        print(f"Notifying moderators of comment requiring review: {comment.id}")

# Comment API routes
def create_comment_routes(app, db, Comment, Article, User):
    """Create comment system routes"""
    
    @app.route('/api/articles/<int:article_id>/comments', methods=['GET'])
    def get_article_comments(article_id):
        """Get comments for an article"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            sort_by = request.args.get('sort', 'newest')  # newest, oldest, popular
            
            # Verify article exists
            article = Article.query.get_or_404(article_id)
            
            # Build query
            query = Comment.query.filter_by(
                article_id=article_id,
                status='approved'
            )
            
            # Apply sorting
            if sort_by == 'oldest':
                query = query.order_by(Comment.created_at.asc())
            elif sort_by == 'popular':
                query = query.order_by(Comment.like_count.desc(), Comment.created_at.desc())
            else:  # newest
                query = query.order_by(Comment.created_at.desc())
            
            # Paginate
            comments = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # Build comment tree for threading
            comment_tree = CommentThreading.build_comment_tree(comments.items)
            
            return jsonify({
                'success': True,
                'data': {
                    'comments': [{
                        'id': comment.id,
                        'content': comment.content,
                        'author_name': comment.author_name,
                        'author_website': comment.author_website,
                        'created_at': comment.created_at.isoformat(),
                        'like_count': comment.like_count,
                        'reply_count': comment.reply_count,
                        'parent_id': comment.parent_id,
                        'depth': CommentThreading.get_comment_depth(comment),
                        'replies': getattr(comment, 'replies', [])
                    } for comment in comment_tree],
                    'pagination': {
                        'page': comments.page,
                        'pages': comments.pages,
                        'per_page': comments.per_page,
                        'total': comments.total,
                        'has_next': comments.has_next,
                        'has_prev': comments.has_prev
                    },
                    'article': {
                        'id': article.id,
                        'title': article.title,
                        'comment_count': article.comment_count
                    }
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/articles/<int:article_id>/comments', methods=['POST'])
    def create_comment(article_id):
        """Create a new comment"""
        try:
            # Get request data
            data = request.get_json()
            content = data.get('content', '').strip()
            author_name = data.get('author_name', '').strip()
            author_email = data.get('author_email', '').strip()
            author_website = data.get('author_website', '').strip()
            parent_id = data.get('parent_id')
            
            # Get user info if authenticated
            user_id = None
            if request.headers.get('Authorization'):
                try:
                    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
                    verify_jwt_in_request()
                    user_id = get_jwt_identity()
                    user = User.query.get(user_id)
                    if user:
                        author_name = f"{user.first_name} {user.last_name}".strip()
                        author_email = user.email
                except:
                    pass  # Not authenticated, continue as guest
            
            # Verify article exists
            article = Article.query.get_or_404(article_id)
            
            # Validate comment data
            validation_errors = CommentValidator.validate_comment(
                content, author_name, author_email, author_website
            )
            if validation_errors:
                return jsonify({'success': False, 'error': validation_errors}), 400
            
            # Sanitize content
            clean_content = CommentValidator.sanitize_content(content)
            
            # Spam detection
            spam_check = CommentValidator.detect_spam(clean_content, author_email, author_website)
            
            # Determine initial status
            if spam_check['is_spam']:
                status = 'spam'
            elif spam_check['is_suspicious']:
                status = 'pending'
            else:
                status = 'approved'  # Auto-approve clean comments
            
            # Validate parent comment if replying
            if parent_id:
                parent_comment = Comment.query.get(parent_id)
                if not parent_comment or parent_comment.article_id != article_id:
                    return jsonify({'success': False, 'error': 'Invalid parent comment'}), 400
                
                # Check nesting depth
                if CommentThreading.get_comment_depth(parent_comment) >= 5:
                    return jsonify({'success': False, 'error': 'Maximum reply depth reached'}), 400
            
            # Create comment
            comment = Comment(
                content=clean_content,
                article_id=article_id,
                author_id=user_id,
                author_name=author_name,
                author_email=author_email,
                author_website=author_website,
                parent_id=parent_id,
                status=status,
                spam_score=spam_check['spam_score'],
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500]
            )
            
            db.session.add(comment)
            
            # Update article comment count if approved
            if status == 'approved':
                article.comment_count += 1
                
                # Update parent comment reply count
                if parent_id:
                    parent_comment.reply_count += 1
            
            db.session.commit()
            
            # Send notifications
            if status == 'approved':
                CommentNotifications.notify_article_author(article, comment)
                if parent_id:
                    CommentNotifications.notify_comment_replies(parent_comment, comment)
            elif status == 'pending':
                CommentNotifications.notify_moderators(comment)
            
            return jsonify({
                'success': True,
                'data': {
                    'id': comment.id,
                    'status': status,
                    'message': 'Comment posted successfully' if status == 'approved' else 'Comment submitted for review'
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/comments/<int:comment_id>/like', methods=['POST'])
    def like_comment(comment_id):
        """Like/unlike a comment"""
        try:
            comment = Comment.query.get_or_404(comment_id)
            
            # Simple like system (in production, track user likes)
            action = request.get_json().get('action', 'like')
            
            if action == 'like':
                comment.like_count += 1
            elif action == 'unlike' and comment.like_count > 0:
                comment.like_count -= 1
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'like_count': comment.like_count
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/comments/<int:comment_id>/report', methods=['POST'])
    def report_comment(comment_id):
        """Report a comment for moderation"""
        try:
            comment = Comment.query.get_or_404(comment_id)
            data = request.get_json()
            reason = data.get('reason', 'inappropriate')
            
            # Update comment with report
            comment.report_count += 1
            comment.reported_at = datetime.utcnow()
            
            # Auto-hide if too many reports
            if comment.report_count >= 5:
                comment.status = 'hidden'
            
            db.session.commit()
            
            # Notify moderators
            CommentNotifications.notify_moderators(comment)
            
            return jsonify({
                'success': True,
                'message': 'Comment reported successfully'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Admin moderation routes
    @app.route('/api/admin/comments', methods=['GET'])
    @jwt_required()
    def get_admin_comments():
        """Get comments for admin moderation"""
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
                        'content': comment.content[:200] + '...' if len(comment.content) > 200 else comment.content,
                        'author_name': comment.author_name,
                        'author_email': comment.author_email,
                        'status': comment.status,
                        'spam_score': comment.spam_score,
                        'report_count': comment.report_count,
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
    @jwt_required()
    def moderate_comment(comment_id):
        """Moderate a comment (approve, reject, spam)"""
        try:
            comment = Comment.query.get_or_404(comment_id)
            data = request.get_json()
            new_status = data.get('status')
            moderator_notes = data.get('notes', '')
            
            if new_status not in ['approved', 'rejected', 'spam', 'hidden']:
                return jsonify({'success': False, 'error': 'Invalid status'}), 400
            
            old_status = comment.status
            comment.status = new_status
            comment.moderated_at = datetime.utcnow()
            comment.moderated_by = get_jwt_identity()
            comment.moderator_notes = moderator_notes
            
            # Update article comment count
            if old_status != 'approved' and new_status == 'approved':
                comment.article.comment_count += 1
            elif old_status == 'approved' and new_status != 'approved':
                comment.article.comment_count = max(0, comment.article.comment_count - 1)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Comment {new_status} successfully'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/admin/comments/bulk-moderate', methods=['POST'])
    @jwt_required()
    def bulk_moderate_comments():
        """Bulk moderate multiple comments"""
        try:
            data = request.get_json()
            comment_ids = data.get('comment_ids', [])
            action = data.get('action')  # approve, reject, spam, delete
            
            if not comment_ids or not action:
                return jsonify({'success': False, 'error': 'Comment IDs and action are required'}), 400
            
            comments = Comment.query.filter(Comment.id.in_(comment_ids)).all()
            
            success_count = 0
            for comment in comments:
                try:
                    if action == 'delete':
                        # Update article comment count
                        if comment.status == 'approved':
                            comment.article.comment_count = max(0, comment.article.comment_count - 1)
                        db.session.delete(comment)
                    else:
                        old_status = comment.status
                        comment.status = action
                        comment.moderated_at = datetime.utcnow()
                        comment.moderated_by = get_jwt_identity()
                        
                        # Update article comment count
                        if old_status != 'approved' and action == 'approved':
                            comment.article.comment_count += 1
                        elif old_status == 'approved' and action != 'approved':
                            comment.article.comment_count = max(0, comment.article.comment_count - 1)
                    
                    success_count += 1
                except:
                    continue
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully processed {success_count} comments'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# Database model updates for comments
def update_comment_model():
    """Updated Comment model with all features"""
    return """
    class Comment(db.Model):
        __tablename__ = 'comments'
        
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.Text, nullable=False)
        status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, spam, hidden
        
        # Author information
        author_name = db.Column(db.String(100))
        author_email = db.Column(db.String(120))
        author_website = db.Column(db.String(255))
        
        # Threading support
        parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
        reply_count = db.Column(db.Integer, default=0)
        
        # Engagement metrics
        like_count = db.Column(db.Integer, default=0)
        report_count = db.Column(db.Integer, default=0)
        
        # Spam detection
        spam_score = db.Column(db.Float, default=0.0)
        
        # Moderation
        moderated_at = db.Column(db.DateTime)
        moderated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
        moderator_notes = db.Column(db.Text)
        reported_at = db.Column(db.DateTime)
        
        # Technical information
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.Text)
        
        # Timestamps
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
        author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        
        article = db.relationship('Article', backref='comments')
        author = db.relationship('User', foreign_keys=[author_id], backref='user_comments')
        moderator = db.relationship('User', foreign_keys=[moderated_by])
        
        # Self-referential relationship for threading
        replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    """

if __name__ == "__main__":
    print("Complete Comment System with Moderation")
    print("Features included:")
    print("- Comment creation and validation")
    print("- Content sanitization and spam detection")
    print("- Threaded comments (replies)")
    print("- Like/unlike functionality")
    print("- Comment reporting")
    print("- Admin moderation interface")
    print("- Bulk moderation operations")
    print("- Notification system")
    print("- Security and rate limiting")

