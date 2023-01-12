import os
import glob
import pandas as pd
import codecs

t = os.getcwd()
os.chdir(t+"/Csvs")
file_extension = '.csv'
all_filenames = [i for i in glob.glob(f"*{file_extension}")]
combined_csv_data = pd.concat([pd.read_csv(f, delimiter='t') for f in all_filenames])
os.chdir('..')
combined_csv_data.to_csv('combined_csv_data.csv')