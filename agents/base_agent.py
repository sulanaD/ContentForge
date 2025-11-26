"""
Base Agent class for the AI Content Orchestrator system.
All specialized agents inherit from this class.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from utils.logger import get_logger

class AgentInput(BaseModel):
    """Standard input format for all agents."""
    data: Dict[str, Any] = Field(..., description="Input data for the agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the input")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of input creation")
    source_agent: Optional[str] = Field(None, description="Previous agent in the workflow")

class AgentOutput(BaseModel):
    """Standard output format for all agents."""
    data: Dict[str, Any] = Field(..., description="Output data from the agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the output")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of output creation")
    agent_name: str = Field(..., description="Name of the agent that produced this output")
    status: str = Field(..., description="Status: success, error, warning")
    error_message: Optional[str] = Field(None, description="Error message if status is error")
    quality_score: Optional[float] = Field(None, description="Quality score (0-1) if applicable")

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize the base agent."""
        self.name = name
        self.config = config or {}
        self.logger = get_logger(self.name)
        self._setup_agent()
    
    def _setup_agent(self) -> None:
        """Setup agent-specific configurations."""
        self.logger.info(f"Initializing {self.name}")
        self.setup()
    
    @abstractmethod
    def setup(self) -> None:
        """Agent-specific setup. Override in subclasses."""
        pass
    
    @abstractmethod
    def process(self, input_data: AgentInput) -> AgentOutput:
        """Main processing method. Override in subclasses."""
        pass
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate input data. Override in subclasses for custom validation."""
        return True
    
    def validate_output(self, output_data: AgentOutput) -> bool:
        """Validate output data. Override in subclasses for custom validation."""
        return True
    
    def execute(self, input_data: Dict[str, Any], metadata: Dict[str, Any] = None) -> AgentOutput:
        """Execute the agent with error handling and validation."""
        try:
            # Create standardized input
            agent_input = AgentInput(
                data=input_data,
                metadata=metadata or {},
                source_agent=metadata.get('source_agent') if metadata else None
            )
            
            # Validate input
            if not self.validate_input(agent_input):
                return AgentOutput(
                    data={},
                    agent_name=self.name,
                    status="error",
                    error_message="Input validation failed"
                )
            
            self.logger.info(f"Processing with {self.name}")
            
            # Process the data
            output = self.process(agent_input)
            
            # Validate output
            if not self.validate_output(output):
                return AgentOutput(
                    data={},
                    agent_name=self.name,
                    status="error",
                    error_message="Output validation failed"
                )
            
            self.logger.info(f"Successfully processed with {self.name}")
            return output
            
        except Exception as e:
            self.logger.error(f"Error in {self.name}: {str(e)}")
            return AgentOutput(
                data={},
                agent_name=self.name,
                status="error",
                error_message=str(e)
            )
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities. Override in subclasses."""
        return []
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return configuration schema. Override in subclasses."""
        return {}