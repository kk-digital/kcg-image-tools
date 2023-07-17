import os
import zipfile
import hashlib
import json
import argparse
from tqdm import tqdm
import cv2
import numpy as np

def open_zip_to_ram(zip_path):
    file_data = {}
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                with zip_ref.open(file_info) as file:
                    file_data[file_info.filename] = file.read()
        print(f"Zip file '{zip_path}' has been loaded into RAM.")
    except Exception as e:
        print(f"Error: {e}")
    return file_data

def parse_json(json_data):
    try:
        return json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"Error in parsing JSON: {e}")
        return None

def filter_and_process_json_files(file_data):
    filtered_json_files = {}

    for file_name, binary_data in file_data.items():
        if file_name.endswith('.json'):
            json_content = parse_json(binary_data)
            if json_content:
                for record in json_content:
                    if 'file-name' in record and record['file-name'].endswith('_bg_removed.jpeg'):
                        filtered_json_files[os.path.basename(record['file-name'])] = {
                            'file_name': record.get('file-name'),
                            'file_hash': record.get('file-hash'),
                            'feature_vector': record.get('feature-vector')
                        }
    return filtered_json_files

def get_bounding_box_details(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray)
    ret, thresh = cv2.threshold(inverted, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]

    if not contours:
        return None

    cnt = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cnt)
    object_center = (x + w // 2, y + h // 2) 

    return object_center, (x, y, w, h)

def calculate_center_offsets(img_center, object_center):
    x_offset = object_center[0] - img_center[0]
    y_offset = object_center[1] - img_center[1]
    distance_squared = x_offset**2 + y_offset**2
    distance = np.sqrt(distance_squared)

    return distance_squared, distance, x_offset, y_offset

def process_zip_files(input_path, output_path):

    if os.path.isdir(input_path):  # The input is a directory
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.endswith('.zip'):
                    zip_file_path = os.path.join(root, file)
                    process_zip_file(zip_file_path, output_path)
    elif os.path.isfile(input_path):  # The input is a file
        if input_path.endswith('.zip'):
            process_zip_file(input_path, output_path)

def process_zip_file(zip_file_path, output_path):
    all_records = []
    file_data = open_zip_to_ram(zip_file_path)
    json_files = filter_and_process_json_files(file_data)

    for file_name in tqdm(file_data.keys(), desc='Processing images', unit='image'):  
         if 'images' in file_name and '_bg_removed.jpeg' in file_name:
            img_binary = file_data[file_name]
            img = cv2.imdecode(np.frombuffer(img_binary, np.uint8), -1)
            img_center = (img.shape[1] // 2, img.shape[0] // 2)
            object_center, bbox = get_bounding_box_details(img)

            if object_center and bbox:
                x, y, w, h = bbox
                distance_squared, distance, x_offset, y_offset = calculate_center_offsets(img_center, object_center)

                feature_vector = json_files[os.path.basename(file_name)].pop('feature_vector')
                json_files[os.path.basename(file_name)].update({
                    'dist_to_center_squared': distance_squared,
                    'dist_to_center': distance,
                    'image-center-offset-x': x_offset,
                    'image-center-offset-y': y_offset,
                    'bounding-box-center-x': object_center[0],
                    'bounding-box-center-y': object_center[1],
                    'bounding-box-width': w,
                    'bounding-box-height': h,
                    'feature_vector': feature_vector  
                })
                all_records.append(json_files[os.path.basename(file_name)])

    os.makedirs(output_path, exist_ok=True)
    # Generate output file name based on input file name
    output_file = os.path.join(output_path, f"{os.path.splitext(os.path.basename(zip_file_path))[0]}.json")
    with open(output_file, 'w') as f:
        json.dump(all_records, f, indent=3)
        print(f"Output written to {output_file}")

parser = argparse.ArgumentParser(description='Process JSON records from zip files.')
parser.add_argument('--input_path', type=str, default='.', help='Path to directory containing zip files or single zip file.')  
parser.add_argument('--output_path', type=str, default='.', help='Path to output file.')

if __name__ == "__main__":
    args = parser.parse_args()
    process_zip_files(args.input_path, args.output_path)
