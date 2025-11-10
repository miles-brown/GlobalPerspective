import os
import json
import requests
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import openai
from flask import Flask, request, jsonify
import schedule
import time
import threading
from dataclasses import dataclass
import re
from collections import Counter
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade
import yake

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

@dataclass
class ContentAnalysis:
    readability_score: float
    sentiment_score: float
    key_topics: List[str]
    word_count: int
    reading_time: int
    seo_score: float
    engagement_prediction: float

@dataclass
class TrendingTopic:
    topic: str
    relevance_score: float
    source: str
    timestamp: datetime
    related_keywords: List[str]
    article_potential: float

class AdvancedAIContentSystem:
    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.trending_topics = []
        self.content_cache = {}
        self.analytics_data = {}
        
    # Content Generation with Multiple AI Providers
    async def generate_article(self, topic: str, style: str = "professional", 
                             length: str = "medium", target_audience: str = "general",
                             ai_provider: str = "openai") -> Dict:
        """Generate high-quality articles using various AI providers"""
        
        # Define article parameters
        word_counts = {
            "short": "400-600 words",
            "medium": "800-1200 words", 
            "long": "1500-2500 words",
            "in-depth": "3000+ words"
        }
        
        style_prompts = {
            "professional": "Write in a professional, authoritative tone suitable for business readers",
            "conversational": "Write in a friendly, conversational tone that's easy to understand",
            "academic": "Write in an academic style with proper citations and formal language",
            "investigative": "Write in an investigative journalism style with deep analysis",
            "opinion": "Write as an opinion piece with strong viewpoints and persuasive arguments"
        }
        
        audience_context = {
            "general": "for a general international audience",
            "business": "for business professionals and executives", 
            "academic": "for researchers and academics",
            "policy": "for policy makers and government officials",
            "youth": "for young adults and students"
        }
        
        # Construct the prompt
        prompt = f"""
        Write a comprehensive news article about: {topic}
        
        Requirements:
        - Length: {word_counts.get(length, word_counts['medium'])}
        - Style: {style_prompts.get(style, style_prompts['professional'])}
        - Audience: {audience_context.get(target_audience, audience_context['general'])}
        - Include a compelling headline
        - Add a brief excerpt/summary
        - Structure with clear sections and subheadings
        - Include relevant quotes (can be hypothetical but realistic)
        - End with a conclusion that ties everything together
        - Ensure factual accuracy and balanced perspective
        
        Format the response as JSON with the following structure:
        {{
            "headline": "Article headline",
            "excerpt": "Brief summary",
            "content": "Full article content with HTML formatting",
            "tags": ["tag1", "tag2", "tag3"],
            "category": "appropriate category",
            "estimated_reading_time": "X minutes"
        }}
        """
        
        try:
            if ai_provider == "openai":
                response = await self._generate_with_openai(prompt)
            elif ai_provider == "claude":
                response = await self._generate_with_claude(prompt)
            elif ai_provider == "deepseek":
                response = await self._generate_with_deepseek(prompt)
            else:
                response = await self._generate_with_openai(prompt)  # Default fallback
                
            # Parse and validate response
            article_data = json.loads(response)
            
            # Add metadata
            article_data.update({
                "generated_at": datetime.now().isoformat(),
                "ai_provider": ai_provider,
                "generation_params": {
                    "topic": topic,
                    "style": style,
                    "length": length,
                    "target_audience": target_audience
                }
            })
            
            # Analyze content quality
            analysis = await self.analyze_content(article_data["content"])
            article_data["content_analysis"] = analysis.__dict__
            
            return article_data
            
        except Exception as e:
            return {"error": f"Failed to generate article: {str(e)}"}
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate content using OpenAI GPT"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional journalist and content creator specializing in international news and world affairs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    
    async def _generate_with_claude(self, prompt: str) -> str:
        """Generate content using Claude (Anthropic)"""
        # This would integrate with Claude API
        # For now, fallback to OpenAI
        return await self._generate_with_openai(prompt)
    
    async def _generate_with_deepseek(self, prompt: str) -> str:
        """Generate content using DeepSeek"""
        # This would integrate with DeepSeek API
        # For now, fallback to OpenAI
        return await self._generate_with_openai(prompt)
    
    # Advanced Content Analysis
    async def analyze_content(self, content: str) -> ContentAnalysis:
        """Perform comprehensive content analysis"""
        
        # Clean HTML tags for analysis
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # Basic metrics
        word_count = len(clean_content.split())
        reading_time = max(1, word_count // 200)  # Average reading speed
        
        # Readability analysis
        try:
            readability_score = flesch_reading_ease(clean_content)
        except:
            readability_score = 50.0  # Default moderate score
        
        # Sentiment analysis
        sentiment_score = await self._analyze_sentiment(clean_content)
        
        # Extract key topics
        key_topics = await self._extract_key_topics(clean_content)
        
        # SEO analysis
        seo_score = await self._analyze_seo(content, clean_content)
        
        # Engagement prediction
        engagement_prediction = await self._predict_engagement(
            clean_content, readability_score, sentiment_score, word_count
        )
        
        return ContentAnalysis(
            readability_score=readability_score,
            sentiment_score=sentiment_score,
            key_topics=key_topics,
            word_count=word_count,
            reading_time=reading_time,
            seo_score=seo_score,
            engagement_prediction=engagement_prediction
        )
    
    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of the content"""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            scores = analyzer.polarity_scores(text)
            return scores['compound']  # Returns value between -1 and 1
        except:
            return 0.0  # Neutral sentiment as fallback
    
    async def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics and keywords from content"""
        try:
            # Use YAKE for keyword extraction
            kw_extractor = yake.KeywordExtractor(
                lan="en",
                n=3,  # n-gram size
                dedupLim=0.7,
                top=10
            )
            keywords = kw_extractor.extract_keywords(text)
            return [kw[1] for kw in keywords[:5]]  # Return top 5 keywords
        except:
            # Fallback: simple word frequency analysis
            words = re.findall(r'\b\w+\b', text.lower())
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
            filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
            return [word for word, count in Counter(filtered_words).most_common(5)]
    
    async def _analyze_seo(self, html_content: str, text_content: str) -> float:
        """Analyze SEO quality of the content"""
        score = 0.0
        
        # Check for headings
        if re.search(r'<h[1-6]>', html_content):
            score += 20
        
        # Check content length (800-2000 words is optimal)
        word_count = len(text_content.split())
        if 800 <= word_count <= 2000:
            score += 30
        elif word_count >= 500:
            score += 15
        
        # Check for internal structure
        if re.search(r'<p>', html_content):
            score += 10
        
        # Check for lists
        if re.search(r'<(ul|ol)>', html_content):
            score += 10
        
        # Check for images (alt text would be ideal)
        if re.search(r'<img', html_content):
            score += 10
        
        # Readability bonus
        try:
            readability = flesch_reading_ease(text_content)
            if 60 <= readability <= 80:  # Optimal range
                score += 20
            elif 40 <= readability <= 90:
                score += 10
        except:
            pass
        
        return min(score, 100.0)
    
    async def _predict_engagement(self, content: str, readability: float, 
                                sentiment: float, word_count: int) -> float:
        """Predict engagement potential of the content"""
        
        # Base score
        engagement_score = 50.0
        
        # Readability factor (easier to read = higher engagement)
        if readability > 60:
            engagement_score += 15
        elif readability > 40:
            engagement_score += 5
        
        # Sentiment factor (slightly positive content performs better)
        if 0.1 <= sentiment <= 0.5:
            engagement_score += 10
        elif sentiment > 0.5:
            engagement_score += 5
        
        # Length factor (medium length performs best)
        if 600 <= word_count <= 1200:
            engagement_score += 15
        elif 400 <= word_count <= 1800:
            engagement_score += 10
        
        # Content quality indicators
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        if 15 <= avg_sentence_length <= 25:  # Optimal sentence length
            engagement_score += 10
        
        return min(engagement_score, 100.0)
    
    # Trend Detection and Monitoring
    async def detect_trending_topics(self, sources: List[str] = None) -> List[TrendingTopic]:
        """Detect trending topics from various sources"""
        
        if sources is None:
            sources = ['twitter', 'reddit', 'google_trends', 'news_apis']
        
        trending_topics = []
        
        for source in sources:
            try:
                if source == 'twitter':
                    topics = await self._get_twitter_trends()
                elif source == 'reddit':
                    topics = await self._get_reddit_trends()
                elif source == 'google_trends':
                    topics = await self._get_google_trends()
                elif source == 'news_apis':
                    topics = await self._get_news_api_trends()
                else:
                    continue
                
                trending_topics.extend(topics)
            except Exception as e:
                print(f"Error fetching trends from {source}: {e}")
        
        # Deduplicate and rank topics
        return await self._rank_trending_topics(trending_topics)
    
    async def _get_twitter_trends(self) -> List[TrendingTopic]:
        """Get trending topics from Twitter/X"""
        # This would integrate with Twitter API v2
        # For demo purposes, return sample data
        return [
            TrendingTopic(
                topic="Climate Summit 2024",
                relevance_score=0.85,
                source="twitter",
                timestamp=datetime.now(),
                related_keywords=["climate", "summit", "environment", "policy"],
                article_potential=0.9
            )
        ]
    
    async def _get_reddit_trends(self) -> List[TrendingTopic]:
        """Get trending topics from Reddit"""
        # This would integrate with Reddit API
        return []
    
    async def _get_google_trends(self) -> List[TrendingTopic]:
        """Get trending topics from Google Trends"""
        # This would integrate with Google Trends API
        return []
    
    async def _get_news_api_trends(self) -> List[TrendingTopic]:
        """Get trending topics from news APIs"""
        # This would integrate with NewsAPI, Reuters, etc.
        return []
    
    async def _rank_trending_topics(self, topics: List[TrendingTopic]) -> List[TrendingTopic]:
        """Rank and filter trending topics by relevance and article potential"""
        
        # Group similar topics
        topic_groups = {}
        for topic in topics:
            key = topic.topic.lower()
            if key not in topic_groups:
                topic_groups[key] = []
            topic_groups[key].append(topic)
        
        # Select best topic from each group
        ranked_topics = []
        for group in topic_groups.values():
            best_topic = max(group, key=lambda t: t.relevance_score * t.article_potential)
            ranked_topics.append(best_topic)
        
        # Sort by combined score
        ranked_topics.sort(key=lambda t: t.relevance_score * t.article_potential, reverse=True)
        
        return ranked_topics[:20]  # Return top 20 topics
    
    # Automated Content Pipeline
    async def auto_generate_content(self, max_articles: int = 5) -> List[Dict]:
        """Automatically generate articles based on trending topics"""
        
        trending_topics = await self.detect_trending_topics()
        generated_articles = []
        
        for i, topic in enumerate(trending_topics[:max_articles]):
            try:
                # Determine article style based on topic
                style = self._determine_article_style(topic.topic)
                length = "medium" if topic.article_potential > 0.7 else "short"
                
                article = await self.generate_article(
                    topic=topic.topic,
                    style=style,
                    length=length,
                    target_audience="general",
                    ai_provider="openai"
                )
                
                if "error" not in article:
                    article["trending_topic"] = topic.__dict__
                    generated_articles.append(article)
                    
                # Add delay to avoid rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Error generating article for topic '{topic.topic}': {e}")
        
        return generated_articles
    
    def _determine_article_style(self, topic: str) -> str:
        """Determine appropriate article style based on topic"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['breaking', 'urgent', 'crisis', 'emergency']):
            return "professional"
        elif any(word in topic_lower for word in ['analysis', 'study', 'research', 'report']):
            return "academic"
        elif any(word in topic_lower for word in ['opinion', 'debate', 'controversy', 'argue']):
            return "opinion"
        elif any(word in topic_lower for word in ['investigation', 'scandal', 'expose', 'reveal']):
            return "investigative"
        else:
            return "professional"
    
    # Content Optimization
    async def optimize_content(self, content: str, target_metrics: Dict) -> Dict:
        """Optimize content for better performance"""
        
        current_analysis = await self.analyze_content(content)
        optimization_suggestions = []
        
        # Readability optimization
        if current_analysis.readability_score < target_metrics.get('readability', 60):
            optimization_suggestions.append({
                "type": "readability",
                "suggestion": "Consider using shorter sentences and simpler vocabulary to improve readability",
                "priority": "high"
            })
        
        # SEO optimization
        if current_analysis.seo_score < target_metrics.get('seo', 70):
            optimization_suggestions.append({
                "type": "seo",
                "suggestion": "Add more headings, improve content structure, and ensure optimal length",
                "priority": "medium"
            })
        
        # Engagement optimization
        if current_analysis.engagement_prediction < target_metrics.get('engagement', 70):
            optimization_suggestions.append({
                "type": "engagement",
                "suggestion": "Consider adding more compelling hooks, questions, or interactive elements",
                "priority": "high"
            })
        
        # Generate optimized version if needed
        optimized_content = None
        if len(optimization_suggestions) > 0:
            optimized_content = await self._generate_optimized_content(content, optimization_suggestions)
        
        return {
            "current_analysis": current_analysis.__dict__,
            "optimization_suggestions": optimization_suggestions,
            "optimized_content": optimized_content
        }
    
    async def _generate_optimized_content(self, content: str, suggestions: List[Dict]) -> str:
        """Generate an optimized version of the content"""
        
        suggestion_text = "\n".join([f"- {s['suggestion']}" for s in suggestions])
        
        prompt = f"""
        Please optimize the following content based on these suggestions:
        {suggestion_text}
        
        Original content:
        {content}
        
        Return the optimized content maintaining the same core information but improving based on the suggestions.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a content optimization expert specializing in improving readability, SEO, and engagement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error optimizing content: {str(e)}"
    
    # Analytics and Insights
    def track_content_performance(self, article_id: str, metrics: Dict):
        """Track performance metrics for generated content"""
        
        if article_id not in self.analytics_data:
            self.analytics_data[article_id] = {
                "created_at": datetime.now(),
                "metrics_history": []
            }
        
        metrics["timestamp"] = datetime.now()
        self.analytics_data[article_id]["metrics_history"].append(metrics)
    
    def get_performance_insights(self, days: int = 30) -> Dict:
        """Get insights on content performance"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_articles = {
            aid: data for aid, data in self.analytics_data.items()
            if data["created_at"] >= cutoff_date
        }
        
        if not recent_articles:
            return {"message": "No recent articles to analyze"}
        
        # Calculate averages
        total_views = sum(
            max([m.get("views", 0) for m in data["metrics_history"]], default=0)
            for data in recent_articles.values()
        )
        
        total_engagement = sum(
            max([m.get("engagement_rate", 0) for m in data["metrics_history"]], default=0)
            for data in recent_articles.values()
        )
        
        avg_views = total_views / len(recent_articles)
        avg_engagement = total_engagement / len(recent_articles)
        
        # Find top performing articles
        top_articles = sorted(
            recent_articles.items(),
            key=lambda x: max([m.get("views", 0) for m in x[1]["metrics_history"]], default=0),
            reverse=True
        )[:5]
        
        return {
            "period_days": days,
            "total_articles": len(recent_articles),
            "average_views": avg_views,
            "average_engagement_rate": avg_engagement,
            "top_performing_articles": [aid for aid, _ in top_articles],
            "insights": self._generate_performance_insights(recent_articles)
        }
    
    def _generate_performance_insights(self, articles_data: Dict) -> List[str]:
        """Generate actionable insights from performance data"""
        
        insights = []
        
        # Analyze view patterns
        high_view_articles = [
            data for data in articles_data.values()
            if max([m.get("views", 0) for m in data["metrics_history"]], default=0) > 1000
        ]
        
        if len(high_view_articles) > len(articles_data) * 0.3:
            insights.append("Your content is performing well with high view counts")
        else:
            insights.append("Consider optimizing headlines and topics for better visibility")
        
        # Analyze engagement patterns
        high_engagement_articles = [
            data for data in articles_data.values()
            if max([m.get("engagement_rate", 0) for m in data["metrics_history"]], default=0) > 0.05
        ]
        
        if len(high_engagement_articles) > len(articles_data) * 0.4:
            insights.append("Your content generates good reader engagement")
        else:
            insights.append("Focus on creating more interactive and engaging content")
        
        return insights

# Flask API Integration
def create_ai_features_api():
    """Create Flask API for AI features"""
    
    app = Flask(__name__)
    ai_system = AdvancedAIContentSystem()
    
    @app.route('/api/ai/generate-article', methods=['POST'])
    def generate_article():
        data = request.get_json()
        
        topic = data.get('topic', '')
        style = data.get('style', 'professional')
        length = data.get('length', 'medium')
        target_audience = data.get('target_audience', 'general')
        ai_provider = data.get('ai_provider', 'openai')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            article = loop.run_until_complete(
                ai_system.generate_article(topic, style, length, target_audience, ai_provider)
            )
            loop.close()
            
            return jsonify({'success': True, 'data': article})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/analyze-content', methods=['POST'])
    def analyze_content():
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(ai_system.analyze_content(content))
            loop.close()
            
            return jsonify({'success': True, 'data': analysis.__dict__})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/trending-topics', methods=['GET'])
    def get_trending_topics():
        sources = request.args.getlist('sources')
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            topics = loop.run_until_complete(ai_system.detect_trending_topics(sources or None))
            loop.close()
            
            topics_data = [topic.__dict__ for topic in topics]
            return jsonify({'success': True, 'data': topics_data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/auto-generate', methods=['POST'])
    def auto_generate_content():
        data = request.get_json()
        max_articles = data.get('max_articles', 5)
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            articles = loop.run_until_complete(ai_system.auto_generate_content(max_articles))
            loop.close()
            
            return jsonify({'success': True, 'data': articles})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/optimize-content', methods=['POST'])
    def optimize_content():
        data = request.get_json()
        content = data.get('content', '')
        target_metrics = data.get('target_metrics', {})
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            optimization = loop.run_until_complete(ai_system.optimize_content(content, target_metrics))
            loop.close()
            
            return jsonify({'success': True, 'data': optimization})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/performance-insights', methods=['GET'])
    def get_performance_insights():
        days = request.args.get('days', 30, type=int)
        
        try:
            insights = ai_system.get_performance_insights(days)
            return jsonify({'success': True, 'data': insights})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return app

if __name__ == '__main__':
    app = create_ai_features_api()
    app.run(host='0.0.0.0', port=5002, debug=True)

