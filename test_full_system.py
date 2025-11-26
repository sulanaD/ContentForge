"""
Comprehensive test for the complete AI Workflow Orchestrator with all agents.

This test demonstrates the full content creation pipeline including
Research, Writing, Humanization, Editing, and SEO optimization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.workflow_manager import WorkflowManager
from utils.logger import get_logger
import json

def test_full_workflow():
    """Test the complete workflow with all agents."""
    logger = get_logger("FullWorkflowTest")
    
    # Configuration for enhanced workflow
    config = {
        'research': {
            'max_sources': 3,
            'include_references': True
        },
        'writer': {
            'min_word_count': 800,
            'tone': 'informative',
            'include_examples': True
        },
        'humanizer': {
            'target_score': 85,
            'style': 'conversational',
            'add_personality': True
        },
        'editor': {
            'target_readability': 70,
            'style_guide': 'ap',
            'fix_grammar': True,
            'improve_flow': True
        },
        'seo': {
            'target_keyword_density': 2.0,
            'min_content_length': 500,
            'ideal_content_length': 1200
        }
    }
    
    # Initialize workflow manager
    manager = WorkflowManager(config)
    
    # Test scenarios
    test_scenarios = [
        {
            'topic': 'Benefits of Machine Learning in Healthcare',
            'workflow_type': 'full_content_creation',
            'content_type': 'blog_post',
            'target_audience': 'healthcare professionals',
            'custom_parameters': {
                'focus_keyword': 'machine learning healthcare',
                'target_keywords': ['AI in medicine', 'healthcare automation', 'medical AI', 'clinical decision support']
            }
        },
        {
            'topic': 'Sustainable Energy Solutions for Small Businesses',
            'workflow_type': 'content_creation_only',
            'content_type': 'article',
            'target_audience': 'small business owners',
            'custom_parameters': {
                'focus_keyword': 'sustainable energy business',
                'target_keywords': ['renewable energy', 'energy efficiency', 'green business', 'solar power']
            }
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"Running Test Scenario {i}: {scenario['topic']}")
        logger.info(f"{'='*80}")
        
        try:
            # Run the workflow
            result = manager.run_workflow(
                topic=scenario['topic'],
                workflow_type=scenario['workflow_type'],
                content_type=scenario['content_type'],
                target_audience=scenario['target_audience'],
                custom_parameters=scenario.get('custom_parameters', {})
            )
            
            if result['success']:
                logger.info("✅ Workflow completed successfully!")
                
                # Extract key metrics
                output = result['output']
                metrics = {
                    'workflow_id': result['workflow_id'],
                    'topic': scenario['topic'],
                    'workflow_type': scenario['workflow_type'],
                    'word_count': len(output.get('content', '').split()) if 'content' in output else 0,
                    'agents_executed': list(result['execution_log'].keys()),
                    'final_scores': {}
                }
                
                # Collect scores from each agent
                for agent_name, agent_output in result['execution_log'].items():
                    if isinstance(agent_output, dict) and 'quality_score' in agent_output:
                        metrics['final_scores'][agent_name] = agent_output['quality_score']
                
                # Special handling for specific agent outputs
                if 'humanizer' in result['execution_log']:
                    humanizer_data = result['execution_log']['humanizer']
                    if 'humanization_improvement' in humanizer_data.get('metadata', {}):
                        metrics['humanization_improvement'] = humanizer_data['metadata']['humanization_improvement']
                
                if 'editor' in result['execution_log']:
                    editor_data = result['execution_log']['editor']
                    if 'editing_score' in editor_data.get('data', {}):
                        metrics['editing_score'] = editor_data['data']['editing_score']
                        metrics['readability_improvement'] = editor_data.get('metadata', {}).get('readability_improvement', 0)
                
                if 'seo' in result['execution_log']:
                    seo_data = result['execution_log']['seo']
                    if 'seo_score' in seo_data.get('data', {}):
                        metrics['seo_score'] = seo_data['data']['seo_score']
                        metrics['keyword_density'] = seo_data.get('metadata', {}).get('keyword_density', {})
                
                results.append({
                    'success': True,
                    'metrics': metrics,
                    'full_output': output
                })
                
                # Display detailed results
                print_detailed_results(scenario, result, metrics)
                
            else:
                logger.error("❌ Workflow failed!")
                results.append({
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'topic': scenario['topic']
                })
                
        except Exception as e:
            logger.error(f"❌ Test scenario {i} failed with exception: {str(e)}")
            results.append({
                'success': False,
                'error': str(e),
                'topic': scenario['topic']
            })
    
    # Generate comprehensive test report
    generate_test_report(results, logger)
    
    return results

def print_detailed_results(scenario, result, metrics):
    """Print detailed results for a workflow execution."""
    print(f"\n🎯 DETAILED RESULTS FOR: {scenario['topic']}")
    print(f"{'='*60}")
    
    # Basic metrics
    print(f"📊 Basic Metrics:")
    print(f"   • Word Count: {metrics['word_count']} words")
    print(f"   • Agents Executed: {', '.join(metrics['agents_executed'])}")
    print(f"   • Workflow Type: {scenario['workflow_type']}")
    
    # Quality scores
    print(f"\n⭐ Quality Scores:")
    for agent, score in metrics['final_scores'].items():
        print(f"   • {agent.title()}: {score:.2f}")
    
    # Special improvements
    if 'humanization_improvement' in metrics:
        print(f"\n🎭 Humanization Analysis:")
        print(f"   • Improvement: +{metrics['humanization_improvement']:.1f} points")
    
    if 'editing_score' in metrics:
        print(f"\n✏️ Editing Analysis:")
        print(f"   • Editing Score: {metrics['editing_score']:.1f}/100")
        if 'readability_improvement' in metrics:
            print(f"   • Readability Improvement: +{metrics['readability_improvement']:.1f} points")
    
    if 'seo_score' in metrics:
        print(f"\n🔍 SEO Analysis:")
        print(f"   • SEO Score: {metrics['seo_score']:.1f}/100")
        if 'keyword_density' in metrics:
            kd = metrics['keyword_density']
            if isinstance(kd, dict) and 'focus_keyword' in kd:
                print(f"   • Focus Keyword: '{kd['focus_keyword']}' ({kd.get('density', 0):.1f}%)")
    
    # Content preview
    output = result['output']
    if 'content' in output:
        content = output['content']
        preview = content[:200] + "..." if len(content) > 200 else content
        print(f"\n📄 Content Preview:")
        print(f"   {preview}")
    
    # SEO elements
    if 'seo_title' in output:
        print(f"\n🏷️ SEO Elements:")
        print(f"   • SEO Title: {output['seo_title']}")
        if 'seo_meta_description' in output:
            print(f"   • Meta Description: {output['seo_meta_description']}")
        if 'url_slug' in output:
            print(f"   • URL Slug: {output['url_slug']}")

def generate_test_report(results, logger):
    """Generate a comprehensive test report."""
    logger.info(f"\n{'='*80}")
    logger.info("COMPREHENSIVE TEST REPORT")
    logger.info(f"{'='*80}")
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests
    
    logger.info(f"📈 Overall Statistics:")
    logger.info(f"   • Total Tests: {total_tests}")
    logger.info(f"   • Successful: {successful_tests} ({(successful_tests/total_tests)*100:.1f}%)")
    logger.info(f"   • Failed: {failed_tests} ({(failed_tests/total_tests)*100:.1f}%)")
    
    if successful_tests > 0:
        # Calculate average metrics
        avg_word_count = sum(r['metrics']['word_count'] for r in results if r['success']) / successful_tests
        
        # Collect all quality scores
        all_scores = []
        for result in results:
            if result['success']:
                all_scores.extend(result['metrics']['final_scores'].values())
        
        avg_quality_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        logger.info(f"\n📊 Performance Metrics:")
        logger.info(f"   • Average Word Count: {avg_word_count:.0f} words")
        logger.info(f"   • Average Quality Score: {avg_quality_score:.2f}")
        
        # Agent-specific metrics
        agent_performance = {}
        for result in results:
            if result['success']:
                for agent, score in result['metrics']['final_scores'].items():
                    if agent not in agent_performance:
                        agent_performance[agent] = []
                    agent_performance[agent].append(score)
        
        logger.info(f"\n🎯 Agent Performance:")
        for agent, scores in agent_performance.items():
            avg_score = sum(scores) / len(scores)
            logger.info(f"   • {agent.title()}: {avg_score:.2f} (across {len(scores)} tests)")
    
    # List any failures
    if failed_tests > 0:
        logger.info(f"\n❌ Failed Tests:")
        for result in results:
            if not result['success']:
                logger.info(f"   • {result['topic']}: {result['error']}")
    
    logger.info(f"\n{'='*80}")
    
    # Save detailed report to file
    save_test_report(results)

def save_test_report(results):
    """Save detailed test report to JSON file."""
    report_data = {
        'test_execution_time': str(datetime.now()),
        'total_tests': len(results),
        'successful_tests': sum(1 for r in results if r['success']),
        'results': results
    }
    
    try:
        with open('test_results_full_workflow.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Detailed test report saved to: test_results_full_workflow.json")
    except Exception as e:
        print(f"⚠️ Could not save test report: {str(e)}")

if __name__ == "__main__":
    from datetime import datetime
    
    print("🚀 Starting Comprehensive AI Workflow Orchestrator Test")
    print(f"Started at: {datetime.now()}")
    print("="*80)
    
    try:
        results = test_full_workflow()
        
        print(f"\n✅ Test suite completed!")
        print(f"Results: {sum(1 for r in results if r['success'])}/{len(results)} tests passed")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()