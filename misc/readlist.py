import pandas as pd

df = pd.read_csv('korean_food_clusters_with_descriptions.csv')
# 영문 이름 열(food_name_en)만 쭉 출력하고 싶을 때
print(df['food_name_en'].to_list())

# 💡 추천: 한글 이름과 영문 이름을 매칭해서 깔끔하게 표 형태로 확인하고 싶을 때
print(df[['food_name', 'food_name_en']])