import os
import sys
import urllib.request
import ssl
import cv2
import numpy as np

# Bypass SSL certificate verification issues on macOS python installations
ssl._create_default_https_context = ssl._create_unverified_context

def download_newton_image(dest_path):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/3/39/GodfreyKneller-IsaacNewton-1689.jpg"
    ]
    print("Attempting to download Newton's portrait...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravityAgent/1.0'}
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as response:
                with open(dest_path, 'wb') as f:
                    f.write(response.read())
            print(f"Successfully downloaded from: {url}")
            return True
        except Exception as e:
            print(f"Failed to download from {url}: {e}")
    return False

def main():
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = "newton.jpg"
        if not os.path.exists(input_path):
            success = download_newton_image(input_path)
            if not success:
                print("Error: Could not obtain Newton's portrait.")
                sys.exit(1)

    print(f"Processing image: {input_path}")
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} does not exist.")
        sys.exit(1)

    # 1. Load image
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error: Could not read image {input_path}")
        sys.exit(1)

    # 2. Background removal using rembg (with fallback)
    bg_removed = False
    try:
        print("Attempting background removal with rembg...")
        from rembg import remove
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        out_rgb = remove(img_rgb)
        # Convert back to BGR/BGRA for OpenCV
        img = cv2.cvtColor(out_rgb, cv2.COLOR_RGBA2BGRA)
        bg_removed = True
        print("Background removal successful.")
    except BaseException as e:
        print(f"Warning: rembg failed or not installed ({e}). Proceeding with simple fallback.")

    # 3. Composite onto pure white if alpha channel is present
    if len(img.shape) == 3 and img.shape[2] == 4:
        # BGRA image
        b, g, r, alpha = cv2.split(img)
        foreground = cv2.merge((b, g, r))
        # Create a white background
        background = np.ones_like(foreground, dtype=np.uint8) * 255
        # Normalize alpha channel to 0.0 - 1.0
        alpha_factor = alpha.astype(float) / 255.0
        alpha_factor = cv2.merge((alpha_factor, alpha_factor, alpha_factor))
        # Blend
        img = (foreground.astype(float) * alpha_factor + background.astype(float) * (1.0 - alpha_factor)).astype(np.uint8)
    else:
        # BGR image - if background removal was skipped/failed
        pass

    # 4. Grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # 5. Local Contrast Boost (CLAHE)
    print("Applying CLAHE local contrast boost...")
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray_clahe = clahe.apply(gray)

    # Save output as source-prepped.png
    output_path = "source-prepped.png"
    cv2.imwrite(output_path, gray_clahe)
    print(f"Successfully prepped photo and saved to {output_path}")

if __name__ == "__main__":
    main()
