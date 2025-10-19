import os
import openai
import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

class AIContentGenerator:
    """Service for generating articles using multiple AI providers"""
    
    def __init__(self):
        # Initialize API clients
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        # API endpoints and keys for different providers
        self.providers = {
            'openai': {
                'client': self.openai_client,
                'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                'cost_per_1k_tokens': 0.03
            },
            'claude': {
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'endpoint': 'https://api.anthropic.com/v1/messages',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
                'cost_per_1k_tokens': 0.015
            },
            'deepseek': {
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
                'endpoint': 'https://api.deepseek.com/v1/chat/completions',
                'models': ['deepseek-chat', 'deepseek-coder'],
                'cost_per_1k_tokens': 0.002
            },
            'manus': {
                'api_key': os.getenv('MANUS_API_KEY'),
                'endpoint': os.getenv('MANUS_API_BASE', 'https://api.manus.ai/v1'),
                'models': ['manus-journalist', 'manus-analyst'],
                'cost_per_1k_tokens': 0.01
            }
        }
    
    def generate_article(self, 
                        topic: str, 
                        category: str, 
                        provider: str = 'openai',
                        model: str = None,
                        article_type: str = 'news',
                        keywords: List[str] = None,
                        target_length: int = 800) -> Dict:
        """
        Generate an article on a given topic
        
        Args:
            topic: The main topic/headline for the article
            category: Article category (World Affairs, Business, etc.)
            provider: AI provider to use (openai, claude, deepseek, manus)
            model: Specific model to use (optional)
            article_type: Type of article (news, analysis, opinion)
            keywords: Keywords to include in the article
            target_length: Target word count
            
        Returns:
            Dict with article content and metadata
        """
        try:
            # Select model if not specified
            if not model:
                model = self._get_default_model(provider, article_type)
            
            # Generate the article prompt
            prompt = self._create_article_prompt(
                topic, category, article_type, keywords, target_length
            )
            
            # Generate content based on provider
            if provider == 'openai':
                result = self._generate_with_openai(prompt, model)
            elif provider == 'claude':
                result = self._generate_with_claude(prompt, model)
            elif provider == 'deepseek':
                result = self._generate_with_deepseek(prompt, model)
            elif provider == 'manus':
                result = self._generate_with_manus(prompt, model)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Parse and structure the generated content
            article_data = self._parse_article_content(result['content'])
            
            # Add metadata
            article_data.update({
                'provider': provider,
                'model': model,
                'tokens_used': result.get('tokens_used', 0),
                'generation_cost': result.get('cost', 0.0),
                'prompt_used': prompt,
                'category': category,
                'article_type': article_type,
                'keywords': keywords or [],
                'generated_at': datetime.utcnow().isoformat()
            })
            
            return article_data
            
        except Exception as e:
            return {
                'error': str(e),
                'provider': provider,
                'model': model,
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _get_default_model(self, provider: str, article_type: str) -> str:
        """Get the default model for a provider based on article type"""
        defaults = {
            'openai': {
                'news': 'gpt-4-turbo',
                'analysis': 'gpt-4',
                'opinion': 'gpt-4'
            },
            'claude': {
                'news': 'claude-3-sonnet',
                'analysis': 'claude-3-opus',
                'opinion': 'claude-3-sonnet'
            },
            'deepseek': {
                'news': 'deepseek-chat',
                'analysis': 'deepseek-chat',
                'opinion': 'deepseek-chat'
            },
            'manus': {
                'news': 'manus-journalist',
                'analysis': 'manus-analyst',
                'opinion': 'manus-journalist'
            }
        }
        
        return defaults.get(provider, {}).get(article_type, 
                                           list(self.providers[provider]['models'])[0])
    
    def _create_article_prompt(self, 
                              topic: str, 
                              category: str, 
                              article_type: str,
                              keywords: List[str],
                              target_length: int) -> str:
        """Create a detailed prompt for article generation"""
        
        keyword_text = f"Keywords to naturally incorporate: {', '.join(keywords)}" if keywords else ""
        
        base_prompt = f"""You are a professional journalist writing for a sophisticated news publication similar to The Atlantic, NBC News, or The Guardian. 

Write a {article_type} article about: {topic}

Category: {category}
Target length: {target_length} words
{keyword_text}

Requirements:
1. Write in a professional, engaging journalistic style
2. Use clear, modern prose with varied sentence structure
3. Include proper journalistic structure (headline, subtitle, body paragraphs)
4. Ensure factual accuracy and balanced perspective
5. Use active voice and compelling storytelling
6. Include relevant context and background information
7. End with a thoughtful conclusion

Format your response as JSON with the following structure:
{{
    "title": "Compelling headline (60-80 characters)",
    "subtitle": "Engaging subtitle that expands on the headline",
    "excerpt": "Brief summary for social media and previews (150-200 characters)",
    "content": "Full article content in markdown format",
    "meta_description": "SEO meta description (150-160 characters)",
    "tags": ["tag1", "tag2", "tag3"],
    "featured_image_prompt": "Description for AI image generation",
    "readability_score": 8.5,
    "estimated_read_time": 4
}}

Article Type Guidelines:
"""
        
        if article_type == 'news':
            base_prompt += """
- Focus on recent developments and breaking news
- Use inverted pyramid structure (most important info first)
- Include quotes from relevant sources
- Maintain objectivity and factual reporting
- Answer who, what, when, where, why, and how
"""
        elif article_type == 'analysis':
            base_prompt += """
- Provide deep analysis and expert perspective
- Explore implications and broader context
- Use data and evidence to support arguments
- Consider multiple viewpoints and scenarios
- Offer insights beyond surface-level reporting
"""
        elif article_type == 'opinion':
            base_prompt += """
- Present a clear, well-reasoned argument
- Use personal voice while maintaining professionalism
- Support opinions with facts and evidence
- Acknowledge counterarguments
- Conclude with a strong, memorable statement
"""
        
        return base_prompt
    
    def _generate_with_openai(self, prompt: str, model: str) -> Dict:
        """Generate content using OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional journalist and content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = (tokens_used / 1000) * self.providers['openai']['cost_per_1k_tokens']
            
            return {
                'content': content,
                'tokens_used': tokens_used,
                'cost': cost
            }
            
        except Exception as e:
            raise Exception(f"OpenAI generation failed: {str(e)}")
    
    def _generate_with_claude(self, prompt: str, model: str) -> Dict:
        """Generate content using Anthropic Claude API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.providers['claude']['api_key'],
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': model,
                'max_tokens': 4000,
                'temperature': 0.7,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            response = requests.post(
                self.providers['claude']['endpoint'],
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']
                tokens_used = result['usage']['input_tokens'] + result['usage']['output_tokens']
                cost = (tokens_used / 1000) * self.providers['claude']['cost_per_1k_tokens']
                
                return {
                    'content': content,
                    'tokens_used': tokens_used,
                    'cost': cost
                }
            else:
                raise Exception(f"Claude API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Claude generation failed: {str(e)}")
    
    def _generate_with_deepseek(self, prompt: str, model: str) -> Dict:
        """Generate content using DeepSeek API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.providers["deepseek"]["api_key"]}'
            }
            
            data = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': 'You are a professional journalist and content creator.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 4000
            }
            
            response = requests.post(
                self.providers['deepseek']['endpoint'],
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                tokens_used = result['usage']['total_tokens']
                cost = (tokens_used / 1000) * self.providers['deepseek']['cost_per_1k_tokens']
                
                return {
                    'content': content,
                    'tokens_used': tokens_used,
                    'cost': cost
                }
            else:
                raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"DeepSeek generation failed: {str(e)}")
    
    def _generate_with_manus(self, prompt: str, model: str) -> Dict:
        """Generate content using Manus AI API"""
        try:
            # Use the existing OpenAI client since Manus uses OpenAI-compatible API
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional journalist and content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = (tokens_used / 1000) * self.providers['manus']['cost_per_1k_tokens']
            
            return {
                'content': content,
                'tokens_used': tokens_used,
                'cost': cost
            }
            
        except Exception as e:
            raise Exception(f"Manus generation failed: {str(e)}")
    
    def _parse_article_content(self, content: str) -> Dict:
        """Parse the generated content and extract structured data"""
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{'):
                return json.loads(content)
            
            # If not JSON, try to extract structured content
            article_data = {
                'title': '',
                'subtitle': '',
                'excerpt': '',
                'content': content,
                'meta_description': '',
                'tags': [],
                'featured_image_prompt': '',
                'readability_score': 7.0,
                'estimated_read_time': len(content.split()) // 200  # Rough estimate
            }
            
            # Try to extract title from content
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not article_data['title']:
                    # Remove markdown formatting
                    title = re.sub(r'^#+\s*', '', line)
                    article_data['title'] = title
                    break
            
            # Generate basic metadata
            words = content.split()
            if len(words) > 20:
                article_data['excerpt'] = ' '.join(words[:25]) + '...'
                article_data['meta_description'] = ' '.join(words[:20]) + '...'
            
            return article_data
            
        except json.JSONDecodeError:
            # Fallback for malformed JSON
            return {
                'title': 'Generated Article',
                'subtitle': '',
                'excerpt': content[:200] + '...' if len(content) > 200 else content,
                'content': content,
                'meta_description': content[:150] + '...' if len(content) > 150 else content,
                'tags': [],
                'featured_image_prompt': '',
                'readability_score': 7.0,
                'estimated_read_time': len(content.split()) // 200
            }
    
    def get_available_providers(self) -> List[Dict]:
        """Get list of available AI providers and their capabilities"""
        providers_info = []
        
        for name, config in self.providers.items():
            # Check if API key is available
            api_key_env = f"{name.upper()}_API_KEY"
            if name == 'openai':
                api_key_env = 'OPENAI_API_KEY'
            elif name == 'claude':
                api_key_env = 'ANTHROPIC_API_KEY'
            
            is_available = bool(os.getenv(api_key_env))
            
            providers_info.append({
                'name': name,
                'models': config['models'],
                'cost_per_1k_tokens': config['cost_per_1k_tokens'],
                'is_available': is_available,
                'capabilities': self._get_provider_capabilities(name)
            })
        
        return providers_info
    
    def _get_provider_capabilities(self, provider: str) -> Dict:
        """Get capabilities for each provider"""
        capabilities = {
            'openai': {
                'best_for': ['general_news', 'analysis', 'creative_writing'],
                'strengths': ['versatility', 'coherence', 'factual_accuracy'],
                'max_context': 128000,
                'supports_json': True
            },
            'claude': {
                'best_for': ['long_form_analysis', 'research', 'nuanced_writing'],
                'strengths': ['analytical_depth', 'safety', 'reasoning'],
                'max_context': 200000,
                'supports_json': True
            },
            'deepseek': {
                'best_for': ['cost_effective', 'technical_content', 'coding'],
                'strengths': ['low_cost', 'technical_accuracy', 'efficiency'],
                'max_context': 32000,
                'supports_json': True
            },
            'manus': {
                'best_for': ['journalism', 'news_writing', 'editorial'],
                'strengths': ['journalism_focus', 'editorial_style', 'news_format'],
                'max_context': 128000,
                'supports_json': True
            }
        }
        
        return capabilities.get(provider, {})
    
    def estimate_cost(self, word_count: int, provider: str) -> float:
        """Estimate the cost for generating an article of given length"""
        # Rough estimation: 1 word ≈ 1.3 tokens
        estimated_tokens = int(word_count * 1.3)
        cost_per_1k = self.providers[provider]['cost_per_1k_tokens']
        return (estimated_tokens / 1000) * cost_per_1k

