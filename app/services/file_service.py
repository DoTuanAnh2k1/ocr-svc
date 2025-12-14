import os
import time
import uuid
from typing import List, Set


class FileService:
    """Service for file operations"""

    @staticmethod
    def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
        """
        Check if the file has an allowed extension

        Args:
            filename: Name of the file
            allowed_extensions: Set of allowed extensions

        Returns:
            True if file extension is allowed
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def generate_timestamped_filename(original_filename: str) -> str:
        """
        Generate filename with unix timestamp

        Args:
            original_filename: Original filename

        Returns:
            Filename with timestamp (e.g., image_1234567890.jpg)
        """
        name, ext = os.path.splitext(original_filename)
        timestamp = int(time.time())
        crypt = str(uuid.uuid4()).replace("-", "")
        return f"{name}_{timestamp}_{crypt}{ext}"

    @staticmethod
    def delete_file(filepath: str) -> bool:
        """
        Delete a file if it exists

        Args:
            filepath: Path to the file

        Returns:
            True if file was deleted
        """
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    @staticmethod
    def get_image_files_from_folder(folder_path: str, allowed_extensions: Set[str]) -> List[str]:
        """
        Get all image files from a folder

        Args:
            folder_path: Path to the folder
            allowed_extensions: Set of allowed extensions

        Returns:
            List of image filenames
        """
        image_files = []
        for filename in os.listdir(folder_path):
            if FileService.allowed_file(filename, allowed_extensions):
                image_files.append(filename)
        return image_files
