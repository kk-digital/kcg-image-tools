# ImageDatasetCleaner
> A standalone tool for cleaning and validating test set images and copying the images passing certain conditions. 

## Tool Description

Given a source directory containing images or compressed files depending on the value of the flag `compressed_files_dir` the tool applies certain conditions,

if `compressed_files_dir` is `False` the tool applies some conditions and copies the valid images into the `output_directory` and two json files of the status of processed images saved in the same output directory with names `failed-images.json` and `images-info.json` if `write_status_files` was set to True. 
            
applied conditions are: 
- Make sure if the image file is not corrupted
- Checks if the image format is within the given allowed image formats (codecs) provided as an option to the cli defaults are `JPEG` and `PNG` only 
- Check if the image size is withing the range of `min size` and `max size` provided by the user as an option defaults are `(32,32)` for `min size` and `(16384,16384)` for `max size`
        
if `compressed_file_dir` is `True` Given  a source directory containing compressed files (with any type of compression) the tool applies the following steps. 

- decompress these files.
- apply the conditions stated above (in validating images part) to the images if `clean_after_decompress` is `True`,
- compress the cleaned directories back again if `compress_after_type` was set and is not `None`.

## Installation
All that's needed to start using ImageDatasetCleaner is to install the dependencies using the command
```
pip install -r src/to/dir/requirements.txt
```

> if you are going to process compressed files, the tool works with almost all compression types, you just need to make sure that this compression program is installed on your OS and found in `PATH` 

## CLI Parameters

* `source_directory` _[string]_ - _[required]_ - The source directory containing the files to apply the conditions on.
* `output_directory` _[string]_ - _[optional]_ - The directory to copy the cleaned images to it in case `compressed_files_dir` was set to `False`, default is `None`
* `compressed_files_dir` _[bool]_ - _[optional]_ - if `True` process a the compressed files inside a directory, otherwise clean the images inside the given `source_directory`, default is `False`. 

* `prefix_name` _[string]_ - _[optional]_ - name of the prefix of the result compressed files, for example if `prefix_name = 'pixel_art'`, then the result files will be `pixel_art_000001`, `pixel_art_000002` ... etc, default it "" (empty string).

* `clean_after_decompress` _[bool]_ - _[optional]_ - apply the image cleaning method to the output directories, default is `True`.

* `compress_after_type` _[string]_ - _[optional]_ - the compression type of the result directories, if was set to None then it doesn't compress the result at all. 



* `allowed_formats` _[list[str]]_ - _[optional]_ A list of strings of the allowed formats (codecs) to be marked as valid for the output dataset, default is `['PNG', 'JPEG']`

* `min_size` _[tuple(int,int)]_ - _[optional]_ -  Min target image size (if the image is less than it then it's ignored and not copied), default is `(32,32)`

* `max_size` _[tuple(int,int)]_ - _[optional]_ - Max target image size (if the image is larger than it then it's ignored and not copied), default is `(16384,16384)`

* `base36` _[int]_ - _[optional]_ - Number of 1st N chars of base36 of the base64url of the blake2b of the image, if is set to `None` then nothing is applied, Please be careful when using this as it may result in duplication, so choose a large value to avoid collision, (choose values larger than 25)

* `write_status_files` _[bool]_ - _[optional]_ - if `True` the tool writes the status of the processed images in two files `failed-images.json` and `images-info.json` in the same directory, default is `False`.

* `num_processes` _[int]_ - _[optional]_ - number of process/cores to use, default value is the number of available cores in the processor. 
* `num_threads` _[int]_ - _[optional]_ - number of workers (threads) to be used in each process, default value is `4`. 

# Example Usage

## Clean Directory of Images. 

```sh
python src/to/dir/ImageDatasetCleaner.py --source_directory = './my-dataset' --output_directory='./cleaned-dataset' --write_status_files
```

> Note that if the `output directory` is not created the tool automatically creates it for you. 

The tool will immediately starts working, and output the status of each image it process into the std output. 

Example Output 
```
image 219 out of 330 was valid, original file: P070.png  new file: NjIxNGY0NmJkOGE5Y2U3MDE4YmYxZGE2OTcwOTM3OWIyIwTljMTJiYzY2NTMxZg==
image 220 out of 330 was valid, original file: P071.png  new file: ZmFhMGEyY2VhNzUyYjQ1NTc2NmFiMDlmMDBlYWY1ZTU2MTdkZmRkM2NlZmJhZjA5OQ==
image 221 out of 330 was valid, original file: P072.png  new file: YmM1ZWY5OTZiZDQyMjI4NDMxMWY2MjBkYWRkNjJiOTEODZkNTA3ZGJiNjFjM2E0NQ==
image 222 out of 330 was NOT valid because of those errors: ["Image format is not PNG nor JPEG it's WEBP"] , original file: T001.webp
```

In the `output directory` there will be two `json` files written in there the first one stores info about all the processed images and the status of each of them called `images-info.json` and the other contains info about the failed images (wasn't copied) and that file is called `failed-images.json`

Example of `images-info.json`
```json
{
    "some_image_name.png": {
        "format": "png",
        "original_file_name": "some_image_name.png",
        "file_size": 6042,
        "image_size": "(200,200)",
        "blake2b": "74cd6c26e76344efe017ec92aa7458f37e124e50bfe1df64c6ae3652bf278d91",
        "base64urlblake2b": "NzRjZDZjMjZlNzYzNDRlZmUwMTdlYzkyYWE3NDU4ZjM3ZTEyNGU1MGJmZTFkZjY0YzZhZTM2NTJiZjI3OGQ5MQ=="
    },
    "some_other_image_name.png": {
        "format": "png",
        "original_file_name": "some_other_image_name.png",
        "file_size": 5945,
        "image_size": "(200,200)",
        "blake2b": "74e04e7bd21bf0f756ed9fa55cd77ab5770ff50bd4838563c78232170b798c5a",
        "base64urlblake2b": "NzRlMDRlN2JkMjFiZjBmNzU2ZWQ5ZmE1NWNkNzdhYjU3NzBmZjUwYmQ0ODM4NTYzYzc4MjMyMTcwYjc5OGM1YQ=="
    },
}
```
Example of `failed-images.json`
```json
{
    "image_with_error.webp": {
        "original_file_name": "image_with_error.webp",
        "errors": [
            "Image format is not PNG nor JPEG it's WEBP"
        ]
    },
}
```

## Clean Directory of Compressed Files. 

```sh
python src/to/dir/ImageDatasetCleaner.py --source_directory = './my-compressed-files-dir' --compressed_files_dir --prefix_name="pixel_art"
```


After the above command the tool will start working, to process the compressed files, cleans them, then compress them back again into `ZIP` format, you can change the applied steps using the `CLI` options described above. 