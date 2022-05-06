import enum
import os
from random import shuffle
import random
import string 
from PIL import Image 
import numpy as np 
import fire 

class ImageDatasetPreview: 
    def __init__(self): 
        return 

    def __get_files_list(self, directory: str) -> list[str]: 
        """returns a list of file paths for a given directory
        :param directory: The directory to get the it's files paths
        :type directory: str
        :returns: list of files
        :rtype: list[str]
        """
        return [os.path.join(directory , image_file) for image_file in os.listdir(directory)]
        
    def __get_PIL_color_conversion_mode(self, color_mode: str) -> str: 
        """converts the string to the PIL image color mode. 
        :param color_mode: The string representing the color mode to be converted to PIL's color mode. 
        :type color_mode: str
        :returns: PIL's color mode. 
        :rtype: str
        """

        return 'L' if color_mode.lower() == 'grey' else 'RGB'
    
    def preview_image_dataset(self, source_directory: str, output_directory: str,  image_size: tuple[int, int] = (32 , 32), 
                                matrix_size: tuple[int, int] = (32 , 32), color_mode: str = 'rgb' , images_order_mode: str = 'sorted') -> None: 
        """ Given a source directory containing images,the tool reads this images scale them down and concatenates them into large image 
                matrix with a given size for preview.
                        
        :param source_directory: The source directory containing the images.
        :type source_directory: str
        :param output_directory: The directory to store the preview images inside it. 
        :type output_directory: str
        :param image_size: The size to scale down the images to before being added to the preview matrix image. 
        :type image_size: tuple[int,int]
        :param matrix_size: The size of the preview matrix image (number of images to be included as width and height of the matrix)
        :type matrix_size: tuple[int,int]
        :param color_mode: the color mode of images to be `grey` or `rgb`, default is `rgb` 
        :type color_mode: str
        :param images_order_mode: The order of images of preview to be random (shuffled) or sorted based on the image file name, options are `random` or `sorted` default is `sorted`
        :type images_order_mode: str
        :returns: None
        :rtype: None
        """
        #create the output folder if not exists
        os.makedirs(output_directory , exist_ok = True)
        #gets the list of files in the folder 
        images = self.__get_files_list(source_directory)
        #get the PIL color mode to convert all images to it when read. 
        PIL_color_mode = self.__get_PIL_color_conversion_mode(color_mode)
        
        batch_size = matrix_size[0] * matrix_size[1]
        #iterate through all the images list to open the files and start working on them
        
        #Shuffle or sort the images list to be previewed based on the chosen mode.
        if images_order_mode == 'sorted': 
            images.sort()
        else: 
            shuffle(images)
        
        #take images as batches and the batch size is the number of images in one `preview matrix image`
        for batch in range(0 , ((len(images) + batch_size - 1) // batch_size)): 
            #take the batch of images files.
            imgs = images[batch * batch_size: min((batch + 1) * batch_size , len(images))]
            #make a new blank matrix image to be used for adding the small patches. 
            matrix_img = Image.new(PIL_color_mode , (matrix_size[0] * image_size[0] , matrix_size[1] * image_size[1]))
            count = 0 
            for image in imgs: 
                #open the image and convert it to the selected color mode. 
                try: 
                    img = Image.open(image).convert(PIL_color_mode)
                except Exception: 
                    continue
                img = img.resize(image_size)
                #paste the resized image in the large matrix image with offset based on the number of the current image. 
                matrix_img.paste(img , box = ((count % matrix_size[0]) * image_size[0] , (count // matrix_size[1]) * image_size[1]) )
                count += 1 
            
            #save the image file in the output directory. 
            matrix_img.save(os.path.join(output_directory, ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))) + '.png')
            
        return 
    
    
def image_dataset_preview_cli(source_directory: str, output_directory: str,  image_size: tuple[int, int] = (32 , 32), 
                                matrix_size: tuple[int, int] = (32 , 32), color_mode: str = 'rgb' , images_order_mode: str = 'sorted') -> None: 
    """ Given a source directory containing images,the tool reads this images scale them down and concatenates them into large image 
            matrix with a given size for preview.
                    
    :param source_directory: The source directory containing the images.
    :type source_directory: str
    :param output_directory: The directory to store the preview images inside it. 
    :type output_directory: str
    :param image_size: The size to scale down the images to before being added to the preview matrix image. 
    :type image_size: tuple[int,int]
    :param matrix_size: The size of the preview matrix image (number of images to be included as width and height of the matrix)
    :type matrix_size: tuple[int,int]
    :param color_mode: the color mode of images to be `grey` or `rgb`, default is `rgb` 
    :type color_mode: str
    :param images_order_mode: The order of images of preview to be random (shuffled) or sorted based on the image file name, options are `random` or `sorted` default is `sorted`
    :type images_order_mode: str
    :returns: None
    :rtype: None
    """
    preview_dataset = ImageDatasetPreview()
    
    preview_dataset.preview_image_dataset(source_directory , output_directory, image_size, matrix_size, color_mode, images_order_mode)
    return 

if __name__ == "__main__":     
    fire.Fire(image_dataset_preview_cli)