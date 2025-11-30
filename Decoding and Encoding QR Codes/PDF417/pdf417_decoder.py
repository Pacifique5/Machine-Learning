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
barcode_image = sys.argv[1] if len(sys.argv) > 1 else "my_pdf417.jpg"

# Normalize paths for Docker and local Java
image_abs = os.path.abspath(barcode_image)
image_abs_forward = image_abs.replace("\\", "/")
image_name = os.path.basename(barcode_image)

# Validate required files
for file in [javase_jar, core_jar, jcommander_jar, barcode_image]:
    if not os.path.exists(file):
        print(f"Error: {file} not found!")
        exit(1)

def docker_command():
    # Docker command to detect the barcode and get its position
    return [
        "docker", "run", "--rm",
        "-v", f"{os.getcwd()}:/app",
        "openjdk:17",
        "java", "-cp",
        f"/app/{javase_jar}:/app/{core_jar}:/app/{jcommander_jar}",
        "com.google.zxing.client.j2se.CommandLineRunner",
        f"/app/{image_name}"
    ]

def local_java_command():
    # Local Java command (Windows uses ';' as classpath separator)
    classpath = f"{javase_jar};{core_jar};{jcommander_jar}"
    # Build a proper file URI to avoid ZXing URI parsing issues on Windows drive letters
    file_uri = f"file:///{quote(image_abs_forward)}"
    return [
        "java", "-cp", classpath,
        "com.google.zxing.client.j2se.CommandLineRunner",
        file_uri
    ]

def attempt_decode(current_image_path: str) -> str:
    """Run ZXing through Docker or local Java for the given image path.
    Returns the raw stdout from ZXing."""
    global image_abs, image_abs_forward, image_name

    # Update normalized paths for this candidate image
    image_abs = os.path.abspath(current_image_path)
    image_abs_forward = image_abs.replace("\\", "/")
    image_name = os.path.basename(current_image_path)

    out = ""
    ran = False

    if shutil.which("docker") is not None:
        try:
            result = subprocess.run(docker_command(), capture_output=True, text=True, check=True)
            out = result.stdout.strip()
            ran = True
        except Exception as e:
            print("Docker failed, attempting local Java fallback:", e)

    if not ran:
        if shutil.which("java") is None:
            print("Neither Docker nor Java is available. Install Docker Desktop or a JDK (Java 17).")
            sys.exit(1)
        try:
            result = subprocess.run(local_java_command(), capture_output=True, text=True, check=True)
            out = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print("Local Java decoding failed:")
            print(e.stderr)
            sys.exit(1)

    return out

# Try original and rotated variants for robustness
candidates = [barcode_image]
try:
    img = cv2.imread(barcode_image)
    if img is not None:
        variants = {
            "rot90.jpg": cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
            "rot270.jpg": cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),
            "rot180.jpg": cv2.rotate(img, cv2.ROTATE_180),
        }
        for name, mat in variants.items():
            cv2.imwrite(name, mat)
            candidates.append(name)
except Exception:
    pass

output = ""
for candidate in candidates:
    output = attempt_decode(candidate)
    if "No barcode found" not in output:
        break

print("Decoded Output:")
print(output)

# Parse the ZXing output for barcode position
points = []
for line in output.splitlines():
    if line.startswith("  Point"):
        parts = line.split(":")[1].strip().replace("(", "").replace(")", "").split(",")
        points.append((int(float(parts[0])), int(float(parts[1]))))

# If points are found, draw a bounding polygon
if len(points) >= 4:
    # Load the image with OpenCV
    image = cv2.imread(barcode_image)
    if image is None:
        print("Error: Unable to read the image!")
        exit(1)

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