"""
Quality Assurance (QA) Agent for validating generated content.

This agent validates that generated content meets specified requirements
including word count, tone, platform optimization, and quality standards.
If requirements aren't met, it provides feedback for content regeneration.
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from utils.logger import get_logger
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade

class QAAgent(BaseAgent):
    """Agent responsible for quality assurance and content validation."""
    
    def setup(self) -> None:
        """Initialize the QA agent."""
        self.logger = get_logger("QAAgent")
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
        
        # Platform-specific requirements
        self.platform_requirements = {
            'linkedin': {
                'min_words': 300,
                'max_words': 3000,
                'ideal_words': (600, 1300),
                'tone': ['professional', 'informative', 'engaging'],
                'required_elements': ['headline', 'key_points', 'call_to_action'],
                'hashtag_count': (3, 5),
                'paragraph_length': (50, 150),  # words per paragraph
                'readability_target': (50, 70)  # Flesch score
            },
            'medium': {
                'min_words': 500,
                'max_words': 5000,
                'ideal_words': (1000, 2500),
                'tone': ['conversational', 'storytelling', 'informative'],
                'required_elements': ['introduction', 'subheadings', 'conclusion'],
                'paragraph_length': (40, 120),
                'readability_target': (50, 70)
            },
            'wordpress': {
                'min_words': 300,
                'max_words': 10000,
                'ideal_words': (1000, 2000),
                'tone': ['seo_optimized', 'informative'],
                'required_elements': ['title', 'meta_description', 'headings', 'internal_links'],
                'paragraph_length': (30, 100),
                'readability_target': (60, 80)
            },
            'twitter': {
                'min_words': 10,
                'max_words': 280,  # characters actually
                'ideal_words': (20, 50),
                'tone': ['concise', 'engaging', 'punchy'],
                'required_elements': ['hook', 'hashtags'],
                'hashtag_count': (1, 3)
            },
            'facebook': {
                'min_words': 50,
                'max_words': 500,
                'ideal_words': (80, 250),
                'tone': ['casual', 'engaging', 'relatable'],
                'required_elements': ['hook', 'engagement_question']
            },
            'default': {
                'min_words': 200,
                'max_words': 5000,
                'ideal_words': (400, 1500),
                'tone': ['professional', 'informative'],
                'required_elements': ['introduction', 'body', 'conclusion'],
                'paragraph_length': (40, 120),
                'readability_target': (50, 70)
            }
        }
        
        # Tone indicators
        self.tone_indicators = {
            'professional': {
                'positive': ['furthermore', 'consequently', 'therefore', 'analysis', 'strategic', 
                            'implement', 'optimize', 'leverage', 'facilitate', 'stakeholder'],
                'negative': ['gonna', 'wanna', 'stuff', 'things', 'cool', 'awesome', 'lol', 'omg']
            },
            'casual': {
                'positive': ['you', 'your', "let's", 'check out', 'awesome', 'cool', 'honestly'],
                'negative': ['heretofore', 'notwithstanding', 'aforementioned']
            },
            'conversational': {
                'positive': ['you', 'we', "i've", "you'll", 'imagine', 'think about', 'ever wondered'],
                'negative': ['one must', 'it is evident that', 'the author']
            },
            'academic': {
                'positive': ['research', 'study', 'findings', 'methodology', 'hypothesis', 'analysis'],
                'negative': ['basically', 'kind of', 'sort of', 'stuff']
            }
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'min_sentences_per_paragraph': 2,
            'max_sentences_per_paragraph': 8,
            'min_paragraphs': 3,
            'repetition_threshold': 0.15,  # Max 15% word repetition
            'transition_word_density': 0.02  # At least 2% transition words
        }
        
        # Transition words for flow analysis
        self.transition_words = {
            'addition': ['additionally', 'furthermore', 'moreover', 'also', 'besides'],
            'contrast': ['however', 'nevertheless', 'although', 'but', 'yet', 'whereas'],
            'cause_effect': ['therefore', 'consequently', 'thus', 'hence', 'as a result'],
            'sequence': ['first', 'second', 'finally', 'next', 'then', 'subsequently'],
            'example': ['for example', 'for instance', 'specifically', 'such as'],
            'conclusion': ['in conclusion', 'to summarize', 'overall', 'ultimately']
        }
    
    def process(self, input_data: AgentInput) -> AgentOutput:
        """Validate content against requirements."""
        content = input_data.data.get('content', '')
        target_word_count = input_data.data.get('target_word_count', 500)
        target_platform = input_data.data.get('target_platform', 'default')
        target_tone = input_data.data.get('tone', 'professional')
        target_audience = input_data.data.get('target_audience', 'general')
        content_type = input_data.data.get('content_type', 'blog_post')
        
        if not content:
            return AgentOutput(
                data={
                    'validation_passed': False,
                    'issues': ['No content provided for validation'],
                    'recommendations': ['Generate content first before validation'],
                    'regeneration_required': True
                },
                agent_name=self.name,
                status="error",
                error_message="No content to validate"
            )
        
        # Run all validation checks
        validation_results = {}
        issues = []
        recommendations = []
        scores = {}
        
        # 1. Word count validation
        word_count_result = self._validate_word_count(content, target_word_count, target_platform)
        validation_results['word_count'] = word_count_result
        scores['word_count'] = word_count_result['score']
        if not word_count_result['passed']:
            issues.extend(word_count_result['issues'])
            recommendations.extend(word_count_result['recommendations'])
        
        # 2. Tone validation
        tone_result = self._validate_tone(content, target_tone)
        validation_results['tone'] = tone_result
        scores['tone'] = tone_result['score']
        if not tone_result['passed']:
            issues.extend(tone_result['issues'])
            recommendations.extend(tone_result['recommendations'])
        
        # 3. Platform optimization validation
        platform_result = self._validate_platform_optimization(content, target_platform)
        validation_results['platform'] = platform_result
        scores['platform'] = platform_result['score']
        if not platform_result['passed']:
            issues.extend(platform_result['issues'])
            recommendations.extend(platform_result['recommendations'])
        
        # 4. Structure validation
        structure_result = self._validate_structure(content, content_type)
        validation_results['structure'] = structure_result
        scores['structure'] = structure_result['score']
        if not structure_result['passed']:
            issues.extend(structure_result['issues'])
            recommendations.extend(structure_result['recommendations'])
        
        # 5. Quality validation
        quality_result = self._validate_quality(content)
        validation_results['quality'] = quality_result
        scores['quality'] = quality_result['score']
        if not quality_result['passed']:
            issues.extend(quality_result['issues'])
            recommendations.extend(quality_result['recommendations'])
        
        # 6. Readability validation
        readability_result = self._validate_readability(content, target_platform, target_audience)
        validation_results['readability'] = readability_result
        scores['readability'] = readability_result['score']
        if not readability_result['passed']:
            issues.extend(readability_result['issues'])
            recommendations.extend(readability_result['recommendations'])
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        
        # Determine if regeneration is needed (threshold: 60%)
        validation_passed = overall_score >= 60 and len([s for s in scores.values() if s < 40]) == 0
        regeneration_required = not validation_passed
        
        # Generate improvement instructions for regeneration
        improvement_instructions = self._generate_improvement_instructions(
            issues, recommendations, target_word_count, target_platform, target_tone
        )
        
        return AgentOutput(
            data={
                'validation_passed': validation_passed,
                'overall_score': overall_score,
                'scores': scores,
                'validation_results': validation_results,
                'issues': issues,
                'recommendations': recommendations,
                'regeneration_required': regeneration_required,
                'improvement_instructions': improvement_instructions,
                'content': content  # Pass through the content
            },
            metadata={
                'total_issues': len(issues),
                'critical_issues': len([i for i in issues if 'critical' in i.lower()]),
                'word_count_actual': len(content.split()),
                'word_count_target': target_word_count,
                'platform': target_platform,
                'tone': target_tone
            },
            agent_name=self.name,
            status="success",
            quality_score=overall_score / 100.0
        )
    
    def _validate_word_count(self, content: str, target: int, platform: str) -> Dict[str, Any]:
        """Validate word count against target."""
        actual_count = len(content.split())
        platform_reqs = self.platform_requirements.get(platform, self.platform_requirements['default'])
        
        min_words = platform_reqs['min_words']
        max_words = platform_reqs['max_words']
        ideal_range = platform_reqs.get('ideal_words', (target * 0.8, target * 1.2))
        
        issues = []
        recommendations = []
        
        # Calculate score
        if actual_count < min_words:
            score = (actual_count / min_words) * 50
            issues.append(f"CRITICAL: Content too short ({actual_count} words, minimum {min_words} required)")
            recommendations.append(f"Add {min_words - actual_count} more words to meet minimum requirement")
            recommendations.append("Expand on key points with more detail and examples")
        elif actual_count < target * 0.8:
            score = 50 + ((actual_count - min_words) / (target * 0.8 - min_words)) * 25
            issues.append(f"Content below target ({actual_count} words, target {target})")
            recommendations.append(f"Add approximately {target - actual_count} more words")
            recommendations.append("Include more examples, case studies, or elaboration")
        elif actual_count > max_words:
            score = max(30, 100 - ((actual_count - max_words) / max_words) * 50)
            issues.append(f"Content exceeds maximum ({actual_count} words, max {max_words})")
            recommendations.append("Condense content and remove redundant sections")
        elif ideal_range[0] <= actual_count <= ideal_range[1]:
            score = 100
        elif actual_count < ideal_range[0]:
            score = 75 + ((actual_count - target * 0.8) / (ideal_range[0] - target * 0.8)) * 25
            issues.append(f"Content slightly below ideal range ({actual_count} words)")
            recommendations.append(f"Consider adding {ideal_range[0] - actual_count} more words for optimal length")
        else:
            score = 75 + ((ideal_range[1] - actual_count) / (max_words - ideal_range[1])) * 25 if actual_count < max_words else 75
        
        return {
            'passed': score >= 60,
            'score': score,
            'actual': actual_count,
            'target': target,
            'min': min_words,
            'max': max_words,
            'ideal_range': ideal_range,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_tone(self, content: str, target_tone: str) -> Dict[str, Any]:
        """Validate content tone matches target."""
        content_lower = content.lower()
        issues = []
        recommendations = []
        
        tone_config = self.tone_indicators.get(target_tone, self.tone_indicators['professional'])
        
        positive_matches = sum(1 for word in tone_config['positive'] if word in content_lower)
        negative_matches = sum(1 for word in tone_config['negative'] if word in content_lower)
        
        total_words = len(content.split())
        positive_density = positive_matches / max(total_words, 1) * 100
        
        # Calculate score
        if negative_matches > 0:
            score = max(30, 80 - negative_matches * 15)
            issues.append(f"Found {negative_matches} words inconsistent with {target_tone} tone")
            recommendations.append(f"Remove or replace informal/inappropriate words for {target_tone} tone")
        elif positive_matches >= 5:
            score = min(100, 70 + positive_matches * 3)
        elif positive_matches >= 2:
            score = 60 + positive_matches * 5
        else:
            score = 50
            issues.append(f"Content lacks {target_tone} tone indicators")
            recommendations.append(f"Add more {target_tone} language and expressions")
        
        return {
            'passed': score >= 60,
            'score': score,
            'target_tone': target_tone,
            'positive_indicators': positive_matches,
            'negative_indicators': negative_matches,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_platform_optimization(self, content: str, platform: str) -> Dict[str, Any]:
        """Validate content is optimized for target platform."""
        platform_reqs = self.platform_requirements.get(platform, self.platform_requirements['default'])
        issues = []
        recommendations = []
        checks_passed = 0
        total_checks = 0
        
        # Check required elements
        required_elements = platform_reqs.get('required_elements', [])
        for element in required_elements:
            total_checks += 1
            if self._check_element_present(content, element):
                checks_passed += 1
            else:
                issues.append(f"Missing {element} for {platform} optimization")
                recommendations.append(f"Add a {element} section to optimize for {platform}")
        
        # Check hashtags for social platforms
        if 'hashtag_count' in platform_reqs:
            total_checks += 1
            hashtag_count = len(re.findall(r'#\w+', content))
            min_hashtags, max_hashtags = platform_reqs['hashtag_count']
            if min_hashtags <= hashtag_count <= max_hashtags:
                checks_passed += 1
            else:
                if hashtag_count < min_hashtags:
                    issues.append(f"Too few hashtags ({hashtag_count}, need {min_hashtags}+)")
                    recommendations.append(f"Add {min_hashtags - hashtag_count} more relevant hashtags")
                else:
                    issues.append(f"Too many hashtags ({hashtag_count}, max {max_hashtags})")
                    recommendations.append(f"Reduce hashtags to {max_hashtags} most relevant ones")
        
        # Check paragraph length for readability platforms
        if 'paragraph_length' in platform_reqs:
            total_checks += 1
            paragraphs = [p for p in content.split('\n\n') if p.strip()]
            if paragraphs:
                avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
                min_len, max_len = platform_reqs['paragraph_length']
                if min_len <= avg_para_length <= max_len:
                    checks_passed += 1
                else:
                    if avg_para_length < min_len:
                        issues.append(f"Paragraphs too short for {platform} (avg {avg_para_length:.0f} words)")
                        recommendations.append("Expand paragraphs with more detail")
                    else:
                        issues.append(f"Paragraphs too long for {platform} (avg {avg_para_length:.0f} words)")
                        recommendations.append("Break up long paragraphs for better readability")
        
        score = (checks_passed / max(total_checks, 1)) * 100
        
        return {
            'passed': score >= 60,
            'score': score,
            'platform': platform,
            'checks_passed': checks_passed,
            'total_checks': total_checks,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _check_element_present(self, content: str, element: str) -> bool:
        """Check if a required element is present in content."""
        element_patterns = {
            'headline': r'^#\s+.+|^[A-Z][^.!?]*[.!?]$',
            'title': r'^#\s+.+',
            'introduction': r'^.{100,}',  # At least 100 chars at start
            'conclusion': r'.{50,}$',  # At least 50 chars at end
            'subheadings': r'^#{2,3}\s+.+',
            'headings': r'^#{1,6}\s+.+',
            'key_points': r'[-•*]\s+.+|\d+\.\s+.+',
            'call_to_action': r'(contact|subscribe|follow|share|comment|click|learn more|get started)',
            'meta_description': r'(meta|description|summary)',
            'internal_links': r'\[.+\]\(.+\)',
            'hook': r'^.{20,100}[.!?]',
            'hashtags': r'#\w+',
            'engagement_question': r'\?'
        }
        
        pattern = element_patterns.get(element, element)
        return bool(re.search(pattern, content, re.MULTILINE | re.IGNORECASE))
    
    def _validate_structure(self, content: str, content_type: str) -> Dict[str, Any]:
        """Validate content structure."""
        issues = []
        recommendations = []
        
        # Count structural elements
        paragraphs = [p for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        headings = re.findall(r'^#{1,6}\s+.+', content, re.MULTILINE)
        bullet_points = re.findall(r'^[-•*]\s+.+', content, re.MULTILINE)
        numbered_lists = re.findall(r'^\d+\.\s+.+', content, re.MULTILINE)
        
        checks_passed = 0
        total_checks = 4
        
        # Check paragraph count
        if len(paragraphs) >= self.quality_thresholds['min_paragraphs']:
            checks_passed += 1
        else:
            issues.append(f"Too few paragraphs ({len(paragraphs)}, need {self.quality_thresholds['min_paragraphs']}+)")
            recommendations.append("Break content into more distinct paragraphs")
        
        # Check for headings
        if len(headings) >= 2:
            checks_passed += 1
        else:
            issues.append("Insufficient headings for content structure")
            recommendations.append("Add more section headings (H2, H3) to improve structure")
        
        # Check for lists or bullet points
        if len(bullet_points) + len(numbered_lists) >= 1:
            checks_passed += 1
        else:
            issues.append("No bullet points or numbered lists found")
            recommendations.append("Add bullet points or numbered lists to improve scannability")
        
        # Check sentence variety in paragraphs
        sentence_variety_good = True
        for para in paragraphs[:3]:  # Check first 3 paragraphs
            sentences = nltk.sent_tokenize(para)
            if len(sentences) > 0:
                lengths = [len(s.split()) for s in sentences]
                if len(set(lengths)) < len(lengths) * 0.5:  # Less than 50% variety
                    sentence_variety_good = False
        
        if sentence_variety_good:
            checks_passed += 1
        else:
            issues.append("Limited sentence length variety")
            recommendations.append("Vary sentence lengths for better readability")
        
        score = (checks_passed / total_checks) * 100
        
        return {
            'passed': score >= 60,
            'score': score,
            'paragraphs': len(paragraphs),
            'headings': len(headings),
            'lists': len(bullet_points) + len(numbered_lists),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_quality(self, content: str) -> Dict[str, Any]:
        """Validate overall content quality."""
        issues = []
        recommendations = []
        
        words = content.lower().split()
        total_words = len(words)
        
        checks_passed = 0
        total_checks = 3
        
        # Check for word repetition
        if total_words > 50:
            word_freq = {}
            for word in words:
                if len(word) > 4:  # Only check significant words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            max_repetition = max(word_freq.values()) if word_freq else 0
            repetition_rate = max_repetition / total_words
            
            if repetition_rate <= self.quality_thresholds['repetition_threshold']:
                checks_passed += 1
            else:
                most_repeated = max(word_freq, key=word_freq.get)
                issues.append(f"High word repetition detected ('{most_repeated}' repeated {max_repetition} times)")
                recommendations.append("Use synonyms and varied vocabulary to reduce repetition")
        else:
            checks_passed += 1
        
        # Check for transition words
        all_transitions = []
        for category in self.transition_words.values():
            all_transitions.extend(category)
        
        transition_count = sum(1 for t in all_transitions if t.lower() in content.lower())
        transition_density = transition_count / max(total_words, 1)
        
        if transition_density >= self.quality_thresholds['transition_word_density']:
            checks_passed += 1
        else:
            issues.append("Insufficient transition words for smooth flow")
            recommendations.append("Add transition words (however, therefore, additionally, etc.)")
        
        # Check for filler phrases
        filler_phrases = ['in order to', 'the fact that', 'it is important to note', 
                         'at the end of the day', 'in today\'s world', 'needless to say']
        filler_count = sum(1 for f in filler_phrases if f.lower() in content.lower())
        
        if filler_count <= 2:
            checks_passed += 1
        else:
            issues.append(f"Too many filler phrases ({filler_count} found)")
            recommendations.append("Remove unnecessary filler phrases for concise writing")
        
        score = (checks_passed / total_checks) * 100
        
        return {
            'passed': score >= 60,
            'score': score,
            'transition_count': transition_count,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _validate_readability(self, content: str, platform: str, audience: str) -> Dict[str, Any]:
        """Validate content readability."""
        issues = []
        recommendations = []
        
        try:
            flesch_score = flesch_reading_ease(content)
            grade_level = flesch_kincaid_grade(content)
        except:
            flesch_score = 50
            grade_level = 10
        
        platform_reqs = self.platform_requirements.get(platform, self.platform_requirements['default'])
        target_range = platform_reqs.get('readability_target', (50, 70))
        
        # Adjust for audience
        if 'beginner' in audience.lower() or 'general' in audience.lower():
            target_range = (60, 80)  # Easier to read
        elif 'expert' in audience.lower() or 'professional' in audience.lower():
            target_range = (40, 60)  # Can be more complex
        
        if target_range[0] <= flesch_score <= target_range[1]:
            score = 100
        elif flesch_score < target_range[0]:
            score = max(40, 100 - (target_range[0] - flesch_score) * 2)
            issues.append(f"Content too complex (Flesch score: {flesch_score:.1f}, target: {target_range[0]}-{target_range[1]})")
            recommendations.append("Simplify sentences and use shorter words")
            recommendations.append("Break up long sentences into shorter ones")
        else:
            score = max(60, 100 - (flesch_score - target_range[1]) * 1.5)
            issues.append(f"Content may be too simple for {audience} audience")
            recommendations.append("Add more sophisticated vocabulary where appropriate")
        
        return {
            'passed': score >= 60,
            'score': score,
            'flesch_score': flesch_score,
            'grade_level': grade_level,
            'target_range': target_range,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _generate_improvement_instructions(self, issues: List[str], recommendations: List[str],
                                          target_word_count: int, platform: str, tone: str) -> Dict[str, Any]:
        """Generate detailed instructions for content regeneration."""
        
        # Prioritize recommendations
        critical_improvements = []
        important_improvements = []
        optional_improvements = []
        
        for rec in recommendations:
            if 'word' in rec.lower() or 'critical' in rec.lower():
                critical_improvements.append(rec)
            elif 'add' in rec.lower() or 'include' in rec.lower():
                important_improvements.append(rec)
            else:
                optional_improvements.append(rec)
        
        return {
            'summary': f"Content needs improvement for {platform} platform with {tone} tone",
            'target_word_count': target_word_count,
            'target_platform': platform,
            'target_tone': tone,
            'critical_improvements': critical_improvements,
            'important_improvements': important_improvements,
            'optional_improvements': optional_improvements,
            'regeneration_prompt': self._build_regeneration_prompt(
                issues, recommendations, target_word_count, platform, tone
            )
        }
    
    def _build_regeneration_prompt(self, issues: List[str], recommendations: List[str],
                                   word_count: int, platform: str, tone: str) -> str:
        """Build a prompt for content regeneration."""
        prompt_parts = [
            f"Regenerate content with the following requirements:",
            f"- Target word count: {word_count} words (current content is insufficient)",
            f"- Platform: {platform}",
            f"- Tone: {tone}",
            "",
            "Issues to address:"
        ]
        
        for issue in issues[:5]:  # Top 5 issues
            prompt_parts.append(f"  • {issue}")
        
        prompt_parts.append("")
        prompt_parts.append("Improvements needed:")
        
        for rec in recommendations[:5]:  # Top 5 recommendations
            prompt_parts.append(f"  • {rec}")
        
        return "\n".join(prompt_parts)
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return [
            "word_count_validation",
            "tone_validation",
            "platform_optimization_check",
            "structure_validation",
            "quality_assessment",
            "readability_analysis",
            "improvement_recommendations",
            "regeneration_instructions",
            "multi_platform_support"
        ]