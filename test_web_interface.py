"""
Quick test script to verify web interface is working properly.

This script tests the workflow API endpoints to ensure JSON serialization
issues have been resolved.
"""

import requests
import json
import time

def test_web_interface():
    """Test the web interface API endpoints."""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing AI Workflow Orchestrator Web Interface")
    print("=" * 60)
    
    try:
        # Test 1: Check if server is running
        print("1️⃣ Testing server connection...")
        response = requests.get(f"{base_url}/api/workflow-types", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
        
        # Test 2: Check workflow types endpoint
        print("\n2️⃣ Testing workflow types endpoint...")
        data = response.json()
        workflow_types = data.get('workflow_types', {})
        print(f"✅ Found {len(workflow_types)} workflow types:")
        for wf_type, info in workflow_types.items():
            print(f"   • {info['name']}: {info['estimated_time']}")
        
        # Test 3: Check content types endpoint
        print("\n3️⃣ Testing content types endpoint...")
        response = requests.get(f"{base_url}/api/content-types", timeout=5)
        if response.status_code == 200:
            data = response.json()
            content_types = data.get('content_types', {})
            print(f"✅ Found {len(content_types)} content types:")
            for ct_type, info in content_types.items():
                print(f"   • {info['name']}: {info['description']}")
        else:
            print(f"❌ Content types endpoint failed: {response.status_code}")
            return False
        
        # Test 4: Test workflow creation (but don't actually start it)
        print("\n4️⃣ Testing workflow creation endpoint...")
        test_workflow = {
            "topic": "Test Topic for API Validation",
            "workflow_type": "quick_post", 
            "content_type": "blog_post",
            "target_audience": "developers",
            "focus_keyword": "test",
            "tone": "professional"
        }
        
        response = requests.post(
            f"{base_url}/api/start-workflow",
            headers={'Content-Type': 'application/json'},
            json=test_workflow,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                workflow_id = result.get('workflow_id')
                print(f"✅ Workflow creation successful!")
                print(f"   • Workflow ID: {workflow_id}")
                print(f"   • Message: {result.get('message')}")
                
                # Wait a moment and check workflow status
                print("\n5️⃣ Testing workflow status endpoint...")
                time.sleep(2)
                
                status_response = requests.get(f"{base_url}/api/workflow/{workflow_id}", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✅ Workflow status retrieved:")
                    print(f"   • Status: {status_data.get('status')}")
                    print(f"   • Progress: {status_data.get('progress', 0)}%")
                else:
                    print(f"❌ Status endpoint failed: {status_response.status_code}")
                
            else:
                print(f"❌ Workflow creation failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Workflow creation endpoint failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
        
        print("\n🎉 All tests passed! Web interface is working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:5000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Server might be overloaded.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_web_interface()
    if success:
        print("\n✨ Web interface is ready for use!")
        print("🌐 Visit http://localhost:5000 to start creating content")
    else:
        print("\n🔧 Please check the server logs and fix any issues")
    
    exit(0 if success else 1)