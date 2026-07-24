import streamlit as st
import pandas as pd
import random
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import mimetypes
from email.mime.image import MIMEImage


APP_DIR = Path(__file__).resolve().parent
IMAGE_DIR = APP_DIR / "static" / "images"

st.markdown("""
    <style>
    /* 1. remove margin on top */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    

    /* 2. back button fix to round shape */

    /* circle 42by42 */
    .st-key-nav_back_button button {
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        max-width: 42px !important;
        min-height: 42px !important;
        max-height: 42px !important;

        padding: 0 !important;
        border-radius: 50% !important;

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;

        line-height: 1 !important;
    }

    /* 
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) div.stButton > button {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        max-width: 42px !important;
        min-height: 42px !important;
        max-height: 42px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    */

    </style>
""", unsafe_allow_html=True)

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
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..700;1,400..700&family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..900;1,6..96,400..900&display=swap');
    
    .brand-logo {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        line-height: 1.1;
        text-align: center;
        color: rgba(255, 211, 211, 0.6); 
        letter-spacing: -0.5px;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-family: 'Bodoni Moda', 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 600;
        text-align: center;
        color: #FFFFFF;
        letter-spacing: -0.3px;
        margin-bottom: 1.5rem;
    }
    /* Global App Style */
    .stApp {
        background-color: #1a0515 !important;
        color: #ffffff !important;
    }
    header, footer, #MainMenu { visibility: hidden; }

    /* Typography */
    .app-title {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        color: #ffffff;
        margin-bottom: 2rem;
    }
    .question-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
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

    /* Clean Custom Progress Bar Styling */
    .custom-progress-track {
        width: 100%;
        background-color: #4E1A3E; /* Dark background bar */
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .custom-progress-fill {
        height: 100%;
        background-color: #AA8EA7; /* Light active progress bar */
        border-radius: 10px;
        transition: width 0.3s ease-in-out;
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

    /* Quiz options only*/
    div[class*="st-key-quiz_options_"] div.stButton > button {
        justify-content: flex-start !important;
        text-align: left !important;
    }

    /* Streamlit button label */
    div[class*="st-key-quiz_options_"]
    div.stButton > button
    div[data-testid="stMarkdownContainer"] {
        width: 100% !important;
        text-align: left !important;
    }

    div[class*="st-key-quiz_options_"]
    div.stButton > button p {
        width: 100% !important;
        margin: 0 !important;
        text-align: left !important;
        white-space: normal !important;
        overflow-wrap: break-word !important;
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


def send_pairing_email(receiver_email, matched_wine, matched_food, rationale_text):
    """Sends a clean burgundy-bordered email matching the app's light theme."""
    sender_email = st.secrets["GMAIL_SENDER"]
    app_password = st.secrets["GMAIL_APP_PASSWORD"]  
    
    subject = "[Seoul & Sip] Your Personalized K-Food & Wine Pairing Result 🍷"
    
    # Safely extract wine details
    wine_name = matched_wine.get('Wine', 'Selected Wine')
    winery_name = str(matched_wine.get('winery', '')).upper()
    if winery_name == 'NAN' or not winery_name:
        winery_name = ""
        
    # Extract wine link from 'info_url_x' column with Google Search fallback
    wine_link = matched_wine.get('info_url_x', '#')
    if pd.isna(wine_link) or str(wine_link).strip() == '' or str(wine_link) == 'nan':
        wine_link = "https://www.google.com/search?q=" + wine_name.replace(" ", "+")

    # Safely extract food details
    food_en = matched_food.get('food_name_en', matched_food.get('food_name', 'Korean Dish'))
    food_kr = matched_food.get('food_name', '')
    dish_details = matched_food.get('food_description_en', '')

    # Food Image URL extraction 
    # Food image file for email
    food_filename = matched_food.get("image_file")

    if pd.isna(food_filename) or not str(food_filename).strip():
        food_filename = matched_food.get("food_image_file")

    food_image_path = None

    if food_filename is not None and not pd.isna(food_filename):
        food_filename = str(food_filename).strip()
        food_image_path = IMAGE_DIR / food_filename

    # Wine Image URL Logic
    wine_type_images = {
        1: "https://images.pexels.com/photos/1123260/pexels-photo-1123260.jpeg?auto=compress&cs=tinysrgb&w=600",
        2: "https://images.unsplash.com/photo-1558001373-7b93ee48ffa0?auto=format&fit=crop&w=600&q=80",
        3: "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=600&q=80",
        4: "https://images.unsplash.com/photo-1613477581402-306fa9dc6b95?q=80&w=774&auto=format&fit=crop"
    }
    try:
        raw_type = matched_wine.get('wine_type', 3)
        wine_type_id = int(raw_type) if not pd.isna(raw_type) else 3
    except (ValueError, TypeError):
        wine_type_id = 3
    wine_img_url = wine_type_images.get(wine_type_id, wine_type_images[3])

    # HTML Email Template
    html_body = f"""
    <html>
    <body style="background-color: #f7f7f7; font-family: 'Helvetica Neue', Arial, sans-serif; padding: 30px 10px; margin: 0;">
        <div style="max-width: 580px; margin: auto; background-color: #ffffff; border-radius: 20px; border: 2px solid #6b1f4a; padding: 40px 30px; box-sizing: border-box;">
            
            <!-- Logo Header -->
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-family: Georgia, serif; font-size: 32px; font-weight: bold; color: #6b1f4a; line-height: 1.1;">
                    Seoul<br>&amp; Sip
                </div>
            </div>
            
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin-bottom: 30px;">
            
            <div style="text-align: center; font-family: Georgia, serif; font-size: 22px; font-weight: bold; color: #111111; margin-bottom: 25px;">
                Your Perfect Pairing
            </div>

            <!-- Cards Container -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 25px;">
                <tr>
                    <!-- Wine Card -->
                    <td width="48%" valign="top" style="background-color: transparent; border: 1.5px solid #6b1f4a; border-radius: 12px; padding: 12px; text-align: center;">
                        <img src="{wine_img_url}" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; display: block; margin-bottom: 12px;">
                        <div style="font-size: 13px; font-weight: bold; color: #111111; text-transform: uppercase; margin-bottom: 4px;">{wine_name}</div>
                        <div style="font-size: 11px; font-style: italic; color: #555555; text-transform: uppercase;">{winery_name}</div>
                    </td>
                    <td width="4%"></td>
                    <!-- Food Card -->
                    <td width="48%" valign="top" style="background-color: transparent; border: 1.5px solid #6b1f4a; border-radius: 12px; padding: 12px; text-align: center;">
                        <img src="cid:food_image" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; display: block; margin-bottom: 12px;">
                        <div style="font-size: 13px; font-weight: bold; color: #111111; margin-bottom: 4px;">{food_en}</div>
                        <div style="font-size: 11px; color: #555555;">{food_kr}</div>
                    </td>
                </tr>
            </table>

            <!-- Rationale Box -->
            <div style="background-color: transparent; border: 1.5px solid #6b1f4a; border-radius: 12px; padding: 20px; color: #111111; font-family: Georgia, serif; font-size: 13px; line-height: 1.6; margin-bottom: 25px;">
                {rationale_text}
                <br><br>
                <span style="color: #555555; font-size: 11px; font-family: Arial, sans-serif;">Dish details: {dish_details}</span>
            </div>

            <!-- Wine Link CTA Button -->
            <div style="text-align: center; margin-bottom: 35px;">
                <a href="{wine_link}" target="_blank" style="background-color: #6b1f4a; color: #ffffff; padding: 14px 28px; border-radius: 8px; font-weight: bold; font-size: 14px; text-decoration: none; display: inline-block;">
                    🍷 VIEW &amp; BUY THIS WINE
                </a>
            </div>

            <hr style="border: none; border-top: 1px solid #e0e0e0; margin-bottom: 20px;">

            <!-- Footer -->
            <div style="text-align: center; font-size: 12px; color: #777777;">
                © Pair Anything All rights reserved.
            </div>
            
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"Seoul & Sip <{sender_email}>"
    msg["To"] = receiver_email

    # HTML body
    html_part = MIMEMultipart("alternative")
    html_part.attach(MIMEText(html_body, "html"))
    msg.attach(html_part)

    # Attach the selected food image
    if food_image_path and food_image_path.is_file():
        with open(food_image_path, "rb") as image_file:
            food_image = MIMEImage(image_file.read())

        food_image.add_header("Content-ID", "<food_image>")
        food_image.add_header(
            "Content-Disposition",
            "inline",
            filename=food_image_path.name
        )

        msg.attach(food_image)
    else:
        print(
            f"[EMAIL IMAGE ERROR] Food image not found: "
            f"{food_image_path}"
        )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def render_nav(prev_page=None):
    """Renders top navigation header with a perfectly circular back button and centered logo."""

    cols = st.columns([1, 8, 1])

    with cols[0]:
        if prev_page:
            with st.container(key="nav_back_button"):
                if st.button(
                    "←",
                    key=f"back_{prev_page}",
                    width=42
                ):
                    move_to(prev_page)

    with cols[1]:
        st.markdown(
            '<div class="brand-logo" '
            'style="margin-bottom:0; margin-top:0; padding-top:0; '
            'font-size:2.1rem; text-align:center;">'
            'Seoul<br>& Sip</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        "<hr style='margin-top:0.5rem; margin-bottom:1.5rem; "
        "border-color:#3d1b34;'>",
        unsafe_allow_html=True
    )
# ==========================================
# 5. Core Matching Logic (Real Filter)
# ==========================================
def get_matching_result(answers):
    f_df = food_data.copy()
    w_df = wine_data.copy()

    # --- [1] filter (Spice Tolerance) ---
    spice = answers.get('q4', 'A')
    if spice == 'A':   
        f_df = f_df[f_df['Spiciness_Heat'].astype(str).str.contains('Mild|Low|0|1|2', case=False, na=False)]
    elif spice == 'B': 
        f_df = f_df[f_df['Spiciness_Heat'].astype(str).str.contains('Medium|2|3', case=False, na=False)]
    elif spice == 'C': 
        f_df = f_df[f_df['Spiciness_Heat'].astype(str).str.contains('Hot|High|Spicy|3|4|5', case=False, na=False)]

    # --- [2] Diet filter (block Ocean vibes only) ---
    diet = answers.get('q2', 'C')
    if diet == 'A': # Vegetarian  
        f_df = f_df[~f_df['food_description_en'].astype(str).str.contains('meat|pork|beef|chicken|seafood|fish|sausage|blood', case=False, na=False)]
    
    elif diet == 'B': # Pescatarian (Ocean vibes only)
        # 1. no meats (no sausage, blood, pork, beef, chicken, meat )
        f_df = f_df[~f_df['food_description_en'].astype(str).str.contains('meat|pork|beef|chicken|sausage|blood|ribs', case=False, na=False)]
        # 2. must contain seafood (octopus, agujjim etc)
        seafood_matches = f_df['food_description_en'].astype(str).str.contains('seafood|fish|squid|octopus|crab|shrimp|monkfish|mackerel|beltfish', case=False, na=False)
        
        # Apply seafood filtering if matching items exist; fallback to full dataset if empty to prevent zero results
        if seafood_matches.any():
            f_df = f_df[seafood_matches]

    if f_df.empty: 
        f_df = food_data

    matched_food = f_df.sample(1).iloc[0]

    # --- [3] wine filtering ---
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
    # Subtle "Seoul & Sip" logo header with opacity styling
    st.markdown('<div class="brand-logo">Seoul<br>& Sip</div>', unsafe_allow_html=True)
    
    # Elegant serif main title
    st.markdown('<div class="main-title">The Wine Questionnaire</div>', unsafe_allow_html=True)
    
    # Subtitle description text
    st.markdown("""
        <p style='text-align: center; color: #b3a1ab; font-family: "Lora", serif; font-size: 1rem; line-height: 1.6; margin-bottom: 2.5rem;'>
            Four questions. Endless possibilities.<br>
            Your perfect bottle and Korean pairing wait at the end of the scene.
        </p>
    """, unsafe_allow_html=True)
    
    # Primary CTA button to start the questionnaire
    if st.button("FIND MY MATCH", type="primary", use_container_width=True):
        move_to('q1')
# Helper function to render a single-layer custom progress bar
def render_custom_progress(percent):
    """Renders a clean custom progress bar without Streamlit's default double-layer issue."""
    st.markdown(f"""
        <div class="custom-progress-track">
            <div class="custom-progress-fill" style="width: {percent}%;"></div>
        </div>
    """, unsafe_allow_html=True)


def render_q1():
    render_nav(prev_page='intro')
    render_custom_progress(25) 
    st.markdown("<div class='kicker'>WINE PALATE</div>", unsafe_allow_html=True)
    st.markdown("<div class='question-title'>What's your wine backstory?</div>", unsafe_allow_html=True)
    
    # check if there's selected answer
    q1_ans = st.session_state.answers.get('q1', None)
    
    # change color darker when selected
    with st.container(key="quiz_options_q1"):
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
        if q1_ans: # move to next page only when an answer selected
            move_to('q2')
        else:
            st.toast("⚠️ Please select an option first!")

def render_q2():

    render_nav(prev_page='q1')
    render_custom_progress(50) 
    st.markdown("<div class='kicker'>DIETARY NOTE</div>", unsafe_allow_html=True)
    st.markdown("<div class='question-title'>Any specific dietary preferences for tonight's menu?</div>", unsafe_allow_html=True)
    
    q2_ans = st.session_state.answers.get('q2', None)

    with st.container(key="quiz_options_q2"):
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
    render_custom_progress(75)
    st.markdown("<div class='kicker'>THE OCCASION</div>", unsafe_allow_html=True)
    st.markdown("<div class='question-title'>What's the vibe for tonight's scene?</div>", unsafe_allow_html=True)
    
    q3_ans = st.session_state.answers.get('q3', None)

    with st.container(key="quiz_options_q3"):
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
    
    # Render custom single-layer progress bar (100% for Question 4)
    render_custom_progress(100)
    
    # Question Header
    st.markdown("<div class='kicker'>SPICE TOLERANCE</div>", unsafe_allow_html=True)
    st.markdown("<div class='question-title'>How much heat can your character handle?</div>", unsafe_allow_html=True)
    
    # Retrieve existing answer for Q4 if previously selected
    q4_ans = st.session_state.answers.get('q4', None)
    
    # Option A: Only save answer on click and trigger UI refresh to highlight selection
    with st.container(key="quiz_options_q4"):
        if st.button("A  🍦  Keep it mild. No spice for me, please.", type="primary" if q4_ans == 'A' else "secondary", use_container_width=True):
            st.session_state.answers['q4'] = 'A'
            st.rerun()
            
        # Option B: Only save answer on click
        if st.button("B  🌶️  Medium spice. Ready for a little kick.", type="primary" if q4_ans == 'B' else "secondary", use_container_width=True):
            st.session_state.answers['q4'] = 'B'
            st.rerun()
            
        # Option C: Only save answer on click
        if st.button("C  🔥  I can handle the heat! Bring on the authentic K-spice.", type="primary" if q4_ans == 'C' else "secondary", use_container_width=True):
            st.session_state.answers['q4'] = 'C'
            st.rerun()

    # Spacing before CTA landing button
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # Landing CTA Button: Only active/visible after an option is selected
    if st.button("SEE MY PAIRING 🍷", type="primary", use_container_width=True):
        if not q4_ans:
            st.warning("Please select an option first!")
        else:
            # Clear previous wine session state to ensure fresh recommendation logic
            if 'matched_wine' in st.session_state:
                del st.session_state.matched_wine
            move_to('result')

def get_image_base64(image_path):
    image_path = Path(image_path)

    try:
        image_bytes = image_path.read_bytes()
        mime_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
        encoded = base64.b64encode(image_bytes).decode("utf-8")

        return f"data:{mime_type};base64,{encoded}"

    except Exception as e:
        st.error(
            f"""
            Image loading failed

            filename: {image_path.name!r}

            requested path: {image_path}

            absolute path: {image_path.resolve()}

            file exists: {image_path.is_file()}

            error: {type(e).__name__}: {e}
            """
        )

        return "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=600"
    

# Custom Dialog Modal with Guaranteed Pink Warning Box (#EFB0DC)
@st.dialog(" ")
def show_email_modal():
    """Renders the custom-styled email modal with very light gray bg and forced burgundy text."""
    
    st.markdown("""
        <style>
        /* 1. 팝업 상자 배경: 아주아주아주 연한 라이트 그레이 (#F7F7F7) */
        section[data-testid="stDialog"] {
            background-color: #F7F7F7 !important;
            border-radius: 16px !important;
        }
        
        section[data-testid="stDialog"] > div {
            background-color: #F7F7F7 !important;
        }

        /* 2. 이메일 입력창: 흰색 배경 + 버건디 글씨 */
        section[data-testid="stDialog"] div[data-baseweb="input"],
        section[data-testid="stDialog"] div[data-baseweb="base-input"],
        section[data-testid="stDialog"] input {
            background-color: #FFFFFF !important;
            color: #4E1A3E !important;
            border: 1px solid #CCCCCC !important;
            border-radius: 8px !important;
            -webkit-text-fill-color: #4E1A3E !important;
        }

        section[data-testid="stDialog"] input::placeholder {
            color: #888888 !important;
            -webkit-text-fill-color: #888888 !important;
            opacity: 1 !important;
        }

        /* 3. SEND RESULT 버튼: 버건디 배경 + 순백색 글씨 */
        section[data-testid="stDialog"] div[data-testid="stButton"] > button {
            background-color: #6B1F4A !important;
            border-color: #6B1F4A !important;
            border-radius: 8px !important;
        }

        /* 버튼 안의 텍스트는 무조건 하얗게! */
        section[data-testid="stDialog"] div[data-testid="stButton"] > button * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
        }

        /* 4. 닫기(X) 버튼 다크 버건디색 */
        section[data-testid="stDialog"] button[aria-label="Close"] svg,
        section[data-testid="stDialog"] button[aria-label="Close"] span,
        section[data-testid="stDialog"] button[aria-label="Close"] {
            color: #4E1A3E !important;
            fill: #4E1A3E !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🎯 여기서부터 글씨 색상을 다크 버건디(#4E1A3E)로 "강제 고정" 합니다.
    # ---------------------------------------------------------
    
    # 팝업 제목 및 설명 (강제 버건디)
    st.markdown("""
        <div style="text-align: center; padding-top: 0px;">
            <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 2.2rem; font-weight: bold; color: #4E1A3E !important; -webkit-text-fill-color: #4E1A3E !important; line-height: 1.1; margin-bottom: 1.2rem;">
                Seoul<br>&amp; Sip
            </div>
            <p style="color: #4E1A3E !important; -webkit-text-fill-color: #4E1A3E !important; font-size: 0.95rem; margin-bottom: 1.5rem; line-height: 1.4;">
                Enter your email to get your personalized<br>pairing results.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 이메일 입력
    user_email = st.text_input("EMAIL", placeholder="yourname@email.com", label_visibility="collapsed")
    
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    
    # 전송 버튼 로직
    if st.button("SEND RESULT", use_container_width=True, type="primary"):
        if user_email:
            st.session_state.email_error = False
            
            matched_wine = st.session_state.get('matched_wine', {})
            matched_food = st.session_state.get('matched_food', {})
            rationale_text = st.session_state.get('rationale_text', '')
            
            with st.spinner("Sending email..."):
                success = send_pairing_email(user_email, matched_wine, matched_food, rationale_text)
                
            if success:
                st.success("Results sent to your inbox!")
                import time
                time.sleep(1.5)  
                st.rerun()       
            else:
                st.error("Failed to send email. Please check your address.")
        else:
            st.session_state.email_error = True
            
    # 에러 메시지 팝업
    if st.session_state.get('email_error', False):
        st.markdown("""
            <div style="background-color: #EFB0DC; color: #4E1A3E; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; font-weight: 600; margin-top: 10px; margin-bottom: 10px; text-align: left; display: flex; align-items: center; gap: 8px; border: 1px solid #D88CB8;">
                <span style="color: #4E1A3E !important; -webkit-text-fill-color: #4E1A3E !important;">⚠️</span>
                <span style="color: #4E1A3E !important; -webkit-text-fill-color: #4E1A3E !important;">Please enter your email address.</span>
            </div>
        """, unsafe_allow_html=True)
            
    # 맨 아래 프라이버시 문구 (강제 버건디)
    st.markdown("""
        <div style="text-align: center; margin-top: 15px; font-size: 0.8rem; color: #4E1A3E !important; -webkit-text-fill-color: #4E1A3E !important;">
            🔒 We respect your privacy.
        </div>
    """, unsafe_allow_html=True)

def render_result():
    # 1. Lock in pairing result ONCE in session state
    if 'matched_wine' not in st.session_state:
        matched_wine, matched_food = get_matching_result(st.session_state.answers)
        st.session_state.matched_wine = matched_wine
        st.session_state.matched_food = matched_food
    else:
        matched_wine = st.session_state.matched_wine
        matched_food = st.session_state.matched_food

    # Extract details safely
    wine_name = matched_wine['Wine']
    food_en = matched_food['food_name_en']
    food_kr = matched_food['food_name']

    # Store text summary for email delivery function
    st.session_state.pairing_result = f"Wine: {wine_name} | Pairing Dish: {food_en} ({food_kr})"

    # Subtle "Seoul & Sip" logo header
    st.markdown('<div class="brand-logo">Seoul<br>& Sip</div>', unsafe_allow_html=True)
    
    # Elegant serif main title
    st.markdown('<div class="main-title">Your Perfect Pairing</div>', unsafe_allow_html=True)
    
    # 1. Types of wine images
    wine_type_images = {
        1: "https://images.pexels.com/photos/1123260/pexels-photo-1123260.jpeg?auto=compress&cs=tinysrgb&w=600", 
        2: "https://images.unsplash.com/photo-1558001373-7b93ee48ffa0?auto=format&fit=crop&w=600&q=80", 
        3: "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=600&q=80", 
        4: "https://images.unsplash.com/photo-1613477581402-306fa9dc6b95?q=80&w=774&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    }
    
    # 2. wine_type mapping to the image
    try:
        raw_type = matched_wine.get('wine_type', 3)
        wine_type_id = int(raw_type) if not pd.isna(raw_type) else 3
    except (ValueError, TypeError):
        wine_type_id = 3 # default: red wine
        
    generated_img_url = wine_type_images.get(wine_type_id, wine_type_images[3])
            
    winery_name = matched_wine.get('winery', '')
    winery_display = str(winery_name).upper() if not pd.isna(winery_name) and str(winery_name) != 'nan' else ''

    col1, col2 = st.columns(2)
    
    with col1:
        # 🍷 Wine Card Rendering
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
        food_filename = matched_food.get("image_file")

        if pd.isna(food_filename) or not str(food_filename).strip():
            food_filename = matched_food.get("food_image_file")

        food_filename = str(food_filename).strip()

        food_img_path = IMAGE_DIR / food_filename
        food_img_src = get_image_base64(food_img_path)
        
        if not food_img_src:
            food_img_src = "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=600"

        html_col2 = f"""<div class="result-card" style="min-height: 380px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 15px; border-radius: 12px; background-color: #1e131d;">
<div style="width: 100%; border-radius: 8px; overflow: hidden; margin-bottom: 15px;">
<img src="{food_img_src}"
            style="width: 100%;
                    object-fit: cover; aspect-ratio: 4/3; display: block;
                    border-radius: 8px;" />
</div>
<div style="text-align: center; margin-top: auto; padding-bottom: 10px;">
<div style="font-size: 1.1rem; font-weight: bold; color: #FFFFFF;">{food_en}</div>
<div style="font-size: 0.85rem; color: #b3a1ab; margin-top: 4px;">{food_kr}</div>
</div>
</div>"""

        st.markdown(html_col2, unsafe_allow_html=True)

    # 1. Fallback wine_type to 'wine' if numeric or missing
    wine_type = str(matched_wine.get('wine_type', 'wine'))
    if wine_type.isdigit() or wine_type == '3' or wine_type == 'nan':
        wine_type = 'wine'

    # 2. Key flavors data
    key_flavors = matched_wine.get('key flavors', '')
    if pd.isna(key_flavors) or key_flavors == '':
        flavor_str = "its beautifully balanced structure"
    else:
        flavor_str = f"its distinct notes of {str(key_flavors).lower()}"

    # 3. Pairing notes analysis
    pairing_notes = matched_wine.get('pairing_notes', '')
    
    if not pd.isna(pairing_notes) and pairing_notes != '':
        if ',' in str(pairing_notes):
            western_dishes = ", ".join([d.strip() for d in str(pairing_notes).split(',')[:3]])
            rationale_text = (
                f"While <b>{wine_name}</b> is traditionally celebrated alongside dishes like {western_dishes}, "
                f"this {wine_type} reveals a spectacular new dimension when paired with Korean cuisine. "
                f"The flavor profile, enriched by {flavor_str}, seamlessly bridges the gap to create a beautiful harmony with <b>{food_en}</b>."
            )
        else:
            rationale_text = f"This pairing shines because this exceptional {wine_type} elevates the dining experience. Specifically, {pairing_notes}"
    else:
        rationale_text = (
            f"This pairing works beautifully because the unique character of <b>{wine_name}</b>, "
            f"driven by {flavor_str}, harmonizes gracefully with the seasoned elements of <b>{food_en}</b>, "
            f"creating a delightful balance on the palate."
        )

    # 4. Streamlit UI Explanation Card
    st.session_state.rationale_text = rationale_text

    st.markdown(f"""
        <div style='background-color:#260d20; border: 1px solid #3d1b34; border-radius:12px; padding:1.5rem; font-family:"Lora", serif; font-size:0.95rem; line-height:1.6;'>
        {rationale_text}
        <br><br>
        <span style='color:#b3a1ab; font-size:0.85rem;'>Dish details: {matched_food['food_description_en']}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Equalized 1:1 Action Buttons
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("EMAIL MY PAIRING", use_container_width=True):
            show_email_modal()
            
    with col_btn2:
        if st.button("START OVER", use_container_width=True):
            # Complete reset of saved session state for a fresh quiz start
            st.session_state.answers = {}
            if 'matched_wine' in st.session_state:
                del st.session_state.matched_wine
            if 'matched_food' in st.session_state:
                del st.session_state.matched_food
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