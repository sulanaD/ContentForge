"""Quick test of the humanization functionality."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_humanization():
    try:
        from agents.humanization_agent import HumanizationAgent
        from agents.base_agent import AgentInput
        
        # Test content
        robotic_text = "Furthermore, artificial intelligence represents significant advancement. Therefore, organizations should implement these solutions. Additionally, the benefits are substantial."
        
        print("Testing Humanization Agent...")
        print(f"Original: {robotic_text}")
        
        humanizer = HumanizationAgent('TestHumanizer')
        
        input_data = AgentInput(
            data={
                'content': robotic_text,
                'content_type': 'blog_post'
            }
        )
        
        result = humanizer.process(input_data)
        
        if result.status == "success":
            print(f"Humanized: {result.data.get('content', 'No content')}")
            print(f"Improvement: +{result.data.get('improvement', 0):.1f} points")
            return True
        else:
            print(f"Error: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_humanization()
    if success:
        print("✅ Humanization test passed!")
    else:
        print("❌ Humanization test failed!")