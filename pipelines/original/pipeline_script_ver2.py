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
import pandas as pd


# Create and parse cli arguments #------------------

parser = ArgumentParser()
parser.add_argument(
    "--num_maps",
    action="store",
    dest="num_maps",
    default=10,
    help="How many maps do you want to create?",
    required=False,
)

parser.add_argument(
    "--num_episodes",
    action="store",
    dest="num_episodes",
    default=30,
    help="How many episodes do you want to run on each simulation?",
    required=False,
)

parser.add_argument(
    "--planners",
    action="store",
    dest="planners",
    default="dwa,aio,teb,crowdnav,rlca",
    help="What planners do you want to use on your simulation?",
    required=False,
)

parser.add_argument(
    "--robots",
    action="store",
    dest="robots",
    default="burger,agvota,dingo,jackal,ridgeback",
    help="What robots do you want to use on your simulations?",
    required=False,
)

parser.add_argument(
    "--num_dyn_obs",
    action="store",
    dest="num_dyn_obs",
    default="0,2,4,6",
    help="How many dynamic obstacles do you want to be present on the simulation?",
    required=False,
)

parser.add_argument(
    "--obs_max_vel",
    action="store",
    dest="obs_max_vel",
    default=1.0,
    help="What should be the maximum velocity of the dynamic obstacles?",
    required=False,
)

parser.add_argument(
    "--obs_min_vel",
    action="store",
    dest="obs_min_vel",
    default=0.1,
    help="What should be the minimum velocity of the dynamic obstacles?",
    required=False,
)

parser.add_argument(
    "--obs_max_radius",
    action="store",
    dest="obs_max_radius",
    default=1.0,
    help="What should be the maximum radius of the dynamic obstacles?",
    required=False,
)

parser.add_argument(
    "--obs_min_radius",
    action="store",
    dest="obs_min_radius",
    default=0.1,
    help="What should be the minimum radius of the dynamic obstacles?",
    required=False,
)

parser.add_argument(
    "--timeout",
    action="store",
    dest="timeout",
    default=30,
    help="After how many seconds should the episode timeout?",
    required=False,
)

parser.add_argument(
    "--map_types",
    action="store",
    dest="map_types",
    default="indoor,outdoor",
    help="On what type of maps do you want to record simulation data?",
    required=False,
)

parser.add_argument(
    "--viz",
    action="store",
    dest="viz",
    default="flatland",
    help="How do you want to see the simulations? [flatland, rviz, none]",
    required=False,
)

parser.add_argument(
    "--del_records",
    action="store",
    dest="del_records",
    default=False,
    help="Do you want to delete all recorded data before starting the pipeline?",
    required=False,
)


args = parser.parse_args()

planners = [item for item in args.planners.replace(" ", "").split(',')]
robots = [item for item in args.robots.replace(" ", "").split(',')]
map_types = [item for item in args.map_types.replace(" ", "").split(',')]
number_dyn_obs = [int(item) for item in args.num_dyn_obs.replace(" ", "").split(',')]
num_maps = int(args.num_maps)
num_episodes = int(args.num_episodes)
maps_path = "maps"
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
    
    width = random.choice([50,70,90])
    height = random.choice([50,70,90])
        
    map_name = "map-" + str(uuid())    
    map_type = random.choice(map_types)
    num_maps_to_generate = 1
    map_res = 0.5
    iterations = random.choice([15,30,45,70]) 
    num_obstacles = random.choice([0,10,20,30,40]) 
    obstacle_size = random.choice([2,4,6])
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
    
    # Working robots: ["burger", "cob4", "agvota", "dingo", "jackal", "ridgeback", "rto", "tiago", "waffle", "youbot"]

    planner = random.choice(planners)
    robot = random.choice(robots)    
    dyn_obs_velocity = (args.obs_min_vel, args.obs_max_vel)
    obs_radius = (args.obs_min_radius, args.obs_max_radius)
    num_dyn_obs = random.choice(number_dyn_obs)

    sim_id = "sim-" + str(uuid())
    roslaunch_command = f"""roslaunch navpred-data-recorder start_arena_navpred.launch map_file:={map_name} num_episodes:={num_episodes} num_dynamic:={num_dyn_obs} obs_max_radius:={obs_radius[1]} obs_min_radius:={obs_radius[0]} obs_max_lin_vel:={dyn_obs_velocity[1]} obs_min_lin_vel:={dyn_obs_velocity[0]} model:={robot} local_planner:={planner} sim_id:={sim_id} timeout:={timeout} update_rate:={update_rate} visualization:={viz}"""
    os.system(roslaunch_command)
    
        
    # Check number of episodes -----------------------------             
    sim_finished = True
    sim_dir = os.path.join(local_records, map_name, sim_id)
    
    episodes_path = os.path.join(sim_dir, "episode.csv")
    
    if os.path.isfile(episodes_path):
        episodes_csv = read_csv(os.path.join(sim_dir, "episode.csv"))
        episodes = episodes_csv["episode"].tolist()
        
        max_miss_count = 3
        miss_counter = 0
        
        for ep_num in range(0, num_episodes):
            if ep_num not in episodes:
                miss_counter += 1
            if miss_counter > max_miss_count:
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
    
    robots_path = os.path.join(sim_dir, "robots")
    
    # Delete all lines with NaN values in the recorded csv files
    try:
        for robot in os.listdir(robots_path):
            odom = pd.read_csv(os.path.join(robots_path, robot, "odom.csv"))
            cmd_vel = pd.read_csv(os.path.join(robots_path, robot, "cmd_vel.csv"))
            scan = pd.read_csv(os.path.join(robots_path, robot, "scan.csv"))

            odom_del_times = odom.loc[odom["data"].isnull()]["time"].tolist()

            for time in odom_del_times:
                odom.drop(odom.loc[odom["time"] == time].index, inplace=True)
                cmd_vel.drop(cmd_vel.loc[cmd_vel["time"] == time].index, inplace=True)
                scan.drop(scan.loc[scan["time"] == time].index, inplace=True)

            cmd_vel_del_times = cmd_vel.loc[cmd_vel["data"].isnull()]["time"].tolist()

            for time in cmd_vel_del_times:
                odom.drop(odom.loc[odom["time"] == time].index, inplace=True)
                cmd_vel.drop(cmd_vel.loc[cmd_vel["time"] == time].index, inplace=True)
                scan.drop(scan.loc[scan["time"] == time].index, inplace=True)
                
            scan_del_times = scan.loc[scan["data"].isnull()]["time"].tolist()

            for time in scan_del_times:
                odom.drop(odom.loc[odom["time"] == time].index, inplace=True)
                cmd_vel.drop(cmd_vel.loc[cmd_vel["time"] == time].index, inplace=True)
                scan.drop(scan.loc[scan["time"] == time].index, inplace=True)
                
            odom.to_csv(os.path.join(robots_path, robot, "odom.csv"), index=False)
            cmd_vel.to_csv(os.path.join(robots_path, robot, "cmd_vel.csv"), index=False)
            scan.to_csv(os.path.join(robots_path, robot, "scan.csv"), index=False)
    except:
        with open("failed_records.txt", 'a') as f:
            f.write(f'missing files,{map_name},{sim_id}\n')
        continue
    
    # Run get_metrics.py -----------------------------------
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
        
    