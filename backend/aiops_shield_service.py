"""
AIOpsShield HTTP Service
Mission Critical - Production Grade

Provides HTTP API for telemetry sanitization.
Used by n8n for real-time log processing.

Author: Jaime Novoa
Status: PRODUCTION READY
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiops_shield import get_shield

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for n8n

# Initialize AIOpsShield (strict mode for production)
shield = get_shield(strict_mode=True)

logger.info("AIOpsShield HTTP Service starting...")


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    
    Returns:
        200: Service is healthy
    """
    return jsonify({
        'status': 'healthy',
        'service': 'aiops-shield',
        'version': '1.0.0'
    }), 200


@app.route('/sanitize', methods=['POST'])
def sanitize():
    """
    Sanitize log entry.
    
    Request body: JSON log entry
    {
        "timestamp": "2025-12-23T10:00:00Z",
        "level": "INFO",
        "service": "web-api",
        "message": "Log message"
    }
    
    Response:
    {
        "sanitized_log": {...},
        "report": {...},
        "status": "success"
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'status': 'error'
            }), 400
        
        log_entry = request.json
        
        if not log_entry:
            return jsonify({
                'error': 'Empty request body',
                'status': 'error'
            }), 400
        
        # Process through AIOpsShield
        logger.debug(f"Processing log entry: {log_entry.get('service', 'unknown')}")
        
        sanitized, report = shield.process(log_entry)
        
        # Log blocked threats
        if sanitized.get('security_flag') == 'BLOCKED':
            logger.warning(
                f"BLOCKED THREAT: {report.threat_level.value} - "
                f"Patterns: {report.patterns_detected}"
            )
        
        return jsonify({
            'sanitized_log': sanitized,
            'report': report.to_dict(),
            'status': 'success'
        }), 200
    
    except Exception as e:
        logger.error(f"Sanitization error: {e}", exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/sanitize/batch', methods=['POST'])
def sanitize_batch():
    """
    Sanitize multiple log entries in batch.
    
    Request body: Array of JSON log entries
    [
        {"level": "INFO", "message": "Log 1"},
        {"level": "ERROR", "message": "Log 2"}
    ]
    
    Response:
    {
        "results": [...],
        "status": "success",
        "summary": {...}
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'status': 'error'
            }), 400
        
        log_entries = request.json
        
        if not isinstance(log_entries, list):
            return jsonify({
                'error': 'Request body must be an array',
                'status': 'error'
            }), 400
        
        results = []
        blocked_count = 0
        sanitized_count = 0
        passed_count = 0
        
        for log_entry in log_entries:
            sanitized, report = shield.process(log_entry)
            
            results.append({
                'sanitized_log': sanitized,
                'report': report.to_dict()
            })
            
            # Count by security flag
            flag = sanitized.get('security_flag')
            if flag == 'BLOCKED':
                blocked_count += 1
            elif flag == 'SANITIZED':
                sanitized_count += 1
            else:
                passed_count += 1
        
        return jsonify({
            'results': results,
            'status': 'success',
            'summary': {
                'total': len(log_entries),
                'blocked': blocked_count,
                'sanitized': sanitized_count,
                'passed': passed_count
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Batch sanitization error: {e}", exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/stats', methods=['GET'])
def stats():
    """
    Get shield statistics.
    
    Returns:
        Statistics about processed logs
    """
    try:
        return jsonify(shield.get_stats()), 200
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/config', methods=['GET'])
def config():
    """
    Get current shield configuration.
    
    Returns:
        Configuration parameters
    """
    return jsonify({
        'strict_mode': shield.strict_mode,
        'max_message_length': shield.MAX_MESSAGE_LENGTH,
        'max_field_count': shield.MAX_FIELD_COUNT,
        'valid_log_levels': list(shield.VALID_LOG_LEVELS),
        'critical_patterns_count': len(shield.CRITICAL_PATTERNS),
        'suspicious_patterns_count': len(shield.SUSPICIOUS_PATTERNS)
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500


if __name__ == '__main__':
    # Production configuration
    import argparse
    
    parser = argparse.ArgumentParser(description='AIOpsShield HTTP Service')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    logger.info(f"Starting AIOpsShield service on {args.host}:{args.port}")
    logger.info(f"Strict mode: {shield.strict_mode}")
    logger.info(f"Debug mode: {args.debug}")
    
    # Run server
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True  # Handle concurrent requests
    )
