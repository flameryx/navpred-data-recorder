import rospy
import os 
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from constants import Constants


class ObstacleManager:
    def __init__(self, namespace, map_manager, environment):
        self.map_manager = map_manager
        self.namespace = namespace
        self.environment = environment

    def start_scenario(self, scenario):
        self.environment.spawn_pedsim_agents(scenario["obstacles"]["dynamic"])

    def reset_scenario(self, scenario):
        self.environment.reset_pedsim_agents()

        self.environment.remove_all_obstacles()

        for obstacle in scenario["obstacles"]["static"]:
            self.environment.spawn_obstacle(
                [*obstacle["pos"], 0],
                yaml_path=obstacle["yaml_path"],
            )

    def reset_random(
            self, 
            dynamic_obstacles=Constants.ObstacleManager.DYNAMIC_OBSTACLES,
            static_obstacles=Constants.ObstacleManager.STATIC_OBSTACLES,
            forbidden_zones=[]
        ):
        self.environment.remove_all_obstacles()
        
        all_params = rospy.get_param_names()
        
        # Delete all params of last scenario
        for param in all_params:
            if "/obstacles/dynamic/" in param or "/obstacles/static/" in param:
                rospy.delete_param(param)
                
        for i in range(dynamic_obstacles):
            obstacle_name = "obs_" + str(i)
            
            position = self.map_manager.get_random_pos_on_map(
                safe_dist=Constants.ObstacleManager.OBSTACLE_MAX_RADIUS, 
                forbidden_zones=forbidden_zones
            )
            self.environment.spawn_random_dynamic_obstacle(position=position, obstacle_name=obstacle_name)
        
        for i in range(static_obstacles):
            obstacle_name = "obs_" + str(i)
            
            position = self.map_manager.get_random_pos_on_map(
                safe_dist=Constants.ObstacleManager.OBSTACLE_MAX_RADIUS, 
                forbidden_zones=forbidden_zones
            )
            self.environment.spawn_random_static_obstacle(position=position, obstacle_name=obstacle_name)    