import os
import sys
from pathlib import Path
import httpx

# Default configuration
API_URL = os.getenv("API_URL", "https://scan.thewayccg.com/api/v1/recognize-card")
# Use the first available PNG from data/gt/png if available, otherwise expects path arg
DEFAULT_IMAGE_DIR = Path("data/gt/png")
DEFAULT_IMAGE = DEFAULT_IMAGE_DIR / "1.png"

def test_deployment(image_path=None):
    if image_path:
        path = Path(image_path)
        if path.is_dir():
            images = list(path.glob("*.[jp][pn]g")) + list(path.glob("*.[jJ][pP][gG]")) + list(path.glob("*.[pP][nN][gG]"))
            # remove duplicates
            images = list(set(images))
            if not images:
                print(f"No images found in {path}")
                return
            for img in images:
                test_deployment(img)
            return
        else:
            img_p = path
    else:
        img_p = DEFAULT_IMAGE
    
    if not img_p.exists():
        print(f"Error: Image not found at {img_p}")
        print(f"Please provide a valid image path or ensure {DEFAULT_IMAGE} exists.")
        return

    print(f"Testing API at: {API_URL}")
    print(f"Using image: {img_p}")

    try:
        with open(img_p, "rb") as f:
            files = {"file": (img_p.name, f, "image/png")}
            print("Sending request to server...")
            with httpx.Client(timeout=30.0) as client:
                response = client.post(API_URL, files=files)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\n✅ Success! Response:")
            print(response.json())
        else:
            print("\n❌ Failed. Response:")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test the recognition service deployment")
    parser.add_argument("--image", help="Path to image file to test", default=None)
    parser.add_argument("--url", help="API URL to test", default=None)
    args = parser.parse_args()

    if args.url:
        API_URL = args.url

    test_deployment(args.image)
