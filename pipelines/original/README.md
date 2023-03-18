# Pipeline
The purpose of this pipeline is to unify the entire process of generating data to train neural networks to make predictions about navigation robot and planner navigation performance into a single script.

## Infrastructure
<img src="https://github.com/flameryx/navpred-data-recorder/blob/master/documentation/training_pipeline.png">
Our pipeline consists of four main modules and neural networks:

- <strong>Map-Generator</strong>: 
This module provides variability in the input parameters and generates a different map for each simulation run.
![Map Creator](https://user-images.githubusercontent.com/73646817/226105572-fc9f0ee5-3d41-4413-bf26-a166357398bc.gif)


- [<strong>Arena-bench Simulation</strong>](https://github.com/ignc-research/arena-bench):
This module is the development platform of our previous works, which is responsible for preparing and running the simulations. It takes as input the map created by the map generated, the navigation planner and the robot to be used, and many other randomized parameters to cause variety in the simulations. The obstacles are created with randomized attributes before the first simulation run, and each preserves the same characteristics through all simulated episodes.
![start up crop](https://user-images.githubusercontent.com/73646817/226103274-48944036-7d50-4117-a002-37840caae837.gif)

- <strong>Data Recorder</strong>:
This module records the parameters that describe the simulation, and real-time data of the behavior of the robot and obstacles during all episodes of the simulation.It consists of two recorders, simulation recorder and robot recorder.
![data raw](https://user-images.githubusercontent.com/73646817/226103747-f486c05a-8f88-450d-b794-0a10ce23b3d0.gif)

- <strong>Data Transformation</strong>: 
This module conveniently create directories for each map and simulation in which all the relevant data can be found. The end result is one line in the CSV data set which represents one simulation run on a random map. The output is also stored in directories with a yaml file format, which allows the map .png file to be stored with the final data.
![training data](https://user-images.githubusercontent.com/73646817/226103949-39df156f-6b29-423c-b183-76fa553b7517.gif)

- <strong>Neural Networks</strong>:
This module train the neural net works for different planners. See the detail [here](https://github.com/ignc-research/nav-prediction/tree/main/dnn).

## Flow Chart
<img src="https://github.com/flameryx/navpred-data-recorder/blob/master/documentation/pipeline_flow.png">

The pipeline script script is separated into three main independent processes:

• <strong>Map generation</strong>: Creating the map or maps on which
the simulations will run.

• <strong>Run simulations and record data</strong>: Running the simu-
lations under the randomized conditions while recording the data.

• <strong>Data cleaning, processing and transformation</strong>: Clean-
ing, processing and transforming the recorded data.

The pipeline takes as input the number of maps that the
user wants to record data on. Subsequently, it enters a loop
that only ends after simulations are ran on the number of
maps specified by the user. Inside the loop, first, the map is
randomly generated, selecting values from a range for each
of the map generation arguments, and stored. Then a separate
script analyzes the map and deducts the complexity of the
map represented in different metrics. This map is then passed
as input to arena-bench, together with other randomized
values that define the conditions of the simulations that will
be ran on that map. At the same time, while the simulations
are running, the data recorder is recording everything that is
happening during the simulation and storing it inside multiple
CSV files. After the simulation is finished, the pipeline
analyzes the recorded data to determine if there were any
errors during the recording, which could lead to misleading
or incomplete data. If the data fulfills the status requirements,
another process is executed on the recorded data to expand it
by extracting additional metrics that can be deduced from the
initial recorded data. Finally, the data transformation script is
executed on this expanded data and on the data of the used
map, created during the map generation process, to bring it
into the format needed to be used by the neural networks.

---

# Running the Pipeline

## Prerequisites
Below is the software we used. We cannot guarantee older versions of the software to work. Yet, newer software is most likely working just fine.

| Software      | Version        |
| ------------- | -------------- |
| OS            | Ubuntu 20.04.4 |
| Python        | 3.8.10         |





### Installation
Create a catkin workspace
Clone the repo:
```
git clone git@github.com:ignc-research/nav-prediction.git
```
Change into dir:
```
cd nav-prediction
```
Ros install
```
rosws update
```
Install python pkgs, you need poetry for this
```
poetry shell&&poetry install
```
Install stable baselines
```
cd ../forks/stable-baselines3 && pip install -e .
```
Build catkin!

```
cd ../../.. && catkin_make
```
For running the recording pipeline, install other requirements:
```
cd src/utils/navpred-data-recorder/pipelines/original && pip install -r requirements.txt
pip install mpi4py
```
Finish





### Recording
Recording should running in poetry:
```
cd ($your workspace)/src/nav-prediction && poetry shell
```

To record data as .csv file, you need to go inside the dir:
```
cd ($your workspace)/src/utils/navpred-data-recorder/pipelines/original
```
Then run the command:
```
python3 pipeline_script_ver2.py —num_maps (number of maps) —num_episodes (number of episodes)
```
You can set how many maps you want to record and how many times simulation resets on a map.
For example, if you want to record 500 lines of data which based on 500 maps, and for each map, the simulation will resets 30 times, then run:
```
python3 pipeline_script_ver2.py —num_maps 500 —num_episodes 30
```
To facilitate the process of gathering only the data of recordings that finished successfully, running the command after finishing recording a batch:
```
python3 collect_records.py

