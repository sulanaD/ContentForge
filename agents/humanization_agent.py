"""
Humanization Agent for making AI-generated content feel more natural and human-like.

This agent employs various techniques to transform robotic AI content into 
engaging, natural-sounding text that resonates with human readers.
"""

import re
import random
from typing import Dict, Any, List, Tuple
from agents.base_agent import BaseAgent, AgentInput, AgentOutput
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade
from collections import defaultdict

class HumanizationAgent(BaseAgent):
    """Agent responsible for humanizing AI-generated content."""
    
    def setup(self) -> None:
        """Initialize the humanization agent."""
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
        
        # Humanization patterns and replacements
        self.formal_to_casual = {
            "furthermore": ["also", "plus", "what's more", "on top of that"],
            "therefore": ["so", "that's why", "which means"],
            "however": ["but", "though", "still", "yet"],
            "subsequently": ["then", "next", "after that"],
            "additionally": ["also", "plus", "and"],
            "consequently": ["so", "as a result", "because of this"],
            "nevertheless": ["still", "even so", "but"],
            "moreover": ["also", "what's more", "plus"],
        }
        
        # Conversational starters
        self.conversation_starters = [
            "Here's the thing:",
            "Let me tell you something:",
            "You know what?",
            "Here's what I've learned:",
            "Think about it:",
            "Picture this:",
            "Imagine this scenario:",
            "Let's be honest:",
            "Here's the reality:",
        ]
        
        # Transition phrases
        self.natural_transitions = [
            "Speaking of which",
            "That reminds me",
            "On a similar note",
            "While we're on the topic",
            "This brings up an interesting point",
            "Now, here's where it gets interesting",
        ]
        
        # Personal touches
        self.personal_phrases = [
            "In my experience",
            "What I've noticed is",
            "From what I've seen",
            "Here's what works",
            "I've found that",
            "The way I see it",
        ]
        
        # Sentence variety patterns
        self.sentence_starters = [
            "What's interesting is",
            "The truth is",
            "Surprisingly,",
            "Believe it or not,",
            "As it turns out,",
            "The reality is",
        ]
    
    def process(self, input_data: AgentInput) -> AgentOutput:
        """Humanize the provided content."""
        content = input_data.data.get('content', '')
        title = input_data.data.get('title', '')
        content_type = input_data.data.get('content_type', 'blog_post')
        
        if not content:
            return AgentOutput(
                data={},
                agent_name=self.name,
                status="error",
                error_message="No content provided for humanization"
            )
        
        # Apply humanization techniques
        humanized_content = self._humanize_content(content, content_type)
        humanized_title = self._humanize_title(title) if title else ""
        
        # Calculate improvement metrics
        original_score = self._calculate_human_score(content)
        humanized_score = self._calculate_human_score(humanized_content)
        
        return AgentOutput(
            data={
                'content': humanized_content,
                'title': humanized_title,
                'original_human_score': original_score,
                'humanized_score': humanized_score,
                'improvement': humanized_score - original_score,
                'content_type': content_type
            },
            metadata={
                'techniques_applied': self._get_applied_techniques(),
                'readability_metrics': self._get_readability_metrics(humanized_content),
                'processing_stats': {
                    'sentences_modified': self.sentences_modified,
                    'phrases_added': self.phrases_added,
                    'transitions_improved': self.transitions_improved
                }
            },
            agent_name=self.name,
            status="success",
            quality_score=min(humanized_score / 100.0, 1.0)
        )
    
    def _humanize_content(self, content: str, content_type: str) -> str:
        """Apply various humanization techniques to the content."""
        self.sentences_modified = 0
        self.phrases_added = 0
        self.transitions_improved = 0
        
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        humanized_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
                
            # Apply humanization techniques
            paragraph = self._add_conversational_elements(paragraph)
            paragraph = self._vary_sentence_structure(paragraph)
            paragraph = self._replace_formal_language(paragraph)
            paragraph = self._add_personal_touches(paragraph, i == 0)
            paragraph = self._improve_transitions(paragraph)
            paragraph = self._add_emotional_language(paragraph)
            
            humanized_paragraphs.append(paragraph)
        
        return '\n\n'.join(humanized_paragraphs)
    
    def _add_conversational_elements(self, text: str) -> str:
        """Add conversational elements to make text more engaging."""
        sentences = nltk.sent_tokenize(text)
        
        # Add conversational starters to some sentences
        for i in range(len(sentences)):
            if i == 0 and random.random() < 0.3:  # 30% chance for first sentence
                starter = random.choice(self.conversation_starters)
                sentences[i] = f"{starter} {sentences[i]}"
                self.phrases_added += 1
            
            # Add rhetorical questions
            if random.random() < 0.15:  # 15% chance
                if not sentences[i].endswith('?'):
                    # Convert some statements to questions
                    if "you" in sentences[i].lower() or "your" in sentences[i].lower():
                        question_starters = ["Ever wonder", "Have you noticed", "Isn't it interesting that"]
                        if random.random() < 0.5:
                            starter = random.choice(question_starters)
                            sentences[i] = f"{starter} {sentences[i].lower()}"
                            sentences[i] = sentences[i].replace('.', '?')
                            self.sentences_modified += 1
        
        return ' '.join(sentences)
    
    def _vary_sentence_structure(self, text: str) -> str:
        """Vary sentence structure for better flow."""
        sentences = nltk.sent_tokenize(text)
        
        for i in range(len(sentences)):
            # Add sentence starters for variety
            if random.random() < 0.2:  # 20% chance
                starter = random.choice(self.sentence_starters)
                sentences[i] = f"{starter} {sentences[i].lower()}"
                self.sentences_modified += 1
            
            # Break long sentences occasionally
            if len(sentences[i].split()) > 25 and random.random() < 0.4:
                sentences[i] = self._break_long_sentence(sentences[i])
                self.sentences_modified += 1
        
        return ' '.join(sentences)
    
    def _replace_formal_language(self, text: str) -> str:
        """Replace formal language with more casual alternatives."""
        for formal, casuals in self.formal_to_casual.items():
            if formal in text.lower():
                replacement = random.choice(casuals)
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(formal) + r'\b'
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _add_personal_touches(self, text: str, is_first_paragraph: bool) -> str:
        """Add personal touches to make content more relatable."""
        sentences = nltk.sent_tokenize(text)
        
        # Add personal phrases to some sentences
        for i in range(len(sentences)):
            if random.random() < 0.1:  # 10% chance
                phrase = random.choice(self.personal_phrases)
                sentences[i] = f"{phrase}, {sentences[i].lower()}"
                self.phrases_added += 1
        
        return ' '.join(sentences)
    
    def _improve_transitions(self, text: str) -> str:
        """Improve transitions between ideas."""
        sentences = nltk.sent_tokenize(text)
        
        # Add natural transitions
        for i in range(1, len(sentences)):
            if random.random() < 0.15:  # 15% chance
                transition = random.choice(self.natural_transitions)
                sentences[i] = f"{transition}, {sentences[i].lower()}"
                self.transitions_improved += 1
        
        return ' '.join(sentences)
    
    def _add_emotional_language(self, text: str) -> str:
        """Add appropriate emotional language to enhance engagement."""
        # Define emotional enhancers
        enhancers = {
            'good': ['amazing', 'fantastic', 'excellent', 'wonderful'],
            'bad': ['terrible', 'awful', 'horrible', 'dreadful'],
            'big': ['huge', 'massive', 'enormous', 'gigantic'],
            'small': ['tiny', 'minuscule', 'microscopic'],
            'important': ['crucial', 'vital', 'essential', 'critical'],
            'interesting': ['fascinating', 'intriguing', 'captivating', 'compelling']
        }
        
        for neutral, emotional in enhancers.items():
            if neutral in text.lower() and random.random() < 0.3:
                replacement = random.choice(emotional)
                pattern = r'\b' + re.escape(neutral) + r'\b'
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _break_long_sentence(self, sentence: str) -> str:
        """Break a long sentence into shorter, more digestible parts."""
        # Find logical break points
        break_points = [', and', ', but', ', so', ', which', ', that']
        
        for point in break_points:
            if point in sentence:
                parts = sentence.split(point, 1)
                if len(parts) == 2:
                    return f"{parts[0]}. {parts[1].strip().capitalize()}"
        
        return sentence
    
    def _humanize_title(self, title: str) -> str:
        """Humanize the title to make it more engaging."""
        if not title:
            return ""
        
        # Add engaging elements to titles
        engaging_starters = [
            "The Truth About",
            "Why",
            "How to",
            "The Ultimate Guide to",
            "Everything You Need to Know About",
            "The Secret to",
            "What Nobody Tells You About"
        ]
        
        # Sometimes add an engaging starter
        if random.random() < 0.3:
            starter = random.choice(engaging_starters)
            if not any(title.lower().startswith(s.lower()) for s in engaging_starters):
                title = f"{starter} {title}"
        
        return title
    
    def _calculate_human_score(self, text: str) -> float:
        """Calculate a score indicating how human-like the text is."""
        if not text:
            return 0.0
        
        score = 0.0
        
        # Readability score (0-30 points)
        try:
            reading_ease = flesch_reading_ease(text)
            if 60 <= reading_ease <= 80:  # Optimal range
                score += 30
            elif 50 <= reading_ease < 90:
                score += 20
            else:
                score += 10
        except:
            score += 15  # Default if calculation fails
        
        # Sentence variety (0-25 points)
        sentences = nltk.sent_tokenize(text)
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            length_variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            
            # Higher variance indicates better sentence variety
            if length_variance > 50:
                score += 25
            elif length_variance > 25:
                score += 20
            else:
                score += 10
        
        # Conversational elements (0-20 points)
        conversational_indicators = ['you', 'your', 'we', 'our', 'let\'s', '?', '!']
        text_lower = text.lower()
        conversational_count = sum(text_lower.count(indicator) for indicator in conversational_indicators)
        score += min(conversational_count * 2, 20)
        
        # Personal touches (0-15 points)
        personal_indicators = ['i', 'my', 'me', 'experience', 'believe', 'think']
        personal_count = sum(text_lower.count(indicator) for indicator in personal_indicators)
        score += min(personal_count * 1.5, 15)
        
        # Natural transitions (0-10 points)
        transition_count = sum(1 for trans in self.natural_transitions if trans.lower() in text_lower)
        score += min(transition_count * 3, 10)
        
        return min(score, 100.0)  # Cap at 100
    
    def _get_readability_metrics(self, text: str) -> Dict[str, Any]:
        """Get comprehensive readability metrics."""
        try:
            return {
                'flesch_reading_ease': flesch_reading_ease(text),
                'flesch_kincaid_grade': flesch_kincaid_grade(text),
                'word_count': len(text.split()),
                'sentence_count': len(nltk.sent_tokenize(text)),
                'avg_words_per_sentence': len(text.split()) / len(nltk.sent_tokenize(text)) if text else 0
            }
        except:
            return {'error': 'Could not calculate readability metrics'}
    
    def _get_applied_techniques(self) -> List[str]:
        """Return list of techniques applied during humanization."""
        return [
            "conversational_elements",
            "sentence_variety",
            "formal_to_casual_replacement",
            "personal_touches",
            "natural_transitions",
            "emotional_language",
            "title_enhancement"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return [
            "content_humanization",
            "conversational_tone_enhancement",
            "sentence_structure_variation",
            "formal_language_casualization",
            "personal_touch_addition",
            "transition_improvement",
            "emotional_language_enhancement",
            "readability_optimization",
            "title_humanization"
        ]