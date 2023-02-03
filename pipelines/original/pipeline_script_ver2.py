'''
@author Ricardo Sosa Melo
'''
import os
import shutil
import glob
from uuid import uuid4 as uuid
from pathlib import Path
from argparse import ArgumentParser
import random
import cv2
from data_preparation_script import Transformation   
from pandas import read_csv


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
    "--timeout",
    action="store",
    dest="timeout",
    default=30,
    help="After how many seconds should the episode timeout.",
    required=False,
)

parser.add_argument(
    "--num_episodes",
    action="store",
    dest="num_episodes",
    default=30,
    help="How many episodes do you want to run on each simulation",
    required=False,
)

parser.add_argument(
    "--viz",
    action="store",
    dest="viz",
    default="flatland",
    help="How do you want to see the simulations? [flatland, rivz, none]",
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

parser.add_argument(
    "--del_records",
    action="store",
    dest="del_records",
    default=False,
    help="Do you want to delete all recorded data before starting the pipeline",
    required=False,
)


args = parser.parse_args()

num_maps = int(args.num_maps)
num_settings = int(args.num_settings)
num_episodes = int(args.num_episodes)
maps_path = args.maps_path
records_path = args.records_path
del_records = bool(args.del_records)
viz = args.viz

# Changing the update_rate also reduces the real time timeout.
# The simulation time scales linearly with the update rate. 
# The maximal update rate one can set to increase the speed of the simulation, is dependent on the hardware setup
# At some point the CPU becomes a bottle neck, and increasing the update_rate further would have no effect
speed_multiplier = 20
update_rate = 10 * speed_multiplier
timeout = int(args.timeout) * speed_multiplier
    
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
# Delete recorded data and their folders#-----------
print(str(local_maps.resolve()))
if del_records:
    shutil.rmtree(str(local_maps.resolve()))
        
    shutil.rmtree(str(local_records.resolve()))

    shutil.rmtree(str(dnn_input.resolve()))
    
#--------------------------------------------------
# Recreate deleted folders #-----------------------
local_maps.mkdir(parents=True, exist_ok=True)
local_records.mkdir(parents=True, exist_ok=True)
dnn_input.mkdir(parents=True, exist_ok=True)


#---------------------------------------------------
# Pipeline loop #-----------------------------------

for i in range(num_maps):
    
    # Generate maps #-----------------------------------------

    mapSize = random.choice([50,70,90])

    if mapSize == 50:
        num_dyn_obs = random.choice([0,2,4,6])

    if mapSize == 70:
        num_dyn_obs = random.choice([0,3,6,9])

    if mapSize == 90:
        num_dyn_obs = random.choice([0,4,8,12])
        
    map_name = "map-" + str(uuid())    
    width = mapSize
    height = mapSize
    map_type = "indoor"
    num_maps_to_generate = 1
    map_res = 0.5
    iterations = random.choice([15,30,45,70]) 
    num_obstacles = 45
    obstacle_size = 10
    corridor_width = random.choice([3,4,5])

    generate_maps_command = f"python3 cliMapGenerator.py --map_name {map_name} --width {width} --height {height} --map_type {map_type} --num_maps {num_maps_to_generate} --map_res {map_res} --save_path {maps_path} --iterations {iterations} --num_obstacles {num_obstacles} --obstacle_size {obstacle_size} --corridor_width {corridor_width}"
    os.system(generate_maps_command)
    
    this_map_folder = f"{maps_path}/{map_name}"
                       
    get_complexity_command = f"python3 world_complexity.py --image_path {this_map_folder}/{map_name}.png --yaml_path {this_map_folder}/map.yaml --dest_path {this_map_folder}"
    os.system(get_complexity_command)
    
    # Add map generation parameters to map folder ------------
    f = open(os.path.join(local_maps, map_name, "generation_params.yaml"), "w")
        
    if map_type == "indoor":
        f.write("width: " + str(width) + "\n" +
                "height: " + str(height) + "\n" +
                "map_type: " + map_type + "\n" +
                "map_res: " + str(map_res) + "\n" +
                "iterations: " + str(iterations) + "\n" +
                "corridor_width: " + str(corridor_width))
    elif map_type == "outdoor":
        f.write("width: " + str(width) + "\n" +
                "height: " + str(height) + "\n" +
                "map_type: " + map_type + "\n" +
                "map_res: " + str(map_res) + "\n" +
                "num_obstacles: " + str(num_obstacles) + "\n" +
                "obstacle_size: " + str(obstacle_size))
    f.close()
    

    #---------------------------------------------------------
    # Run simulations and record data #-----------------------
    os.mkdir(os.path.join(local_records, map_name))
    
    # Working planners: ["dwa", "aio", "teb", "crowdnav", "rlca"]
    # Planners with planning issues (dumb planners) : ["mpc", "arena", "sarl"]
    # Not working: ["cadrl", "rosnav"]
    
    # Alex: ["dwa", "rlca", "crowdnav"]
    # Bassel: ["dwa", "aio", "teb", "crowdnav", "rlca"] 
    # Ricardo: ["dwa", "aio", "teb", "crowdnav", "rlca"]
    # Bo: pending...

    planner = random.choice(["dwa"])
    robot = random.choice(["burger"])    
    dyn_obs_velocity = (0.1, 1.0)
    obs_radius = (0.1, 1.0)

    sim_id = "sim-" + str(uuid())
    roslaunch_command = f"""roslaunch navpred-data-recorder start_arena_navpred.launch map_file:={map_name} num_episodes:={num_episodes} num_dynamic:={num_dyn_obs} obs_max_radius:={obs_radius[1]} obs_min_radius:={obs_radius[0]} obs_max_lin_vel:={dyn_obs_velocity[1]} obs_min_lin_vel:={dyn_obs_velocity[0]} local_planner:={planner} sim_id:={sim_id} timeout:={timeout} update_rate:={update_rate} visualization:={viz}"""
    os.system(roslaunch_command)
    
        
    # Check number of episodes -----------------------------             
    sim_finished = True
    sim_dir = os.path.join(local_records, map_name, sim_id)
    
    episodes_path = os.path.join(sim_dir, "episode.csv")
    
    if os.path.isfile(episodes_path):
        episodes_csv = read_csv(os.path.join(sim_dir, "episode.csv"))
        episodes = episodes_csv["episode"].tolist()
        
        for ep_num in range(0, 30):
            if ep_num not in episodes:
                sim_finished = False
                break
        
        if not sim_finished:
            with open("failed_records.txt", 'a') as f:
                f.write(f'missing episodes,{map_name},{sim_id}\n')
            continue
    else:
        with open("failed_records.txt", 'a') as f:
            f.write(f'missing files,{map_name},{sim_id}\n')
        continue
    
    get_metrics_command = f"""python3 ../../data-recorder/get_metrics.py --map_name {map_name} --sim_id {sim_id} --timeout {timeout}"""
    os.system(get_metrics_command)
    
    # Error handling get_metrics.py ------------------------
    metrics_created = True
    robots_path = os.path.join(sim_dir, "robots")

    for robot in os.listdir(robots_path):
        metrics_path = os.path.join(robots_path, robot, "metrics.csv")
        
        if not os.path.isfile(metrics_path):
            metrics_created = False
            break
            
    if not metrics_created:
        with open("failed_records.txt", 'a') as f:
            f.write(f'get_metrics.py,{map_name},{sim_id}\n')
        continue
        
    #---------------------------------------------------------
    # Data cleaning, analysis and map complexity calculation #

    try:
        Transformation.readData(
            "sims_data_records/{}".format(map_name), 
            "maps/{}".format(map_name)
        )
    except:
        with open("failed_records.txt", 'a') as f:
            f.write(f'data_preparation_script.py,{map_name},{sim_id}\n')
        continue
    #----------------------------------------------------------

    with open("correct_records.txt", 'a') as f:
        f.write(f'{map_name},{sim_id}\n')
        
    