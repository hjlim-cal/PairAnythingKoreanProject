import pandas as pd
import re

def clean_ingredient_text(raw_text):
    """
    Cleans raw ingredient strings by stripping out metrics, units, 
    and unnecessary programmatic words like '구매'.
    """
    if pd.isna(raw_text) or "Element not found" in str(raw_text):
        return []
        
    # 1. Remove bracket headers like [재료], [양념], [주재료]
    text = re.sub(r'\[.*?\]', ' ', raw_text)
    
    # 2. Remove the specific repetitive target word '구매'
    text = text.replace('구매', ' ')
    
    # 3. Remove numeric values, fractions, and ranges (e.g., 800g, 1/2, 4~6)
    text = re.sub(r'\d+\/\d+', ' ', text)  # Matches fractions like 1/2
    text = re.sub(r'\d+~\d+', ' ', text)   # Matches ranges like 4~6
    text = re.sub(r'\d+', ' ', text)       # Matches any standalone digits
    
    # 4. Standardize delimiters: replace spaces or special markings with commas
    # Split text into a preliminary list of words
    raw_words = text.split()
    
    # 5. Filter out specific measurement units and common filler words
    stop_words = {
        'g', 'kg', 'ml', 'l', '컵', '줌', '대', '개', '모', '봉', '봉지', '팩', '토막', '장', 
        '마리', '알', '톨', '뿌리', '포기', '근', '통', '권', '조각', '스푼', '큰술', '티스푼', 
        'ts', 'TS', 't', 'T', '꼬집', '숟갈', '숟가락', '종이컵', '인분', '컵기준', '개기준',
        '약간', '적당량', '톡톡', '기호에맞게', '원하는만큼', '생략가능', '내외', '컷팅해서',
        '또는', '이나', '국그릇', '밥그릇', '동전크기', '원함', '없음패스', '톡', '번'
    }
    
    cleaned_ingredients = []
    for word in raw_words:
        # Strip trailing punctuation marks if any
        word = word.strip(',.()')
        
        # Keep the word only if it's not empty, not a stop word, and longer than 1 character
        if word and word not in stop_words and len(word) > 1:
            cleaned_ingredients.append(word)
            
    return cleaned_ingredients

def main():
    print("Initializing rule-based ingredient extraction pipeline.")
    print("=" * 70)
    
    # Load the synchronized master dataset from your Google Sheets workflow
    try:
        df = pd.read_csv('korean_recipes_raw.csv')
    except FileNotFoundError:
        print("❌ Error: 'korean_recipes_raw.csv' missing from working directory.")
        return

    all_ingredients_list = []
    dish_ingredient_map = []

    # Iterate through the 51 structured dishes
    for index, row in df.iterrows():
        food_name = row['food_name']
        raw_text = row['raw_ingredients']
        
        # Execute text normalization sequence
        ingredients = clean_ingredient_text(raw_text)
        
        # Collect for global unique tracking
        all_ingredients_list.extend(ingredients)
        
        # Format for mapping table
        dish_ingredient_map.append({
            "food_name": food_name,
            "cleaned_ingredients": ", ".join(ingredients)
        })
        
    # ------------------------------------------------------------
    # TASK 1: Generate Cleaned Ingredients Mapping for each Dish
    # ------------------------------------------------------------
    df_mapped = pd.DataFrame(dish_ingredient_map)
    df_mapped.to_csv('korean_recipes_cleaned.csv', index=False, encoding='utf-8-sig')
    print("✅ Task 1 Complete: Cleaned dataset saved to 'korean_recipes_cleaned.csv'")
    
    # ------------------------------------------------------------
    # TASK 2: Deduplicate and Extract Unique Master Ingredient List
    # ------------------------------------------------------------
    # Using Pandas series to easily drop duplicates and sort alphabetically
    unique_ingredients = pd.Series(all_ingredients_list).drop_duplicates().sort_values().reset_index(drop=True)
    
    # Export the deduplicated Master Ingredient List
    df_master_ingredients = pd.DataFrame({"master_ingredient_name": unique_ingredients})
    df_master_ingredients.to_csv('master_ingredients_list.csv', index=False, encoding='utf-8-sig')
    
    print("✅ Task 2 Complete: Deduplicated Master List saved to 'master_ingredients_list.csv'")
    print("=" * 70)
    print(f" Summary: Successfully extracted {len(unique_ingredients)} unique master ingredients!")

if __name__ == "__main__":
    main()