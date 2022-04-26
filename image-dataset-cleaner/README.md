# ImageDatasetCleaner
> A standalone tool for cleaning and validating test set images and copying the images passing certain conditions. 

## Tool Description

Given a `source directory` containing images, it applies some conditions and copies the valid images into the `output directory` and two yml files of the status of processed images saved in the same output directory with names `failed-images.yml` and `images-info.yml`

- Make sure if the image file is not corrupted
- Checks if the image format is within the given allowed image formats (codecs) provided as an option to the cli defualts are `JPEG` and `PNG` only 
- Check if the image size is withing the range of `min size` and `max size` provided by the user as an option defualts are `(32,32)` for `min size` and `(16384,16384)` for `max size`

## Installation
All that's needed to start using ImageDatasetCleaner is to install the dependencies using the command
```
pip install -r src/to/dir/requirements.txt
```

## CLI Parameters

* `source_directory` _[string]_ - _[required]_ - The source directory of the dataset containing the required images to be cleaned. 
* `output_directory` _[string]_ - _[required]_ - The output directory to write the copies of the valid images and the `yml` files.

* `allowed_formats` _[list[str]]_ - _[optional]_ A list of strings of the allowed formats (codecs) to be marked as valid for the output dataset, default is `['PNG', 'JPEG']`

* `min_size` _[tuple(int,int)]_ - _[optional]_ -  Min target image size (if the image is less than it then it's ignored and not copied), default is `(32,32)`

* `max_size` _[tuple(int,int)]_ - _[optional]_ - Max target image size (if the image is larger than it then it's ignored and not copied), default is `(16384,16384)`

`"sandstone"`.

## Example Usage

```
python src/to/dir/ImageDatasetCleaner.py source_directory = './my-dataset' output_directory='./cleaned-dataset'
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

In the `output directory` there will be two `yml` files written in there the first one stores info about all the processd images and the status of each of them called `images-info.yml` and the other contains info about the failed images (wasn't copied) and that file is called `failed-images.yml`

Example of `images-info.yml`
```yaml
some_image_name.png:
  base64sha256: NzRjZDZjMjZlNzYzNDRlZmUwMTdlYzkyYWE3NDU4ZjM3ZTEyNGU1MGJmZTFkZjY0YzZhZTM2NTJiZjI3OGQ5MQ==
  file_size: 6042
  format: png
  image_size: (200,200)
  original_file_name: some_image_name.png
  sha256: 74cd6c26e76344efe017ec92aa7458f37e124e50bfe1df64c6ae3652bf278d91
some_other_image_name.jpeg:
  base64sha256: NzRlMDRlN2JkMjFiZjBmNzU2ZWQ5ZmE1NWNkNzdhYjU3NzBmZjUwYmQ0ODM4NTYzYzc4MjMyMTcwYjc5OGM1YQ==
  file_size: 5945
  format: jpeg
  image_size: (200,200)
  original_file_name: some_other_image_name.jpeg
  sha256: 74e04e7bd21bf0f756ed9fa55cd77ab5770ff50bd4838563c78232170b798c5a
```
Example of `failed-images.yml`
```yaml
image_with_error.webp:
  errors:
  - Image format is not PNG nor JPEG it's WEBP
  original_file_name: image_with_error.webp
```