"""
Logging utility for the AI Content Orchestrator system.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if hasattr(record, 'levelname') and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None) -> None:
    """Setup logging configuration for the entire system."""
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]
    )
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler if specified
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='a')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers = handlers
    
    # Suppress noisy third-party loggers
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)

class AgentLogger:
    """Specialized logger for agent operations."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = get_logger(f"Agent.{agent_name}")
        self.operation_start_time = None
    
    def start_operation(self, operation_name: str, details: str = None):
        """Log the start of an operation."""
        self.operation_start_time = datetime.now()
        message = f"Starting operation: {operation_name}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def end_operation(self, operation_name: str, success: bool = True, details: str = None):
        """Log the end of an operation with duration."""
        duration = ""
        if self.operation_start_time:
            elapsed = datetime.now() - self.operation_start_time
            duration = f" (Duration: {elapsed.total_seconds():.2f}s)"
        
        status = "completed successfully" if success else "failed"
        message = f"Operation {operation_name} {status}{duration}"
        if details:
            message += f" - {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_input(self, input_data: dict):
        """Log agent input data."""
        self.logger.debug(f"Input data keys: {list(input_data.keys())}")
        if 'topic' in input_data:
            self.logger.info(f"Processing topic: {input_data['topic']}")
    
    def log_output(self, output_data: dict):
        """Log agent output data."""
        self.logger.debug(f"Output data keys: {list(output_data.keys())}")
        if 'status' in output_data:
            self.logger.info(f"Agent status: {output_data['status']}")
    
    def log_quality_score(self, score: float):
        """Log quality score."""
        self.logger.info(f"Quality score: {score:.2f}")
    
    def log_processing_stats(self, stats: dict):
        """Log processing statistics."""
        for key, value in stats.items():
            self.logger.info(f"{key}: {value}")

class WorkflowLogger:
    """Specialized logger for workflow operations."""
    
    def __init__(self):
        self.logger = get_logger("Workflow")
        self.workflow_start_time = None
        self.current_workflow_id = None
    
    def start_workflow(self, workflow_id: str, workflow_type: str, topic: str):
        """Log workflow start."""
        self.current_workflow_id = workflow_id
        self.workflow_start_time = datetime.now()
        self.logger.info(f"Starting workflow {workflow_id} (Type: {workflow_type}, Topic: {topic})")
    
    def end_workflow(self, success: bool = True, details: str = None):
        """Log workflow completion."""
        duration = ""
        if self.workflow_start_time:
            elapsed = datetime.now() - self.workflow_start_time
            duration = f" (Total duration: {elapsed.total_seconds():.2f}s)"
        
        status = "completed successfully" if success else "failed"
        message = f"Workflow {self.current_workflow_id} {status}{duration}"
        if details:
            message += f" - {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_agent_execution(self, agent_name: str, success: bool, duration: float):
        """Log individual agent execution."""
        status = "succeeded" if success else "failed"
        self.logger.info(f"Agent {agent_name} {status} (Duration: {duration:.2f}s)")
    
    def log_workflow_progress(self, current_step: int, total_steps: int, current_agent: str):
        """Log workflow progress."""
        progress_percent = (current_step / total_steps) * 100
        self.logger.info(f"Workflow progress: {current_step}/{total_steps} ({progress_percent:.1f}%) - Executing {current_agent}")

# Initialize logging on import
setup_logging()