'''
@author Ricardo Sosa Melo
'''
import os
import glob
from uuid import uuid4 as uuid
from pathlib import Path
from argparse import ArgumentParser
from random import randint, choice
import cv2

# Create and parse cli arguments #------------------

parser = ArgumentParser()
parser.add_argument(
    "--num_maps",
    action="store",
    dest="num_maps",
    default=10,
    help="How many maps do you want to create",
    required=False,
)

parser.add_argument(
    "--num_settings",
    action="store",
    dest="num_settings",
    default=1,
    help="How many different simulation settings you want to run on each map",
    required=False,
)

parser.add_argument(
    "--maps_path",
    action="store",
    dest="maps_path",
    default="maps",
    help="The path where the maps are stored.",
    required=False,
)

parser.add_argument(
    "--records_path",
    action="store",
    dest="records_path",
    default="../data_recorder/data",
    help="The path where the recordings of the simulations ran on the maps are stored.",
    required=False,
)


args = parser.parse_args()

num_maps = int(args.num_maps)
num_settings = int(args.num_settings)
maps_path = args.maps_path
records_path = args.records_path

#---------------------------------------------------
# Create necessary directories #--------------------

dirname = os.path.dirname(__file__)

# Create local maps folder if it does not exist
local_maps = Path(dirname) / "maps"
local_maps.mkdir(parents=True, exist_ok=True)

# Create local records folder if it does not exist
local_records = Path(dirname) / "sims_data_records"
local_records.mkdir(parents=True, exist_ok=True)

# Create local dnn input data folder if it does not exist
dnn_input = Path(dirname) / "dnn_input_data"
dnn_input.mkdir(parents=True, exist_ok=True)

#---------------------------------------------------
# Pipeline loop #-----------------------------------

for i in range(num_maps):
    
    # Generate maps #-----------------------------------------

    map_name = str(uuid())
    width = randint(80, 150)
    height = randint(80, 150)
    map_type = choice(["indoor", "outdoor"])
    num_maps_to_generate = 1
    map_res = 0.5
    iterations = randint(80, 200)
    num_obstacles = randint(30, 60)
    obstacle_size = 3
    corridor_width = 3

    generate_maps_command = f"python3 cliMapGenerator.py --map_name {map_name} --width {width} --height {height} --map_type {map_type} --num_maps {num_maps_to_generate} --map_res {map_res} --save_path {maps_path} --iterations {iterations} --num_obstacles {num_obstacles} --obstacle_size {obstacle_size} --corridor_width {corridor_width}"
    os.system(generate_maps_command)
    
    #---------------------------------------------------------
    # Add padding to map image to 150x150 pixels #------------
    
    image_path = f"{maps_path}/{map_name}/{map_name}.png"
    img_file = cv2.imread(image_path)
    
    width_padding = 150 - width
    height_padding = 150 - height
    image = cv2.copyMakeBorder(img_file, height_padding, 0, width_padding, 0, cv2.BORDER_CONSTANT)
    
    cv2.imwrite(image_path, image)
    
    #---------------------------------------------------------
    # Run simulations and record data #-----------------------

    local_planners = ["dwa"]
    robot_models = ["burger"]    
    dyn_obs_velocity = (0.1, 0.5)
    dyn_obs_radius = (0.2, 0.8)
    static_obs_vertices = (3, 8)
    obstacles_settings = []
    
    for j in range(num_settings):
        obstacles_settings.append((randint(0, 15), randint(0, 15)))
    
    for planner in local_planners:
        for robot in robot_models:
            for sett in obstacles_settings:
                num_dyn_obs = sett[0]
                num_static_obs = sett[1]
                roslaunch_command = f""" roslaunch navpred-data-recorder start_arena_navpred.launch map_file:={map_name} """
                os.system(roslaunch_command)


    # Copy new generated map to local maps folder
    # os.system(f"mv {maps_path}/{map_name} maps")
    
    # Copy recorded data for the new map to local sims_data_records folder
    # os.system(f"mv {records_path}/{map_name} sims_data_records")
        
    #---------------------------------------------------------
    # Data cleaning, analysis and map complexity calculation #
    # TODO: New createAverage.py script for new recorded data structure
    # os.system("python3 createAverage.py --csv_name /{}/{}*.csv".format(map_name,map_name))
    
    #----------------------------------------------------------
