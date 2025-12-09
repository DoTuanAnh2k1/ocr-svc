from flask import Flask, request, jsonify
import os
import time
from werkzeug.utils import secure_filename
from logic_cpu import extract_image, initialize_model

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
        
        # Delete file after processing
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️  Deleted temporary file: {timestamped_filename}")
        
        return jsonify({
            'success': True,
            'filename': original_filename,
            'text': extracted_text
        }), 200
        
    except Exception as e:
        # Clean up file if error occurs
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️  Cleaned up file after error: {filepath}")
        
        return jsonify({
            'error': f'Error processing image: {str(e)}'
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
    print("📸 Image to Text: http://localhost:5000/image-to-text")
    print("=" * 60)
    print("\n🎉 Server is ready to accept requests!\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)  # Set debug=False to avoid reloading