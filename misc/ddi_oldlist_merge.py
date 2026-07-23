import pandas as pd

# 1. Load the scraped 38 wines (Change the file name if you used a different one)
df_scraped = pd.read_csv("Master_DDI_Wine_List.csv")

# 2. Load Dylan's flavor profiles (1-5 scales)
df_profiles = pd.read_csv("DDI Wines List - Wine Flavor Profiles.csv")

# 3. Merge the two datasets (Left join based on wine names)
# 'Wine' from scraped data matches 'varietal' from Dylan's data
merged_df = pd.merge(df_scraped, df_profiles, left_on='Wine', right_on='varietal', how='left')

# 4. Drop the duplicate name column and save the final master file
if 'varietal' in merged_df.columns:
    merged_df = merged_df.drop('varietal', axis=1)

merged_df.to_csv("Final_Wine_Database.csv", index=False, encoding='utf-8-sig')
print("✅ Merge complete! 'Final_Wine_Database.csv' has been created.")