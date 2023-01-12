'''
@author Ricardo Sosa Melo
'''
import os
from pathlib import Path
from argparse import ArgumentParser
from random import randint

# Create and parse cli arguments #------------------

parser = ArgumentParser()

parser.add_argument(
    "--dataset",
    action="store",
    dest="dataset",
    default="dataset",
    help="How many maps do you want to create",
    required=False,
)

parser.add_argument(
    "--trained_model",
    action="store",
    dest="trained_model",
    default="trained_model.h5",
    help="How many maps do you want to create",
    required=False,
)

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
    default="../../../arena-rosnav/simulator_setup/maps",
    help="The path where the maps are stored.",
    required=False,
)

parser.add_argument(
    "--records_path",
    action="store",
    dest="records_path",
    default="../../arena-evaluation/01_recording/recordings",
    help="The path where the recordings of the simulations ran on the maps are stored.",
    required=False,
)


args = parser.parse_args()

num_maps = int(args.num_maps)
num_settings = int(args.num_settings)
maps_path = args.maps_path
records_path = args.records_path
dataset = args.dataset
trained_model = args.trained_model

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

unfiltered_maps = Path(dirname) / "unfiltered_maps"
unfiltered_maps.mkdir(parents=True, exist_ok=True)

filtered_maps = Path(dirname) / "filtered_maps"
filtered_maps.mkdir(parents=True, exist_ok=True)

#---------------------------------------------------
# Pipeline #-----------------------------------

# Generate maps #-----------------------------------------
os.system(f"python3 gan.py --image_path {dataset} --output_path unfiltered_maps --map_num {num_maps} --trained_model {trained_model}")
os.system(f"python3 filter.py --image_path unfiltered_maps --output_path filtered_maps")
os.system(f"rm -rf unfiltered_maps")
os.system(f"python3 create_yaml.py --image_path filtered_maps")

map_names = os.listdir("filtered_maps")

os.system(f"mv -v filtered_maps/* {maps_path}")
os.system(f"rm -rf filtered_maps")
#---------------------------------------------------------

for map_name in map_names:
        
    #---------------------------------------------------------
    # Run simulations and record data #-----------------------

    local_planners = ["dwa"]
    robot_models = ["burger"]    
    dyn_obs_velocity = (0.1, 0.5)
    dyn_obs_radius = (0.2, 0.5)
    static_obs_vertices = (3, 8)
    obstacles_settings = []
    
    for j in range(num_settings):
        obstacles_settings.append((randint(0, 15), randint(0, 15)))
    
    for planner in local_planners:
        for robot in robot_models:
            for sett in obstacles_settings:
                num_dyn_obs = sett[0]
                num_static_obs = sett[1]
                roslaunch_command = f""" roslaunch arena_bringup start_arena_flatland.launch model:={robot} num_dynamic_obs:={num_dyn_obs} num_static_obs:={num_static_obs} min_dyn_vel:={dyn_obs_velocity[0]} max_dyn_vel:={dyn_obs_velocity[1]} min_dyn_radius:={dyn_obs_radius[0]} max_dyn_radius:={dyn_obs_radius[1]} min_static_num_vertices:={static_obs_vertices[0]} max_static_num_vertices:={static_obs_vertices[1]} local_planner:={planner} map_file:={map_name} task_mode:="project_eval" scenario_file:="project_eval/scenario_1.json" use_recorder:="true" show_rviz:="true" use_rviz:="true" """
                os.system(roslaunch_command)


    # Copy new generated map to local maps folder
    os.system(f"mv {maps_path}/{map_name} maps")
    
    # Copy recorded data for the new map to local sims_data_records folder
    os.system(f"mv {records_path}/{map_name} sims_data_records")
        
    #---------------------------------------------------------
    # Data cleaning, analysis and map complexity calculation #
    os.system("python3 createAverage.py --csv_name /{}/{}*.csv".format(map_name,map_name))
    
    #----------------------------------------------------------
