# ImageUniqueColors
> A standalone tool calculating the unique colors in images. 

## Tool Description

Given a source directory the tool go through all the images inside the directory and counts the number of unique colors of each image and then prints a single line for each image contains the computed number of unique pixels and the image path separated by a `separator` and the number of unique pixels is fixed in output length. 

The tool counts unique pixels in images of any type, so it works with RGB, RGBA, gray scale images or whatever.

## Installation
All what is needed to start using ImageUniqueColors is to install the dependencies using the command
```
pip install -r src/to/dir/requirements.txt
```

## CLI Parameters

* `images_directory` _[string]_ - _[required]_ - the path for the image directory needed to processed by the tool. 
* `color_count_width` _[int]_ - _[optional]_ - the width of the color count output, for example if `color_count_width=6` then `15` is `000015` in output instead of just `15`, default is `6`

* `separator` _[string]_ - _[optional]_ separator that takes place between the number of unique colors and image path in the output, default is comma `,` 

* `num_workers` _[int]_ - _[optional]_ - number of processes to be used in parallel to process the given directory, defaults to the number of cpu cores available on the used pc. 

## Example Usage

```sh
python src/to/dir/ImageUniqueColors.py --images_directory='path/to/my-image-dataset'
```

Example Output 
```
000024,path/to/my-image-dataset/img1.png
000006,path/to/my-image-dataset/img2.png
000006,path/to/my-image-dataset/img3.png
000017,path/to/my-image-dataset/img4.png
```
