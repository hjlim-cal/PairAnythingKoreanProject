import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from tqdm import tqdm

def search_wtable_url(food_name):
    """
    Searches the secondary platform 'wtable.co.kr' to find the most relevant
    recipe detail page URL for the given dish.
    """
    search_url = f"https://wtable.co.kr/search?q={food_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            links = soup.find_all('a', href=re.compile(r'/recipes/\d+'))
            if links:
                return "https://wtable.co.kr" + links[0]['href']
    except Exception as e:
        print(f"⚠️ Search API Warning ({food_name}): {e}")
    return None

def scrape_wtable_ingredients(url):
    """
    Parses the target Wtable URL and extracts normalized textual ingredients metadata.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            ingredient_section = soup.find_all(class_=re.compile(r'Ingredient|ingredient|RecipeIngredients'))
            if ingredient_section:
                ingredients_text = " ".join([item.get_text(separator=" ").strip() for item in ingredient_section])
                return re.sub(r'\s+', ' ', ingredients_text)
    except Exception as e:
        return f"Exception during DOM parsing: {e}"
    return "Ingredient container element not found"

def main():
    file_name = 'korean_recipes_clean.csv'
    try:
        df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()
    except FileNotFoundError:
        print(f"❌ Error: '{file_name}' missing from working directory.")
        return
    
    print("🔒 Guardrail Active: Human-curated data protection mode enabled.")
    print("🔄 Target Column Mapped: 'cleaned_ingredients'")
    
    # Ensure 'url' column exists in dataframe without overwriting anything
    if 'url' not in df.columns:
        df['url'] = None
        
    updated_count = 0
    target_column = 'cleaned_ingredients' 

    for index, row in tqdm(df.iterrows(), total=len(df)):
        current_ingredients = str(row[target_column]).strip()
        food_name = row['food_name']
        
        # 🚨 [CRITICAL PROTECTION RULE] Skip rows already cleaned/validated by the user.
        if len(current_ingredients) > 15 and "container not found" not in current_ingredients and "nan" != current_ingredients.lower():
            continue
            
        print(f"\n🔍 Data gap detected ➔ Initiating fallback script for [{food_name}]")
        wtable_url = search_wtable_url(food_name)
        
        if wtable_url:
            print(f"  🔗 Target URL resolved: {wtable_url}")
            fetched_ingredients = scrape_wtable_ingredients(wtable_url)
            
            df.at[index, 'url'] = wtable_url
            df.at[index, target_column] = fetched_ingredients
            updated_count += 1
            print(f"  ✅ Extraction pipeline complete for [{food_name}]!")
        else:
            print(f"  ❌ Primary & Secondary mismatch for [{food_name}]. (Manual audit required)")
            
        time.sleep(1.5)
        
    output_file = 'korean_recipes_fixed_v1.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 70)
    print("🎉 Pipeline executed successfully!")
    print(f"💡 Total records patched from Wtable: {updated_count}")
    print(f"💾 Secure master dataset saved to: '{output_file}'")

if __name__ == "__main__":
    main()