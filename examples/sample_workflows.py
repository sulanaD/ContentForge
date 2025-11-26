"""
Example usage of the AI Content Orchestrator system.

This file demonstrates various ways to use the orchestrator
for different content creation scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.workflow_manager import WorkflowManager
from utils.config import Config
from utils.logger import setup_logging
import json

def example_basic_workflow():
    """Example of a basic content creation workflow."""
    print("Example 1: Basic Content Creation Workflow")
    print("-" * 50)
    
    # Initialize the system
    config = Config()
    setup_logging(log_level='INFO')
    
    orchestrator = WorkflowManager()
    
    # Create a blog post about AI
    result = orchestrator.run_workflow(
        topic="The Future of Artificial Intelligence in Healthcare",
        workflow_type="quick_post",
        content_type="blog_post",
        target_audience="healthcare professionals"
    )
    
    if result['success']:
        output = result['output']
        print(f"✅ Success! Created content:")
        print(f"Title: {output.get('title', 'N/A')}")
        print(f"Word Count: {output.get('content_metrics', {}).get('word_count', 'N/A')}")
        
        # Show humanization improvement
        if 'humanization_metrics' in output:
            improvement = output['humanization_metrics'].get('improvement', 0)
            print(f"Humanization Improvement: +{improvement:.1f} points")
        
        print(f"\nFirst 200 characters:")
        content = output.get('content', '')
        print(f"{content[:200]}...")
        
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    return result

def example_custom_workflow():
    """Example of a custom workflow with specific steps."""
    print("\n\nExample 2: Custom Workflow")
    print("-" * 50)
    
    orchestrator = WorkflowManager()
    
    # Custom workflow: Research -> Write -> Humanize only
    custom_steps = ['research', 'writer', 'humanizer']
    
    initial_data = {
        'topic': "Benefits of Remote Work for Software Developers",
        'content_type': "article",
        'target_audience': "software developers",
        'tone': "professional",
        'word_count': 1200
    }
    
    result = orchestrator.run_custom_workflow(custom_steps, initial_data)
    
    if result['success']:
        output = result['output']
        print(f"✅ Custom workflow completed!")
        print(f"Steps executed: {' -> '.join(custom_steps)}")
        print(f"Final word count: {output.get('content_metrics', {}).get('word_count', 'N/A')}")
    else:
        print(f"❌ Custom workflow failed: {result.get('error')}")
    
    return result

def example_humanize_existing_content():
    """Example of humanizing existing content."""
    print("\n\nExample 3: Humanizing Existing Content")
    print("-" * 50)
    
    orchestrator = WorkflowManager()
    
    # Sample AI-generated content that needs humanization
    existing_content = """
    Artificial intelligence represents a significant technological advancement. 
    Furthermore, machine learning algorithms demonstrate considerable potential 
    for various applications. Therefore, organizations should consider implementing 
    AI solutions to enhance their operational efficiency. Additionally, the 
    integration of AI systems requires careful planning and substantial investment.
    """
    
    # Use humanize_existing workflow
    result = orchestrator.run_workflow(
        topic="AI Implementation",  # Topic for context
        workflow_type="humanize_existing",
        content_type="blog_post"
    )
    
    if result['success']:
        print("✅ Content humanization completed!")
        
        # In a real scenario, you'd pass the existing content to the humanizer
        # This is a demonstration of the workflow structure
        print("Original content would be transformed to be more natural and engaging.")
    
    return result

def example_social_media_post():
    """Example of creating social media content."""
    print("\n\nExample 4: Social Media Post Creation")
    print("-" * 50)
    
    orchestrator = WorkflowManager()
    
    result = orchestrator.run_workflow(
        topic="5 Python Tips for Beginners",
        workflow_type="quick_post",
        content_type="social_post",
        target_audience="beginner programmers",
        tone="casual_engaging"
    )
    
    if result['success']:
        output = result['output']
        print(f"✅ Social media post created!")
        print(f"Character count: {len(output.get('content', ''))}")
        print(f"\nContent preview:")
        print(f"{output.get('content', '')[:150]}...")
    
    return result

def example_workflow_validation():
    """Example of workflow input validation."""
    print("\n\nExample 5: Workflow Validation")
    print("-" * 50)
    
    orchestrator = WorkflowManager()
    
    # Test invalid input
    invalid_input = {
        'topic': '',  # Empty topic
        'content_type': 'invalid_type'
    }
    
    is_valid, errors = orchestrator.validate_workflow_input('full_content_creation', invalid_input)
    
    print(f"Validation result: {is_valid}")
    if not is_valid:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Test valid input
    valid_input = {
        'topic': 'Machine Learning Fundamentals',
        'content_type': 'article',
        'target_platform': 'wordpress'
    }
    
    is_valid, errors = orchestrator.validate_workflow_input('full_content_creation', valid_input)
    print(f"\nValid input validation: {is_valid}")

def example_agent_capabilities():
    """Example of checking agent capabilities."""
    print("\n\nExample 6: Agent Capabilities")
    print("-" * 50)
    
    orchestrator = WorkflowManager()
    
    capabilities = orchestrator.get_agent_capabilities()
    
    print("Available agents and their capabilities:")
    for agent_name, agent_capabilities in capabilities.items():
        print(f"\n{agent_name.upper()} Agent:")
        for capability in agent_capabilities:
            print(f"  - {capability}")

def save_example_output(result, filename):
    """Save example output to a file."""
    if result and result.get('success'):
        output_path = Path(__file__).parent / 'outputs' / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"Example output saved to: {output_path}")

def main():
    """Run all examples."""
    print("AI Content Orchestrator - Examples")
    print("=" * 50)
    
    # Run examples
    try:
        result1 = example_basic_workflow()
        save_example_output(result1, 'basic_workflow_output.json')
        
        result2 = example_custom_workflow()
        save_example_output(result2, 'custom_workflow_output.json')
        
        example_humanize_existing_content()
        
        result4 = example_social_media_post()
        save_example_output(result4, 'social_post_output.json')
        
        example_workflow_validation()
        
        example_agent_capabilities()
        
        print(f"\n{'='*50}")
        print("All examples completed!")
        print("Check the 'outputs' directory for saved results.")
        
    except Exception as e:
        print(f"Example execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()