# OCR Service - Invoice Data Extraction

Professional Flask-based HTTP server for extracting structured data from invoice images using AI-powered OCR.

## Features

- **Single Image Processing**: Extract data from individual invoice images
- **Batch Folder Processing**: Process all images in a directory at once
- **Structured JSON Output**: Returns data in standardized format with fields: `ten_hang`, `so_luong`, `don_gia`, `thanh_tien`
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
├── __main__.py                  # Application entry point
└── README.md
```

## Installation

1. Install dependencies:
```bash
pip install flask transformers torch torchvision pillow werkzeug
```

2. Make sure the AI model is accessible (will be downloaded on first run):
   - Model: `5CD-AI/Vintern-1B-v3_5`

## Usage

### Start Server

```bash
python __main__.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
GET /healthcheck
```

Response:
```json
{
  "status": "ok",
  "message": "Server is running smoothly!"
}
```

#### 2. Extract from Single Image
```bash
POST /image-to-text
Content-Type: multipart/form-data
```

**Request:**
- Field name: `image`
- File: Invoice image (png, jpg, jpeg, gif, bmp, webp)

**Example:**
```bash
curl -X POST http://localhost:5000/image-to-text \
  -F "image=@invoice.jpg"
```

**Response:**
```json
{
  "success": true,
  "filename": "invoice.jpg",
  "raw_text": "| Tên hàng | Số lượng | Đơn giá | Thành tiền |...",
  "products": [
    {
      "ten_hang": "Coca Cola",
      "so_luong": "2",
      "don_gia": "10000",
      "thanh_tien": "20000"
    }
  ]
}
```

#### 3. Extract from Folder
```bash
POST /extract-from-folder
Content-Type: application/json
```

**Request Body:**
```json
{
  "path": "/path/to/folder"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/extract-from-folder \
  -H "Content-Type: application/json" \
  -d '{"path": "/home/user/invoices"}'
```

**Response:**
```json
{
  "success": true,
  "folder_path": "/home/user/invoices",
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

Edit `app/config/settings.py` to customize:

```python
class Config:
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max file size (16MB)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False

    MODEL_NAME = "5CD-AI/Vintern-1B-v3_5"
    MAX_NUM_IMAGES = 3
    MAX_NEW_TOKENS = 2048
```

## Architecture

### Application Factory Pattern
Uses Flask's application factory pattern for better modularity and testing.

### Service Layer
- **AIModelService**: Handles AI model initialization and inference
- **OCRService**: Business logic for OCR operations
- **FileService**: File handling utilities

### Routes (Blueprints)
- **health_routes**: Health check endpoint
- **ocr_routes**: OCR extraction endpoints

### Utilities
- **ResponseParser**: Parses and normalizes AI model responses

## Output Format

All responses include standardized product data:

| Field | Type | Description |
|-------|------|-------------|
| `ten_hang` | string | Product name |
| `so_luong` | string | Quantity |
| `don_gia` | string | Unit price |
| `thanh_tien` | string | Total amount |

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (missing fields, invalid input)
- `413`: File too large
- `500`: Internal server error

## Notes

- Model is loaded once at startup and cached for performance
- Temporary uploaded files are automatically cleaned up after processing
- Supports both CPU and CUDA (GPU) inference
- Uses bfloat16 precision on GPU, float32 on CPU