import pytest
import os
import shutil
from background_remover import process_images

def test_background_remover():
    # The input_path should point to a zip file for testing
    input_path = "./test/test_zip_files/pixel-art-pinterest-001.zip"
    # Output path where processed files will be saved
    output_path = "./test_tmp"
    size_filter = '512x512'

    # Process the single zip file
    process_images(input_path, output_path, size_filter)

    # After running process_images, we should have a new zip file in the output directory.
    assert len(os.listdir(output_path)) > 0

    # Clean up the output directory after the test
    shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)
