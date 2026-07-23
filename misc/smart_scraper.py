import os
import requests
import json

# 1. 환경변수에서 Serper API 키 가져오기
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

# [보안 팁] 만약 터미널을 새로 켜서 키가 안 읽힌다면, 아래 주석을 풀고 실제 키를 넣으세요.
# os.environ["SERPER_API_KEY"] = "발급받은_실제_Serper_Key"
# SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

if not SERPER_API_KEY:
    print("❌ 에러: SERPER_API_KEY 환경변수를 찾을 수 없습니다.")
    print("💡 해결방법: 터미널에 export SERPER_API_KEY='내키'를 입력하거나 코드에 임시 주입하세요.")
    exit()

# Serper 구글 검색 API 엔드포인트
SERPER_URL = "https://google.serper.dev/search"
headers = {
    'X-API-KEY': SERPER_API_KEY,
    'Content-Type': 'application/json'
}

file_name = "KoreanFoodList.txt"

print("🚀 데이터 수집 2단계 폴백 파이프라인을 가동합니다.")
print("=" * 60)

if os.path.exists(file_name):
    # 2. 텍스트 파일 읽기
    with open(file_name, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    # 50개 메뉴 순회 시작
    for line in lines:
        if not line.strip():
            continue
            
        # 3. 쉼표(,)를 기준으로 한글 키워드와 영어 키워드 분리 (데이터 전처리)
        kr_dish, en_dish = line.strip().split(",")
        kr_dish = kr_dish.strip()
        en_dish = en_dish.strip()
        
        print(f"\n🔍 분석 중: {kr_dish} ({en_dish})")
        
        # ------------------------------------------------------------
        # [TRACK 1] 1순위: Food.com에서 영문명으로 검색
        # ------------------------------------------------------------
        query_food_com = f"site:food.com {en_dish}"
        payload_food_com = json.dumps({"q": query_food_com, "num": 1}) # 1등 결과만 필요
        
        try:
            response = requests.post(SERPER_URL, headers=headers, data=payload_food_com)
            results = response.json()
            
            # Food.com 검색 결과가 존재하는 경우
            if "organic" in results and len(results["organic"]) > 0:
                match = results["organic"][0]
                print(f"  ⭕ [1순위 성공] Food.com 매핑 완료!")
                print(f"  🔗 URL: {match.get('link')}")
                print(f"  📝 제목: {match.get('title')}")
                
                # TODO: 나중에 이 URL을 타고 들어가서 실제 레시피 본문을 긁어오는 코드가 들어갈 자리입니다.
                
            # ------------------------------------------------------------
            # [TRACK 2] 2순위 폴백: Food.com에 없으면 만개의 레시피에서 한글명으로 검색
            # ------------------------------------------------------------
            else:
                print(f"  ❌ [1순위 실패] Food.com에 결과 없음 ➔ 2순위 폴백 가동")
                
                query_10000 = f"site:10000recipe.com {kr_dish}"
                payload_10000 = json.dumps({"q": query_10000, "num": 1})
                
                response_10000 = requests.post(SERPER_URL, headers=headers, data=payload_10000)
                results_10000 = response_10000.json()
                
                if "organic" in results_10000 and len(results_10000["organic"]) > 0:
                    match_10000 = results_10000["organic"][0]
                    print(f"  ✅ [2순위 성공] 만개의 레시피 매핑 완료!")
                    print(f"  🔗 URL: {match_10000.get('link')}")
                    print(f"  📝 제목: {match_10000.get('title')}")
                    
                    # TODO: 나중에 만개의 레시피 본문을 긁어오는 코드가 들어갈 자리입니다.
                else:
                    print(f"  ⚠️ [최종 실패] 양쪽 플랫폼 모두에서 '{kr_dish}' 레시피를 찾지 못했습니다.")
                    
        except Exception as e:
            print(f"  ❌ API 통신 중 에러 발생 ({kr_dish}): {e}")
            
    print("\n" + "=" * 60)
    print("🎉 50개 메뉴에 대한 1차 주소 매핑 루프가 완료되었습니다!")

else:
    print(f"❌ '{file_name}' 파일을 찾을 수 없습니다.")