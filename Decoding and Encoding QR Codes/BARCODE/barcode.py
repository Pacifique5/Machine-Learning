import cv2
import numpy as np
from pyzbar.pyzbar import decode
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
    
    # Inverted (sometimes needed for dark barcodes on light background)
    inverted = cv2.bitwise_not(gray)
    enhanced.append(("Inverted", inverted))
    
    return enhanced

def decode_all_barcodes(image_path):
    """Decode all types of barcodes from image with multiple preprocessing attempts"""
    
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return None
    
    print("="*70)
    print("UNIVERSAL BARCODE DECODER")
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
        barcodes = decode(image)
        
        if barcodes:
            print(f"[SUCCESS] Decoded using original image")
        else:
            print("[INFO] Original image failed, trying enhanced variants...")
            
            # Try preprocessed versions
            enhanced_images = preprocess_image(image)
            
            for name, img_data in enhanced_images:
                print(f"  Trying: {name}...", end=" ")
                try:
                    barcodes = decode(img_data)
                    
                    if barcodes:
                        print("SUCCESS!")
                        break
                    else:
                        print("failed")
                except Exception as e:
                    print(f"error: {e}")
        
        if not barcodes:
            print("\n[FAILED] No barcodes detected after trying all variants!")
            return None
        
        print(f"[SUCCESS] Found {len(barcodes)} barcode(s)\n")
        
        results = []
        
        for i, barcode in enumerate(barcodes, 1):
            # Extract data
            try:
                barcode_data = barcode.data.decode('utf-8')
            except:
                barcode_data = str(barcode.data)
            
            barcode_type = barcode.type
            (x, y, w, h) = barcode.rect
            
            results.append({
                'type': barcode_type,
                'data': barcode_data
            })
            
            # Print details
            print(f"Barcode #{i}")
            print(f"   Type: {barcode_type}")
            print(f"   Data: {barcode_data}")
            print(f"   Position: (x={x}, y={y})")
            print(f"   Size: {w}x{h} pixels")
            
            # Special handling for EAN-13
            if barcode_type == 'EAN13' and len(barcode_data) == 13:
                print(f"\n   EAN-13 Structure:")
                print(f"      Prefix: {barcode_data[:3]}")
                print(f"      Manufacturer: {barcode_data[3:7]}")
                print(f"      Product: {barcode_data[7:12]}")
                print(f"      Check digit: {barcode_data[12]}")
            
            print("-" * 70)
            
            # Visualize
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
            
            label = f"{barcode_type}: {barcode_data}"
            cv2.putText(image, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Save and display
        output_path = "annotated_barcode.png"
        cv2.imwrite(output_path, image)
        print(f"\n[INFO] Annotated image saved: {output_path}")
        
        cv2.imshow("Barcode Detection", image)
        print("\n[INFO] Press any key to close the preview window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return results
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Use barcode.jpg as the image file
    image_file = "barcode.jpg"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
    
    # Decode all barcodes
    results = decode_all_barcodes(image_file)
    
    if results:
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        for i, item in enumerate(results, 1):
            print(f"{i}. [{item['type']}] {item['data']}")