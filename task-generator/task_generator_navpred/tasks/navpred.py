import random
import rospy

import os
import sys
import inspect


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from constants import Constants, TaskMode
from tasks.task_factory import TaskFactory

from .base_task import BaseTask


@TaskFactory.register(TaskMode.NAVPRED)
# This task is similar to RANDOM, the main difference being that the number of obstacles and 
# their characteristics remain the same after each episode (only their positions and the robot's 
# are randomized). RANDOM on the other hand randomizes everything after each episode.
class NavPredTask(BaseTask):
    """
        The navpred task reuses the dynamic and
        static obstacles created on the first episode but
        spawns them in different positions, and will create 
        a new robot start and goal position for each task.
    """

    def reset(
        self, start=None, goal=None,
        static_obstacles=None, dynamic_obstacles=None,
    ):
        return super().reset(
            lambda: self._reset_robot_and_obstacles(
                start=start, goal=goal,
                static_obstacles=static_obstacles,
                dynamic_obstacles=dynamic_obstacles,
            )
        )

    def _reset_robot_and_obstacles(
        self, start=None, goal=None, 
        dynamic_obstacles=None, static_obstacles=None,
    ):
        robot_positions = []

        for manager in self.robot_managers:
            for pos in manager.reset(
                forbidden_zones=robot_positions
            ):
                robot_positions.append(
                    [
                        pos[0], 
                        pos[1], 
                        manager.robot_radius + Constants.RobotManager.SPAWN_ROBOT_SAFE_DIST
                    ]
                )
                
        self.obstacles_manager.reset_navpred(
            forbidden_zones=robot_positions
        )

        return False, (0, 0, 0)
