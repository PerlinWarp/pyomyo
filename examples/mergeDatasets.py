import os
import pandas as pd

# Set the path to the folder containing datasets
folder_path = 'datasets'

# List all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize an empty DataFrame to store the combined data
combined_data = pd.DataFrame()

# Iterate through each CSV file and concatenate the data
for csv_file in csv_files:
    file_path = os.path.join(folder_path, csv_file)
    df = pd.read_csv(file_path)
    combined_data = pd.concat([combined_data, df], axis=1, ignore_index=True)

# Add the header to the combined DataFrame
header = ["sample_" + str(i) for i in range(combined_data.shape[1])]
combined_data.columns = header

# Save the combined DataFrame to a new CSV file
combined_data.to_csv('combined_dataset.csv', index=False)
