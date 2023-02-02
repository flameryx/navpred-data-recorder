import shutil
import os
from pathlib import Path

# Create collect_records folder if it does not exist
dirname = os.path.dirname(__file__)

# Create local maps folder if it does not exist
correct_records = Path(dirname) / "correct_records"
correct_records.mkdir(parents=True, exist_ok=True)

(correct_records.resolve() / "dnn_input_data").mkdir(parents=True, exist_ok=True)
(correct_records.resolve() / "maps").mkdir(parents=True, exist_ok=True)
(correct_records.resolve() / "sims_data_records").mkdir(parents=True, exist_ok=True)

# Create failed_records folder if it does not exist
failed_records = Path(dirname) / "failed_records"
failed_records.mkdir(parents=True, exist_ok=True)

(failed_records.resolve() / "dnn_input_data").mkdir(parents=True, exist_ok=True)
(failed_records.resolve() / "maps").mkdir(parents=True, exist_ok=True)
(failed_records.resolve() / "sims_data_records").mkdir(parents=True, exist_ok=True)


with open("correct_records.txt") as file:
    for idx, line in enumerate(file):
        if idx > 0:
            map_id, sim_id = line.split(",")
            
            map_path = f"maps/{map_id}"
            dnn_input_path = f"dnn_input_data/{map_id}"
            records_path = f"sims_data_records/{map_id}"
            
            if os.path.exists(map_path):
                shutil.move(f"maps/{map_id}", f"correct_records/maps/{map_id}")
                
            if os.path.exists(dnn_input_path): 
                shutil.move(f"dnn_input_data/{map_id}", f"correct_records/dnn_input_data/{map_id}")
                
            if os.path.exists(records_path):
                shutil.move(f"sims_data_records/{map_id}", f"correct_records/sims_data_records/{map_id}")
            
            
averages_path = "dnn_input_data/CombinedAverages.csv"
new_averages_path = "correct_records/dnn_input_data/CombinedAverages.csv"

if not os.path.exists(new_averages_path):
    if os.path.exists(averages_path) :
        shutil.move(averages_path, "correct_records/dnn_input_data/CombinedAverages.csv")
else:
    f_old = open("dnn_input_data/CombinedAverages.csv")
    f_new = open("correct_records/dnn_input_data/CombinedAverages.csv", 'a')
    
    for idx, line in enumerate(f_old):
        if idx > 0:
            f_new.write(line)
    os.remove("dnn_input_data/CombinedAverages.csv")
    
                
with open("correct_records.txt", 'w') as f:
    f.write('map_name,sim_id\n')
            
            
with open("failed_records.txt") as file:
    for idx, line in enumerate(file):
        if idx > 0:
            failed_reason, map_id, sim_id = line.split(",")
            
            map_path = f"maps/{map_id}"
            dnn_input_path = f"dnn_input_data/{map_id}"
            records_path = f"sims_data_records/{map_id}"
            
            if os.path.exists(map_path):
                shutil.move(map_path, f"failed_records/maps/{map_id}")
            
            if os.path.exists(dnn_input_path):
                shutil.move(dnn_input_path, f"failed_records/dnn_input_data/{map_id}")
            
            if os.path.exists(records_path):
                shutil.move(records_path, f"failed_records/sims_data_records/{map_id}")

with open("failed_records.txt", 'w') as f:
    f.write('fail_reason,map_name,sim_id\n')
    
