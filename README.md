# OCR Service - Invoice Data Extraction

Professional Flask-based HTTP server for extracting structured data from invoice images using AI-powered OCR.

## Features

- **Single Image Processing**: Extract data from individual invoice images
- **Batch Folder Processing**: Process all images in a directory at once
- **Structured JSON Output**: Returns data in standardized format with fields: `name`, `quantity`, `unit_price`, `total`
- **AI-Powered**: Uses Vintern-1B-v3.5 model for accurate Vietnamese text extraction
- **Professional Architecture**: Clean, modular code structure following Flask best practices

## Project Structure

```
ocr-svc/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuration settings
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health_routes.py     # Health check endpoint
│   │   ├── ocr_routes.py        # OCR endpoints
│   │   └── error_handlers.py    # Error handlers
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_model_service.py  # AI model operations
│   │   ├── ocr_service.py       # OCR business logic
│   │   └── file_service.py      # File operations
│   └── utils/
│       ├── __init__.py
│       └── response_parser.py   # Response parsing utilities
├── client/
│   └── main.py                  # Test client
├── __main__.py                  # Application entry point
└── README.md
```

## Prerequisites

- **Python 3.8+**
- **CUDA-capable GPU** (optional, but recommended for faster inference)
- **8GB+ RAM** (16GB recommended for GPU usage)
- **Internet connection** (for initial model download)

## Installation & Setup

### 1. Clone or Download the Repository

```bash
cd ocr-svc
```

### 2. Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

**For GPU (CUDA) Support:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install flask transformers pillow werkzeug requests
```

**For CPU Only:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install flask transformers pillow werkzeug requests
```

### 4. Model Download

The AI model (`5CD-AI/Vintern-1B-v3_5`) will be automatically downloaded on first run. This is approximately **2-3GB** and may take a few minutes depending on your internet connection.

## Running the Server

### Start the Server

```bash
python __main__.py
```

**Expected Output:**
```
============================================================
🚀 Server is starting...
============================================================

📦 Loading AI model (this may take a while)...
Initializing model on device: cuda
Model initialized successfully!

============================================================
📍 Healthcheck: http://localhost:5000/healthcheck
📸 Single Image: http://localhost:5000/image-to-text
📂 Folder Batch: http://localhost:5000/extract-from-folder
============================================================

🎉 Server is ready to accept requests!

 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000
```

The server will be available at `http://localhost:5000`

## Testing the Server

### Method 1: Using the Test Client (Recommended)

The project includes a test client for easy testing.

**1. Update the image path in `client/main.py`:**

Edit line 97 in [client/main.py](client/main.py):
```python
image_path = "path/to/your/test/image.jpg"
```

**2. Run the test client:**

```bash
python client/main.py
```

**Expected Output:**
```
==================================================
Image to Text Client
==================================================

1. Checking server health...
✅ Server is healthy!
   Response: {'status': 'ok', 'message': 'Server is running smoothly!'}

3. Processing image...
📤 Sending image: test.jpg
✅ Success!
   Filename: test.jpg
   Extracted text: {'filename': 'test.jpg', 'products': [...], ...}
   ⏱️  Processing time: 12.34 seconds

✨ Done!
```

### Method 2: Using cURL

**Test Health Check:**
```bash
curl http://localhost:5000/healthcheck
```

**Test Single Image:**
```bash
curl -X POST http://localhost:5000/image-to-text \
  -F "image=@/path/to/invoice.jpg"
```

**Test Folder Processing:**
```bash
curl -X POST http://localhost:5000/extract-from-folder \
  -H "Content-Type: application/json" \
  -d "{\"path\": \"/path/to/folder\"}"
```

### Method 3: Using Python Requests

```python
import requests

# Health check
response = requests.get("http://localhost:5000/healthcheck")
print(response.json())

# Single image
with open("invoice.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post("http://localhost:5000/image-to-text", files=files)
    print(response.json())
```

## API Reference

### 1. Health Check
```
GET /healthcheck
```

**Response:**
```json
{
  "status": "ok",
  "message": "Server is running smoothly!"
}
```

### 2. Extract from Single Image
```
POST /image-to-text
Content-Type: multipart/form-data
```

**Request:**
- Field name: `image`
- File: Invoice image (png, jpg, jpeg, gif, bmp, webp)
- Max size: 16MB

**Response:**
```json
{
  "success": true,
  "filename": "invoice.jpg",
  "raw_text": "Tên hàng | Số lượng | Đơn giá | Thành tiền\n...",
  "products": [
    {
      "name": "Coca Cola",
      "quantity": "2",
      "unit_price": "10000",
      "total": "20000"
    }
  ]
}
```

### 3. Extract from Folder
```
POST /extract-from-folder
Content-Type: application/json
```

**Request Body:**
```json
{
  "path": "/path/to/folder"
}
```

**Response:**
```json
{
  "success": true,
  "folder_path": "/path/to/folder",
  "summary": {
    "total": 5,
    "successful": 4,
    "failed": 1
  },
  "results": [
    {
      "filename": "invoice1.jpg",
      "success": true,
      "raw_text": "...",
      "products": [...]
    },
    {
      "filename": "invoice2.jpg",
      "success": false,
      "error": "Error message"
    }
  ]
}
```

## Configuration

Edit [app/config/settings.py](app/config/settings.py) to customize:

```python
class Config:
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max file size (16MB)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

    # Server settings
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False

    # Model settings
    MODEL_NAME = "5CD-AI/Vintern-1B-v3_5"
    MAX_NUM_IMAGES = 3
    MAX_NEW_TOKENS = 2048
    NUM_BEAMS = 3
    REPETITION_PENALTY = 2.5
```

## Output Format

All responses include standardized product data:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Product name |
| `quantity` | string | Quantity |
| `unit_price` | string | Unit price |
| `total` | string | Total amount |

## Architecture

### Application Factory Pattern
Uses Flask's application factory pattern for better modularity and testing.

### Service Layer
- **AIModelService**: Handles AI model initialization and inference (singleton pattern)
- **OCRService**: Business logic for OCR operations
- **FileService**: File handling utilities

### Routes (Blueprints)
- **health_routes**: Health check endpoint
- **ocr_routes**: OCR extraction endpoints
- **error_handlers**: Centralized error handling

### Utilities
- **ResponseParser**: Parses and normalizes AI model responses into structured JSON

## Performance Notes

- **First request**: May take 10-30 seconds (model loading)
- **Subsequent requests**: 2-5 seconds per image (GPU) or 10-20 seconds (CPU)
- **Model is cached**: Loaded once at startup for optimal performance
- **Temporary files**: Automatically cleaned up after processing

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (missing fields, invalid input)
- `404`: Endpoint not found
- `413`: File too large (max 16MB)
- `500`: Internal server error

## Troubleshooting

### Server won't start
- Check if port 5000 is already in use
- Ensure all dependencies are installed
- Check Python version (3.8+ required)

### Model download fails
- Check internet connection
- Try downloading model manually using Hugging Face CLI
- Ensure sufficient disk space (3GB+)

### Out of memory errors
- Reduce `MAX_NUM_IMAGES` in config
- Use CPU instead of GPU if GPU memory is limited
- Close other applications

### Slow inference
- Enable GPU if available (CUDA)
- Reduce `MAX_NEW_TOKENS` in config
- Ensure model is properly cached

## Development

To run in debug mode, edit [app/config/settings.py](app/config/settings.py):
```python
DEBUG = True
```

## License

[Your License Here]

## Support

For issues, questions, or contributions, please contact the development team.
