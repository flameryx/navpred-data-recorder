import os
from numpy import empty
import pandas as pd
import glob
import warnings
import pathlib as pl
from argparse import ArgumentParser
import yaml
from yaml.loader import SafeLoader
import math

class Transformation:

    def readData(args):
        
        map_path = args.map_path
        
        for simulation in os.listdir(map_path):
            
            simulation_path = "{}/{}".format(map_path,simulation)

            obstacleData = Transformation.readObstalceData(simulation_path)
            Transformation.readRobotData(simulation_path)
            print(obstacleData)


 
    def readObstalceData(simulation_path):
            
            sum_linear_vel = 0
            obstacle_counter = 0
            sum_obstacle_size = 0

            # read every obstacle and calculate the average linear velocity and average size of the obstacles

            obstacles_path = "{}/obstacles".format(simulation_path)
            
            for obstacle in os.listdir(obstacles_path):

                obstacle_path = "{}/{}".format(obstacles_path, obstacle)
                
                with open('{}/params.yaml'.format(obstacle_path)) as f:
                    obstalce_parameters = yaml.load(f, Loader=SafeLoader)
                
                sum_linear_vel  = sum_linear_vel + obstalce_parameters["linear_vel"]
                sum_obstacle_size = sum_obstacle_size + obstalce_parameters["radius"]
                obstacle_counter = obstacle_counter + 1 

            average_linear_vel = sum_linear_vel / obstacle_counter
            average_obstalce_size = sum_obstacle_size / obstacle_counter
            columns = {
                'average_linear_vel': [average_linear_vel],
                'average_obstalce_size': [average_obstalce_size],
                'number_dynamic_obstalces':[obstacle_counter]
                }

            return pd.DataFrame(data = columns)

    def readRobotData(simulation_path):
        robots_path = "{}/robots".format(simulation_path)
        
        for robot in os.listdir(robots_path):
            robot_path = "{}/{}".format(robots_path, robot)
            
            with open('{}/params.yaml'.format(robot_path)) as f:
                robot_parameters = yaml.load(f, Loader=SafeLoader)
            local_planner = robot_parameters["local_planner"]
            robot_model = robot_parameters["model"]
            
            metrics = pd.read_csv("{}/metrics.csv".format(robot_path))
            
            average_path_length = metrics["path_length"].mean()
            
            episode_counter = 0
            count_if_collision = 0
            success_counter = 0
            timeout_couner = 0
            
            for ind in metrics.index:
                episode_counter = episode_counter + 1
                if metrics["collision_amount"][ind] != 0:
                    count_if_collision = count_if_collision + 1
                elif metrics["result"][ind] == "GOAL_REACHER":
                        success_counter = success_counter + 1
                elif metrics["result"][ind] == "TIMEOUT":
                        timeout_couner = timeout_couner + 1
                else:
                    print("Something went wrong here. Not identified result")
            
            success_rate = success_counter / episode_counter
            collisiron_rate = count_if_collision / episode_counter
            timeout_rate = timeout_couner / episode_counter

            columns = {
                'local_planner': [local_planner],
                'robot_model':[robot_model],
                'success_rate': [success_rate],
                'collisiron_rate': [collisiron_rate],
                'timeout_rate':[timeout_rate],
                'average_path_length':[average_path_length]
            }

            return pd.DataFrame(data = columns)


# episode_duration, success_rate, collision_rate, robot_radius, robot_max_speed, number_dynamic_obs, planner, map, world complexity metrics, 
# numIterations, map type, robot_model, map_res, 
# indoor: corridor_width, iterations
# outdoor: numObstacles, size of obstacles    

       

    
if __name__ == "__main__":
        
    parser = ArgumentParser()
        
    parser.add_argument(
        "--map_path",
        action="store",
        dest="map_path",
        help="path to the map",
        required=True,
    )

    args = parser.parse_args()

    Transformation.readData(args)

