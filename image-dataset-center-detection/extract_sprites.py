import os
import cv2
import argparse
import numpy as np

def resize_and_fill(image, desired_size):
    # Resize the image while preserving proportions
    height, width = image.shape[:2]
    aspect_ratio = width / float(height)
    if aspect_ratio > 1:
        new_width = desired_size
        new_height = int(desired_size / aspect_ratio)
    else:
        new_height = desired_size
        new_width = int(desired_size * aspect_ratio)

    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Create a blank 64x64 image with a transparent background
    final_image = np.zeros((desired_size, desired_size, 4), dtype=np.uint8)
    final_image[:, :, 3] = 0  # Set alpha channel to 0 (fully transparent)

    # Calculate the center position to paste the resized image
    y_offset = (desired_size - new_height) // 2
    x_offset = (desired_size - new_width) // 2

    # Paste the resized image onto the blank image
    final_image[y_offset:y_offset+new_height, x_offset:x_offset+new_width, :3] = resized_image

    # Set alpha channel to 255 (fully opaque) for the regions where the image is present
    final_image[:, :, 3] = (final_image[:, :, :3].sum(axis=2) > 0).astype(np.uint8) * 255

    return final_image

def detect_sprites(input_dir, output_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            image_path = os.path.join(input_dir, filename)
            image = cv2.imread(image_path)

            # Convert the image to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply GaussianBlur to reduce noise and improve edge detection
            blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

            # Perform Canny edge detection
            edges = cv2.Canny(blurred_image, threshold1=100, threshold2=300)

            # Find contours in the edges
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # For each contour, create a bounding box and save the sprite
            for index, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                sprite = image[y:y+h, x:x+w]

                # Resize and fill the sprite to 64x64 with transparency
                sprite_resized = resize_and_fill(sprite, desired_size=64)

                # Save the individual sprite to the output directory with a new filename
                cv2.imwrite(os.path.join(output_dir, f"{filename}_sprite_{index}.png"), sprite_resized)

def main():
    parser = argparse.ArgumentParser(description="Pixel Art Sprite Sheet Separation and Resize")
    parser.add_argument("--input-dir", required=True, help="Input directory containing sprite sheets")
    parser.add_argument("--output-dir", required=True, help="Output directory to save separated sprites")
    args = parser.parse_args()

    detect_sprites(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
