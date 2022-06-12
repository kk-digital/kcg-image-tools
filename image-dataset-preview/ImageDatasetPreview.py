import hashlib
import os
from random import shuffle
import random
import string
import time 
from PIL import Image 
import fire 
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from Base36lib import Base36

class ImageDatasetPreview: 
    def __init__(self): 
        self.written_files = {} 
        return 

    def __image_to_blake2b(self, image: Image.Image) -> str: 
        """Method to compute the blake2b of an image given the image as PIL.Image instance. 
        :param image: The directory to get the it's files paths
        :type image: str
        :returns: blake2b of the image
        :rtype: str
        """
        return hashlib.blake2b(image.tobytes()).hexdigest()

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
    
    def __write_images_to_grid(self, output_directory: str, images: list[str], PIL_color_mode: str,
                               image_size: tuple[int, int] = (64 , 64),matrix_size: tuple[int, int] = (32 , 32), base36: int = None) -> None: 
        """ Given a list of images paths, the method scale them down and concatenates them into large image 
            matrix with a given size and writes the matrix/grid image into `output_directory` as `.png`. 
                        
        :param output_directory: The directory to store the preview images inside it. 
        :type output_directory: str
        :param images: The images list to be concatenated and written into grid image. 
        :type images: list[str]
        :param PIL_color_mode: the color mode of images whatever they are to be read in RGB or grayscale. 
        :type PIL_color_mode: str
        :param image_size: The size to scale down the images to before being added to the preview matrix image. 
        :type image_size: tuple[int,int]
        :param matrix_size: The size of the preview matrix image (number of images to be included as width and height of the matrix)
        :type matrix_size: tuple[int,int]
        :param base36: Number of 1st N chars of base36 of the base64url of the blake2b of the image, if is set to `None` then nothing is applied.
        :type base36: int
        :returns: None
        :rtype: None
        """
        
        #make a new blank matrix image to be used for adding the small patches. 
        matrix_img = Image.new(PIL_color_mode , (matrix_size[0] * image_size[0] , matrix_size[1] * image_size[1]))
        count = 0 
        for image in images: 
            #open the image and convert it to the selected color mode. 
            try: 
                img = Image.open(image).convert(PIL_color_mode)
            except Exception: 
                continue
            img = img.resize(image_size)
            #paste the resized image in the large matrix image with offset based on the number of the current image. 
            matrix_img.paste(img , box = ((count % matrix_size[0]) * image_size[0] , (count // matrix_size[1]) * image_size[1]) )
            count += 1 
        
        file_name = self.__image_to_blake2b(matrix_img)
        
        #convert to Base36 if the flag is provided by the user.
        if base36 is not None: 
            file_name = Base36.encode(file_name)[:min(len(file_name), base36)]
        
        #make sure the file was not written before. 
        if file_name not in self.written_files: 
            #save the image file in the output directory. 
            matrix_img.save(os.path.join(output_directory, file_name) + '.png')

        
    def preview_image_dataset(self, source_directory: str, output_directory: str,  image_size: tuple[int, int] = (64 , 64), 
                                matrix_size: tuple[int, int] = (32 , 32), color_mode: str = 'rgb' , images_order_mode: str = 'sorted', base36: int = None,  num_workers: int = 8) -> None: 
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
        :param base36: Number of 1st N chars of base36 of the base64url of the blake2b of the image, if is set to `None` then nothing is applied.
        :type base36: int
        :param num_workers: Number of threads to be used in executing the process, default is `8` 
        :type num_workers: int
        :returns: None
        :rtype: None
        """
        #create the output folder if not exists
        os.makedirs(output_directory , exist_ok = True)
        #gets the list of files in the folder 
        images = self.__get_files_list(source_directory)
        #get the PIL color mode to convert all images to it when read. 
        PIL_color_mode = self.__get_PIL_color_conversion_mode(color_mode)
        
        #fetch all files previously existed in the output_directory
        self.written_files = {os.path.splitext(os.path.basename(path))[0]: True for path in self.__get_files_list(output_directory)}
        
        batch_size = matrix_size[0] * matrix_size[1]
        #iterate through all the images list to open the files and start working on them
        
        #Shuffle or sort the images list to be previewed based on the chosen mode.
        if images_order_mode == 'sorted': 
            images.sort()
        else: 
            shuffle(images)
        
        #Defining the thread pool with max number of workers given. 
        thread_pool = ThreadPoolExecutor(max_workers = num_workers)
        futures = [] 
        
        #take images as batches and the batch size is the number of images in one `preview matrix image`
        for batch in range(0 , ((len(images) + batch_size - 1) // batch_size)): 
            #take the batch of images files.
            imgs = images[batch * batch_size: min((batch + 1) * batch_size , len(images))]
            
            task = thread_pool.submit(self.__write_images_to_grid, output_directory, imgs, PIL_color_mode, image_size, matrix_size, base36, )
            
            futures.append(task)
        
        #wait for all tasks to be executed. 
        completed_batches = 0
        for future in as_completed(futures): 
            completed_batches += 1 
            print("finished batch {} out of {} batches".format(completed_batches, ((len(images) + batch_size - 1) // batch_size)))
            
        return 
    
    
def image_dataset_preview_cli(source_directory: str, output_directory: str,  image_size: tuple = (64 , 64), 
                                        matrix_size: tuple = (32 , 32), color_mode: str = 'rgb' , images_order_mode: str = 'sorted', base36: int = None,  num_workers: int = 8) -> None: 
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
        :param base36: Number of 1st N chars of base36 of the base64url of the blake2b of the image, if is set to `None` then nothing is applied.
        :type base36: int
        :param num_workers: Number of threads to be used in executing the process, default is `8` 
        :type num_workers: int
        :returns: None
        :rtype: None
    """
    
    start = time.time() 
    preview_dataset = ImageDatasetPreview()
    
    preview_dataset.preview_image_dataset(source_directory , output_directory, image_size, matrix_size, color_mode, images_order_mode, base36, num_workers)

    print("Process took {} seconds to execute".format(time.time() - start))
if __name__ == "__main__":     
    warnings.filterwarnings("ignore")

    fire.Fire(image_dataset_preview_cli)