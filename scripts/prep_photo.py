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

    # 2. Crop to Newton head and upper torso
    crop_y1, crop_y2 = int(h * 0.05), int(h * 0.70)
    crop_x1, crop_x2 = int(w * 0.15), int(w * 0.85)
    cropped = img[crop_y1:crop_y2, crop_x1:crop_x2]

    # 3. Convert to Grayscale
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    # 4. Subject isolation: Elliptical mask centered on portrait
    mask = np.zeros_like(gray)
    ch, cw = gray.shape
    cv2.ellipse(mask, (cw // 2, int(ch * 0.48)), (int(cw * 0.44), int(ch * 0.47)), 0, 0, 360, 255, -1)

    # Outside the subject mask or dark background -> set to pure white (255)
    gray_masked = np.where((mask == 0) | (gray < 45), 255, gray)

    # 5. Bilateral filter to smooth skin tones while preserving sharp structural edges (eyes, jaw, hair)
    smoothed = cv2.bilateralFilter(gray_masked, d=9, sigmaColor=75, sigmaSpace=75)

    # 6. Soften harsh small nostril spots in central face region
    face_y1, face_y2 = int(ch * 0.35), int(ch * 0.60)
    face_x1, face_x2 = int(cw * 0.35), int(cw * 0.65)
    face_region = smoothed[face_y1:face_y2, face_x1:face_x2]
    smoothed[face_y1:face_y2, face_x1:face_x2] = np.where(face_region < 100, 110, face_region)

    # 7. Mild CLAHE contrast equalization
    clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8))
    gray_prepped = clahe.apply(smoothed)

    output_path = "source-prepped.png"
    cv2.imwrite(output_path, gray_prepped)
    print(f"Successfully prepped smooth facial portrait and saved to {output_path}")

if __name__ == "__main__":
    main()
