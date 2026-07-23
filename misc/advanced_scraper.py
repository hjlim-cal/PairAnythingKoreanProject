import os
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
import time
import random

# 1. API Key Authentication Configuration
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
if not SERPER_API_KEY:
    # Local fallback injection for development environment
    os.environ["SERPER_API_KEY"] = "044487658cb476d863ff8101ff99d01491a3b511"
    SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

if not SERPER_API_KEY:
    print("❌ Error: Please configure a valid SERPER_API_KEY.")
    exit()

SERPER_URL = "https://google.serper.dev/search"
HEADERS_SERPER = {
    'X-API-KEY': SERPER_API_KEY,
    'Content-Type': 'application/json'
}

# Spoof User-Agent to bypass basic anti-bot scraping blockades
HEADERS_BROWSER = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_ingredients_from_10000(url):
    """
    Parses the target URL from '10000recipe.com' and extracts raw ingredients text using BeautifulSoup.
    """
    try:
        response = requests.get(url, headers=HEADERS_BROWSER)
        if response.status_code != 200:
            return "Failed to establish connection to the webpage"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Target specific DOM structures containing ingredient metadata
        ingredient_area = soup.select_one('.ready_ingre3')
        if not ingredient_area:
            # Secondary fallback for legacy DOM layouts
            ingredient_area = soup.select_one('#divIngredientsInfo')
            
        if ingredient_area:
            # Sanitize text by removing excessive whitespaces and line breaks
            raw_text = ingredient_area.get_text(separator=" ").strip()
            clean_text = " ".join(raw_text.split())
            return clean_text
            
    except Exception as e:
        return f"Exception occurred during DOM parsing: {e}"
        
    return "Ingredient container element not found"

def main():
    print("🚀 Initializing Serper.dev + BeautifulSoup hybrid scraper pipeline.")
    print("=" * 70)
    
    # Ingest the refined master dataset
    try:
        df_master = pd.read_csv('korean_foods_master.csv')
    except FileNotFoundError:
        print("❌ Error: 'korean_foods_master.csv' missing from working directory.")
        return

    final_results = []

    # Execute full iteration pipeline for all 51 core Korean dishes
    for index, row in df_master.iterrows():
        food_id = row['id']
        food_name = row['search_key']
        
        print(f"\n[ID {food_id}] Processing pipeline for '{food_name}'...")
        
        # ------------------------------------------------------------
        # PHASE 1: Route precise recipe URL using Google Search API
        # ------------------------------------------------------------
        query = f"site:10000recipe.com/recipe/ {food_name}"
        payload = json.dumps({"q": query, "num": 1})
        
        recipe_url = None
        ingredients_text = "N/A"
        
        try:
            res_serper = requests.post(SERPER_URL, headers=HEADERS_SERPER, data=payload)
            results = res_serper.json()
            
            if "organic" in results and len(results["organic"]) > 0:
                recipe_url = results["organic"][0].get("link")
                print(f"  🔗 Target URL resolved: {recipe_url}")
                
                # ------------------------------------------------------------
                # PHASE 2: Dom scraping & content extraction via BeautifulSoup
                # ------------------------------------------------------------
                print("  🪝 Executing soup parser -> Extracting textual raw ingredients...")
                ingredients_text = get_ingredients_from_10000(recipe_url)
                print(f"  📝 Scraped snippet: {ingredients_text[:60]}...")
                
            else:
                print("  ❌ Primary fallback: '10000recipe' indexing mismatch. (Pending 'wtable' integration)")
                recipe_url = "wtable_integration_pending"
                ingredients_text = "wtable_integration_pending"
                
        except Exception as e:
            print(f"  ❌ Operational failure: {e}")
            
        final_results.append({
            "id": food_id,
            "food_name": food_name,
            "url": recipe_url,
            "raw_ingredients": ingredients_text
        })
        
        # Enforce random backoff interval to prevent IP ban (Rate Limiting)
        time.sleep(random.uniform(1.0, 2.5))

    # Export complete structured raw pipeline dataset to local storage
    df_output = pd.DataFrame(final_results)
    df_output.to_csv('korean_recipes_raw.csv', index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 70)
    print("Pipeline executed successfully! Data saved to 'korean_recipes_raw.csv'.")

if __name__ == "__main__":
    main()