# kcg-tiletool

Set of helping tools for cleaning image datasets and extracting patches from this set of images. 

# Table of Contents
There is currently 6 standalone tools in the project 
- [ImagePatchExtractor](#ImagePatchExtractor)
- [ImageDatasetCleaner](#ImageDatasetCleaner)
- [ImageDatasetPreview](#ImageDatasetPreview)
- [ImageDatasetInfo](#ImageDatasetInfo)
- [IntegerEncoder](#IntegerEncoder)
- [TileLerp](#tilelerp)

# ImagePatchExtractor
A standalone tool for extracting patches from a set of images in a certain directory and output the output concatenation in `.png` format in another directory.

Given a `source directory` containing images, the tool checks and validates this set of images, then extract patches from those images `randomly` or `on grid` and may applies some kind of augmentation or noise addition but those are left as options to the user.  

For more info about the tool and usage instructions check this [link](image-patch-extractor)

# ImageDatasetCleaner
A standalone tool for cleaning and validating test set images and copying the images passing certain conditions. 

Given a `source directory` containing images, it applies some conditions and copies the valid images into the `output directory` and two json files of the status of processed images saved in the same output directory with names `failed-images.json` and `images-info.json`

- Make sure if the image file is not corrupted
- Checks if the image format is within the given allowed image formats.
- Check if the image size is withing the range of `min size` and `max size`.

For more info about the tool and usage instructions check this [link](image-dataset-cleaner)

# ImageDatasetPreview
A standalone tool for image dataset preview. 

Given a `source directory` containing images, the tool reads all the images in this directory scale them down to a size provided from the user and then concatenates those scaled images into a matrix shaped image with those small images as elements, and those matrix images are saved in PNG formats in the `output_directory` provided by the user. 

For more info about the tool and usage instructions check this [link](image-dataset-preview)

# ImageDatasetPreview
A standalone tool for obtaining the metadata of a given directory of images. 

given a directory containing images, process all those images and write a file with the metadata (in current working directory)
of those processed images, which are `image_path` , `image_name`, `image_blake2b_hash`, `image_size_bytes` , `image_dims_tuple`, `image_dims_string` and `unique_colors`. 

For more info about the tool and usage instructions check this [link](image-dataset-info)


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
