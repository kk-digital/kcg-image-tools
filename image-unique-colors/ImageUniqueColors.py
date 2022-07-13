from PIL import Image
import fire 
import os 
import multiprocessing
from pathos.multiprocessing import ProcessingPool
import numpy as np

class ImageUniqueColors:
    
    def __init__(self) -> None:
        pass
    
    def __get_files_list(self, images_directory: str, recursive: bool = True) -> list[str]: 
        """method to get a list of file paths inside a given directory.
        
        :param images_directory: The source directory to get the list of files inside it. 
        :type images_directory: str
        :param recursive: If it's set to `True` the function will return paths of all files in the given directory 
                and all its subdirectories and will return the files inside the directory only if `False`, defaults to `True`. 
        :type recursive: bool
        
        :returns: a list contains all file paths. 
        :rtype: list[str]

        """
        if recursive: 
            return [os.path.join(root , file) for root , dirs , files in os.walk(images_directory) for file in files]
        else: 
            return [os.path.join(images_directory, file) for file in os.listdir(images_directory)] 
    
    @staticmethod
    def __count_unique_colors(image: Image.Image) -> int: 
        """counts unique RGB colors within a given image. 
        
        :param image: image to compute the number of unique colors for. 
        :type image: PIL.Image.Image

        :returns: The number of unique colors in the given image. 
        :rtype: int
        """
        image_array = np.array(image)
        return np.unique(image_array.reshape(-1, image_array.shape[-1] if image_array.ndim > 2 else 1), axis=0, return_counts=True)[1].size
    
    @staticmethod
    def __process_image(image_path: str, color_count_width: int, separator: str) -> None: 
        """method to open image and counts the number of unique colors in it. 
        
        :param image_path: the path of the image to compute the number of unique colors for. 
        :type image_path: str
        
        :param color_count_width: the width of the color count output, for example if `color_count_width=6` then `15` is `000015`
            in output instead of just `15`, default is `6`
        :type color_count_width: int

        :param separator: separator that takes place between the number of unique colors and image path in the output. 
        :type separator: str

        :returns: prints in single line in std output `the number of unique colors, image path`
        :rtype: None
        """
        try: 
            image = Image.open(image_path)
            print("{}{}{}".format(str(ImageUniqueColors.__count_unique_colors(image)).zfill(color_count_width), separator, image_path))
        except Exception as ex: 
            pass 
        return 
    
    def run(self, images_directory: str, color_count_width: int = 6, separator: str = ',', num_workers: int = multiprocessing.cpu_count()) -> None: 
        """Given a source directory the tool go through all the images inside the directory and counts the number of unique colors 
            of each image and then prints a single line for each image contains the computed number of unique pixels and the image path separated by a `separator`. 
        
        :param images_directory: the path for the image directory needed to processed by the tool. 
        :type images_directory: str
        
        :param color_count_width: the width of the color count output, for example if `color_count_width=6` then `15` is `000015`
            in output instead of just `15`, default is `6`
        :type color_count_width: int

        :param separator: separator that takes place between the number of unique colors and image path in the output. 
        :type separator: str

        :param num_workers: number of processes to be used in parallel to process the given directory, defaults to the number of cpu 
            cores available on the used pc. 
        :type num_workers: int
        
        :returns: 
        :rtype: None
        """
        #gets all paths of files inside the given directory. 
        images_files_paths = self.__get_files_list(images_directory)
        no_of_files = len(images_files_paths)
        #define the thread pool to execute the process in parallel. 
        pool = ProcessingPool(nodes = num_workers)
        
        #process the whole images in a given directory. 
        pool.map(ImageUniqueColors.__process_image, images_files_paths,[color_count_width] * no_of_files, [separator] * no_of_files)
        
                
        return 

def image_unique_colors_cli(image_directory: str, color_count_width: int = 6, separator: str = ',', num_workers: int = multiprocessing.cpu_count()) -> None: 
    """Given a source directory the tool go through all the images inside the directory and counts the number of unique colors 
        of each image and then prints a single line for each image contains the computed number of unique pixels and the image path separated by a `separator`. 
    
    :param images_directory: the path for the image directory needed to processed by the tool. 
    :type images_directory: str

    :param color_count_width: the width of the color count output, for example if `color_count_width=6` then `15` is `000015`
        in output instead of just `15`, default is `6`
    :type color_count_width: int
    
    :param separator: separator that takes place between the number of unique colors and image path in the output, default is comma `,` 
    :type separator: str

    :param num_workers: number of processes to be used in parallel to process the given directory, defaults to the number of cpu 
        cores available on the used pc. 
    :type num_workers: int
    
    :returns: 
    :rtype: None
    """

    instance = ImageUniqueColors()
    
    instance.run(image_directory,color_count_width, separator, num_workers) 


if __name__ == "__main__": 
    
    fire.Fire(image_unique_colors_cli)