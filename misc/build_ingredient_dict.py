import os
import pandas as pd
import re

def extract_unique_ingredients(df, column_name):
    """
    Robust tokenizer that extracts clean, pure Korean ingredient tokens
    by stripping out quantities, units, and customized junk words.
    """
    unique_ingredients = set()
    for text in df[column_name].dropna():
        cleaned_text = str(text)
        cleaned_text = re.sub(r'\d+(g|ml|kg|Ts|ts|컵|스푼|개|줄|장|쪽|알|통|공기)?', ' ', cleaned_text)
        cleaned_text = re.sub(r'[^가-힣\s]', ' ', cleaned_text)
        
        tokens = cleaned_text.split()
        for token in tokens:
            token = token.strip()
            
            # stop words
            stopwords = [
                '약간', '적당량', '구매', '필수', '선택', '재료', '양념', '또또아', '마늘크기',
                '받음', '센티', '손질된', '스틱', '앞다리', '앞다리살', '인치', '작은거', '작은술', '주먹',
                '큰거', '한마리', '혹은', '된장크게', '슈레드','공기','다진','등분으로',
                '가루', '굵은것', '냉동', '넉넉히', '다진것', '조금', '적당히', '준비'
            ]
            
            if len(token) > 1 and token not in stopwords:
                unique_ingredients.add(token)
                
    return sorted(list(unique_ingredients))

def get_company_flavor_profile(ingredient_name):
    """
    PairAnything Official 8-Flavor Matrix Alignment Engine.
    Maps Korean raw components strictly to the company's proprietary taxonomy.
    """
    # Baseline: 1 (None/Low) to 5 (High)
    profile = {
        "Sweetness": 1,
        "Acidity": 1,
        "Saltiness": 1,
        "Bitterness": 1,
        "Umami": 1,
        "Spiciness_Heat": 1,
        "Richness": 1,
        "Texture_Prep": 1
    }
    
    name = ingredient_name.strip()
    
    # 🥩 Rich Fats, Heavy Proteins, and Substantial Textures
    if any(x in name for x in ['고기', '갈비', '삼겹살', '목살', '안심', '등심', '소고기', '돼지고기', '닭고기', '오리', '베이컨', '사골']):
        profile.update({"Umami": 5, "Richness": 5, "Texture_Prep": 4})
    # 🌶️ Spiciness & Heat
    elif any(x in name for x in ['고추장', '고춧가루', '고추', '청양고추', '다대기', '辛', '핫소스']):
        profile.update({"Spiciness_Heat": 5, "Sweetness": 2, "Saltiness": 3, "Umami": 3})
    # 🍯 Sugars & Sweeteners
    elif any(x in name for x in ['설탕', '물엿', '올리고당', '꿀', '매실청', '시럽']):
        profile.update({"Sweetness": 5})
    # 🍋 Acids / Fermented Tang
    elif any(x in name for x in ['식초', '레몬', '쌈무', '장아찌', '김치', '동치미']):
        profile.update({"Acidity": 4, "Saltiness": 2, "Umami": 2})
    # 🧄 Aromatics / Alliums
    elif any(x in name for x in ['마늘', '양파', '대파', '쪽파', '생강']):
        profile.update({"Sweetness": 2, "Umami": 2, "Bitterness": 2})
    # 🐟 Seafood & Marine Umami
    elif any(x in name for x in ['오징어', '새우', '낙지', '멸치', '굴', '조개', '고등어', '갈치', '해물', '액젓', '간장', '된장', '고추장']):
        profile.update({"Saltiness": 4, "Umami": 5})
    # 🥑 Oils, Dairy, and Mouthcoating Fats
    elif any(x in name for x in ['참기름', '들기름', '버터', '치즈', '마요네즈', '참깨', '오일']):
        profile.update({"Richness": 4, "Texture_Prep": 3})
    # 🌿 Bitter Greens / Herbs
    elif any(x in name for x in ['깻잎', '쑥', '미나리', '취나물', '씀바귀', '도라지']):
        profile.update({"Bitterness": 4})
        
    return profile

def main():
    input_file = 'korean_recipes_fixed_v1.csv'
    target_column = 'cleaned_ingredients'
    
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"❌ Error: '{input_file}' missing from project directory.")
        return

    print("🧩 Step 1: Isolating unique culinary components from clean master dataset...")
    ingredients_vocab = extract_unique_ingredients(df, target_column)
    print(f"📊 Total unique ingredients isolated (After custom filters): {len(ingredients_vocab)}")

    print("\n🧠 Step 2: Mapping to PairAnything Proprietary 8-Flavor Matrix...")
    output_rows = []
    
    for ing in ingredients_vocab:
        scores = get_company_flavor_profile(ing)
        output_rows.append({
            "ingredient_name": ing,
            "Sweetness": scores["Sweetness"],
            "Acidity": scores["Acidity"],
            "Saltiness": scores["Saltiness"],
            "Bitterness": scores["Bitterness"],
            "Umami": scores["Umami"],
            "Spiciness_Heat": scores["Spiciness_Heat"],
            "Richness": scores["Richness"],
            "Texture_Prep": scores["Texture_Prep"]
        })
        
    output_file = 'ingredient_flavor_lexicon.csv'
    df_lexicon = pd.DataFrame(output_rows)
    df_lexicon.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 70)
    print("🎉 Pipeline Stage 2 Complete (Custom Stopwords Filtered)!")
    print(f"💾 Active flavor lexicon safely generated and saved to: '{output_file}'")

if __name__ == "__main__":
    main()