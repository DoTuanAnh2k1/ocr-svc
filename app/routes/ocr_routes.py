from flask import Blueprint, request, jsonify, current_app
import os
import time
from werkzeug.utils import secure_filename

from app.services.ocr_service import OCRService
from app.services.file_service import FileService

bp = Blueprint('ocr', __name__)


@bp.route('/image-to-text', methods=['POST'])
def extract_from_image():
    """
    Extract structured data from a single image

    Usage:
    - Method: POST
    - Content-Type: multipart/form-data
    - Field name: 'image'

    Returns:
    - JSON with extracted products (ten_hang, so_luong, don_gia, thanh_tien)
    """
    # Validate request
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image file provided. Use field name "image"'
        }), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({
            'error': 'No file selected'
        }), 400

    if not FileService.allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify({
            'error': f'Invalid file type. Allowed types: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'
        }), 400

    filepath = None
    try:
        # Save file temporarily
        original_filename = secure_filename(file.filename)
        timestamped_filename = FileService.generate_timestamped_filename(original_filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], timestamped_filename)

        file.save(filepath)
        print(f"📁 Saved temporary file: {timestamped_filename}")

        # Process image
        result = OCRService.process_single_image(filepath, original_filename)

        # Clean up
        FileService.delete_file(filepath)
        print(f"🗑️  Deleted temporary file: {timestamped_filename}")

        return jsonify(result), 200

    except Exception as e:
        # Clean up on error
        if filepath:
            FileService.delete_file(filepath)

        return jsonify({
            'error': f'Error processing image: {str(e)}'
        }), 500


@bp.route('/extract-from-folder', methods=['POST'])
def extract_from_folder():
    """
    Extract structured data from all images in a folder

    Usage:
    - Method: POST
    - Content-Type: application/json
    - Body: {"path": "/path/to/folder"}

    Returns:
    - JSON with list of results for each image
    """
    # Validate request
    if not request.is_json:
        return jsonify({
            'error': 'Content-Type must be application/json'
        }), 400

    data = request.get_json()

    if 'path' not in data:
        return jsonify({
            'error': 'Missing "path" field in request body'
        }), 400

    folder_path = data['path']

    # Validate folder
    if not os.path.exists(folder_path):
        return jsonify({
            'error': f'Folder path does not exist: {folder_path}'
        }), 400

    if not os.path.isdir(folder_path):
        return jsonify({
            'error': f'Path is not a directory: {folder_path}'
        }), 400

    try:
        # Get image files
        image_files = FileService.get_image_files_from_folder(
            folder_path,
            current_app.config['ALLOWED_EXTENSIONS']
        )

        if not image_files:
            return jsonify({
                'success': True,
                'message': 'No valid image files found in folder',
                'folder_path': folder_path,
                'results': []
            }), 200

        print(f"📂 Processing {len(image_files)} images from: {folder_path}")

        # Process all images
        result = OCRService.process_folder(folder_path, image_files)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': f'Error processing folder: {str(e)}'
        }), 500
