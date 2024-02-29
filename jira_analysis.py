import pandas as pd
import numpy as np

# Set display options
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Use maximum width of the console
pd.set_option('display.max_colwidth', 30)  # Adjusted to None to show full content

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

# Define your categories and associated keywords
category_keywords = {
    'JDA': ['supply chain', 'warehouse management'],  
    'JDE': ['enterprise resource planning', 'ERP'],  
    'ORO': ['Inventory', 'ORO'],  
    'DBA': ['database administration', 'SQL server'],
    'Informatica': ['data integration', 'ETL'],
    'Catsy': ['PIM', 'product information management'],
    'Snowflake': ['data lake','snowflake']
}

# Function to search for categories and associated keywords in the combined text
def find_categories_with_keywords(text):
    found_categories = []
    for category, keywords in category_keywords.items():
        if category in text:
            found_categories.append(category)
        else:
            for keyword in keywords:
                if keyword.lower() in text.lower():  # Case-insensitive search
                    found_categories.append(category)
                    break  # Stop searching other keywords once a match is found for this category
    return ', '.join(set(found_categories)) if found_categories else np.nan

# Update the 'Associated Systems' column to use the new search function
df_done['Associated Systems'] = df_done['Combined Text'].apply(find_categories_with_keywords)



# Rename 'Custom field (Story Points)' to 'Story Points'
df_done.rename(columns={'Custom field (Story Points)': 'Story Points'}, inplace=True)

# Define columns of interest, now excluding 'Created', 'Resolved', and with 'Story Points' renamed
columns_of_interest = [
    'Issue key',
    'Summary',
    'Story Points',
    'Story Point Rate',
    'Associated Systems'  # Make sure this is included
]


# Filter the DataFrame to include only the columns of interest
filtered_df_updated = df_done[columns_of_interest]

# Display the first 40 entries of the filtered DataFrame
print(filtered_df_updated.head(50))
