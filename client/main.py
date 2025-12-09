import requests
import sys
import os
import time

# Server configuration
SERVER_URL = "http://localhost:5000"
HEALTHCHECK_ENDPOINT = f"{SERVER_URL}/healthcheck"
IMAGE_TO_TEXT_ENDPOINT = f"{SERVER_URL}/image-to-text"

def check_server_health():
    """Check if the server is running"""
    try:
        response = requests.get(HEALTHCHECK_ENDPOINT, timeout=10)
        if response.status_code == 200:
            print("✅ Server is healthy!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running!")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def send_image(image_path):
    """Send an image to the server for text extraction"""
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return None
    
    # Check if it's a file (not a directory)
    if not os.path.isfile(image_path):
        print(f"❌ Path is not a file: {image_path}")
        return None
    
    print(f"📤 Sending image: {image_path}")
    
    try:
        # Start timer
        start_time = time.time()
        
        # Open and send the image file
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            response = requests.post(IMAGE_TO_TEXT_ENDPOINT, files=files, timeout=300)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Extracted text: {result.get('text')}")
            print(f"   ⏱️  Processing time: {elapsed_time:.2f} seconds")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Message: {response.json()}")
            print(f"   ⏱️  Time taken: {elapsed_time:.2f} seconds")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running!")
        return None
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    """Main function"""
    print("=" * 50)
    print("Image to Text Client")
    print("=" * 50)
    print()
    
    # First, check server health
    print("1. Checking server health...")
    if not check_server_health():
        print("\n⚠️  Server is not available. Please start the server first.")
        sys.exit(1)
    
    print()
    
    image_path = "E:\\Data\\Python\\ocr_service\\client\\test.jpg"
    
    # Send image to server
    print()
    print("3. Processing image...")
    result = send_image(image_path)
    
    if result:
        print("\n✨ Done!")
    else:
        print("\n❌ Failed to process image.")
        sys.exit(1)

if __name__ == "__main__":
    main()