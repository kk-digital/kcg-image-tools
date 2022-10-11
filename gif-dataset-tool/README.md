# GIFDatasetTools
> A standalone tool for manipulating GIF images. 

## Tool Description

Given a source directory containing GIF images, the tool go through all the images inside the directory and computes each image metadata saves the result into a `JSON` file with name `images_metadata.json`, and an option to extract the frames of each image and specifying a max number of frames to extract for each image. 

## Installation
All what is needed to start using GIFDatasetTools is to install the dependencies using the command
```
pip install -r src/to/dir/requirements.txt
```

## CLI Parameters

* `folder_path` _[string]_ - _[required]_ - path to the folder contains the GIF images to process.
* `output_folder_path` _[string]_ - _[required]_ - path to the folder to write the results to

* `extract_frames` _[bool]_ - _[optional]_ option to extract frames out of the GIF image or not, default is `True` 

* `frames_limit` _[int]_ - _[optional]_ - the max number of frames to extract from each GIF image in the folder.

    if `frames_limit >= actual_frames_number`  then all frames is being returned. 

    if `frames_limit < actual_frames_number` then `limit` number of frames are selected at random and returned. 

    if `frames_limit is 0`, then all frames will be extracted (default)
                

* `num_processes` _[int]_ - _[optional]_ - number of processes to use for executing the task, default is the number of cores of the processor of the host machine. 

## Example Usage

```sh
python .\GIFDatasetTool.py process-gif-dataset --folder_path "./gif-images" --output_folder_path "./extracted-frames" --extract_frames True --frames_limit 5
```

Example output for the `images_metadata.json` file. 
```json
[
    {
        "file_size": 3553085,
        "format": "gif",
        "image_size": "(480,362)",
        "number_of_frames": 51,
        "original_file_name": "C:\\Users\\MahmoudSaudi\\Documents\\KCG\\repo\\image-tools\\gif-dataset-tool\\gif-images\\giphy (1).gif",
        "sha256": "7b5063d6143209e64fe4b90b4b8388911e6454e30eae9781e3dcb2641d187a85"
    },
    {
        "file_size": 425426,
        "format": "gif",
        "image_size": "(250,275)",
        "number_of_frames": 18,
        "original_file_name": "C:\\Users\\MahmoudSaudi\\Documents\\KCG\\repo\\image-tools\\gif-dataset-tool\\gif-images\\giphy (2).gif",
        "sha256": "eef1bae12026d6795982f94ff10f5794cf1028bf93db364bfd37bbb6a3a5ca24"
    }
]
```
