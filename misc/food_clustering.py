import pandas as pd
import numpy as np
import re
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def parse_ingredients(text):
    # Custom stopwords list including recent additions
    stopwords = [
        '약간', '적당량', '구매', '필수', '선택', '재료', '양념', '또또아', '마늘크기',
        '받음', '센티', '손질된', '스틱', '앞다리', '앞다리살', '인치', '작은거', '작은술', '주먹',
        '큰거', '한마리', '혹은', '된장크게', '슈레드', '공기', '다진', '등분으로',
        '가루', '굵은것', '냉동', '넉넉히', '다진것', '조금', '적당히', '준비'
    ]
    
    cleaned_text = re.sub(r'\d+(g|ml|kg|Ts|ts|컵|스푼|개|줄|장|쪽|알|통|공기)?', ' ', str(text))
    cleaned_text = re.sub(r'[^가-힣\s]', ' ', cleaned_text)
    
    tokens = [t.strip() for t in cleaned_text.split() if len(t.strip()) > 1 and t.strip() not in stopwords]
    return tokens

def calculate_recipe_vector(recipe_ingredients, lexicon_df):
    axes = ['Sweetness', 'Acidity', 'Saltiness', 'Bitterness', 'Umami', 'Spiciness_Heat', 'Richness', 'Texture_Prep']
    vector = {axis: [] for axis in axes}
    
    # List of main proteins to prevent dilution
    main_proteins = ['고기', '갈비', '삼겹살', '목살', '항정살', '곱창', '오겹살', '베이컨', '새우', '오징어', '낙지', '꽃게', '아구', '골뱅이', '순대']
    
    for ing in recipe_ingredients:
        match = lexicon_df[lexicon_df['ingredient_name'] == ing]
        if not match.empty:
            # Apply weight of 2 for main protein ingredients
            weight = 2 if any(p in ing for p in main_proteins) else 1
            
            for _ in range(weight):
                for axis in axes:
                    vector[axis].append(match.iloc[0][axis])
    
    final_vector = {}
    for axis in axes:
        if vector[axis]:
            final_vector[axis] = round(np.mean(vector[axis]), 2)
        else:
            final_vector[axis] = 1.0
            
    return final_vector

def main():
    print("Stage 3: Culinary Clustering Pipeline Initialized")
    
    try:
        recipes_df = pd.read_csv('korean_recipes_fixed_v1.csv')
        lexicon_df = pd.read_csv('ingredient_flavor_lexicon.csv')
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return
        
    print("Step 1: Vectorizing 51 Korean Recipes into 8D Flavor Space...")
    flavor_vectors = []
    
    for index, row in recipes_df.iterrows():
        ingredients_list = parse_ingredients(row['cleaned_ingredients'])
        vector = calculate_recipe_vector(ingredients_list, lexicon_df)
        vector['food_name'] = row['food_name']
        flavor_vectors.append(vector)
        
    vector_df = pd.DataFrame(flavor_vectors)
    
    cols = ['food_name', 'Sweetness', 'Acidity', 'Saltiness', 'Bitterness', 'Umami', 'Spiciness_Heat', 'Richness', 'Texture_Prep']
    vector_df = vector_df[cols]
    
    X = vector_df.drop('food_name', axis=1).copy()
    
    # Amplify Spiciness_Heat feature to clearly separate spicy vs non-spicy dishes
    X['Spiciness_Heat'] = X['Spiciness_Heat'] * 2.0
    
    # Introduce Seafood_Index to isolate seafood dishes (prevents mixing with meat clusters)
    seafood_keywords = ['꽃게', '게장', '새우', '낙지', '오징어', '골뱅이', '아구', '해물', '쭈꾸미', '명란']
    X['Seafood_Index'] = vector_df['food_name'].apply(
        lambda name: 3.0 if any(s in name for s in seafood_keywords) else 0.0
    )
    
    print("Step 2: Standardizing data for scale-invariant distances...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Set clusters to 6 to accommodate the new seafood separation
    n_clusters = 6
    print(f"Step 3: Applying K-Means algorithm (k={n_clusters})...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    vector_df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    output_file = 'korean_food_clusters.csv'
    vector_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 70)
    print("Pipeline Stage 3 Complete!")
    print(f"Clustered recipe vectors saved to: '{output_file}'")
    
    print("\nDish Distribution across Clusters:")
    print(vector_df['Cluster'].value_counts())

if __name__ == "__main__":
    main()