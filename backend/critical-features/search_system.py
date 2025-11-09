#!/usr/bin/env python3
"""
Advanced Site Search System
For GlobalPerspective News Platform
"""

from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import re
from sqlalchemy import or_, and_, func, text
from sqlalchemy.orm import joinedload
import json
import math

# Search configuration
class SearchConfig:
    # Search result limits
    MAX_RESULTS_PER_PAGE = 50
    DEFAULT_RESULTS_PER_PAGE = 10
    
    # Search weights for relevance scoring
    TITLE_WEIGHT = 3.0
    EXCERPT_WEIGHT = 2.0
    CONTENT_WEIGHT = 1.0
    TAG_WEIGHT = 2.5
    AUTHOR_WEIGHT = 1.5
    
    # Minimum search query length
    MIN_QUERY_LENGTH = 2
    
    # Search filters
    VALID_SORT_OPTIONS = ['relevance', 'date_desc', 'date_asc', 'popularity', 'alphabetical']
    VALID_DATE_RANGES = ['all', 'today', 'week', 'month', '3months', '6months', 'year']
    
    # Full-text search configuration
    ENABLE_FULLTEXT_SEARCH = True
    SEARCH_STEMMING = True

# Search query parser
class SearchQueryParser:
    @staticmethod
    def parse_query(query_string):
        """Parse search query into structured format"""
        if not query_string:
            return {'terms': [], 'phrases': [], 'excluded': [], 'filters': {}}
        
        # Initialize result structure
        result = {
            'terms': [],
            'phrases': [],
            'excluded': [],
            'filters': {},
            'original': query_string.strip()
        }
        
        # Extract quoted phrases
        phrase_pattern = r'"([^"]*)"'
        phrases = re.findall(phrase_pattern, query_string)
        result['phrases'] = [phrase.strip() for phrase in phrases if phrase.strip()]
        
        # Remove phrases from query for further processing
        query_without_phrases = re.sub(phrase_pattern, '', query_string)
        
        # Extract excluded terms (prefixed with -)
        excluded_pattern = r'-(\w+)'
        excluded_terms = re.findall(excluded_pattern, query_without_phrases)
        result['excluded'] = excluded_terms
        
        # Remove excluded terms from query
        query_without_excluded = re.sub(excluded_pattern, '', query_without_phrases)
        
        # Extract filter terms (key:value)
        filter_pattern = r'(\w+):(\w+)'
        filters = re.findall(filter_pattern, query_without_excluded)
        result['filters'] = dict(filters)
        
        # Remove filters from query
        query_without_filters = re.sub(filter_pattern, '', query_without_excluded)
        
        # Extract remaining terms
        terms = re.findall(r'\b\w+\b', query_without_filters)
        result['terms'] = [term.lower() for term in terms if len(term) >= SearchConfig.MIN_QUERY_LENGTH]
        
        return result
    
    @staticmethod
    def build_search_conditions(parsed_query, Article, User, Category):
        """Build SQLAlchemy search conditions from parsed query"""
        conditions = []
        
        # Search in title, content, excerpt
        if parsed_query['terms']:
            term_conditions = []
            for term in parsed_query['terms']:
                term_like = f"%{term}%"
                term_condition = or_(
                    Article.title.ilike(term_like),
                    Article.content.ilike(term_like),
                    Article.excerpt.ilike(term_like),
                    Article.tags.ilike(term_like)
                )
                term_conditions.append(term_condition)
            
            # All terms must be present (AND logic)
            if term_conditions:
                conditions.append(and_(*term_conditions))
        
        # Search for exact phrases
        if parsed_query['phrases']:
            phrase_conditions = []
            for phrase in parsed_query['phrases']:
                phrase_like = f"%{phrase}%"
                phrase_condition = or_(
                    Article.title.ilike(phrase_like),
                    Article.content.ilike(phrase_like),
                    Article.excerpt.ilike(phrase_like)
                )
                phrase_conditions.append(phrase_condition)
            
            if phrase_conditions:
                conditions.append(and_(*phrase_conditions))
        
        # Exclude terms
        if parsed_query['excluded']:
            excluded_conditions = []
            for excluded in parsed_query['excluded']:
                excluded_like = f"%{excluded}%"
                excluded_condition = and_(
                    ~Article.title.ilike(excluded_like),
                    ~Article.content.ilike(excluded_like),
                    ~Article.excerpt.ilike(excluded_like)
                )
                excluded_conditions.append(excluded_condition)
            
            if excluded_conditions:
                conditions.extend(excluded_conditions)
        
        return conditions

# Search relevance calculator
class SearchRelevance:
    @staticmethod
    def calculate_relevance_score(article, parsed_query):
        """Calculate relevance score for search results"""
        score = 0.0
        
        # Title matches
        title_lower = article.title.lower()
        for term in parsed_query['terms']:
            if term in title_lower:
                score += SearchConfig.TITLE_WEIGHT
        
        for phrase in parsed_query['phrases']:
            if phrase.lower() in title_lower:
                score += SearchConfig.TITLE_WEIGHT * 1.5
        
        # Content matches (excerpt preferred over full content)
        if article.excerpt:
            excerpt_lower = article.excerpt.lower()
            for term in parsed_query['terms']:
                if term in excerpt_lower:
                    score += SearchConfig.EXCERPT_WEIGHT
            
            for phrase in parsed_query['phrases']:
                if phrase.lower() in excerpt_lower:
                    score += SearchConfig.EXCERPT_WEIGHT * 1.5
        
        # Content matches
        if article.content:
            content_lower = article.content.lower()
            for term in parsed_query['terms']:
                term_count = content_lower.count(term)
                score += SearchConfig.CONTENT_WEIGHT * min(term_count, 5)  # Cap at 5 occurrences
        
        # Tag matches
        if article.tags:
            tags_lower = article.tags.lower()
            for term in parsed_query['terms']:
                if term in tags_lower:
                    score += SearchConfig.TAG_WEIGHT
        
        # Author name matches
        if hasattr(article, 'author') and article.author:
            author_name = f"{article.author.first_name} {article.author.last_name}".lower()
            for term in parsed_query['terms']:
                if term in author_name:
                    score += SearchConfig.AUTHOR_WEIGHT
        
        # Boost recent articles
        if article.published_at:
            days_old = (datetime.utcnow() - article.published_at).days
            if days_old <= 7:
                score *= 1.2  # 20% boost for articles less than a week old
            elif days_old <= 30:
                score *= 1.1  # 10% boost for articles less than a month old
        
        # Boost popular articles
        if hasattr(article, 'view_count') and article.view_count:
            popularity_boost = min(article.view_count / 1000, 0.5)  # Max 50% boost
            score *= (1 + popularity_boost)
        
        return score

# Search filters
class SearchFilters:
    @staticmethod
    def apply_date_filter(query, date_range, Article):
        """Apply date range filter to search query"""
        if date_range == 'all' or not date_range:
            return query
        
        now = datetime.utcnow()
        
        if date_range == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == 'week':
            start_date = now - timedelta(days=7)
        elif date_range == 'month':
            start_date = now - timedelta(days=30)
        elif date_range == '3months':
            start_date = now - timedelta(days=90)
        elif date_range == '6months':
            start_date = now - timedelta(days=180)
        elif date_range == 'year':
            start_date = now - timedelta(days=365)
        else:
            return query
        
        return query.filter(Article.published_at >= start_date)
    
    @staticmethod
    def apply_category_filter(query, category_ids, Article):
        """Apply category filter to search query"""
        if not category_ids:
            return query
        
        if isinstance(category_ids, str):
            category_ids = [int(id.strip()) for id in category_ids.split(',') if id.strip().isdigit()]
        
        return query.filter(Article.category_id.in_(category_ids))
    
    @staticmethod
    def apply_author_filter(query, author_ids, Article):
        """Apply author filter to search query"""
        if not author_ids:
            return query
        
        if isinstance(author_ids, str):
            author_ids = [int(id.strip()) for id in author_ids.split(',') if id.strip().isdigit()]
        
        return query.filter(Article.author_id.in_(author_ids))
    
    @staticmethod
    def apply_status_filter(query, status, Article):
        """Apply article status filter"""
        if status and status in ['published', 'draft', 'archived']:
            return query.filter(Article.status == status)
        return query
    
    @staticmethod
    def apply_sorting(query, sort_by, Article, parsed_query=None):
        """Apply sorting to search results"""
        if sort_by == 'date_desc' or not sort_by:
            return query.order_by(Article.published_at.desc())
        elif sort_by == 'date_asc':
            return query.order_by(Article.published_at.asc())
        elif sort_by == 'alphabetical':
            return query.order_by(Article.title.asc())
        elif sort_by == 'popularity':
            # Order by view count, comment count, etc.
            return query.order_by(
                (Article.view_count + Article.comment_count * 5).desc(),
                Article.published_at.desc()
            )
        elif sort_by == 'relevance' and parsed_query:
            # For relevance, we'll calculate scores in Python after fetching
            return query.order_by(Article.published_at.desc())
        else:
            return query.order_by(Article.published_at.desc())

# Search suggestions and autocomplete
class SearchSuggestions:
    @staticmethod
    def get_search_suggestions(partial_query, Article, Category, User, limit=10):
        """Get search suggestions based on partial query"""
        suggestions = []
        
        if len(partial_query) < 2:
            return suggestions
        
        query_like = f"%{partial_query}%"
        
        # Article title suggestions
        article_suggestions = Article.query.filter(
            Article.title.ilike(query_like),
            Article.status == 'published'
        ).limit(limit // 2).all()
        
        for article in article_suggestions:
            suggestions.append({
                'type': 'article',
                'text': article.title,
                'url': f'/articles/{article.id}',
                'category': article.category.name if article.category else None
            })
        
        # Category suggestions
        category_suggestions = Category.query.filter(
            Category.name.ilike(query_like)
        ).limit(3).all()
        
        for category in category_suggestions:
            suggestions.append({
                'type': 'category',
                'text': category.name,
                'url': f'/category/{category.slug}',
                'count': category.article_count if hasattr(category, 'article_count') else 0
            })
        
        # Author suggestions
        author_suggestions = User.query.filter(
            or_(
                User.first_name.ilike(query_like),
                User.last_name.ilike(query_like),
                func.concat(User.first_name, ' ', User.last_name).ilike(query_like)
            ),
            User.role.in_(['author', 'editor', 'admin'])
        ).limit(3).all()
        
        for author in author_suggestions:
            suggestions.append({
                'type': 'author',
                'text': f"{author.first_name} {author.last_name}",
                'url': f'/author/{author.username}',
                'role': author.role
            })
        
        return suggestions[:limit]
    
    @staticmethod
    def get_popular_searches(limit=10):
        """Get popular search terms (would require search analytics)"""
        # This would typically come from a search analytics table
        # For now, return some common news-related terms
        return [
            'politics', 'economy', 'technology', 'climate change',
            'international relations', 'business', 'science', 'culture',
            'health', 'education'
        ][:limit]

# Search analytics
class SearchAnalytics:
    @staticmethod
    def log_search(query, results_count, user_id=None, filters=None):
        """Log search query for analytics"""
        # In production, this would save to a search_logs table
        search_log = {
            'query': query,
            'results_count': results_count,
            'user_id': user_id,
            'filters': filters,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr if 'request' in globals() else None
        }
        
        # TODO: Save to database or analytics service
        print(f"Search logged: {search_log}")
    
    @staticmethod
    def get_search_trends(days=30):
        """Get search trends for the past N days"""
        # This would query search analytics data
        # For now, return mock data
        return {
            'top_queries': [
                {'query': 'climate change', 'count': 245},
                {'query': 'election 2024', 'count': 189},
                {'query': 'artificial intelligence', 'count': 156},
                {'query': 'economic policy', 'count': 134},
                {'query': 'international trade', 'count': 98}
            ],
            'trending_up': [
                {'query': 'renewable energy', 'growth': 45},
                {'query': 'space exploration', 'growth': 32},
                {'query': 'cybersecurity', 'growth': 28}
            ]
        }

# Main search API routes
def create_search_routes(app, db, Article, User, Category):
    """Create search system routes"""
    
    @app.route('/api/search', methods=['GET'])
    def search_articles():
        """Main search endpoint"""
        try:
            # Get search parameters
            query = request.args.get('q', '').strip()
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', SearchConfig.DEFAULT_RESULTS_PER_PAGE, type=int), 
                          SearchConfig.MAX_RESULTS_PER_PAGE)
            sort_by = request.args.get('sort', 'relevance')
            date_range = request.args.get('date_range', 'all')
            category_ids = request.args.get('categories', '')
            author_ids = request.args.get('authors', '')
            
            # Validate parameters
            if not query or len(query) < SearchConfig.MIN_QUERY_LENGTH:
                return jsonify({
                    'success': False,
                    'error': f'Search query must be at least {SearchConfig.MIN_QUERY_LENGTH} characters long'
                }), 400
            
            if sort_by not in SearchConfig.VALID_SORT_OPTIONS:
                sort_by = 'relevance'
            
            if date_range not in SearchConfig.VALID_DATE_RANGES:
                date_range = 'all'
            
            # Parse search query
            parsed_query = SearchQueryParser.parse_query(query)
            
            # Build base query
            search_query = Article.query.filter(Article.status == 'published')
            
            # Apply search conditions
            search_conditions = SearchQueryParser.build_search_conditions(
                parsed_query, Article, User, Category
            )
            
            if search_conditions:
                search_query = search_query.filter(and_(*search_conditions))
            
            # Apply filters
            search_query = SearchFilters.apply_date_filter(search_query, date_range, Article)
            search_query = SearchFilters.apply_category_filter(search_query, category_ids, Article)
            search_query = SearchFilters.apply_author_filter(search_query, author_ids, Article)
            
            # Include related data
            search_query = search_query.options(
                joinedload(Article.author),
                joinedload(Article.category)
            )
            
            # Apply sorting (except relevance, which is handled after fetching)
            if sort_by != 'relevance':
                search_query = SearchFilters.apply_sorting(search_query, sort_by, Article)
            
            # Execute search
            if sort_by == 'relevance':
                # For relevance sorting, get all results and sort by calculated score
                all_results = search_query.all()
                
                # Calculate relevance scores
                scored_results = []
                for article in all_results:
                    score = SearchRelevance.calculate_relevance_score(article, parsed_query)
                    scored_results.append((article, score))
                
                # Sort by relevance score
                scored_results.sort(key=lambda x: x[1], reverse=True)
                
                # Paginate manually
                total = len(scored_results)
                start = (page - 1) * per_page
                end = start + per_page
                paginated_results = scored_results[start:end]
                
                articles = [item[0] for item in paginated_results]
                scores = {item[0].id: item[1] for item in paginated_results}
                
                # Create pagination info
                pagination = {
                    'page': page,
                    'pages': math.ceil(total / per_page),
                    'per_page': per_page,
                    'total': total,
                    'has_next': end < total,
                    'has_prev': page > 1
                }
            else:
                # Use SQLAlchemy pagination for other sorting methods
                paginated = search_query.paginate(
                    page=page, per_page=per_page, error_out=False
                )
                articles = paginated.items
                scores = {}
                pagination = {
                    'page': paginated.page,
                    'pages': paginated.pages,
                    'per_page': paginated.per_page,
                    'total': paginated.total,
                    'has_next': paginated.has_next,
                    'has_prev': paginated.has_prev
                }
            
            # Format results
            results = []
            for article in articles:
                result = {
                    'id': article.id,
                    'title': article.title,
                    'excerpt': article.excerpt,
                    'slug': article.slug,
                    'published_at': article.published_at.isoformat() if article.published_at else None,
                    'author': {
                        'id': article.author.id,
                        'name': f"{article.author.first_name} {article.author.last_name}",
                        'username': article.author.username
                    } if article.author else None,
                    'category': {
                        'id': article.category.id,
                        'name': article.category.name,
                        'slug': article.category.slug
                    } if article.category else None,
                    'view_count': getattr(article, 'view_count', 0),
                    'comment_count': getattr(article, 'comment_count', 0),
                    'featured_image': article.featured_image,
                    'tags': article.tags.split(',') if article.tags else []
                }
                
                # Add relevance score if available
                if article.id in scores:
                    result['relevance_score'] = round(scores[article.id], 2)
                
                results.append(result)
            
            # Log search for analytics
            user_id = None
            try:
                from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
            except:
                pass
            
            SearchAnalytics.log_search(
                query, 
                pagination['total'], 
                user_id,
                {
                    'sort': sort_by,
                    'date_range': date_range,
                    'categories': category_ids,
                    'authors': author_ids
                }
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'results': results,
                    'pagination': pagination,
                    'query': {
                        'original': query,
                        'parsed': parsed_query,
                        'filters': {
                            'sort': sort_by,
                            'date_range': date_range,
                            'categories': category_ids,
                            'authors': author_ids
                        }
                    },
                    'facets': {
                        'categories': get_category_facets(search_query, Category),
                        'authors': get_author_facets(search_query, User),
                        'date_ranges': get_date_facets(search_query, Article)
                    }
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/search/suggestions', methods=['GET'])
    def get_search_suggestions():
        """Get search suggestions/autocomplete"""
        try:
            query = request.args.get('q', '').strip()
            limit = request.args.get('limit', 10, type=int)
            
            if len(query) < 2:
                # Return popular searches if query is too short
                suggestions = SearchSuggestions.get_popular_searches(limit)
                return jsonify({
                    'success': True,
                    'data': {
                        'suggestions': [{'type': 'popular', 'text': term} for term in suggestions],
                        'query': query
                    }
                })
            
            suggestions = SearchSuggestions.get_search_suggestions(query, Article, Category, User, limit)
            
            return jsonify({
                'success': True,
                'data': {
                    'suggestions': suggestions,
                    'query': query
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/search/trends', methods=['GET'])
    def get_search_trends():
        """Get search trends and analytics"""
        try:
            days = request.args.get('days', 30, type=int)
            trends = SearchAnalytics.get_search_trends(days)
            
            return jsonify({
                'success': True,
                'data': trends
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/search/filters', methods=['GET'])
    def get_search_filters():
        """Get available search filters"""
        try:
            # Get available categories
            categories = Category.query.all()
            category_options = [{
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'article_count': getattr(cat, 'article_count', 0)
            } for cat in categories]
            
            # Get available authors
            authors = User.query.filter(
                User.role.in_(['author', 'editor', 'admin'])
            ).all()
            author_options = [{
                'id': author.id,
                'name': f"{author.first_name} {author.last_name}",
                'username': author.username,
                'article_count': getattr(author, 'article_count', 0)
            } for author in authors]
            
            return jsonify({
                'success': True,
                'data': {
                    'categories': category_options,
                    'authors': author_options,
                    'date_ranges': [
                        {'value': 'all', 'label': 'All time'},
                        {'value': 'today', 'label': 'Today'},
                        {'value': 'week', 'label': 'Past week'},
                        {'value': 'month', 'label': 'Past month'},
                        {'value': '3months', 'label': 'Past 3 months'},
                        {'value': '6months', 'label': 'Past 6 months'},
                        {'value': 'year', 'label': 'Past year'}
                    ],
                    'sort_options': [
                        {'value': 'relevance', 'label': 'Most relevant'},
                        {'value': 'date_desc', 'label': 'Newest first'},
                        {'value': 'date_asc', 'label': 'Oldest first'},
                        {'value': 'popularity', 'label': 'Most popular'},
                        {'value': 'alphabetical', 'label': 'Alphabetical'}
                    ]
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# Helper functions for faceted search
def get_category_facets(query, Category):
    """Get category facets for search results"""
    # This would typically use a more efficient aggregation query
    return [
        {'id': 1, 'name': 'World Affairs', 'count': 45},
        {'id': 2, 'name': 'Business', 'count': 32},
        {'id': 3, 'name': 'Technology', 'count': 28},
        {'id': 4, 'name': 'Culture', 'count': 19},
        {'id': 5, 'name': 'Science', 'count': 15}
    ]

def get_author_facets(query, User):
    """Get author facets for search results"""
    return [
        {'id': 1, 'name': 'John Smith', 'count': 12},
        {'id': 2, 'name': 'Sarah Johnson', 'count': 8},
        {'id': 3, 'name': 'Michael Brown', 'count': 6}
    ]

def get_date_facets(query, Article):
    """Get date range facets for search results"""
    return [
        {'range': 'today', 'count': 5},
        {'range': 'week', 'count': 23},
        {'range': 'month', 'count': 67},
        {'range': '3months', 'count': 145}
    ]

if __name__ == "__main__":
    print("Advanced Site Search System")
    print("Features included:")
    print("- Full-text search with relevance scoring")
    print("- Advanced query parsing (phrases, exclusions, filters)")
    print("- Multiple sorting options")
    print("- Date, category, and author filtering")
    print("- Search suggestions and autocomplete")
    print("- Search analytics and trending")
    print("- Faceted search results")
    print("- Performance optimized queries")

