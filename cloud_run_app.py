"""
Cloud Run Flask Application
Handles HTTP requests from Cloud Scheduler
"""

import os
import logging
import json
from flask import Flask, request, jsonify
from cloud_scheduler import CloudVideoGenerator, cloud_run_handler, cleanup_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'tamil-video-generator'}), 200


@app.route('/generate', methods=['POST'])
def generate_video():
    """
    Generate and publish video
    Endpoint: POST /generate
    """
    try:
        logger.info("Received video generation request")
        
        # Load configuration from environment
        config = {
            'gcp_project_id': os.getenv('GCP_PROJECT_ID'),
            'gcp_bucket_name': os.getenv('GCP_BUCKET_NAME'),
            'gcp_credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            'youtube_credentials': os.getenv('YOUTUBE_CREDENTIALS', 'credentials.json'),
            'video_resolution': os.getenv('VIDEO_RESOLUTION', '1920x1080'),
            'video_fps': int(os.getenv('VIDEO_FPS', '30')),
            'video_duration_max': int(os.getenv('VIDEO_DURATION_MAX', '20')),
            'tts_voice': os.getenv('TTS_VOICE', 'ta-IN-Standard-A'),
            'tts_speaking_rate': float(os.getenv('TTS_SPEAKING_RATE', '1.0')),
            'database_path': os.getenv('DATABASE_PATH', '/tmp/videos.db')
        }
        
        # Validate configuration
        if not config['gcp_project_id'] or not config['gcp_bucket_name']:
            logger.error("Missing GCP configuration")
            return jsonify({
                'success': False,
                'error': 'Missing GCP configuration (GCP_PROJECT_ID, GCP_BUCKET_NAME)'
            }), 400
        
        # Generate video
        generator = CloudVideoGenerator(config)
        result = generator.generate_and_publish()
        
        status_code = 200 if result['success'] else 500
        logger.info(f"Video generation result: {result}")
        
        return jsonify(result), status_code
    
    except Exception as e:
        logger.error(f"Error generating video: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/cleanup', methods=['POST'])
def cleanup_old_files():
    """
    Clean up old files from Cloud Storage
    Endpoint: POST /cleanup
    """
    try:
        logger.info("Received cleanup request")
        
        # Get days parameter from request
        days = request.json.get('days', 14) if request.json else 14
        
        # Load configuration
        config = {
            'gcp_project_id': os.getenv('GCP_PROJECT_ID'),
            'gcp_bucket_name': os.getenv('GCP_BUCKET_NAME'),
            'gcp_credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            'youtube_credentials': os.getenv('YOUTUBE_CREDENTIALS', 'credentials.json'),
            'video_resolution': os.getenv('VIDEO_RESOLUTION', '1920x1080'),
            'video_fps': int(os.getenv('VIDEO_FPS', '30')),
            'video_duration_max': int(os.getenv('VIDEO_DURATION_MAX', '20')),
            'database_path': os.getenv('DATABASE_PATH', '/tmp/videos.db')
        }
        
        # Cleanup
        generator = CloudVideoGenerator(config)
        result = generator.cleanup_old_files(days=days)
        
        status_code = 200 if result['success'] else 500
        logger.info(f"Cleanup result: {result}")
        
        return jsonify(result), status_code
    
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def get_status():
    """
    Get bucket statistics
    Endpoint: GET /status
    """
    try:
        logger.info("Received status request")
        
        # Load configuration
        config = {
            'gcp_project_id': os.getenv('GCP_PROJECT_ID'),
            'gcp_bucket_name': os.getenv('GCP_BUCKET_NAME'),
            'gcp_credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            'youtube_credentials': os.getenv('YOUTUBE_CREDENTIALS', 'credentials.json'),
            'video_resolution': os.getenv('VIDEO_RESOLUTION', '1920x1080'),
            'video_fps': int(os.getenv('VIDEO_FPS', '30')),
            'video_duration_max': int(os.getenv('VIDEO_DURATION_MAX', '20')),
            'database_path': os.getenv('DATABASE_PATH', '/tmp/videos.db')
        }
        
        # Get stats
        generator = CloudVideoGenerator(config)
        stats = generator.get_bucket_stats()
        
        return jsonify({
            'success': True,
            'bucket_stats': stats,
            'config': {
                'project_id': config['gcp_project_id'],
                'bucket_name': config['gcp_bucket_name'],
                'video_resolution': config['video_resolution'],
                'video_fps': config['video_fps']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting status: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/config', methods=['GET'])
def get_config():
    """
    Get current configuration
    Endpoint: GET /config
    """
    config = {
        'gcp_project_id': os.getenv('GCP_PROJECT_ID', 'not-set'),
        'gcp_bucket_name': os.getenv('GCP_BUCKET_NAME', 'not-set'),
        'video_resolution': os.getenv('VIDEO_RESOLUTION', '1920x1080'),
        'video_fps': os.getenv('VIDEO_FPS', '30'),
        'video_duration_max': os.getenv('VIDEO_DURATION_MAX', '20'),
        'tts_voice': os.getenv('TTS_VOICE', 'ta-IN-Standard-A'),
        'tts_speaking_rate': os.getenv('TTS_SPEAKING_RATE', '1.0')
    }
    
    return jsonify({
        'success': True,
        'config': config
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'POST /generate',
            'POST /cleanup',
            'GET /status',
            'GET /config'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
