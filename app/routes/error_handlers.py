from flask import jsonify


def register_error_handlers(app):
    """Register error handlers for the application"""

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handler for file too large error"""
        return jsonify({
            'error': 'File is too large. Maximum size is 16MB'
        }), 413

    @app.errorhandler(404)
    def not_found(error):
        """Handler for 404 errors"""
        return jsonify({
            'error': 'Endpoint not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handler for 500 errors"""
        return jsonify({
            'error': 'Internal server error'
        }), 500
