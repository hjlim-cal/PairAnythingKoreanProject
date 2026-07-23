import streamlit as st
import pandas as pd
import random

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title="Seoul & Sip",
    page_icon="🍷",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. Data Loading (Cached for performance)
# ==========================================
@st.cache_data
def load_data():
    try:
        wine_df = pd.read_csv('DDI_wine_updated_FINAL.csv')
        food_df = pd.read_csv('korean_food_clusters_with_descriptions.csv')
    except FileNotFoundError:
        wine_df = pd.DataFrame({'Wine': ['Swiss Pinot Noir', 'Chasselas', 'Merlot'], 'light/bold (body)': ['Light', 'Light', 'Bold'], 'dry/sweetness': ['Dry', 'Dry', 'Dry']})
        food_df = pd.DataFrame({'food_name': ['Jeyuk-bokkeum', 'Pajeon', 'Galbijjim'], 'Spiciness_Heat': ['4', '1', '3'], 'food_description_en': ['Spicy pork', 'Pancake', 'Beef stew']})
    return wine_df, food_df

wine_data, food_data = load_data()

# ==========================================
# 3. CSS Styling (Figma Design Implementation)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;600&display=swap');
    
    /* Global App Style */
    .stApp {
        background-color: #1a0515 !important;
        color: #ffffff !important;
    }
    header, footer, #MainMenu { visibility: hidden; }

    /* Typography */
    .app-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        color: #ffffff;
        margin-bottom: 2rem;
    }
    .question-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 400;
        text-align: left;
        color: #ffffff;
        margin-top: 1rem;
        margin-bottom: 2rem;
        line-height: 1.4;
    }
    .kicker {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #8c6b79;
        margin-bottom: 0.5rem;
    }

    /* Default Option Button Style */
    div.stButton > button {
        background-color: #2a1123 !important;
        color: #e6dfdec7 !important;
        border: 1px solid #422039 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        width: 100% !important;
        font-family: 'Lora', serif !important;
        font-size: 1rem !important;
        text-align: left !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border-color: #a6324f !important;
        background-color: #381830 !important;
        color: #ffffff !important;
    }

    /* Back Button Style (Perfect Circle) */
    .nav-back-btn div.stButton > button {
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        min-height: 44px !important;
        padding: 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        border: 1px solid #422039 !important;
    }

    /* Primary Action Button & Selected Option Highlight */
    div.stButton > button[kind="primary"] {
        background-color: #8c1c3f !important;
        color: #ffffff !important;
        text-align: center !important;
        font-weight: bold !important;
        border: none !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #a6264f !important;
    }

    /* Result Card Placeholder */
    .result-card {
        background-color: #260d20;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #3d1b34;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# 4. Session State & Routing Logic
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
if 'answers' not in st.session_state:
    st.session_state.answers = {}

def move_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def render_nav(prev_page=None):
    cols = st.columns([1, 8, 1])
    with cols[0]:
        if prev_page:
            st.markdown('<div class="nav-back-btn">', unsafe_allow_html=True)
            if st.button("←", key=f"back_{prev_page}"):
                move_to(prev_page)
            st.markdown('</div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown("<div style='text-align:center; font-family:\"Playfair Display\", serif; font-size:1.3rem; letter-spacing:0.05em;'>Seoul & Sip</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0.5rem; margin-bottom:1.5rem; border-color:#3d1b34;'>", unsafe_allow_html=True)

# ==========================================
# 5. Core Matching Logic (Real Filter)
# ==========================================
def get_matching_result(answers):
    f_df = food_data.copy()
    w_df = wine_data.copy()

    # --- [1] 한식 필터링 (Spice Tolerance) ---
    spice = answers.get('q4', 'A')
    if spice == 'A':   
        f_df = f_df[f_df['Spiciness_Heat'].astype(str).str.contains('Mild|Low|0|1|2', case=False, na=False)]
    elif spice == 'B': 
        f_df = f_df[f_df['Spiciness_Heat'].astype(str).str.contains('Medium|2|3', case=False, na=False)]
    elif spice == 'C': 
        f_df = f_df[f_df['Spiciness_Heat'].astype(str).str.contains('Hot|High|Spicy|3|4|5', case=False, na=False)]

    # --- [2] Diet 필터 보정 (Ocean vibes only 완벽 차단) ---
    diet = answers.get('q2', 'C')
    if diet == 'A': # Vegetarian  
        f_df = f_df[~f_df['food_description_en'].astype(str).str.contains('meat|pork|beef|chicken|seafood|fish|sausage|blood', case=False, na=False)]
    
    elif diet == 'B': # Pescatarian (Ocean vibes only)
        # 1. 육류 완전 차단 (sausage, blood, pork, beef, chicken, meat 제거)
        f_df = f_df[~f_df['food_description_en'].astype(str).str.contains('meat|pork|beef|chicken|sausage|blood|ribs', case=False, na=False)]
        # 2. 반드시 해산물 키워드가 포함된 요리만 선택 (낙지, 아구찜, 게장, 해물탕 등)
        seafood_matches = f_df['food_description_en'].astype(str).str.contains('seafood|fish|squid|octopus|crab|shrimp|monkfish|mackerel|beltfish', case=False, na=False)
        
        # 해산물 요리가 존재하면 필터링 적용, 데이터 부족으로 비어버릴 때만 전체 폴백
        if seafood_matches.any():
            f_df = f_df[seafood_matches]

    if f_df.empty: 
        f_df = food_data

    matched_food = f_df.sample(1).iloc[0]

    # --- [3] 와인 필터링 ---
    palate = answers.get('q1', 'B')
    if palate == 'A':   
        w_df = w_df[w_df['light/bold (body)'].astype(str).str.contains('Light|Medium', case=False, na=False)]
    elif palate == 'C': 
        w_df = w_df[w_df['light/bold (body)'].astype(str).str.contains('Bold|Full', case=False, na=False)]

    if spice == 'C':
        w_df = w_df[w_df['dry/sweetness'].astype(str).str.contains('Off-Dry|Sweet', case=False, na=False)]

    if w_df.empty: 
        w_df = wine_data

    matched_wine = w_df.sample(1).iloc[0]

    return matched_wine, matched_food

# ==========================================
# 6. Page Rendering Functions
# ==========================================

def render_intro():
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='app-title'>Seoul<br>& Sip</div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; font-size:1.4rem; font-weight:400; margin-bottom:2rem;'>The Wine Questionnaire</h3>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align:center; font-family:"Lora", serif; font-size:0.95rem; color:#b3a1ab; line-height:1.6; margin-bottom:3rem;'>
        Four questions. Endless possibilities.<br>
        Your perfect bottle and Korean pairing<br>
        wait at the end of the scene.
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("FIND MY MATCH", type="primary", use_container_width=True):
        move_to('q1')

def render_q1():
    render_nav(prev_page='intro')
    st.progress(0.25) 
    st.markdown("<div class='kicker'>WINE PALATE</div>", unsafe_allow_html=True)
    st.markdown("<div class='question-title'>What's your wine backstory?</div>", unsafe_allow_html=True)
    
    # 현재 선택된 답이 있는지 확인
    q1_ans = st.session_state.answers.get('q1', None)
    
    # 선택된 버튼만 버건디 색상(primary)으로 렌더링
    if st.button("A  🍇  Just starting my wine journey.", type="primary" if q1_ans == 'A' else "secondary", use_container_width=True):
        st.session_state.answers['q1'] = 'A'
        st.rerun()
    if st.button("B  🍷  I know what I like. Keep it classic.", type="primary" if q1_ans == 'B' else "secondary", use_container_width=True):
        st.session_state.answers['q1'] = 'B'
        st.rerun()
    if st.button("C  🗺️  An adventurous enthusiast.", type="primary" if q1_ans == 'C' else "secondary", use_container_width=True):
        st.session_state.answers['q1'] = 'C'
        st.rerun()
        
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("CONTINUE", key="next_q1", use_container_width=True):
        if q1_ans: # 선택이 되었을 때만 다음 페이지로 이동
            move_to('q2')
        else:
            st.toast("⚠️ Please select an option first!")

def render_q2():
    render_nav(prev_page='q1')
    st.progress(0.50) 
    st.markdown("<div class='kicker'>DIETARY NOTE</div>", unsafe_allow_html=True)
    st.markdown("<div class='question-title'>Any specific dietary preferences for tonight's menu?</div>", unsafe_allow_html=True)
    
    q2_ans = st.session_state.answers.get('q2', None)
    
    if st.button("A  🌿  Keep it green. I'm a vegetarian / plant-based.", type="primary" if q2_ans == 'A' else "secondary", use_container_width=True):
        st.session_state.answers['q2'] = 'A'
        st.rerun()
    if st.button("B  🦐  Ocean vibes only. (Pescatarian)", type="primary" if q2_ans == 'B' else "secondary", use_container_width=True):
        st.session_state.answers['q2'] = 'B'
        st.rerun()
    if st.button("C  🥩  I eat everything. Bring on the meat and seafood!", type="primary" if q2_ans == 'C' else "secondary", use_container_width=True):
        st.session_state.answers['q2'] = 'C'
        st.rerun()
        
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("CONTINUE", key="next_q2", use_container_width=True):
        if q2_ans:
            move_to('q3')
        else:
            st.toast("⚠️ Please select an option first!")

def render_q3():
    render_nav(prev_page='q2')
    st.progress(0.75)
    st.markdown("<div class='kicker'>THE OCCASION</div>", unsafe_allow_html=True)
    st.markdown("<div class='question-title'>What's the vibe for tonight's scene?</div>", unsafe_allow_html=True)
    
    q3_ans = st.session_state.answers.get('q3', None)
    
    if st.button("A  🎬  A quiet night, a glass of wine, and the lead role in my own film.", type="primary" if q3_ans == 'A' else "secondary", use_container_width=True):
        st.session_state.answers['q3'] = 'A'
        st.rerun()
    if st.button("B  🥂  Gathering with my favorite co-stars for a night to remember.", type="primary" if q3_ans == 'B' else "secondary", use_container_width=True):
        st.session_state.answers['q3'] = 'B'
        st.rerun()
    if st.button("C  🍽️  A blockbuster family feast, where everyone is a main character.", type="primary" if q3_ans == 'C' else "secondary", use_container_width=True):
        st.session_state.answers['q3'] = 'C'
        st.rerun()
        
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("CONTINUE", key="next_q3", use_container_width=True):
        if q3_ans:
            move_to('q4')
        else:
            st.toast("⚠️ Please select an option first!")

def render_q4():
    render_nav(prev_page='q3')
    st.progress(1.0)
    st.markdown("<div class='kicker'>SPICE TOLERANCE</div>", unsafe_allow_html=True)
    st.markdown("<div class='question-title'>How much heat can your character handle?</div>", unsafe_allow_html=True)
    
    q4_ans = st.session_state.answers.get('q4', None)
    
    if st.button("A  🍦  Keep it mild. No spice for me, please.", type="primary" if q4_ans == 'A' else "secondary", use_container_width=True):
        st.session_state.answers['q4'] = 'A'
        st.rerun()
    if st.button("B  🌶️  Medium spice. Ready for a little kick.", type="primary" if q4_ans == 'B' else "secondary", use_container_width=True):
        st.session_state.answers['q4'] = 'B'
        st.rerun()
    if st.button("C  🔥  I can handle the heat! Bring on the authentic K-spice.", type="primary" if q4_ans == 'C' else "secondary", use_container_width=True):
        st.session_state.answers['q4'] = 'C'
        st.rerun()
        
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("SEE MY PAIRING", key="to_result", use_container_width=True):
        if q4_ans:
            move_to('result')
        else:
            st.toast("⚠️ Please select an option first!")

def render_result():
    st.markdown("<div style='text-align:center; font-family:\"Playfair Display\", serif; font-size:1.5rem; margin-bottom:0.5rem;'>Seoul & Sip</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1.8rem; font-weight:700; margin-bottom:2rem;'>Your Perfect Pairing</h2>", unsafe_allow_html=True)
    
    matched_wine, matched_food = get_matching_result(st.session_state.answers)
    wine_name = matched_wine['Wine']
    
    wine_name = matched_wine['Wine']
    
    # 1. 와인 타입(1, 2, 3, 4)별 고화질 대표 이미지 딕셔너리 세팅
    wine_type_images = {
        # 📍 [1.white]
        1: "https://images.pexels.com/photos/1123260/pexels-photo-1123260.jpeg?auto=compress&cs=tinysrgb&w=600", 
        
        # 📍 [2. rose]
        2: "https://images.unsplash.com/photo-1558001373-7b93ee48ffa0?auto=format&fit=crop&w=600&q=80", 
        
        # 📍 [3. red] 
        3: "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=600&q=80", 
        
        # 📍 [4. bubbly] 
        4: "https://images.unsplash.com/photo-1613477581402-306fa9dc6b95?q=80&w=774&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    }
    
    # 2. DB에서 wine_type 숫자를 가져와 이미지 매핑 (문자열 형태일 경우 대비 int 변환)
    try:
        raw_type = matched_wine.get('wine_type', 3)
        wine_type_id = int(raw_type) if not pd.isna(raw_type) else 3
    except (ValueError, TypeError):
        wine_type_id = 3 # 예외 시 기본값 레드
        
    # 3. 태그 숫자에 맞는 이미지 URL 할당 (없는 숫자일 경우 기본 3번 레드 적용)
    generated_img_url = wine_type_images.get(wine_type_id, wine_type_images[3])
    
 # 변수 선언 (와인 & 한식)
    wine_name = matched_wine['Wine']
    food_en = matched_food['food_name_en']
    food_kr = matched_food['food_name']
            
    winery_name = matched_wine.get('winery', '')
    winery_display = str(winery_name).upper() if not pd.isna(winery_name) and str(winery_name) != 'nan' else ''

    col1, col2 = st.columns(2)
    
    with col1:
        # 🍷 와인 카드 (Streamlit이 코드 블록으로 인식하지 못하도록 왼쪽 여백을 0으로 밀착)
        html_col1 = f"""<div class="result-card" style="min-height: 380px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 15px; border-radius: 12px; background-color: #1e131d;">
<div style="width: 100%; border-radius: 8px; overflow: hidden; margin-bottom: 15px;">
<img src="{generated_img_url}" style="width: 100%; object-fit: cover; aspect-ratio: 4/3; display: block; border-radius: 8px;" />
</div>
<div style="text-align: center; margin-top: auto; padding-bottom: 10px;">
<div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.5px;">{wine_name}</div>
<div style="font-size: 0.85rem; font-style: italic; color: #b3a1ab; margin-top: 4px; text-transform: uppercase;">{winery_display}</div>
</div>
</div>"""
        st.markdown(html_col1, unsafe_allow_html=True)
        
    with col2:
        # 🍳 한식 카드
        html_col2 = f"""<div class="result-card" style="min-height: 380px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 15px; border-radius: 12px; background-color: #1e131d;">
<div style="font-size: 4rem; display: flex; align-items: center; justify-content: center; flex-grow: 1;">🍳</div>
<div style="text-align: center; padding-bottom: 10px;">
<div style="font-size: 1.1rem; font-weight: bold; color: #FFFFFF;">{food_en}</div>
<div style="font-size: 0.85rem; color: #b3a1ab; margin-top: 4px;">{food_kr}</div>
</div>
</div>"""
        st.markdown(html_col2, unsafe_allow_html=True)
    # 1. 와인 데이터베이스의 데이터 안전하게 처리
    wine_name = matched_wine['Wine']
    
    # wine_type이 숫자로 나오면 'wine'으로 안전하게 대체
    wine_type = str(matched_wine.get('wine_type', 'wine'))
    if wine_type.isdigit() or wine_type == '3' or wine_type == 'nan':
        wine_type = 'wine'

    # 2. key flavors 데이터 정제
    key_flavors = matched_wine.get('key flavors', '')
    if pd.isna(key_flavors) or key_flavors == '':
        flavor_str = "its beautifully balanced structure"
    else:
        flavor_str = f"its distinct notes of {str(key_flavors).lower()}"

    # 3. pairing_notes 데이터 분석 및 가독성 업그레이드
    pairing_notes = matched_wine.get('pairing_notes', '')
    
    if not pd.isna(pairing_notes) and pairing_notes != '':
        # 만약 콤마로 연결된 음식 리스트라면 자연스러운 텍스트로 변환
        if ',' in str(pairing_notes):
            # 콤마 기준 상위 3개 어울리는 서양 요리만 예시로 추출
            western_dishes = ", ".join([d.strip() for d in str(pairing_notes).split(',')[:3]])
            rationale_text = (
                f"While <b>{wine_name}</b> is traditionally celebrated alongside dishes like {western_dishes}, "
                f"this {wine_type} reveals a spectacular new dimension when paired with Korean cuisine. "
                f"The flavor profile, enriched by {flavor_str}, seamlessly bridges the gap to create a beautiful harmony with <b>{food_en}</b>."
            )
        else:
            # 텍스트 설명글 형태인 경우
            rationale_text = f"This pairing shines because this exceptional {wine_type} elevates the dining experience. Specifically, {pairing_notes}"
    else:
        # 데이터가 아예 없을 경우 폴백 문장
        rationale_text = (
            f"This pairing works beautifully because the unique character of <b>{wine_name}</b>, "
            f"driven by {flavor_str}, harmonizes gracefully with the seasoned elements of <b>{food_en}</b>, "
            f"creating a delightful balance on the palate."
        )

    # 4. 스트림릿 UI 화면에 반영
    st.markdown(f"""
        <div style='background-color:#260d20; border: 1px solid #3d1b34; border-radius:12px; padding:1.5rem; font-family:"Lora", serif; font-size:0.95rem; line-height:1.6;'>
        {rationale_text}
        <br><br>
        <span style='color:#b3a1ab; font-size:0.85rem;'>Dish details: {matched_food['food_description_en']}</span>
        </div>
    """, unsafe_allow_html=True)
    
    
    
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("EMAIL MY PAIRING", type="primary", use_container_width=True):
            st.toast("📧 Email feature coming soon!")
            
    with col_btn2:
        if st.button("START OVER", use_container_width=True):
            st.session_state.answers = {}
            move_to('intro')

# ==========================================
# 7. Router
# ==========================================
if st.session_state.page == 'intro':
    render_intro()
elif st.session_state.page == 'q1':
    render_q1()
elif st.session_state.page == 'q2':
    render_q2()
elif st.session_state.page == 'q3':
    render_q3()
elif st.session_state.page == 'q4':
    render_q4()
elif st.session_state.page == 'result':
    render_result()