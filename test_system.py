"""
Test script for the AI Content Orchestrator system.

This script demonstrates the system functionality and provides
a way to test the humanization capabilities.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.workflow_manager import WorkflowManager
from utils.config import Config
from utils.logger import setup_logging, get_logger

def test_humanization_agent():
    """Test the humanization agent with sample AI-generated content."""
    print("Testing Humanization Agent")
    print("=" * 40)
    
    # Sample robotic AI content
    robotic_content = """
    Artificial intelligence represents a significant technological advancement that offers numerous benefits. 
    Furthermore, machine learning algorithms demonstrate considerable potential for enhancing business operations. 
    Therefore, organizations should consider implementing AI solutions to improve efficiency. Additionally, 
    the integration of these systems requires careful planning and substantial investment. Moreover, the 
    benefits include automated processes and improved decision-making capabilities. However, organizations 
    must also consider the challenges associated with implementation. Subsequently, proper training and 
    change management become essential components of successful adoption.
    """
    
    # Initialize system
    config = Config()
    setup_logging(log_level='INFO')
    logger = get_logger("Test")
    
    try:
        # Import and test humanization agent directly
        from agents.humanization_agent import HumanizationAgent
        from agents.base_agent import AgentInput
        
        humanizer = HumanizationAgent('TestHumanizer')
        
        # Prepare input
        agent_input = AgentInput(
            data={
                'content': robotic_content,
                'title': 'The Benefits of Artificial Intelligence Implementation',
                'content_type': 'blog_post'
            }
        )
        
        # Process the content
        logger.info("Processing content with humanization agent...")
        result = humanizer.process(agent_input)
        
        if result.status == "success":
            print("✅ Humanization successful!")
            print(f"\nOriginal Human Score: {result.data.get('original_human_score', 'N/A')}")
            print(f"Humanized Score: {result.data.get('humanized_score', 'N/A')}")
            print(f"Improvement: +{result.data.get('improvement', 'N/A')}")
            
            print(f"\nOriginal Content (first 200 chars):")
            print(f"{robotic_content[:200]}...")
            
            print(f"\nHumanized Content (first 200 chars):")
            humanized = result.data.get('content', '')
            print(f"{humanized[:200]}...")
            
            # Show processing stats
            metadata = result.metadata or {}
            processing_stats = metadata.get('processing_stats', {})
            print(f"\nProcessing Statistics:")
            print(f"  Sentences Modified: {processing_stats.get('sentences_modified', 0)}")
            print(f"  Phrases Added: {processing_stats.get('phrases_added', 0)}")
            print(f"  Transitions Improved: {processing_stats.get('transitions_improved', 0)}")
            
            return humanized
        else:
            print(f"❌ Humanization failed: {result.error_message}")
            return None
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}")
        return None

def test_full_workflow():
    """Test the complete workflow with a simple topic."""
    print("\n\nTesting Full Workflow")
    print("=" * 40)
    
    config = Config()
    setup_logging(log_level='INFO')
    logger = get_logger("FullWorkflowTest")
    
    try:
        orchestrator = WorkflowManager()
        
        logger.info("Starting full workflow test...")
        
        result = orchestrator.run_workflow(
            topic="Benefits of Python Programming for Beginners",
            workflow_type="quick_post",
            content_type="blog_post",
            target_audience="beginner programmers"
        )
        
        if result['success']:
            output = result['output']
            print("✅ Full workflow completed successfully!")
            
            # Display results
            print(f"\nGenerated Content Summary:")
            print(f"  Title: {output.get('title', 'N/A')}")
            
            # Content metrics
            metrics = output.get('content_metrics', {})
            print(f"  Word Count: {metrics.get('word_count', 'N/A')}")
            print(f"  Reading Time: {metrics.get('reading_time', 'N/A')} minutes")
            print(f"  Paragraphs: {metrics.get('paragraph_count', 'N/A')}")
            
            # Humanization metrics
            h_metrics = output.get('humanization_metrics', {})
            if h_metrics:
                print(f"\n  Humanization Results:")
                print(f"    Original Score: {h_metrics.get('original_score', 'N/A')}")
                print(f"    Improved Score: {h_metrics.get('improved_score', 'N/A')}")
                print(f"    Improvement: +{h_metrics.get('improvement', 'N/A')}")
            
            # Show workflow execution details
            exec_log = result.get('execution_log', {})
            print(f"\n  Agents Executed:")
            for agent_name in exec_log.keys():
                print(f"    - {agent_name}")
            
            return True
        else:
            print(f"❌ Full workflow failed: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"Full workflow test failed: {str(e)}")
        print(f"❌ Full workflow test failed: {str(e)}")
        return False

def test_agent_capabilities():
    """Test agent capability reporting."""
    print("\n\nTesting Agent Capabilities")
    print("=" * 40)
    
    try:
        orchestrator = WorkflowManager()
        capabilities = orchestrator.get_agent_capabilities()
        
        print("Available Agents and Capabilities:")
        for agent_name, agent_caps in capabilities.items():
            print(f"\n{agent_name.upper()}:")
            for cap in agent_caps:
                print(f"  • {cap}")
        
        return True
    except Exception as e:
        print(f"❌ Capability test failed: {str(e)}")
        return False

def demonstrate_humanization_techniques():
    """Demonstrate specific humanization techniques."""
    print("\n\nDemonstrating Humanization Techniques")
    print("=" * 50)
    
    examples = [
        {
            'name': 'Formal Language Replacement',
            'input': 'Furthermore, the implementation provides significant benefits. Therefore, we recommend adoption.',
            'technique': 'Replaces formal connectors with casual alternatives'
        },
        {
            'name': 'Conversational Elements',
            'input': 'Machine learning algorithms process data efficiently.',
            'technique': 'Adds conversational starters and questions'
        },
        {
            'name': 'Personal Touches',
            'input': 'This approach works well in most scenarios.',
            'technique': 'Adds personal experience phrases'
        }
    ]
    
    try:
        from agents.humanization_agent import HumanizationAgent
        from agents.base_agent import AgentInput
        
        humanizer = HumanizationAgent('DemoHumanizer')
        
        for example in examples:
            print(f"\n{example['name']}:")
            print(f"Technique: {example['technique']}")
            print(f"Input: {example['input']}")
            
            # Process the example
            agent_input = AgentInput(
                data={
                    'content': example['input'],
                    'content_type': 'blog_post'
                }
            )
            
            result = humanizer.process(agent_input)
            
            if result.status == "success":
                humanized = result.data.get('content', '')
                print(f"Output: {humanized}")
                improvement = result.data.get('improvement', 0)
                print(f"Improvement: +{improvement:.1f} points")
            else:
                print("Failed to process example")
    
    except Exception as e:
        print(f"❌ Demonstration failed: {str(e)}")

def run_performance_test():
    """Run a basic performance test."""
    print("\n\nPerformance Test")
    print("=" * 40)
    
    import time
    
    try:
        start_time = time.time()
        
        # Test with a medium-length content piece
        test_content = """
        Cloud computing has revolutionized the way businesses operate. Furthermore, 
        it provides scalable solutions for data storage and processing. Therefore, 
        many organizations are migrating their infrastructure to cloud platforms. 
        Additionally, this transition offers cost savings and improved flexibility. 
        However, security considerations must be carefully evaluated before implementation.
        """ * 3  # Repeat to make it longer
        
        from agents.humanization_agent import HumanizationAgent
        from agents.base_agent import AgentInput
        
        humanizer = HumanizationAgent('PerfTestHumanizer')
        
        agent_input = AgentInput(
            data={
                'content': test_content,
                'content_type': 'article'
            }
        )
        
        result = humanizer.process(agent_input)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if result.status == "success":
            word_count = len(test_content.split())
            words_per_second = word_count / processing_time
            
            print(f"✅ Performance test completed!")
            print(f"  Processing Time: {processing_time:.2f} seconds")
            print(f"  Word Count: {word_count}")
            print(f"  Processing Speed: {words_per_second:.1f} words/second")
            print(f"  Improvement: +{result.data.get('improvement', 0):.1f} points")
        else:
            print(f"❌ Performance test failed: {result.error_message}")
    
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")

def main():
    """Run all tests."""
    print("AI Content Orchestrator - Test Suite")
    print("=" * 50)
    
    # Run individual tests
    test_results = []
    
    print("\n1. Testing Humanization Agent...")
    humanized_content = test_humanization_agent()
    test_results.append(humanized_content is not None)
    
    print("\n2. Testing Full Workflow...")
    workflow_success = test_full_workflow()
    test_results.append(workflow_success)
    
    print("\n3. Testing Agent Capabilities...")
    cap_success = test_agent_capabilities()
    test_results.append(cap_success)
    
    print("\n4. Demonstrating Humanization Techniques...")
    demonstrate_humanization_techniques()
    
    print("\n5. Running Performance Test...")
    run_performance_test()
    
    # Summary
    successful_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests Passed: {successful_tests}/{total_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! The system is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    print(f"\nTo run the full system:")
    print(f"  python main.py")
    print(f"  or")
    print(f"  python main.py \"Your Topic Here\" --workflow-type quick_post")

if __name__ == "__main__":
    main()