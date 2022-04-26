import numpy as np
import cv2
from PIL import Image
import random

class ImageManipulation: 
    
    def __init__(self): 
        return 
    # 1. I need a utility function that cuts up larger images into 32x32 pixel patches for training
    # - parameters should be specifiable from command line, with defaults listed with --help and in readme.md (Google fire)
    # - utility to output a .png, showing these "training patches" produced from a specific 
    #           image or directory of images (size n x m in tiles/patches specified) (Work on it)
        
    # - option to specify "border" of N pixels, where patches will not be taken if they are within border region (What?!)
    # - ability to process N random files from input directory and produce N example images with square MxM grid of "random patches" of specified size.
    # - specifciation of output directory (Okay)

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
        :returns: A list of view of the fliiped images after applying horizontal flipping. 
        :rtype: list[ndarray] 
        """
        return [self.__horizontal_flip(image) if random.randint(0 , 1) % 2 == 0 else image for image in images]
    
    def __add_gaussian_noise(self, images: list, tile_size: tuple , mean: float = 0 , sigma: float = 10 ** 0.5) -> list[np.ndarray]:
        """
        :param images: The list of images/tiles to add the noise on
        :type images: list[ndarray] 
        :param tile_size: The size of the images in the given list 
        :type tile_size: tuple
        :param mean: the mean of the nnormal gaussian distribution 
        :type mean: float
        :param sigma: the sigma of the nnormal gaussian distribution 
        :type sigma: float
        :returns: A list of view of the images after adding the noise to it. 
        :rtype: list[ndarray] 
        """
        noise = np.random.normal(mean , sigma , tile_size)
        #Add the gaussian noise to all the images/tiles within the list 
        noisy_images = [(image + noise) for image in images]
        #return the images after being clipped as it might have exceeded the limit because of the noise 
        return [np.clip(noisy_image , 0 , 255) for noisy_image in noisy_images]
        
    def __stride_split(image: np.ndarray, tile_size: tuple) -> np.ndarray:
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
            rand_x = random.randint(0 , image.shape[0]) - tile_size[0]
            rand_y = random.randint(0 , image.shape[1]) - tile_size[1] 
            tiles.append(image[rand_x: rand_x + tile_size[0], rand_y: rand_y + tile_size[1]])
            
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
    
    
    def __stride_split_batch(self, images: list, tile_size: tuple) -> list: 
        """Splits the given images into equal tiles of the given tile size

        :param image: The list of images matrix needed for splitting into tiles. 
        :type image: list[ndarray] 
        :param tile_size: the desired output for the patch/tile size 
        :type tile_size: tuple
        :returns: a list of the numpay arrays of tiles after splitting the given image
        :rtype: list 
        """
        return [self.__stride_split(image , tile_size) for image in images]
    
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
    
    
