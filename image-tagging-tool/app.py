import json
from flask import Flask, render_template, url_for, request
from utils import Utils
from flask_cors import CORS
import os 
from urllib.parse import unquote

#FIXME -> should set the folder to the images folder the user has set in the command line. 
app = Flask(__name__, static_folder="static")
CORS(app)

#global variables their values should be passed by the user in the cli.  
images_folder = "" 
files_list = [] 
N = 4 
seed = None 

# def get_images_sample(sample_size: int = 16, seed: int = None) -> list[str]: 
#    """TODO docs 
#    """
#    return Utils.get_random_sample(files_list, sample_size, seed)
   
   
#index of the web app. 
@app.route('/', methods = ['GET'])
def index(): 
    """TODO docs 
    """
    #should send an initial sample.    
    return render_template('index.html', images = Utils.get_random_sample(files_list , N * N), labels = [{'id': 0, 'name': 'good'}, {'id': 1, 'name': 'bad'}], username = username)

#get random images urls to be sampled.

@app.route('/taggingTool/api/labelImages' , methods = ["POST"])
def get_images():
   """TODO 
   """

   #open and compute the hash of the images. 
   print(request.json)
   print(os.path.join(images_folder, os.path.basename(request.json['images'][0])))
   images_metadata = [Utils.image_metadata(unquote(os.path.join(images_folder, os.path.basename(image_path))), 'sha256', request.json['username'], request.json['label']) for image_path in request.json['images']]
   
   #store the images metadata and labels sent by user inside json file. 
   labeled_images = images_metadata 
   
   try: 
      with open('./labeled_images.json', "r") as labels_file: 
         labeled_images = json.load(labels_file)
         labeled_images.extend(images_metadata)
   except Exception as ex:   
      print(ex)    
      pass  
   
   with open("./labeled_images.json", "w") as labels_files: 
      json.dump(labeled_images, labels_files, indent = 4)

   #remove the labeled images from the files list. 
   print(files_list)
   for image in request.json['images']: 
      #Make the path in the same format of paths in files_list variable. 
      image_path = {'url': unquote(os.path.basename(image))}
      #if the image path in the files_list remove it as it's already labeled (it should always be found)
      if image_path in files_list: 
         files_list.remove(image_path)
   
   #Change the global username to the new one. 
   username = request.json['username']
   
   #return a new list of images to the user to label. 
   return render_template('index.html', images = Utils.get_random_sample(files_list, N * N), labels = [{'id': 0, 'name': 'good'}, {'id': 1, 'name': 'bad'}], username = username)



def image_tagging_tool_cli(images_directory: str, grid_dim: int = 4, samples_seed: int = None) -> None: 
   """TODO docs. 
   """
   global images_folder 
   images_folder = images_directory
   
   global files_list 
   files_list = Utils.get_files_list(images_folder)
   
   global N 
   N = grid_dim
   
   global seed
   seed = samples_seed
   
   global username
   username = "Mahmoud"
   
   app.run(debug = True)
   
if __name__ == '__main__':

   image_tagging_tool_cli("C:/Users/MahmoudSaudi/Documents/KCG/repo/image-tools/image-tagging-tool/app/static")
