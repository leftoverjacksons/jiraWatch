import pandas as pd
import numpy as np

# Set display options
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Use maximum width of the console
pd.set_option('display.max_colwidth', None)  # Adjusted to None to show full content

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

# Concatenate all text fields into a single string for each entry
df_done['Combined Text'] = df_done.apply(lambda row: ' '.join(str(row[col]) for col in df_done.columns if pd.api.types.is_string_dtype(df_done[col])), axis=1)

# Define the categories to search for
categories = ['JDA', 'JDE', 'ORO', 'DBA']

# Function to search for categories in the combined text and return found categories
def find_categories(text):
    found_categories = [category for category in categories if category in text]
    return ', '.join(found_categories) if found_categories else np.nan

# Search for categories in each entry and populate a new attribute
df_done['Associated Systems'] = df_done['Combined Text'].apply(find_categories)

# Previously missing definition of columns_of_interest
columns_of_interest = [
    'Issue key',
    'Summary',
    'Created',
    'Resolved',
    'Custom field (Story Points)',
    'Story Point Rate'  # This was already part of your final DataFrame
]

# Update the columns of interest to include 'Associated Systems'
columns_of_interest_updated = columns_of_interest + ['Associated Systems']

# Filter the DataFrame to include only the updated columns of interest
filtered_df_updated = df_done[columns_of_interest_updated]

# Display the first 10 entries of the filtered DataFrame
print(filtered_df_updated.head(40))
