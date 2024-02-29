import pandas as pd
import numpy as np

# Set display options
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Use maximum width of the console
pd.set_option('display.max_colwidth', 50)  # Adjusted to None to show full content

# Path to your CSV file
csv_file_path = 'jira_data.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Filter the DataFrame for entries where the status is "Done"
df_done = df[df['Status'] == 'Done'].copy()  # Create a copy to avoid SettingWithCopyWarning

# Convert 'Created' and 'Resolved' to datetime
df_done['Created'] = pd.to_datetime(df_done['Created'], errors='coerce')
df_done['Resolved'] = pd.to_datetime(df_done['Resolved'], errors='coerce')

# Rename 'Custom field (Story Points)' to 'Story Points'
df_done.rename(columns={'Custom field (Story Points)': 'Story Points'}, inplace=True)

# Calculate the total time in days for rows where both 'Created' and 'Resolved' are not NaT
df_done = df_done.dropna(subset=['Created', 'Resolved'])
df_done['Total Time (days)'] = (df_done['Resolved'] - df_done['Created']).dt.days

# Add a new column for Story Point Rate
# Set to 500 for 0 'Total Time (days)', otherwise calculate normally
df_done['Story Point Rate'] = df_done.apply(
    lambda row: 500 if row['Total Time (days)'] == 0 else row['Story Points'] / row['Total Time (days)'],
    axis=1
)



# Concatenate specific fields into a single string for each entry, ensuring all are converted to strings
df_done['Combined Text'] = df_done.apply(lambda row: ' '.join(str(row[col]) for col in ['Summary', 'Issue key', 'Status', 'Project name', 'Assignee', 'Priority', 'Resolution', 'Reporter', 'Created', 'Resolved', 'Description', 'VCP Pillar'] if col in df_done.columns), axis=1)

# Or, to print the concatenated text of a specific row, for example, row with index 68
if 68 in df_done.index:
    print(df_done.loc[68, 'Combined Text'])

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



# Rename 'Custom field (VCP Strategic Pillar)' to 'VCP Pillar'
df_done.rename(columns={'Custom field (VCP Strategic Pillar)': 'VCP Pillar'}, inplace=True)

# Define your VCP Pillars and associated auxiliary terms
vcp_pillar_keywords = {
    'Operations Execution': ['Drop Ship', 'eCommerce', 'Buford 3.0', 'CABRA', 'OFL', 'TMS'],
    'Transactional Experience': ['CPOV'],
    
    # ... add more pillars and associated keywords as needed
}

# Function to search for VCP Pillars and associated auxiliary terms in the combined text
def find_vcp_pillars(row):
    # Start with what's in the 'VCP Pillar' column
    pillars = {row['VCP Pillar']} if pd.notnull(row['VCP Pillar']) else set()

    # Check for auxiliary terms
    for pillar, keywords in vcp_pillar_keywords.items():
        for keyword in keywords:
            if keyword.lower() in row['Combined Text'].lower():
                pillars.add(pillar)

    return ', '.join(pillars) if pillars else np.nan

# Populate the new 'VCP Pillar' column using the function
df_done['VCP Pillar'] = df_done.apply(find_vcp_pillars, axis=1)

# Update the columns of interest to include 'Description' after 'Summary'
columns_of_interest = [
    'Issue key',
    'Summary',
    'Description',  # Include the description field
    'Story Points',
    'Story Point Rate',
    'Total Time (days)',
    'Associated Systems',
    'VCP Pillar'  # Make sure to include the new VCP Pillar column if you have added it
]

# Filter the DataFrame to include only the columns of interest
filtered_df_updated = df_done[columns_of_interest]

# Display the entries of the filtered DataFrame
print(filtered_df_updated.head(50))