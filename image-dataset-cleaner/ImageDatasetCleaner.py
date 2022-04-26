import base64
import os 
import shutil
from PIL import Image
import hashlib
import yaml
import fire 

class ImageDatasetCleaner: 
    
    def __init__(self) -> None:
        return 
    
    def get_files_list(directory: str , recursive: bool) -> list[str]: 
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


    def __write_dict_to_yaml(info: dict , folder_path: str , file_name: str) -> None: 
        """ Writes an dict object into yaml file given the output folder and file name to write in. 
        :param info: The dictionary to be written in the YAML file 
        :type info: dict
        :param folder_path: the output folder to write the file in it. 
        :type folder_path: str
        :param file_name: the yaml file name to be written, 
        :type file_name: str
        :returns: None
        :rtype: None
        """
        with open(os.path.join(folder_path , file_name), 'w') as yaml_file:
            yaml.dump(info , yaml_file, default_flow_style = False)

    def __base64url_encode(object: str) -> str: 
        """ encodes a string into base64url format 
        :param object: The object to be encoded to base64url. 
        :type object: str
        :returns: The base64url encodings of the given string
        :rtype: str
        """

        return base64.urlsafe_b64encode(bytes(object , 'utf-8')).decode('ascii')
    
    def __base64urlsha256(object: bytes , depth: int = 2) -> str: 
        """ Given a buffer of bytes, the function computes the sha256 recursively with `depth` times 
                    and returns it in base64url encodings
        :param object: The object to be encoded to base64sha256. 
        :type object: str
        :param depth: Number of repeated computations of the base64sha256 encodings 
        :type depth: int
        :returns: The base64sha256 encodings of the given string
        :rtype: str
        """
        if depth == 1: 
            return ImageDatasetCleaner.__base64url_encode(hashlib.sha256(object).hexdigest())
    
        return ImageDatasetCleaner.__base64urlsha256(bytes(hashlib.sha256(object).hexdigest(), 'ascii') , depth - 1)
    
    def process_images(self, source_directory: str , output_directory: str, allowed_formats = ['PNG' , 'JPEG'],
                                min_size: tuple = (32 , 32) , max_size = (16 * 1024 , 16 * 1024)) -> None: 
        #FixME -> Add steps of the processing to be more clear to the user. 
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
        :returns: None
        :rtype: None
        """
        
        #creates the output folder recursively if it doesn't exists 
        os.makedirs(output_directory , exist_ok = True)
        #Fetch the image paths list from the source directory 
        images_list = ImageDatasetCleaner.get_files_list(source_directory , False)
        #Info for each image 
        images_info = {} 
        failed_images = {} 
        counter = 0 
        #Loops over the whole image list in the source directory 
        for image in images_list: 
            #errors (conditions that weren't met at this image)
            errors = [] 
            counter += 1 
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
                                
                images_info[file_name] = {
                    'format': im.format.lower(), 
                    'original_file_name': file_name, 
                    'file_size': os.stat(image).st_size, 
                    'image_size': "({},{})".format(im.size[0] , im.size[1]), 
                    'sha256': hashlib.sha256(im.tobytes()).hexdigest(), 
                    'base64sha256': ImageDatasetCleaner.__base64urlsha256(im.tobytes() , depth = 1),
                }
                
            except Exception: 
                images_info[file_name] = {
                    'format': 'unk', 
                    'original_file_name': file_name, 
                    'file_size': os.stat(image).st_size, 
                    'image_size': 'unk', 
                    'sha256': 'unk', 
                    'base64urlsha256': 'unk', 
                }

            
            if not errors: 
                new_file_name = ImageDatasetCleaner.__base64urlsha256(im.tobytes())
                shutil.copy2(image , os.path.join(output_directory , "{}.{}".format(new_file_name , im.format.lower())))
                
                print("image {} out of {} was valid, original file: {}  new file: {}"
                                .format(counter , len(images_list) , file_name , new_file_name))
            else:
                failed_images[file_name] = {
                    'original_file_name': file_name, 
                    'errors': errors, 
                }
                
                print("image {} out of {} was NOT valid because of those errors: {} , original file: {}"
                        .format(counter , len(images_list) , errors , file_name))

            
            
        #Write the yaml files into the same output directory 
        ImageDatasetCleaner.__write_dict_to_yaml(failed_images , output_directory , 'failed-images.yml')
        ImageDatasetCleaner.__write_dict_to_yaml(images_info , output_directory , 'images-info.yml')
        
        return 



def image_dataset_cleaner_cli(source_directory: str , output_directory: str, allowed_formats = ['PNG' , 'JPEG'],
                                min_size: tuple = (32 , 32) , max_size = (16 * 1024 , 16 * 1024)) -> None: 
        """ Given a source directory containing images, it applies some conditions and copies 
                        the valid images into the `output_directory` and two yml files of the status of processed images 
                        saved in the same output directory with names `failed-images.yml` and `images-info.yml`
                
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
        :returns: None
        :rtype: None
        """
        dataset_cleaner = ImageDatasetCleaner()
        
        dataset_cleaner.process_images(source_directory , output_directory , allowed_formats , min_size , max_size)

if __name__ == "__main__": 
    
    #for pyinstaller 
    # command = input()
    # fire.Fire(image_dataset_cleaner_cli , command)
    
    fire.Fire(image_dataset_cleaner_cli)
    
