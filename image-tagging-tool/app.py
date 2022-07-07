import json
from flask import Flask, render_template, send_from_directory, url_for, request
from utils import Utils
from flask_cors import CORS
import os 
from urllib.parse import unquote
import fire 

#FIXME -> should set the folder to the images folder the user has set in the command line. 
app = Flask(__name__, template_folder='templates')
CORS(app)

#global variables their values should be passed by the user in the cli.  
images_folder = "" 
files_list = [] 
N = 4 
seed = None 
   
   
#index of the web app. 
@app.route('/', methods = ['GET'])
def index(): 
    """TODO docs 
    """
    #should send an initial sample.    
    return render_template('index.html', images = Utils.get_random_sample(files_list , N * N), labels = tags, username = username)

#get random images urls to be sampled.

@app.route('/taggingTool/api/getImages/<path:filename>')
def get_images(filename): 
   """TODO method docs.    
   """
   return send_from_directory(images_folder, unquote(filename), as_attachment=True)

@app.route('/taggingTool/api/labelImages' , methods = ["POST"])
def label_images():
   """TODO 
   """

   #open and compute the hash of the images. 
   images_metadata = [Utils.image_metadata(images_folder, unquote(os.path.join(images_folder, os.path.basename(image_path))), 'sha256', request.json['username'], request.json['label']) for image_path in request.json['images']]
   
   #store the images metadata and labels sent by user inside json file. 
   labeled_images = {} 
   
   #if the json file storing the labels is not found then create it. 
   if not os.path.isfile('./labeled_images.json'): 
      json.dump(labeled_images, open('./labeled_images.json', 'w'), indent = 4)
   
   try: 
      
      with open('./labeled_images.json', "r") as labels_file: 
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
   
   with open("./labeled_images.json", "w") as labels_file: 
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
   return render_template('index.html', images = Utils.get_random_sample(files_list, N * N), labels = tags, username = username)



def image_tagging_tool_cli(images_dataset_directory: str, labels: list, grid_dim: int = 4, samples_seed: int = None) -> None: 
   """TODO docs. 
   """
   global images_folder 
   images_folder = images_dataset_directory
   
   global tags
   tags = [{'id': index, 'name': label} for index, label in enumerate(labels)]
   
   global files_list 
   files_list = Utils.get_files_list(images_folder)
   
   global N 
   N = grid_dim
   
   global seed
   seed = samples_seed
   
   global username
   username = ""
   
   app.run(debug = True)
   
if __name__ == '__main__':

   fire.Fire(image_tagging_tool_cli)