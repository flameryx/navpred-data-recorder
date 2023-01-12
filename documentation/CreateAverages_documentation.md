Create Averages:

In this section we introduce the CreateAverages script and how to run it.

How to run the script:

The script is started by calling the command below. In this example the csv path and image path are specified by flat. 
There are also default flags which work with the general repository structure. 
A requirements file is provided which can be used to install all the necessary imports.

pip install -r requirements.txt

python3 createAverage.py

--image\_path /path/to/images

--csv\_path /path/to/csvFiles

The goal of the script is to compress the output of a recorded simulation setup with 36 iterations into a single output of their averages which can then be used as the input for a neuronal network. The output of a recorded simulation is a CSV file with several columns. Since not all columns are interesting for the neuronal network, we can classify our initial input columns into relevant and non relevant for the neuronal network

| Non relevant: | relevant |
| --- | --- |
| "Laser\_scan", "robot\_lin\_vel\_x", "robot\_lin\_vel\_y", "robot\_ang\_vel", "robot\_orientation", "robot\_pos\_x", "robot\_pos\_y", "action", "episode", "form\_dynamic\_obs", "Form\_static\_obs", | Time, Collision, Done\_resason, robot \_radius, robot\_max\_speed Size\_dynamic\_obs\_[1-15], Size\_static\_obstacles\_[1-15] Speed\_dynamic\_obs\_[1-15]
 

After reading a single CSV file the script drops the non relevant columns. Then duplicates and rows with missing values are removed. Since a neuronal network works more efficiently on numeric input values, the column "planner" which holds the route planner used for the simulated robot is one hot encoded. The columns size\_dynamic\_obs as well as speed\_dynamic\_obs are recorded in a way which leads to an array of values in the respected CSV column. This however is not suitable for operations which average over the columns. To combat this problem the problematic columns are extracted and the columns of the arrays are added to the original CSV file in the correct format. To end the data preprocessing the ['None'] values in the size\_static\_obs columns are replaced by zero. This allows the mean function, provided by the pandas DataFrame class, to create the averages of all columns of a CSV input file. The averages are stored in a new Dataframe containing only the relevant columns.

This process is done with all CSVs in the specified path. After that, if not suppressed the world\_complexity script is called. It will create the world complexity metrics and store them in a CSV file. The createAverage script will then read the metrics CSV and clean the data. Then the world metrics are added to the corresponding rows which were created using the map from which the complexity metrics are created. Also for every row a UUID is added. This creates the final dataframe with the columns

| Category | Column Name |
| --- | --- |
| Complexity metrics | angleInfo\_mean, entropyRatio, mapSize numObs\_Cv2, occupancyRatio, distance\_avg, distance\_norm distance\_var |
| Obstacle metrics | size\_dynamic\_obs\_[1-15], size\_static\_obs\_[1-15], speed\_dynamic\_obs\_[1-15] |
| Performance metrics | collision\_rate, episode\_duration, success\_rate
| Robot metrics | robot\_max\_speed, robot\_radius |

Finally output will be created in a folder structure resembling:

data/{UUID}/

{UUID}\_map\_complexity\_metric.yml

{UUID}\_map\_obstacle\_metrics.yml

{UUID}\_performance\_metric.yml

{UUID}\_robot\_metrics.yml
