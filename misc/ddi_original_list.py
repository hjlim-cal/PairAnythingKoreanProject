import requests
import pandas as pd

# 💡 Pro tip: Adding /products.json?limit=250 fetches the raw product data cleanly!
url = "https://www.ddiwine.com/collections/all-wine/products.json?limit=250"

try:
    # 1. Fetch data from the website
    response = requests.get(url)
    data = response.json()
    products = data.get('products', [])
    
    # 2. Extract only the wine titles and URLs
    wine_list = []
    for p in products:
        wine_list.append({
            'Wine': p['title'],
            'info_url': f"https://www.ddiwine.com/products/{p['handle']}"
        })
        
    # 3. Convert to a DataFrame
    df = pd.DataFrame(wine_list)
    print(f"🎉 Successfully fetched {len(df)} wines!")
    
    # 4. Save to a CSV file (utf-8-sig prevents encoding issues)
    file_name = "Master_DDI_Wine_List.csv"
    df.to_csv(file_name, index=False, encoding='utf-8-sig')
    print(f"{file_name} has been created in your current folder!")
    
except Exception as e:
    print(f"An error occurred: {e}")