"""
PDF417 Barcode Decoder
This script decodes PDF417 barcode from pdf417.jpg using ZXing library
"""

import cv2
import numpy as np
import subprocess
import os
import sys
import shutil
import tempfile
from urllib.parse import quote

# Hardcoded image file to decode
BARCODE_IMAGE = "pdf417.jpg"

# Paths to required JAR files
JAVASE_JAR = "javase-3.5.0.jar"
CORE_JAR = "core-3.5.0.jar"
JCOMMANDER_JAR = "jcommander-1.82.jar"

def validate_files():
    """Check if all required files exist"""
    required_files = [JAVASE_JAR, CORE_JAR, JCOMMANDER_JAR, BARCODE_IMAGE]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"Error: Missing required files: {', '.join(missing_files)}")
        print(f"Current directory: {os.getcwd()}")
        sys.exit(1)

def preprocess_image(img):
    """Create multiple enhanced versions of the image for better detection"""
    enhanced = []
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced.append(("gray.jpg", gray))
    
    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    enhanced.append(("thresh.jpg", thresh))
    
    # Otsu threshold
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    enhanced.append(("otsu.jpg", otsu))
    
    # Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)
    enhanced.append(("clahe.jpg", clahe_img))
    
    # Denoised
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    enhanced.append(("denoised.jpg", denoised))
    
    # Sharpen
    kernel = np.array([[-1, -1, -1],
                      [-1,  9, -1],
                      [-1, -1, -1]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    enhanced.append(("sharpened.jpg", sharpened))
    
    # Upscaled 2x for better detail
    upscaled = cv2.resize(gray, (gray.shape[1] * 2, gray.shape[0] * 2), 
                         interpolation=cv2.INTER_CUBIC)
    enhanced.append(("upscaled.jpg", upscaled))
    
    # Morphological operations to clean the image
    kernel_morph = np.ones((2, 2), np.uint8)
    morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel_morph)
    enhanced.append(("morph.jpg", morph))
    
    return enhanced

def create_local_java_command(image_path):
    """Create Java command to run ZXing decoder"""
    classpath = f"{JAVASE_JAR};{CORE_JAR};{JCOMMANDER_JAR}"
    
    # Convert to proper file URI format for Windows paths with spaces
    abs_path = os.path.abspath(image_path)
    # Normalize forward slashes for URI
    abs_path_forward = abs_path.replace("\\", "/")
    # Build file URI (ZXing expects URI format on Windows)
    file_uri = f"file:///{quote(abs_path_forward, safe=':/')}"
    
    return [
        "java", "-cp", classpath,
        "com.google.zxing.client.j2se.CommandLineRunner",
        file_uri
    ]

def decode_with_zxing(image_path, debug=False):
    """Decode barcode using ZXing library"""
    try:
        cmd = create_local_java_command(image_path)
        if debug:
            print(f"\n  DEBUG: Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, 
                               timeout=30, check=False)
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if debug:
            print(f"  DEBUG: Return code: {result.returncode}")
            print(f"  DEBUG: stdout length: {len(output)}")
            print(f"  DEBUG: stdout content:\n{output}")
            if stderr:
                print(f"  DEBUG: stderr:\n{stderr}")
        
        # Even if it says "No barcode found", return the output for debugging
        if output:
            return output
        return None
    except subprocess.TimeoutExpired:
        if debug:
            print("  DEBUG: Command timed out")
        return None
    except Exception as e:
        if debug:
            print(f"  DEBUG: Exception: {e}")
        return None

def parse_zxing_output(output):
    """Parse ZXing output to extract decoded text and points"""
    lines = output.splitlines()
    decoded_text = None
    points = []
    
    # First non-empty line that doesn't start with "file://" or "  Point" is usually the decoded text
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("file://"):
            continue
        if line.startswith("  Point"):
            # Extract point coordinates
            try:
                parts = line.split(":")[1].strip().replace("(", "").replace(")", "").split(",")
                x = int(float(parts[0].strip()))
                y = int(float(parts[1].strip()))
                points.append((x, y))
            except:
                pass
            continue
        if not decoded_text and "No barcode found" not in line:
            decoded_text = line
            break
    
    # If we didn't find text in the loop, try first line
    if not decoded_text and lines:
        first_line = lines[0].strip()
        if not first_line.startswith("file://") and "No barcode found" not in first_line:
            decoded_text = first_line
    
    return decoded_text, points

def main():
    """Main decoding function"""
    print("PDF417 Barcode Decoder")
    print("=" * 50)
    
    # Validate files
    validate_files()
    
    # Check if Java is available
    if shutil.which("java") is None:
        print("Error: Java is not installed or not in PATH")
        print("Please install Java JDK (version 17 or later)")
        sys.exit(1)
    
    # Load the original image
    print(f"Loading image: {BARCODE_IMAGE}")
    img = cv2.imread(BARCODE_IMAGE)
    if img is None:
        print(f"Error: Unable to read image {BARCODE_IMAGE}")
        sys.exit(1)
    
    print(f"Image loaded successfully: {img.shape}")
    
    # Create candidates list - start with original
    candidates = [BARCODE_IMAGE]
    temp_files = []
    
    # Create preprocessed versions
    print("\nCreating enhanced image variants...")
    enhanced_images = preprocess_image(img)
    for name, img_data in enhanced_images:
        cv2.imwrite(name, img_data)
        candidates.append(name)
        temp_files.append(name)
    
    # Create rotated versions of original
    print("Creating rotated versions...")
    rotated_variants = {
        "rot90.jpg": cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
        "rot180.jpg": cv2.rotate(img, cv2.ROTATE_180),
        "rot270.jpg": cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),
    }
    for name, mat in rotated_variants.items():
        cv2.imwrite(name, mat)
        candidates.append(name)
        temp_files.append(name)
    
    print(f"Total variants to try: {len(candidates)}")
    
    # Try decoding each candidate
    print("\nAttempting to decode...")
    decoded_text = None
    decoded_points = []
    successful_variant = None
    
    # First, try with debug on for the first candidate
    print(f"\n[DEBUG MODE] Trying first variant with full debug output:")
    print(f"Trying variant 1/{len(candidates)}: {candidates[0]}")
    output = decode_with_zxing(candidates[0], debug=True)
    
    if output:
        text, points = parse_zxing_output(output)
        print(f"  DEBUG: Parsed text: {repr(text)}")
        print(f"  DEBUG: Parsed points: {len(points)}")
        
        if text and "No barcode found" not in text:
            decoded_text = text
            decoded_points = points
            successful_variant = candidates[0]
            print("\n[SUCCESS] Decoded on first try!")
    
    # If first didn't work, try all others
    if not decoded_text:
        print(f"\n[Standard mode] Trying remaining variants...")
        for i, candidate in enumerate(candidates[1:], 2):
            print(f"Trying variant {i}/{len(candidates)}: {candidate}", end=" ... ")
            output = decode_with_zxing(candidate, debug=False)
            
            if output:
                text, points = parse_zxing_output(output)
                if text and "No barcode found" not in text:
                    decoded_text = text
                    decoded_points = points
                    successful_variant = candidate
                    print("SUCCESS!")
                    break
            print("failed")
    
    # Clean up temporary files
    print("\nCleaning up temporary files...")
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
    
    # Display results
    print("\n" + "=" * 50)
    print("DECODING RESULTS")
    print("=" * 50)
    
    if decoded_text:
        print(f"\n[SUCCESS] Successfully decoded from: {successful_variant}")
        print(f"\nDecoded Text:")
        print("-" * 50)
        print(decoded_text)
        print("-" * 50)
        
        if decoded_points:
            print(f"\nBounding box points: {len(decoded_points)} points detected")
            
            # Draw bounding box on original image
            if len(decoded_points) >= 4:
                annotated_img = img.copy()
                points_array = np.array(decoded_points, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_img, [points_array], isClosed=True, 
                            color=(0, 255, 0), thickness=3)
                
                annotated_path = "annotated_barcode.png"
                cv2.imwrite(annotated_path, annotated_img)
                print(f"Annotated image saved as: {annotated_path}")
        else:
            print("\n(No bounding box points found)")
    else:
        print("\n[FAILED] Could not decode the PDF417 barcode")
        print("Tried all image variants and preprocessing methods")
        print("The barcode might be damaged or the image quality is insufficient")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()

