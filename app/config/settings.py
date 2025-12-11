import os


class Config:
    """Application configuration"""

    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max 16MB

    # Allowed file extensions
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
