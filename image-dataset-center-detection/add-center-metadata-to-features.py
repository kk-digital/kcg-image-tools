import argparse
import json
import zipfile

def update_zipped_json(zip_file_path, json_file_path):
    # Read the metadata JSON file
    with open(json_file_path, 'r') as json_file:
        metadata_json_data = json.load(json_file)

    # Open the ZIP file in read mode
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        # Find JSON files inside the ZIP file
        json_files = [file for file in zip_file.namelist() if file.endswith('.json')]

        for json_file_name in json_files:
            # Read each JSON file in the ZIP file
            with zip_file.open(json_file_name) as zipped_json_file:
                zipped_json_data = json.load(zipped_json_file)

                # Iterate through all 'masked-image' values in the metadata JSON file
                for masked_image_value in metadata_json_data:
                    # Search for the object with the matching 'file-name' in the zipped JSON file
                    for obj in zipped_json_data:
                        if obj['file-name'] == masked_image_value['masked-image']:
                            # Add the desired key-value pairs from the metadata JSON file to the matching object
                            obj['extra-data'] = {}
                            obj['extra-data']['percentage-outside'] = masked_image_value['percentage-outside']
                            obj['extra-data']['total-pixels'] = masked_image_value['total-pixels']
                            obj['extra-data']['outside-pixels'] = masked_image_value['outside-pixels']
                            obj['extra-data']['log10-outside-pixels'] = masked_image_value['log10-outside-pixels']
                            obj['extra-data']['log2-outside-pixels'] = masked_image_value['log2-outside-pixels']
                            break

            # Write the updated zipped JSON file to a new file
            updated_zip_file_path = zip_file_path + '2'
            with zipfile.ZipFile(updated_zip_file_path, 'w') as updated_zip_file:
                for json_file_name in json_files:
                    # Convert the updated zipped JSON data to a string
                    updated_json_data = json.dumps(zipped_json_data, indent=4)

                    # Write the updated JSON data to the updated ZIP file
                    updated_zip_file.writestr(json_file_name, updated_json_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update zipped JSON files.')
    parser.add_argument('--image-dataset-path', required=True,
                        help='Path to the ZIP file containing the JSON files.')
    parser.add_argument('--metadata-json-path', required=True,
                        help='Path to the JSON file with the metadata to add to the ZIP files.')

    args = parser.parse_args()

    # Call the function with the provided CLI arguments
    update_zipped_json(args.image_dataset_path, args.metadata_json_path)

    print("Done")
