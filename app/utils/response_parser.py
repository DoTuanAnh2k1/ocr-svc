import json
import re
from typing import List, Dict, Any


class ResponseParser:
    """Parser for AI model responses"""

    @staticmethod
    def parse_ocr_response(response: str) -> List[Dict[str, Any]]:
        """
        Parse AI model response to structured JSON format

        Args:
            response: Raw response from AI model

        Returns:
            List of normalized products with fields: name, quantity, unit_price, total
        """
        products = ResponseParser._parse_ocr_response_to_json(response)
        return ResponseParser._normalize_product_data(products)

    @staticmethod
    def _parse_ocr_response_to_json(response: str) -> List[Dict[str, Any]]:
        """
        Parse AI model response to structured JSON format

        Args:
            response (str): Raw response from AI model

        Returns:
            List[Dict]: List of products with fields: ten_hang, so_luong, don_gia, thanh_tien

        Example response formats:
        ```
        Tên hàng | Số lượng | Đơn giá | Thành tiền
        ---|---|---|---
        Hành học | 1 | 35000 | 35000
        ```
        """
        products = []

        # Try to parse markdown table format
        lines = response.strip().split('\n')

        # Find table content (skip header and separator)
        header_passed = False

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Detect table separator (e.g., |---|---| or ---|---|---)
            if re.match(r'^[\|\s]*---', line):
                header_passed = True
                continue

            # Skip header line (contains "Tên hàng" or similar)
            if not header_passed and any(keyword in line.lower() for keyword in ['tên hàng', 'ten hang', 'số lượng', 'so luong']):
                continue

            # Parse table rows
            if '|' in line and header_passed:
                # Split by | and clean up
                parts = [p.strip() for p in line.split('|')]
                # Remove empty first/last elements from splitting
                parts = [p for p in parts if p]

                if len(parts) >= 4:
                    try:
                        product = {
                            "ten_hang": parts[0],
                            "so_luong": parts[1],
                            "don_gia": parts[2],
                            "thanh_tien": parts[3]
                        }
                        products.append(product)
                    except (IndexError, ValueError) as e:
                        print(f"Warning: Could not parse line: {line} - {e}")
                        continue

        # If no products found via table parsing, try alternative formats
        if not products:
            # Try to find JSON in response
            try:
                # Look for JSON array or object
                json_match = re.search(r'\[.*\]|\{.*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    if isinstance(parsed, list):
                        products = parsed
                    elif isinstance(parsed, dict):
                        products = [parsed]
            except json.JSONDecodeError:
                pass

        return products


    @staticmethod
    def _clean_numeric_value(value: str) -> str:
        """
        Clean numeric values by removing currency symbols and formatting

        Args:
            value: Raw value like "10,000 VND" or "10.000đ"

        Returns:
            Cleaned value like "10000"
        """
        if not value:
            return "0"

        # Remove common currency symbols
        cleaned = re.sub(r'[đĐ₫VNDvnd,.\s]+', '', value)
        # Keep only digits
        cleaned = re.sub(r'[^\d]', '', cleaned)
        return cleaned if cleaned else "0"

    @staticmethod
    def _normalize_product_data(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize product data to ensure consistent format with English field names

        Args:
            products: List of product dictionaries

        Returns:
            List of normalized products with fields: name, quantity, unit_price, total
        """
        normalized = []

        for product in products:
            normalized_product = {
                "name": str(product.get("ten_hang", "")).strip(),
                "quantity": str(product.get("so_luong", "0")).strip(),
                "unit_price": str(product.get("don_gia", "0")).strip(),
                "total": str(product.get("thanh_tien", "0")).strip()
            }

            # Only add if product name is not empty
            if normalized_product["name"]:
                normalized.append(normalized_product)

        return normalized
