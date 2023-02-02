import shutil
import os

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
if os.path.exists(records_path):
    shutil.move(averages_path, "correct_records/dnn_input_data/CombinedAverages.csv")
                
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