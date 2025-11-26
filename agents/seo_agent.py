"""
SEO Agent for optimizing content for search engines.

This agent analyzes content and optimizes it for better search engine visibility
by improving keyword usage, meta descriptions, headers, and overall SEO structure.
"""

import re
import math
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter, defaultdict
from urllib.parse import urlparse
from agents.base_agent import BaseAgent, AgentInput, AgentOutput
import nltk
from textstat import flesch_reading_ease, automated_readability_index

class SEOAgent(BaseAgent):
    """Agent responsible for SEO optimization of content."""
    
    def setup(self) -> None:
        """Initialize the SEO agent."""
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
        
        # SEO configuration
        self.target_keyword_density = self.config.get('target_keyword_density', 1.5)  # 1.5%
        self.min_content_length = self.config.get('min_content_length', 300)
        self.ideal_content_length = self.config.get('ideal_content_length', 1500)
        self.max_title_length = 60
        self.max_meta_description_length = 160
        
        # Stop words for keyword analysis
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'would', 'you', 'your', 'have', 'had',
            'but', 'not', 'or', 'this', 'they', 'we', 'can', 'could', 'should',
            'may', 'might', 'must', 'shall', 'do', 'does', 'did', 'get', 'got'
        }
        
        # Common SEO power words
        self.power_words = {
            'guide', 'complete', 'ultimate', 'best', 'top', 'essential', 'proven',
            'effective', 'powerful', 'secret', 'amazing', 'incredible', 'ultimate',
            'comprehensive', 'detailed', 'step-by-step', 'easy', 'simple', 'quick',
            'fast', 'instant', 'beginner', 'advanced', 'professional', 'expert'
        }
        
        # Header tag hierarchy
        self.header_hierarchy = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        
        # SEO-friendly URL patterns
        self.url_patterns = {
            'spaces': r'[\s_]+',
            'special_chars': r'[^\w\-]',
            'multiple_hyphens': r'-+'
        }
    
    def process(self, input_data: AgentInput) -> AgentOutput:
        """Optimize content for SEO."""
        content = input_data.data.get('content', '')
        title = input_data.data.get('title', '')
        meta_description = input_data.data.get('meta_description', '')
        target_keywords = input_data.data.get('target_keywords', [])
        content_type = input_data.data.get('content_type', 'blog_post')
        focus_keyword = input_data.data.get('focus_keyword', '')
        
        if not content:
            return AgentOutput(
                data={},
                agent_name=self.name,
                status="error",
                error_message="No content provided for SEO optimization"
            )
        
        # Auto-extract keywords if not provided
        if not target_keywords and not focus_keyword:
            extracted_keywords = self._extract_keywords(content, title)
            target_keywords = extracted_keywords[:5]  # Top 5 keywords
            focus_keyword = extracted_keywords[0] if extracted_keywords else ""
        elif not focus_keyword and target_keywords:
            focus_keyword = target_keywords[0]
        
        # Store original content for comparison
        original_content = content
        original_title = title
        original_meta = meta_description
        
        # SEO optimization steps
        seo_recommendations = []
        
        # 1. Optimize title
        optimized_title, title_recommendations = self._optimize_title(title, focus_keyword)
        seo_recommendations.extend(title_recommendations)
        
        # 2. Optimize meta description
        optimized_meta, meta_recommendations = self._optimize_meta_description(
            meta_description, content, focus_keyword
        )
        seo_recommendations.extend(meta_recommendations)
        
        # 3. Optimize content structure
        optimized_content, structure_recommendations = self._optimize_content_structure(
            content, focus_keyword, target_keywords
        )
        seo_recommendations.extend(structure_recommendations)
        
        # 4. Optimize keyword usage
        optimized_content, keyword_recommendations = self._optimize_keyword_usage(
            optimized_content, focus_keyword, target_keywords
        )
        seo_recommendations.extend(keyword_recommendations)
        
        # 5. Improve internal linking opportunities
        linking_suggestions = self._suggest_internal_links(optimized_content, target_keywords)
        
        # 6. Generate SEO-friendly URL slug
        url_slug = self._generate_url_slug(optimized_title or title)
        
        # Calculate SEO scores
        seo_analysis = self._analyze_seo_metrics(
            optimized_content, optimized_title, optimized_meta, focus_keyword, target_keywords
        )
        
        # Generate comprehensive SEO report
        seo_report = self._generate_seo_report(
            original_content, optimized_content, seo_analysis, seo_recommendations
        )
        
        return AgentOutput(
            data={
                'optimized_content': optimized_content,
                'seo_title': optimized_title,
                'seo_meta_description': optimized_meta,
                'focus_keyword': focus_keyword,
                'target_keywords': target_keywords,
                'url_slug': url_slug,
                'seo_score': seo_analysis['overall_score'],
                'seo_analysis': seo_analysis,
                'seo_recommendations': seo_recommendations,
                'internal_linking_suggestions': linking_suggestions,
                'seo_report': seo_report
            },
            metadata={
                'keyword_density': seo_analysis.get('keyword_density', {}),
                'readability_score': seo_analysis.get('readability_score', 0),
                'content_structure_score': seo_analysis.get('structure_score', 0),
                'recommendations_count': len(seo_recommendations)
            },
            agent_name=self.name,
            status="success",
            quality_score=seo_analysis['overall_score'] / 100.0
        )
    
    def _extract_keywords(self, content: str, title: str = "") -> List[str]:
        """Extract potential keywords from content and title."""
        # Combine content and title for keyword extraction
        text = f"{title} {content}".lower()
        
        # Remove punctuation and split into words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        
        # Remove stop words
        filtered_words = [word for word in words if word not in self.stop_words]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Extract phrases (2-3 words)
        phrases = []
        words_list = text.split()
        for i in range(len(words_list) - 1):
            two_word = f"{words_list[i]} {words_list[i+1]}"
            if len(two_word) > 6 and not any(word in self.stop_words for word in words_list[i:i+2]):
                phrases.append(two_word)
        
        for i in range(len(words_list) - 2):
            three_word = f"{words_list[i]} {words_list[i+1]} {words_list[i+2]}"
            if len(three_word) > 10 and not any(word in self.stop_words for word in words_list[i:i+3]):
                phrases.append(three_word)
        
        phrase_counts = Counter(phrases)
        
        # Combine single words and phrases, prioritizing phrases
        all_keywords = []
        
        # Add top phrases
        for phrase, count in phrase_counts.most_common(10):
            if count >= 2:  # Phrase appears at least twice
                all_keywords.append(phrase)
        
        # Add top single words
        for word, count in word_counts.most_common(20):
            if len(word) > 4 and count >= 3:  # Word appears at least 3 times
                all_keywords.append(word)
        
        return all_keywords[:10]  # Return top 10 keywords
    
    def _optimize_title(self, title: str, focus_keyword: str) -> Tuple[str, List[str]]:
        """Optimize title for SEO."""
        recommendations = []
        
        if not title:
            title = f"Complete Guide to {focus_keyword.title()}" if focus_keyword else "Comprehensive Guide"
            recommendations.append("Generated SEO-optimized title")
        
        optimized_title = title
        
        # Check title length
        if len(title) > self.max_title_length:
            # Truncate while preserving focus keyword
            if focus_keyword and focus_keyword.lower() in title.lower():
                # Keep the part with focus keyword
                keyword_pos = title.lower().find(focus_keyword.lower())
                if keyword_pos != -1:
                    start = max(0, keyword_pos - 20)
                    end = min(len(title), keyword_pos + len(focus_keyword) + 20)
                    optimized_title = title[start:end].strip()
                    if start > 0:
                        optimized_title = "..." + optimized_title
                    if end < len(title):
                        optimized_title = optimized_title + "..."
            else:
                optimized_title = title[:self.max_title_length-3] + "..."
            recommendations.append(f"Shortened title to {len(optimized_title)} characters")
        
        # Add focus keyword if missing
        if focus_keyword and focus_keyword.lower() not in optimized_title.lower():
            # Try to naturally incorporate the keyword
            if optimized_title.endswith(('Guide', 'Tips', 'Methods')):
                optimized_title = f"{focus_keyword.title()} {optimized_title}"
            else:
                optimized_title = f"{optimized_title}: {focus_keyword.title()}"
            recommendations.append(f"Added focus keyword '{focus_keyword}' to title")
        
        # Add power words if space allows
        if len(optimized_title) < 50:
            title_words = optimized_title.lower().split()
            missing_power_words = [pw for pw in self.power_words if pw not in title_words]
            if missing_power_words:
                power_word = missing_power_words[0]
                if power_word in ['complete', 'ultimate', 'best']:
                    optimized_title = f"The {power_word.title()} {optimized_title}"
                    recommendations.append(f"Added power word '{power_word}'")
        
        return optimized_title, recommendations
    
    def _optimize_meta_description(self, meta_description: str, content: str, 
                                  focus_keyword: str) -> Tuple[str, List[str]]:
        """Optimize meta description for SEO."""
        recommendations = []
        
        if not meta_description:
            # Generate meta description from content
            sentences = nltk.sent_tokenize(content)
            if sentences:
                # Use first two sentences as base
                base_desc = ' '.join(sentences[:2])
                # Clean and truncate
                meta_description = re.sub(r'[#*`]', '', base_desc)  # Remove markdown
                meta_description = meta_description[:150] + "..."
                recommendations.append("Generated meta description from content")
        
        optimized_meta = meta_description
        
        # Check length
        if len(meta_description) > self.max_meta_description_length:
            optimized_meta = meta_description[:self.max_meta_description_length-3] + "..."
            recommendations.append(f"Shortened meta description to {len(optimized_meta)} characters")
        elif len(meta_description) < 120:
            # Too short, try to expand
            sentences = nltk.sent_tokenize(content)
            if sentences and len(optimized_meta) + len(sentences[0]) < 160:
                optimized_meta += f" {sentences[0]}"
                recommendations.append("Extended meta description for better length")
        
        # Add focus keyword if missing
        if focus_keyword and focus_keyword.lower() not in optimized_meta.lower():
            # Try to naturally incorporate at the beginning
            optimized_meta = f"Learn about {focus_keyword}. {optimized_meta}"
            if len(optimized_meta) > self.max_meta_description_length:
                optimized_meta = optimized_meta[:self.max_meta_description_length-3] + "..."
            recommendations.append(f"Added focus keyword '{focus_keyword}' to meta description")
        
        # Ensure it ends with proper punctuation
        if not optimized_meta.endswith(('.', '!', '?', '...')):
            optimized_meta += '.'
        
        return optimized_meta, recommendations
    
    def _optimize_content_structure(self, content: str, focus_keyword: str, 
                                   target_keywords: List[str]) -> Tuple[str, List[str]]:
        """Optimize content structure for SEO."""
        recommendations = []
        lines = content.split('\n')
        optimized_lines = []
        
        h1_found = False
        h2_count = 0
        
        for line in lines:
            optimized_line = line
            
            # Check for headings
            if line.startswith('#'):
                heading_level = len(line) - len(line.lstrip('#'))
                heading_text = line.lstrip('# ').strip()
                
                # Ensure proper H1 usage
                if heading_level == 1:
                    if h1_found:
                        # Convert additional H1s to H2s
                        optimized_line = f"## {heading_text}"
                        recommendations.append("Converted duplicate H1 to H2")
                    else:
                        h1_found = True
                        # Optimize H1 with focus keyword
                        if focus_keyword and focus_keyword.lower() not in heading_text.lower():
                            optimized_line = f"# {heading_text}: {focus_keyword.title()}"
                            recommendations.append("Added focus keyword to H1")
                
                # Count H2s and optimize with keywords
                elif heading_level == 2:
                    h2_count += 1
                    # Add target keywords to some H2s
                    if target_keywords and h2_count <= len(target_keywords):
                        keyword = target_keywords[h2_count - 1]
                        if keyword.lower() not in heading_text.lower():
                            optimized_line = f"## {keyword.title()}: {heading_text}"
                            recommendations.append(f"Added keyword '{keyword}' to H2")
            
            optimized_lines.append(optimized_line)
        
        # Add H1 if missing
        if not h1_found and focus_keyword:
            h1_line = f"# {focus_keyword.title()}"
            optimized_lines.insert(0, h1_line)
            optimized_lines.insert(1, "")  # Add blank line
            recommendations.append("Added H1 with focus keyword")
        
        # Ensure minimum H2 headings for structure
        if h2_count < 2:
            recommendations.append("Consider adding more H2 headings for better structure")
        
        return '\n'.join(optimized_lines), recommendations
    
    def _optimize_keyword_usage(self, content: str, focus_keyword: str, 
                               target_keywords: List[str]) -> Tuple[str, List[str]]:
        """Optimize keyword density and usage."""
        recommendations = []
        
        if not focus_keyword:
            return content, recommendations
        
        # Calculate current keyword density
        word_count = len(content.split())
        focus_keyword_count = len(re.findall(rf'\b{re.escape(focus_keyword)}\b', content, re.IGNORECASE))
        current_density = (focus_keyword_count / word_count) * 100 if word_count > 0 else 0
        
        optimized_content = content
        
        # Optimize focus keyword density
        target_density = self.target_keyword_density
        target_count = math.ceil((target_density / 100) * word_count)
        
        if current_density < target_density * 0.5:  # Too low
            # Add keyword naturally in a few places
            sentences = nltk.sent_tokenize(optimized_content)
            added_count = 0
            needed_additions = min(target_count - focus_keyword_count, 3)  # Don't over-optimize
            
            for i, sentence in enumerate(sentences):
                if added_count >= needed_additions:
                    break
                
                # Add keyword to sentences that don't have it
                if focus_keyword.lower() not in sentence.lower() and len(sentence.split()) > 10:
                    # Try to add naturally
                    if 'this' in sentence.lower():
                        sentences[i] = sentence.replace('this', f'this {focus_keyword}', 1)
                        added_count += 1
                    elif i == 0:  # First sentence
                        sentences[i] = f"When it comes to {focus_keyword}, {sentence.lower()}"
                        added_count += 1
            
            optimized_content = ' '.join(sentences)
            recommendations.append(f"Improved focus keyword density from {current_density:.1f}% to target {target_density}%")
        
        elif current_density > target_density * 2:  # Too high
            recommendations.append(f"Keyword density ({current_density:.1f}%) may be too high - consider reducing")
        
        # Add semantic keywords (related terms)
        semantic_keywords = self._generate_semantic_keywords(focus_keyword)
        for semantic_kw in semantic_keywords[:2]:  # Add up to 2 semantic keywords
            if semantic_kw.lower() not in optimized_content.lower():
                # Find a good place to add it
                sentences = nltk.sent_tokenize(optimized_content)
                for i, sentence in enumerate(sentences[:3]):  # Try first 3 sentences
                    if focus_keyword.lower() in sentence.lower():
                        # Add semantic keyword near focus keyword
                        sentences[i] = sentence.replace(focus_keyword, f"{focus_keyword} and {semantic_kw}", 1)
                        optimized_content = ' '.join(sentences)
                        recommendations.append(f"Added semantic keyword '{semantic_kw}'")
                        break
        
        return optimized_content, recommendations
    
    def _generate_semantic_keywords(self, focus_keyword: str) -> List[str]:
        """Generate semantic keywords related to the focus keyword."""
        # This is a simplified implementation
        # In a real system, you might use NLP libraries or APIs for better semantic analysis
        
        semantic_map = {
            'ai': ['artificial intelligence', 'machine learning', 'automation'],
            'python': ['programming', 'coding', 'development'],
            'seo': ['search optimization', 'google rankings', 'organic traffic'],
            'marketing': ['advertising', 'promotion', 'branding'],
            'health': ['wellness', 'fitness', 'medical'],
            'business': ['enterprise', 'company', 'organization'],
            'technology': ['tech', 'digital', 'innovation'],
            'education': ['learning', 'training', 'teaching']
        }
        
        focus_lower = focus_keyword.lower()
        for key, values in semantic_map.items():
            if key in focus_lower or focus_lower in key:
                return values
        
        # Generic semantic keywords
        return ['solutions', 'strategies', 'methods']
    
    def _suggest_internal_links(self, content: str, target_keywords: List[str]) -> List[Dict[str, str]]:
        """Suggest internal linking opportunities."""
        suggestions = []
        
        # Look for keyword mentions that could be internal links
        for keyword in target_keywords:
            matches = re.finditer(rf'\b{re.escape(keyword)}\b', content, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(content), match.end() + 50)
                context = content[context_start:context_end]
                
                suggestions.append({
                    'keyword': keyword,
                    'context': context,
                    'suggested_anchor': keyword,
                    'suggested_url': f"/{self._generate_url_slug(keyword)}",
                    'position': match.start()
                })
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _generate_url_slug(self, title: str) -> str:
        """Generate SEO-friendly URL slug."""
        if not title:
            return "article"
        
        slug = title.lower()
        
        # Remove special characters and replace with hyphens
        slug = re.sub(self.url_patterns['spaces'], '-', slug)
        slug = re.sub(self.url_patterns['special_chars'], '', slug)
        slug = re.sub(self.url_patterns['multiple_hyphens'], '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        # Limit length
        if len(slug) > 60:
            words = slug.split('-')
            slug = '-'.join(words[:8])  # Keep first 8 words
        
        return slug or "article"
    
    def _analyze_seo_metrics(self, content: str, title: str, meta_description: str,
                            focus_keyword: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze comprehensive SEO metrics."""
        analysis = {}
        
        # Content analysis
        word_count = len(content.split())
        analysis['word_count'] = word_count
        analysis['content_length_score'] = self._score_content_length(word_count)
        
        # Keyword analysis
        if focus_keyword:
            keyword_count = len(re.findall(rf'\b{re.escape(focus_keyword)}\b', content, re.IGNORECASE))
            keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
            analysis['keyword_density'] = {
                'focus_keyword': focus_keyword,
                'count': keyword_count,
                'density': keyword_density,
                'score': self._score_keyword_density(keyword_density)
            }
        
        # Title analysis
        analysis['title_analysis'] = {
            'length': len(title),
            'score': self._score_title(title, focus_keyword),
            'has_focus_keyword': focus_keyword.lower() in title.lower() if focus_keyword else False
        }
        
        # Meta description analysis
        analysis['meta_analysis'] = {
            'length': len(meta_description),
            'score': self._score_meta_description(meta_description, focus_keyword),
            'has_focus_keyword': focus_keyword.lower() in meta_description.lower() if focus_keyword else False
        }
        
        # Structure analysis
        analysis['structure_score'] = self._score_content_structure(content)
        
        # Readability analysis
        try:
            analysis['readability_score'] = flesch_reading_ease(content)
        except:
            analysis['readability_score'] = 50  # Default
        
        # Calculate overall SEO score
        scores = [
            analysis['content_length_score'],
            analysis.get('keyword_density', {}).get('score', 50),
            analysis['title_analysis']['score'],
            analysis['meta_analysis']['score'],
            analysis['structure_score'],
            min(analysis['readability_score'], 100)  # Cap at 100
        ]
        
        analysis['overall_score'] = sum(scores) / len(scores)
        
        return analysis
    
    def _score_content_length(self, word_count: int) -> float:
        """Score content length (0-100)."""
        if word_count < self.min_content_length:
            return (word_count / self.min_content_length) * 50
        elif word_count >= self.ideal_content_length:
            return 100
        else:
            # Linear scale between min and ideal
            return 50 + ((word_count - self.min_content_length) / 
                        (self.ideal_content_length - self.min_content_length)) * 50
    
    def _score_keyword_density(self, density: float) -> float:
        """Score keyword density (0-100)."""
        target = self.target_keyword_density
        
        if density == 0:
            return 0
        elif target * 0.5 <= density <= target * 2:
            # Optimal range
            return 100 - abs(density - target) * 10
        elif density < target * 0.5:
            # Too low
            return (density / (target * 0.5)) * 50
        else:
            # Too high
            return max(0, 100 - (density - target * 2) * 20)
    
    def _score_title(self, title: str, focus_keyword: str) -> float:
        """Score title SEO quality (0-100)."""
        if not title:
            return 0
        
        score = 0
        
        # Length score (0-30)
        if 30 <= len(title) <= 60:
            score += 30
        elif len(title) < 30:
            score += (len(title) / 30) * 20
        else:
            score += max(0, 30 - (len(title) - 60) * 2)
        
        # Focus keyword score (0-40)
        if focus_keyword and focus_keyword.lower() in title.lower():
            score += 40
            # Bonus for keyword position (earlier is better)
            keyword_pos = title.lower().find(focus_keyword.lower())
            if keyword_pos < len(title) * 0.5:
                score += 10
        
        # Power words score (0-20)
        title_words = title.lower().split()
        power_word_count = sum(1 for word in title_words if word in self.power_words)
        score += min(power_word_count * 10, 20)
        
        # Readability score (0-10)
        if not any(char in title for char in '()[]{}'):
            score += 10
        
        return min(score, 100)
    
    def _score_meta_description(self, meta_desc: str, focus_keyword: str) -> float:
        """Score meta description SEO quality (0-100)."""
        if not meta_desc:
            return 0
        
        score = 0
        
        # Length score (0-40)
        if 120 <= len(meta_desc) <= 160:
            score += 40
        elif len(meta_desc) < 120:
            score += (len(meta_desc) / 120) * 30
        else:
            score += max(0, 40 - (len(meta_desc) - 160) * 2)
        
        # Focus keyword score (0-40)
        if focus_keyword and focus_keyword.lower() in meta_desc.lower():
            score += 40
        
        # Call-to-action score (0-20)
        cta_words = ['learn', 'discover', 'find out', 'get', 'download', 'read']
        if any(cta in meta_desc.lower() for cta in cta_words):
            score += 20
        
        return min(score, 100)
    
    def _score_content_structure(self, content: str) -> float:
        """Score content structure (0-100)."""
        score = 0
        
        # Check for headings
        h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', content, re.MULTILINE))
        
        # H1 score (0-25)
        if h1_count == 1:
            score += 25
        elif h1_count == 0:
            score += 0
        else:
            score += max(0, 25 - (h1_count - 1) * 10)
        
        # H2 score (0-30)
        if 2 <= h2_count <= 6:
            score += 30
        elif h2_count > 0:
            score += min(h2_count * 10, 20)
        
        # H3 score (0-15)
        if h3_count > 0:
            score += min(h3_count * 5, 15)
        
        # Paragraph count (0-20)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            score += 20
        else:
            score += len(paragraphs) * 7
        
        # List usage (0-10)
        if re.search(r'^\s*[-*+]\s', content, re.MULTILINE) or re.search(r'^\s*\d+\.\s', content, re.MULTILINE):
            score += 10
        
        return min(score, 100)
    
    def _generate_seo_report(self, original_content: str, optimized_content: str,
                            seo_analysis: Dict[str, Any], recommendations: List[str]) -> Dict[str, Any]:
        """Generate comprehensive SEO report."""
        return {
            'summary': {
                'overall_seo_score': seo_analysis['overall_score'],
                'total_recommendations': len(recommendations),
                'word_count': seo_analysis['word_count'],
                'content_length_assessment': self._assess_content_length(seo_analysis['word_count'])
            },
            'keyword_analysis': seo_analysis.get('keyword_density', {}),
            'title_analysis': seo_analysis['title_analysis'],
            'meta_description_analysis': seo_analysis['meta_analysis'],
            'content_structure_analysis': {
                'structure_score': seo_analysis['structure_score'],
                'headings_found': self._count_headings(optimized_content),
                'paragraphs_count': len([p for p in optimized_content.split('\n\n') if p.strip()])
            },
            'readability_analysis': {
                'flesch_score': seo_analysis['readability_score'],
                'readability_level': self._get_readability_level(seo_analysis['readability_score'])
            },
            'recommendations': recommendations,
            'next_steps': self._generate_next_steps(seo_analysis)
        }
    
    def _assess_content_length(self, word_count: int) -> str:
        """Assess content length category."""
        if word_count < self.min_content_length:
            return "Too short - consider expanding"
        elif word_count < self.ideal_content_length:
            return "Good length - could be expanded"
        elif word_count < 3000:
            return "Excellent length for SEO"
        else:
            return "Very comprehensive - ensure it stays focused"
    
    def _count_headings(self, content: str) -> Dict[str, int]:
        """Count headings by level."""
        return {
            'h1': len(re.findall(r'^# ', content, re.MULTILINE)),
            'h2': len(re.findall(r'^## ', content, re.MULTILINE)),
            'h3': len(re.findall(r'^### ', content, re.MULTILINE)),
            'h4': len(re.findall(r'^#### ', content, re.MULTILINE))
        }
    
    def _get_readability_level(self, flesch_score: float) -> str:
        """Get readability level description."""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _generate_next_steps(self, seo_analysis: Dict[str, Any]) -> List[str]:
        """Generate next steps for SEO improvement."""
        next_steps = []
        
        if seo_analysis['overall_score'] < 70:
            next_steps.append("Focus on implementing the recommendations to improve overall SEO score")
        
        if seo_analysis.get('keyword_density', {}).get('score', 100) < 60:
            next_steps.append("Optimize keyword usage and density")
        
        if seo_analysis['title_analysis']['score'] < 80:
            next_steps.append("Improve title optimization with focus keyword and power words")
        
        if seo_analysis['structure_score'] < 70:
            next_steps.append("Enhance content structure with proper headings and formatting")
        
        if seo_analysis['readability_score'] < 60:
            next_steps.append("Improve readability by simplifying language and sentence structure")
        
        next_steps.append("Monitor search rankings and adjust strategy based on performance")
        next_steps.append("Consider adding internal links to related content")
        
        return next_steps
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return [
            "keyword_extraction",
            "keyword_density_optimization",
            "title_seo_optimization",
            "meta_description_optimization",
            "content_structure_optimization",
            "url_slug_generation",
            "internal_linking_suggestions",
            "readability_analysis",
            "seo_scoring",
            "comprehensive_seo_reports",
            "semantic_keyword_generation",
            "heading_optimization",
            "content_length_analysis",
            "competitor_keyword_analysis"
        ]