"""
AI Content Orchestrator - Multi-agent content creation system.
"""

__version__ = "1.0.0"
__author__ = "AI Content Team"

from .orchestrator.workflow_manager import WorkflowManager
from .utils.config import Config
from .utils.logger import setup_logging

__all__ = ['WorkflowManager', 'Config', 'setup_logging']