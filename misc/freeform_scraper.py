import os
import requests
import json

SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

if not SERPER_API_KEY:
    print("❌ 에러: SERPER_API_KEY 환경변수를 찾을 수 없습니다.")
    exit()

SERPER_URL = "https://google.serper.dev/search"
headers = {
    'X-API-KEY': SERPER_API_KEY,
    'Content-Type': 'application/json'
}

file_name = "korean_food_list.txt"

print("🚀 텍스트 레시피 전용 글로벌 검색 파이프라인 가동 (유튜브 배제)")
print("=" * 60)

if os.path.exists(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        if not line.strip():
            continue
            
        kr_dish, en_dish = line.strip().split(",")
        kr_dish = kr_dish.strip()
        en_dish = en_dish.strip()
        
        print(f"\n🔍 분석 중: {kr_dish} ({en_dish})")
        
        # 1. 검색어 고도화: 유튜브 배제(-site) 및 'ingredients' 키워드 추가
        query_open_search = f"{en_dish} {kr_dish} Korean recipe ingredients -site:youtube.com -site:youtu.be"
        
        # 2. 혹시 모를 상황을 대비해 상위 3개 결과를 가져옵니다.
        payload = json.dumps({"q": query_open_search, "num": 3}) 
        
        try:
            response = requests.post(SERPER_URL, headers=headers, data=payload)
            results = response.json()
            
            valid_match = None
            
            # 3. 파이썬 문지기 로직: 상위 3개 중 동영상/이미지 사이트가 아닌 '첫 번째 텍스트 문서' 찾기
            if "organic" in results:
                for match in results["organic"]:
                    link = match.get('link', '').lower()
                    
                    # 피해야 할 블랙리스트 사이트 도메인들
                    if "youtube" not in link and "pinterest" not in link and "tiktok" not in link:
                        valid_match = match
                        break # 텍스트 사이트를 찾았으므로 즉시 검색 종료!
            
            # 유효한 텍스트 레시피를 찾았을 때의 출력
            if valid_match:
                domain = valid_match.get('link').split('/')[2]
                print(f"  🌟 [검색 성공] 텍스트 레시피 발견!")
                print(f"  🏢 출처: {domain}")
                print(f"  🔗 URL: {valid_match.get('link')}")
                print(f"  📝 제목: {valid_match.get('title')}")
            else:
                print(f"  ❌ [실패] 유효한 텍스트 레시피 웹사이트를 찾지 못했습니다.")
                
        except Exception as e:
            print(f"  ❌ API 통신 중 에러 발생 ({kr_dish}): {e}")
            
    print("\n" + "=" * 60)
    print("🎉 텍스트 문서 전용 검색 매핑이 완료되었습니다!")

else:
    print(f"❌ '{file_name}' 파일을 찾을 수 없습니다.")