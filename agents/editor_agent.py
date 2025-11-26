"""
Editor Agent for improving grammar, style, coherence, and readability of content.

This agent refines humanized content by fixing grammar errors, improving style
consistency, enhancing readability, and ensuring professional quality.
"""

import re
import string
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from collections import Counter
from agents.base_agent import BaseAgent, AgentInput, AgentOutput
import nltk
from textstat import (
    flesch_reading_ease, flesch_kincaid_grade, 
    automated_readability_index, coleman_liau_index,
    gunning_fog, smog_index
)

class EditorAgent(BaseAgent):
    """Agent responsible for editing and improving content quality."""
    
    def setup(self) -> None:
        """Initialize the editor agent."""
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
            
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
        
        # Grammar and style rules
        self.grammar_rules = {
            # Common grammar fixes
            r'\b(it\'s)\s+(own)\b': r'its \2',  # it's own -> its own
            r'\b(your)\s+(welcome)\b': r"you're \2",  # your welcome -> you're welcome
            r'\b(there)\s+(going)\b': r"they're \2",  # there going -> they're going
            r'\b(who\'s)\s+(car)\b': r'whose \2',  # who's car -> whose car
            r'\b(loose)\s+(weight)\b': r'lose \2',  # loose weight -> lose weight
            r'\b(affect)\s+(on)\b': r'effect \2',  # affect on -> effect on
            r'\b(alot)\b': r'a lot',  # alot -> a lot
            r'\b(definately)\b': r'definitely',  # definately -> definitely
            r'\b(seperate)\b': r'separate',  # seperate -> separate
            r'\b(occured)\b': r'occurred',  # occured -> occurred
            r'\b(recieve)\b': r'receive',  # recieve -> receive
        }
        
        # Style improvements
        self.style_rules = {
            # Redundant phrases
            r'\b(in order to)\b': r'to',
            r'\b(at this point in time)\b': r'now',
            r'\b(due to the fact that)\b': r'because',
            r'\b(in spite of the fact that)\b': r'although',
            r'\b(it should be noted that)\b': r'',
            r'\b(it is important to note that)\b': r'',
            r'\b(needless to say)\b': r'',
            
            # Weak qualifiers
            r'\b(very unique)\b': r'unique',
            r'\b(quite interesting)\b': r'interesting',
            r'\b(really good)\b': r'excellent',
            r'\b(pretty much)\b': r'',
            r'\b(sort of)\b': r'',
            r'\b(kind of)\b': r'',
        }
        
        # Readability improvements
        self.readability_rules = {
            # Split long sentences
            'max_sentence_length': 25,
            'preferred_sentence_length': 15,
            
            # Paragraph guidelines
            'max_paragraph_sentences': 5,
            'preferred_paragraph_sentences': 3,
            
            # Word choice
            'complex_to_simple': {
                'utilize': 'use',
                'demonstrate': 'show',
                'facilitate': 'help',
                'commence': 'begin',
                'terminate': 'end',
                'approximately': 'about',
                'methodology': 'method',
                'implementation': 'use',
                'optimization': 'improvement',
                'functionality': 'features'
            }
        }
        
        # Coherence markers
        self.transition_words = {
            'addition': ['also', 'furthermore', 'moreover', 'additionally', 'plus'],
            'contrast': ['however', 'but', 'yet', 'nevertheless', 'on the other hand'],
            'cause_effect': ['therefore', 'thus', 'consequently', 'as a result', 'because'],
            'sequence': ['first', 'next', 'then', 'finally', 'meanwhile'],
            'emphasis': ['indeed', 'certainly', 'obviously', 'clearly', 'importantly']
        }
    
    def process(self, input_data: AgentInput) -> AgentOutput:
        """Edit and improve the provided content."""
        content = input_data.data.get('content', '')
        title = input_data.data.get('title', '')
        content_type = input_data.data.get('content_type', 'blog_post')
        style_guide = input_data.data.get('style_guide', 'default')
        
        if not content:
            return AgentOutput(
                data={},
                agent_name=self.name,
                status="error",
                error_message="No content provided for editing"
            )
        
        # Store original for comparison
        original_content = content
        original_title = title
        
        # Apply editing improvements
        editing_log = []
        
        # 1. Grammar corrections
        content, grammar_fixes = self._fix_grammar(content)
        editing_log.extend(grammar_fixes)
        
        # 2. Style improvements
        content, style_fixes = self._improve_style(content)
        editing_log.extend(style_fixes)
        
        # 3. Readability enhancements
        content, readability_fixes = self._enhance_readability(content)
        editing_log.extend(readability_fixes)
        
        # 4. Coherence improvements
        content, coherence_fixes = self._improve_coherence(content)
        editing_log.extend(coherence_fixes)
        
        # 5. Title editing
        edited_title = self._edit_title(title) if title else ""
        
        # 6. Structure optimization
        content = self._optimize_structure(content)
        
        # Calculate improvement metrics
        original_score = self._calculate_editing_score(original_content)
        edited_score = self._calculate_editing_score(content)
        
        # Generate editing report
        editing_report = self._generate_editing_report(
            original_content, content, editing_log, original_score, edited_score
        )
        
        return AgentOutput(
            data={
                'edited_content': content,
                'edited_title': edited_title,
                'original_content': original_content,
                'original_title': original_title,
                'editing_notes': editing_log,
                'editing_report': editing_report,
                'grammar_score': self._calculate_grammar_score(content),
                'readability_score': edited_score,
                'improvement': edited_score - original_score
            },
            metadata={
                'fixes_applied': len(editing_log),
                'readability_metrics': self._get_readability_metrics(content),
                'coherence_score': self._calculate_coherence_score(content),
                'style_guide_used': style_guide
            },
            agent_name=self.name,
            status="success",
            quality_score=min(edited_score / 100.0, 1.0)
        )
    
    def _fix_grammar(self, text: str) -> Tuple[str, List[str]]:
        """Fix common grammar errors."""
        fixes_applied = []
        original_text = text
        
        for pattern, replacement in self.grammar_rules.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                fixes_applied.append(f"Grammar fix: {pattern} -> {replacement}")
        
        # Fix double spaces
        if '  ' in text:
            text = re.sub(r'\s+', ' ', text)
            fixes_applied.append("Fixed multiple spaces")
        
        # Fix punctuation spacing
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([,.;:!?])([A-Za-z])', r'\1 \2', text)  # Add space after punctuation
        
        # Fix capitalization after periods
        text = re.sub(r'(\.)(\s*)([a-z])', lambda m: m.group(1) + m.group(2) + m.group(3).upper(), text)
        
        return text, fixes_applied
    
    def _improve_style(self, text: str) -> Tuple[str, List[str]]:
        """Improve writing style."""
        fixes_applied = []
        
        # Apply style rules
        for pattern, replacement in self.style_rules.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                clean_pattern = pattern.replace(r'\b', '').replace(r')', '').replace('(', '')
                fixes_applied.append(f"Style improvement: removed '{clean_pattern}'")
        
        # Reduce adverb usage (words ending in -ly)
        adverbs = re.findall(r'\b\w+ly\b', text)
        excessive_adverbs = [adv for adv in adverbs if adverbs.count(adv) > 2]
        for adv in excessive_adverbs:
            # Replace some instances
            pattern = r'\b' + re.escape(adv) + r'\b'
            text = re.sub(pattern, '', text, count=1)
            fixes_applied.append(f"Reduced excessive adverb: '{adv}'")
        
        # Fix passive voice (basic detection)
        passive_patterns = [
            r'\bis\s+(\w+ed)\b',
            r'\bare\s+(\w+ed)\b',
            r'\bwas\s+(\w+ed)\b',
            r'\bwere\s+(\w+ed)\b'
        ]
        
        for pattern in passive_patterns:
            if re.search(pattern, text):
                fixes_applied.append("Detected passive voice - consider making active")
        
        return text, fixes_applied
    
    def _enhance_readability(self, text: str) -> Tuple[str, List[str]]:
        """Enhance content readability."""
        fixes_applied = []
        
        # Replace complex words with simpler alternatives
        complex_to_simple = self.readability_rules['complex_to_simple']
        for complex_word, simple_word in complex_to_simple.items():
            if complex_word in text.lower():
                pattern = r'\b' + re.escape(complex_word) + r'\b'
                text = re.sub(pattern, simple_word, text, flags=re.IGNORECASE)
                fixes_applied.append(f"Simplified: '{complex_word}' -> '{simple_word}'")
        
        # Break up overly long sentences
        sentences = nltk.sent_tokenize(text)
        new_sentences = []
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) > self.readability_rules['max_sentence_length']:
                # Try to split at conjunctions
                split_sentence = self._split_long_sentence(sentence)
                if split_sentence != sentence:
                    new_sentences.extend(split_sentence)
                    fixes_applied.append(f"Split long sentence ({len(words)} words)")
                else:
                    new_sentences.append(sentence)
            else:
                new_sentences.append(sentence)
        
        text = ' '.join(new_sentences)
        
        # Improve paragraph structure
        text = self._improve_paragraph_structure(text, fixes_applied)
        
        return text, fixes_applied
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split a long sentence into shorter ones."""
        # Look for natural break points
        break_points = [
            ', and ', ', but ', ', so ', ', which ', ', that ', 
            ' because ', ' although ', ' while ', ' when ', ' where '
        ]
        
        for break_point in break_points:
            if break_point in sentence:
                parts = sentence.split(break_point, 1)
                if len(parts) == 2:
                    first_part = parts[0].strip()
                    second_part = parts[1].strip()
                    
                    # Ensure first part ends with punctuation
                    if not first_part.endswith(('.', '!', '?')):
                        first_part += '.'
                    
                    # Capitalize second part
                    if second_part and second_part[0].islower():
                        second_part = second_part[0].upper() + second_part[1:]
                    
                    return [first_part, second_part]
        
        return [sentence]
    
    def _improve_paragraph_structure(self, text: str, fixes_applied: List[str]) -> str:
        """Improve paragraph structure and flow."""
        paragraphs = text.split('\n\n')
        improved_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            sentences = nltk.sent_tokenize(paragraph)
            
            # Split overly long paragraphs
            if len(sentences) > self.readability_rules['max_paragraph_sentences']:
                # Split into smaller paragraphs
                mid_point = len(sentences) // 2
                first_half = ' '.join(sentences[:mid_point])
                second_half = ' '.join(sentences[mid_point:])
                improved_paragraphs.extend([first_half, second_half])
                fixes_applied.append(f"Split long paragraph ({len(sentences)} sentences)")
            else:
                improved_paragraphs.append(paragraph)
        
        return '\n\n'.join(improved_paragraphs)
    
    def _improve_coherence(self, text: str) -> Tuple[str, List[str]]:
        """Improve content coherence and flow."""
        fixes_applied = []
        
        paragraphs = text.split('\n\n')
        improved_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
                
            sentences = nltk.sent_tokenize(paragraph)
            
            # Add transitions between paragraphs if missing
            if i > 0 and len(sentences) > 0:
                first_sentence = sentences[0]
                if not self._has_transition(first_sentence):
                    # Add appropriate transition
                    transition = self._suggest_transition(i, len(paragraphs))
                    if transition:
                        sentences[0] = f"{transition}, {first_sentence.lower()}"
                        fixes_applied.append(f"Added transition: '{transition}'")
            
            improved_paragraph = ' '.join(sentences)
            improved_paragraphs.append(improved_paragraph)
        
        return '\n\n'.join(improved_paragraphs), fixes_applied
    
    def _has_transition(self, sentence: str) -> bool:
        """Check if a sentence starts with a transition word."""
        sentence_lower = sentence.lower()
        all_transitions = []
        for transition_list in self.transition_words.values():
            all_transitions.extend(transition_list)
        
        for transition in all_transitions:
            if sentence_lower.startswith(transition.lower()):
                return True
        return False
    
    def _suggest_transition(self, paragraph_index: int, total_paragraphs: int) -> Optional[str]:
        """Suggest an appropriate transition word."""
        if paragraph_index == 1:
            return "Additionally"
        elif paragraph_index < total_paragraphs - 1:
            return "Furthermore"
        else:
            return "Finally"
    
    def _edit_title(self, title: str) -> str:
        """Edit and improve the title."""
        if not title:
            return ""
        
        # Capitalize properly (title case)
        # Simple title case (doesn't handle articles perfectly, but good enough)
        words = title.split()
        title_words = []
        
        for i, word in enumerate(words):
            if i == 0 or len(word) > 3 or word.lower() not in ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with']:
                title_words.append(word.capitalize())
            else:
                title_words.append(word.lower())
        
        edited_title = ' '.join(title_words)
        
        # Remove redundant words
        redundant_patterns = [
            r'\bThe Ultimate Guide to (.+)',
            r'\bComplete Guide to (.+)',
            r'\bEverything You Need to Know About (.+)'
        ]
        
        for pattern in redundant_patterns:
            match = re.match(pattern, edited_title)
            if match:
                # Keep the core topic, but make it more concise
                core_topic = match.group(1)
                edited_title = f"Guide to {core_topic}"
                break
        
        return edited_title
    
    def _optimize_structure(self, text: str) -> str:
        """Optimize overall content structure."""
        # Ensure proper heading hierarchy
        lines = text.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Fix heading levels (ensure logical progression)
            if line.startswith('#'):
                # Count heading level
                level = len(line) - len(line.lstrip('#'))
                if level > 4:  # Limit to h4
                    line = '#### ' + line.lstrip('# ')
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _calculate_editing_score(self, text: str) -> float:
        """Calculate overall editing quality score."""
        if not text:
            return 0.0
        
        score = 0.0
        
        # Grammar score (0-25 points)
        grammar_score = self._calculate_grammar_score(text)
        score += grammar_score * 0.25
        
        # Readability score (0-35 points)
        try:
            reading_ease = flesch_reading_ease(text)
            if 60 <= reading_ease <= 80:  # Optimal range
                score += 35
            elif 50 <= reading_ease <= 90:
                score += 25
            else:
                score += 15
        except:
            score += 20
        
        # Coherence score (0-25 points)
        coherence_score = self._calculate_coherence_score(text)
        score += coherence_score * 0.25
        
        # Style score (0-15 points)
        style_score = self._calculate_style_score(text)
        score += style_score * 0.15
        
        return min(score, 100.0)
    
    def _calculate_grammar_score(self, text: str) -> float:
        """Calculate grammar quality score (0-100)."""
        if not text:
            return 0.0
        
        score = 100.0
        
        # Check for common grammar errors
        for pattern in self.grammar_rules.keys():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score -= matches * 10  # Penalize each grammar error
        
        # Check punctuation
        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            if not sentence.strip().endswith(('.', '!', '?')):
                score -= 5  # Penalize missing punctuation
        
        return max(score, 0.0)
    
    def _calculate_coherence_score(self, text: str) -> float:
        """Calculate coherence score (0-100)."""
        if not text:
            return 0.0
        
        score = 0.0
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 2:
            return 50.0  # Single paragraph gets medium score
        
        # Check for transitions between paragraphs
        transitions_found = 0
        for i in range(1, len(paragraphs)):
            first_sentence = nltk.sent_tokenize(paragraphs[i])[0] if paragraphs[i] else ""
            if self._has_transition(first_sentence):
                transitions_found += 1
        
        # Score based on transition usage
        transition_ratio = transitions_found / (len(paragraphs) - 1)
        score = transition_ratio * 100
        
        return score
    
    def _calculate_style_score(self, text: str) -> float:
        """Calculate style quality score (0-100)."""
        if not text:
            return 0.0
        
        score = 100.0
        
        # Penalize style issues
        for pattern in self.style_rules.keys():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score -= matches * 5  # Penalize each style issue
        
        # Check sentence variety
        sentences = nltk.sent_tokenize(text)
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            if len(set(lengths)) < len(lengths) * 0.3:  # Low variety
                score -= 10
        
        return max(score, 0.0)
    
    def _get_readability_metrics(self, text: str) -> Dict[str, Any]:
        """Get comprehensive readability metrics."""
        if not text:
            return {}
        
        try:
            return {
                'flesch_reading_ease': flesch_reading_ease(text),
                'flesch_kincaid_grade': flesch_kincaid_grade(text),
                'automated_readability_index': automated_readability_index(text),
                'coleman_liau_index': coleman_liau_index(text),
                'gunning_fog': gunning_fog(text),
                'smog_index': smog_index(text),
                'avg_sentence_length': len(text.split()) / len(nltk.sent_tokenize(text)),
                'word_count': len(text.split()),
                'sentence_count': len(nltk.sent_tokenize(text)),
                'paragraph_count': len([p for p in text.split('\n\n') if p.strip()])
            }
        except:
            return {'error': 'Could not calculate readability metrics'}
    
    def _generate_editing_report(self, original: str, edited: str, 
                               editing_log: List[str], original_score: float, 
                               edited_score: float) -> Dict[str, Any]:
        """Generate comprehensive editing report."""
        return {
            'summary': {
                'total_fixes': len(editing_log),
                'original_score': original_score,
                'edited_score': edited_score,
                'improvement': edited_score - original_score,
                'percentage_improvement': ((edited_score - original_score) / original_score * 100) if original_score > 0 else 0
            },
            'fixes_by_category': self._categorize_fixes(editing_log),
            'before_after_comparison': {
                'original_word_count': len(original.split()),
                'edited_word_count': len(edited.split()),
                'original_sentence_count': len(nltk.sent_tokenize(original)),
                'edited_sentence_count': len(nltk.sent_tokenize(edited))
            },
            'recommendations': self._generate_recommendations(edited)
        }
    
    def _categorize_fixes(self, editing_log: List[str]) -> Dict[str, int]:
        """Categorize the types of fixes applied."""
        categories = {
            'grammar': 0,
            'style': 0,
            'readability': 0,
            'coherence': 0,
            'structure': 0
        }
        
        for fix in editing_log:
            fix_lower = fix.lower()
            if 'grammar' in fix_lower:
                categories['grammar'] += 1
            elif 'style' in fix_lower or 'removed' in fix_lower:
                categories['style'] += 1
            elif 'simplified' in fix_lower or 'split' in fix_lower:
                categories['readability'] += 1
            elif 'transition' in fix_lower:
                categories['coherence'] += 1
            else:
                categories['structure'] += 1
        
        return categories
    
    def _generate_recommendations(self, text: str) -> List[str]:
        """Generate recommendations for further improvement."""
        recommendations = []
        
        # Check readability
        try:
            reading_ease = flesch_reading_ease(text)
            if reading_ease < 60:
                recommendations.append("Consider simplifying language for better readability")
            elif reading_ease > 90:
                recommendations.append("Consider adding some complexity for more sophisticated writing")
        except:
            pass
        
        # Check sentence variety
        sentences = nltk.sent_tokenize(text)
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            
            if avg_length > 20:
                recommendations.append("Consider shortening some sentences for better flow")
            elif avg_length < 8:
                recommendations.append("Consider combining some short sentences for better rhythm")
        
        # Check paragraph structure
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            avg_sentences_per_paragraph = len(sentences) / len(paragraphs)
            if avg_sentences_per_paragraph > 6:
                recommendations.append("Consider breaking up long paragraphs")
        
        return recommendations
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return [
            "grammar_correction",
            "style_improvement",
            "readability_enhancement",
            "coherence_improvement",
            "structure_optimization",
            "title_editing",
            "passive_voice_detection",
            "sentence_variety_analysis",
            "paragraph_optimization",
            "transition_enhancement",
            "punctuation_correction",
            "word_choice_improvement",
            "comprehensive_editing_reports"
        ]