import os
import argparse
import zipfile
import io
from PIL import Image
from rembg import remove
from tqdm import tqdm
import time
from PIL import UnidentifiedImageError


def process_images(input_path, output_path, size_filter):
    start_time = time.time()
    size_filter = tuple(map(int, size_filter.split('x')))
    file_counter = 0
    zip_counter = 0
    
    os.makedirs(output_path, exist_ok=True)

    # Check if input_path is a directory or a file
    if os.path.isdir(input_path):
        filenames = [os.path.join(input_path, filename) for filename in os.listdir(input_path) if filename.lower().endswith('.zip')]
    elif os.path.isfile(input_path) and input_path.lower().endswith('.zip'):
        filenames = [input_path]
    else:
        print(f"Invalid input_path. It must be a directory or a .zip file.")
        return

    for filename in filenames:
        zip_start_time = time.time()
        with zipfile.ZipFile(filename, 'r') as input_zip:
            with zipfile.ZipFile(os.path.join(output_path, os.path.splitext(os.path.basename(filename))[0]) + '.zip', 'w') as output_zip:
                for name in tqdm(input_zip.namelist(), desc=f"Processing {filename}"):
                    if not name.endswith(('.jpg', '.jpeg', '.png')):  # only process image files
                        continue
                    data = input_zip.read(name)
                    file_like_object = io.BytesIO(data)
                    file_counter += process_directory(file_like_object, output_zip, size_filter, name)
            zip_counter += 1
            zip_end_time = time.time()
            print(f"Processed zip file: {os.path.basename(filename)}, time taken: {zip_end_time - zip_start_time}")

    end_time = time.time()
    print(f"Processing finished. Time elapsed: {end_time - start_time} seconds")
    print(f"Total zip files processed: {zip_counter}")
    print(f"Total number of processed images: {file_counter}")

    if end_time - start_time > 0:  
        images_per_second = file_counter / (end_time - start_time)
        print(f"Images processed per second: {images_per_second}")
    else:
        print("Time measurement is too short to calculate images processed per second.")

    if file_counter > 0:
        average_time_per_image = (end_time - start_time) / file_counter
        print(f"Average time per image: {average_time_per_image}")
    else:
        print("No images processed to calculate average time per image.")


def process_directory(file_like_object, output_zip, size_filter, name):
    # Initialize the file counter
    file_counter = 0

    try:
        # Open the image file
        with Image.open(file_like_object) as img:
            # If the image is not the right size, skip it
            if img.size != size_filter:
                return 0
            
            # Split the filename and extension
            filename, extension = os.path.splitext(os.path.basename(name)) # Modify here to get only filename
            # Append "_bg_removed" to the filename before the extension
            bg_removed_name = f"{filename}_bg_removed{extension}"

            # Get the image data with the background removed
            output = remove(file_like_object.getvalue())

            # Reset pointer
            file_like_object.seek(0)
            # Save the original image to the zip file
            output_zip.writestr('images/original_images/' + os.path.basename(name), file_like_object.read()) # Modify here to get only filename

            # Save the image with the background removed to the zip file
            output_zip.writestr('images/bg_removed/' + bg_removed_name, output)

            # Increase the file counter
            file_counter += 1

    except UnidentifiedImageError:
        print(f"Failed to process file {name}. It may not be a valid image file.")

    except Exception as e:
        print(f"Failed to process file {name}. Error: {e}")

    # Return the number of files processed
    return file_counter


def main():
    parser = argparse.ArgumentParser(description='Remove backgrounds from images in a zip file.')
    parser.add_argument('--dataset_path', required=True, help='Input directory path')
    parser.add_argument('--size_filter', default='512x512', help='Filter images by size (WIDTHxHEIGHT)')
    parser.add_argument('--output_path', required=True, help='Output path')
    args = parser.parse_args()
    process_images(args.dataset_path, args.output_path, args.size_filter)

if __name__ == '__main__':
    main()
