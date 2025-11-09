# Advanced CMS Features and Workflow Management
# This extends the admin dashboard backend with sophisticated features

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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Additional Models for Advanced Features
class ArticleRevision(db.Model):
    """Track article revision history"""
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    revision_number = db.Column(db.Integer, default=1)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    change_summary = db.Column(db.Text)
    
    # Relationships
    article = db.relationship('Article', backref='revisions')
    creator = db.relationship('User')

class WorkflowStep(db.Model):
    """Define workflow steps for editorial process"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    required_role = db.Column(db.String(20))  # author, editor, admin
    auto_advance = db.Column(db.Boolean, default=False)
    notification_template = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ArticleWorkflow(db.Model):
    """Track article progress through workflow"""
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('workflow_step.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, rejected
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Relationships
    article = db.relationship('Article')
    step = db.relationship('WorkflowStep')
    assignee = db.relationship('User')

class ScheduledPost(db.Model):
    """Schedule articles for future publication"""
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    scheduled_for = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(50), default='UTC')
    status = db.Column(db.String(20), default='scheduled')  # scheduled, published, failed
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Relationships
    article = db.relationship('Article')
    creator = db.relationship('User')

class SEOAnalysis(db.Model):
    """Store SEO analysis results for articles"""
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    seo_score = db.Column(db.Float, default=0.0)
    readability_score = db.Column(db.Float, default=0.0)
    keyword_density = db.Column(db.JSON)
    meta_analysis = db.Column(db.JSON)
    suggestions = db.Column(db.JSON)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    article = db.relationship('Article')

class ContentTemplate(db.Model):
    """Reusable content templates"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    template_type = db.Column(db.String(50))  # article, newsletter, social_post
    content_structure = db.Column(db.JSON)
    default_values = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User')

class BulkOperation(db.Model):
    """Track bulk operations on content"""
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(50), nullable=False)  # bulk_edit, bulk_delete, bulk_publish
    target_type = db.Column(db.String(50), nullable=False)  # articles, users, comments
    target_ids = db.Column(db.JSON)
    operation_data = db.Column(db.JSON)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, failed
    progress = db.Column(db.Integer, default=0)
    total_items = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    error_log = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship('User')

class SystemSettings(db.Model):
    """Store system-wide settings"""
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.JSON)
    setting_type = db.Column(db.String(20), default='string')  # string, integer, boolean, json
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    updater = db.relationship('User')

# Advanced API Routes

@app.route('/api/admin/articles/<int:article_id>/revisions', methods=['GET'])
@admin_required
def get_article_revisions(article_id):
    """Get revision history for an article"""
    try:
        revisions = ArticleRevision.query.filter_by(article_id=article_id).order_by(
            ArticleRevision.created_at.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': rev.id,
                'revision_number': rev.revision_number,
                'title': rev.title,
                'change_summary': rev.change_summary,
                'created_by': {
                    'id': rev.creator.id,
                    'username': rev.creator.username,
                    'name': f"{rev.creator.first_name} {rev.creator.last_name}".strip()
                },
                'created_at': rev.created_at.isoformat()
            } for rev in revisions]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/articles/<int:article_id>/revisions', methods=['POST'])
@admin_required
def create_article_revision(article_id):
    """Create a new revision of an article"""
    try:
        article = Article.query.get_or_404(article_id)
        data = request.get_json()
        
        # Get the latest revision number
        latest_revision = ArticleRevision.query.filter_by(article_id=article_id).order_by(
            ArticleRevision.revision_number.desc()
        ).first()
        
        revision_number = (latest_revision.revision_number + 1) if latest_revision else 1
        
        revision = ArticleRevision(
            article_id=article_id,
            title=data.get('title', article.title),
            content=data.get('content', article.content),
            excerpt=data.get('excerpt', article.excerpt),
            revision_number=revision_number,
            created_by=1,  # TODO: Get from JWT token
            change_summary=data.get('change_summary', '')
        )
        
        db.session.add(revision)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': revision.id,
                'revision_number': revision.revision_number
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/workflow/steps', methods=['GET'])
@admin_required
def get_workflow_steps():
    """Get all workflow steps"""
    try:
        steps = WorkflowStep.query.filter_by(is_active=True).order_by(WorkflowStep.order).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': step.id,
                'name': step.name,
                'description': step.description,
                'order': step.order,
                'required_role': step.required_role,
                'auto_advance': step.auto_advance
            } for step in steps]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/workflow/steps', methods=['POST'])
@admin_required
def create_workflow_step():
    """Create a new workflow step"""
    try:
        data = request.get_json()
        
        step = WorkflowStep(
            name=data['name'],
            description=data.get('description', ''),
            order=data.get('order', 0),
            required_role=data.get('required_role'),
            auto_advance=data.get('auto_advance', False),
            notification_template=data.get('notification_template', '')
        )
        
        db.session.add(step)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': step.id,
                'name': step.name
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/articles/<int:article_id>/workflow', methods=['GET'])
@admin_required
def get_article_workflow(article_id):
    """Get workflow status for an article"""
    try:
        workflow_items = ArticleWorkflow.query.filter_by(article_id=article_id).join(
            WorkflowStep
        ).order_by(WorkflowStep.order).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': item.id,
                'step': {
                    'id': item.step.id,
                    'name': item.step.name,
                    'required_role': item.step.required_role
                },
                'status': item.status,
                'assigned_to': {
                    'id': item.assignee.id,
                    'username': item.assignee.username
                } if item.assignee else None,
                'started_at': item.started_at.isoformat(),
                'completed_at': item.completed_at.isoformat() if item.completed_at else None,
                'notes': item.notes
            } for item in workflow_items]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/articles/<int:article_id>/workflow/<int:step_id>', methods=['PUT'])
@admin_required
def update_workflow_step(article_id, step_id):
    """Update workflow step status"""
    try:
        workflow_item = ArticleWorkflow.query.filter_by(
            article_id=article_id, 
            step_id=step_id
        ).first_or_404()
        
        data = request.get_json()
        
        workflow_item.status = data.get('status', workflow_item.status)
        workflow_item.notes = data.get('notes', workflow_item.notes)
        
        if data.get('status') == 'completed':
            workflow_item.completed_at = datetime.utcnow()
            
            # Auto-advance to next step if configured
            step = WorkflowStep.query.get(step_id)
            if step.auto_advance:
                next_step = WorkflowStep.query.filter(
                    WorkflowStep.order > step.order,
                    WorkflowStep.is_active == True
                ).order_by(WorkflowStep.order).first()
                
                if next_step:
                    next_workflow = ArticleWorkflow(
                        article_id=article_id,
                        step_id=next_step.id,
                        status='pending'
                    )
                    db.session.add(next_workflow)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Workflow updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/scheduled-posts', methods=['GET'])
@admin_required
def get_scheduled_posts():
    """Get all scheduled posts"""
    try:
        scheduled_posts = ScheduledPost.query.order_by(ScheduledPost.scheduled_for).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': post.id,
                'article': {
                    'id': post.article.id,
                    'title': post.article.title
                },
                'scheduled_for': post.scheduled_for.isoformat(),
                'timezone': post.timezone,
                'status': post.status,
                'created_by': {
                    'id': post.creator.id,
                    'username': post.creator.username
                },
                'created_at': post.created_at.isoformat(),
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'error_message': post.error_message
            } for post in scheduled_posts]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/scheduled-posts', methods=['POST'])
@admin_required
def create_scheduled_post():
    """Schedule an article for publication"""
    try:
        data = request.get_json()
        
        scheduled_post = ScheduledPost(
            article_id=data['article_id'],
            scheduled_for=datetime.fromisoformat(data['scheduled_for']),
            timezone=data.get('timezone', 'UTC'),
            created_by=1  # TODO: Get from JWT token
        )
        
        db.session.add(scheduled_post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': scheduled_post.id,
                'scheduled_for': scheduled_post.scheduled_for.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/articles/<int:article_id>/seo-analysis', methods=['GET'])
@admin_required
def get_seo_analysis(article_id):
    """Get SEO analysis for an article"""
    try:
        analysis = SEOAnalysis.query.filter_by(article_id=article_id).order_by(
            SEOAnalysis.analyzed_at.desc()
        ).first()
        
        if not analysis:
            return jsonify({'success': False, 'error': 'No SEO analysis found'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'seo_score': analysis.seo_score,
                'readability_score': analysis.readability_score,
                'keyword_density': analysis.keyword_density,
                'meta_analysis': analysis.meta_analysis,
                'suggestions': analysis.suggestions,
                'analyzed_at': analysis.analyzed_at.isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/articles/<int:article_id>/seo-analysis', methods=['POST'])
@admin_required
def analyze_article_seo(article_id):
    """Perform SEO analysis on an article"""
    try:
        article = Article.query.get_or_404(article_id)
        
        # Perform SEO analysis (simplified version)
        seo_score = calculate_seo_score(article)
        readability_score = calculate_readability_score(article.content)
        keyword_density = analyze_keyword_density(article.content)
        meta_analysis = analyze_meta_tags(article)
        suggestions = generate_seo_suggestions(article, seo_score, readability_score)
        
        # Save analysis
        analysis = SEOAnalysis(
            article_id=article_id,
            seo_score=seo_score,
            readability_score=readability_score,
            keyword_density=keyword_density,
            meta_analysis=meta_analysis,
            suggestions=suggestions
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'seo_score': seo_score,
                'readability_score': readability_score,
                'suggestions': suggestions
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/templates', methods=['GET'])
@admin_required
def get_content_templates():
    """Get all content templates"""
    try:
        templates = ContentTemplate.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'template_type': template.template_type,
                'usage_count': template.usage_count,
                'created_by': {
                    'id': template.creator.id,
                    'username': template.creator.username
                },
                'created_at': template.created_at.isoformat()
            } for template in templates]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/templates', methods=['POST'])
@admin_required
def create_content_template():
    """Create a new content template"""
    try:
        data = request.get_json()
        
        template = ContentTemplate(
            name=data['name'],
            description=data.get('description', ''),
            template_type=data['template_type'],
            content_structure=data.get('content_structure', {}),
            default_values=data.get('default_values', {}),
            created_by=1  # TODO: Get from JWT token
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': template.id,
                'name': template.name
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/bulk-operations', methods=['POST'])
@admin_required
def create_bulk_operation():
    """Create a bulk operation"""
    try:
        data = request.get_json()
        
        bulk_op = BulkOperation(
            operation_type=data['operation_type'],
            target_type=data['target_type'],
            target_ids=data['target_ids'],
            operation_data=data.get('operation_data', {}),
            total_items=len(data['target_ids']),
            created_by=1  # TODO: Get from JWT token
        )
        
        db.session.add(bulk_op)
        db.session.commit()
        
        # Start bulk operation in background
        threading.Thread(target=process_bulk_operation, args=(bulk_op.id,)).start()
        
        return jsonify({
            'success': True,
            'data': {
                'id': bulk_op.id,
                'status': bulk_op.status
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/bulk-operations/<int:operation_id>', methods=['GET'])
@admin_required
def get_bulk_operation_status(operation_id):
    """Get status of a bulk operation"""
    try:
        bulk_op = BulkOperation.query.get_or_404(operation_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': bulk_op.id,
                'operation_type': bulk_op.operation_type,
                'status': bulk_op.status,
                'progress': bulk_op.progress,
                'total_items': bulk_op.total_items,
                'success_count': bulk_op.success_count,
                'error_count': bulk_op.error_count,
                'error_log': bulk_op.error_log,
                'created_at': bulk_op.created_at.isoformat(),
                'completed_at': bulk_op.completed_at.isoformat() if bulk_op.completed_at else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/settings', methods=['GET'])
@admin_required
def get_system_settings():
    """Get all system settings"""
    try:
        settings = SystemSettings.query.all()
        
        return jsonify({
            'success': True,
            'data': [{
                'key': setting.setting_key,
                'value': setting.setting_value,
                'type': setting.setting_type,
                'description': setting.description,
                'is_public': setting.is_public,
                'updated_at': setting.updated_at.isoformat()
            } for setting in settings]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/settings', methods=['PUT'])
@admin_required
def update_system_settings():
    """Update system settings"""
    try:
        data = request.get_json()
        
        for key, value in data.items():
            setting = SystemSettings.query.filter_by(setting_key=key).first()
            
            if setting:
                setting.setting_value = value
                setting.updated_by = 1  # TODO: Get from JWT token
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSettings(
                    setting_key=key,
                    setting_value=value,
                    updated_by=1
                )
                db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Settings updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Helper Functions

def calculate_seo_score(article):
    """Calculate SEO score for an article"""
    score = 0
    
    # Title length check
    if 30 <= len(article.title) <= 60:
        score += 20
    
    # Meta description check
    if article.seo_description and 120 <= len(article.seo_description) <= 160:
        score += 20
    
    # Content length check
    if len(article.content) >= 300:
        score += 20
    
    # Keywords in title
    if article.seo_keywords:
        keywords = [k.strip().lower() for k in article.seo_keywords.split(',')]
        title_lower = article.title.lower()
        if any(keyword in title_lower for keyword in keywords):
            score += 20
    
    # Image alt text check
    if 'alt=' in article.content:
        score += 20
    
    return min(score, 100)

def calculate_readability_score(content):
    """Calculate readability score (simplified Flesch Reading Ease)"""
    import re
    
    # Count sentences
    sentences = len(re.findall(r'[.!?]+', content))
    if sentences == 0:
        return 0
    
    # Count words
    words = len(content.split())
    if words == 0:
        return 0
    
    # Count syllables (simplified)
    syllables = sum([max(1, len(re.findall(r'[aeiouAEIOU]', word))) for word in content.split()])
    
    # Flesch Reading Ease formula
    if sentences > 0 and words > 0:
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0, min(100, score))
    
    return 0

def analyze_keyword_density(content):
    """Analyze keyword density in content"""
    import re
    from collections import Counter
    
    # Clean and tokenize content
    words = re.findall(r'\b\w+\b', content.lower())
    total_words = len(words)
    
    if total_words == 0:
        return {}
    
    # Count word frequency
    word_freq = Counter(words)
    
    # Calculate density for top words
    keyword_density = {}
    for word, count in word_freq.most_common(10):
        if len(word) > 3:  # Skip short words
            density = (count / total_words) * 100
            keyword_density[word] = round(density, 2)
    
    return keyword_density

def analyze_meta_tags(article):
    """Analyze meta tags for SEO"""
    analysis = {
        'title_length': len(article.title),
        'title_optimal': 30 <= len(article.title) <= 60,
        'meta_description_length': len(article.seo_description) if article.seo_description else 0,
        'meta_description_optimal': bool(article.seo_description and 120 <= len(article.seo_description) <= 160),
        'has_keywords': bool(article.seo_keywords),
        'keywords_count': len(article.seo_keywords.split(',')) if article.seo_keywords else 0
    }
    
    return analysis

def generate_seo_suggestions(article, seo_score, readability_score):
    """Generate SEO improvement suggestions"""
    suggestions = []
    
    if len(article.title) < 30:
        suggestions.append("Title is too short. Consider expanding it to 30-60 characters.")
    elif len(article.title) > 60:
        suggestions.append("Title is too long. Consider shortening it to under 60 characters.")
    
    if not article.seo_description:
        suggestions.append("Add a meta description to improve search engine visibility.")
    elif len(article.seo_description) < 120:
        suggestions.append("Meta description is too short. Expand it to 120-160 characters.")
    elif len(article.seo_description) > 160:
        suggestions.append("Meta description is too long. Shorten it to under 160 characters.")
    
    if not article.seo_keywords:
        suggestions.append("Add relevant keywords to improve search rankings.")
    
    if len(article.content) < 300:
        suggestions.append("Content is too short. Aim for at least 300 words for better SEO.")
    
    if readability_score < 60:
        suggestions.append("Content readability could be improved. Use shorter sentences and simpler words.")
    
    if 'alt=' not in article.content:
        suggestions.append("Add alt text to images for better accessibility and SEO.")
    
    return suggestions

def process_bulk_operation(operation_id):
    """Process bulk operation in background"""
    with app.app_context():
        bulk_op = BulkOperation.query.get(operation_id)
        if not bulk_op:
            return
        
        bulk_op.status = 'in_progress'
        db.session.commit()
        
        try:
            if bulk_op.operation_type == 'bulk_publish':
                process_bulk_publish(bulk_op)
            elif bulk_op.operation_type == 'bulk_delete':
                process_bulk_delete(bulk_op)
            elif bulk_op.operation_type == 'bulk_edit':
                process_bulk_edit(bulk_op)
            
            bulk_op.status = 'completed'
            bulk_op.completed_at = datetime.utcnow()
            
        except Exception as e:
            bulk_op.status = 'failed'
            bulk_op.error_log = bulk_op.error_log or []
            bulk_op.error_log.append(str(e))
        
        db.session.commit()

def process_bulk_publish(bulk_op):
    """Process bulk publish operation"""
    for article_id in bulk_op.target_ids:
        try:
            article = Article.query.get(article_id)
            if article:
                article.status = 'published'
                article.published_at = datetime.utcnow()
                bulk_op.success_count += 1
            
            bulk_op.progress = int((bulk_op.success_count + bulk_op.error_count) / bulk_op.total_items * 100)
            db.session.commit()
            
        except Exception as e:
            bulk_op.error_count += 1
            bulk_op.error_log = bulk_op.error_log or []
            bulk_op.error_log.append(f"Article {article_id}: {str(e)}")

def process_bulk_delete(bulk_op):
    """Process bulk delete operation"""
    for item_id in bulk_op.target_ids:
        try:
            if bulk_op.target_type == 'articles':
                article = Article.query.get(item_id)
                if article:
                    db.session.delete(article)
            elif bulk_op.target_type == 'comments':
                comment = Comment.query.get(item_id)
                if comment:
                    db.session.delete(comment)
            
            bulk_op.success_count += 1
            bulk_op.progress = int((bulk_op.success_count + bulk_op.error_count) / bulk_op.total_items * 100)
            db.session.commit()
            
        except Exception as e:
            bulk_op.error_count += 1
            bulk_op.error_log = bulk_op.error_log or []
            bulk_op.error_log.append(f"Item {item_id}: {str(e)}")

def process_bulk_edit(bulk_op):
    """Process bulk edit operation"""
    edit_data = bulk_op.operation_data
    
    for item_id in bulk_op.target_ids:
        try:
            if bulk_op.target_type == 'articles':
                article = Article.query.get(item_id)
                if article:
                    for field, value in edit_data.items():
                        if hasattr(article, field):
                            setattr(article, field, value)
            
            bulk_op.success_count += 1
            bulk_op.progress = int((bulk_op.success_count + bulk_op.error_count) / bulk_op.total_items * 100)
            db.session.commit()
            
        except Exception as e:
            bulk_op.error_count += 1
            bulk_op.error_log = bulk_op.error_log or []
            bulk_op.error_log.append(f"Item {item_id}: {str(e)}")

# Scheduled Tasks

def check_scheduled_posts():
    """Check for posts that need to be published"""
    with app.app_context():
        now = datetime.utcnow()
        scheduled_posts = ScheduledPost.query.filter(
            ScheduledPost.scheduled_for <= now,
            ScheduledPost.status == 'scheduled'
        ).all()
        
        for post in scheduled_posts:
            try:
                article = Article.query.get(post.article_id)
                if article:
                    article.status = 'published'
                    article.published_at = now
                    
                    post.status = 'published'
                    post.published_at = now
                    
                    db.session.commit()
                    
            except Exception as e:
                post.status = 'failed'
                post.error_message = str(e)
                db.session.commit()

# Schedule the task to run every minute
schedule.every().minute.do(check_scheduled_posts)

def run_scheduled_tasks():
    """Run scheduled tasks in background"""
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduled tasks in background thread
threading.Thread(target=run_scheduled_tasks, daemon=True).start()

# Initialize default workflow steps
def create_default_workflow():
    """Create default editorial workflow"""
    with app.app_context():
        if WorkflowStep.query.count() == 0:
            steps = [
                WorkflowStep(name='Draft Creation', order=1, required_role='author', auto_advance=True),
                WorkflowStep(name='Editorial Review', order=2, required_role='editor', auto_advance=False),
                WorkflowStep(name='Final Approval', order=3, required_role='admin', auto_advance=False),
                WorkflowStep(name='Publication', order=4, required_role='admin', auto_advance=True)
            ]
            
            for step in steps:
                db.session.add(step)
            
            db.session.commit()

# Initialize default settings
def create_default_settings():
    """Create default system settings"""
    with app.app_context():
        if SystemSettings.query.count() == 0:
            settings = [
                SystemSettings(setting_key='site_name', setting_value='GlobalPerspective', setting_type='string', description='Site name'),
                SystemSettings(setting_key='site_description', setting_value='International News and Analysis', setting_type='string', description='Site description'),
                SystemSettings(setting_key='articles_per_page', setting_value=20, setting_type='integer', description='Articles per page'),
                SystemSettings(setting_key='enable_comments', setting_value=True, setting_type='boolean', description='Enable comments'),
                SystemSettings(setting_key='auto_publish_scheduled', setting_value=True, setting_type='boolean', description='Auto-publish scheduled posts'),
                SystemSettings(setting_key='seo_analysis_enabled', setting_value=True, setting_type='boolean', description='Enable SEO analysis'),
                SystemSettings(setting_key='email_notifications', setting_value=True, setting_type='boolean', description='Enable email notifications')
            ]
            
            for setting in settings:
                db.session.add(setting)
            
            db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_workflow()
        create_default_settings()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

