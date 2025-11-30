"""
Aztec Code Decoder using aztec-tool library
Aztec codes are 2D barcodes used in transport, ticketing, and identification
"""

import cv2
import numpy as np
import os
import sys

try:
    from aztec_tool import decode as aztec_decode
    AZTEC_TOOL_AVAILABLE = True
except ImportError:
    AZTEC_TOOL_AVAILABLE = False
    try:
        from pyzbar.pyzbar import decode
        PYZBAR_AVAILABLE = True
    except ImportError:
        PYZBAR_AVAILABLE = False

def preprocess_image(img):
    """Create multiple enhanced versions of the image for better detection"""
    enhanced = []
    
    # Original grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced.append(("Original grayscale", gray))
    
    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    enhanced.append(("Adaptive threshold", thresh))
    
    # Otsu threshold
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    enhanced.append(("Otsu threshold", otsu))
    
    # Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)
    enhanced.append(("CLAHE enhanced", clahe_img))
    
    # Denoised
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    enhanced.append(("Denoised", denoised))
    
    # Upscaled 2x for better detail
    upscaled = cv2.resize(gray, (gray.shape[1] * 2, gray.shape[0] * 2), 
                         interpolation=cv2.INTER_CUBIC)
    enhanced.append(("Upscaled 2x", upscaled))
    
    # Inverted (sometimes needed for dark codes on light background)
    inverted = cv2.bitwise_not(gray)
    enhanced.append(("Inverted", inverted))
    
    return enhanced

def decode_aztec_code(image_path):
    """Decode Aztec code from image with multiple preprocessing attempts"""
    
    # Validate file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return None
    
    print("="*70)
    print("AZTEC CODE DECODER")
    print("="*70)
    print(f"Processing: {image_path}\n")
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Unable to read image file '{image_path}'")
            return None
        
        print(f"Image loaded: {image.shape}")
        
        if not AZTEC_TOOL_AVAILABLE and not PYZBAR_AVAILABLE:
            print("[ERROR] No Aztec decoding library available!")
            print("Please install: pip install aztec-tool")
            return None
        
        decoded_data = None
        aztec_codes = []
        
        # Try decoding with aztec-tool first
        if AZTEC_TOOL_AVAILABLE:
            try:
                print("[INFO] Trying aztec-tool library...")
                decoded_data = aztec_decode(image_path)
                if decoded_data:
                    print(f"[SUCCESS] Decoded using aztec-tool on original image")
                    # Create a mock code object for consistency
                    aztec_codes = [type('Code', (), {
                        'data': decoded_data.encode('utf-8'),
                        'type': 'AZTEC',
                        'rect': cv2.boundingRect(cv2.findNonZero(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)))
                    })()]
            except Exception as e:
                print(f"[INFO] aztec-tool failed: {e}")
        
        # If aztec-tool didn't work, try with preprocessing
        if not aztec_codes and AZTEC_TOOL_AVAILABLE:
            print("[INFO] Trying enhanced variants with aztec-tool...")
            enhanced_images = preprocess_image(image)
            
            for name, img_data in enhanced_images:
                print(f"  Trying: {name}...", end=" ")
                try:
                    # Save preprocessed image temporarily
                    temp_path = f"temp_{name}"
                    cv2.imwrite(temp_path, img_data)
                    decoded_data = aztec_decode(temp_path)
                    os.remove(temp_path)
                    
                    if decoded_data:
                        print("SUCCESS!")
                        aztec_codes = [type('Code', (), {
                            'data': decoded_data.encode('utf-8'),
                            'type': 'AZTEC',
                            'rect': (0, 0, image.shape[1], image.shape[0])
                        })()]
                        break
                    else:
                        print("failed")
                except Exception as e:
                    print(f"error: {e}")
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except:
                        pass
        
        if not aztec_codes:
            print("\n[FAILED] No Aztec code detected after trying all variants!")
            print("\nTips:")
            print("  - Ensure the bulls-eye center is clearly visible")
            print("  - Check if the image has good contrast")
            print("  - Try improving image quality/resolution")
            print("  - Ensure proper lighting and focus")
            return None
        
        print(f"[SUCCESS] Found {len(aztec_codes)} Aztec code(s)\n")
        
        decoded_data_list = []
        
        for i, aztec in enumerate(aztec_codes, 1):
            # Extract data
            try:
                if hasattr(aztec.data, 'decode'):
                    aztec_data = aztec.data.decode('utf-8')
                else:
                    aztec_data = str(aztec.data)
            except:
                aztec_data = str(aztec.data)
            
            aztec_type = getattr(aztec, 'type', 'AZTEC')
            rect = getattr(aztec, 'rect', None)
            if rect:
                (x, y, w, h) = rect
            else:
                # Default to full image if no rect available
                (x, y, w, h) = (0, 0, image.shape[1], image.shape[0])
            
            decoded_data_list.append(aztec_data)
            
            # Print details
            print(f"Aztec Code #{i}")
            print(f"   Data: {aztec_data}")
            print(f"   Type: {aztec_type}")
            print(f"   Position: (x={x}, y={y})")
            print(f"   Size: {w}x{h} pixels")
            print(f"   Data Length: {len(aztec_data)} characters")
            
            # Detect content type
            if aztec_data.startswith('http://') or aztec_data.startswith('https://'):
                print(f"   Content Type: URL")
            elif '@' in aztec_data and '.' in aztec_data:
                print(f"   Content Type: Email/Contact")
            elif aztec_data.isdigit():
                print(f"   Content Type: Numeric ID")
            elif aztec_data.startswith('BEGIN:'):
                print(f"   Content Type: vCard")
            else:
                print(f"   Content Type: Text/Data")
            
            print("-" * 70)
            
            # Draw rectangle around Aztec code
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
            
            # Draw polygon outline if available
            points = getattr(aztec, 'polygon', None)
            if points and len(points) >= 4:
                try:
                    pts = [(int(p.x), int(p.y)) for p in points]
                    for j in range(len(pts)):
                        cv2.line(image, pts[j], pts[(j+1) % len(pts)], (255, 0, 0), 2)
                except:
                    pass
            
            # Add text label
            label = f"AZTEC-{i}"
            cv2.putText(image, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save annotated image
        output_path = "annotated_aztec.png"
        cv2.imwrite(output_path, image)
        print(f"\n[INFO] Annotated image saved: {output_path}")
        
        # Display
        cv2.imshow("Aztec Code Detection", image)
        print("\n[INFO] Press any key to close the preview window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return decoded_data_list
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Use aztec.jpg as the image file
    image_file = "aztec.jpg"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
    
    # Decode the Aztec code
    results = decode_aztec_code(image_file)
    
    if results:
        print("\n" + "="*70)
        print("SUMMARY - ALL DECODED DATA")
        print("="*70)
        for i, data in enumerate(results, 1):
            print(f"{i}. {data}")