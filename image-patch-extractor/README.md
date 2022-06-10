# ImagePatchExtractor
> A standalone tool for extracting patches from a set of images in a certain directory and output the output concatenation in `.png` format in another directory. 

## Tool Description

Given a `source directory` containing images, the tool checks and validates this set of images, then extract patches from those images `randomly` or `on grid` and may applies some kind of augmentation or noise addition but those are left as options to the user.  

## Installation
All that's needed to start using ImagePatchExtractor is to install the dependencies using the command
```
pip install -r src/to/dir/requirements.txt
```

## CLI Parameters


* `source_directory` _[string]_ - _[required]_ - The source directory of the dataset containing the images. 
* `output_directory` _[string]_ - _[required]_ - The output directory to write the extracted patches. 

* `min_image_size` _[tuple]_ - _[optional]_ - min size of image dimension to be considered as valid image, comparison is made with on each dimension. `i.e. (min_dim[0] >= image_dim[0] and min_dim[1] >= image_dim[1])`.

* `allowed_formats` _[list[str]]_ - _[optional]_ A list of strings of the allowed formats (codecs) to be marked as valid for the output dataset any format is allowed when the list is left empty, default is `[]`

* `tile_size` _[tuple(int,int)]_ - _[optional]_ The desired patch size, default is `(32,32)`


* `split_patches_type` _[str]_ - _[optional]_ Type of patch extraction applied to the set of images, available options are `random` or `grid`, `random` is taking the patches at random locations of the image while `grid` extracting patches with offset of the `tile_size`, default is `random`. 

* `output_png_size` _[tuple(int,int)]_ - _[optional]_ The output size of the `PNG` image of concatenated patches, note it should be divisible by `tile_size`, default is `(512,512)`

* `noise` _[bool]_ - _[optional]_ When `True` it adds `Gaussian` noise to the output patches
* `flip_patches` _[bool]_ - _[optional]_  When `True` it flips the patches horizontally with probability of 50%patches, note it should be divisible by `tile_size`.

* `number_of_tiles` _[int]_ - _[optional]_ Number of tiles to be extracted if the `split_patches_type` param was set to `random`,
                if it was not set then the tool will set it to the number of grid splits in the image with size of `tile_size`
* `batch_size` _[int]_ - _[optional]_ Number of images to process at a time.

* `num_workers` _[int]_ - _[optional]_ Number of workers (Threads) to be used for executing the process, default is `8`

* `write_single_patches` _[bool]_ - _[optional]_ If True it write each patch as a single `.png` file otherwise it concatenates them as grid of size `output_png_size`, default is `True`.

## Example Usage

```
python src/to/dir/ImagePatchExtractor.py --source_directory = './my-dataset' --output_directory='./extracted-random-patches'
```

> Note that if the `output directory` is not created the tool automatically creates it for you. 

The tool will immediately starts working, and output the status of each processed batch in the standard output. 

Example Output 
```
Finished 14 batches out of 40 total batches.
Finished 15 batches out of 40 total batches.
Finished 16 batches out of 40 total batches.
Finished 17 batches out of 40 total batches.
Finished 18 batches out of 40 total batches.
Finished 19 batches out of 40 total batches.
```

or maybe you can change the split type option to `grid` 
```
python src/to/dir/ImagePatchExtractor.py source_directory = './my-dataset' output_directory='./extracted-grid-patches' --split_patches_type='grid'
```

Also you may call `--help` to see the options and their defaults in the cli. 

