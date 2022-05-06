# kcg-tiletool

Set of helping tools for cleaning image datasets and extracting patches from this set of images. 

# Table of Contents
There is currently 3 standalone tools in the project 
- [ImagePatchExtractor](#ImagePatchExtractor)
- [ImageDatasetCleaner](#ImageDatasetCleaner)
- [ImageDatasetPreview](#ImageDatasetPreview)
- [IntegerEncoder](#IntegerEncoder)

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


# IntegerEncoder
A standalone tool for encoding integers into other chosen codes. 

The tool takes in a single integer value and encodes it into a different form from the available implemented encodings methods. 

Supported methods are: 
- Binary Encodings. 
- Grey code Encodings. 


For more info about the tool and usage instructions check this [link](int-encoder)
