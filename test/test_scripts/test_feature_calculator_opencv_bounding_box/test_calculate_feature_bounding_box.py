import os
import sys
sys.path.insert(0, os.getcwd())
from feature_calculator_opencv_bounding_box.calculate_feature_bounding_box import process_zip_file
import zipfile

def test_feature_calculator_opencv_bounding_box():
    # The input_path should point to a zip file for testing
    input_path = "./test/test_zip_files/000001.zip"
    zip_name = os.path.splitext(os.path.basename(input_path))[0]

    # Process the single zip file
    process_zip_file(input_path)

    # Open the zip file
    with zipfile.ZipFile(input_path, 'r') as z:
        # Check if the 'open-cv-bounding-box.json' file is in the zip file
        json_path = f'{zip_name}/features/open-cv-bounding-box.json'
        assert json_path in z.namelist(), f"{json_path} not found in the zip file"
