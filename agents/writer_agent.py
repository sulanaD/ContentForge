"""
Writer Agent for generating structured content from research data.

This agent takes research output and creates well-structured, engaging content
with proper flow, headings, and formatting in Markdown.

Supports LLM integration for AI-powered content generation.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from utils.llm_integration import get_llm_manager

class WriterAgent(BaseAgent):
    """Agent responsible for generating structured content."""
    
    def setup(self) -> None:
        """Initialize the writer agent."""
        # Initialize LLM Manager
        self.llm_manager = get_llm_manager()
        self.use_llm = self._check_llm_availability()
        
        if self.use_llm:
            self.logger.info(f"LLM available: {self.llm_manager.get_available_providers()}")
        else:
            self.logger.info("No LLM available, using template-based generation")
        
        # Content structure templates
        self.content_templates = {
            'blog_post': {
                'sections': ['introduction', 'main_content', 'conclusion'],
                'min_words': 800,
                'max_words': 2500,
                'tone': 'informative_engaging'
            },
            'article': {
                'sections': ['abstract', 'introduction', 'body', 'conclusion', 'references'],
                'min_words': 1200,
                'max_words': 3500,
                'tone': 'professional'
            },
            'social_post': {
                'sections': ['hook', 'content', 'call_to_action'],
                'min_words': 50,
                'max_words': 300,
                'tone': 'casual_engaging'
            },
            'guide': {
                'sections': ['overview', 'steps', 'tips', 'conclusion'],
                'min_words': 1000,
                'max_words': 4000,
                'tone': 'instructional'
            }
        }
        
        # Writing style configurations
        self.writing_styles = {
            'informative_engaging': {
                'paragraph_length': 'medium',
                'use_questions': True,
                'use_examples': True,
                'personal_pronouns': 'moderate'
            },
            'professional': {
                'paragraph_length': 'long',
                'use_questions': False,
                'use_examples': True,
                'personal_pronouns': 'minimal'
            },
            'casual_engaging': {
                'paragraph_length': 'short',
                'use_questions': True,
                'use_examples': True,
                'personal_pronouns': 'frequent'
            },
            'instructional': {
                'paragraph_length': 'medium',
                'use_questions': True,
                'use_examples': True,
                'personal_pronouns': 'direct'
            }
        }
    
    def _check_llm_availability(self) -> bool:
        """Check if any LLM provider (other than template) is available."""
        providers = self.llm_manager.get_available_providers()
        real_providers = [p for p in providers if p != 'template']
        return len(real_providers) > 0
    
    def process(self, input_data: AgentInput) -> AgentOutput:
        """Generate structured content from research data."""
        research_data = input_data.data.get('research_data', {})
        content_type = input_data.data.get('content_type', 'blog_post')
        target_audience = input_data.data.get('target_audience', 'general')
        tone = input_data.data.get('tone', 'informative_engaging')
        word_count_target = input_data.data.get('word_count', None)
        
        # Get QA feedback if this is a regeneration
        qa_feedback = input_data.data.get('qa_feedback', None)
        
        if not research_data:
            return AgentOutput(
                data={},
                agent_name=self.name,
                status="error",
                error_message="No research data provided for content generation"
            )
        
        try:
            # Get content template
            template = self.content_templates.get(content_type, self.content_templates['blog_post'])
            style = self.writing_styles.get(tone, self.writing_styles['informative_engaging'])
            
            # Generate content structure
            content_structure = self._plan_content_structure(research_data, template, target_audience)
            
            # Set target word count
            if word_count_target:
                target_words = word_count_target
            else:
                target_words = template.get('min_words', 800)
            
            # Generate the actual content
            if self.use_llm:
                # Use LLM for high-quality content generation
                generated_content = self._generate_content_with_llm(
                    research_data, content_structure, style, template, 
                    target_words, qa_feedback
                )
                title = self._generate_title_with_llm(research_data, content_type)
            else:
                # Use template-based generation
                generated_content = self._generate_content(
                    research_data, content_structure, style, template, 
                    target_words
                )
                title = self._generate_title(research_data, content_type)
            
            # Generate meta description
            meta_description = self._generate_meta_description(generated_content, content_type)
            
            # Calculate content metrics
            metrics = self._calculate_content_metrics(generated_content)
            
            return AgentOutput(
                data={
                    'title': title,
                    'content': generated_content,
                    'meta_description': meta_description,
                    'content_type': content_type,
                    'structure': content_structure,
                    'metrics': metrics,
                    'target_audience': target_audience,
                    'tone': tone
                },
                metadata={
                    'word_count': metrics['word_count'],
                    'reading_time': metrics['reading_time'],
                    'sections_count': len(content_structure['sections']),
                    'template_used': content_type,
                    'style_applied': tone,
                    'llm_used': self.use_llm
                },
                agent_name=self.name,
                status="success",
                quality_score=self._calculate_content_quality(generated_content, template)
            )
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {str(e)}")
            return AgentOutput(
                data={},
                agent_name=self.name,
                status="error",
                error_message=f"Content generation failed: {str(e)}"
            )
    
    def _plan_content_structure(self, research_data: Dict[str, Any], template: Dict[str, Any], 
                              target_audience: str) -> Dict[str, Any]:
        """Plan the structure of the content based on research data."""
        topic = research_data.get('topic', 'Unknown Topic')
        key_points = research_data.get('key_points', [])
        sources = research_data.get('sources', [])
        
        # Create section outline
        sections = []
        
        if 'introduction' in template['sections']:
            sections.append({
                'type': 'introduction',
                'title': 'Introduction',
                'content_plan': 'Hook + context + overview of what will be covered',
                'key_points': key_points[:2] if key_points else [],
                'estimated_words': 150
            })
        
        if 'main_content' in template['sections'] or 'body' in template['sections']:
            # Organize main content into logical subsections
            main_sections = self._organize_main_content(key_points, research_data)
            sections.extend(main_sections)
        
        if 'conclusion' in template['sections']:
            sections.append({
                'type': 'conclusion',
                'title': 'Conclusion',
                'content_plan': 'Summary + key takeaways + call to action',
                'key_points': [],
                'estimated_words': 100
            })
        
        # Add other specific sections based on content type
        if 'abstract' in template['sections']:
            sections.insert(0, {
                'type': 'abstract',
                'title': 'Abstract',
                'content_plan': 'Brief summary of the entire content',
                'estimated_words': 100
            })
        
        if 'references' in template['sections']:
            sections.append({
                'type': 'references',
                'title': 'References',
                'content_plan': 'List of sources and citations',
                'references': research_data.get('references', [])
            })
        
        return {
            'topic': topic,
            'sections': sections,
            'total_estimated_words': sum(s.get('estimated_words', 0) for s in sections),
            'target_audience': target_audience
        }
    
    def _organize_main_content(self, key_points: List[str], research_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Organize main content into logical subsections."""
        sections = []
        
        # Group key points into themes
        if len(key_points) > 5:
            # For longer content, create multiple sections
            points_per_section = 3
            for i in range(0, len(key_points), points_per_section):
                section_points = key_points[i:i + points_per_section]
                section_title = self._generate_section_title(section_points, i // points_per_section + 1)
                
                sections.append({
                    'type': 'main_section',
                    'title': section_title,
                    'content_plan': f'Detailed discussion of {len(section_points)} related points',
                    'key_points': section_points,
                    'estimated_words': 300,
                    'statistics': [stat for stat in research_data.get('statistics', [])[:2]],
                    'quotes': [quote for quote in research_data.get('quotes', [])[:1]]
                })
        else:
            # For shorter content, create fewer sections
            sections.append({
                'type': 'main_section',
                'title': 'Key Insights',
                'content_plan': 'Main discussion covering all key points',
                'key_points': key_points,
                'estimated_words': 500,
                'statistics': research_data.get('statistics', [])[:3],
                'quotes': research_data.get('quotes', [])[:2]
            })
        
        return sections
    
    def _generate_section_title(self, key_points: List[str], section_number: int) -> str:
        """Generate an appropriate title for a content section."""
        # Extract themes from key points
        common_themes = {
            'benefit': ['Benefits', 'Advantages', 'Positive Impact'],
            'challenge': ['Challenges', 'Obstacles', 'Considerations'],
            'method': ['Methods', 'Approaches', 'Strategies'],
            'trend': ['Trends', 'Developments', 'Evolution'],
            'impact': ['Impact', 'Effects', 'Consequences']
        }
        
        # Simple theme detection
        points_text = ' '.join(key_points).lower()
        
        for theme, titles in common_themes.items():
            if theme in points_text:
                return titles[section_number % len(titles)]
        
        # Fallback titles
        fallback_titles = [
            'Understanding the Basics',
            'Key Considerations',
            'Important Factors',
            'Critical Elements',
            'Essential Information'
        ]
        
        return fallback_titles[section_number % len(fallback_titles)]
    
    def _generate_content_with_llm(self, research_data: Dict[str, Any], structure: Dict[str, Any],
                                   style: Dict[str, Any], template: Dict[str, Any],
                                   target_words: int, qa_feedback: Optional[Dict] = None) -> str:
        """Generate content using LLM API."""
        topic = research_data.get('topic', 'Unknown Topic')
        key_points = research_data.get('key_points', [])
        summary = research_data.get('summary', '')
        
        # Build the prompt
        prompt = f"""Write a comprehensive {template.get('tone', 'professional')} article about "{topic}".

TARGET LENGTH: {target_words} words (this is CRITICAL - must be at least {int(target_words * 0.8)} words)

RESEARCH SUMMARY:
{summary}

KEY POINTS TO COVER:
{chr(10).join(f'- {point}' for point in key_points[:8])}

CONTENT STRUCTURE:
{chr(10).join(f'- {section["title"]}: {section.get("content_plan", "")}' for section in structure['sections'])}

WRITING STYLE:
- Paragraph length: {style.get('paragraph_length', 'medium')}
- Use rhetorical questions: {style.get('use_questions', True)}
- Include examples: {style.get('use_examples', True)}
- Tone: {template.get('tone', 'professional')}

FORMAT:
- Use Markdown formatting
- Include a compelling title as an H1 heading
- Use H2 for main sections and H3 for subsections
- Include bullet points where appropriate
- Add a clear call to action at the end
"""
        
        # Add QA feedback if regenerating
        if qa_feedback:
            prompt += f"""

IMPORTANT - PREVIOUS ATTEMPT FEEDBACK:
The previous content had issues that need to be fixed:
- Previous score: {qa_feedback.get('previous_score', 'N/A')}%
- Areas needing improvement: {', '.join(qa_feedback.get('improvement_areas', []))}
- Recommendations: {', '.join(qa_feedback.get('recommendations', [])[:3])}

Please address these issues in this version.
"""
        
        try:
            content = self.llm_manager.generate(
                prompt,
                max_tokens=max(2000, target_words * 2),
                temperature=0.7
            )
            return content
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}, falling back to template")
            return self._generate_content(research_data, structure, style, template, target_words)
    
    def _generate_title_with_llm(self, research_data: Dict[str, Any], content_type: str) -> str:
        """Generate a compelling title using LLM."""
        topic = research_data.get('topic', 'Unknown Topic')
        
        prompt = f"""Generate a compelling, SEO-friendly title for a {content_type} about "{topic}".
        
Requirements:
- Maximum 70 characters
- Engaging and click-worthy
- Clear and descriptive
- No clickbait

Return ONLY the title, nothing else."""
        
        try:
            title = self.llm_manager.generate(prompt, max_tokens=50, temperature=0.8)
            # Clean up the title
            title = title.strip().strip('"').strip("'")
            return title
        except Exception as e:
            self.logger.error(f"LLM title generation failed: {e}")
            return self._generate_title(research_data, content_type)
    
    def _generate_content(self, research_data: Dict[str, Any], structure: Dict[str, Any], 
                         style: Dict[str, Any], template: Dict[str, Any],
                         target_words: int = 800) -> str:
        """Generate the actual content based on structure and style (template-based)."""
        content_parts = []
        
        # Calculate words per section based on target
        num_sections = len(structure['sections'])
        words_per_section = max(100, target_words // max(1, num_sections))
        
        for section in structure['sections']:
            section['target_words'] = words_per_section
            section_content = self._generate_section_content(section, research_data, style)
            content_parts.append(section_content)
        
        return '\n\n'.join(content_parts)
    
    def _generate_section_content(self, section: Dict[str, Any], research_data: Dict[str, Any], 
                                 style: Dict[str, Any]) -> str:
        """Generate content for a specific section."""
        section_type = section['type']
        title = section['title']
        key_points = section.get('key_points', [])
        
        # Generate section header
        if section_type == 'abstract':
            header = f"## {title}\n\n"
        elif section_type in ['introduction', 'conclusion']:
            header = f"## {title}\n\n"
        else:
            header = f"### {title}\n\n"
        
        # Generate section content based on type
        if section_type == 'introduction':
            content = self._generate_introduction(research_data, key_points, style)
        elif section_type == 'main_section':
            content = self._generate_main_section(section, research_data, style)
        elif section_type == 'conclusion':
            content = self._generate_conclusion(research_data, style)
        elif section_type == 'abstract':
            content = self._generate_abstract(research_data)
        elif section_type == 'references':
            content = self._generate_references(section.get('references', []))
        else:
            content = self._generate_generic_section(section, research_data, style)
        
        return header + content
    
    def _generate_introduction(self, research_data: Dict[str, Any], key_points: List[str], 
                              style: Dict[str, Any]) -> str:
        """Generate an engaging introduction."""
        topic = research_data.get('topic', 'this topic')
        
        # Create hook
        hook_options = [
            f"In today's rapidly evolving world, {topic} has become increasingly important.",
            f"Have you ever wondered about the impact of {topic}?",
            f"Understanding {topic} is crucial for anyone looking to stay ahead of the curve.",
            f"The landscape of {topic} is changing faster than ever before."
        ]
        
        hook = hook_options[0]  # Could be randomized
        
        # Add context
        context = f"This comprehensive guide explores the key aspects of {topic}, providing insights based on the latest research and expert analysis."
        
        # Preview what's covered
        if key_points:
            preview = f"We'll examine {', '.join([point[:50] + '...' if len(point) > 50 else point for point in key_points[:2]])}."
        else:
            preview = f"We'll dive deep into the essential elements that make {topic} such a compelling subject."
        
        return f"{hook}\n\n{context}\n\n{preview}"
    
    def _generate_main_section(self, section: Dict[str, Any], research_data: Dict[str, Any], 
                              style: Dict[str, Any]) -> str:
        """Generate main content section with target word count."""
        key_points = section.get('key_points', [])
        statistics = section.get('statistics', [])
        quotes = section.get('quotes', [])
        target_words = section.get('target_words', 200)
        
        content_parts = []
        current_words = 0
        
        # Introduce the section topic
        topic = research_data.get('topic', 'this topic')
        intro = f"Let's explore the key aspects related to {topic} and understand why they matter."
        content_parts.append(intro)
        current_words += len(intro.split())
        
        # Expand on key points with more detail
        for i, point in enumerate(key_points):
            if current_words >= target_words * 0.9:
                break
                
            expanded_point = self._expand_key_point_detailed(
                point, research_data, style, 
                min_words=max(50, (target_words - current_words) // max(1, len(key_points) - i))
            )
            content_parts.append(expanded_point)
            current_words += len(expanded_point.split())
            
            # Add supporting information
            if i < len(statistics) and statistics[i]:
                stat_context = statistics[i].get('context', '')
                if stat_context:
                    stat_text = f"According to recent data, {stat_context}. This data point underscores the significance of understanding these dynamics and their broader implications for practitioners and stakeholders alike."
                    content_parts.append(stat_text)
                    current_words += len(stat_text.split())
        
        # Add relevant quotes
        for quote in quotes[:1]:  # Limit quotes per section
            quote_text = f"\n> {quote.get('quote', '')}\n"
            if quote.get('source'):
                quote_text += f"*— {quote['source']}*\n"
            content_parts.append(quote_text)
            current_words += len(quote_text.split())
        
        # If we still need more words, add additional context
        while current_words < target_words * 0.8:
            filler = self._generate_contextual_paragraph(topic, target_words - current_words)
            content_parts.append(filler)
            current_words += len(filler.split())
        
        return '\n\n'.join(content_parts)
    
    def _expand_key_point_detailed(self, point: str, research_data: Dict[str, Any], 
                                   style: Dict[str, Any], min_words: int = 50) -> str:
        """Expand a key point into a detailed paragraph meeting word requirements."""
        topic = research_data.get('topic', 'this topic')
        point = point.rstrip('.')
        
        # Build a comprehensive paragraph
        paragraphs = []
        
        # Main point
        main = f"{point}. This aspect of {topic} deserves particular attention due to its significance in the broader context."
        paragraphs.append(main)
        
        # Elaboration
        if style.get('use_examples', True):
            elaboration = f"To illustrate this point, consider how organizations and individuals are adapting their approaches to address these considerations. The practical applications extend across multiple domains, demonstrating the versatility and importance of understanding these dynamics."
            paragraphs.append(elaboration)
        
        # Analysis
        analysis = f"When we examine the underlying factors, it becomes clear that {point.lower()} represents a critical element that cannot be overlooked. Industry experts and researchers have highlighted this aspect as a key driver of success and progress in the field."
        paragraphs.append(analysis)
        
        # Additional context if needed
        if style.get('use_questions', False):
            questions = "What does this mean for those seeking to leverage these insights? The evidence suggests that proactive engagement with these concepts leads to better outcomes and more informed decision-making."
            paragraphs.append(questions)
        
        result = ' '.join(paragraphs)
        
        # If still short, add more detail
        while len(result.split()) < min_words:
            result += f" Furthermore, the implications of {point.lower()} extend beyond immediate applications, influencing long-term strategies and planning."
        
        return result
    
    def _generate_contextual_paragraph(self, topic: str, target_words: int) -> str:
        """Generate additional contextual content to meet word requirements."""
        paragraphs = [
            f"The landscape surrounding {topic} continues to evolve at a rapid pace. Staying informed about these developments is essential for anyone seeking to maintain a competitive edge and make well-informed decisions.",
            f"Research in this area has revealed numerous insights that challenge conventional thinking and open new avenues for exploration. The interdisciplinary nature of {topic} means that developments in related fields often have significant implications.",
            f"Industry leaders and thought leaders have emphasized the transformative potential of {topic}. Their perspectives provide valuable guidance for navigating the complexities and capitalizing on emerging opportunities.",
            f"As we look to the future, the trajectory of {topic} appears increasingly significant. Understanding current trends and anticipating future developments will be crucial for success in this dynamic environment.",
            f"The practical applications of knowledge in this area extend across diverse sectors and contexts. From individual practitioners to large organizations, the relevance of {topic} touches virtually every aspect of modern life.",
        ]
        
        result = []
        current_words = 0
        idx = 0
        
        while current_words < target_words and idx < len(paragraphs) * 2:
            para = paragraphs[idx % len(paragraphs)]
            result.append(para)
            current_words += len(para.split())
            idx += 1
        
        return '\n\n'.join(result)
    
    def _generate_conclusion(self, research_data: Dict[str, Any], style: Dict[str, Any]) -> str:
        """Generate a compelling conclusion."""
        topic = research_data.get('topic', 'this topic')
        
        # Summary
        summary = f"As we've explored throughout this analysis, {topic} presents both opportunities and challenges that require careful consideration."
        
        # Key takeaways
        takeaways = "The key takeaways from our research highlight the importance of staying informed and adapting to changing circumstances."
        
        # Call to action
        cta_options = [
            "Stay updated on the latest developments and continue learning about this evolving field.",
            "Consider how these insights might apply to your own situation or organization.",
            "What aspects of this topic interest you most? Continue exploring to deepen your understanding."
        ]
        
        cta = cta_options[0]
        
        return f"{summary}\n\n{takeaways}\n\n{cta}"
    
    def _generate_abstract(self, research_data: Dict[str, Any]) -> str:
        """Generate an abstract for academic-style content."""
        topic = research_data.get('topic', 'this topic')
        summary = research_data.get('summary', '')
        
        # Create a concise abstract
        abstract = f"This article provides a comprehensive analysis of {topic}. "
        
        if summary:
            # Use first 200 characters of summary
            abstract += summary[:200].rstrip() + "..."
        
        abstract += f" The findings contribute to our understanding of {topic} and its implications for future development."
        
        return abstract
    
    def _generate_references(self, references: List[Dict[str, Any]]) -> str:
        """Generate properly formatted references."""
        if not references:
            return "No references available."
        
        ref_lines = []
        for ref in references:
            title = ref.get('title', 'Unknown Title')
            url = ref.get('url', '')
            date = ref.get('date_accessed', '')
            
            if url:
                ref_line = f"- [{title}]({url})"
                if date:
                    ref_line += f" (Accessed: {date[:10]})"
            else:
                ref_line = f"- {title}"
            
            ref_lines.append(ref_line)
        
        return '\n'.join(ref_lines)
    
    def _generate_generic_section(self, section: Dict[str, Any], research_data: Dict[str, Any], 
                                 style: Dict[str, Any]) -> str:
        """Generate content for generic sections."""
        content_plan = section.get('content_plan', 'General content about the topic.')
        
        return f"This section covers {content_plan.lower()}"
    
    def _generate_title(self, research_data: Dict[str, Any], content_type: str) -> str:
        """Generate an engaging title."""
        topic = research_data.get('topic', 'Important Topic')
        
        title_templates = {
            'blog_post': [
                f"The Complete Guide to {topic}",
                f"Understanding {topic}: What You Need to Know",
                f"Everything About {topic} in 2024"
            ],
            'article': [
                f"A Comprehensive Analysis of {topic}",
                f"Research Insights into {topic}",
                f"The Current State of {topic}"
            ],
            'social_post': [
                f"Quick Facts About {topic}",
                f"{topic} Explained Simply",
                f"What Everyone Should Know About {topic}"
            ],
            'guide': [
                f"Step-by-Step Guide to {topic}",
                f"How to Master {topic}",
                f"The Ultimate {topic} Handbook"
            ]
        }
        
        templates = title_templates.get(content_type, title_templates['blog_post'])
        return templates[0]  # Could be randomized
    
    def _generate_meta_description(self, content: str, content_type: str) -> str:
        """Generate SEO-friendly meta description."""
        # Extract first meaningful paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
        
        if paragraphs:
            first_paragraph = paragraphs[0]
            # Remove markdown formatting
            clean_text = re.sub(r'[*_`#>\-]', '', first_paragraph)
            # Limit to 160 characters
            if len(clean_text) > 157:
                clean_text = clean_text[:157] + '...'
            return clean_text
        
        return "Comprehensive guide covering the essential aspects of this important topic."
    
    def _calculate_content_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate various content metrics."""
        words = len(content.split())
        characters = len(content)
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])
        
        # Estimate reading time (average 200 words per minute)
        reading_time = max(1, round(words / 200))
        
        # Count headings
        headings = len(re.findall(r'^#{1,6}\s', content, re.MULTILINE))
        
        return {
            'word_count': words,
            'character_count': characters,
            'paragraph_count': paragraphs,
            'heading_count': headings,
            'reading_time': reading_time
        }
    
    def _calculate_content_quality(self, content: str, template: Dict[str, Any]) -> float:
        """Calculate content quality score."""
        metrics = self._calculate_content_metrics(content)
        score = 0.0
        
        # Word count appropriateness (0-30 points)
        target_min = template.get('min_words', 500)
        target_max = template.get('max_words', 2000)
        word_count = metrics['word_count']
        
        if target_min <= word_count <= target_max:
            score += 30
        elif word_count >= target_min * 0.8:
            score += 20
        else:
            score += 10
        
        # Structure quality (0-25 points)
        if metrics['heading_count'] >= 3:
            score += 25
        elif metrics['heading_count'] >= 2:
            score += 20
        else:
            score += 10
        
        # Content density (0-25 points)
        if metrics['paragraph_count'] >= 5:
            score += 25
        elif metrics['paragraph_count'] >= 3:
            score += 20
        else:
            score += 10
        
        # Readability (0-20 points)
        avg_words_per_paragraph = word_count / max(metrics['paragraph_count'], 1)
        if 50 <= avg_words_per_paragraph <= 150:
            score += 20
        else:
            score += 10
        
        return min(score / 100.0, 1.0)
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return [
            "content_generation",
            "structure_planning",
            "title_generation",
            "meta_description_creation",
            "multi_format_support",
            "tone_adaptation",
            "audience_targeting",
            "content_optimization",
            "reference_formatting",
            "quality_assessment"
        ]