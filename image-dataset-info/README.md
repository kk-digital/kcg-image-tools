# ImageDatasetInfo
> A standalone tool for obtaining the metadata of a given directory containing images. 
## Tool Description

given a directory containing images, process all those images and write a file with the metadata (in current working directory)
of those processed images, which are `image_path` , `image_name`, `image_blake2b_hash`, `image_size_bytes` , `image_dims_tuple`, `image_dims_string` and `unique_colors`. 


## Installation
All that's needed to start using ImageDatasetInfo is to install the dependencies using the command
```
pip install -r src/to/dir/requirements.txt
```

## CLI Parameters

* `source_directory` _[str]_ - _[required]_ - The source directory of the dataset containing the required images to be cleaned. 
* `output_type` _[str]_ - _[optional]_ - The output type of the produced metadata file, `csv` or `json`, default is `csv`  

* `num_workers` _[int]_ - _[optional]_ - number of workers (threads) to be used in the process, default value is `8`.

## Example Usage

```sh
python src/to/dir/ImageDatasetInfo.py --source_directory='./my-dataset' --output_type='json' --num_workers=20
```

The tool will immediately starts working, and output the status after processing each 100 images.

Example Output 
```
Finished 100 out of 1128 images, 100 of them are valid and 0 are corrupted.
Finished 200 out of 1128 images, 200 of them are valid and 0 are corrupted.
Finished 300 out of 1128 images, 300 of them are valid and 0 are corrupted.
Finished 400 out of 1128 images, 400 of them are valid and 0 are corrupted.
Finished 500 out of 1128 images, 500 of them are valid and 0 are corrupted.
Finished 600 out of 1128 images, 600 of them are valid and 0 are corrupted.
```

In the current working directory there will be two `json` or `csv` files written the first one stores info about all the valid processed images which is called `valid-images-metadata` and the other contains info about the corrupted images and is called `failed-images-metadata`.

Example of `valid-images-metadata.json`
```json
[
    {
        "image_path": "./my-dataset\\img1.png",
        "image_name": "img1",
        "image_blake2b_hash": "e47eb1cf20d368f438c2adcfc128333efccf8324ec01ada9742b12989979192a31af8d0327de590e89b0a16e8940d2bb7b0e2e7f5830b7b42695090e5f993d13",
        "image_size_bytes": 3460,
        "image_dims_tuple": [
            38,
            135
        ],
        "image_dims_string": "38x135",
        "unique_colors": 16
    },
    {
        "image_path": "./my-dataset\\img2.png",
        "image_name": "img2",
        "image_blake2b_hash": "1ad883939d2a42cd747238a885814ba278b991a15805d5b47f1a6074b65116a87915e58c88d82a4dc33633a67c9db12dd9ecc15a309a0e5b5c2700be97d33fb9",
        "image_size_bytes": 131353,
        "image_dims_tuple": [
            800,
            608
        ],
        "image_dims_string": "800x608",
        "unique_colors": 27
    },
]
```
Example of `failed-images-metadata.json`
```json
[
    {
        "image_path": "./my-dataset\\corrupted-image.png",
        "image_name": "corrupted-image",
        "image_size_bytes": 9815
    }
]
```
