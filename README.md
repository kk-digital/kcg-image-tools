# kcg-tiletool

Set of helping tools for cleaning image datasets and extracting patches from this set of images. 

# Table of Contents
There is currently 9 standalone tools in the project 
- [GIFDatasetTools](#GIFDatasetTools)
- [ImagePatchExtractor](#ImagePatchExtractor)
- [ImageDatasetCleaner](#ImageDatasetCleaner)
- [ImageDatasetPreview](#ImageDatasetPreview)
- [ImageDatasetInfo](#ImageDatasetInfo)
- [ImageUniqueColors](#ImageUniqueColors)
- [ImageTaggingTool](#ImageTaggingTool)
- [IntegerEncoder](#IntegerEncoder)
- [TileLerp](#tilelerp)

# GIFDatasetTools

Given a source directory containing GIF images, the tool go through all the images inside the directory and computes each image metadata saves the result into a `JSON` file with name `images_metadata.json`, and an option to extract the frames of each image and specifying a max number of frames to extract for each image. 

For more info about the tool and usage instructions check this [link](gif-dataset-tool)

# ImagePatchExtractor
A standalone tool for extracting patches from a set of images in a certain directory and output the output concatenation in `.png` format in another directory.

Given a `source directory` containing images, the tool checks and validates this set of images, then extract patches from those images `randomly` or `on grid` and may applies some kind of augmentation or noise addition but those are left as options to the user.  

For more info about the tool and usage instructions check this [link](image-patch-extractor)

# ImageDatasetCleaner
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

For more info about the tool and usage instructions check this [link](image-dataset-cleaner)

# ImageDatasetPreview
A standalone tool for image dataset preview. 

Given a `source directory` containing images, the tool reads all the images in this directory scale them down to a size provided from the user and then concatenates those scaled images into a matrix shaped image with those small images as elements, and those matrix images are saved in PNG formats in the `output_directory` provided by the user. 

For more info about the tool and usage instructions check this [link](image-dataset-preview)

# ImageUniqueColors
A standalone tool calculating the unique colors in images. 

Given a source directory the tool go through all the images inside the directory and counts the number of unique colors of each image and then prints a single line for each image contains the computed number of unique pixels and the image path separated by a `separator` and the number of unique pixels is fixed in output length. 

The tool counts unique pixels in images of any type, so it works with `RGB`, `RGBA`, `gray scale` images or whatever.

For more info about the tool and usage instructions check this [link](image-unique-colors)

# ImageDatasetInfo
A standalone tool for obtaining the metadata of a given directory of images. 

given a directory containing images, process all those images and write a file with the metadata (in current working directory)
of those processed images, which are `image_path` , `image_name`, `image_blake2b_hash`, `image_size_bytes` , `image_dims_tuple`, `image_dims_string` and `unique_colors`. 

For more info about the tool and usage instructions check this [link](image-dataset-info)


# ImageTaggingTool
A standalone tool for tagging image datasets.  

given an image dataset directory and the tag tasks you need to apply for this dataset, the tool runs web UI can be accessed at  http://127.0.0.1:5000 with a grid of images taken from the image directory you have passed to be used for tagging depending on the task you choose, the tagged images metadata can be found in `data_output_directory` in `json` format.

For more info about the tool and usage instructions check this [link](image-tagging-tool)


# IntegerEncoder
A standalone tool for encoding integers into other chosen codes. 

The tool takes in a single integer value and encodes it into a different form from the available implemented encodings methods. 

Supported methods are: 
- Binary Encodings. 
- Grey code Encodings. 


For more info about the tool and usage instructions check this [link](int-encoder)


# TileLerp
A standalone tool for generating linear interpolation of two images given their paths, and preview for different interpolation factor.

Given paths of two images and an interpolation factor called `lerp`, the linear interpolation result of the both images is produced and written as `.png` image in the specified directory, and also an option to preview the result of interpolation between the both images for different `lerp` values ranges from `0` to `1` with a step depending on the specified `preview_grid_size`. 

For more info about the tool and usage instructions check this [link](tile-lerp-tool)

# Background Remover

This script processes ZIP files, extracting images, removing their backgrounds, and storing the original and background removed images in separate ZIP files.

### Usage

To run this script, you need to provide the following arguments:

**dataset_path**: This is the input path to your dataset. It could be a directory containing multiple zip files or a single zip file.
**output_path**: This is the path where the output will be stored.
**size_filter**: **Default is '512x512'** This is the size of the images you want to process. Images that don't match this size will be skipped. The size should be provided as 'WIDTHxHEIGHT'. 

    python background_remover.py --dataset_path ./input_zip_files --output_path ./output --size_filter '512x512'


# Image Processing Script

This Python script processes background removed images in zip files, specifically extracting relevant details from JSON files, calculating bounding box information for images, and then outputting the processed data as JSON files.

## Description

The script performs the following steps:

1.The input path provided by the user is checked. If it's a directory, all zip files within that directory are processed. If it's a single zip file, only that file is processed.

2.Each zip file is opened and loaded into RAM.

3.JSON files within the zip files are parsed and filtered based on certain conditions.

4.Images are processed to determine the center of the object within the image and calculate its bounding box details.

5.All processed details are combined and stored in a JSON file in the output directory specified by the user.

### step 1

Remove background for the images

    python background_remover.py --dataset_path ./input_zip_files --output_path ./output --size_filter '512x512'

### step 2

Compute Features Of Zip Dataset (from kcg-ml)

    python ./scripts/image_dataset_storage_format/process_dataset.py compute-features-of-zip --image-dataset-path "input_path" --clip-model="ViT-L/14"


### Usage

You can execute this script using the following command:


    python zip_json_processor.py --input_path <path_to_zip_files> --output_path <output_directory>

