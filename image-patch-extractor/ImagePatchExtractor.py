import math
import time
import numpy as np
import cv2
from PIL import Image
import random
import os
import string
from ImageValidator import ImageValidator
import fire 
from concurrent.futures import ThreadPoolExecutor, as_completed

class ImagePatchExtractor: 
    
    def __init__(self): 
        return 

    def __horizontal_flip(self, image: np.ndarray) -> np.ndarray: 
        """applies horizontal flip to the image and returns a view of the flipped version

        :param image: The image matrix needed for for flipping
        :type image: ndarray 
        :returns: A view of image after apping horizontal flipping
        :rtype: ndarray 
        """
        return np.fliplr(image)
    
    def __horizontal_flip_batch(self, images: list) -> list[np.ndarray]: 
        """applies horizontal flip to the list of images with probability of 0.5 and returns a list of ndarray view of the flipped versions

        :param images: The list of image matrices needed for for flipping
        :type images: list[ndarray] 
        :returns: A list of view of the flipped images after applying horizontal flipping. 
        :rtype: list[ndarray] 
        """
        return [self.__horizontal_flip(image) if random.randint(0 , 1) % 2 == 0 else image for image in images]
    
    def __add_gaussian_noise(self, images: list, tile_size: tuple , mean: float = 0 , sigma: float = 10 ** 0.5) -> list[np.ndarray]:
        """
        :param images: The list of images/tiles to add the noise on
        :type images: list[ndarray] 
        :param tile_size: The size of the images in the given list 
        :type tile_size: tuple
        :param mean: the mean of the normal gaussian distribution 
        :type mean: float
        :param sigma: the sigma of the normal gaussian distribution 
        :type sigma: float
        :returns: A list of view of the images after adding the noise to it. 
        :rtype: list[ndarray] 
        """
        noise = np.random.normal(mean , sigma , (tile_size[0] , tile_size[1], 3))
        #Add the gaussian noise to all the images/tiles within the list 
        noisy_images = [(image + noise) for image in images]
        #return the images after being clipped as it might have exceeded the limit because of the noise 
        return [np.clip(noisy_image , 0 , 255) for noisy_image in noisy_images]
        
    def __stride_split(self, image: np.ndarray, tile_size: tuple) -> np.ndarray:
        """Splits the given image into equal tiles of the given tile size

        :param image: The image matrix needed for splitting into tiles. 
        :type image: ndarray 
        :param tile_size: the desired output for the patch/tile size 
        :type tile_size: tuple
        :returns: an array of the tiles after splitting the given image
        :rtype: ndarray 
        """
        img_height, img_width, channels = image.shape
        tile_height, tile_width = tile_size

        # bytelength of a single element
        bytelength = image.nbytes // image.size

        tiled_array = np.lib.stride_tricks.as_strided(
            image,
            shape=(img_height // tile_height,
                img_width // tile_width,
                tile_height,
                tile_width,
                channels),
            strides=(img_width*tile_height*bytelength*channels,
                    tile_width*bytelength*channels,
                    img_width*bytelength*channels,
                    bytelength*channels,
                    bytelength)
        )
        
        return tiled_array
    
    def __stride_split_batch(self, images: list, tile_size: tuple) -> list: 
        """Splits the given images into equal tiles of the given tile size

        :param image: The list of images matrix needed for splitting into tiles. 
        :type image: list[ndarray] 
        :param tile_size: the desired output for the patch/tile size 
        :type tile_size: tuple
        :returns: a list of the numpy arrays of tiles after splitting the given image
        :rtype: list 
        """
        return [self.__stride_split(image , tile_size) for image in images]

    def __random_split(self, image: np.ndarray, tile_size: tuple , number_of_tiles: int) -> list[np.ndarray]: 
        """Splits the given image into number of tiles with the given tile size with random locations.  

        :param image: The image matrix needed for splitting into tiles. 
        :type image: ndarray 
        :param tile_size: the desired output for the patch/tile size 
        :type tile_size: tuple
        :param number_of_tiles: the number of randomly extracted tiles needed to be extracted from the image
        :type number_of_tiles: int
        :returns: a list of the tiles after splitting the given image
        :rtype: list[ndarray] 
        """
        tiles = [] 
        for _ in range(number_of_tiles): 
            rand_x = random.randint(0 , image.shape[0] - tile_size[0]) 
            rand_y = random.randint(0 , image.shape[1] - tile_size[1] ) 
            tiles.append(image[rand_x: rand_x + tile_size[0], rand_y: rand_y + tile_size[1],:])
            
        return tiles
    
    def __random_split_batch(self, images: list[np.ndarray], tile_size: tuple, number_of_tiles: int) -> list[list[np.ndarray]]: 
        """Splits a batch of images into tiles with the given tile size with randomly generated offsets from the image

        :param images: The images matrices needed for splitting into tiles. 
        :type images: list[ndarray] 
        :param tile_size: the desired output for the patch/tile size 
        :type tile_size: tuple
        :param number_of_tiles: the number of randomly extracted tiles needed to be extracted from the image
        :type number_of_tiles: int
        :returns: a list of lists each of them containing the extracted tiles form the image. 
        :rtype: list[list[ndarray]] 
        """  
        return [self.__random_split(image, tile_size , number_of_tiles) for image in images] 
    
    def __concatenate_patches(self, patches: list[np.ndarray] , tile_size: tuple, output_size: tuple) -> np.ndarray: 
        """Concatenates a list of patches into an array of a given size note that `output_size` should be divisible by `tile_size`

        :param patches: The images matrices needed for splitting into tiles. 
        :type patches: list[ndarray] 
        :param tile_size: The size of each patch 
        :type tile_size: tuple
        :param output_size: The size of the output array after concatenating all the patches. 
        :type output_size: tuple
        :returns: a numpy array with `output_size` with the given patches concatenated inside it. 
        :rtype: list[list[ndarray]] 
        """  

        result = np.ndarray((output_size[0] , output_size[1] , 3))
        
        number_of_rows = output_size[0] // tile_size[0] 
        number_of_cols = output_size[1] // tile_size[1] 
        for row in range(number_of_rows): 
            result[(row * tile_size[0]):(row + 1) * tile_size[0],:] = np.hstack(patches[row * number_of_cols: (row + 1) * number_of_cols])
            
        return result

    def __write_array_to_png(self, image: np.ndarray , output_directory: str , file_name: str) -> None:
        """Writes the given numpy array into a `PNG` image and saves it into the specified directory. 

        :param image: The numpy array containing the values to be written into the `PNG` image
        :type image: ndarray
        :param output_directory: The directory to save the resultant image. 
        :type output_directory: str
        :param file_name: The file name of the save image. 
        :type file_name: str
        :returns: None
        :rtype: None
        """  
        Image.fromarray(image.astype(np.uint8)).save(os.path.join(output_directory , "{}.png".format(file_name))) 
        
        return  
        
    def __resize(self, image: np.ndarray , dsize: tuple = (32 , 32)) -> np.ndarray:
        """Resizes the given image to the size given as tuple 

        :param image: The image matrix needed for resizing. 
        :type image: ndarray 
        :param dsize: the desired output size for the image
        :type dsize: tuple
        :returns: The image matrix with the new size after being resized using cubic interpolation
        :rtype: ndarray
        """
        return np.array(cv2.resize(image , dsize , interpolation = cv2.INTER_CUBIC))
    
    def __resize_batch(self, images: list , dsize: tuple = (32 , 32)) -> list[np.ndarray]: 
        """Resizes the given batch of images to the size given as tuple 
        :param images: The list of image matrices needed for resizing. 
        :type images: list[ndarray] 
        :param dsize: the desired output size for the image
        :type dsize: tuple
        :returns: The image matrix with the new size after being resized using cubic interpolation
        :rtype: list[ndarray]
        """
        return [self.__resize(image , dsize) for image in images]
    
    
    #############TEMP Function for resizing ###################################### 
    
    def _resize_image_folder(self, source_directory: str, output_directory: str, resize_to: tuple):
        #Validate the image in the source directory and get the valid image paths list. 
        validator = ImageValidator()
        valid_images_list , _ = validator.validate(source_directory, False , [])
        
        os.makedirs(output_directory , exist_ok = True)
        corrupts = 0 
        for image_file in valid_images_list: 
            #open the image file and convert it into a numpy array. 
            try: 
                image = np.asarray(Image.open(image_file).convert('RGB'))
                image = self.__resize(image, resize_to)
                _ , file_name = os.path.split(os.path.splitext(image_file)[0])
                Image.fromarray(image.astype(np.uint8)).save(os.path.join(output_directory , "{}.png".format(file_name))) 
            except Exception: 
                corrupts += 1 
                print(corrupts)
                continue 

        return 
    ##############################################################################
    
    def _extract_patches_task(self, output_directory: str, image_files: list[str], split_patches_type: str = "random",  tile_size: tuple = (32 , 32), output_png_size: tuple = (512,512),
            noise: bool = False, flip_patches: bool = False, number_of_tiles: int = None, write_single_patches: bool = True): 
        """Method to apply patch extraction in for a batch of images, used to be executed as a task inside a thread. 
        """
        images = [] 
        patches = [] 

        for image_file in image_files: 

            image = np.asarray(Image.open(image_file).convert('RGB'))
            images.append(image)

        if split_patches_type == 'random':
            #If it was not set by the user then take the splits of grid size. 
            if number_of_tiles is None: 
                number_of_tiles = ((images[0].shape[0] * images[0].shape[1]) // (64 * 64)) * 6 
            
            patches = self.__random_split_batch(images , tile_size, number_of_tiles)
            patches = [patch for value in patches for patch in value]
            
        elif split_patches_type == 'grid': 
            
            all_patches = self.__stride_split_batch(images , tile_size)
            tmp = [] 
            for image in all_patches: 
                for x in range(image.shape[0]): 
                    for y in range(image.shape[1]): 
                        tmp.append(image[x,y,:,:,:])
            
            patches = tmp 

        #add noise if user set it to True 
        if noise: 
            patches = self.__add_gaussian_noise(patches , tile_size)
        #add horizontal flipping for data augmentation if the use set it to True 
        if flip_patches: 
            patches = self.__horizontal_flip_batch(patches)
        
        if write_single_patches:
            for patch in patches: 
                    self.__write_array_to_png(patch, output_directory , ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8)))
        else: 
            no_of_elements = (output_png_size[0] // tile_size[0]) * (output_png_size[1] // tile_size[1])
            
            for i in range(len(patches) // no_of_elements): 
                concatendated = self.__concatenate_patches(patches[i * no_of_elements: (i + 1) * no_of_elements] , tile_size , output_png_size)
                self.__write_array_to_png(concatendated , output_directory , ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8)))
            
            #remaining patches that didn't fit in the output_png size 
            if len(patches) % no_of_elements != 0: 
                offset = len(patches) // no_of_elements
                number_of_values = len(patches[offset * no_of_elements:])
                concatendated = self.__concatenate_patches(patches[offset * no_of_elements:] , tile_size , (tile_size[0] * number_of_values , tile_size[1]))
                self.__write_array_to_png(concatendated , output_directory , ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8)))

    def extract_patches(self, source_directory: str, output_directory: str, min_image_size: tuple = (64, 64), allowed_types: list = [], 
            split_patches_type: str = "random",  tile_size: tuple = (32 , 32), output_png_size: tuple = (512,512),
            noise: bool = False, flip_patches: bool = False, number_of_tiles: int = None, batch_size: int = 8, num_workers: int = 8,  write_single_patches: bool = True) -> None: 
        """Method to apply extracting patches given a set of options by the user.
        :param `source_directory`: The source directory containing the set of images to extract patches from them. 
        :type `source_directory`: str
        :param `output_directory`: The output directory to save the `PNG` images of concatenated patches. 
        :type `output_directory`: str
        :param `min_image_size`: min size of image dimension to be considered as valid image, comparison is made with on each dimension.  
        :type `min_image_size`: tuple
        :param `allowed_types`: a list of allowed images formats (Image codecs) to be considered within the dataset it accepts all 
                types when left as an empty list, default is `[]`
        :type `allowed_types`: list
        :param `split_patches_type`: Type of patch splitting, `random` or `grid` default is `random` 
        :type `split_patches_type`: str
        :param `tile_size`: The desired patch size, default is `(32,32)`
        :type `tile_size`: tuple(int , int)
        :param `output_png_size`: The output size of the `PNG` image of concatenated patches, note it should be divisible by `tile_size` default is `(512,512)`
        :type `output_png_size`: tuple(int , int)
        :param `noise`: When `True` it adds `Gaussian` noise to the output patches, default is `False` 
        :type `noise`: bool
        :param `flip_patches`: When `True` it flips the patches horizontally with probability of 50%, default is `False` 
        :type `flip_patches`: bool
        :param `number_of_tiles`: Number of tiles to be extracted if the `split_patches_type` param was set to `random`,
                    if it was not set then the tool will set it to the number of grid splits in the image with size of `tile_size`.  
        :type `number_of_tiles`: int
        :param `batch_size`: Number of images to process at a time, default is `8`
        :type `batch_size`: int
        :param `num_workers`: Number of workers (Threads) to be used for executing the process, default is `8`
        :type `num_workers`: int
        :param `write_single_patches`: If True it write each patch as a single .png file otherwise it concatenates them as `output_png_size`. 
        :type `write_single_patches`: bool
        :returns: None
        :rtype: None
        """

        #Validate the image in the source directory and get the valid image paths list. 
        validator = ImageValidator()
        valid_images_list , _ = validator.validate(source_directory, min_image_size ,  False , allowed_types)
        
        os.makedirs(output_directory , exist_ok = True)
        
        thread_pool = ThreadPoolExecutor(max_workers = num_workers)
        futures = [] 

        for i in range(0, len(valid_images_list) , batch_size): 
            
            future = thread_pool.submit(self._extract_patches_task , output_directory,  valid_images_list[i:i+batch_size], split_patches_type, tile_size,
                                                             output_png_size, noise, flip_patches,
                                                             number_of_tiles, write_single_patches,)
            
            futures.append(future)
                    
        
        #Make sure all threads were executed successfully. 
        cur_working_batch = 0 

        for _ in as_completed(futures):
            cur_working_batch  += 1
            print("Finished {} batches out of {} total batches.".format(cur_working_batch , len(valid_images_list) // batch_size))

        
        return 
    

def extract_patches_cli_tool(source_directory: str, output_directory: str, min_image_size: tuple = (64, 64), allowed_types: list = [], 
            split_patches_type: str = "random",  tile_size: tuple = (32 , 32), output_png_size: tuple = (512,512),
            noise: bool = False, flip_patches: bool = False, number_of_tiles: int = None, batch_size: int = 8, num_workers: int = 8,  write_single_patches: bool = True) -> None: 
    """Method to apply extracting patches given a set of options by the user.
    :param `source_directory`: The source directory containing the set of images to extract patches from them. 
    :type `source_directory`: str
    :param `output_directory`: The output directory to save the `PNG` images of concatenated patches. 
    :type `output_directory`: str
    :param `min_image_size`: min size of image dimension to be considered as valid image, comparison is made with on each dimension.  
    :type `min_image_size`: tuple
    :param `allowed_types`: a list of allowed images formats (Image codecs) to be considered within the dataset it accepts all 
            types when left as an empty list, default is `[]`
    :type `allowed_types`: list
    :param `split_patches_type`: Type of patch splitting, `random` or `grid` default is `random` 
    :type `split_patches_type`: str
    :param `tile_size`: The desired patch size, default is `(32,32)`
    :type `tile_size`: tuple(int , int)
    :param `output_png_size`: The output size of the `PNG` image of concatenated patches, note it should be divisible by `tile_size` default is `(512,512)`
    :type `output_png_size`: tuple(int , int)
    :param `noise`: When `True` it adds `Gaussian` noise to the output patches, default is `False` 
    :type `noise`: bool
    :param `flip_patches`: When `True` it flips the patches horizontally with probability of 50%, default is `False` 
    :type `flip_patches`: bool
    :param `number_of_tiles`: Number of tiles to be extracted if the `split_patches_type` param was set to `random`,
                if it was not set then the tool will set it to the number of grid splits in the image with size of `tile_size`.  
    :type `number_of_tiles`: int
    :param `batch_size`: Number of images to process at a time, default is `8`
    :type `batch_size`: int
    :param `num_workers`: Number of workers (Threads) to be used for executing the process, default is `8`
    :type `num_workers`: int
    :param `write_single_patches`: If True it write each patch as a single .png file otherwise it concatenates them as `output_png_size`. 
    :type `write_single_patches`: bool
    :returns: None
    :rtype: None
    """
    start_time = time.time() 
    patch_extractor = ImagePatchExtractor()
    patch_extractor.extract_patches(source_directory , output_directory , min_image_size,  allowed_types , split_patches_type, tile_size, output_png_size , noise , flip_patches, number_of_tiles, batch_size , num_workers, write_single_patches)
    
    print("Process took {:.2f} seconds to finish your task".format(time.time() - start_time))
if __name__ == "__main__": 

    fire.Fire(extract_patches_cli_tool)
    