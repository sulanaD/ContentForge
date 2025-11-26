"""
Research Agent for gathering and synthesizing information from various sources.

This agent can collect information from web sources, PDFs, databases, and APIs,
then structure and summarize the findings for content creation.
"""

import requests
from bs4 import BeautifulSoup
import wikipedia
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
from agents.base_agent import BaseAgent, AgentInput, AgentOutput

class ResearchAgent(BaseAgent):
    """Agent responsible for researching topics and gathering information."""
    
    def setup(self) -> None:
        """Initialize the research agent."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Configure rate limiting and timeouts
        self.request_timeout = self.config.get('request_timeout', 10)
        self.max_sources = self.config.get('max_sources', 5)
        self.wikipedia_limit = self.config.get('wikipedia_limit', 3)
    
    def process(self, input_data: AgentInput) -> AgentOutput:
        """Research the specified topic and gather relevant information."""
        topic = input_data.data.get('topic', '')
        search_queries = input_data.data.get('search_queries', [topic])
        source_types = input_data.data.get('source_types', ['web', 'wikipedia'])
        depth = input_data.data.get('depth', 'moderate')  # shallow, moderate, deep
        
        if not topic:
            return AgentOutput(
                data={},
                agent_name=self.name,
                status="error",
                error_message="No topic provided for research"
            )
        
        research_results = {
            'topic': topic,
            'sources': [],
            'summary': '',
            'key_points': [],
            'statistics': [],
            'quotes': [],
            'references': []
        }
        
        try:
            # Gather information from different sources
            if 'wikipedia' in source_types:
                wiki_results = self._research_wikipedia(topic)
                research_results['sources'].extend(wiki_results)
            
            if 'web' in source_types:
                web_results = self._research_web(search_queries)
                research_results['sources'].extend(web_results)
            
            # Synthesize the collected information
            research_results['summary'] = self._create_summary(research_results['sources'])
            research_results['key_points'] = self._extract_key_points(research_results['sources'])
            research_results['statistics'] = self._extract_statistics(research_results['sources'])
            research_results['quotes'] = self._extract_quotes(research_results['sources'])
            research_results['references'] = self._create_references(research_results['sources'])
            
            # Calculate quality metrics
            quality_score = self._calculate_research_quality(research_results)
            
            return AgentOutput(
                data=research_results,
                metadata={
                    'research_depth': depth,
                    'sources_found': len(research_results['sources']),
                    'source_types_used': source_types,
                    'search_queries': search_queries
                },
                agent_name=self.name,
                status="success",
                quality_score=quality_score
            )
            
        except Exception as e:
            self.logger.error(f"Research failed: {str(e)}")
            return AgentOutput(
                data=research_results,
                agent_name=self.name,
                status="error",
                error_message=f"Research failed: {str(e)}"
            )
    
    def _research_wikipedia(self, topic: str) -> List[Dict[str, Any]]:
        """Research topic using Wikipedia."""
        sources = []
        
        try:
            # Search for relevant Wikipedia pages
            search_results = wikipedia.search(topic, results=self.wikipedia_limit)
            
            for page_title in search_results:
                try:
                    page = wikipedia.page(page_title)
                    
                    source = {
                        'title': page.title,
                        'url': page.url,
                        'content': page.summary,
                        'full_content': page.content[:5000],  # Limit content length
                        'source_type': 'wikipedia',
                        'credibility': 'high',
                        'date_accessed': datetime.now().isoformat(),
                        'word_count': len(page.content.split()),
                        'categories': getattr(page, 'categories', [])[:10]  # Limit categories
                    }
                    
                    sources.append(source)
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    # Try the first option from disambiguation
                    try:
                        page = wikipedia.page(e.options[0])
                        source = {
                            'title': page.title,
                            'url': page.url,
                            'content': page.summary,
                            'full_content': page.content[:5000],
                            'source_type': 'wikipedia',
                            'credibility': 'high',
                            'date_accessed': datetime.now().isoformat(),
                            'word_count': len(page.content.split())
                        }
                        sources.append(source)
                    except:
                        continue
                        
                except wikipedia.exceptions.PageError:
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Wikipedia research failed: {str(e)}")
        
        return sources
    
    def _research_web(self, search_queries: List[str]) -> List[Dict[str, Any]]:
        """Research using web sources (placeholder implementation)."""
        sources = []
        
        # Note: This is a simplified implementation
        # In a production system, you would integrate with search APIs
        # like Google Custom Search, Bing Search API, etc.
        
        for query in search_queries[:3]:  # Limit queries
            try:
                # Example: Mock search results
                # Replace this with actual search API integration
                mock_results = [
                    {
                        'title': f"Article about {query}",
                        'url': f"https://example.com/{query.replace(' ', '-')}",
                        'content': f"This is research content about {query}. " * 10,
                        'source_type': 'web_article',
                        'credibility': 'medium',
                        'date_accessed': datetime.now().isoformat(),
                        'word_count': 100
                    }
                ]
                
                sources.extend(mock_results)
                
            except Exception as e:
                self.logger.warning(f"Web research failed for query '{query}': {str(e)}")
                continue
        
        return sources
    
    def _scrape_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from a web article."""
        try:
            response = self.session.get(url, timeout=self.request_timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('title')
            title = title_elem.text.strip() if title_elem else "Unknown Title"
            
            # Extract main content
            content_selectors = [
                'article', '[role="main"]', '.content', '.post-content',
                '.entry-content', '.article-body', 'main'
            ]
            
            content = ""
            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    content = elem.get_text(strip=True)
                    break
            
            if not content:
                # Fallback to body text
                body = soup.find('body')
                content = body.get_text(strip=True) if body else ""
            
            return {
                'title': title,
                'url': url,
                'content': content[:2000],  # Limit content
                'full_content': content[:10000],
                'source_type': 'web_article',
                'credibility': 'medium',
                'date_accessed': datetime.now().isoformat(),
                'word_count': len(content.split())
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to scrape {url}: {str(e)}")
            return None
    
    def _create_summary(self, sources: List[Dict[str, Any]]) -> str:
        """Create a comprehensive summary from all sources."""
        if not sources:
            return "No sources available for summary."
        
        # Combine key information from all sources
        combined_content = []
        
        for source in sources:
            content = source.get('content', '')
            if content:
                combined_content.append(f"From {source.get('title', 'Unknown Source')}: {content[:500]}")
        
        summary = "Research Summary:\n\n" + "\n\n".join(combined_content)
        return summary[:2000]  # Limit summary length
    
    def _extract_key_points(self, sources: List[Dict[str, Any]]) -> List[str]:
        """Extract key points from research sources."""
        key_points = []
        
        for source in sources:
            content = source.get('full_content', source.get('content', ''))
            
            # Simple extraction based on sentence patterns
            sentences = content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 50 and len(sentence) < 200:
                    # Look for important indicators
                    if any(keyword in sentence.lower() for keyword in 
                          ['important', 'key', 'significant', 'crucial', 'main', 'primary']):
                        key_points.append(sentence + '.')
        
        return list(set(key_points))[:10]  # Remove duplicates and limit
    
    def _extract_statistics(self, sources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract statistics and data points from sources."""
        import re
        statistics = []
        
        for source in sources:
            content = source.get('full_content', source.get('content', ''))
            
            # Look for percentage patterns
            percentages = re.findall(r'\d+(?:\.\d+)?%', content)
            for percentage in percentages[:3]:  # Limit per source
                context_start = max(0, content.find(percentage) - 100)
                context_end = min(len(content), content.find(percentage) + 100)
                context = content[context_start:context_end].strip()
                
                statistics.append({
                    'value': percentage,
                    'context': context,
                    'source': source.get('title', 'Unknown')
                })
            
            # Look for number patterns
            numbers = re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s+(?:million|billion|thousand|users|people|customers)', content, re.IGNORECASE)
            for number in numbers[:2]:  # Limit per source
                context_start = max(0, content.find(number) - 100)
                context_end = min(len(content), content.find(number) + 100)
                context = content[context_start:context_end].strip()
                
                statistics.append({
                    'value': number,
                    'context': context,
                    'source': source.get('title', 'Unknown')
                })
        
        return statistics[:15]  # Limit total statistics
    
    def _extract_quotes(self, sources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract relevant quotes from sources."""
        import re
        quotes = []
        
        for source in sources:
            content = source.get('full_content', source.get('content', ''))
            
            # Look for quoted text
            quoted_texts = re.findall(r'"([^"]{50,300})"', content)
            for quote in quoted_texts[:2]:  # Limit per source
                quotes.append({
                    'quote': f'"{quote}"',
                    'source': source.get('title', 'Unknown'),
                    'url': source.get('url', '')
                })
        
        return quotes[:10]  # Limit total quotes
    
    def _create_references(self, sources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Create properly formatted references."""
        references = []
        
        for i, source in enumerate(sources, 1):
            reference = {
                'id': i,
                'title': source.get('title', 'Unknown Title'),
                'url': source.get('url', ''),
                'source_type': source.get('source_type', 'web'),
                'date_accessed': source.get('date_accessed', ''),
                'credibility': source.get('credibility', 'medium')
            }
            references.append(reference)
        
        return references
    
    def _calculate_research_quality(self, research_results: Dict[str, Any]) -> float:
        """Calculate the quality of research based on various factors."""
        score = 0.0
        
        # Number of sources (0-30 points)
        num_sources = len(research_results['sources'])
        score += min(num_sources * 6, 30)
        
        # Source diversity (0-25 points)
        source_types = set(source.get('source_type', '') for source in research_results['sources'])
        score += len(source_types) * 8
        
        # Content quality (0-25 points)
        total_content_length = sum(len(source.get('content', '')) for source in research_results['sources'])
        if total_content_length > 5000:
            score += 25
        elif total_content_length > 2000:
            score += 20
        else:
            score += 10
        
        # Key information extracted (0-20 points)
        score += len(research_results.get('key_points', [])) * 2
        score += len(research_results.get('statistics', [])) * 1
        score += len(research_results.get('quotes', [])) * 1
        
        return min(score / 100.0, 1.0)
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return [
            "web_research",
            "wikipedia_research", 
            "content_extraction",
            "information_synthesis",
            "key_point_extraction",
            "statistics_extraction",
            "quote_extraction",
            "reference_formatting",
            "source_credibility_assessment"
        ]