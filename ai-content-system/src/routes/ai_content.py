from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json

from src.models.content import (
    db, MonitoringKeyword, AIProvider, TrendingTopic, 
    GeneratedArticle, ArticleAnalytics, ContentGenerationJob
)
from src.services.ai_content_generator import AIContentGenerator
from src.services.trend_monitor import TrendMonitor

ai_content_bp = Blueprint('ai_content', __name__)

# Initialize services
content_generator = AIContentGenerator()
trend_monitor = TrendMonitor()

# ============================================================================
# KEYWORD MANAGEMENT ROUTES
# ============================================================================

@ai_content_bp.route('/keywords', methods=['GET'])
def get_keywords():
    """Get all monitoring keywords"""
    try:
        keywords = MonitoringKeyword.query.all()
        return jsonify({
            'success': True,
            'keywords': [k.to_dict() for k in keywords]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/keywords', methods=['POST'])
def add_keyword():
    """Add a new monitoring keyword"""
    try:
        data = request.get_json()
        
        keyword = MonitoringKeyword(
            keyword=data['keyword'],
            category=data['category'],
            priority=data.get('priority', 1),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(keyword)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'keyword': keyword.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/keywords/<int:keyword_id>', methods=['PUT'])
def update_keyword(keyword_id):
    """Update a monitoring keyword"""
    try:
        keyword = MonitoringKeyword.query.get_or_404(keyword_id)
        data = request.get_json()
        
        keyword.keyword = data.get('keyword', keyword.keyword)
        keyword.category = data.get('category', keyword.category)
        keyword.priority = data.get('priority', keyword.priority)
        keyword.is_active = data.get('is_active', keyword.is_active)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'keyword': keyword.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/keywords/<int:keyword_id>', methods=['DELETE'])
def delete_keyword(keyword_id):
    """Delete a monitoring keyword"""
    try:
        keyword = MonitoringKeyword.query.get_or_404(keyword_id)
        db.session.delete(keyword)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# AI PROVIDER MANAGEMENT ROUTES
# ============================================================================

@ai_content_bp.route('/providers', methods=['GET'])
def get_providers():
    """Get all AI providers"""
    try:
        providers = AIProvider.query.all()
        available_providers = content_generator.get_available_providers()
        
        return jsonify({
            'success': True,
            'configured_providers': [p.to_dict() for p in providers],
            'available_providers': available_providers
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/providers', methods=['POST'])
def add_provider():
    """Add or update an AI provider configuration"""
    try:
        data = request.get_json()
        
        # Check if provider already exists
        existing = AIProvider.query.filter_by(name=data['name']).first()
        
        if existing:
            # Update existing provider
            existing.model_name = data.get('model_name', existing.model_name)
            existing.is_active = data.get('is_active', existing.is_active)
            existing.temperature = data.get('temperature', existing.temperature)
            existing.max_tokens = data.get('max_tokens', existing.max_tokens)
            existing.preferred_for_news = data.get('preferred_for_news', existing.preferred_for_news)
            existing.preferred_for_analysis = data.get('preferred_for_analysis', existing.preferred_for_analysis)
            existing.preferred_for_opinion = data.get('preferred_for_opinion', existing.preferred_for_opinion)
            
            provider = existing
        else:
            # Create new provider
            provider = AIProvider(
                name=data['name'],
                model_name=data.get('model_name'),
                is_active=data.get('is_active', True),
                temperature=data.get('temperature', 0.7),
                max_tokens=data.get('max_tokens', 4000),
                preferred_for_news=data.get('preferred_for_news', False),
                preferred_for_analysis=data.get('preferred_for_analysis', False),
                preferred_for_opinion=data.get('preferred_for_opinion', False)
            )
            db.session.add(provider)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'provider': provider.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# TREND MONITORING ROUTES
# ============================================================================

@ai_content_bp.route('/trends/monitor', methods=['POST'])
def monitor_trends():
    """Start monitoring trends for keywords"""
    try:
        data = request.get_json()
        hours_back = data.get('hours_back', 24)
        
        # Get active keywords
        keywords = MonitoringKeyword.query.filter_by(is_active=True).all()
        keyword_list = [k.keyword for k in keywords]
        
        if not keyword_list:
            return jsonify({
                'success': False,
                'error': 'No active keywords found'
            }), 400
        
        # Monitor trends
        trends = trend_monitor.monitor_trends(keyword_list, hours_back)
        
        # Save trends to database
        saved_trends = []
        for trend_data in trends:
            # Check if trend already exists
            existing = TrendingTopic.query.filter_by(
                topic=trend_data['topic'],
                source=trend_data['source']
            ).first()
            
            if not existing:
                trend = TrendingTopic(
                    topic=trend_data['topic'],
                    source=trend_data['source'],
                    engagement_score=trend_data.get('total_engagement', trend_data.get('engagement_score', 0)),
                    trend_velocity=trend_data.get('trend_velocity', 1.0),
                    sentiment_score=trend_data.get('sentiment_score', 0.0),
                    geographic_region=trend_data.get('geographic_region', 'global')
                )
                
                # Set matched keywords
                matched_keywords = trend_data.get('matched_keywords', [trend_data.get('matched_keyword')])
                if matched_keywords and matched_keywords[0]:
                    keyword_ids = []
                    for kw_text in matched_keywords:
                        kw = MonitoringKeyword.query.filter_by(keyword=kw_text).first()
                        if kw:
                            keyword_ids.append(kw.id)
                    trend.set_matched_keywords(keyword_ids)
                
                db.session.add(trend)
                saved_trends.append(trend)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'trends_found': len(trends),
            'trends_saved': len(saved_trends),
            'trends': [t.to_dict() for t in saved_trends]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get trending topics"""
    try:
        # Query parameters
        limit = request.args.get('limit', 50, type=int)
        hours_back = request.args.get('hours_back', 24, type=int)
        category = request.args.get('category')
        unprocessed_only = request.args.get('unprocessed_only', 'false').lower() == 'true'
        
        # Build query
        query = TrendingTopic.query
        
        # Filter by time
        since_time = datetime.utcnow() - timedelta(hours=hours_back)
        query = query.filter(TrendingTopic.detected_at >= since_time)
        
        # Filter by processing status
        if unprocessed_only:
            query = query.filter(TrendingTopic.is_processed == False)
        
        # Filter by category (through matched keywords)
        if category:
            keyword_ids = [k.id for k in MonitoringKeyword.query.filter_by(category=category).all()]
            if keyword_ids:
                # This is a simplified filter - in practice you'd need a more complex query
                query = query.filter(TrendingTopic.matched_keywords.isnot(None))
        
        # Order by engagement score and limit
        trends = query.order_by(TrendingTopic.engagement_score.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'trends': [t.to_dict() for t in trends]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ARTICLE GENERATION ROUTES
# ============================================================================

@ai_content_bp.route('/articles/generate', methods=['POST'])
def generate_article():
    """Generate an article from a trending topic or custom prompt"""
    try:
        data = request.get_json()
        
        # Required parameters
        topic = data.get('topic')
        category = data.get('category', 'World Affairs')
        
        # Optional parameters
        provider = data.get('provider', 'openai')
        model = data.get('model')
        article_type = data.get('article_type', 'news')
        keywords = data.get('keywords', [])
        target_length = data.get('target_length', 800)
        trend_id = data.get('trend_id')
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        # Generate the article
        result = content_generator.generate_article(
            topic=topic,
            category=category,
            provider=provider,
            model=model,
            article_type=article_type,
            keywords=keywords,
            target_length=target_length
        )
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        # Save to database
        article = GeneratedArticle(
            title=result.get('title', topic),
            subtitle=result.get('subtitle'),
            content=result.get('content'),
            excerpt=result.get('excerpt'),
            category=category,
            meta_description=result.get('meta_description'),
            featured_image_url=result.get('featured_image_url'),
            prompt_used=result.get('prompt_used'),
            generation_cost=result.get('generation_cost', 0.0),
            tokens_used=result.get('tokens_used', 0),
            readability_score=result.get('readability_score'),
            sentiment_score=result.get('sentiment_score')
        )
        
        # Set tags
        if result.get('tags'):
            article.set_tags(result['tags'])
        
        # Link to AI provider
        provider_obj = AIProvider.query.filter_by(name=provider).first()
        if provider_obj:
            article.ai_provider_id = provider_obj.id
        
        # Link to trending topic
        if trend_id:
            article.topic_id = trend_id
            # Mark trend as processed
            trend = TrendingTopic.query.get(trend_id)
            if trend:
                trend.is_processed = True
        
        db.session.add(article)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'article': article.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/articles', methods=['GET'])
def get_articles():
    """Get generated articles"""
    try:
        # Query parameters
        limit = request.args.get('limit', 20, type=int)
        status = request.args.get('status')
        category = request.args.get('category')
        provider = request.args.get('provider')
        
        # Build query
        query = GeneratedArticle.query
        
        if status:
            query = query.filter(GeneratedArticle.status == status)
        
        if category:
            query = query.filter(GeneratedArticle.category == category)
        
        if provider:
            provider_obj = AIProvider.query.filter_by(name=provider).first()
            if provider_obj:
                query = query.filter(GeneratedArticle.ai_provider_id == provider_obj.id)
        
        # Order by creation date and limit
        articles = query.order_by(GeneratedArticle.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'articles': [a.to_dict() for a in articles]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Get a specific article"""
    try:
        article = GeneratedArticle.query.get_or_404(article_id)
        return jsonify({
            'success': True,
            'article': article.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/articles/<int:article_id>/status', methods=['PUT'])
def update_article_status(article_id):
    """Update article status (draft, review, approved, published, rejected)"""
    try:
        article = GeneratedArticle.query.get_or_404(article_id)
        data = request.get_json()
        
        new_status = data.get('status')
        if new_status not in ['draft', 'review', 'approved', 'published', 'rejected']:
            return jsonify({
                'success': False,
                'error': 'Invalid status'
            }), 400
        
        article.status = new_status
        
        if new_status == 'published':
            article.is_published = True
            article.published_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'article': article.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """Update article content"""
    try:
        article = GeneratedArticle.query.get_or_404(article_id)
        data = request.get_json()
        
        # Update fields
        article.title = data.get('title', article.title)
        article.subtitle = data.get('subtitle', article.subtitle)
        article.content = data.get('content', article.content)
        article.excerpt = data.get('excerpt', article.excerpt)
        article.meta_description = data.get('meta_description', article.meta_description)
        article.featured_image_url = data.get('featured_image_url', article.featured_image_url)
        
        if data.get('tags'):
            article.set_tags(data['tags'])
        
        article.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'article': article.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ANALYTICS ROUTES
# ============================================================================

@ai_content_bp.route('/analytics/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get dashboard analytics"""
    try:
        # Get counts
        total_keywords = MonitoringKeyword.query.filter_by(is_active=True).count()
        total_trends = TrendingTopic.query.filter(
            TrendingTopic.detected_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        total_articles = GeneratedArticle.query.count()
        published_articles = GeneratedArticle.query.filter_by(is_published=True).count()
        
        # Get recent activity
        recent_trends = TrendingTopic.query.order_by(
            TrendingTopic.detected_at.desc()
        ).limit(5).all()
        
        recent_articles = GeneratedArticle.query.order_by(
            GeneratedArticle.created_at.desc()
        ).limit(5).all()
        
        # Get provider usage
        provider_usage = db.session.query(
            AIProvider.name,
            db.func.count(GeneratedArticle.id).label('count')
        ).join(GeneratedArticle).group_by(AIProvider.name).all()
        
        # Get category distribution
        category_distribution = db.session.query(
            GeneratedArticle.category,
            db.func.count(GeneratedArticle.id).label('count')
        ).group_by(GeneratedArticle.category).all()
        
        return jsonify({
            'success': True,
            'analytics': {
                'counts': {
                    'active_keywords': total_keywords,
                    'trends_this_week': total_trends,
                    'total_articles': total_articles,
                    'published_articles': published_articles
                },
                'recent_trends': [t.to_dict() for t in recent_trends],
                'recent_articles': [a.to_dict() for a in recent_articles],
                'provider_usage': [{'provider': p[0], 'count': p[1]} for p in provider_usage],
                'category_distribution': [{'category': c[0], 'count': c[1]} for c in category_distribution]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# AUTOMATION ROUTES
# ============================================================================

@ai_content_bp.route('/automation/generate-from-trends', methods=['POST'])
def auto_generate_from_trends():
    """Automatically generate articles from top trending topics"""
    try:
        data = request.get_json()
        max_articles = data.get('max_articles', 5)
        provider = data.get('provider', 'openai')
        article_type = data.get('article_type', 'news')
        
        # Get top unprocessed trends
        trends = TrendingTopic.query.filter_by(is_processed=False).order_by(
            TrendingTopic.engagement_score.desc()
        ).limit(max_articles).all()
        
        generated_articles = []
        
        for trend in trends:
            try:
                # Get matched keywords
                matched_keywords = []
                for keyword_id in trend.get_matched_keywords():
                    keyword = MonitoringKeyword.query.get(keyword_id)
                    if keyword:
                        matched_keywords.append(keyword.keyword)
                
                # Determine category from keywords
                category = 'World Affairs'  # Default
                if matched_keywords:
                    keyword_obj = MonitoringKeyword.query.filter_by(
                        keyword=matched_keywords[0]
                    ).first()
                    if keyword_obj:
                        category = keyword_obj.category
                
                # Generate article
                result = content_generator.generate_article(
                    topic=trend.topic,
                    category=category,
                    provider=provider,
                    article_type=article_type,
                    keywords=matched_keywords,
                    target_length=800
                )
                
                if 'error' not in result:
                    # Save article
                    article = GeneratedArticle(
                        title=result.get('title', trend.topic),
                        subtitle=result.get('subtitle'),
                        content=result.get('content'),
                        excerpt=result.get('excerpt'),
                        category=category,
                        topic_id=trend.id,
                        meta_description=result.get('meta_description'),
                        prompt_used=result.get('prompt_used'),
                        generation_cost=result.get('generation_cost', 0.0),
                        tokens_used=result.get('tokens_used', 0)
                    )
                    
                    # Link to provider
                    provider_obj = AIProvider.query.filter_by(name=provider).first()
                    if provider_obj:
                        article.ai_provider_id = provider_obj.id
                    
                    # Set tags
                    if result.get('tags'):
                        article.set_tags(result['tags'])
                    
                    db.session.add(article)
                    generated_articles.append(article)
                    
                    # Mark trend as processed
                    trend.is_processed = True
                
            except Exception as e:
                print(f"Error generating article for trend {trend.id}: {e}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'articles_generated': len(generated_articles),
            'articles': [a.to_dict() for a in generated_articles]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_content_bp.route('/automation/cost-estimate', methods=['POST'])
def estimate_generation_cost():
    """Estimate cost for generating articles"""
    try:
        data = request.get_json()
        word_count = data.get('word_count', 800)
        provider = data.get('provider', 'openai')
        article_count = data.get('article_count', 1)
        
        cost_per_article = content_generator.estimate_cost(word_count, provider)
        total_cost = cost_per_article * article_count
        
        return jsonify({
            'success': True,
            'estimate': {
                'cost_per_article': round(cost_per_article, 4),
                'total_cost': round(total_cost, 4),
                'provider': provider,
                'word_count': word_count,
                'article_count': article_count
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

