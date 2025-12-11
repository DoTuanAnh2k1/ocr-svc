import os
from typing import Dict, List, Any

from app.services.ai_model_service import AIModelService
from app.utils.response_parser import ResponseParser


class OCRService:
    """Service for OCR operations"""

    @staticmethod
    def process_single_image(image_path: str, original_filename: str) -> Dict[str, Any]:
        """
        Process a single image and extract structured data

        Args:
            image_path: Path to the image file
            original_filename: Original filename

        Returns:
            Dictionary with success status and extracted products
        """
        # Extract text using AI model
        extracted_text = AIModelService.extract_text_from_image(image_path)

        # Parse to structured JSON
        products = ResponseParser.parse_ocr_response(extracted_text)

        return {
            'success': True,
            'filename': original_filename,
            'raw_text': extracted_text,
            'products': products
        }

    @staticmethod
    def process_folder(folder_path: str, image_files: List[str]) -> Dict[str, Any]:
        """
        Process all images in a folder

        Args:
            folder_path: Path to the folder
            image_files: List of image filenames

        Returns:
            Dictionary with summary and results for each image
        """
        results = []

        for filename in image_files:
            image_path = os.path.join(folder_path, filename)

            try:
                print(f"🖼️  Processing: {filename}")

                # Extract text
                extracted_text = AIModelService.extract_text_from_image(image_path)

                # Parse to JSON
                products = ResponseParser.parse_ocr_response(extracted_text)

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

        # Calculate summary
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        return {
            'success': True,
            'folder_path': folder_path,
            'summary': {
                'total': len(results),
                'successful': successful,
                'failed': failed
            },
            'results': results
        }
