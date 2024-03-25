import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from category_config import category_keywords, vcp_pillar_keywords, update_category_mappings, save_category_mappings

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

csv_file_path = 'jira_data.csv'
df = pd.read_csv(csv_file_path)

df_done = df[df['Status'] == 'Done'].copy()

df_done['Created'] = pd.to_datetime(df_done['Created'], errors='coerce')
df_done['Resolved'] = pd.to_datetime(df_done['Resolved'], errors='coerce')

df_done.rename(columns={'Custom field (Story Points)': 'Story Points'}, inplace=True)

df_done = df_done.dropna(subset=['Created', 'Resolved'])
df_done['Total Time (days)'] = (df_done['Resolved'] - df_done['Created']).dt.days

df_done['Story Point Rate'] = df_done.apply(
    lambda row: 500 if row['Total Time (days)'] == 0 else row['Story Points'] / row['Total Time (days)'],
    axis=1
)

df_done['Combined Text'] = df_done.apply(lambda row: ' '.join(str(row[col]) for col in ['Summary', 'Issue key', 'Status', 'Project name', 'Assignee', 'Priority', 'Resolution', 'Reporter', 'Created', 'Resolved', 'Description', 'VCP Pillar'] if col in df_done.columns), axis=1)

if 68 in df_done.index:
    print(df_done.loc[68, 'Combined Text'])

def find_categories_with_keywords(text):
    found_categories = []
    for category, keywords in category_keywords.items():
        if category in text:
            found_categories.append(category)
        else:
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    found_categories.append(category)
                    break
    return ', '.join(set(found_categories)) if found_categories else np.nan

df_done['Associated Systems'] = df_done['Combined Text'].apply(find_categories_with_keywords)

df_done['Associated Systems'] = df_done['Associated Systems'].fillna('Unknown')

df_done.rename(columns={'Custom field (VCP Strategic Pillar)': 'VCP Pillar'}, inplace=True)

def find_vcp_pillars(row):
    pillars = {row['VCP Pillar']} if pd.notnull(row['VCP Pillar']) else set()
    for pillar, keywords in vcp_pillar_keywords.items():
        for keyword in keywords:
            if keyword.lower() in row['Combined Text'].lower():
                pillars.add(pillar)
    return ', '.join(pillars) if pillars else np.nan

df_done['VCP Pillar'] = df_done.apply(find_vcp_pillars, axis=1)

columns_of_interest = [
    'Issue key',
    'Summary',
    'Description',
    'Story Points',
    'Story Point Rate',
    'Total Time (days)',
    'Associated Systems',
    'VCP Pillar'
]

filtered_df_updated = df_done[columns_of_interest]

print(filtered_df_updated.iloc[80:120])

df_done['WeekYear'] = df_done['Created'].dt.strftime('%Y-%U')

df_done_expanded = df_done.drop('Associated Systems', axis=1).join(
    df_done['Associated Systems'].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).rename('Associated Systems')
).reset_index(drop=True)

df_done_expanded['Story Points'] /= df_done_expanded.groupby(['Issue key'])['Story Points'].transform('size')

weekly_points = df_done_expanded.groupby(['WeekYear', 'Associated Systems'])['Story Points'].sum().reset_index()

weekly_points_pivot = weekly_points.pivot(index='WeekYear', columns='Associated Systems', values='Story Points').fillna(0)

weekly_points_pivot.sort_index(inplace=True)

category_totals = weekly_points_pivot.sum(axis=0)

sorted_categories = category_totals.sort_values(ascending=False).index

weekly_points_pivot_sorted = weekly_points_pivot[sorted_categories]

plt.figure(figsize=(12, 8))
plt.stackplot(weekly_points_pivot_sorted.index, weekly_points_pivot_sorted.T, labels=weekly_points_pivot_sorted.columns, alpha=0.8)
plt.title('Story Points per Week per Category (Stacked Area Plot, Sorted)')
plt.xlabel('Week of the Year')
plt.ylabel('Story Points')
plt.xticks(rotation=45)
plt.legend(loc='upper left', title='Category')
plt.tight_layout()

plt.show()
plt.ion()

def update_entry_mapping(entry, current_index):
    print(f"\nEntry: {entry}")
    while True:
        choice = input("Choose an option:\n1. Update Category\n2. Update VCP Pillar\n3. Show the next 20 lines\n")
        if choice == '1':
            while True:
                category_choice = input("Choose an option:\n1. Create a new category\n2. Update an existing category\n")
                if category_choice == '1':
                    category = input("Enter the new category name: ")
                    keywords = input("Enter the associated keywords (comma-separated): ").split(",")
                    category_keywords[category] = [keyword.strip() for keyword in keywords]
                    print(f"New category '{category}' added with keywords: {keywords}")
                    save_category_mappings()
                    break
                elif category_choice == '2':
                    print("Existing categories:")
                    for idx, category in enumerate(category_keywords.keys(), start=1):
                        print(f"{idx}. {category}")
                    category_index = input("Enter the number of the category you want to update: ")
                    if category_index.isdigit() and 1 <= int(category_index) <= len(category_keywords):
                        category = list(category_keywords.keys())[int(category_index) - 1]
                        keyword = input(f"Enter the keyword to add to the '{category}' category: ")
                        category_keywords[category].append(keyword)
                        print(f"Keyword '{keyword}' added to the '{category}' category.")
                        save_category_mappings()
                    else:
                        print("Invalid category choice. Skipping entry.")
                    break
                else:
                    print("Invalid choice. Please try again.")
        elif choice == '2':
            while True:
                pillar_choice = input("Choose an option:\n1. Create a new VCP pillar\n2. Update an existing VCP pillar\n")
                if pillar_choice == '1':
                    pillar = input("Enter the new VCP pillar name: ")
                    keywords = input("Enter the associated keywords (comma-separated): ").split(",")
                    vcp_pillar_keywords[pillar] = [keyword.strip() for keyword in keywords]
                    print(f"New VCP pillar '{pillar}' added with keywords: {keywords}")
                    save_category_mappings()
                    break
                elif pillar_choice == '2':
                    print("Existing VCP pillars:")
                    for idx, pillar in enumerate(vcp_pillar_keywords.keys(), start=1):
                        print(f"{idx}. {pillar}")
                    pillar_index = input("Enter the number of the VCP pillar you want to update: ")
                    if pillar_index.isdigit() and 1 <= int(pillar_index) <= len(vcp_pillar_keywords):
                        pillar = list(vcp_pillar_keywords.keys())[int(pillar_index) - 1]
                        keyword = input(f"Enter the keyword to add to the '{pillar}' VCP pillar: ")
                        vcp_pillar_keywords[pillar].append(keyword)
                        print(f"Keyword '{keyword}' added to the '{pillar}' VCP pillar.")
                        save_category_mappings()
                    else:
                        print("Invalid VCP pillar choice. Skipping entry.")
                    break
                else:
                    print("Invalid choice. Please try again.")
        elif choice == '3':
            print("Showing the next 20 lines:")
            start_index = current_index + 1
            end_index = min(start_index + 20, len(filtered_df_updated))
            print(filtered_df_updated.iloc[start_index:end_index])
            break
        else:
            print("Invalid choice. Please try again.")

current_index = -1
print("\nEntries without associated systems:")
for idx, entry in filtered_df_updated[filtered_df_updated['Associated Systems'].isnull()].iterrows():
    current_index = idx
    update_entry_mapping(entry['Combined Text'], current_index)