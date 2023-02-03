from pandas import read_csv
import os
from pathlib import Path


dirname = os.path.dirname(__file__)

failed_path = Path(dirname) / "failed_records" / "sims_data_records"

for map_id in os.listdir(failed_path.resolve()):
    map_path = os.path.join(failed_path.resolve(), map_id)
    for sim_id in os.listdir(map_path):

        episodes_csv = read_csv(os.path.join(map_path, sim_id, "episode.csv"))
        episodes = episodes_csv["episode"].tolist()
        
        for num_ep in range(0, 30):
            if num_ep not in episodes:
                print(f"{num_ep} , {map_id}/{sim_id}")