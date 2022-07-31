import json
from flask import Flask, render_template, send_from_directory, url_for, request
from utils import Utils
from flask_cors import CORS
import os 
from urllib.parse import unquote
import fire 

#start the Flask app and define the templates folder path. 
app = Flask(__name__, static_folder='./templates/libs', template_folder='templates')
#allow cors requests. 
CORS(app)

utils = None 
#global variables their values should be passed by the user in the cli.  
images_folder = "" 
files_list = [] 
N = 4 
seed = None 
   
   
#index of the web app. 
@app.route('/', methods = ['GET'])
def index(): 
    """returns the index page of the tool and generates a random sample of images to start with. 
    """
    #should send an initial sample.    
    return render_template('index.html', aesthetic_score_image = Utils.get_random_sample(files_list, 1)[0], images = Utils.get_random_sample(files_list , N * N), labels = tags, username = username, predicted_tags = utils.get_all_dictionary())


@app.route('/taggingTool/api/checkTag')
def check_if_tag_found(): 
   """endpoint to check if a certain tag is found in the dictionary (in the dictionary.txt file)
   """
   return utils._is_word_in_dictionary(request.json['tag'])

@app.route('/taggingTool/api/predictTag')
def predict_tag_from_pattern(): 
   """endpoint to make a prediction from a given pattern based on the given dictionary.
   """
   return utils._auto_complete(request.json['pattern'])


#get random images urls to be sampled
@app.route('/taggingTool/api/getImages/<path:filename>')
def get_images(filename): 
   """endpoint to serve the images from the image dataset folder given the image file name as a param.  
   """
   #serving the required image from the image dataset folder provided by the user when running the tool. 
   return send_from_directory(os.path.join(images_folder, os.path.dirname(filename)), unquote(os.path.basename(filename)), as_attachment=True)

@app.route('/taggingTool/api/labelImages' , methods = ["POST"])
def label_images():
   """endpoint responds to POST requests containing the labeled/tagged images info inside the request body, 
      the endpoint computes the selected images metadata and stores them inside a json file within the same path. 
   """
   #open and compute the hash of the images. 
   images_metadata = [Utils.image_metadata(images_folder, unquote(os.path.join(images_folder, os.path.basename(image_path))), request.json['username'], request.json['label'], 'sha256') for image_path in request.json['images']]
   
   
   if request.json['task'] == 'aesthetic-score': 
      images_metadata[0]['score'] = int(request.json['score'])
      images_metadata[0]['img_tags'] = request.json['img_tags']
      
   #store the images metadata and labels sent by user inside json file. 
   labeled_images = {} 
   
   output_file_path = os.path.join(output_directory, request.json['label'] + '.json')
   
   #if the json file storing the labels is not found then create it. 
   if not os.path.isfile(output_file_path): 
      json.dump(labeled_images, open(output_file_path, 'w'), indent = 4)
   
   try: 
      
      with open(output_file_path, "r") as labels_file: 
         #loads the json file into dict to update it with the new values. 
         labeled_images = json.load(labels_file)
         #the label chosen by the user. 
         label = request.json['label']
         #Check if the tag is not already found in 
         if label not in labeled_images: 
            labeled_images[label] = {'tag_task': label, 'tag_data': []}
         #update the tagged data. 
         labeled_images[label]['tag_data'].extend(images_metadata)
      
   except Exception as ex:   
      print(ex)    
      pass  
   
   with open(output_file_path, "w") as labels_file: 
      json.dump(labeled_images, labels_file, indent = 4)

   #remove the labeled images from the files list. 
   for image in request.json['images']: 
      #Make the path in the same format of paths in files_list variable. 
      image_path = {'url': unquote(os.path.basename(image))}
      #if the image path in the files_list remove it as it's already labeled (it should always be found)
      if image_path in files_list: 
         files_list.remove(image_path)
   
   #Change the global username to the new one. 
   username = request.json['username']
   
   #return a new list of images to the user to label. 
   return render_template('index.html', aesthetic_score_image = Utils.get_random_sample(files_list, 1)[0], images = Utils.get_random_sample(files_list, N * N), labels = tags, username = username, active_label = label,  predicted_tags = utils.get_all_dictionary())



def image_tagging_tool_cli(images_dataset_directory: str, tag_tasks: list, data_output_directory: str, dictionary_path: str = None,  grid_dim: int = 4, samples_seed: int = None) -> None: 
   """ given an image dataset directory and the tag tasks you need to apply for this dataset, the tool runs web UI can be found at 
         http://127.0.0.1:5000 with a grid of images taken from the image directory you have passed to be used for tagging depending 
            on the task you choose, the tagged images metadata can be found inside the `data_output_directory` as `json` files. 
   
   :param images_dataset_directory: the root path of the image dataset directory. 
   :type images_dataset_directory: str
   :param tag_tasks: the tagging tasks/labels to use in the tool, and should be provided as a list. 
   :type tag_tasks: list
   :param data_output_directory: the directory to write the resultant `json` files inside, the `json` files contains the tagged images metadata.
   :type data_output_directory: str
   :param dictionary_path: path to the dictionary to be used in tagging the `Aesthetic scores` task. 
   :type dictionary_path: str
   :param grid_dim: the dimension of the grid displaying the images, the grid is a square default dim is `4`. 
   :type grid_dim: int
   :param samples_seed: seed of the pseudo random generator generating the sample images generated to be displayed in the grid, default is `None`
   :type samples_seed: int
   :returns: 
   :rtype: None
   """
   global images_folder 
   images_folder = images_dataset_directory
   
   global tags
   tags = [{'id': index, 'name': label} for index, label in enumerate(tag_tasks)]
   
   global output_directory
   output_directory = data_output_directory
   
   #create the output directory if it's not found. 
   os.makedirs(output_directory, exist_ok = True)
   
   global files_list 
   files_list = Utils.get_images_list(images_folder)
   
   global N 
   N = grid_dim
   
   global seed
   seed = samples_seed
   
   global username
   username = ""
   
   global utils 
   
   utils = Utils(dictionary_path)

   app.run(debug = True)
   
if __name__ == '__main__':

   fire.Fire(image_tagging_tool_cli)