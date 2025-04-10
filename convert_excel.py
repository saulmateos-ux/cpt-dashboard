import pandas as pd
import numpy as np
import pprint

# Read the Excel file
df = pd.read_excel('Collections by CPT Code Georgia - merged.xlsx')

# Clean the data
def clean_data(df):
    # Replace NaN values with None
    df = df.replace({np.nan: None})
    
    # Convert DataFrame to dict
    data_dict = df.to_dict('list')
    
    # Clean up the dictionary values
    for key in data_dict:
        data_dict[key] = [
            None if pd.isna(x) else x 
            for x in data_dict[key]
        ]
    
    return data_dict

# Clean and convert the data
data_dict = clean_data(df)

# Write to Python file with proper formatting
with open('data_code.py', 'w', encoding='utf-8') as f:
    f.write('import numpy as np\n\n')
    f.write('data = ')
    # Use pprint to format the dictionary with Python syntax
    f.write(pprint.pformat(data_dict, indent=2, width=120)) 