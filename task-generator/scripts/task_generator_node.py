#! /usr/bin/env python3

import math
import rospy
import time
from nav_msgs.msg import Odometry
from std_msgs.msg import Int16, Bool
from std_srvs.srv import Empty, EmptyRequest, EmptyResponse
from geometry_msgs.msg import PoseStamped
import subprocess
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from task_generator_navpred.utils import Utils
from task_generator_navpred.constants import Constants, TaskMode

# from task_generator_navpred.tasks.random import RandomTask
from task_generator_navpred.tasks.utils import get_predefined_task
from task_generator_navpred.environments.environment_factory import EnvironmentFactory
from task_generator_navpred.environments.gazebo_environment import GazeboEnvironment
from task_generator_navpred.environments.flatland_environment import FlatlandRandomModel
from task_generator_navpred.environments.flatland_navpred_environment import FlatlandNavPredEnvironment

from datetime import datetime


class TaskGenerator:
    """
    Task Generator Node
    Will initialize and reset all tasks. The task to use is read from the `/task_mode` param.
    """

    def __init__(self) -> None:
        ## Params
        self.task_mode = rospy.get_param("/task_mode")
        self.auto_reset = rospy.get_param("~auto_reset", True)
        self.curr_time = rospy.set_param("/start_datetime", datetime.now().strftime("%d-%m-%Y_%H-%M-%S"))

        ## Publishers
        self.pub_scenario_reset = rospy.Publisher("scenario_reset", Int16, queue_size=1)
        self.pub_scenario_finished = rospy.Publisher('scenario_finished', Bool, queue_size=10)
        
        ## Services
        rospy.Service("reset_task", Empty, self.reset_task_srv_callback)

        ## Vars
        self.env_wrapper = EnvironmentFactory.instantiate(Utils.get_environment())("")

        rospy.loginfo(f"Launching task mode: {self.task_mode}")

        self.start_time = rospy.get_time()
        self.task = get_predefined_task("", self.task_mode, self.env_wrapper)
        self.task.set_robot_names_param()

        # self.number_of_resets = 0

        self.srv_start_model_visualization = rospy.ServiceProxy("start_model_visualization", Empty)
        self.srv_start_model_visualization(EmptyRequest())
        
        # self.reset_task()

        self.srv_setup_finished = rospy.ServiceProxy("task_generator_setup_finished", Empty)
        self.srv_setup_finished(EmptyRequest())
        
        rospy.sleep(10)

        self.number_of_resets = 0
        self.reset_task()

        ## Timers
        rospy.Timer(rospy.Duration(0.5), self.check_task_status)


    def check_task_status(self, _):
        if self.task.is_done():
            self.reset_task()

    def reset_task(self):
        self.start_time = rospy.get_time()

        num_episodes = rospy.get_param("num_episodes")
        if self.number_of_resets >= num_episodes:
            self.shutdown_sim()
            return
        
        rospy.loginfo("=============")
        rospy.loginfo("Task Reseted!")
        rospy.loginfo("=============")

        self.env_wrapper.before_reset_task()

        is_end = self.task.reset()

        self.pub_scenario_reset.publish(self.number_of_resets)
        self._send_end_message_on_end(is_end)

        self.env_wrapper.after_reset_task()

        self.number_of_resets += 1
        


            
    def shutdown_sim(self):
        rospy.loginfo("Shutting down. All tasks completed")

        self.pub_scenario_finished.publish(Bool(True))
        rospy.signal_shutdown("Finished all episodes of the current scenario")
        
        subprocess.call(["killall","-9","rosmaster"]) # apt-get install psmisc necessary
        sys.exit()
        

    def reset_task_srv_callback(self, req):
        rospy.logdebug("Task Generator received task-reset request!")

        self.reset_task()

        return EmptyResponse()

    def _send_end_message_on_end(self, is_end):
        if not is_end or self.task_mode != TaskMode.SCENARIO:
            return

        self.shutdown_sim()


if __name__ == "__main__":
    rospy.init_node("task_generator")

    task_generator = TaskGenerator()

    rospy.spin()
