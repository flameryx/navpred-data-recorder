import os
from numpy import empty
import pandas as pd
import pathlib as pl
from argparse import ArgumentParser
import yaml
from yaml.loader import SafeLoader

class Transformation:

    @staticmethod
    def readData(record_path,map_path):
        print("gathering data")
        for simulation in os.listdir(record_path):
            
            simulation_path = "{}/{}".format(record_path,simulation)

            # calculate obstacle data    
            obstacle_data = Transformation.readObstalceData(simulation_path)
            # calculate robot data
            robot_data = Transformation.readRobotData(simulation_path)
            # calculate map data
            map_data = Transformation.readMapData(map_path)

            output_data_frame = pd.concat([robot_data,map_data,obstacle_data],axis=1, join='inner')
            
            # output as .csv
            csvFilename = "dnn_input_data/CombinedAverages.csv"
            with open(csvFilename, 'a') as f:
                output_data_frame.to_csv(f, mode='a', header=f.tell()==0, index=False)

            #Output as .yaml
            Transformation.createYAML(output_data_frame)

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

            if(obstacle_counter != 0):
                average_linear_vel = sum_linear_vel / obstacle_counter
                average_obstalce_size = sum_obstacle_size / obstacle_counter
            else:
                average_linear_vel = 0
                average_obstalce_size = 0

            columns = {
                'average_linear_velocity': [str(round(average_linear_vel, 2))],
                'average_obstalce_size': [str(round(average_obstalce_size, 2))],
                'number_dynamic_obstalces':[str(round(obstacle_counter, 2))]
                }

            return pd.DataFrame(data = columns)

#------------------------------------------def readRobotData----------------------------------------------------------

    def readRobotData(simulation_path):
        robots_path = "{}/robots".format(simulation_path)
        
        for robot in os.listdir(robots_path):
            robot_path = "{}/{}".format(robots_path, robot)
            
            # calculate metrics from params.yaml

            robot_model=""

            with open('{}/params.yaml'.format(robot_path)) as f:
                robot_parameters = yaml.load(f, Loader=SafeLoader)
            local_planner = robot_parameters["local_planner"]
            robot_model = robot_parameters["model"]
            
            #calculate metrics from metrics.csv
            
            metrics = pd.read_csv("{}/metrics.csv".format(robot_path))
            average_time_diff = metrics["time_diff"].mean()
            average_path_length = metrics["path_length"].mean()
            
            episode_counter = 0
            count_if_collision = 0
            success_counter = 0
            timeout_couner = 0

            for ind in metrics.index:
                episode_counter = episode_counter + 1
                if metrics["collision_amount"][ind] != 0:
                    count_if_collision = count_if_collision + 1
                elif metrics["result"][ind] == "GOAL_REACHED":
                        success_counter = success_counter + 1
                elif metrics["result"][ind] == "TIMEOUT":
                        timeout_couner = timeout_couner + 1
                else:
                    print("Something went wrong here. Not identified result")
            
            if(episode_counter != 0):
                success_rate = success_counter / episode_counter
                collisiron_rate = count_if_collision / episode_counter
                timeout_rate = timeout_couner / episode_counter
            else:
                success_rate = 0
                collisiron_rate = 0
                timeout_rate = 0

            #calculate metrics from robot directory

            robot_dir_path = "{}/../../../../../../arena-simulation-setup/robot/{}".format(simulation_path,robot_model)
            
            with open('{}/model_params.yaml'.format(robot_dir_path)) as f:
                model_params = yaml.load(f, Loader=SafeLoader)
            
            robot_max_speed = max(model_params["actions"]["continuous"]["linear_range"])
            robot_radius = model_params["robot_radius"]

            columns = {
                'local_planner': [local_planner],
                'robot_model':[robot_model],
                'robot_max_speed' :[robot_max_speed],
                'robot_radius':[robot_radius],
                'success_rate': [str(round(success_rate, 2))],
                'collisiron_rate': [str(round(collisiron_rate, 2))],
                'timeout_rate':[str(round(timeout_rate, 2))],
                'average_path_length':[str(round(average_path_length, 2))],
                'average_time_diff':[str(round(average_time_diff, 2))]   
            }

            return pd.DataFrame(data = columns)

#------------------------------------------readMapData---------------------------------------------------

    def readMapData(map_path):
        
        with open('{}/generation_params.yaml'.format(map_path)) as f:
            generation_params = yaml.load(f, Loader=SafeLoader)

        map_type = generation_params["map_type"]
        
        indoor_map_type = False
        iterations = 0
        corridor_width = 0

        outdoor_map_type = False
        num_obstacles = 0
        obstacle_size = 0

        other_map_type = False

        if map_type == "indoor":
            indoor_map_type = True
            iterations = generation_params["iterations"]
            corridor_width = generation_params["corridor_width"]
        elif map_type == "outdoor":
            outdoor_map_type = True
            num_obstacles = generation_params["num_obstacles"]
            obstacle_size = generation_params["obstacle_size"]
        else:
            other_map_type = False

        # image data
    
        with open('{}/map.yaml'.format(map_path)) as f:
            map = yaml.load(f, Loader=SafeLoader)

        # map complexity data
        with open('{}/complexity.yaml'.format(map_path)) as f:
            complexity = yaml.load(f, Loader=SafeLoader)

        

        columns = {
            'image':[map["image"]],

            'width': [generation_params["width"]],
            'height':[generation_params["height"]],
            
            'indoor_map_type':[indoor_map_type],
            'iterations':[iterations],
            'corridor_width':[corridor_width],
            
            'outdoor_map_type':[outdoor_map_type],
            'num_static_obstacles':[num_obstacles],
            'static_obstacle_size':[obstacle_size],
            
            'other_map_type':[other_map_type],

            "mean_angle_info": [str(round(complexity["AngleInfo"]["mean"], 4))],
            "entropy":[str(round(complexity["Entropy"], 4))],
            "map_size": [complexity["MapSize"]],
            "max_entropy": [str(round(complexity["MaxEntropy"], 4))],
            "num_obs_cv2":[complexity["NumObs_Cv2"]],
            "occupancy_ratio": [str(round(complexity["OccupancyRatio"], 4))],
            "distance_normalized": [str(round(complexity["distance(normalized)"], 4))],
            "distance_avg": [str(round(complexity["distance.avg"], 4))],
            "distance_variance":[str(round(complexity["distance.variance"], 4))] 
        }

        return pd.DataFrame(data = columns)
        
    def createYAML(data):

        for idx, row in data.iterrows():
            
            robot_metrics = dict(
                local_planner = row.loc["local_planner"],
                robot_model = row.loc["robot_model"],
                robot_max_speed = row.loc["robot_max_speed"],
                robot_radius = row.loc["robot_radius"]
            )

            performance_metrics = dict(
                success_rate = row.loc["success_rate"],
                collisiron_rate = row.loc["collisiron_rate"],
                timeout_rate = row.loc["timeout_rate"],
                average_path_length = row.loc["average_path_length"],
                average_time_diff = row.loc["average_time_diff"]

            )

            map_metrics = dict(
                image = row.loc["image"],
                width = row.loc["width"],
                height = row.loc["height"],
                indoor_map_type = row.loc["indoor_map_type"],
                iterations = row.loc["iterations"],
                corridor_width = row.loc["corridor_width"],
                outdoor_map_type = row.loc["outdoor_map_type"],
                average_linear_velocity = row.loc["average_linear_velocity"],
                average_obstalce_size = row.loc["average_obstalce_size"],
                number_dynamic_obstalces = row.loc["number_dynamic_obstalces"],
                num_static_obstacles = row.loc["num_static_obstacles"],
                static_obstacle_size = row.loc["static_obstacle_size"],
                other_map_type = row.loc["other_map_type"],
                mean_angle_info = row.loc["mean_angle_info"],
                entropy = row.loc["entropy"],
                map_size = row.loc["map_size"],
                num_obs_cv2 = row.loc["num_obs_cv2"],
                occupancy_ratio = row.loc["occupancy_ratio"],
                distance_normalized = row.loc["distance_normalized"],
                distance_avg = row.loc["distance_avg"],
                distance_variance = row.loc["distance_variance"]
            )
            mapName =row.loc["image"]
            mapName = mapName.replace('.png', '')
            path = pl.Path("dnn_input_data/{}".format(mapName))
            path.mkdir(parents=True, exist_ok=True)

            imageSource = "maps/{}/{}.png".format(mapName,mapName)

            imageDestination = 'dnn_input_data/{}/{}'.format(mapName,mapName)

            os.system("cp {} {}".format(imageSource,imageDestination))

            with open('dnn_input_data/{}/{}_robot_metrics.yml'.format(mapName,mapName), 'w') as outfile:
                yaml.dump(robot_metrics, outfile, default_flow_style=False)

            with open('dnn_input_data/{}/{}_performance_metrics.yml'.format(mapName,mapName), 'w') as outfile:
                yaml.dump(performance_metrics, outfile, default_flow_style=False)

            with open('dnn_input_data/{}/{}_map_metrics.yml'.format(mapName,mapName), 'w') as outfile:
                yaml.dump(map_metrics, outfile, default_flow_style=False)

if __name__ == "__main__":
        
    parser = ArgumentParser()
        
    parser.add_argument(
        "--record_path",
        action="store",
        dest="record_path",
        help="path to the recordings",
        required=True,
    )

    parser.add_argument(
        "--map_path",
        action="store",
        dest="map_path",
        help="path to the map",
        required=True,
    )

    args = parser.parse_args()
    
    record_path = args.record_path
    map_path = args.map_path

    Transformation.readData(record_path,map_path)

