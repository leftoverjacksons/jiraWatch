import pandas as pd
import numpy as np

# Set display options
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Use maximum width of the console
pd.set_option('display.max_colwidth', 1)  # Show the full content of each column

# Path to your CSV file
csv_file_path = 'jira_data.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Filter the DataFrame for entries where the status is "Done"
df_done = df[df['Status'] == 'Done'].copy()  # Create a copy to avoid SettingWithCopyWarning

# Convert 'Created' and 'Resolved' to datetime
df_done['Created'] = pd.to_datetime(df_done['Created'], errors='coerce')
df_done['Resolved'] = pd.to_datetime(df_done['Resolved'], errors='coerce')

# Calculate the total time in days for rows where both 'Created' and 'Resolved' are not NaT
df_done = df_done.dropna(subset=['Created', 'Resolved'])
df_done['Total Time (days)'] = (df_done['Resolved'] - df_done['Created']).apply(lambda x: x.total_seconds() / (24 * 3600))

# Add a new column for Story Point Rate
# Set to 500 for 0 'Total Time (days)', otherwise calculate normally
df_done['Story Point Rate'] = df_done.apply(
    lambda row: 500 if row['Total Time (days)'] == 0 else row['Custom field (Story Points)'] / row['Total Time (days)'],
    axis=1
)

# Define the columns you're interested in, including the new 'Story Point Rate'
columns_of_interest = [
    'Issue key',
    'Summary',
    'Created',
    'Resolved',
    'Custom field (Story Points)',
    'Story Point Rate'  # New calculated field
]

# Filter the DataFrame to include only the columns of interest
filtered_df = df_done[columns_of_interest]

# Display the first 10 entries of the filtered DataFrame
print(filtered_df.head(10))
