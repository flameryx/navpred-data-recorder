import rospy
import os 
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from constants import Constants


class ObstacleNavPredManager:
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
            
    def reset_navpred(self, forbidden_zones=[]):
        dynamic_obstacles = rospy.get_param("/obstacles/num_dynamic")
        static_obstacles = rospy.get_param("/obstacles/num_static")
        max_radius = rospy.get_param("/obstacles/max_radius")
        obs_initialized = rospy.get_param("/obstacles/initialized")
        
        self.environment.remove_all_obstacles()
        
        for i in range(dynamic_obstacles):
            obstacle_name = "obs_" + str(i)
            
            position = self.map_manager.get_random_pos_on_map(
                safe_dist=max_radius, 
                forbidden_zones=forbidden_zones
            )
            
            if not obs_initialized:
                self.environment.init_random_dynamic_obstacle(position=position, obstacle_name=obstacle_name)
            else:
                self.environment.respawn_obstacle(position=position, obstacle_name=obstacle_name, is_dynamic=True)
            
        for i in range(static_obstacles):
            obstacle_name = "obs_" + str(i)
            
            position = self.map_manager.get_random_pos_on_map(
                safe_dist=max_radius, 
                forbidden_zones=forbidden_zones
            )
            
            if not obs_initialized:
                self.environment.init_random_static_obstacle(position=position, obstacle_name=obstacle_name)
            else:
                self.environment.respawn_obstacle(position=position, obstacle_name=obstacle_name, is_dynamic=False)
                
        rospy.set_param("/obstacles/initialized", True)