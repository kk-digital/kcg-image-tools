import os
import sys
import shutil
sys.path.insert(0, os.getcwd())
from image_background_remover.background_remover import remove_backgrounds

def test_background_remover():
    # The input_path should point to a zip file for testing
    input_path = "./test/test_zip_files/pixel-art-pinterest-001.zip"
    # Output path where processed files will be saved
    output_path = "./test_tmp"
    size_filter = '512x512'

    # Process the single zip file
    remove_backgrounds(input_path, output_path, size_filter)

    # After running remove_backgrounds, we should have a new zip file in the output directory.
    assert len(os.listdir(output_path)) > 0

    # Clean up the output directory after the test
    shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)
