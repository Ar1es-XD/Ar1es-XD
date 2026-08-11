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
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        print(f"Error: Could not read image {input_path}")
        sys.exit(1)

    h, w, _ = img.shape

    # 2. Crop to head & upper torso (12% to 62% Y, 25% to 75% X)
    crop_y1, crop_y2 = int(h * 0.12), int(h * 0.62)
    crop_x1, crop_x2 = int(w * 0.25), int(w * 0.75)
    cropped = img[crop_y1:crop_y2, crop_x1:crop_x2]

    # 3. Grayscale & Normalize
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    # 4. Extract prominent facial feature edges (eyes, eyebrows, nose, mouth, wig)
    edges = cv2.Canny(gray_norm, 40, 130)
    edges_dilated = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)

    # Combine gray tones with edges: edges sharpen facial features
    blended = cv2.addWeighted(gray_norm, 0.75, 255 - edges_dilated, 0.25, 0)

    # 5. Mask background around face & wig
    ch, cw = blended.shape
    mask = np.zeros_like(blended)
    cv2.ellipse(mask, (cw // 2, int(ch * 0.48)), (int(cw * 0.44), int(ch * 0.47)), 0, 0, 360, 255, -1)
    final_prepped = np.where((mask == 0) | (blended > 215), 255, blended)

    output_path = "source-prepped.png"
    cv2.imwrite(output_path, final_prepped)
    print(f"Successfully prepped edge-enhanced facial portrait and saved to {output_path}")

if __name__ == "__main__":
    main()
