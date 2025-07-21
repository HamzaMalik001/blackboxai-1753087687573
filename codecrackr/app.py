from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import uuid
import threading
import time
import json
from datetime import datetime, timedelta

from config import Config
from services.repo_analyzer import RepoAnalyzer
from services.llm_service import LLMService
from services.tutorial_generator import TutorialGenerator
from utils.cleanup import cleanup_temp_files
from utils.github_utils import validate_github_url
from admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
app.register_blueprint(admin_bp, url_prefix='/admin')

# Initialize services
repo_analyzer = RepoAnalyzer()
llm_service = LLMService()
tutorial_generator = TutorialGenerator(llm_service)

# In-memory storage for processing status (use Redis in production)
processing_status = {}

@app.route('/')
def index():
    """Main page with GitHub URL input form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_repository():
    """Start repository analysis"""
    try:
        data = request.get_json()
        github_url = data.get('github_url', '').strip()
        
        if not github_url:
            return jsonify({'error': 'GitHub URL is required'}), 400
        
        # Validate GitHub URL
        if not validate_github_url(github_url):
            return jsonify({'error': 'Invalid GitHub URL format'}), 400
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize processing status
        processing_status[task_id] = {
            'status': 'started',
            'progress': 0,
            'message': 'Initializing analysis...',
            'github_url': github_url,
            'created_at': datetime.now(),
            'result': None,
            'error': None
        }
        
        # Start background processing
        thread = threading.Thread(
            target=process_repository_background,
            args=(task_id, github_url)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Repository analysis started'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to start analysis: {str(e)}'}), 500

@app.route('/status/<task_id>')
def get_status(task_id):
    """Get processing status"""
    if task_id not in processing_status:
        return jsonify({'error': 'Task not found'}), 404
    
    status = processing_status[task_id]
    
    # Clean up old completed tasks
    if status['status'] in ['completed', 'failed']:
        created_at = status['created_at']
        if datetime.now() - created_at > timedelta(hours=1):
            del processing_status[task_id]
            return jsonify({'error': 'Task expired'}), 404
    
    return jsonify({
        'task_id': task_id,
        'status': status['status'],
        'progress': status['progress'],
        'message': status['message'],
        'result': status['result'],
        'error': status['error']
    })

@app.route('/results/<task_id>')
def view_results(task_id):
    """View tutorial results"""
    if task_id not in processing_status:
        return render_template('error.html', error='Task not found'), 404
    
    status = processing_status[task_id]
    
    if status['status'] != 'completed':
        return render_template('error.html', error='Analysis not completed'), 400
    
    return render_template('results.html', 
                         task_id=task_id,
                         tutorial=status['result'],
                         github_url=status['github_url'])

@app.route('/export/<task_id>/<format>')
def export_tutorial(task_id, format):
    """Export tutorial in different formats"""
    if task_id not in processing_status:
        return jsonify({'error': 'Task not found'}), 404
    
    status = processing_status[task_id]
    
    if status['status'] != 'completed':
        return jsonify({'error': 'Analysis not completed'}), 400
    
    try:
        if format == 'markdown':
            return tutorial_generator.export_markdown(status['result'])
        elif format == 'pdf':
            return tutorial_generator.export_pdf(status['result'])
        else:
            return jsonify({'error': 'Unsupported format'}), 400
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

def process_repository_background(task_id, github_url):
    """Background task to process repository"""
    try:
        # Update status
        processing_status[task_id].update({
            'status': 'cloning',
            'progress': 10,
            'message': 'Cloning repository...'
        })
        
        # Clone and analyze repository
        repo_data = repo_analyzer.analyze_repository(github_url)
        
        processing_status[task_id].update({
            'status': 'analyzing',
            'progress': 30,
            'message': 'Analyzing code structure...'
        })
        
        # Generate tutorial using LLM
        processing_status[task_id].update({
            'status': 'generating',
            'progress': 60,
            'message': 'Generating tutorial with AI...'
        })
        
        tutorial = tutorial_generator.generate_tutorial(repo_data)
        
        processing_status[task_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Tutorial generated successfully!',
            'result': tutorial
        })
        
    except Exception as e:
        processing_status[task_id].update({
            'status': 'failed',
            'progress': 0,
            'message': f'Analysis failed: {str(e)}',
            'error': str(e)
        })

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500

# Cleanup task
def cleanup_background():
    """Background cleanup task"""
    while True:
        try:
            cleanup_temp_files()
            # Clean up old processing status
            current_time = datetime.now()
            expired_tasks = []
            for task_id, status in processing_status.items():
                if current_time - status['created_at'] > timedelta(hours=2):
                    expired_tasks.append(task_id)
            
            for task_id in expired_tasks:
                del processing_status[task_id]
                
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        time.sleep(3600)  # Run every hour

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_background)
cleanup_thread.daemon = True
cleanup_thread.start()

if __name__ == '__main__':
    # Ensure temp directory exists
    os.makedirs(app.config['TEMP_DIR'], exist_ok=True)
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=app.config['DEBUG']
    )
