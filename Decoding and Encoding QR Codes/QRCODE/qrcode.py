"""
QR Code Decoder using pyzbar
Best for complex QR codes and multiple QR detection
"""

import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
import os
import sys

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
    
    # Inverted (sometimes needed for dark QR codes on light background)
    inverted = cv2.bitwise_not(gray)
    enhanced.append(("Inverted", inverted))
    
    return enhanced

def decode_qr_code(image_path):
    """Decode QR code from image using pyzbar with multiple preprocessing attempts"""
    
    # Validate file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return None
    
    print("="*70)
    print("QR CODE DECODER")
    print("="*70)
    print(f"Processing: {image_path}\n")
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Unable to read image file '{image_path}'")
            return None
        
        print(f"Image loaded: {image.shape}")
        
        # Try original image first
        qr_codes = decode(image, symbols=[ZBarSymbol.QRCODE])
        
        if qr_codes:
            print(f"[SUCCESS] Decoded using original image")
        else:
            print("[INFO] Original image failed, trying enhanced variants...")
            
            # Try preprocessed versions
            enhanced_images = preprocess_image(image)
            
            for name, img_data in enhanced_images:
                print(f"  Trying: {name}...", end=" ")
                try:
                    qr_codes = decode(img_data, symbols=[ZBarSymbol.QRCODE])
                    
                    if qr_codes:
                        print("SUCCESS!")
                        break
                    else:
                        print("failed")
                except Exception as e:
                    print(f"error: {e}")
        
        if not qr_codes:
            print("\n[FAILED] No QR code detected after trying all variants!")
            print("\nTips:")
            print("  - Ensure the QR code is clear and well-lit")
            print("  - Check if all corner markers are visible")
            print("  - Try different angles or distances")
            return None
        
        print(f"[SUCCESS] Found {len(qr_codes)} QR code(s)\n")
        
        decoded_data_list = []
        
        for i, qr in enumerate(qr_codes, 1):
            # Extract data
            try:
                qr_data = qr.data.decode('utf-8')
            except:
                qr_data = str(qr.data)
            
            qr_type = qr.type
            (x, y, w, h) = qr.rect
            
            decoded_data_list.append(qr_data)
            
            # Print details
            print(f"QR Code #{i}")
            print(f"   Data: {qr_data}")
            print(f"   Type: {qr_type}")
            print(f"   Position: (x={x}, y={y})")
            print(f"   Size: {w}x{h} pixels")
            print(f"   Data Length: {len(qr_data)} characters")
            
            # Detect data type
            if qr_data.startswith('http://') or qr_data.startswith('https://'):
                print(f"   Content Type: URL/Website")
            elif qr_data.startswith('mailto:'):
                print(f"   Content Type: Email")
            elif qr_data.startswith('tel:'):
                print(f"   Content Type: Phone Number")
            elif qr_data.startswith('WIFI:'):
                print(f"   Content Type: WiFi Credentials")
            elif qr_data.startswith('BEGIN:'):
                print(f"   Content Type: vCard")
            else:
                print(f"   Content Type: Text/Other")
            
            print("-" * 70)
            
            # Draw rectangle around QR code
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
            
            # Draw corner points
            points = qr.polygon
            if len(points) == 4:
                pts = [(int(p.x), int(p.y)) for p in points]
                for j in range(4):
                    cv2.line(image, pts[j], pts[(j+1) % 4], (255, 0, 0), 3)
            
            # Add text label
            label = f"QR-{i}"
            cv2.putText(image, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save annotated image
        output_path = "annotated_qrcode.png"
        cv2.imwrite(output_path, image)
        print(f"\n[INFO] Annotated image saved: {output_path}")
        
        # Display
        cv2.imshow("QR Code Detection", image)
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
    # Use qrcode.jpg as the image file
    image_file = "qrcode.jpg"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
    
    # Decode the QR code
    results = decode_qr_code(image_file)
    
    if results:
        print("\n" + "="*70)
        print("SUMMARY - ALL DECODED DATA")
        print("="*70)
        for i, data in enumerate(results, 1):
            print(f"{i}. {data}")