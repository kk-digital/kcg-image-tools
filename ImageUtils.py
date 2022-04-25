import base64
import os 
import re
import shutil
from PIL import Image
import hashlib
import yaml


class ImageUtils: 
    
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

    def __allowed_type(file: str , allowed_types: list = []) -> bool: 
        """Returns True only if the given file path is from the allowed file types by the user 
        :param file: The file path needed to validate 
        :type file: str
        :param allowed_types: list of the allowed file types , leave empty if you want to allow any type 
        :type allowed_types: list
        :returns: True if the file type is within the allowed list 
        :rtype: bool
        """
        return True if len(allowed_types) == 0 else (os.path.splitext(file)[1] in allowed_types)

    def validate(directory: str , recursive: bool = False , allowed_types = []) -> list:
        #FixME -> Add the steps of validation to be clear for the user. 
        """Validates all images contained in the path given with all it's subdirectories as well if recursive is true
        :param directory: The directory containing the files to be validated 
        :type directory: str
        :param recursive: If it's set to True the function will search and validate all images in 
                the given directory and all its subdirectories
        :type recursive: bool
        :param allowed_types: list of the allowed images extensions if it's empty then all image types will be considered 
        :type allowed_types: list
        :returns: list of files that failed the validation 
        :rtype: list[str]
        """
        
        #gets the whole files from the directory 
        files_list = ImageUtils.get_files_list(directory , recursive)
        #execlude only files 
        images_list = [file for file in files_list if ImageUtils.__allowed_type(file , allowed_types)]
        
        #List of invalid files to make the function return it
        failed_validation = set()
        
        #Remove any file that has non-base64 character as a file name 
        #Regular expression used to match strings containing only base64 chars 
        #FixME add options to execlude ASCII characters as well.
        regular_exp = re.compile(r'^[a-zA-Z0-9+/=]*$')
        [failed_validation.add(image) for image in images_list if regular_exp.fullmatch(os.path.splitext(os.path.split(image)[-1])[0]) is None]
        
        for image in images_list: 
            try: 
                #try to open the image if it was corrupted it will return an exception 
                im = Image.open(image)
                _ , image_extension = os.path.splitext(image)

                #check if the file extension matches the image format an exception is applied for jpeg and jpg files as they are the same
                if im.format is None or im.format.lower() != image_extension.lower()[1:]: 
                    if image_extension.lower()[1:] == 'jpg' and im.format.lower() == 'jpeg': 
                        continue
                    #image is invalid because its extension doesn't match its format 
                    failed_validation.add(image)
                    
                im.verify()
            except Exception: 
                #File is invalid because it's corrupted 
                failed_validation.add(image)
            
            
        return list(failed_validation)

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

    def __base64_encode(object: str) -> str: 
        """ encodes a string into base64 format 
        :param object: The object to be encoded to base64. 
        :type object: str
        :returns: The base64 encodings of the given string
        :rtype: str
        """
        return base64.b64encode(bytes(object , 'utf-8'))
    
    def __base64sha256(object: bytes , depth: int = 2) -> str: 
        """ Given a buffer of bytes, the function computes the sha256 recursively with `depth` times 
                    and returns it in base64 encodings
        :param object: The object to be encoded to base64sha256. 
        :type object: str
        :param depth: Number of repeated computations of the base64sha256 encodings 
        :type depth: int
        :returns: The base64sha256 encodings of the given string
        :rtype: str
        """
        if depth == 1: 
            return ImageUtils.__base64_encode(hashlib.sha256(object).hexdigest())
    
        return ImageUtils.__base64sha256(bytes(hashlib.sha256(object)) , depth - 1)
    
    def process_images(source_directory: str , output_directory: str , target_size: tuple = (128 , 128)) -> None: 
        #FixME -> Add steps of the processing to be more clear to the user. 
        """ Given a source directory containing images, it applies some conditions and copies 
                        the valid images into the `output_directory` 
                        
        :param source_directory: The source directory containing the images to apply the conditions on 
        :type source_directory: str
        :param output_directory: The directory to copy the images into it. 
        :type output_directory: str
        :param target_size: target image size (if the image is less than it then it's ignored and not copied). 
        :type target_size: tuple
        :returns: None
        :rtype: None
        """
        
        #creates the output folder recursively if it doesn't exists 
        os.makedirs(output_directory , exist_ok = True)
        #Fetch the image paths list from the source directory 
        images_list = ImageUtils.get_files_list(source_directory , True)
        
        #Info for each image 
        images_info = {} 
        failed_images = {} 
        #Loops over the whole image list in the source directory 
        for image in images_list: 
            #errors (conditions that weren't met at this image)
            errors = [] 
            corrupted = False 
            #try to open the image and check if not corrupted 
            try: 
                #try to lazy loading for the image and verify it's not corrupted. 
                im = Image.open(image)
                #checks is the image format is PNG or JPEG as specified. 
                if im.format not in ['PNG' , 'JPEG']: 
                    errors.append('Image format is not PNG nor Jpeg it\'s {}'.format(im.format.lower()))
                
                #checks if the image size is smaller than the target size 
                if im.size < target_size: 
                    errors.append('The image is smaller than the target size, image size is {}'.format(im.size))
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
                    'image_size': im.size, 
                    'sha256': hashlib.sha256(im.tobytes()).hexdigest(), 
                    'base64sha256': ImageUtils.__base64sha256(im.tobytes() , depth = 1),
                }
                
            except Exception: 
                images_info[file_name] = {
                    'format': 'unk', 
                    'original_file_name': file_name, 
                    'file_size': os.stat(image).st_size, 
                    'image_size': 'unk', 
                    'sha256': 'unk', 
                    'base64sha256': 'unk', 
                }

            
            if not errors: 
                new_file_name = ImageUtils.__base64sha256(im.tobytes())
                shutil.copy2(image , os.path.join(output_directory , new_file_name , '.' , im.format.lower()))
            else:
                
                failed_images[file_name] = {
                    'original_file_name': file_name, 
                    'errors': errors, 
                }
            
        #Write the yaml files into the same output directory 
        ImageUtils.__write_dict_to_yaml(failed_images , output_directory , 'failed-images.yml')
        ImageUtils.__write_dict_to_yaml(images_info , output_directory , 'images-info.yml')
        
        return 

if __name__ == "__main__": 
    a = "AAasjsldjalsjdaoudoqweuojd;sfsd"
    
    print(base64.b64encode(bytes(hashlib.sha256(bytes(a , 'utf-8')).hexdigest() , 'utf-8')))