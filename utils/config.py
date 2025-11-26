"""
Configuration management for the AI Content Orchestrator system.
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from utils.logger import get_logger

@dataclass
class AgentConfig:
    """Configuration for individual agents."""
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    custom_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemConfig:
    """System-wide configuration."""
    log_level: str = "INFO"
    log_file: Optional[str] = None
    max_concurrent_agents: int = 3
    workflow_timeout: int = 300
    cache_enabled: bool = True
    cache_ttl: int = 3600

class Config:
    """Configuration manager for the AI Content Orchestrator."""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize configuration from dictionary or files."""
        self.logger = get_logger("Config")
        
        # Default configuration
        self._config = {
            'system': {
                'log_level': 'INFO',
                'log_file': None,
                'max_concurrent_agents': 3,
                'workflow_timeout': 300,
                'cache_enabled': True,
                'cache_ttl': 3600
            },
            'agents': {
                'research': {
                    'enabled': True,
                    'timeout': 60,
                    'max_sources': 5,
                    'wikipedia_limit': 3,
                    'request_timeout': 10
                },
                'writer': {
                    'enabled': True,
                    'timeout': 120,
                    'default_word_count': 1000,
                    'min_quality_score': 0.7
                },
                'humanizer': {
                    'enabled': True,
                    'timeout': 60,
                    'min_improvement_threshold': 5.0,
                    'aggressive_humanization': False
                },
                'editor': {
                    'enabled': True,
                    'timeout': 90,
                    'grammar_check': True,
                    'style_check': True,
                    'plagiarism_check': False
                },
                'seo': {
                    'enabled': True,
                    'timeout': 60,
                    'target_keyword_density': 1.5,
                    'min_seo_score': 80
                },
                'publisher': {
                    'enabled': False,  # Disabled by default for safety
                    'timeout': 120,
                    'auto_publish': False,
                    'supported_platforms': ['wordpress', 'medium', 'linkedin']
                }
            },
            'api_keys': {
                'openai_api_key': None,
                'anthropic_api_key': None,
                'google_search_api_key': None,
                'virustotal_api_key': None,
                'wordpress_username': None,
                'wordpress_password': None,
                'wordpress_url': None
            },
            'content_defaults': {
                'content_type': 'blog_post',
                'target_audience': 'general',
                'tone': 'informative_engaging',
                'word_count_range': [800, 2500],
                'include_images': False,
                'include_citations': True
            },
            'quality_thresholds': {
                'min_research_sources': 3,
                'min_content_quality': 0.7,
                'min_humanization_score': 60,
                'min_readability_score': 60,
                'min_seo_score': 75
            }
        }
        
        # Override with provided config
        if config_dict:
            self._merge_config(self._config, config_dict)
        
        # Load from configuration files
        self._load_from_files()
        
        # Load from environment variables
        self._load_from_env()
        
        self.logger.info("Configuration loaded successfully")
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _load_from_files(self) -> None:
        """Load configuration from JSON files."""
        config_dir = Path(__file__).parent.parent / 'config'
        
        # Load main settings
        settings_file = config_dir / 'settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    file_config = json.load(f)
                self._merge_config(self._config, file_config)
                self.logger.info(f"Loaded configuration from {settings_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load {settings_file}: {e}")
        
        # Load API keys (separate file for security)
        api_keys_file = config_dir / 'api_keys.json'
        if api_keys_file.exists():
            try:
                with open(api_keys_file, 'r') as f:
                    api_keys = json.load(f)
                self._config['api_keys'].update(api_keys)
                self.logger.info(f"Loaded API keys from {api_keys_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load {api_keys_file}: {e}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'ORCHESTRATOR_LOG_LEVEL': ('system', 'log_level'),
            'ORCHESTRATOR_LOG_FILE': ('system', 'log_file'),
            'OPENAI_API_KEY': ('api_keys', 'openai_api_key'),
            'ANTHROPIC_API_KEY': ('api_keys', 'anthropic_api_key'),
            'GOOGLE_SEARCH_API_KEY': ('api_keys', 'google_search_api_key'),
            'WORDPRESS_USERNAME': ('api_keys', 'wordpress_username'),
            'WORDPRESS_PASSWORD': ('api_keys', 'wordpress_password'),
            'WORDPRESS_URL': ('api_keys', 'wordpress_url'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._config[section][key] = value
                self.logger.debug(f"Loaded {env_var} from environment")
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value by key."""
        if key in self._config:
            return self._config[key]
        return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        self._config[key] = value
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        agents_config = self.get('agents', {})
        return agents_config.get(agent_name, {})
    
    def get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key with proper error handling."""
        api_keys = self.get('api_keys', {})
        api_key = api_keys.get(key_name)
        if not api_key:
            self.logger.warning(f"API key '{key_name}' not configured")
        return api_key
    
    def is_agent_enabled(self, agent_name: str) -> bool:
        """Check if an agent is enabled."""
        agents_config = self.get('agents', {})
        agent_config = agents_config.get(agent_name, {})
        return agent_config.get('enabled', True)
    
    def get_quality_thresholds(self) -> Dict[str, float]:
        """Get quality threshold settings."""
        return self.get('quality_thresholds', {})
    
    def get_content_defaults(self) -> Dict[str, Any]:
        """Get default content settings."""
        return self.get('content_defaults', {})
    
    def validate_configuration(self) -> tuple[bool, List[str]]:
        """Validate the current configuration."""
        errors = []
        
        # Check required API keys for enabled agents
        if self.is_agent_enabled('research'):
            if not self.get_api_key('google_search_api_key'):
                errors.append("Google Search API key required for research agent")
        
        if self.is_agent_enabled('publisher'):
            agents_config = self.get('agents', {})
            publisher_config = agents_config.get('publisher', {})
            platforms = publisher_config.get('supported_platforms', [])
            if 'wordpress' in platforms:
                if not all([
                    self.get_api_key('wordpress_username'),
                    self.get_api_key('wordpress_password'),
                    self.get_api_key('wordpress_url')
                ]):
                    errors.append("WordPress credentials required for publishing")
        
        # Check system configuration
        system_config = self.get('system', {})
        log_level = system_config.get('log_level')
        if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            errors.append(f"Invalid log level: {log_level}")
        
        # Check quality thresholds
        thresholds = self.get_quality_thresholds()
        for threshold_name, threshold_value in thresholds.items():
            if not isinstance(threshold_value, (int, float)) or threshold_value < 0:
                errors.append(f"Invalid quality threshold '{threshold_name}': {threshold_value}")
        
        return len(errors) == 0, errors
    
    def save_to_file(self, file_path: str) -> None:
        """Save current configuration to a file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            self.logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def export_config_template(self, file_path: str) -> None:
        """Export a configuration template with default values."""
        template = self._config.copy()
        
        # Remove sensitive data from template
        template['api_keys'] = {key: "YOUR_" + key.upper() for key in template['api_keys']}
        
        try:
            with open(file_path, 'w') as f:
                json.dump(template, f, indent=2)
            self.logger.info(f"Configuration template exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to export configuration template: {e}")
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(agents_enabled={sum(1 for agent in self._config['agents'] if self._config['agents'][agent].get('enabled', True))})"