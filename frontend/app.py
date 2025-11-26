"""
Flask Web Application for AI Workflow Orchestrator Frontend

This provides a modern web interface for the AI content creation system,
allowing users to easily configure workflows, monitor progress, and view results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import json
import uuid
from datetime import datetime
import threading
import time
from typing import Dict, Any, List

# Import our orchestrator system
from orchestrator.workflow_manager import WorkflowManager
from utils.logger import get_logger
from utils.config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai_orchestrator_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
workflow_manager = None
active_workflows = {}
logger = get_logger("WebApp")

def json_serializer(obj):
    """Custom JSON serializer to handle datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

def safe_emit(event, data):
    """Safely emit data with proper JSON serialization."""
    try:
        # Convert data to JSON-serializable format
        json_str = json.dumps(data, default=json_serializer)
        json_data = json.loads(json_str)
        socketio.emit(event, json_data)
    except Exception as e:
        logger.error(f"Error emitting {event}: {str(e)}")
        # Emit a simplified error message
        socketio.emit(event, {
            'workflow_id': data.get('workflow_id'),
            'status': 'error',
            'message': f'Serialization error: {str(e)}'
        })

def json_serializer(obj):
    """Custom JSON serializer to handle datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

def safe_emit(event, data):
    """Safely emit data with proper JSON serialization."""
    try:
        # Convert data to JSON-serializable format
        json_str = json.dumps(data, default=json_serializer)
        json_data = json.loads(json_str)
        socketio.emit(event, json_data)
    except Exception as e:
        logger.error(f"Error emitting {event}: {str(e)}")
        # Emit a simplified error message
        socketio.emit(event, {
            'workflow_id': data.get('workflow_id'),
            'status': 'error',
            'message': f'Serialization error: {str(e)}'
        })

def initialize_workflow_manager():
    """Initialize the workflow manager with default configuration."""
    global workflow_manager
    try:
        config = {
            'research': {
                'max_sources': 3,
                'include_references': True
            },
            'writer': {
                'min_word_count': 500,
                'tone': 'professional',
                'include_examples': True
            },
            'humanizer': {
                'target_score': 80,
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
                'target_keyword_density': 1.5,
                'min_content_length': 400,
                'ideal_content_length': 1200
            }
        }
        workflow_manager = WorkflowManager(config)
        logger.info("Workflow manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize workflow manager: {str(e)}")
        raise

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/workflow-types')
def get_workflow_types():
    """Get available workflow types."""
    return jsonify({
        'workflow_types': {
            'full_content_creation': {
                'name': 'Full Content Creation',
                'description': 'Complete pipeline: Research → Write → Humanize → Edit → SEO → Publish',
                'agents': ['research', 'writer', 'humanizer', 'editor', 'seo', 'publisher'],
                'estimated_time': '2-3 minutes'
            },
            'content_creation_only': {
                'name': 'Content Creation Only', 
                'description': 'Create and optimize content without publishing',
                'agents': ['research', 'writer', 'humanizer', 'editor'],
                'estimated_time': '1-2 minutes'
            },
            'humanize_existing': {
                'name': 'Humanize & Optimize',
                'description': 'Improve existing content with humanization, editing, and SEO',
                'agents': ['humanizer', 'editor', 'seo'],
                'estimated_time': '30-60 seconds'
            },
            'quick_post': {
                'name': 'Quick Post',
                'description': 'Fast content creation for social media or blogs',
                'agents': ['research', 'writer', 'humanizer'],
                'estimated_time': '1 minute'
            }
        }
    })

@app.route('/api/content-types')
def get_content_types():
    """Get available content types."""
    return jsonify({
        'content_types': {
            'blog_post': {
                'name': 'Blog Post',
                'description': 'Comprehensive blog articles with SEO optimization'
            },
            'article': {
                'name': 'Article',
                'description': 'In-depth informational articles'
            },
            'social_media': {
                'name': 'Social Media',
                'description': 'Short-form content for social platforms'
            },
            'newsletter': {
                'name': 'Newsletter',
                'description': 'Email newsletter content'
            },
            'guide': {
                'name': 'How-to Guide',
                'description': 'Step-by-step instructional content'
            },
            'listicle': {
                'name': 'Listicle',
                'description': 'List-based articles and guides'
            }
        }
    })

@app.route('/api/start-workflow', methods=['POST'])
def start_workflow():
    """Start a new content creation workflow."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['topic', 'workflow_type', 'content_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate workflow ID
        workflow_id = str(uuid.uuid4())
        
        # Prepare workflow parameters
        workflow_params = {
            'topic': data['topic'],
            'workflow_type': data['workflow_type'],
            'content_type': data['content_type'],
            'target_audience': data.get('target_audience', 'general'),
            'target_platform': data.get('target_platform'),
            'custom_parameters': {}
        }
        
        # Add SEO parameters if provided
        if data.get('focus_keyword'):
            workflow_params['custom_parameters']['focus_keyword'] = data['focus_keyword']
        if data.get('target_keywords'):
            workflow_params['custom_parameters']['target_keywords'] = data['target_keywords'].split(',')
        
        # Add advanced parameters
        if data.get('tone'):
            workflow_params['custom_parameters']['tone'] = data['tone']
        if data.get('word_count'):
            workflow_params['custom_parameters']['target_word_count'] = int(data['word_count'])
        
        # Store workflow info
        active_workflows[workflow_id] = {
            'id': workflow_id,
            'status': 'starting',
            'progress': 0,
            'current_agent': None,
            'start_time': datetime.now(),
            'parameters': workflow_params,
            'result': None,
            'error': None
        }
        
        # Start workflow in background thread
        thread = threading.Thread(
            target=run_workflow_background,
            args=(workflow_id, workflow_params)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'workflow_id': workflow_id,
            'message': 'Workflow started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting workflow: {str(e)}")
        return jsonify({'error': str(e)}), 500

def run_workflow_background(workflow_id: str, params: Dict[str, Any]):
    """Run workflow in background thread with real-time updates."""
    try:
        # Update status
        active_workflows[workflow_id]['status'] = 'running'
        safe_emit('workflow_update', {
            'workflow_id': workflow_id,
            'status': 'running',
            'message': 'Starting workflow...',
            'progress': 5
        })
        
        # Get workflow steps
        workflow_type = params['workflow_type']
        workflow_templates = {
            'full_content_creation': ['research', 'writer', 'humanizer', 'editor', 'seo', 'publisher'],
            'content_creation_only': ['research', 'writer', 'humanizer', 'editor'],
            'humanize_existing': ['humanizer', 'editor', 'seo'],
            'quick_post': ['research', 'writer', 'humanizer']
        }
        
        steps = workflow_templates.get(workflow_type, workflow_templates['quick_post'])
        total_steps = len(steps)
        
        # Run workflow
        result = workflow_manager.run_workflow(
            topic=params['topic'],
            workflow_type=workflow_type,
            content_type=params['content_type'],
            target_audience=params['target_audience'],
            target_platform=params.get('target_platform'),
            custom_parameters=params.get('custom_parameters', {})
        )
        
        if result['success']:
            active_workflows[workflow_id]['status'] = 'completed'
            active_workflows[workflow_id]['progress'] = 100
            active_workflows[workflow_id]['result'] = result
            active_workflows[workflow_id]['end_time'] = datetime.now()
            
            # Create a simplified result for emission (remove problematic objects)
            simplified_result = {
                'success': result['success'],
                'workflow_id': result['workflow_id'],
                'output': result.get('output', {})
            }
            
            safe_emit('workflow_update', {
                'workflow_id': workflow_id,
                'status': 'completed',
                'message': 'Workflow completed successfully!',
                'progress': 100,
                'result': simplified_result
            })
        else:
            active_workflows[workflow_id]['status'] = 'failed'
            active_workflows[workflow_id]['error'] = result.get('error', 'Unknown error')
            
            safe_emit('workflow_update', {
                'workflow_id': workflow_id,
                'status': 'failed',
                'message': f"Workflow failed: {result.get('error', 'Unknown error')}",
                'progress': 0
            })
            
    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed: {str(e)}")
        active_workflows[workflow_id]['status'] = 'failed'
        active_workflows[workflow_id]['error'] = str(e)
        
        safe_emit('workflow_update', {
            'workflow_id': workflow_id,
            'status': 'failed',
            'message': f'Workflow failed: {str(e)}',
            'progress': 0
        })

@app.route('/api/workflow/<workflow_id>')
def get_workflow_status(workflow_id):
    """Get status of a specific workflow."""
    if workflow_id not in active_workflows:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = active_workflows[workflow_id]
    return jsonify({
        'id': workflow['id'],
        'status': workflow['status'],
        'progress': workflow['progress'],
        'current_agent': workflow.get('current_agent'),
        'start_time': workflow['start_time'].isoformat(),
        'end_time': workflow.get('end_time').isoformat() if workflow.get('end_time') else None,
        'parameters': workflow['parameters'],
        'result': workflow.get('result'),
        'error': workflow.get('error')
    })

@app.route('/api/workflows')
def get_all_workflows():
    """Get all workflow statuses."""
    workflows = []
    for wf_id, workflow in active_workflows.items():
        workflows.append({
            'id': workflow['id'],
            'status': workflow['status'],
            'progress': workflow['progress'],
            'start_time': workflow['start_time'].isoformat(),
            'end_time': workflow.get('end_time').isoformat() if workflow.get('end_time') else None,
            'topic': workflow['parameters']['topic'],
            'workflow_type': workflow['parameters']['workflow_type']
        })
    
    # Sort by start time (newest first)
    workflows.sort(key=lambda x: x['start_time'], reverse=True)
    return jsonify({'workflows': workflows})

@app.route('/api/download-content/<workflow_id>')
def download_content(workflow_id):
    """Download generated content as markdown file."""
    if workflow_id not in active_workflows:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = active_workflows[workflow_id]
    if workflow['status'] != 'completed' or not workflow.get('result'):
        return jsonify({'error': 'Workflow not completed or no result available'}), 400
    
    result = workflow['result']
    output = result['output']
    
    # Create markdown content
    content = []
    
    if 'seo_title' in output:
        content.append(f"# {output['seo_title']}\n")
    elif 'title' in output:
        content.append(f"# {output['title']}\n")
    
    if 'seo_meta_description' in output:
        content.append(f"**Meta Description:** {output['seo_meta_description']}\n")
    
    if 'url_slug' in output:
        content.append(f"**URL Slug:** {output['url_slug']}\n")
    
    content.append("---\n")
    content.append(output.get('content', ''))
    
    markdown_content = '\n'.join(content)
    
    from flask import Response
    return Response(
        markdown_content,
        mimetype='text/markdown',
        headers={'Content-Disposition': f'attachment; filename=content_{workflow_id[:8]}.md'}
    )

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'message': 'Connected to AI Workflow Orchestrator'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info('Client disconnected')

if __name__ == '__main__':
    logger.info("Starting AI Workflow Orchestrator Web Application")
    
    # Initialize the workflow manager
    initialize_workflow_manager()
    
    # Start the web application
    logger.info("Web application starting on http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)