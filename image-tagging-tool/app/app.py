from flask import Flask, render_template, url_for, request
from utils import Utils


#FIXME -> should set the folder to the images folder the user has set in the command line. 
app = Flask(__name__, static_folder="static")

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
    return render_template('index.html', images = Utils.get_random_sample(files_list , N * N))

#get random images urls to be sampled.

@app.route('/taggingTool/api/labelImages' , methods = ["POST"])
def get_images():
   """TODO 
   """
   #open and compute the hash of the images. 
   images_metadata = [Utils.image_metadata(image['path'], 'sha256') for image in request.json()['images']]
   
   #store the images metadata and labels sent by user inside json file. 
   
   #remove the labeled images from the files list. 
   for image in request.json()['image']: 
      if image['path'] in files_list: 
         files_list.remove(image['path'])
   
   #return a new list of images to the user to label. 
   return render_template('index.html', images = Utils.get_random_sample(files_list, N * N))



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
   
   app.run(debug = True)
   
if __name__ == '__main__':

   image_tagging_tool_cli("C:/Users/MahmoudSaudi/Documents/KCG/repo/image-tools/image-tagging-tool/app/static")
