from flask import Flask, request, jsonify
import os
import time
from werkzeug.utils import secure_filename
from logic_cpu import extract_image, initialize_model
from utils import parse_ocr_response_to_json, normalize_product_data

app = Flask(__name__)

# Config upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB

def allowed_file(filename):
    """Check if the file is a valid image"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_timestamped_filename(original_filename):
    """
    Generate filename with unix timestamp
    Example: image.jpg -> image_1234567890.jpg
    """
    # Get filename and extension
    name, ext = os.path.splitext(original_filename)
    # Get current unix timestamp
    timestamp = int(time.time())
    # Return new filename
    return f"{name}_{timestamp}{ext}"

def process_image_to_text(image_path) -> str:
    """
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Text extracted from the image
    """
    return extract_image(image_file=image_path)

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Healthcheck handler - check if server is running"""
    return jsonify({
        'status': 'ok',
        'message': 'Server is running smoothly!'
    }), 200

@app.route('/image-to-text', methods=['POST'])
def image_to_text():
    """
    Handler that receives an image and returns text
    
    Usage:
    - Method: POST
    - Content-Type: multipart/form-data
    - Field name: 'image'
    """
    # Check if file is in request
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image file provided. Use field name "image"'
        }), 400
    
    file = request.files['image']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({
            'error': 'No file selected'
        }), 400
    
    # Check if extension is valid
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    filepath = None
    try:
        # Generate timestamped filename
        original_filename = secure_filename(file.filename)
        timestamped_filename = generate_timestamped_filename(original_filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], timestamped_filename)
        
        # Save file
        file.save(filepath)
        print(f"📁 Saved temporary file: {timestamped_filename}")
        
        # Call image processing function
        extracted_text = process_image_to_text(filepath)

        # Parse response to structured JSON
        products = parse_ocr_response_to_json(extracted_text)
        products = normalize_product_data(products)

        # Delete file after processing
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️  Deleted temporary file: {timestamped_filename}")

        return jsonify({
            'success': True,
            'filename': original_filename,
            'raw_text': extracted_text,
            'products': products
        }), 200
        
    except Exception as e:
        # Clean up file if error occurs
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️  Cleaned up file after error: {filepath}")
        
        return jsonify({
            'error': f'Error processing image: {str(e)}'
        }), 500

@app.route('/extract-from-folder', methods=['POST'])
def extract_from_folder():
    """
    Handler that receives a folder path and processes all images in it

    Usage:
    - Method: POST
    - Content-Type: application/json
    - Body: {"path": "/path/to/folder"}

    Returns:
    - List of results for each image with products extracted
    """
    # Check if JSON data is provided
    if not request.is_json:
        return jsonify({
            'error': 'Content-Type must be application/json'
        }), 400

    data = request.get_json()

    # Check if path is provided
    if 'path' not in data:
        return jsonify({
            'error': 'Missing "path" field in request body'
        }), 400

    folder_path = data['path']

    # Validate folder path
    if not os.path.exists(folder_path):
        return jsonify({
            'error': f'Folder path does not exist: {folder_path}'
        }), 400

    if not os.path.isdir(folder_path):
        return jsonify({
            'error': f'Path is not a directory: {folder_path}'
        }), 400

    try:
        # Get all image files in folder
        image_files = []
        for filename in os.listdir(folder_path):
            if allowed_file(filename):
                image_files.append(filename)

        if not image_files:
            return jsonify({
                'success': True,
                'message': 'No valid image files found in folder',
                'folder_path': folder_path,
                'results': []
            }), 200

        print(f"📂 Processing {len(image_files)} images from: {folder_path}")

        # Process each image
        results = []
        for filename in image_files:
            image_path = os.path.join(folder_path, filename)

            try:
                print(f"🖼️  Processing: {filename}")

                # Extract text from image
                extracted_text = process_image_to_text(image_path)

                # Parse to JSON
                products = parse_ocr_response_to_json(extracted_text)
                products = normalize_product_data(products)

                results.append({
                    'filename': filename,
                    'success': True,
                    'raw_text': extracted_text,
                    'products': products
                })

                print(f"✅ Completed: {filename} ({len(products)} products)")

            except Exception as img_error:
                print(f"❌ Error processing {filename}: {str(img_error)}")
                results.append({
                    'filename': filename,
                    'success': False,
                    'error': str(img_error)
                })

        # Summary
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        return jsonify({
            'success': True,
            'folder_path': folder_path,
            'summary': {
                'total': len(results),
                'successful': successful,
                'failed': failed
            },
            'results': results
        }), 200

    except Exception as e:
        return jsonify({
            'error': f'Error processing folder: {str(e)}'
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handler for file too large error"""
    return jsonify({
        'error': 'File is too large. Maximum size is 16MB'
    }), 413

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Server is starting...")
    print("=" * 60)
    
    # Pre-load model before starting server
    print("\n📦 Loading AI model (this may take a while)...")
    initialize_model()
    print("✅ Model loaded successfully!\n")
    
    print("=" * 60)
    print("📍 Healthcheck: http://localhost:5000/healthcheck")
    print("📸 Single Image: http://localhost:5000/image-to-text")
    print("📂 Folder Batch: http://localhost:5000/extract-from-folder")
    print("=" * 60)
    print("\n🎉 Server is ready to accept requests!\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)  # Set debug=False to avoid reloading