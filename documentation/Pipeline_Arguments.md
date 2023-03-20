# Pipeline Arguments
On the following table you will find all the different arguments that can be set on the pipeline script to alter the conditions and scenarios of the simulation runs you will be recording with the pipeline. Whenever the argument is of input type "String separated by commas", the pipeline will randomly choose one of the given values for the simulations on the next map to be recorded on. Whenever the argument represents a maximum or minimum value, the pipeline will randomly choose a float value in between the given maximum and minimum values for the simulations on the next map to be recorded on.


| Arguments | Input type | Default | Description  |
|----------|:-------------:|:-----------:|-----------|
| --num_maps | Integer | 10 | On how many different maps do you want to record simulation data. |
| --num_episodes | Integer | 30 | How many episodes (simulation runs) do you want to record. |
| --planners | String separated by commas | "dwa,aio,teb,crowdnav,rlca" | What local planners do you want to use on the simulations. | 
| --robots | String separated by commas | "burger,agvota,dingo,jackal,ridgeback" | What robots do you want to use on the simulations. |
| --num_dyn_obs | String separated by commas | "0,2,4,6" | How many dynamic obstacles do you want on the simulations. |
| --obs_max_vel | Float | 1.0 | Maximum possible velocity an obstacle could have. | 
| --obs_min_vel | Float | 0.1 | Minumum possible velocity an obstacle could have. |
| --obs_max_radius | Float | 1.0 | Maximum possible radius an obstacle could have. |
| --obs_min_radius | Float | 0.1 | Minimum possible radius an obstacle could have. |
| --timeout | Integer | 30 | After how many seconds should a simulation run timeout. | 
| --map_types | String separated by commas | "indoor,outdoor" | On what type of map do you want to run the simulations. Only two options available: indoor and outdoor |
| --viz | String | flatland | How do you want to visualize the simulations. Only three options available: flatland, rviz, none
| --del_records | Boolean | False | Only set to True if you want to automatically delete all previously recorded data before starting a new recording process. Use with caution. | 
