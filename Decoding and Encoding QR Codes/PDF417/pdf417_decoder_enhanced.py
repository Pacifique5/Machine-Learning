import cv2
import numpy as np
import subprocess
import os
import sys
import shutil
from urllib.parse import quote

# Paths to required files
javase_jar = "javase-3.5.0.jar"
core_jar = "core-3.5.0.jar"
jcommander_jar = "jcommander-1.82.jar"

# Allow passing the image path via CLI, fallback to default
barcode_image = sys.argv[1] if len(sys.argv) > 1 else "pdf417.jpg"

# Normalize paths for Docker and local Java
image_abs = os.path.abspath(barcode_image)
image_abs_forward = image_abs.replace("\\", "/")
image_name = os.path.basename(barcode_image)

# Validate required files
for file in [javase_jar, core_jar, jcommander_jar, barcode_image]:
    if not os.path.exists(file):
        print(f"Error: {file} not found!")
        exit(1)

def preprocess_image(img):
    """Create multiple enhanced versions of the image"""
    enhanced = []
    
    # Original grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced.append(("gray.jpg", gray))
    
    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    enhanced.append(("thresh.jpg", thresh))
    
    # Otsu threshold
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    enhanced.append(("otsu.jpg", otsu))
    
    # Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_img = clahe.apply(gray)
    enhanced.append(("clahe.jpg", clahe_img))
    
    # Denoised
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    enhanced.append(("denoised.jpg", denoised))
    
    # Scaled up (2x)
    upscaled = cv2.resize(gray, (gray.shape[1]*2, gray.shape[0]*2), interpolation=cv2.INTER_CUBIC)
    enhanced.append(("upscaled.jpg", upscaled))
    
    # Scaled down then up (sharpening effect)
    small = cv2.resize(gray, (gray.shape[1]//2, gray.shape[0]//2))
    sharpened = cv2.resize(small, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_CUBIC)
    enhanced.append(("sharpened.jpg", sharpened))
    
    return enhanced

def local_java_command(image_path):
    # Local Java command (Windows uses ';' as classpath separator)
    classpath = f"{javase_jar};{core_jar};{jcommander_jar}"
    # Use direct path instead of file URI
    return [
        "java", "-cp", classpath,
        "com.google.zxing.client.j2se.CommandLineRunner",
        image_path
    ]

def attempt_decode(current_image_path: str) -> str:
    """Run ZXing through local Java for the given image path.
    Returns the raw stdout from ZXing."""
    try:
        result = subprocess.run(local_java_command(current_image_path), 
                              capture_output=True, text=True, check=True)
        out = result.stdout.strip()
        return out
    except subprocess.CalledProcessError as e:
        # Return stderr if available, otherwise empty
        return e.stderr.strip() if e.stderr else ""

# Load and preprocess image
img = cv2.imread(barcode_image)
if img is None:
    print(f"Error: Unable to read {barcode_image}")
    exit(1)

# Create enhanced versions
enhanced_images = preprocess_image(img)
candidates = [barcode_image]

# Save enhanced versions
for name, img_data in enhanced_images:
    cv2.imwrite(name, img_data)
    candidates.append(name)

# Also try rotated versions of original
rotated = {
    "rot90.jpg": cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
    "rot270.jpg": cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),
    "rot180.jpg": cv2.rotate(img, cv2.ROTATE_180),
}
for name, mat in rotated.items():
    cv2.imwrite(name, mat)
    candidates.append(name)

# Try decoding each candidate
decoded_text = None
output = ""
for candidate in candidates:
    output = attempt_decode(candidate)
    
    # Check if we got a successful decode (ZXing outputs the decoded text on first line if successful)
    lines = output.splitlines()
    if lines and "No barcode found" not in output and ":" not in lines[0]:
        # First line is usually the decoded text
        decoded_text = lines[0].strip()
        if decoded_text:
            print(f"Successfully decoded from: {candidate}")
            print("Decoded Output:")
            print(output)
            break
    elif lines and "No barcode found" not in output:
        # Look for decoded content after the file path line
        for i, line in enumerate(lines):
            if i > 0 and line.strip() and not line.startswith("file://") and not line.startswith("  Point"):
                decoded_text = line.strip()
                print(f"Successfully decoded from: {candidate}")
                print("Decoded Output:")
                print(output)
                break
        if decoded_text:
            break

if not decoded_text:
    print("Decoded Output:")
    print(output)
    print("\nNo barcode could be decoded from any image variant.")

# Parse the ZXing output for barcode position
points = []
for line in output.splitlines():
    if line.startswith("  Point"):
        parts = line.split(":")[1].strip().replace("(", "").replace(")", "").split(",")
        points.append((int(float(parts[0])), int(float(parts[1]))))

# Clean up temporary files
for name, _ in enhanced_images:
    if os.path.exists(name):
        os.remove(name)
for name in rotated.keys():
    if os.path.exists(name):
        os.remove(name)

# If points are found, draw a bounding polygon
if len(points) >= 4:
    # Load the image with OpenCV
    image = cv2.imread(barcode_image)
    if image is not None:
        # Draw a polygon connecting the points
        points_array = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        print(f"Drawing polygon with points: {points}")

        cv2.polylines(image, [points_array], isClosed=True, color=(0, 255, 0), thickness=2)

        # Save and display the annotated image
        annotated_image_path = "annotated_barcode.png"
        cv2.imwrite(annotated_image_path, image)
        print(f"Annotated image saved as {annotated_image_path}")

        # Display the image
        cv2.imshow("Detected Barcode", image)
        print("Press any key to close the window.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
else:
    print("No bounding box points detected.")

