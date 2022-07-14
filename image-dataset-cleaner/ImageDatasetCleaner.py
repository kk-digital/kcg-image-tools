import base64
import multiprocessing
import os 
import shutil
from typing_extensions import Self
from PIL import Image
import hashlib
import fire 
import json 
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathos.multiprocessing import ProcessingPool
import patoolib

from Base36lib import Base36

class ImageDatasetCleaner: 
    
    def __init__(self) -> None:
        self.copied_files = {} 
        return 
    
    @staticmethod
    def __get_files_list(directory: str , recursive: bool) -> list[str]: 
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

    @staticmethod
    def __write_dict_to_json(info: dict , folder_path: str , file_name: str) -> None: 
        """ Writes an dict object into json file given the output folder and file name to write in. 
        :param info: The dictionary to be written in the JSON file 
        :type info: dict
        :param folder_path: the output folder to write the file in it. 
        :type folder_path: str
        :param file_name: the json file name to be written, 
        :type file_name: str
        :returns: None
        :rtype: None
        """
        with open(os.path.join(folder_path , file_name), 'w') as json_file:
            json.dump(info , json_file , indent = 4)
    @staticmethod
    def __decompress_file(compressed_file_path: str, output_path: str) -> None:
        """decompress the content of compressed file into `rar`, `zip`, `gz` or any other file type as long it's supported on the os.
        
        :param compressed_file_path: The path for the compressed file to decompress.
        :type compressed_file_path: str
        :param output_path: the directory to save the result at. 
        :type output_path: str
        
        :returns: 
        :rtype: None
        """ 
        patoolib.extract_archive(compressed_file_path, outdir = output_path)


    @staticmethod
    def __compress_folder(folder_path: str, zip_folder_path: str) -> None: 
        """Given a folder path compress it and saves the result in the provided `zip_folder_path`. 
        
        :param folder_path: the folder path which should be compressed along with its contents.
        :type folder_path: str
        :param zip_folder_path: The path of the compressed file to store at. 
        :type zip_folder_path: str

        :returns: 
        :rtype: None
        """
        
        cwd = os.getcwd()
        os.chdir(folder_path)
        patoolib.create_archive(zip_folder_path, tuple(os.listdir(folder_path)))
        os.chdir(cwd)

    @staticmethod
    def __is_archive(file_path: str) -> bool:
        """TODO docs 
        """ 
        
        try: 
            patoolib.get_archive_format(file_path)
            return True 
        except Exception: 
            return False
    
    
    @staticmethod
    def __make_iterable_from_value(value, length: int) -> list: 
        """TODO docs 
        """
        return [value] * length


    @staticmethod
    def __base64url_encode(object: str) -> str: 
        """ encodes a string into base64url format 
        :param object: The object to be encoded to base64url. 
        :type object: str
        :returns: The base64url encodings of the given string
        :rtype: str
        """

        return base64.urlsafe_b64encode(bytes(object , 'utf-8')).decode('ascii')
    
    @staticmethod
    def __base64urlblake2b(object: bytes , depth: int = 2) -> str: 
        """ Given a buffer of bytes, the function computes the blake2b recursively with `depth` times 
                    and returns it in base64url encodings
        :param object: The object to be encoded to base64blake2b. 
        :type object: str
        :param depth: Number of repeated computations of the base64blake2b encodings 
        :type depth: int
        :returns: The base64blake2b encodings of the given string
        :rtype: str
        """
        if depth == 1: 
            return ImageDatasetCleaner.__base64url_encode(hashlib.blake2b(object).hexdigest())
    
        return ImageDatasetCleaner.__base64urlblake2b(bytes(hashlib.blake2b(object).hexdigest(), 'ascii') , depth - 1)
    
    def __validate_image_task(self, image: str, output_directory: str, allowed_formats = ['PNG' , 'JPEG'],
                              min_size: tuple = (32 , 32) , max_size = (16 * 1024 , 16 * 1024), base36: int = None): 
        """ Given an image path read it and make the validation steps specified in the cleaner, then return the info 
                        
        :param image: The path for the image to be validated.
        :type image: str
        :param output_directory: The directory to copy the images into it. 
        :type output_directory: str
        :param allowed_formats: list of the allowed image formats to be considered in the copied folder 
        :type allowed_formats: list
        :param min_size: min target image size (if the image is less than it then it's ignored and not copied). 
        :type min_size: tuple
        :param max_size: max target image size (if the image is larger than it then it's ignored and not copied). 
        :type max_size: tuple
        :param base36: Number of 1st N chars of base36 of the base64url of the blake2b of the image, if is set to `None` then nothing is applied.
        :type base36: int
        :returns: The original image file name, the new image file name,   `image_info` and `failed_image` and errors and list.  
        :rtype: (str, str, dict, dict, list)
        """

        errors = [] 
        image_info = {} 
        failed_image = {} 
        
        #try to open the image and check if not corrupted 
        try: 
            #try to lazy loading for the image and verify it's not corrupted. 
            im = Image.open(image)
            #checks is the image format is PNG or JPEG as specified. 
            if im.format not in allowed_formats: 
                errors.append('Image format is not PNG nor JPEG it\'s {}'.format(im.format))
            
            #checks if the image size is smaller than the target size 
            if im.size < min_size: 
                errors.append('The image is smaller than the target size, image size is {}'.format(im.size))
            elif im.size > max_size: 
                errors.append('The image is larger than the target size, image size is {}'.format(im.size))
            #verifies that the image is not corrupted 
            im.verify()
        except Exception:
            errors.append("Image is corrupted")
        
        _ , file_name = os.path.split(image)

        try: 
            im = Image.open(image)
                            
            image_info = {
                'format': im.format.lower(), 
                'original_file_name': file_name, 
                'file_size': os.stat(image).st_size, 
                'image_size': "({},{})".format(im.size[0] , im.size[1]), 
                'blake2b': hashlib.blake2b(im.tobytes()).hexdigest(), 
                'base64urlblake2b': ImageDatasetCleaner.__base64urlblake2b(im.tobytes() , depth = 1),
            }
            
        except Exception: 
            image_info = {
                'format': 'unk', 
                'original_file_name': file_name, 
                'file_size': os.stat(image).st_size, 
                'image_size': 'unk', 
                'blake2b': 'unk', 
                'base64urlblake2b': 'unk', 
            }

        #init the variable to make sure it return something if there is errors with the image
        new_file_name = '' 
        if not errors: 
            try: 
                new_file_name = ImageDatasetCleaner.__base64urlblake2b(im.tobytes())
                #check if base36 was chosen as the naming convention for the files
                if base36 is not None: 
                    new_file_name = Base36.encode(new_file_name)[:min(len(new_file_name), base36)]
                
                #make sure the image was not written before to the directory. 
                if new_file_name not in self.copied_files: 
                    self.copied_files[new_file_name] = True 
                    shutil.copy2(image , os.path.join(output_directory , "{}.{}".format(new_file_name , im.format.lower())))
            
            except Exception as ex: 
                errors.append("Image is corrupted")
        
        if errors:
            failed_image = {
                'original_file_name': file_name, 
                'errors': errors, 
            }
            

        return file_name, new_file_name, image_info, failed_image, errors
    
    @staticmethod
    def __clean_images(source_directory: str , output_directory: str, image_cleaner_instance: Self, allowed_formats = ['PNG' , 'JPEG'],
                                min_size: tuple = (32 , 32) , max_size = (16 * 1024 , 16 * 1024), base36: int = None, write_status_files: bool = False,  num_workers: int = 8) -> None: 
        """ Given a source directory containing images, it applies some conditions and copies 
                        the valid images into the `output_directory` 
                        
        :param source_directory: The source directory containing the images to apply the conditions on 
        :type source_directory: str
        :param output_directory: The directory to copy the images into it. 
        :type output_directory: str
        :param allowed_formats: list of the allowed image formats to be considered in the copied folder 
        :type allowed_formats: list
        :param min_size: min target image size (if the image is less than it then it's ignored and not copied). 
        :type min_size: tuple
        :param max_size: max target image size (if the image is larger than it then it's ignored and not copied). 
        :type max_size: tuple
        :param base36: Number of 1st N chars of base36 of the base64url of the blake2b of the image, if is set to `None` then nothing is applied.
        :type base36: int
        :param write_status_files: if `True` the tool writes the status of the processed images in two files 
                    `failed-images.json` and `images-info.json` in the same directory, default is `False`
        :type write_status_files: bool
        
        :param num_workers: number of workers (threads) to be used in the process, default value is `8`. 
        :type num_workers: int
        :returns: None
        :rtype: None
        """
        
        #creates the output folder recursively if it doesn't exists 
        os.makedirs(output_directory , exist_ok = True)
        #Fetch the image paths list from the source directory 
        images_list = ImageDatasetCleaner.__get_files_list(source_directory , recursive = True)
        
        #Info for each image 
        images_info = {} 
        failed_images = {} 
        counter = 0 
        
        #Fetch all files previously available in output_directory
        image_cleaner_instance.copied_files = {os.path.splitext(os.path.basename(path))[0]: True for path in ImageDatasetCleaner.__get_files_list(output_directory, False)}

        #Define the thread pool. 
        thread_pool = ThreadPoolExecutor(max_workers = num_workers)
        futures = [] 
        #Loops over the whole image list in the source directory 
        for image in images_list: 
            #errors (conditions that weren't met at this image)
            
            task = thread_pool.submit(image_cleaner_instance.__validate_image_task, image, output_directory, allowed_formats, min_size, max_size,base36,)
            futures.append(task)
        
        #loop over threads and fetch data from completed threads.
        for task in as_completed(futures): 
            
            counter += 1 
            file_name, new_file_name, image_info, failed_image, errors = task.result() 
            
            images_info[file_name] = image_info
            
            if errors: 
                failed_images[file_name] = failed_image
                print("image {} out of {} was NOT valid because of those errors: {} , original file: {}"
                        .format(counter , len(images_list) , errors , file_name))
            else: 
                print("image {} out of {} was valid, original file: {}  new file: {}"
                    .format(counter , len(images_list) , file_name , new_file_name))

        #Write the json files into the same output directory 
        if write_status_files is True: 
            ImageDatasetCleaner.__write_dict_to_json(failed_images , output_directory , 'failed-images.json')
            ImageDatasetCleaner.__write_dict_to_json(images_info , output_directory , 'images-info.json')
        
        return 

    
    def process_directory(self, source_directory: str,  output_directory: str, prefix_name: str, allowed_formats = ['PNG' , 'JPEG'],
                                min_size: tuple = (32 , 32) , max_size = (16 * 1024 , 16 * 1024), base36: int = None, write_status_files: bool = False, num_processes: int = multiprocessing.cpu_count(), num_threads: int = 8) -> None: 
        """TODO docs. 
        """
        
        #get the list of all files in the source directory. 
        files_list = ImageDatasetCleaner.__get_files_list(source_directory ,   recursive = True)
        
        #define the processes pool. 
        pool = ProcessingPool(num_processes)
        archives_count = 1 
        to_archive_paths = [] 
        
        
        
        for file in files_list:
            if ImageDatasetCleaner.__is_archive(file): 
                #get the root path and the file name 
                root_path, filename = os.path.split(file)
                
                #make the new folder path
                decompressed_path = os.path.join(root_path, "TMP_{}_{}".format(prefix_name, str(archives_count).zfill(6)))
                os.makedirs(decompressed_path, exist_ok = True)
                to_archive_paths.append(decompressed_path)
                archives_count += 1 

                #decompress the file
                ImageDatasetCleaner.__decompress_file(file, decompressed_path)
                
                #delete the compressed file. 
                os.remove(file)


        
        #clean the images inside the zipped folder. 
        save_folder_paths = [decompressed_path.replace("TMP_", "") for decompressed_path in to_archive_paths]

        image_dataset_cleaner_instances = [] 
        compressed_files_count = len(save_folder_paths)
        
        for _ in range(compressed_files_count): 
            instance = ImageDatasetCleaner()
            image_dataset_cleaner_instances.append(instance)
        
        #clean all decompressed folders. 
        pool.map(ImageDatasetCleaner.__clean_images, to_archive_paths, save_folder_paths, image_dataset_cleaner_instances,
                             ImageDatasetCleaner.__make_iterable_from_value(allowed_formats, compressed_files_count) , ImageDatasetCleaner.__make_iterable_from_value(min_size, compressed_files_count),
                             ImageDatasetCleaner.__make_iterable_from_value(max_size, compressed_files_count),ImageDatasetCleaner.__make_iterable_from_value(base36, compressed_files_count),
                             ImageDatasetCleaner.__make_iterable_from_value(write_status_files, compressed_files_count), ImageDatasetCleaner.__make_iterable_from_value(num_threads, compressed_files_count)),             
        
        
        #remove decompressed folders after they were cleaned. 
        for folder_path in to_archive_paths: 
            shutil.rmtree(folder_path)
        
        #zip all decompressed folders. 
        pool.map(ImageDatasetCleaner.__compress_folder, save_folder_paths, ["{}.zip".format(file) for file in save_folder_paths])

        
        for folder_path in save_folder_paths: 
            shutil.rmtree(folder_path)
        
        #close the pool to avoid any errors.
        pool.close()
    
def image_dataset_cleaner_cli(source_directory: str , output_directory: str = None, compressed_files_dir: bool = False, prefix_name: str = "", allowed_formats = ['PNG' , 'JPEG'],
                                min_size: tuple = (32 , 32) , max_size = (16 * 1024 , 16 * 1024), base36: int = None, write_status_files: bool = False, num_processes: int = multiprocessing.cpu_count(), num_threads: int = 8) -> None: 
        """ Given a source directory containing images, it applies some conditions and copies 
                        the valid images into the `output_directory` and two json files of the status of processed images 
                        saved in the same output directory with names `failed-images.json` and `images-info.json` if `write_status_files` was set to True. 
                
            applied conditions are: 
                1-Make sure if the image file is not corrupted
                2-Checks if the image format is within the given allowed formats. 
                3-Check if the image size is withing the range of `min size` and `max size` provided by the user. 
                        
        :param source_directory: The source directory containing the images to apply the conditions on 
        :type source_directory: str
        :param output_directory: The directory to copy the images into it. 
        :type output_directory: str
        :param allowed_formats: list of the allowed image formats to be considered in the copied folder Formats MUST be in Capilat letters.
        :type allowed_formats: list
        :param min_size: min target image size (if the image is less than it then it's ignored and not copied). 
        :type min_size: tuple
        :param max_size: max target image size (if the image is larger than it then it's ignored and not copied). 
        :type max_size: tuple
        :param base36: Number of 1st N chars of base36 of the base64url of the blake2b of the image, if is set to `None` then nothing is applied.
        :type base36: int
        :param write_status_files: if `True` the tool writes the status of the processed images in two files 
                    `failed-images.json` and `images-info.json` in the same directory, default is `False`
        :type write_status_files: bool
        
        :param num_workers: number of workers (threads) to be used in the process, default value is `8`. 
        :type num_workers: int
        :returns: None
        :rtype: None
        """
        
        dataset_cleaner = ImageDatasetCleaner()
        if compressed_files_dir is True: 
            dataset_cleaner.process_directory(source_directory , output_directory , prefix_name, allowed_formats,
                                              min_size , max_size ,base36, write_status_files, num_processes, num_threads)
        else: 
            
            if output_directory is None: 
                raise FileNotFoundError("Please provide a valid output directory")
            
            #clean main folder. 
            ImageDatasetCleaner.__clean_images(source_directory, output_directory, ImageDatasetCleaner(), 
                                            allowed_formats, min_size, max_size, base36, write_status_files, num_threads)


if __name__ == "__main__": 
        
    fire.Fire(image_dataset_cleaner_cli)
