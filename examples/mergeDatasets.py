import pandas as pd
import glob

# Specify the path where your CSV files are located
path = 'datasets'

# Use glob to get all the CSV files in the specified path
all_files = glob.glob(path + "/*.csv")

# Initialize an empty list to store the data frames
li = []

# Loop through all the CSV files and read them into pandas data frames
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

# Concatenate all the data frames into a single data frame
combined_df = pd.concat(li, axis=0, ignore_index=True)

# Write the combined data frame to a new CSV file
combined_df.to_csv('combined_data.csv', index=False)
