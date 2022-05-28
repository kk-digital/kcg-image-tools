from PIL import Image
import fire
import numpy as np


class TileLerp: 
    def __init__(self) -> None:
        pass
    
    def __read_image(self, image_path: str) -> Image.Image:
        """Reads an image given its path and returns an instance of PIL image.  
        :param image_path: The path to the image to be read
        :type image_path: str
        :returns: PIL Image
        :rtype: PIL.Image.Image
        """
        return Image.open(image_path)
        
    def __read_and_validate_image_pair(self, first_image_path: str, second_image_path: str) -> tuple[np.ndarray, np.ndarray]:
        """Given two image paths makes sure they are not corrupted and validate the both images that they both have
                        4 channels (RGBA) and both images of same size
        :param first_image_path: The path for the first image
        :type first_image_path: str
        :param second_image_path: The path for the second image
        :type second_image_path: str
        :returns: a tuple of the two images as numpy array, and raises error if any of the validations was not satisfied.  
        :rtype: tuple[NDArray, NDArray]
        """

        #reads the images and make sure they are not corrupted. 
        try: 
            first_image = self.__read_image(first_image_path)
            second_image = self.__read_image(second_image_path)
        except Exception: 
            raise Exception('One or both images are corrupted')
        
        #Check the both size of images are identical. 
        if first_image.size != second_image.size:
            raise Exception("Images are of different size first image is of size {}, but second is {}"
                            .format(first_image.size, second_image.size))
        
        
        #checks that both images are in RGBA format. 
        if first_image.mode != second_image.mode and first_image.mode != 'RGBA': 
            raise Exception("Images must have 4 channels `RGBA`, but first image is of {} mode and second is {}"
                                    .format(first_image.mode, second_image.mode))
        
        return (np.array(first_image), np.array(second_image))
    
    
    def __linear_interpolation(self, first_image: np.ndarray, second_image: np.ndarray, lerp: float) -> np.ndarray:
        """makes linear interpolation between to images as numpy arrays, given the lerp factor. 
        :param first_image: The numpy array of the first image
        :type first_image: NDArray
        :param second_image: The numpy array of the second image
        :type second_image: NDArray
        :param lerp: The interpolation factor
        :type lerp: float
        :returns:  The interpolated result of the two images. 
        :rtype: NDArray
        """
        return (first_image + lerp * second_image).astype(np.uint8)
        
    
    def __save_image(self, image: np.ndarray, save_path: str) -> None: 
        """Given a numpy array of, the method saves it in the given. 
        :param image: The numpy array of the image
        :type image: NDArray
        :param save_path: The path to save the image at. 
        :type save_path: str
        :returns: 
        :rtype: None
        """
        Image.fromarray(image.astype(np.uint8)).save(save_path)
        
        return 
    
    def __preview_interpolation_grid(self, first_image_path: str, second_image_path: str, grid_size: tuple = (16, 16)) -> None: 
        """Makes a grid to preview interpolated result of two images with different lerp values ranging from 0 to 1.0
        :param first_image_path: The path of the first image
        :type first_image_path: str
        :param second_image_path: The path of the second image
        :type second_image_path: str
        :param grid_size: The grid size of the image preview, default is (16,16)
        :type grid_size: tuple(int,int)
        :returns: 
        :rtype: None
        """

        #load and validate the images
        first_image, second_image = self.__read_and_validate_image_pair(first_image_path, second_image_path)
        #define the grid  
        grid_img = Image.new('RGBA' , (grid_size[0] * first_image.shape[0] , grid_size[1] * first_image.shape[1]))
        #We will apply interpolation for all lerp values from (0 to number_of_examples)/number_of_examples as the grid is 16x16
        number_of_examples = grid_size[0] * grid_size[1]
        
        for step in range(number_of_examples):
            lerp = step / number_of_examples
            example_image = self.__linear_interpolation(first_image, second_image, lerp)

            grid_img.paste(Image.fromarray(example_image), box = ((step % grid_size[0]) * first_image.shape[0], (step // grid_size[1]) * first_image.shape[1]))
        
        grid_img.show('Interpolation results with lerp ranges from 0 to 1.0')
        return
    
    def tile_lerp(self, first_image_path: str, second_image_path: str, lerp: float = 0.5, 
                        output_img_path: str = './interpolated-img.png', preview_grid_size: tuple = (16 , 16),  preview: bool = False) -> None: 
        """Tool to interpolate two images given their paths and the `lerp` factor and an option to preview the interpolation result 
            for different values of `lerp`. 
        :param first_image_path: The path of the first image
        :type first_image_path: str
        :param second_image_path: The path of the second image
        :type second_image_path: str
        :param lerp: The interpolation factor, default is 0.5
        :type lerp: float
        :param output_img_path: The path to save the image at, default is './interpolated-img.png'
        :type output_img_path: str
        :param preview_grid_size: The grid size of the image preview, default is (16,16)
        :type preview_grid_size: tuple(int,int)
        :param preview: Option to output a preview of the interpolated result for different values of lerp, default is `False`
        :type preview: bool
        :returns: 
        :rtype: None
        """

        #Read and validate the images that they have 4 channels and they are of the same size. 
        first_image, second_image = self.__read_and_validate_image_pair(first_image_path, second_image_path)
        #get linear interpolation 
        interpolated_img = self.__linear_interpolation(first_image, second_image, lerp)
        #save the image in the provided path. 
        self.__save_image(interpolated_img, output_img_path)
        
        #If the user selected the preview option then apply preview as well. 
        if preview is True: 
            self.__preview_interpolation_grid(first_image_path, second_image_path, preview_grid_size)
            return 
        

def tile_lerp_cli_tool(first_image_path: str, second_image_path: str, lerp: float = 0.5, 
                        output_img_path: str = './interpolated-img.png', preview_grid_size: tuple = (16 , 16),  preview: bool = False) -> None: 
    
    """Tool to interpolate two images given their paths and the `lerp` factor and an option to preview the interpolation result 
            for different values of `lerp`. 
    :param first_image_path: The path of the first image
    :type first_image_path: str
    :param second_image_path: The path of the second image
    :type second_image_path: str
    :param lerp: The interpolation factor, default is 0.5
    :type lerp: float
    :param output_img_path: The path to save the image at, default is './interpolated-img.png'
    :type output_img_path: str
    :param preview_grid_size: The grid size of the image preview, default is (16,16)
    :type preview_grid_size: tuple(int,int)
    :param preview: Option to output a preview of the interpolated result for different values of lerp, default is `False`
    :type preview: bool
    :returns: 
    :rtype: None
    """
    tile_lerp = TileLerp() 
    tile_lerp.tile_lerp(first_image_path, second_image_path, lerp, output_img_path, preview_grid_size, preview)
    return 
    
if __name__ == "__main__": 
    
    fire.Fire(tile_lerp_cli_tool)