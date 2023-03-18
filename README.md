# Arena Rosnav Navpred Data Recorder

This is a package developed to facilitate the process of recording data of Arena Benchmark simulations, with the purpose of using that data to train Neural 
Networks to make predictions on the performance of certain robots and planners under specific scenarios. This package is meant to be used together with the
following Arena Benchmark infrastructure: https://github.com/ignc-research/nav-prediction.

## Contents

The package contains several .launch files used by nav-prediction to setup the simulation runs, and 3 other packages. The packages are:

### Data Recorder

This package is based on an older version of the Arena Evaluation package (https://github.com/Arena-Rosnav/arena-evaluation) with some minor changes applied 
to the data recording process and the recorded data file structure. Official documentation about this package can be found in the README.md inside the repo 
(https://github.com/flameryx/navpred-data-recorder/tree/master/data-recorder/README.md).

Some of the changes made to this repository include:
- Two different types of data recording nodes, one for recording general data about the simulation single instance per simulation) and one for recording data 
about the robot/s (one instance per robot).
- Added recording data of obstacles, including obstacle characteristics and starting position of each obstacle on each episode.
- New file structure of recorded data. Now general simulation data is stored in the main folder and the rest is separated into two inner folders: obstacles, 
robots. Inside obstacles, there is one folder designated for each obstacle, which contains the data of that obstacle. Inside robots, there is one folder
designated for each robot, which contains the data of that robot.


### Task Generator

This package is based on an older version of the Task Generator package (https://github.com/Arena-Rosnav/task-generator) with some minor additions and alterations
applied for the purpose of the Navigation Prediction Project. Official documentation about this package can be found in the README.md inside the repo
(https://github.com/flameryx/navpred-data-recorder/blob/master/task-generator/README.md).

Some of the changes made to this repository include:
- Addition of a new task mode called "Navpred". It creates a specified number of static and dynamic obstacles with randomized characteristics, and preserves 
them with their individual characteristics to be used on all episodes on the same map. When starting the task a random start position is selected for all 
obstacles, and a random goal and start position for the robot/s is also selected. After the robot reaches the goal a new task is started.

> 🚧 Warning: This package was adapted with the sole purpose of being used as part of the data recording pipeline, which only uses the Navpred task mode. For this
reason, it is possible that the other task modes do not function as expected. If you want to use Arena Benchmark for other purposes than recording simulation
data, we recommend using the latest version of Arena Benchmark.


### Pipelines

This package contains two data recording pipelines developed to make the process of recording randomized simulation data as easy and straightforward as 
possible. The two pipelines are named "original" and "alternative". The main difference between them, is that the original uses maps generated using the
Arena Tools Map Generator (https://github.com/Arena-Rosnav/arena-tools), whereas the alternative pipeline employs a different method for generating maps,
using generative adversarial network (GAN). The alternative pipeline did not make it to the later stages of development, for which reason we strongly recommend
ONLY using the original pipeline. Official documentation about the original pipeline can be found in the README.md inside the repo 
(https://github.com/flameryx/navpred-data-recorder/blob/master/pipelines/original/README.md).
