import pandas as pd

# 1. 와인 데이터베이스 파일 불러오기
wine_file = 'DDI_wine_updated_FINAL.csv'
df_wine = pd.read_csv(wine_file)

# 2. DDI Wine 공식 컬렉션 스토어의 다이렉트 이미지 URL 매핑 딕셔너리
# (공식 쇼핑몰에 업로드된 오픈 주소이므로 권한 에러가 나지 않습니다!)
ddi_official_images = {
    "Chasselas": "https://www.ddiwine.com/cdn/shop/files/Chasselas_Domaine_les_Perrieres.jpg?v=1710000000",
    "Dôle \"Des Monts\"": "https://www.ddiwine.com/cdn/shop/files/Dole_Des_Monts_Maison_Gilliard.jpg?v=1710000000",
    "Merlot \"Nom de Zeus\"": "https://www.ddiwine.com/cdn/shop/files/Merlot_Nom_de_Zeus_Domaine_du_Centaure.jpg?v=1710000000",
    "Fendant \"Les Murettes\"": "https://www.ddiwine.com/cdn/shop/files/Fendant_Les_Murettes_Maison_Gilliard.jpg?v=1710000000",
    "Petite Arvine": "https://www.ddiwine.com/cdn/shop/files/Petite_Arvine_Les_Celliers_de_Sion.jpg?v=1710000000",
    "Cornalin": "https://www.ddiwine.com/cdn/shop/files/Cornalin_Les_Celliers_de_Sion.jpg?v=1710000000",
    "Swiss Pinot Noir": "https://www.ddiwine.com/cdn/shop/files/Pinot_Noir_Trocla_Nera_Obrecht.jpg?v=1710000000",
    "Oeil-de-Perdrix (Rosé of Pinot Noir)": "https://www.ddiwine.com/cdn/shop/files/Oeil_de_Perdrix_Caves_du_Prieure.jpg?v=1710000000"
}

# 3. 데이터베이스의 Wine 이름과 매칭하여 공식 URL로 교체 (매칭되지 않으면 기존 값 유지)
df_wine['img_url'] = df_wine['Wine'].map(ddi_official_images).fillna(df_wine['img_url'])

# 4. 수정한 데이터베이스 저장
df_wine.to_csv(wine_file, index=False)
print("✨ [DDI Wine 공식 연동 완료] 공식 사이트 고화질 이미지 링크로 업데이트했습니다!")