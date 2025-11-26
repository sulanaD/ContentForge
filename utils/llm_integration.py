"""
LLM Integration Module for AI Workflow Orchestrator.

Supports multiple LLM providers:
- Groq (Llama, Mixtral - fast inference)
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Ollama (Local models)

Set your API keys in environment variables (.env file) or config/settings.json
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

from utils.logger import get_logger

logger = get_logger("LLMIntegration")

class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured."""
        pass

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider (GPT-4, GPT-3.5)."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

class AnthropicProvider(BaseLLMProvider):
    """Anthropic API provider (Claude)."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("Anthropic API key not configured")
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

class GroqProvider(BaseLLMProvider):
    """Groq API provider (fast inference with Llama, Mixtral, etc.)."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("Groq API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("Ollama not running or not accessible")
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=data, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result["response"]
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            raise

class TemplateProvider(BaseLLMProvider):
    """
    Fallback template-based provider when no LLM is available.
    Uses rule-based content generation (current default behavior).
    """
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def is_available(self) -> bool:
        return True  # Always available as fallback
    
    def _load_templates(self) -> Dict[str, str]:
        """Load content templates."""
        return {
            'blog_post': """# {title}

## Introduction
{introduction}

## Key Points

### Point 1: {point_1_title}
{point_1_content}

### Point 2: {point_2_title}
{point_2_content}

### Point 3: {point_3_title}
{point_3_content}

## Best Practices
{best_practices}

## Conclusion
{conclusion}

## Call to Action
{cta}
""",
            'linkedin': """🚀 **{hook}**

{introduction}

Here's what I've learned about {topic}:

✅ **{point_1}**
{point_1_detail}

✅ **{point_2}**
{point_2_detail}

✅ **{point_3}**
{point_3_detail}

💡 **Key Takeaway:** {key_takeaway}

What are your thoughts on this? I'd love to hear your experiences!

{hashtags}
""",
            'article': """# {title}

## Executive Summary
{summary}

## Introduction
{introduction}

## Background
{background}

## Analysis
{analysis}

## Key Findings

### Finding 1
{finding_1}

### Finding 2
{finding_2}

### Finding 3
{finding_3}

## Implications
{implications}

## Recommendations
{recommendations}

## Conclusion
{conclusion}

## References
{references}
"""
        }
    
    def generate(self, prompt: str, content_type: str = "blog_post", 
                 topic: str = "", word_count: int = 500, **kwargs) -> str:
        """Generate content using templates and the prompt context."""
        
        # Parse the prompt to extract requirements
        requirements = self._parse_prompt(prompt)
        
        # Select appropriate template
        template = self.templates.get(content_type, self.templates['blog_post'])
        
        # Generate content sections based on word count
        sections = self._generate_sections(topic, requirements, word_count, content_type)
        
        # Fill template
        try:
            content = template.format(**sections)
        except KeyError:
            # If template variables don't match, return raw generated content
            content = self._generate_raw_content(topic, requirements, word_count)
        
        return content
    
    def _parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parse prompt to extract requirements."""
        requirements = {
            'tone': 'professional',
            'platform': 'default',
            'audience': 'general',
            'key_points': []
        }
        
        prompt_lower = prompt.lower()
        
        # Extract tone
        tones = ['professional', 'casual', 'conversational', 'academic', 'friendly']
        for tone in tones:
            if tone in prompt_lower:
                requirements['tone'] = tone
                break
        
        # Extract platform
        platforms = ['linkedin', 'medium', 'wordpress', 'twitter', 'facebook']
        for platform in platforms:
            if platform in prompt_lower:
                requirements['platform'] = platform
                break
        
        return requirements
    
    def _generate_sections(self, topic: str, requirements: Dict, 
                          word_count: int, content_type: str) -> Dict[str, str]:
        """Generate content sections to fill templates."""
        
        # Calculate words per section based on total target
        num_sections = 10
        words_per_section = max(30, word_count // num_sections)
        
        sections = {
            'title': f"The Complete Guide to {topic.title()}",
            'hook': f"Did you know that {topic} is transforming how we work?",
            'topic': topic,
            'introduction': self._generate_paragraph(topic, 'introduction', words_per_section * 2),
            'summary': self._generate_paragraph(topic, 'summary', words_per_section),
            'background': self._generate_paragraph(topic, 'background', words_per_section * 2),
            'analysis': self._generate_paragraph(topic, 'analysis', words_per_section * 2),
            'point_1_title': f"Understanding {topic.title()}",
            'point_1_content': self._generate_paragraph(topic, 'key benefit', words_per_section * 2),
            'point_1': f"Key insight about {topic}",
            'point_1_detail': self._generate_paragraph(topic, 'detail', words_per_section),
            'point_2_title': f"Benefits of {topic.title()}",
            'point_2_content': self._generate_paragraph(topic, 'benefits', words_per_section * 2),
            'point_2': f"Important consideration for {topic}",
            'point_2_detail': self._generate_paragraph(topic, 'consideration', words_per_section),
            'point_3_title': f"Implementing {topic.title()}",
            'point_3_content': self._generate_paragraph(topic, 'implementation', words_per_section * 2),
            'point_3': f"Best practice for {topic}",
            'point_3_detail': self._generate_paragraph(topic, 'best practice', words_per_section),
            'finding_1': self._generate_paragraph(topic, 'finding 1', words_per_section),
            'finding_2': self._generate_paragraph(topic, 'finding 2', words_per_section),
            'finding_3': self._generate_paragraph(topic, 'finding 3', words_per_section),
            'best_practices': self._generate_list(topic, 'best practices', 5),
            'implications': self._generate_paragraph(topic, 'implications', words_per_section),
            'recommendations': self._generate_list(topic, 'recommendations', 4),
            'conclusion': self._generate_paragraph(topic, 'conclusion', words_per_section),
            'key_takeaway': f"Embracing {topic} can significantly improve outcomes and efficiency.",
            'cta': f"Ready to learn more about {topic}? Contact us to get started on your journey.",
            'references': "1. Industry Research Report 2024\n2. Expert Analysis Studies\n3. Best Practices Guide",
            'hashtags': f"#{topic.replace(' ', '')} #Innovation #Growth #Success #Leadership"
        }
        
        return sections
    
    def _generate_paragraph(self, topic: str, context: str, target_words: int) -> str:
        """Generate a paragraph with approximately target_words."""
        
        sentences = [
            f"When it comes to {topic}, understanding the {context} is essential for success.",
            f"Research has shown that organizations focusing on {topic} see significant improvements in their operations.",
            f"The importance of {context} in the context of {topic} cannot be overstated.",
            f"Industry experts recommend taking a strategic approach to {topic} implementation.",
            f"By carefully considering the {context}, professionals can maximize their results.",
            f"The landscape of {topic} continues to evolve, bringing new opportunities and challenges.",
            f"Successful implementation of {topic} strategies requires careful planning and execution.",
            f"Organizations that embrace {topic} often find themselves ahead of their competition.",
            f"The key to success lies in understanding how {context} relates to broader {topic} initiatives.",
            f"As we look to the future, {topic} will play an increasingly important role in our work.",
            f"Data-driven approaches to {topic} have proven particularly effective in recent years.",
            f"Collaboration and communication are essential when implementing {topic} strategies.",
            f"The benefits of focusing on {context} extend beyond immediate results.",
            f"Leading organizations are already seeing returns from their {topic} investments.",
            f"Understanding the nuances of {context} helps teams make better decisions.",
        ]
        
        # Build paragraph with enough words
        paragraph_parts = []
        current_words = 0
        sentence_index = 0
        
        while current_words < target_words and sentence_index < len(sentences) * 3:
            sentence = sentences[sentence_index % len(sentences)]
            paragraph_parts.append(sentence)
            current_words += len(sentence.split())
            sentence_index += 1
        
        return " ".join(paragraph_parts)
    
    def _generate_list(self, topic: str, context: str, items: int) -> str:
        """Generate a bullet point list."""
        list_items = [
            f"Establish clear objectives for your {topic} initiatives",
            f"Invest in training and development for team members",
            f"Measure and track progress using relevant metrics",
            f"Foster a culture of continuous improvement",
            f"Leverage technology to enhance {topic} outcomes",
            f"Build strong partnerships with stakeholders",
            f"Stay informed about industry trends and best practices",
            f"Create feedback loops to optimize your approach",
        ]
        
        return "\n".join([f"- {item}" for item in list_items[:items]])
    
    def _generate_raw_content(self, topic: str, requirements: Dict, word_count: int) -> str:
        """Generate raw content without template."""
        sections = []
        
        sections.append(f"# {topic.title()}: A Comprehensive Guide\n")
        sections.append(self._generate_paragraph(topic, 'introduction', word_count // 4))
        sections.append(f"\n## Key Insights\n")
        sections.append(self._generate_paragraph(topic, 'key insights', word_count // 4))
        sections.append(f"\n## Best Practices\n")
        sections.append(self._generate_list(topic, 'best practices', 5))
        sections.append(f"\n## Conclusion\n")
        sections.append(self._generate_paragraph(topic, 'conclusion', word_count // 4))
        
        return "\n".join(sections)


class LLMManager:
    """
    Manages LLM providers and selects the best available option.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.providers = {}
        self.logger = get_logger("LLMManager")
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers."""
        
        # Get LLM section from config (from settings.json)
        llm_config = self.config.get('llm', {})
        
        # Try to initialize each provider
        try:
            openai_config = llm_config.get('openai', {})
            openai_key = openai_config.get('api_key') or self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
            if openai_key:
                openai_model = openai_config.get('model', 'gpt-3.5-turbo')
                self.providers['openai'] = OpenAIProvider(api_key=openai_key, model=openai_model)
                self.logger.info(f"OpenAI provider initialized with model: {openai_model}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize OpenAI: {e}")
        
        try:
            anthropic_config = llm_config.get('anthropic', {})
            anthropic_key = anthropic_config.get('api_key') or self.config.get('anthropic_api_key') or os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                anthropic_model = anthropic_config.get('model', 'claude-3-sonnet-20240229')
                self.providers['anthropic'] = AnthropicProvider(api_key=anthropic_key, model=anthropic_model)
                self.logger.info(f"Anthropic provider initialized with model: {anthropic_model}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Anthropic: {e}")
        
        try:
            groq_config = llm_config.get('groq', {})
            groq_key = groq_config.get('api_key') or self.config.get('groq_api_key') or os.getenv('GROQ_API_KEY')
            if groq_key:
                groq_model = groq_config.get('model', 'llama-3.3-70b-versatile')
                self.providers['groq'] = GroqProvider(api_key=groq_key, model=groq_model)
                self.logger.info(f"Groq provider initialized with model: {groq_model}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Groq: {e}")
        
        try:
            ollama = OllamaProvider()
            if ollama.is_available():
                self.providers['ollama'] = ollama
                self.logger.info("Ollama provider initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Ollama: {e}")
        
        # Always add template provider as fallback
        self.providers['template'] = TemplateProvider()
        self.logger.info("Template provider initialized as fallback")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [name for name, provider in self.providers.items() if provider.is_available()]
    
    def get_best_provider(self) -> BaseLLMProvider:
        """Get the best available provider."""
        priority = ['groq', 'openai', 'anthropic', 'ollama', 'template']
        
        for provider_name in priority:
            if provider_name in self.providers and self.providers[provider_name].is_available():
                self.logger.info(f"Using provider: {provider_name}")
                return self.providers[provider_name]
        
        return self.providers['template']
    
    def generate(self, prompt: str, provider: Optional[str] = None, **kwargs) -> str:
        """
        Generate content using the specified or best available provider.
        
        Args:
            prompt: The generation prompt
            provider: Specific provider to use (optional)
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        if provider and provider in self.providers:
            selected_provider = self.providers[provider]
        else:
            selected_provider = self.get_best_provider()
        
        try:
            return selected_provider.generate(prompt, **kwargs)
        except Exception as e:
            self.logger.error(f"Generation failed with primary provider: {e}")
            
            # Fallback to template if other providers fail
            if 'template' in self.providers:
                self.logger.info("Falling back to template provider")
                return self.providers['template'].generate(prompt, **kwargs)
            
            raise
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers."""
        return {name: provider.is_available() for name, provider in self.providers.items()}


# Singleton instance
_llm_manager = None

def get_llm_manager(config: Optional[Dict[str, Any]] = None) -> LLMManager:
    """Get or create the LLM manager singleton."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager(config)
    return _llm_manager