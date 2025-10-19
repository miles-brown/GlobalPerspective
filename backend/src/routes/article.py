from datetime import datetime
from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.article import Article, Category, MediaItem
import re

article_bp = Blueprint('article', __name__)

def create_slug(title):
    """Create URL-friendly slug from title"""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

@article_bp.route('/articles', methods=['GET'])
def get_articles():
    """Get all articles with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', 'published')
    category_id = request.args.get('category_id', type=int)
    featured = request.args.get('featured', type=bool)
    
    query = Article.query
    
    if status:
        query = query.filter(Article.status == status)
    if category_id:
        query = query.filter(Article.category_id == category_id)
    if featured is not None:
        query = query.filter(Article.is_featured == featured)
    
    # Order by published date for published articles, created date for others
    if status == 'published':
        query = query.order_by(Article.published_at.desc())
    else:
        query = query.order_by(Article.created_at.desc())
    
    articles = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'articles': [article.to_dict() for article in articles.items],
        'total': articles.total,
        'pages': articles.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': articles.has_next,
        'has_prev': articles.has_prev
    })

@article_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Get single article by ID"""
    article = Article.query.get_or_404(article_id)
    return jsonify(article.to_dict(include_content=True))

@article_bp.route('/articles/slug/<slug>', methods=['GET'])
def get_article_by_slug(slug):
    """Get single article by slug"""
    article = Article.query.filter_by(slug=slug).first_or_404()
    return jsonify(article.to_dict(include_content=True))

@article_bp.route('/articles', methods=['POST'])
def create_article():
    """Create new article"""
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400
    
    # Create slug from title
    slug = create_slug(data['title'])
    
    # Check if slug already exists
    existing = Article.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    article = Article(
        title=data['title'],
        slug=slug,
        subtitle=data.get('subtitle'),
        content=data['content'],
        excerpt=data.get('excerpt'),
        featured_image=data.get('featured_image'),
        featured_image_caption=data.get('featured_image_caption'),
        status=data.get('status', 'draft'),
        is_featured=data.get('is_featured', False),
        is_breaking=data.get('is_breaking', False),
        meta_description=data.get('meta_description'),
        meta_keywords=data.get('meta_keywords'),
        author_id=data.get('author_id', 1),  # Default to first user for now
        category_id=data.get('category_id', 1)  # Default to first category
    )
    
    if data.get('status') == 'published' and not article.published_at:
        article.published_at = datetime.utcnow()
    
    try:
        db.session.add(article)
        db.session.commit()
        return jsonify(article.to_dict(include_content=True)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@article_bp.route('/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """Update existing article"""
    article = Article.query.get_or_404(article_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields if provided
    if 'title' in data:
        article.title = data['title']
        # Update slug if title changed
        new_slug = create_slug(data['title'])
        if new_slug != article.slug:
            existing = Article.query.filter_by(slug=new_slug).filter(Article.id != article_id).first()
            if not existing:
                article.slug = new_slug
    
    if 'subtitle' in data:
        article.subtitle = data['subtitle']
    if 'content' in data:
        article.content = data['content']
    if 'excerpt' in data:
        article.excerpt = data['excerpt']
    if 'featured_image' in data:
        article.featured_image = data['featured_image']
    if 'featured_image_caption' in data:
        article.featured_image_caption = data['featured_image_caption']
    if 'is_featured' in data:
        article.is_featured = data['is_featured']
    if 'is_breaking' in data:
        article.is_breaking = data['is_breaking']
    if 'meta_description' in data:
        article.meta_description = data['meta_description']
    if 'meta_keywords' in data:
        article.meta_keywords = data['meta_keywords']
    if 'category_id' in data:
        article.category_id = data['category_id']
    
    # Handle status changes
    if 'status' in data:
        old_status = article.status
        article.status = data['status']
        
        # Set published_at when publishing for the first time
        if data['status'] == 'published' and old_status != 'published':
            article.published_at = datetime.utcnow()
    
    article.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify(article.to_dict(include_content=True))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@article_bp.route('/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """Delete article"""
    article = Article.query.get_or_404(article_id)
    
    try:
        db.session.delete(article)
        db.session.commit()
        return jsonify({'message': 'Article deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@article_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = Category.query.order_by(Category.name).all()
    return jsonify([category.to_dict() for category in categories])

@article_bp.route('/categories', methods=['POST'])
def create_category():
    """Create new category"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Category name is required'}), 400
    
    slug = create_slug(data['name'])
    
    # Check if slug already exists
    existing = Category.query.filter_by(slug=slug).first()
    if existing:
        return jsonify({'error': 'Category with this name already exists'}), 400
    
    category = Category(
        name=data['name'],
        slug=slug,
        description=data.get('description')
    )
    
    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@article_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update category"""
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' in data:
        category.name = data['name']
        new_slug = create_slug(data['name'])
        if new_slug != category.slug:
            existing = Category.query.filter_by(slug=new_slug).filter(Category.id != category_id).first()
            if not existing:
                category.slug = new_slug
    
    if 'description' in data:
        category.description = data['description']
    
    try:
        db.session.commit()
        return jsonify(category.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@article_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete category"""
    category = Category.query.get_or_404(category_id)
    
    # Check if category has articles
    if category.articles:
        return jsonify({'error': 'Cannot delete category with articles'}), 400
    
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

