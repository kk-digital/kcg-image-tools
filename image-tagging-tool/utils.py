import hashlib
import os
import random
from PIL import Image
import datetime
import mimetypes
from fast_autocomplete import AutoComplete


mimetypes.init()


class Utils: 
    def __init__(self, dictionary_path: str = None) -> None:
        
        #initiate the dictionary 
        dictionary_words = {} 
        
        #if the dictionary file path was provided.
        if dictionary_path is not None and os.path.isfile(dictionary_path): 
            self.dictionary_words = self.__txt_dictionary_to_dict(dictionary_path)
        
        self.autocomplete = AutoComplete(words = dictionary_words)
        
        pass 
    
    
    def get_all_dictionary(self) -> list[str]: 
        """ method to get all words in the dictionary as a list.  
        
        :returns: a list containing all words in the dictionary. 
        :rtype: list[str]
        """
        return [word for word in self.autocomplete.words]

    def __txt_dictionary_to_dict(self, dictionary_path: str) -> dict :
        """ given the path of text file dictionary containing a word per each line, the method reads it and returns 
            the dictionary as python dict data structure.
        
        :param dictionary_path: the path to the text dictionary to extract its words. 
        :type dictionary_path: str
        
        :returns: the dictionary in dict format with each word as a key. 
        :rtype: dict 
        """
        
        #open dictionary file given the path 
        with open(dictionary_path) as txt_dictionary: 
            #read the text file line by line (each word is in a single line). 
            lines = txt_dictionary.readlines()
            return {line.rstrip(): {} for line in lines} 
    
    
    def _auto_complete(self, pattern: str) -> list[str]: 
        """method to auto complete a pattern to the nearest match from the provided dictionary. 
        
        :param pattern: the pattern to predict its nearest match from the dictionary. 
        :type pattern: str
        
        :returns: a list of the most matched words for the given pattern (the max length of the list is 5).
        :rtype: list[str]
        """
        return [word[0] for word in self.autocomplete.search(word = pattern, size = 5)]

    
    def _is_word_in_dictionary(self, word: str) -> bool: 
        """check if the given word is found in the dictionary.
        
        :param word: thw word to check if found in the dictionary.  
        :type word: str
        
        :returns: `True` if the word is found and `False` otherwise. 
        :rtype: bool
        """
    
        return word in self.autocomplete.words

    
    
    @staticmethod
    def image_metadata(image_dataset_directory: str, image_path: str, username: str, label: str, hashing_type: str = 'sha256') -> dict: 
        """ method to to extract and compute the metadata and basic information about the labeled image. 
        
        :param image_dataset_directory: the root path of the image directory. 
        :type image_dataset_directory: str
        :param image_path: the path of the image to computes its metadata. 
        :type image_path: str
        :param username: username of the user who have labeled/tagged this image. 
        :type username: str
        :param label: The label/tag assigned to the given image. 
        :type label: str
        :param hashing_type: the type of hashing to apply for the given image, default is `sha256`
        :type hashing_type: str
        :returns: metadata of the image with certain attributes. 
        :rtype: dict
        """
        metadata = {}
        #read the image, make sure it's not corrupted 
        try: 
            image = Image.open(image_path)
        
            metadata = {
                'username': username, 
                'task': label, 
                'image_hash_function': hashing_type, 
                'image_hash': Utils.compute_hash(image.tobytes(), hashing_type), 
                'image_dataset_directory': image_dataset_directory, 
                'image_path': image_path, 
                'image_filename': os.path.basename(image_path), 
                'image_size_bytes': os.stat(image_path).st_size, 
                'image_dimensions': image.size, 
                'tag_date': str(datetime.datetime.now()), 
                'tag_date_unix': datetime.datetime.now().timestamp(), 
            }
            
        except Exception: 
            metadata = {
                'username': username, 
                'label': label, 
                'image_dataset_directory': image_dataset_directory, 
                'image_path': image_path, 
                'image_name': os.path.basename(image_path), 
                'image_size_bytes': os.stat(image_path).st_size,
                'tag_date': str(datetime.datetime.now()), 
                'tag_date_unix': datetime.datetime.now().timestamp(), 
            } 

        return metadata
    
    @staticmethod
    def get_random_sample(source: list, sample_size: int = 16, seed: int = None) -> list: 
        """ given a list, select random sample out of this list of size `sample_size` and you it's optional to provide the seed.
        
        :param source: the source list to go over and take samples from it. 
        :type source: list
        :param sample_size: the size of the sample to take from the source list, default is `16`. 
        :type sample_size: int
        :param seed: seed of the pseudo generator, default is `None`
        :type seed: int
        :returns: list of dict each containing an only attribute called `url` contains the file path as its value. 
        :rtype: list
        """
        #if the seed was specified by the user. 
        if seed is not None:         
            #define the seed generated by the user. 
            random.seed(seed)
        
        #return the random sample from the source with the specified sample size.
        return random.sample(source, min(sample_size , len(source)))
    

    @staticmethod
    def __is_image(file_name: str) -> bool:
        """ method that checks if a file is an image or not.  
        :param file_name: the 
        :type file_name: str
        :returns: True if the provided file is an image, False otherwise. 
        :rtype: bool
        """
        #guess the type of the file from its name. 
        mimestart = mimetypes.guess_type(file_name)[0]

        #split the mime name with / and check the first part. 
        if mimestart != None:
            mimestart = mimestart.split('/')[0]
            #make sure the file type is an image. 
            if mimestart in ['image']:
                return True
        
        return False

    @staticmethod
    def get_images_list(directory: str) -> list[str]: 
        """ method to get all the images inside a certain directory. 
        :param directory: The directory path to go over it and get its contents. 
        :type directory: str
        :returns: list of dict each containing an only attribute called `url` contains the image path as its value. 
        :rtype: str
        """
        return [{'url': os.path.join(os.path.relpath(root, directory), file)} for root , dirs , files in os.walk(directory) for file in files if Utils.__is_image(file)]
    
    @staticmethod
    def compute_hash(object: bytes, hashing_type: str) -> str: 
        """ method to compute the hash of a bytes object for a chosen hashing type. 
        :param object: The bytes object to be hashed. 
        :type object: bytes
        :param hashing_type: the type of hashing to be applied to the provided bytes, supported types are sha256 and blake2b. 
        :type hashing_type: str
        :returns: a string which represents the hashing of the bytes object sent by the user. 
        :rtype: str
        """
        #make sure the received object is an instance of bytes. 
        assert isinstance(object, bytes)
        
        #Check the chosen hashing type. 
        if hashing_type == 'blake2b': 
            return hashlib.blake2b(object).hexdigest()
        elif hashing_type == 'sha256':
            return hashlib.sha256(object).hexdigest()
        else: 
            raise Exception("{} hashing type is not found only blake2b & sha256 are supported.")
        

if __name__ == "__main__":
    pass     