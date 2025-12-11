from flask import Blueprint, jsonify

bp = Blueprint('health', __name__)


@bp.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Healthcheck endpoint - verify server is running"""
    return jsonify({
        'status': 'ok',
        'message': 'Server is running smoothly!'
    }), 200
