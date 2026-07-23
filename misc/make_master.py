import pandas as pd

# 1. korean food data
korean_foods_data = [
    {"id": "01", "search_key": "소갈비구이", "official_name": "Sogalbi-gui", "description": "Grilled Beef Short Ribs"},
    {"id": "02", "search_key": "불고기", "official_name": "Bulgogi", "description": "Marinated Thinly Sliced Beef"},
    {"id": "03", "search_key": "순대", "official_name": "Sundae", "description": "Korean Blood Sausage"},
    {"id": "04", "search_key": "삼겹살구이", "official_name": "Samgyeopsal-gui", "description": "Grilled Pork Belly"},
    {"id": "05", "search_key": "소고기등심구이", "official_name": "Sogogi Deungsim-gui", "description": "Grilled Beef Ribeye"},
    {"id": "06", "search_key": "제육볶음", "official_name": "Jeyuk-bokkeum", "description": "Spicy Stir-fried Pork"},
    {"id": "07", "search_key": "항정살구이", "official_name": "Hangjeongsal-gui", "description": "Grilled Pork Neck"},
    {"id": "08", "search_key": "통삼겹오븐구이", "official_name": "Tong-samgyeop-gui", "description": "Oven-Roasted Pork Belly"},
    {"id": "09", "search_key": "매운족발", "official_name": "Maeun-jokbal", "description": "Spicy Braised Pork Trotters"},
    {"id": "10", "search_key": "소갈비찜", "official_name": "Sogalbi-jjim", "description": "Braised Beef Short Ribs"},
    {"id": "11", "수육보쌈": "수육보쌈", "official_name": "Suyuk Bossam", "description": "Boiled Pork Wraps"},
    {"id": "12", "search_key": "한방족발", "official_name": "Hanbang-jokbal", "description": "Braised Pork Trotters with Herbs"},
    {"id": "13", "search_key": "닭볶음탕", "official_name": "Dak-bokkeum-tang", "description": "Spicy Braised Chicken"},
    {"id": "14", "search_key": "안동찜닭", "official_name": "Andong-jjimdak", "description": "Braised Chicken with Soy Sauce"},
    {"id": "15", "search_key": "두부김치", "official_name": "Dubu-kimchi", "description": "Tofu with Stir-fried Kimchi"},
    {"id": "16", "search_key": "매운갈비찜", "official_name": "Maeun-galbi-jjim", "description": "Spicy Braised Pork Ribs"},
    {"id": "17", "search_key": "치킨만들기", "official_name": "Chikin", "description": "Crispy Korean Fried Chicken"},
    {"id": "18", "search_key": "양념치킨", "official_name": "Yangnyeom Chikin", "description": "Sweet and Spicy Fried Chicken"},
    {"id": "19", "search_key": "김치전", "official_name": "Kimchijeon", "description": "Kimchi Pancake"},
    {"id": "20", "search_key": "해물파전", "official_name": "Haemul-pajeon", "description": "Seafood Green Onion Pancake"},
    {"id": "21", "search_key": "감자전", "official_name": "Gamjajeon", "description": "Potato Pancake"},
    {"id": "22", "search_key": "소고기육전", "official_name": "Sogogi-yukjeon", "description": "Pan-fried Battered Beef"},
    {"id": "23", "search_key": "탕수육", "official_name": "Tangsuyuk", "description": "Sweet and Sour Pork"},
    {"id": "24", "search_key": "고기만두", "official_name": "Gogi-mandu", "description": "Meat Dumplings"},
    {"id": "25", "search_key": "아구찜", "official_name": "Agujjim", "description": "Spicy Braised Monkfish"},
    {"id": "26", "search_key": "낙지볶음", "official_name": "Nakji-bokkeum", "description": "Spicy Stir-fried Octopus"},
    {"id": "27", "search_key": "간장게장", "official_name": "Ganjang-gejang", "description": "Soy Sauce Marinated Crab"},
    {"id": "28", "search_key": "해물탕", "official_name": "Haemultang", "description": "Spicy Seafood Stew"},
    {"id": "29", "search_key": "골뱅이무침", "official_name": "Golbaengi-muchim", "description": "Spicy Sea Snail Salad"},
    {"id": "30", "search_key": "간장새우장", "official_name": "Ganjang-saeujang", "description": "Soy Sauce Marinated Shrimp"},
    {"id": "31", "search_key": "오뎅탕", "official_name": "Eomuk-tang", "description": "Fish Cake Soup"},
    {"id": "32", "search_key": "비빔밥", "official_name": "Bibimbap", "description": "Mixed Rice with Vegetables and Meat"},
    {"id": "33", "search_key": "김밥", "official_name": "Gimbap", "description": "Korean Seaweed Rice Rolls"},
    {"id": "34", "search_key": "잡채", "official_name": "Japchae", "description": "Stir-fried Glass Noodles and Vegetables"},
    {"id": "35", "search_key": "짜장면", "official_name": "Jajangmyeon", "description": "Noodles in Black Bean Sauce"},
    {"id": "36", "search_key": "짬뽕", "official_name": "Jjamppong", "description": "Spicy Seafood Noodle Soup"},
    {"id": "37", "search_key": "김치볶음밥", "official_name": "Kimchi-bokkeumbap", "description": "Kimchi Fried Rice"},
    {"id": "38", "search_key": "비빔냉면", "official_name": "Bibim-naengmyeon", "description": "Spicy Cold Noodles"},
    {"id": "39", "search_key": "떡볶이", "official_name": "Tteokbokki", "description": "Spicy Stir-fried Rice Cakes"},
    {"id": "40", "search_key": "로제떡볶이", "official_name": "Rose Tteokbokki", "description": "Rice Cakes in Spicy Cream Sauce"},
    {"id": "41", "search_key": "소고기육회", "official_name": "Sogogi-yukhoe", "description": "Korean Beef Tartare"},
    {"id": "42", "search_key": "떡갈비", "official_name": "Tteokgalbi", "description": "Grilled Short Rib Patties"},
    {"id": "43", "search_key": "소곱창구이", "official_name": "Sogopchang-gui", "description": "Grilled Beef Intestines"},
    {"id": "44", "search_key": "두부조림", "official_name": "Dubu-jorim", "description": "Braised Tofu in Spicy Sauce"},
    {"id": "45", "search_key": "제육타코", "official_name": "Jeyuk Tacos", "description": "Spicy Pork Tacos"},
    {"id": "46", "search_key": "김치치즈볼", "official_name": "Kimchi Cheese Ball", "description": "Kimchi and Cheese Arancini"},
    {"id": "47", "search_key": "등갈비바베큐", "official_name": "Deunggalbi Barbecue", "description": "Korean BBQ Pork Ribs"},
    {"id": "48", "search_key": "순대볶음", "official_name": "Sundae-bokkeum", "description": "Spicy Stir-fried Blood Sausage"},
    {"id": "49", "search_key": "순두부찌개", "official_name": "Sundubu-jjigae", "description": "Spicy Soft Tofu Stew"},
    {"id": "50", "search_key": "부대찌개", "official_name": "Budae-jjigae", "description": "Spicy Sausage Stew"},
    {"id": "51", "search_key": "감자탕", "official_name": "Gamjatang", "description": "Pork Bone Stew"}
]

# 2. dateframe
df = pd.DataFrame(korean_foods_data)

# 3. save CSV file 
df.to_csv('korean_foods_master.csv', index=False, encoding='utf-8-sig')
print("Successfully generated the master CSV file")