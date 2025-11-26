"""
Main entry point for the AI Content Orchestrator system.

This script provides a command-line interface and demonstrates the usage
of the multi-agent content creation workflow.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.workflow_manager import WorkflowManager
from utils.config import Config
from utils.logger import setup_logging, get_logger

def create_sample_config():
    """Create sample configuration files."""
    config_dir = Path(__file__).parent / 'config'
    config_dir.mkdir(exist_ok=True)
    
    # Sample settings
    settings = {
        "system": {
            "log_level": "INFO",
            "log_file": "logs/orchestrator.log",
            "max_concurrent_agents": 3,
            "workflow_timeout": 300
        },
        "agents": {
            "research": {
                "enabled": True,
                "max_sources": 5,
                "wikipedia_limit": 3
            },
            "writer": {
                "enabled": True,
                "default_word_count": 1000
            },
            "humanizer": {
                "enabled": True,
                "aggressive_humanization": False
            }
        },
        "content_defaults": {
            "content_type": "blog_post",
            "target_audience": "general",
            "tone": "informative_engaging"
        }
    }
    
    # Sample API keys template
    api_keys_template = {
        "openai_api_key": "YOUR_OPENAI_API_KEY",
        "anthropic_api_key": "YOUR_ANTHROPIC_API_KEY", 
        "google_search_api_key": "YOUR_GOOGLE_SEARCH_API_KEY",
        "wordpress_username": "YOUR_WORDPRESS_USERNAME",
        "wordpress_password": "YOUR_WORDPRESS_PASSWORD",
        "wordpress_url": "YOUR_WORDPRESS_URL"
    }
    
    # Save files
    settings_file = config_dir / 'settings.json'
    api_keys_file = config_dir / 'api_keys.example.json'
    
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    with open(api_keys_file, 'w') as f:
        json.dump(api_keys_template, f, indent=2)
    
    print(f"Created sample configuration files:")
    print(f"  - {settings_file}")
    print(f"  - {api_keys_file}")
    print(f"\nCopy api_keys.example.json to api_keys.json and add your actual API keys.")

def run_workflow_cli():
    """Run workflow from command line arguments."""
    parser = argparse.ArgumentParser(description='AI Content Orchestrator')
    
    # Workflow parameters
    parser.add_argument('topic', help='Topic for content creation')
    parser.add_argument('--workflow-type', default='quick_post', 
                       choices=['full_content_creation', 'content_creation_only', 
                               'humanize_existing', 'quick_post'],
                       help='Type of workflow to run')
    parser.add_argument('--content-type', default='blog_post',
                       choices=['blog_post', 'article', 'social_post', 'guide'],
                       help='Type of content to create')
    parser.add_argument('--target-audience', default='general',
                       help='Target audience for the content')
    parser.add_argument('--tone', default='informative_engaging',
                       choices=['informative_engaging', 'professional', 'casual_engaging', 'instructional'],
                       help='Tone of the content')
    parser.add_argument('--word-count', type=int,
                       help='Target word count for the content')
    parser.add_argument('--output-file', 
                       help='File to save the generated content')
    parser.add_argument('--config-file',
                       help='Path to configuration file')
    parser.add_argument('--create-config', action='store_true',
                       help='Create sample configuration files and exit')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    # Initialize configuration
    config = None
    if args.config_file:
        with open(args.config_file, 'r') as f:
            config = json.load(f)
    
    config_manager = Config(config)
    setup_logging(config_manager.get('system', 'log_level', default='INFO'),
                  config_manager.get('system', 'log_file'))
    
    logger = get_logger("Main")
    
    # Initialize workflow manager
    workflow_manager = WorkflowManager(config_manager._config)
    
    # Prepare workflow parameters
    workflow_params = {
        'topic': args.topic,
        'workflow_type': args.workflow_type,
        'content_type': args.content_type,
        'target_audience': args.target_audience,
        'tone': args.tone
    }
    
    if args.word_count:
        workflow_params['word_count'] = args.word_count
    
    logger.info(f"Starting workflow for topic: {args.topic}")
    
    # Run the workflow
    try:
        result = workflow_manager.run_workflow(**workflow_params)
        
        if result['success']:
            logger.info("Workflow completed successfully!")
            
            # Display results
            output = result['output']
            print("\n" + "="*60)
            print("CONTENT CREATION RESULTS")
            print("="*60)
            
            if 'title' in output:
                print(f"\nTitle: {output['title']}")
            
            if 'meta_description' in output:
                print(f"\nMeta Description: {output['meta_description']}")
            
            if 'content' in output:
                print(f"\nContent:\n{output['content']}")
            
            # Display metrics
            if 'content_metrics' in output:
                metrics = output['content_metrics']
                print(f"\nContent Metrics:")
                print(f"  Word Count: {metrics.get('word_count', 'N/A')}")
                print(f"  Reading Time: {metrics.get('reading_time', 'N/A')} minutes")
                print(f"  Paragraphs: {metrics.get('paragraph_count', 'N/A')}")
            
            # Display humanization metrics if available
            if 'humanization_metrics' in output:
                h_metrics = output['humanization_metrics']
                print(f"\nHumanization Metrics:")
                print(f"  Original Score: {h_metrics.get('original_score', 'N/A')}")
                print(f"  Improved Score: {h_metrics.get('improved_score', 'N/A')}")
                print(f"  Improvement: +{h_metrics.get('improvement', 'N/A')}")
            
            # Save to file if requested
            if args.output_file:
                save_output_to_file(output, args.output_file)
                print(f"\nOutput saved to: {args.output_file}")
        
        else:
            logger.error(f"Workflow failed: {result.get('error', 'Unknown error')}")
            print(f"\nWorkflow failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nUnexpected error: {str(e)}")

def save_output_to_file(output: Dict[str, Any], file_path: str):
    """Save workflow output to a file."""
    output_path = Path(file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine file format based on extension
    if output_path.suffix.lower() == '.json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    elif output_path.suffix.lower() == '.md':
        with open(output_path, 'w', encoding='utf-8') as f:
            if 'title' in output:
                f.write(f"# {output['title']}\n\n")
            if 'meta_description' in output:
                f.write(f"*{output['meta_description']}*\n\n")
            if 'content' in output:
                f.write(output['content'])
    else:
        # Default to text format
        with open(output_path, 'w', encoding='utf-8') as f:
            if 'title' in output:
                f.write(f"Title: {output['title']}\n\n")
            if 'meta_description' in output:
                f.write(f"Meta Description: {output['meta_description']}\n\n")
            if 'content' in output:
                f.write(f"Content:\n{output['content']}")

def run_interactive_demo():
    """Run an interactive demonstration of the system."""
    print("AI Content Orchestrator - Interactive Demo")
    print("=" * 45)
    
    # Get user input
    topic = input("Enter a topic for content creation: ").strip()
    if not topic:
        print("Topic is required!")
        return
    
    print("\nContent Types:")
    print("1. Blog Post (default)")
    print("2. Article") 
    print("3. Social Media Post")
    print("4. Guide")
    
    content_type_choice = input("Select content type (1-4, default=1): ").strip()
    content_type_map = {
        '1': 'blog_post',
        '2': 'article', 
        '3': 'social_post',
        '4': 'guide'
    }
    content_type = content_type_map.get(content_type_choice, 'blog_post')
    
    print(f"\nWorkflow Types:")
    print("1. Quick Post (Research + Write + Humanize)")
    print("2. Content Creation Only (Research + Write + Humanize + Edit)")
    print("3. Full Content Creation (All agents including SEO and Publishing)")
    
    workflow_choice = input("Select workflow type (1-3, default=1): ").strip()
    workflow_map = {
        '1': 'quick_post',
        '2': 'content_creation_only',
        '3': 'full_content_creation'
    }
    workflow_type = workflow_map.get(workflow_choice, 'quick_post')
    
    # Initialize system
    print(f"\nInitializing AI Content Orchestrator...")
    config = Config()
    setup_logging(config.get('system', 'log_level', default='INFO'))
    
    workflow_manager = WorkflowManager(config._config)
    
    # Run workflow
    print(f"Creating {content_type} about '{topic}'...")
    print("This may take a few minutes...\n")
    
    try:
        result = workflow_manager.run_workflow(
            topic=topic,
            workflow_type=workflow_type,
            content_type=content_type
        )
        
        if result['success']:
            print("✅ Content creation completed successfully!")
            
            output = result['output']
            
            # Display results
            print(f"\n📝 Generated Content:")
            print(f"Title: {output.get('title', 'N/A')}")
            print(f"Word Count: {output.get('content_metrics', {}).get('word_count', 'N/A')}")
            print(f"Reading Time: {output.get('content_metrics', {}).get('reading_time', 'N/A')} minutes")
            
            if 'humanization_metrics' in output:
                h_metrics = output['humanization_metrics']
                print(f"Humanization Improvement: +{h_metrics.get('improvement', 0):.1f} points")
            
            # Ask if user wants to see the full content
            if input("\nWould you like to see the full content? (y/N): ").lower().startswith('y'):
                print(f"\n{'-'*60}")
                print(output.get('content', 'No content available'))
                print(f"{'-'*60}")
            
            # Ask if user wants to save the content
            save_choice = input("\nWould you like to save this content to a file? (y/N): ").lower()
            if save_choice.startswith('y'):
                filename = input("Enter filename (e.g., 'my_article.md'): ").strip()
                if filename:
                    save_output_to_file(output, filename)
                    print(f"Content saved to {filename}")
        
        else:
            print(f"❌ Content creation failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        # No command line arguments, run interactive demo
        run_interactive_demo()
    else:
        # Command line arguments provided, use CLI mode
        run_workflow_cli()

if __name__ == "__main__":
    main()