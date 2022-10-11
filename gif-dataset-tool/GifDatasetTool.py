import hashlib
import json
import multiprocessing
from typing import Union
from PIL import Image, ImageSequence
import os 
from pathos.multiprocessing import ProcessingPool
import numpy as np 
import click 

class GifDatasetTools: 
    """wrapper for methods that help to manipulate and datasets/folders containing gif images. 
    """
    def __init__(self) -> None:
        pass
    
    def filter_files(self, files: list[str], allowed_exts: list[str]) -> list[str]: 
        """method to filter a list of file names depending on their certain allowed extensions provided in `allowed_exts` list.
        """
        
        return [file for file in files if os.path.splitext(file)[1] in allowed_exts]
    
    
    def get_files_list(self, folder_path: str, recursive: bool = True) -> list[str]: 
        """method to list all files in the provided directory, if `recursive` is True then 
                it will loop recursively over the root folder and all its sub-folders. 
        """
        
        if recursive: 
            return [os.path.join(dir_path, file_name) for dir_path, dir_names, file_names in os.walk(folder_path) for file_name in file_names]
        else: 
            return [os.path.join(folder_path, file_name) for file_name in os.listdir(folder_path)]
    
    @staticmethod
    def image_sha256(image: Image.Image) -> str: 
        """compute the sha256 of the given image. 
        """
        return hashlib.sha256(image.tobytes()).hexdigest()

    @staticmethod
    def gif_metadata(image: Union[Image.Image, str]) -> dict: 
        """method to compute the metadata of a given GIF image. 
        """
        
        if isinstance(image, str):
            image = Image.open(image)
            
        return {
            'original_file_name': os.path.abspath(image.filename), 
            'sha256': GifDatasetTools.image_sha256(image),
            'number_of_frames': GifDatasetTools.get_number_of_frames(image),
            'file_size': os.stat(image.filename).st_size , 
            'image_size': "({},{})".format(image.size[0] , image.size[1]),
            'format': image.format.lower(),
        }

    @staticmethod
    def save_image(image: Image.Image, path: str) -> None: 
        """save the given image in PNG format at the given path. 
        """
        image.save(path)
    
    @staticmethod
    def get_number_of_frames(gif_image: Union[str, Image.Image]) -> int: 
        """method to return the number of frames for a given gif image. 
        """
        
        if isinstance(gif_image, str): 
            gif_image = Image.open(gif_image)
        
        return gif_image.n_frames
    
    @staticmethod
    def extract_gif_frames(gif_image: Union[str, Image.Image], save_folder_path: str, limit: int = 0) ->  dict:
        """method that extracts `limit` number of frames of a given GIF image and writes them as PNG, and returns the GIF image metadata.  
                if `limit >= actual_frames_number`  then all frames is being returned. 
                if `limit < actual_frames_number` then `limit` number of frames are selected at random and returned. 
                if `limit is 0`, then all frames will be extracted
        """
        
        #if the provided gid_image variables is a path. 
        if isinstance(gif_image, str):
            gif_image = Image.open(gif_image)
        
        #if the conditions to choose all the frames is met. 
        if limit == 0 or limit > gif_image.n_frames: 
            chosen_frames = range(gif_image.n_frames)
        else:
            #choose random `limit` indices from [0, gif_image_frames_number[
            chosen_frames = np.random.choice(gif_image.n_frames, limit, replace=False)
        
        frames_iter = ImageSequence.Iterator(gif_image)
        frames = [] 
        
        #extract the selected frames. 
        for frame_index in chosen_frames:
            #construct the output filename and the frame number for a certain more user friendly format. 
            file_name = os.path.splitext(os.path.basename(gif_image.filename))[0]
            frame_number = str(frame_index).zfill(5)
            #write the frame to disk. 
            frames_iter[frame_index].save(os.path.join(save_folder_path, '{}_frame_no_{}.png'.format(file_name, frame_number)))
        
        #compute the image metadata. 
        image_metadata = {
            'original_file_name': os.path.abspath(gif_image.filename), 
            'sha256': GifDatasetTools.image_sha256(gif_image),
            'number_of_frames': GifDatasetTools.get_number_of_frames(gif_image),
            'file_size': os.stat(gif_image.filename).st_size , 
            'image_size': "({},{})".format(gif_image.size[0] , gif_image.size[1]),
            'format': gif_image.format.lower(),
        }

        return image_metadata
    
    

@click.command()
@click.option('--folder_path', help='path to the folder contains the GIF images to process.', type = str, required = True)
@click.option('--output_folder_path', help='path to the folder to write the results to', type = str, required = True)
@click.option('--extract_frames', help='option to extract frames out of the GIF image or not.', type = bool, default = True)
@click.option('--frames_limit', help='the max number of frames to extract from each GIF image in the folder.', type = int, default = 0)
@click.option('--num_processes', help='number of processes to use for executing the task.', type = int, default = multiprocessing.cpu_count())
def process_gif_dataset(folder_path: str, output_folder_path: str, extract_frames: bool = True, frames_limit: int = 0, num_processes: int = multiprocessing.cpu_count()) -> None: 
    """tool to process a folder of GIF images and extract their metadata and option to extract certain number of frames out of each Gif.
    """
    
    #if the output folder is not already exists then create it. 
    os.makedirs(output_folder_path, exist_ok = True)
    
    #initialize an instance of the GIF tools class. 
    gif_tools = GifDatasetTools()
    
    #get the list of the files for the given directory. 
    files_paths = gif_tools.get_files_list(folder_path, recursive = True)
    
    processing_pool = ProcessingPool(num_processes)
    
    #option to extract frames was not selected. 
    if extract_frames:
        #extract the image frames
        images_metadata = processing_pool.map(gif_tools.extract_gif_frames, files_paths,[output_folder_path] * len(files_paths),  [frames_limit] * len(files_paths))
    else:
        #extract the images metadata. 
        images_metadata = processing_pool.map(gif_tools.gif_metadata, files_paths)        

    #save the metadata in a `JSON` file format in the output folder. 
    with open(os.path.join(output_folder_path, 'images_metadata.json'), 'w', encoding = 'utf-8') as metadata_file: 
        json.dump(images_metadata, metadata_file, indent = 4, sort_keys = True)

    processing_pool.close()

@click.group()
def cli(): 
    pass 

cli.add_command(process_gif_dataset)

if __name__ == "__main__": 
    cli() 