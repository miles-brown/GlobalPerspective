import os
import requests
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import feedparser
from collections import Counter
import time

class TrendMonitor:
    """Service for monitoring social media and news sources for trending topics"""
    
    def __init__(self):
        # API credentials
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
        # Reddit API setup
        self.reddit_access_token = None
        if self.reddit_client_id and self.reddit_client_secret:
            self._get_reddit_token()
        
        # News RSS feeds to monitor
        self.news_feeds = [
            'https://feeds.reuters.com/reuters/topNews',
            'https://feeds.bbci.co.uk/news/world/rss.xml',
            'https://rss.cnn.com/rss/edition.rss',
            'https://feeds.npr.org/1001/rss.xml',
            'https://feeds.washingtonpost.com/rss/world',
            'https://www.theguardian.com/world/rss',
            'https://feeds.nytimes.com/nyt/rss/World',
            'https://feeds.ft.com/rss/world'
        ]
        
        # Subreddits to monitor
        self.subreddits = [
            'worldnews', 'news', 'politics', 'business', 'technology',
            'economics', 'geopolitics', 'finance', 'investing',
            'climate', 'science', 'futurology'
        ]
    
    def _get_reddit_token(self):
        """Get Reddit API access token"""
        try:
            auth = requests.auth.HTTPBasicAuth(self.reddit_client_id, self.reddit_client_secret)
            data = {
                'grant_type': 'client_credentials'
            }
            headers = {'User-Agent': 'NewsBot/1.0'}
            
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                self.reddit_access_token = response.json()['access_token']
            
        except Exception as e:
            print(f"Failed to get Reddit token: {e}")
    
    def monitor_trends(self, keywords: List[str], hours_back: int = 24) -> List[Dict]:
        """
        Monitor all sources for trending topics related to keywords
        
        Args:
            keywords: List of keywords to monitor
            hours_back: How many hours back to look for trends
            
        Returns:
            List of trending topics with metadata
        """
        all_trends = []
        
        # Monitor Twitter/X
        if self.twitter_bearer_token:
            twitter_trends = self._monitor_twitter(keywords, hours_back)
            all_trends.extend(twitter_trends)
        
        # Monitor Reddit
        if self.reddit_access_token:
            reddit_trends = self._monitor_reddit(keywords, hours_back)
            all_trends.extend(reddit_trends)
        
        # Monitor News RSS feeds
        news_trends = self._monitor_news_feeds(keywords, hours_back)
        all_trends.extend(news_trends)
        
        # Monitor Google Trends (if API available)
        google_trends = self._monitor_google_trends(keywords)
        all_trends.extend(google_trends)
        
        # Analyze and score trends
        scored_trends = self._analyze_trends(all_trends, keywords)
        
        return scored_trends
    
    def _monitor_twitter(self, keywords: List[str], hours_back: int) -> List[Dict]:
        """Monitor Twitter/X for trending topics"""
        trends = []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.twitter_bearer_token}',
                'Content-Type': 'application/json'
            }
            
            # Search for each keyword
            for keyword in keywords:
                # Twitter API v2 search
                params = {
                    'query': f'{keyword} -is:retweet lang:en',
                    'tweet.fields': 'created_at,public_metrics,context_annotations',
                    'max_results': 100,
                    'start_time': (datetime.utcnow() - timedelta(hours=hours_back)).isoformat() + 'Z'
                }
                
                response = requests.get(
                    'https://api.twitter.com/2/tweets/search/recent',
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data:
                        for tweet in data['data']:
                            trends.append({
                                'topic': tweet['text'][:200],
                                'source': 'twitter',
                                'engagement_score': (
                                    tweet['public_metrics']['like_count'] +
                                    tweet['public_metrics']['retweet_count'] +
                                    tweet['public_metrics']['reply_count']
                                ),
                                'created_at': tweet['created_at'],
                                'matched_keyword': keyword,
                                'url': f"https://twitter.com/i/web/status/{tweet['id']}"
                            })
                
                # Rate limiting
                time.sleep(1)
        
        except Exception as e:
            print(f"Twitter monitoring error: {e}")
        
        return trends
    
    def _monitor_reddit(self, keywords: List[str], hours_back: int) -> List[Dict]:
        """Monitor Reddit for trending topics"""
        trends = []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.reddit_access_token}',
                'User-Agent': 'NewsBot/1.0'
            }
            
            for subreddit in self.subreddits:
                # Get hot posts from subreddit
                response = requests.get(
                    f'https://oauth.reddit.com/r/{subreddit}/hot',
                    headers=headers,
                    params={'limit': 50}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for post in data['data']['children']:
                        post_data = post['data']
                        post_time = datetime.fromtimestamp(post_data['created_utc'])
                        
                        # Check if post is within time range
                        if post_time > datetime.utcnow() - timedelta(hours=hours_back):
                            # Check if any keywords match
                            title_text = (post_data['title'] + ' ' + post_data.get('selftext', '')).lower()
                            
                            for keyword in keywords:
                                if keyword.lower() in title_text:
                                    trends.append({
                                        'topic': post_data['title'],
                                        'source': f'reddit_r_{subreddit}',
                                        'engagement_score': post_data['score'] + post_data['num_comments'],
                                        'created_at': post_time.isoformat(),
                                        'matched_keyword': keyword,
                                        'url': f"https://reddit.com{post_data['permalink']}"
                                    })
                                    break
                
                # Rate limiting
                time.sleep(1)
        
        except Exception as e:
            print(f"Reddit monitoring error: {e}")
        
        return trends
    
    def _monitor_news_feeds(self, keywords: List[str], hours_back: int) -> List[Dict]:
        """Monitor RSS news feeds for trending topics"""
        trends = []
        
        for feed_url in self.news_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    # Parse publication date
                    if hasattr(entry, 'published_parsed'):
                        pub_time = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed'):
                        pub_time = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_time = datetime.utcnow()
                    
                    # Check if article is within time range
                    if pub_time > datetime.utcnow() - timedelta(hours=hours_back):
                        # Check if any keywords match
                        content = (entry.title + ' ' + entry.get('summary', '')).lower()
                        
                        for keyword in keywords:
                            if keyword.lower() in content:
                                trends.append({
                                    'topic': entry.title,
                                    'source': f'news_rss_{feed.feed.get("title", "unknown")}',
                                    'engagement_score': 1,  # RSS doesn't provide engagement metrics
                                    'created_at': pub_time.isoformat(),
                                    'matched_keyword': keyword,
                                    'url': entry.link,
                                    'summary': entry.get('summary', '')[:300]
                                })
                                break
            
            except Exception as e:
                print(f"RSS feed error for {feed_url}: {e}")
        
        return trends
    
    def _monitor_google_trends(self, keywords: List[str]) -> List[Dict]:
        """Monitor Google Trends for keyword popularity"""
        trends = []
        
        try:
            # Note: This would require pytrends library and proper setup
            # For now, we'll use a placeholder implementation
            
            # from pytrends.request import TrendReq
            # pytrends = TrendReq(hl='en-US', tz=360)
            
            for keyword in keywords:
                # Placeholder trend data
                trends.append({
                    'topic': f'Google Trends: {keyword}',
                    'source': 'google_trends',
                    'engagement_score': 50,  # Placeholder
                    'created_at': datetime.utcnow().isoformat(),
                    'matched_keyword': keyword,
                    'trend_velocity': 1.2  # Placeholder
                })
        
        except Exception as e:
            print(f"Google Trends error: {e}")
        
        return trends
    
    def _analyze_trends(self, trends: List[Dict], keywords: List[str]) -> List[Dict]:
        """Analyze and score trending topics"""
        if not trends:
            return []
        
        # Group similar topics
        grouped_trends = self._group_similar_topics(trends)
        
        # Score each trend group
        scored_trends = []
        for group in grouped_trends:
            score = self._calculate_trend_score(group)
            
            # Create consolidated trend entry
            consolidated_trend = {
                'topic': group[0]['topic'],  # Use first topic as representative
                'sources': list(set([t['source'] for t in group])),
                'total_engagement': sum([t['engagement_score'] for t in group]),
                'mention_count': len(group),
                'matched_keywords': list(set([t['matched_keyword'] for t in group])),
                'trend_score': score,
                'first_seen': min([t['created_at'] for t in group]),
                'last_seen': max([t['created_at'] for t in group]),
                'urls': [t.get('url') for t in group if t.get('url')],
                'sentiment_score': self._analyze_sentiment(group),
                'geographic_region': 'global',  # Placeholder
                'trend_velocity': self._calculate_velocity(group)
            }
            
            scored_trends.append(consolidated_trend)
        
        # Sort by trend score
        scored_trends.sort(key=lambda x: x['trend_score'], reverse=True)
        
        return scored_trends
    
    def _group_similar_topics(self, trends: List[Dict]) -> List[List[Dict]]:
        """Group similar topics together"""
        groups = []
        used_indices = set()
        
        for i, trend in enumerate(trends):
            if i in used_indices:
                continue
            
            group = [trend]
            used_indices.add(i)
            
            # Find similar trends
            for j, other_trend in enumerate(trends[i+1:], i+1):
                if j in used_indices:
                    continue
                
                if self._are_topics_similar(trend['topic'], other_trend['topic']):
                    group.append(other_trend)
                    used_indices.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_topics_similar(self, topic1: str, topic2: str, threshold: float = 0.6) -> bool:
        """Check if two topics are similar using simple word overlap"""
        words1 = set(re.findall(r'\w+', topic1.lower()))
        words2 = set(re.findall(r'\w+', topic2.lower()))
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold
    
    def _calculate_trend_score(self, trend_group: List[Dict]) -> float:
        """Calculate a trend score based on various factors"""
        # Base score from engagement
        engagement_score = sum([t['engagement_score'] for t in trend_group])
        
        # Bonus for multiple sources
        source_bonus = len(set([t['source'] for t in trend_group])) * 10
        
        # Bonus for recency
        latest_time = max([datetime.fromisoformat(t['created_at'].replace('Z', '+00:00')) 
                          for t in trend_group])
        hours_ago = (datetime.utcnow().replace(tzinfo=latest_time.tzinfo) - latest_time).total_seconds() / 3600
        recency_bonus = max(0, 24 - hours_ago) * 2
        
        # Bonus for mention frequency
        frequency_bonus = len(trend_group) * 5
        
        total_score = engagement_score + source_bonus + recency_bonus + frequency_bonus
        
        return round(total_score, 2)
    
    def _analyze_sentiment(self, trend_group: List[Dict]) -> float:
        """Analyze sentiment of trend group (placeholder implementation)"""
        # This would typically use a sentiment analysis library
        # For now, return a neutral score
        return 0.0
    
    def _calculate_velocity(self, trend_group: List[Dict]) -> float:
        """Calculate how fast a trend is growing"""
        if len(trend_group) < 2:
            return 1.0
        
        # Sort by time
        sorted_trends = sorted(trend_group, 
                             key=lambda x: datetime.fromisoformat(x['created_at'].replace('Z', '+00:00')))
        
        # Calculate mentions over time
        time_span = (datetime.fromisoformat(sorted_trends[-1]['created_at'].replace('Z', '+00:00')) - 
                    datetime.fromisoformat(sorted_trends[0]['created_at'].replace('Z', '+00:00'))).total_seconds()
        
        if time_span == 0:
            return 1.0
        
        # Velocity = mentions per hour
        velocity = len(trend_group) / (time_span / 3600)
        
        return round(velocity, 2)
    
    def get_trending_keywords(self, text_samples: List[str], min_frequency: int = 3) -> List[Tuple[str, int]]:
        """Extract trending keywords from text samples"""
        # Combine all text
        combined_text = ' '.join(text_samples).lower()
        
        # Extract words (simple tokenization)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text)
        
        # Filter out common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
            'those', 'his', 'her', 'its', 'their', 'what', 'which', 'who', 'when',
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'only', 'own', 'same', 'than', 'too',
            'very', 'can', 'will', 'just', 'should', 'now', 'said', 'says', 'new'
        }
        
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count frequency
        word_counts = Counter(filtered_words)
        
        # Return words that appear at least min_frequency times
        trending = [(word, count) for word, count in word_counts.most_common() 
                   if count >= min_frequency]
        
        return trending
    
    def check_keyword_relevance(self, topic: str, keywords: List[str]) -> Dict:
        """Check how relevant a topic is to monitoring keywords"""
        topic_lower = topic.lower()
        matches = []
        
        for keyword in keywords:
            if keyword.lower() in topic_lower:
                matches.append(keyword)
        
        relevance_score = len(matches) / len(keywords) if keywords else 0
        
        return {
            'is_relevant': len(matches) > 0,
            'matched_keywords': matches,
            'relevance_score': relevance_score,
            'keyword_count': len(matches)
        }

