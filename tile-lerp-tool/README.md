# TileLerp Tool
> A standalone tool for generating linear interpolation of two images given their paths, and preview for different interpolation factor.


## Tool Description

Given paths of two images and an interpolation factor called `lerp`, the linear interpolation result of the both images is produced and written as `.png` image in the specified directory, and also an option to preview the result of interpolation between the both images for different `lerp` values ranges from `0` to `1` with a step depending on the specified `preview_grid_size`. 

## Installation
All that's needed to start using TileLerp is to install the dependencies using the command
```
pip install -r src/to/dir/requirements.txt
```

## CLI Parameters

* `first_image_path` _[string]_ - _[required]_ - The path of the first image. 
* `second_image_path` _[string]_ - _[required]_ - The path of the second image. 

* `lerp` _[float]_ - _[optional]_ The interpolation factor, default is `0.5`

* `output_img_path` _[str]_ - _[optional]_ The path to save the image at, default is `'./interpolated-img.png'`


* `preview_grid_size` _[tuple(int,int)]_ - _[optional]_ The grid size of the image preview, each tile in the grid is the interpolated result of the two images with different `lerp` ranging from `0` to `1` with a step depending on size of the grid,default is `(16,16)`

* `preview` _[bool]_ - _[optional]_ Option to output a preview of the interpolated result for different values of lerp, default is `False`

## Example Usage

### CLI Examples: 
To get the linear interpolation of two results with factor of 0.7
```sh 
python src/to/dir/tilelerp.py --first_image_path='./img1.png' --second_image_path='./img2.png' --lerp=0.7
```

Then the tool will produce the interpolated image and writes it on the same current directory with the name `interpolated-img.png`. 


To output the preview as well of interpolation results with different lerp values. 
```
python src/to/dir/tilelerp.py --first_image_path='./img1.png' --second_image_path='./img2.png' --lerp=0.7 --preview
```

Also you may call `--help` to see the options and their defaults in the cli. 

### Programmatic API
To use the tool as a Python method you can simply call it in your program in the following way. 
```python
from tilelerp import TileLerp

tilelerp = TileLerp()

tilelerp.tile_lerp('./img1.png', './img2.png', lerp = 0.7)
```