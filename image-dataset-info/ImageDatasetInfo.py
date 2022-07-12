import time
import numpy as np 
from PIL import Image
import fire 
from concurrent.futures import ThreadPoolExecutor, as_completed
import os 
import hashlib
import csv
import json 

class ImageDatasetInfo:
    def __init__(self) -> None:
        pass 
    
    def __list_to_json(self, rows: list[dict] , file_name: str) -> None: 
        """takes list and writes it to a json file. 
        
        :param rows: list of records to write in json files as dicts.
        :type rows: list[dict]
        :param file_name: The written file name.
        :type file_name: str

        :returns: Writes a json file with the given data into the current working directory with name of `file_name`.
        :rtype: None 

        """

        with open(file_name, 'w') as json_file:
            json.dump(rows , json_file , indent=4)


    def __write_json(self, valid_images_metadata: list[dict], failed_images_metadata: list[dict]) -> None: 
        """takes `valid images` and `failed images` lists and writes them into json file in the current working directory. 
        
        :param valid_images_metadata: list of valid images metadata.
        :type valid_images_metadata: list[dict]
        :param failed_images_metadata: list of failed images metadata.
        :type failed_images_metadata: list[dict]
         
        :returns: Writes two json files, `valid-images-metadata.json` and `failed-images-metadata.json` in the current directory. 
        :rtype: None 

        """

        self.__list_to_json(valid_images_metadata, 'valid-images-metadata.json')
        self.__list_to_json(failed_images_metadata, 'failed-images-metadata.json')
        
        return 
    
    def __list_to_csv(self, keys: list, rows: list , file_name: str) -> None: 
        """takes list and writes it to a csv file. 
        
        :param keys: list of keys to use as csv file header. 
        :type keys: list[str]
        :param rows: list of records to write in csv files as dicts.
        :type rows: list[dict]
        :param file_name: The written file name.
        :type file_name: str

        :returns: Writes a csv file with the given data into the current working directory with name of `file_name`.
        :rtype: None 

        """
        with open(file_name , 'w') as csv_file: 
            writer = csv.DictWriter(csv_file, keys)
            writer.writeheader()
            writer.writerows(rows)

    def __write_csv(self, valid_images_metadata: list[dict], failed_images_metadata: list[dict]) -> None: 
        """takes `valid images` and `failed images` lists and writes them into csv file in the current working directory. 
        
        :param valid_images_metadata: list of valid images metadata.
        :type valid_images_metadata: list[dict]
        :param failed_images_metadata: list of failed images metadata.
        :type failed_images_metadata: list[dict]
         
        :returns: Writes two csv files, `valid-images-metadata.csv` and `failed-images-metadata.csv` in the current directory. 
        :rtype: None 

        """
        self.__list_to_csv(valid_images_metadata[0].keys() if len(valid_images_metadata) > 0 else [], valid_images_metadata, 'valid-images-metadata.csv')
        self.__list_to_csv(failed_images_metadata[0].keys() if len(failed_images_metadata) > 0 else [], failed_images_metadata, 'failed-images-metadata.csv')

        return 

    def __image_blake2b_hash(self, image: Image.Image) -> str:
        """method to compute the blake2b of given image.
        
        :param image: The image to compute the blake2b hash for. 
        :type image: PIL.Image.Image 
        
        :returns: The blake2b hash of the given image. 
        :rtype: str 
        """ 
        return hashlib.blake2b(image.tobytes()).hexdigest()
    

    def __count_unique_colors(self, image: Image.Image) -> int: 
        """counts unique RGB colors within a given image. 
        
        :param image: image to compute the number of unique colors for. 
        :type image: PIL.Image.Image

        :returns: The number of unique colors in the given image. 
        :rtype: int

        """
        
        image_array = np.array(image)
        return np.unique(image_array.reshape(-1, image_array.shape[-1] if image_array.ndim > 2 else 1), axis=0, return_counts=True)[1].size
    
    def __get_files_list(self, directory: str , recursive: bool) -> list[str]: 
        """gets the list of file paths inside a directory and also its subdirectories if recursive is set to True 
        :param directory: The directory to get the it's files paths
        :type directory: str
        :param recursive: If it's set to True the function will return paths of all files in the given directory 
                and all its subdirectories
        :type recursive: bool
        :returns: list of files
        :rtype: list[str]
        """
        if recursive is True: 
            return [os.path.join(root , file) for root , dirs , files in os.walk(directory) for file in files]
        else:      
            return [os.path.join(directory , path) for path in os.listdir(directory)]
        
    def __get_metadata(self, image_path) -> dict:
        """method to compute the chosen metadata of an image given its path,
        
        :param image_path: The path of the image required to get its metadata
        :type image_path: str

        :returns: metadata of the image as dictionary. 
        :rtype: dict
        """
        
        result = {} 
        try: 
            image = Image.open(image_path)
        
            result = {
                'image_path': image_path, 
                'image_name': os.path.splitext(os.path.basename(image_path))[0], 
                'image_blake2b_hash': self.__image_blake2b_hash(image), 
                'image_size_bytes': os.stat(image_path).st_size, 
                'image_resolution': image.size, 
                'image_xsize': image.size[0], 
                'image_ysize': image.size[1], 
                'unique_colors': self.__count_unique_colors(image), 
            }
        except Exception: 
            #image is corrupted 
            result = {
                'image_path': image_path, 
                'image_name': os.path.splitext(os.path.basename(image_path))[0], 
                'image_size_bytes': os.stat(image_path).st_size, 
            }
            
        return result
    
    def run(self, source_directory: str, output_type: str = 'csv', num_workers: int = 8) -> None:
        """given a directory containing images, process all those images and write a file with the metadata (in current directory)
            of those processed images, which are:
                        `image_path` , `image_name`, `image_blake2b_hash`, `image_size_bytes` , `image_dims_tuple`, `image_dims_string`, `unique_colors`
        
        :param source_directory: Directory containing the images to be processed. 
        :type source_directory: str
        :param output_type: The output type of the produced metadata file, `csv` or `json`, default us `csv` 
        :type output_type: str
        :param num_workers: Number of workers (threads) will be used to process the data.  
        :type num_workers: int
        
        :returns: writes the metadata file in the current directory. 
        :rtype: None

        """ 
        #Gets files list in the given directory
        images_paths = self.__get_files_list(source_directory, True)
        
        #Define the threads pool 
        thread_pool = ThreadPoolExecutor(max_workers = num_workers)
        futures = [] 
        #each call will be in separate thread with max threads of `num_workers`
        
        for image_path in images_paths: 
            task = thread_pool.submit(self.__get_metadata, image_path,)
            futures.append(task)
        
        #dicts to hold metadata of all directory. 
        valid_images_metadata = []
        failed_images_metadata = []
        
        finished = 0 
        for task in futures: 
            result = task.result()
            #if 'unique_colrs` is not found as key , then this thread processed a corrupted image. 
            if 'unique_colors' not in result: 
                failed_images_metadata.append(result)
            else:
                valid_images_metadata.append(result)
            
            finished += 1 
            
            if finished % 100 == 0: 
                print("Finished {} out of {} images, {} of them are valid and {} are corrupted.".format(finished , len(images_paths) , len(valid_images_metadata) , len(failed_images_metadata)))
        
        
        #write the files. 
        if output_type == 'json': 
            self.__write_json(valid_images_metadata, failed_images_metadata)
        else: 
            self.__write_csv(valid_images_metadata, failed_images_metadata)
        return  
    
def image_dataset_info_cli(source_directory: str, output_type: str = 'csv', num_workers: int = 8) -> None:
    """given a directory containing images, process all those images and write a file with the metadata (in current directory)
        of those processed images, which are:
                    `image_path` , `image_name`, `image_blake2b_hash`, `image_size_bytes` , `image_dims_tuple`, `image_dims_string`, `unique_colors`
    
    :param source_directory: Directory containing the images to be processed. 
    :type source_directory: str
    :param output_type: The output type of the produced metadata file, `csv` or `json`, default is `csv` 
    :type output_type: str
    :param num_workers: Number of workers (threads) will be used to process the data.  
    :type num_workers: int
    
    :returns: writes the metadata file in the current directory. 
    :rtype: None

    """ 
    
    start = time.time() 
    instance = ImageDatasetInfo()

    instance.run(source_directory, output_type, num_workers)
    
    print("Process took {} seconds to complete".format(time.time() - start))
    
if __name__ == "__main__": 
    
    fire.Fire(image_dataset_info_cli)
