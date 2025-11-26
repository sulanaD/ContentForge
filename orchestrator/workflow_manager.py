"""
Workflow Manager for orchestrating multi-agent content creation process.

This manager coordinates the execution of specialized agents to create, 
humanize, optimize, and publish content automatically.

Includes QA Agent integration for content validation and automatic regeneration.
"""

import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import traceback
from utils.logger import get_logger
from utils.config import Config
from utils.llm_integration import get_llm_manager, LLMManager

# Import agents
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent
from agents.humanization_agent import HumanizationAgent
from agents.editor_agent import EditorAgent
from agents.seo_agent import SEOAgent
from agents.qa_agent import QAAgent
# from agents.publisher_agent import PublisherAgent

class WorkflowState:
    """Manages the state of the content creation workflow."""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.created_at = datetime.now()
        self.current_stage = "initialized"
        self.agent_outputs = {}
        self.errors = []
        self.metadata = {}
        self.final_output = None
        
    def update_stage(self, stage: str, agent_name: str, output: Dict[str, Any]):
        """Update the current workflow stage."""
        self.current_stage = stage
        self.agent_outputs[agent_name] = output
        
    def add_error(self, agent_name: str, error: str):
        """Add an error to the workflow state."""
        self.errors.append({
            'agent': agent_name,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
        
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the workflow execution."""
        return {
            'workflow_id': self.workflow_id,
            'created_at': self.created_at.isoformat(),
            'current_stage': self.current_stage,
            'agents_executed': list(self.agent_outputs.keys()),
            'error_count': len(self.errors),
            'has_final_output': self.final_output is not None
        }

class WorkflowManager:
    """Main orchestrator for the multi-agent content creation workflow."""
    
    # Maximum regeneration attempts to prevent infinite loops
    MAX_REGENERATION_ATTEMPTS = 3
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the workflow manager."""
        self.config = Config(config or {})
        self.logger = get_logger("WorkflowManager")
        
        # Initialize LLM Manager
        self.llm_manager = get_llm_manager(config)
        self.logger.info(f"LLM providers available: {self.llm_manager.get_available_providers()}")
        
        # Initialize agents
        self.agents = {
            'research': ResearchAgent('ResearchAgent', self.config.get('research', {})),
            'writer': WriterAgent('WriterAgent', self.config.get('writer', {})),
            'humanizer': HumanizationAgent('HumanizationAgent', self.config.get('humanizer', {})),
            'editor': EditorAgent('EditorAgent', self.config.get('editor', {})),
            'seo': SEOAgent('SEOAgent', self.config.get('seo', {})),
            'qa': QAAgent('QAAgent', self.config.get('qa', {})),
            # 'publisher': PublisherAgent('PublisherAgent', self.config.get('publisher', {}))
        }
        
        # Define workflow templates
        self.workflow_templates = {
            'full_content_creation': [
                'research', 'writer', 'humanizer', 'editor', 'seo', 'publisher'
            ],
            'content_creation_only': [
                'research', 'writer', 'humanizer', 'editor'
            ],
            'humanize_existing': [
                'humanizer', 'editor', 'seo'
            ],
            'quick_post': [
                'research', 'writer', 'humanizer'
            ]
        }
        
        # Track regeneration attempts per workflow
        self.regeneration_counts = {}
    
    def run_workflow(self, 
                    topic: str,
                    workflow_type: str = 'quick_post',
                    content_type: str = 'blog_post',
                    target_audience: str = 'general',
                    target_platform: str = None,
                    custom_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a complete content creation workflow with QA validation."""
        
        # Generate unique workflow ID
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        state = WorkflowState(workflow_id)
        
        # Track regeneration attempts for this workflow
        self.regeneration_counts[workflow_id] = 0
        
        self.logger.info(f"Starting workflow {workflow_id} for topic: {topic}")
        
        try:
            # Get workflow steps
            workflow_steps = self.workflow_templates.get(workflow_type, 
                                                       self.workflow_templates['quick_post'])
            
            # Initialize workflow input
            current_data = {
                'topic': topic,
                'content_type': content_type,
                'target_audience': target_audience,
                'target_platform': target_platform
            }
            
            # Add custom parameters
            if custom_parameters:
                current_data.update(custom_parameters)
            
            # Store original requirements for QA validation
            original_requirements = {
                'word_count': custom_parameters.get('word_count') if custom_parameters else None,
                'target_platform': target_platform,
                'tone': custom_parameters.get('tone', 'professional') if custom_parameters else 'professional',
                'content_type': content_type
            }
            
            # Execute workflow with QA validation loop
            current_data = self._execute_workflow_with_qa(
                workflow_steps, current_data, state, original_requirements
            )
            
            # Finalize workflow
            state.final_output = current_data
            state.current_stage = "completed"
            
            # Clean up regeneration tracking
            if workflow_id in self.regeneration_counts:
                del self.regeneration_counts[workflow_id]
            
            self.logger.info(f"Workflow {workflow_id} completed successfully")
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'output': current_data,
                'state_summary': state.get_summary(),
                'execution_log': state.agent_outputs
            }
            
        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            state.add_error("WorkflowManager", str(e))
            
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e),
                'state_summary': state.get_summary(),
                'execution_log': state.agent_outputs
            }
    
    def _execute_workflow_with_qa(self, workflow_steps: List[str], 
                                   current_data: Dict[str, Any],
                                   state: WorkflowState,
                                   original_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workflow steps with QA validation and automatic regeneration.
        
        The QA agent validates content after the main workflow completes.
        If requirements are not met, it triggers regeneration of content.
        """
        
        workflow_id = state.workflow_id
        
        while True:
            # Execute all workflow steps
            for step_name in workflow_steps:
                if step_name not in self.agents:
                    self.logger.warning(f"Agent {step_name} not available, skipping...")
                    continue
                
                current_data, success = self._execute_agent_step(
                    step_name, current_data, state
                )
                
                if not success:
                    self.logger.error(f"Workflow failed at step: {step_name}")
                    return current_data
            
            # Run QA validation after workflow completes
            qa_result = self._run_qa_validation(current_data, original_requirements, state)
            
            if qa_result['passed']:
                self.logger.info("QA validation passed - content meets requirements")
                current_data['qa_validation'] = qa_result
                return current_data
            
            # Check regeneration limit
            self.regeneration_counts[workflow_id] = self.regeneration_counts.get(workflow_id, 0) + 1
            
            if self.regeneration_counts[workflow_id] >= self.MAX_REGENERATION_ATTEMPTS:
                self.logger.warning(
                    f"Maximum regeneration attempts ({self.MAX_REGENERATION_ATTEMPTS}) reached. "
                    f"Returning best effort content."
                )
                current_data['qa_validation'] = qa_result
                current_data['qa_validation']['note'] = "Max regeneration attempts reached"
                return current_data
            
            # Log regeneration attempt
            self.logger.info(
                f"QA validation failed. Triggering regeneration "
                f"(attempt {self.regeneration_counts[workflow_id]}/{self.MAX_REGENERATION_ATTEMPTS})"
            )
            
            # Prepare data for regeneration with improved parameters
            current_data = self._prepare_regeneration_data(
                current_data, qa_result, original_requirements
            )
    
    def _run_qa_validation(self, current_data: Dict[str, Any], 
                          original_requirements: Dict[str, Any],
                          state: WorkflowState) -> Dict[str, Any]:
        """Run QA agent validation on the generated content."""
        
        try:
            qa_agent = self.agents.get('qa')
            if not qa_agent:
                self.logger.warning("QA Agent not available, skipping validation")
                return {'passed': True, 'reason': 'QA agent not available'}
            
            # Prepare QA input
            qa_input = {
                'content': current_data.get('content', ''),
                'title': current_data.get('title', ''),
                'requirements': {
                    'target_word_count': original_requirements.get('word_count'),
                    'target_platform': original_requirements.get('target_platform'),
                    'target_tone': original_requirements.get('tone', 'professional'),
                    'content_type': original_requirements.get('content_type', 'blog_post')
                }
            }
            
            # Execute QA validation
            result = qa_agent.execute(qa_input, {
                'workflow_id': state.workflow_id,
                'source_agent': state.current_stage
            })
            
            # Update state with QA results
            state.update_stage('qa_validation', 'qa', result.dict())
            
            if result.status == "success":
                qa_data = result.data
                
                # Determine if content passed validation
                passed = qa_data.get('validation_passed', False)
                overall_score = qa_data.get('overall_score', 0)
                
                # Also accept if score is above 70% even if some checks failed
                if not passed and overall_score >= 70:
                    self.logger.info(f"Content score {overall_score}% is acceptable, proceeding")
                    passed = True
                
                return {
                    'passed': passed,
                    'overall_score': overall_score,
                    'word_count_check': qa_data.get('word_count_check', {}),
                    'tone_check': qa_data.get('tone_check', {}),
                    'platform_check': qa_data.get('platform_check', {}),
                    'improvement_areas': qa_data.get('improvement_areas', []),
                    'recommendations': qa_data.get('recommendations', [])
                }
            else:
                self.logger.warning(f"QA validation failed: {result.error_message}")
                return {'passed': True, 'reason': 'QA validation error, proceeding anyway'}
                
        except Exception as e:
            self.logger.error(f"QA validation error: {str(e)}")
            return {'passed': True, 'reason': f'QA error: {str(e)}'}
    
    def _prepare_regeneration_data(self, current_data: Dict[str, Any],
                                   qa_result: Dict[str, Any],
                                   original_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for content regeneration based on QA feedback."""
        
        regeneration_data = current_data.copy()
        
        # Get improvement areas from QA result
        improvement_areas = qa_result.get('improvement_areas', [])
        
        # Adjust word count requirement
        word_count_check = qa_result.get('word_count_check', {})
        if not word_count_check.get('passed', True):
            target = original_requirements.get('word_count')
            if target:
                # Increase target slightly to ensure we meet minimum
                regeneration_data['word_count'] = int(target * 1.1)
                self.logger.info(f"Adjusting word count target to {regeneration_data['word_count']}")
        
        # Add QA feedback to help improve generation
        regeneration_data['qa_feedback'] = {
            'previous_score': qa_result.get('overall_score', 0),
            'improvement_areas': improvement_areas,
            'recommendations': qa_result.get('recommendations', [])
        }
        
        # Clear previous content to trigger fresh generation
        regeneration_data['content'] = ''
        regeneration_data['title'] = ''
        
        # Keep research data for context
        # research_data remains intact
        
        self.logger.info(f"Prepared regeneration data with feedback from QA")
        
        return regeneration_data
    
    def _execute_agent_step(self, agent_name: str, input_data: Dict[str, Any], 
                           state: WorkflowState) -> tuple[Dict[str, Any], bool]:
        """Execute a single agent step in the workflow."""
        
        try:
            self.logger.info(f"Executing {agent_name} agent")
            agent = self.agents[agent_name]
            
            # Prepare agent-specific input data
            agent_input = self._prepare_agent_input(agent_name, input_data, state)
            
            # Execute the agent
            result = agent.execute(agent_input, {
                'workflow_id': state.workflow_id,
                'source_agent': state.current_stage
            })
            
            # Update workflow state
            state.update_stage(agent_name, agent_name, result.dict())
            
            if result.status == "success":
                # Merge result data with current workflow data
                updated_data = self._merge_agent_output(agent_name, input_data, result.data)
                return updated_data, True
            else:
                state.add_error(agent_name, result.error_message or "Unknown error")
                return input_data, False
                
        except Exception as e:
            error_msg = f"Agent {agent_name} execution failed: {str(e)}"
            self.logger.error(error_msg)
            state.add_error(agent_name, error_msg)
            return input_data, False
    
    def _prepare_agent_input(self, agent_name: str, workflow_data: Dict[str, Any], 
                            state: WorkflowState) -> Dict[str, Any]:
        """Prepare input data specific to each agent type."""
        
        base_input = workflow_data.copy()
        
        if agent_name == 'research':
            return {
                'topic': workflow_data.get('topic', ''),
                'search_queries': workflow_data.get('search_queries', []),
                'source_types': workflow_data.get('source_types', ['web', 'wikipedia']),
                'depth': workflow_data.get('research_depth', 'moderate')
            }
            
        elif agent_name == 'writer':
            return {
                'research_data': workflow_data.get('research_data', {}),
                'content_type': workflow_data.get('content_type', 'blog_post'),
                'target_audience': workflow_data.get('target_audience', 'general'),
                'tone': workflow_data.get('tone', 'informative_engaging'),
                'word_count': workflow_data.get('word_count')
            }
            
        elif agent_name == 'humanizer':
            return {
                'content': workflow_data.get('content', ''),
                'title': workflow_data.get('title', ''),
                'content_type': workflow_data.get('content_type', 'blog_post')
            }
            
        elif agent_name == 'editor':
            return {
                'content': workflow_data.get('content', ''),
                'title': workflow_data.get('title', ''),
                'content_type': workflow_data.get('content_type', 'blog_post'),
                'style_guide': workflow_data.get('style_guide', 'default')
            }
            
        elif agent_name == 'seo':
            return {
                'content': workflow_data.get('content', ''),
                'title': workflow_data.get('title', ''),
                'meta_description': workflow_data.get('meta_description', ''),
                'target_keywords': workflow_data.get('target_keywords', []),
                'content_type': workflow_data.get('content_type', 'blog_post')
            }
            
        elif agent_name == 'publisher':
            return {
                'content': workflow_data.get('content', ''),
                'title': workflow_data.get('title', ''),
                'meta_description': workflow_data.get('meta_description', ''),
                'target_platform': workflow_data.get('target_platform', ''),
                'schedule_time': workflow_data.get('schedule_time'),
                'tags': workflow_data.get('tags', [])
            }
        
        elif agent_name == 'qa':
            return {
                'content': workflow_data.get('content', ''),
                'title': workflow_data.get('title', ''),
                'requirements': {
                    'target_word_count': workflow_data.get('word_count'),
                    'target_platform': workflow_data.get('target_platform'),
                    'target_tone': workflow_data.get('tone', 'professional'),
                    'content_type': workflow_data.get('content_type', 'blog_post')
                }
            }
        
        return base_input
    
    def _merge_agent_output(self, agent_name: str, current_data: Dict[str, Any], 
                           agent_output: Dict[str, Any]) -> Dict[str, Any]:
        """Merge agent output with current workflow data."""
        
        merged_data = current_data.copy()
        
        if agent_name == 'research':
            merged_data['research_data'] = agent_output
            
        elif agent_name == 'writer':
            merged_data.update({
                'title': agent_output.get('title', ''),
                'content': agent_output.get('content', ''),
                'meta_description': agent_output.get('meta_description', ''),
                'content_structure': agent_output.get('structure', {}),
                'content_metrics': agent_output.get('metrics', {})
            })
            
        elif agent_name == 'humanizer':
            merged_data.update({
                'content': agent_output.get('content', merged_data.get('content', '')),
                'title': agent_output.get('title', merged_data.get('title', '')),
                'humanization_metrics': {
                    'original_score': agent_output.get('original_human_score', 0),
                    'improved_score': agent_output.get('humanized_score', 0),
                    'improvement': agent_output.get('improvement', 0)
                }
            })
            
        elif agent_name == 'editor':
            merged_data.update({
                'content': agent_output.get('edited_content', merged_data.get('content', '')),
                'title': agent_output.get('edited_title', merged_data.get('title', '')),
                'editing_notes': agent_output.get('editing_notes', []),
                'grammar_score': agent_output.get('grammar_score', 0)
            })
            
        elif agent_name == 'seo':
            merged_data.update({
                'seo_optimized_content': agent_output.get('optimized_content', ''),
                'seo_title': agent_output.get('seo_title', ''),
                'seo_meta_description': agent_output.get('seo_meta_description', ''),
                'keywords': agent_output.get('keywords', []),
                'seo_score': agent_output.get('seo_score', 0),
                'seo_recommendations': agent_output.get('recommendations', [])
            })
            
        elif agent_name == 'publisher':
            merged_data.update({
                'publication_url': agent_output.get('publication_url', ''),
                'publication_id': agent_output.get('publication_id', ''),
                'publication_status': agent_output.get('status', ''),
                'scheduled_time': agent_output.get('scheduled_time', '')
            })
        
        return merged_data
    
    def run_custom_workflow(self, steps: List[str], initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a custom workflow with specified steps."""
        
        workflow_id = f"custom_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        state = WorkflowState(workflow_id)
        
        try:
            current_data = initial_data.copy()
            
            for step_name in steps:
                if step_name not in self.agents:
                    self.logger.warning(f"Agent {step_name} not available, skipping...")
                    continue
                
                current_data, success = self._execute_agent_step(step_name, current_data, state)
                
                if not success:
                    self.logger.error(f"Custom workflow failed at step: {step_name}")
                    break
            
            state.final_output = current_data
            state.current_stage = "completed"
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'output': current_data,
                'state_summary': state.get_summary()
            }
            
        except Exception as e:
            self.logger.error(f"Custom workflow {workflow_id} failed: {str(e)}")
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e),
                'state_summary': state.get_summary()
            }
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all available agents."""
        capabilities = {}
        for name, agent in self.agents.items():
            capabilities[name] = agent.get_capabilities()
        return capabilities
    
    def validate_workflow_input(self, workflow_type: str, input_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate input data for a specific workflow type."""
        errors = []
        
        # Common required fields
        if not input_data.get('topic'):
            errors.append("Topic is required")
        
        # Workflow-specific validation
        if workflow_type in ['full_content_creation', 'content_creation_only']:
            if not input_data.get('content_type'):
                errors.append("Content type is required for content creation workflows")
        
        if 'publisher' in self.workflow_templates.get(workflow_type, []):
            if not input_data.get('target_platform'):
                errors.append("Target platform is required for publishing workflows")
        
        return len(errors) == 0, errors
    
    def get_workflow_templates(self) -> Dict[str, List[str]]:
        """Get available workflow templates."""
        return self.workflow_templates.copy()
    
    def add_custom_agent(self, name: str, agent_instance):
        """Add a custom agent to the workflow manager."""
        self.agents[name] = agent_instance
        self.logger.info(f"Added custom agent: {name}")
    
    def remove_agent(self, name: str):
        """Remove an agent from the workflow manager."""
        if name in self.agents:
            del self.agents[name]
            self.logger.info(f"Removed agent: {name}")
        else:
            self.logger.warning(f"Agent {name} not found for removal")