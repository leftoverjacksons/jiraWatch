import json

category_keywords = {
    'JDA': ['supply chain', 'warehouse management'],  
    'JDE': ['enterprise resource planning', 'ERP'],  
    'ORO': ['Inventory', 'ORO'],  
    'DBA': ['database administration', 'SQL server'],
    'Informatica': ['data integration', 'ETL'],
    'Catsy': ['PIM', 'product information management', 'casty'],
    'Snowflake': ['data lake', 'snowflake', 'snowfalke'],
    'CISCO': ['cisco'],
    'Veeam': ['veeam'],
    'AWS': ['aws']
}

vcp_pillar_keywords = {
    'Operations Execution': ['Drop Ship', 'eCommerce', 'Buford 3.0', 'CABRA', 'OFL', 'TMS'],
    'Transactional Experience': ['CPOV'],
}

def add_category_mapping():
    category = input("Enter the category name: ")
    keywords = input("Enter the associated keywords (comma-separated): ").split(",")
    category_keywords[category] = [keyword.strip() for keyword in keywords]
    print(f"New category '{category}' added with keywords: {keywords}")

def add_vcp_pillar_mapping():
    pillar = input("Enter the VCP pillar name: ")
    keywords = input("Enter the associated keywords (comma-separated): ").split(",")
    vcp_pillar_keywords[pillar] = [keyword.strip() for keyword in keywords]
    print(f"New VCP pillar '{pillar}' added with keywords: {keywords}")

def update_category_mappings():
    while True:
        print("\nCategory Mapping Update Options:")
        print("1. Add a new category mapping")
        print("2. Add a new VCP pillar mapping")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            add_category_mapping()
        elif choice == '2':
            add_vcp_pillar_mapping()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def save_category_mappings():
    with open('category_mappings.json', 'w') as f:
        json.dump({'category_keywords': category_keywords, 'vcp_pillar_keywords': vcp_pillar_keywords}, f)

try:
    with open('category_mappings.json', 'r') as f:
        mappings = json.load(f)
        category_keywords = mappings['category_keywords']
        vcp_pillar_keywords = mappings['vcp_pillar_keywords']
except FileNotFoundError:
    pass