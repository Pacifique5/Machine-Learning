import cv2
import numpy as np
from pyzbar import pyzbar

def preprocess_image(image_path):
    """Preprocess image to improve barcode detection"""
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    return gray, thresh

def decode_pdf417(image_path):
    """Try to decode PDF417 barcode using pyzbar"""
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # Try original image
    decoded = pyzbar.decode(img)
    if decoded:
        return decoded
    
    # Try grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    decoded = pyzbar.decode(gray)
    if decoded:
        return decoded
    
    # Try preprocessing
    gray, thresh = preprocess_image(image_path)
    if gray is not None:
        decoded = pyzbar.decode(gray)
        if decoded:
            return decoded
        decoded = pyzbar.decode(thresh)
        if decoded:
            return decoded
    
    # Try rotated versions
    for angle in [90, 180, 270]:
        if angle == 90:
            rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            rotated = cv2.rotate(img, cv2.ROTATE_180)
        else:
            rotated = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        decoded = pyzbar.decode(rotated)
        if decoded:
            return decoded
        
        gray_rotated = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
        decoded = pyzbar.decode(gray_rotated)
        if decoded:
            return decoded
    
    return None

if __name__ == "__main__":
    import sys
    image_path = sys.argv[1] if len(sys.argv) > 1 else "pdf417.jpg"
    
    decoded = decode_pdf417(image_path)
    
    if decoded:
        print("Decoded Output:")
        for barcode in decoded:
            print(f"Type: {barcode.type}")
            print(f"Data: {barcode.data.decode('utf-8')}")
            print(f"Polygon points: {barcode.polygon}")
    else:
        print("No barcode found")

