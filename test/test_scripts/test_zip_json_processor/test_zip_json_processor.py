import pytest
import os
import shutil
from zip_json_processor.zip_json_processor import process_zip_files

def test_process_zip_files():
    # The input_path should point to a zip file for testing
    input_path = "./test/test_zip_files/000001.zip"
    # Output path where processed files will be saved
    output_path = "./test_tmp"

    # Process the single zip file
    process_zip_files(input_path, output_path)

    # After running process_zip_files, we should have a new JSON file in the output directory.
    assert len(os.listdir(output_path)) > 0

    # Check if the file is a JSON file
    for file in os.listdir(output_path):
        assert file.endswith('.json')

    # Clean up the output directory after the test
    shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)


