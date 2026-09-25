import streamlit as st
import pandas as pd
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import mimetypes
from email.mime.image import MIMEImage
import plotly.graph_objects as go


APP_DIR = Path(__file__).resolve().parent
IMAGE_DIR = APP_DIR / "static" / "images"

# PairAnything Brand Guide 2023, page 1.
# Presentation only: matching, data, image paths, routing and SMTP stay unchanged.
BRAND_COLORS = {
    "burgundy": "#951901",
    "red": "#D0011B",
    "light_gray": "#EFEFEF",
    "dark_gray": "#7D7D7D",
    "white": "#FFFFFF",
    "mineshaft": "#343434",
    "sable_beige": "#D7DECE",
    "bright_orange": "#F4A821",
    "dark_orange": "#F96331",
    "contessa": "#BB7668",
    "gray": "#7E7E7E",
    "dove_gray": "#646464",
}
BRAND_FONT = "Montserrat, Arial, sans-serif"
_brand_css_variables = "\n".join(
    f"--pa-{name.replace('_', '-')}: {value};"
    for name, value in BRAND_COLORS.items()
)

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
# 2. Data Loading 
# ==========================================
def load_data():
    wine_path = APP_DIR / 'DDI_wine_updated_FINAL.csv'
    food_path = APP_DIR / 'korean_food_clusters_with_descriptions.csv'

    # Make missing files visible instead of silently using fake fallback data
    if not wine_path.is_file():
        st.error(f"Wine data file not found: {wine_path.name}")
        st.stop()

    if not food_path.is_file():
        st.error(f"Food data file not found: {food_path.name}")
        st.stop()

    wine_df = pd.read_csv(wine_path)
    food_df = pd.read_csv(food_path)

    # Validate required columns
    required_food_cols = {
        'food_name',
        'food_name_en',
        'Spiciness_Heat',
        'is_vegetarian',
        'is_pescatarian',
        'vibe_solo',
        'vibe_friends',
        'vibe_family'
    }

    required_wine_cols = {
        'Wine',
        'dry/sweetness',
        'light/bold (body)',
        'tannins',
        'acidity'
    }

    missing_food = required_food_cols - set(food_df.columns)
    missing_wine = required_wine_cols - set(wine_df.columns)

    if missing_food:
        st.error(
            f"Food CSV is missing required columns: "
            f"{', '.join(sorted(missing_food))}"
        )
        st.stop()

    if missing_wine:
        st.error(
            f"Wine CSV is missing required columns: "
            f"{', '.join(sorted(missing_wine))}"
        )
        st.stop()

    return wine_df, food_df


wine_data, food_data = load_data()

# ==========================================
# 3. CSS Styling (PairAnything Brand Guide 2023)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,700;0,800;1,400;1,700&display=swap');

:root {
    /* BRAND_CSS_VARIABLES */
    --pa-font: 'Montserrat', Arial, sans-serif;
}

/* PairAnything Brand Guide 2023, page 1. Keep the existing page geometry. */
html, body, .stApp {
    font-family: var(--pa-font);
    background-color: var(--pa-white) !important;
    color: var(--pa-mineshaft) !important;
    color-scheme: light;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--pa-white) !important;
    color: var(--pa-mineshaft) !important;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    margin-top: 0 !important;
}
header[data-testid="stHeader"] { display: none !important; }
header, footer, #MainMenu { visibility: hidden; }
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"],
[data-testid="stCaptionContainer"], [data-testid="stText"] {
    font-family: var(--pa-font);
}
[data-testid="stWidgetLabel"], [data-testid="stText"] {
    color: var(--pa-mineshaft) !important;
}
[data-testid="stCaptionContainer"] { color: var(--pa-dove-gray) !important; }
[data-testid="stMarkdownContainer"] a:not(.wine-purchase-link) {
    color: var(--pa-burgundy);
}
::selection { background: var(--pa-sable-beige); color: var(--pa-mineshaft); }

/* Montserrat: ExtraBold headings, Bold subheadings, Regular body text. */
.brand-logo {
    font-family: var(--pa-font);
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.1;
    text-align: center;
    color: var(--pa-burgundy);
    letter-spacing: -0.5px;
    margin-bottom: 2rem;
}
.main-title {
    font-family: var(--pa-font);
    font-size: 2.2rem;
    font-weight: 800;
    text-align: center;
    color: var(--pa-mineshaft);
    letter-spacing: -0.3px;
    margin-bottom: 1.5rem;
}
.app-title {
    font-family: var(--pa-font);
    font-size: 2rem;
    font-weight: 800;
    text-align: center;
    color: var(--pa-mineshaft);
    margin-bottom: 2rem;
}
.question-title {
    font-family: var(--pa-font);
    font-size: 1.4rem;
    font-weight: 700;
    text-align: left;
    color: var(--pa-mineshaft);
    margin-top: 1rem;
    margin-bottom: 2rem;
    line-height: 1.4;
}
.kicker {
    font-family: var(--pa-font);
    font-size: 0.75rem;
    font-weight: 400;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--pa-burgundy);
    margin-bottom: 0.5rem;
}

/* Unselected options and secondary actions. */
div.stButton > button {
    background-color: var(--pa-white) !important;
    color: var(--pa-mineshaft) !important;
    border: 1px solid var(--pa-sable-beige) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    width: 100% !important;
    font-family: var(--pa-font) !important;
    font-weight: 400 !important;
    font-size: 1rem !important;
    text-align: left !important;
    transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}
div.stButton > button p {
    font-family: var(--pa-font) !important;
    color: inherit !important;
    font-weight: inherit !important;
}
div.stButton > button:hover {
    border-color: var(--pa-burgundy) !important;
    background-color: var(--pa-light-gray) !important;
    color: var(--pa-burgundy) !important;
}
div.stButton > button:focus-visible,
a.wine-purchase-link:focus-visible {
    outline: 2px solid var(--pa-burgundy) !important;
    outline-offset: 3px;
    box-shadow: none !important;
}

/* Burgundy action buttons; Red is the active/hover accent. */
div.stButton > button[kind="primary"],
.st-key-next_q1 button[kind],
.st-key-next_q2 button[kind],
.st-key-next_q3 button[kind],
.st-key-see_pairing button[kind],
.st-key-email_my_pairing button[kind] {
    background-color: var(--pa-burgundy) !important;
    border-color: var(--pa-burgundy) !important;
    color: var(--pa-white) !important;
    font-weight: 700 !important;
    text-align: center !important;
    justify-content: center !important;
}
div.stButton > button[kind="primary"]:hover,
.st-key-next_q1 button[kind]:hover,
.st-key-next_q2 button[kind]:hover,
.st-key-next_q3 button[kind]:hover,
.st-key-see_pairing button[kind]:hover,
.st-key-email_my_pairing button[kind]:hover {
    background-color: var(--pa-red) !important;
    border-color: var(--pa-red) !important;
    color: var(--pa-white) !important;
}

/* Preserve the left alignment of all quiz choices, including selected ones. */
div[class*="st-key-quiz_options_"] div.stButton > button {
    justify-content: flex-start !important;
    text-align: left !important;
}
div[class*="st-key-quiz_options_"] div.stButton > button[kind="primary"] {
    background-color: var(--pa-red) !important;
    border-color: var(--pa-red) !important;
    color: var(--pa-white) !important;
}
div[class*="st-key-quiz_options_"] div.stButton > button[kind="primary"]:hover {
    background-color: var(--pa-burgundy) !important;
    border-color: var(--pa-burgundy) !important;
}
div[class*="st-key-quiz_options_"] div.stButton > button div[data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
}
div[class*="st-key-quiz_options_"] div.stButton > button p {
    width: 100% !important;
    margin: 0 !important;
    text-align: left !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
}
div.stButton > button:disabled,
div.stButton > button:disabled:hover {
    background-color: var(--pa-light-gray) !important;
    color: var(--pa-dark-gray) !important;
    border-color: var(--pa-light-gray) !important;
    cursor: not-allowed;
}

/* The original 42 x 42 round back button and centered quiz header. */
.st-key-nav_back_button div.stButton > button {
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
    color: var(--pa-burgundy) !important;
}
.nav-logo {
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--pa-font);
    font-size: 1.45rem;
    font-weight: 700;
    line-height: 1;
    color: var(--pa-burgundy);
    text-align: center;
    margin: 0;
    padding: 0;
}
.st-key-quiz_nav div[data-testid="stHorizontalBlock"] { align-items: center; }
.custom-progress-track {
    width: 100%;
    background-color: var(--pa-light-gray);
    border-radius: 10px;
    height: 8px;
    overflow: hidden;
    margin-top: 10px;
    margin-bottom: 20px;
}
.custom-progress-fill {
    height: 100%;
    background-color: var(--pa-burgundy);
    border-radius: 10px;
    transition: width 0.3s ease-in-out;
}

/* Cards and the existing in-card purchase link. */
.result-card {
    background-color: var(--pa-light-gray);
    color: var(--pa-mineshaft);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid var(--pa-light-gray);
    text-align: center;
}
a.wine-purchase-link:hover {
    background-color: var(--pa-red) !important;
    color: var(--pa-white) !important;
}

/* Native inputs: keep text legible even if an old dark config is present. */
[data-testid="stTextInput"] label { color: var(--pa-mineshaft) !important; }
[data-testid="stTextInput"] div[data-baseweb="input"] {
    background-color: var(--pa-white) !important;
    border: 1px solid var(--pa-sable-beige) !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] div[data-baseweb="base-input"] {
    background-color: var(--pa-white) !important;
}
[data-testid="stTextInput"] input {
    background-color: var(--pa-white) !important;
    color: var(--pa-mineshaft) !important;
    -webkit-text-fill-color: var(--pa-mineshaft) !important;
    caret-color: var(--pa-burgundy);
    font-family: var(--pa-font) !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: var(--pa-dove-gray) !important;
    -webkit-text-fill-color: var(--pa-dove-gray) !important;
    opacity: 1 !important;
}
[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    border-color: var(--pa-burgundy) !important;
    box-shadow: 0 0 0 2px rgba(149, 25, 1, 0.12) !important;
}

/* Brand-colored notifications; keep the original messages and status icons. */
[data-testid="stAlert"] > div,
[data-testid="stAlert"] [data-baseweb="notification"] {
    background-color: var(--pa-light-gray) !important;
    color: var(--pa-mineshaft) !important;
    border-left: 3px solid var(--pa-burgundy) !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
    color: var(--pa-mineshaft) !important;
}
[data-testid="stAlert"] svg { color: var(--pa-burgundy) !important; }
[data-testid="stToast"] {
    background-color: var(--pa-white) !important;
    color: var(--pa-mineshaft) !important;
    border: 1px solid var(--pa-sable-beige) !important;
    font-family: var(--pa-font);
}
[data-testid="stToast"] p { color: var(--pa-mineshaft) !important; }
[data-testid="stSpinner"] { color: var(--pa-burgundy) !important; }
[data-testid="stSpinner"] i { border-right-color: var(--pa-burgundy) !important; }

/* =========================================
FIX: sticky hover/focus on mobile devices
   ========================================= */

/* Desktop: allow hover effect normally */
@media (hover: hover) and (pointer: fine) {
    div[class*="st-key-quiz_options_"]
    div.stButton > button[kind="secondary"]:hover {
        background-color: #EFEFEF !important;
        border-color: #951901 !important;
        color: #951901 !important;
    }
}

/* Mobile / touch: prevent false "selected" appearance */
@media (hover: none), (pointer: coarse) {
    div[class*="st-key-quiz_options_"]
    div.stButton > button[kind="secondary"]:hover,

    div[class*="st-key-quiz_options_"]
    div.stButton > button[kind="secondary"]:focus,

    div[class*="st-key-quiz_options_"]
    div.stButton > button[kind="secondary"]:focus-visible,

    div[class*="st-key-quiz_options_"]
    div.stButton > button[kind="secondary"]:active {
        background-color: #FFFFFF !important;
        border-color: #D7DECE !important;
        color: #343434 !important;
        box-shadow: none !important;
        outline: none !important;
    }

    div[class*="st-key-quiz_options_"]
    div.stButton > button {
        -webkit-tap-highlight-color: transparent !important;
        touch-action: manipulation;
    }
}

</style>

""".replace("/* BRAND_CSS_VARIABLES */", _brand_css_variables), unsafe_allow_html=True)
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

    # HTML Email Template (Montserrat when supported; Arial fallback)
    html_body = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="color-scheme" content="light">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,700;0,800;1,400;1,700&display=swap');
        </style>
    </head>
    <body style="background-color: {BRAND_COLORS['light_gray']}; font-family: {BRAND_FONT}; padding: 30px 10px; margin: 0;">
        <div style="max-width: 580px; margin: auto; background-color: {BRAND_COLORS['white']}; border-radius: 20px; border: 2px solid {BRAND_COLORS['burgundy']}; padding: 40px 30px; box-sizing: border-box;">
            
            <!-- Logo Header -->
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-family: {BRAND_FONT}; font-size: 32px; font-weight: 800; color: {BRAND_COLORS['burgundy']}; line-height: 1.1;">
                    Seoul<br>&amp; Sip
                </div>
            </div>
            
            <hr style="border: none; border-top: 1px solid {BRAND_COLORS['light_gray']}; margin-bottom: 30px;">
            
            <div style="text-align: center; font-family: {BRAND_FONT}; font-size: 22px; font-weight: 800; color: {BRAND_COLORS['mineshaft']}; margin-bottom: 25px;">
                Your Perfect Pairing
            </div>

            <!-- Cards Container -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 25px;">
                <tr>
                    <!-- Wine Card -->
                    <td width="48%" valign="top" style="background-color: transparent; border: 1.5px solid {BRAND_COLORS['burgundy']}; border-radius: 12px; padding: 12px; text-align: center;">
                        <img src="{wine_img_url}" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; display: block; margin-bottom: 12px;">
                        <div style="font-size: 13px; font-weight: bold; color: {BRAND_COLORS['mineshaft']}; text-transform: uppercase; margin-bottom: 4px;">{wine_name}</div>
                        <div style="font-size: 11px; font-style: italic; color: {BRAND_COLORS['dove_gray']}; text-transform: uppercase;">{winery_name}</div>
                    </td>
                    <td width="4%"></td>
                    <!-- Food Card -->
                    <td width="48%" valign="top" style="background-color: transparent; border: 1.5px solid {BRAND_COLORS['burgundy']}; border-radius: 12px; padding: 12px; text-align: center;">
                        <img src="cid:food_image" style="width: 100%; height: 140px; object-fit: cover; border-radius: 8px; display: block; margin-bottom: 12px;">
                        <div style="font-size: 13px; font-weight: bold; color: {BRAND_COLORS['mineshaft']}; margin-bottom: 4px;">{food_en}</div>
                        <div style="font-size: 11px; color: {BRAND_COLORS['dove_gray']};">{food_kr}</div>
                    </td>
                </tr>
            </table>

            <!-- Rationale Box -->
            <div style="background-color: transparent; border: 1.5px solid {BRAND_COLORS['burgundy']}; border-radius: 12px; padding: 20px; color: {BRAND_COLORS['mineshaft']}; font-family: {BRAND_FONT}; font-size: 13px; line-height: 1.6; margin-bottom: 25px;">
                {rationale_text}
                <br><br>
                <span style="color: {BRAND_COLORS['dove_gray']}; font-size: 11px; font-family: {BRAND_FONT};">Dish details: {dish_details}</span>
            </div>

            <!-- Wine Link CTA Button -->
            <div style="text-align: center; margin-bottom: 35px;">
                <a href="{wine_link}" target="_blank" style="background-color: {BRAND_COLORS['burgundy']}; color: {BRAND_COLORS['white']}; padding: 14px 28px; border-radius: 8px; font-weight: bold; font-size: 14px; text-decoration: none; display: inline-block;">
                    🍷 VIEW &amp; BUY THIS WINE
                </a>
            </div>

            <hr style="border: none; border-top: 1px solid {BRAND_COLORS['light_gray']}; margin-bottom: 20px;">

            <!-- Footer -->
            <div style="text-align: center; font-size: 12px; color: {BRAND_COLORS['dove_gray']};">
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
    """Compact navigation used only on quiz pages."""

    with st.container(key="quiz_nav"):
        cols = st.columns([1, 8, 1], gap="small")

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
                '<div class="nav-logo">Seoul &amp; Sip</div>',
                unsafe_allow_html=True
            )

# ==========================================
# 5. Core Matching Logic (Real Filter)
# ==========================================
def get_matching_result(answers):
    f_df = food_data.copy()
    w_df = wine_data.copy()

    # ==========================================
    # 0. Normalize numeric columns
    # ==========================================
    food_numeric_cols = [
        'Sweetness',
        'Acidity',
        'Saltiness',
        'Umami',
        'Spiciness_Heat',
        'Richness'
    ]

    wine_numeric_cols = [
        'dry/sweetness',
        'light/bold (body)',
        'tannins',
        'acidity'
    ]

    for col in food_numeric_cols:
        if col in f_df.columns:
            f_df[col] = pd.to_numeric(f_df[col], errors='coerce')

    for col in wine_numeric_cols:
        if col in w_df.columns:
            w_df[col] = pd.to_numeric(w_df[col], errors='coerce')

    # Keep full datasets as references for 0–1 normalization.
    # This keeps scoring consistent even after filtering.
    food_reference = f_df.copy()
    wine_reference = w_df.copy()

    # ==========================================
    # Helper: True / False CSV columns
    # ==========================================
    def bool_mask(df, column_name):
        if column_name not in df.columns:
            return pd.Series(False, index=df.index)

        series = df[column_name]

        if pd.api.types.is_bool_dtype(series):
            return series.fillna(False)

        return (
            series.astype(str)
            .str.strip()
            .str.lower()
            .eq('true')
        )

    # ==========================================
    # 1. DIETARY FILTER
    #    Hard constraint — never relax
    # ==========================================
    diet = answers.get('q2', 'C')

    if diet == 'A':
        # Vegetarian
        food_pool = f_df[
            bool_mask(f_df, 'is_vegetarian')
        ]

    elif diet == 'B':
        # "Ocean vibes only" — actual seafood dishes
        food_pool = f_df[
            bool_mask(f_df, 'is_pescatarian') &
            (
                f_df['protein_type']
                .astype(str)
                .str.strip()
                .str.lower()
                .eq('seafood')
            )
        ]

    else:
        # No dietary restriction
        food_pool = f_df.copy()

    if food_pool.empty:
        st.error(
            "No dishes matched the selected dietary preference. "
            "Please check the dietary columns in the food CSV."
        )
        st.stop()

    # ==========================================
    # 2. SPICE TOLERANCE
    # ==========================================
    spice = answers.get('q4', 'A')

    if spice == 'A':
        # Mild
        spice_pool = food_pool[
            food_pool['Spiciness_Heat'] <= 1.5
        ]

    elif spice == 'B':
        # Medium
        spice_pool = food_pool[
            (food_pool['Spiciness_Heat'] > 1.5) &
            (food_pool['Spiciness_Heat'] < 2.25)
        ]

    else:
        # Hot / authentic K-spice
        spice_pool = food_pool[
            food_pool['Spiciness_Heat'] >= 2.25
        ]

    # If the exact spice category has no candidate,
    # relax spice only — dietary restriction stays intact.
    if not spice_pool.empty:
        food_pool = spice_pool

    # ==========================================
    # 3. OCCASION / VIBE
    #    Soft preference
    # ==========================================
    vibe = answers.get('q3', 'B')

    vibe_column_map = {
        'A': 'vibe_solo',
        'B': 'vibe_friends',
        'C': 'vibe_family'
    }

    vibe_column = vibe_column_map.get(vibe)

    if vibe_column and vibe_column in food_pool.columns:
        vibe_pool = food_pool[
            bool_mask(food_pool, vibe_column)
        ]

        # Relax vibe only if no exact match exists.
        if not vibe_pool.empty:
            food_pool = vibe_pool

    # ==========================================
    # 4. WINE EXPERIENCE LEVEL
    # ==========================================
    palate = answers.get('q1', 'B')

    if palate == 'A':
        # Beginner:
        # avoid very full-bodied and highly tannic wines
        experience_pool = w_df[
            (w_df['light/bold (body)'] <= 3.0) &
            (w_df['tannins'] <= 2.5)
        ]

    elif palate == 'B':
        # Some experience:
        # broader range but avoid the most intense wines
        experience_pool = w_df[
            (w_df['light/bold (body)'] <= 4.0) &
            (w_df['tannins'] <= 3.5)
        ]

    else:
        # Adventurous / experienced
        experience_pool = w_df.copy()

    if not experience_pool.empty:
        w_df = experience_pool

    # ==========================================
    # 5. EXTRA FILTER FOR HOT FOOD
    # ==========================================
    if spice == 'C':
        spicy_wine_pool = w_df[
            (w_df['dry/sweetness'] >= 2.0) &
            (w_df['tannins'] <= 3.0)
        ]

        if not spicy_wine_pool.empty:
            w_df = spicy_wine_pool

    # ==========================================
    # 6. PAIRING SCORE HELPERS
    # ==========================================
    def normalize_value(value, reference_series):
        reference_series = pd.to_numeric(
            reference_series,
            errors='coerce'
        )

        min_val = reference_series.min()
        max_val = reference_series.max()

        if (
            pd.isna(value) or
            pd.isna(min_val) or
            pd.isna(max_val) or
            max_val == min_val
        ):
            return 0.5

        normalized = (
            (float(value) - min_val) /
            (max_val - min_val)
        )

        return max(0.0, min(1.0, normalized))

    def clamp(value):
        return max(0.0, min(1.0, value))

    # ==========================================
    # 7. FOOD × WINE PAIRING SCORE
    # ==========================================
    def calculate_pairing_score(food, wine):

        # ---------- Food ----------
        food_richness = normalize_value(
            food.get('Richness'),
            food_reference['Richness']
        )

        food_acidity = normalize_value(
            food.get('Acidity'),
            food_reference['Acidity']
        )

        food_sweetness = normalize_value(
            food.get('Sweetness'),
            food_reference['Sweetness']
        )

        food_spice = normalize_value(
            food.get('Spiciness_Heat'),
            food_reference['Spiciness_Heat']
        )

        food_umami = normalize_value(
            food.get('Umami'),
            food_reference['Umami']
        )

        food_saltiness = normalize_value(
            food.get('Saltiness'),
            food_reference['Saltiness']
        )

        # ---------- Wine ----------
        wine_body = normalize_value(
            wine.get('light/bold (body)'),
            wine_reference['light/bold (body)']
        )

        wine_acidity = normalize_value(
            wine.get('acidity'),
            wine_reference['acidity']
        )

        wine_sweetness = normalize_value(
            wine.get('dry/sweetness'),
            wine_reference['dry/sweetness']
        )

        wine_tannin = normalize_value(
            wine.get('tannins'),
            wine_reference['tannins']
        )

        # ======================================
        # A. BODY ↔ RICHNESS
        # 30 points
        # ======================================
        body_score = clamp(
            1.0 - abs(wine_body - food_richness)
        )

        # ======================================
        # B. ACIDITY BALANCE
        # 25 points
        #
        # Rich/salty food benefits from enough
        # acidity, while acidic food needs a wine
        # that can keep up.
        # ======================================
        target_acidity = clamp(
            max(
                food_acidity,
                (0.65 * food_richness) +
                (0.15 * food_saltiness)
            )
        )

        acidity_score = clamp(
            1.0 - abs(wine_acidity - target_acidity)
        )

        # ======================================
        # C. SWEETNESS ↔ SPICE
        # 25 points
        #
        # Spicier food calls for more sweetness.
        # A wine that is too dry is penalized
        # more than one that is slightly sweeter.
        # ======================================
        target_sweetness = clamp(
            max(
                0.55 * food_sweetness,
                0.85 * food_spice
            )
        )

        if wine_sweetness >= target_sweetness:
            sweetness_score = clamp(
                1.0 -
                0.35 * (
                    wine_sweetness -
                    target_sweetness
                )
            )
        else:
            sweetness_score = clamp(
                1.0 -
                (
                    target_sweetness -
                    wine_sweetness
                )
            )

        # ======================================
        # D. TANNIN COMPATIBILITY
        # 20 points
        #
        # Rich/salty foods can support tannin.
        # Spice and high umami lower the ideal
        # tannin level.
        # ======================================
        target_tannin = clamp(
            (0.75 * food_richness) +
            (0.20 * food_saltiness) -
            (0.55 * food_spice) -
            (0.20 * food_umami)
        )

        tannin_score = clamp(
            1.0 - abs(
                wine_tannin -
                target_tannin
            )
        )

        # ======================================
        # TOTAL — 100 points
        # ======================================
        total_score = (
            body_score * 30 +
            acidity_score * 25 +
            sweetness_score * 25 +
            tannin_score * 20
        )

        components = {
            'body_match': round(body_score * 100, 1),
            'acidity_balance': round(acidity_score * 100, 1),
            'sweetness_spice': round(sweetness_score * 100, 1),
            'tannin_compatibility': round(tannin_score * 100, 1)
        }

        return total_score, components

    # ==========================================
    # 8. FIND BEST FOOD × WINE COMBINATION
    # ==========================================
    best_score = -1
    best_food = None
    best_wine = None
    best_components = None

    for _, food_row in food_pool.iterrows():

        for _, wine_row in w_df.iterrows():

            score, components = calculate_pairing_score(
                food_row,
                wine_row
            )

            if score > best_score:
                best_score = score
                best_food = food_row
                best_wine = wine_row
                best_components = components

    if best_food is None or best_wine is None:
        st.error(
            "A valid food and wine pairing could not be generated."
        )
        st.stop()

    # Save scoring information for the result page.
    # We will use this in the next step.
    st.session_state.pairing_score = round(best_score, 1)
    st.session_state.pairing_components = best_components

    return best_wine, best_food

# ==========================================
# 6. Page Rendering Functions
# ==========================================

def render_intro():
    # Brand-colored "Seoul & Sip" text header
    st.markdown('<div class="brand-logo">Seoul<br>& Sip</div>', unsafe_allow_html=True)
    
    # Montserrat ExtraBold main title
    st.markdown('<div class="main-title">The Wine Questionnaire</div>', unsafe_allow_html=True)
    
    # Subtitle description text
    st.markdown("""
        <p style='text-align: center; color: var(--pa-dove-gray); font-family: Montserrat, Arial, sans-serif; font-size: 1rem; line-height: 1.6; margin-bottom: 2.5rem;'>
            Four questions. Endless possibilities.<br>
            Your perfect bottle and Korean pairing wait at the end of the scene.
        </p>
    """, unsafe_allow_html=True)
    
    # Primary CTA button to start the questionnaire
    if st.button("FIND MY MATCH", type="primary", use_container_width=True):
        # Start every new quiz with a clean state
        st.session_state.answers = {}

        if 'matched_wine' in st.session_state:
            del st.session_state.matched_wine

        if 'matched_food' in st.session_state:
            del st.session_state.matched_food

        if 'rationale_text' in st.session_state:
            del st.session_state.rationale_text

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
        if st.button("A  🍇  New to the wine scene. keep it smooth and approachable.", type="primary" if q1_ans == 'A' else "secondary", use_container_width=True):
            st.session_state.answers['q1'] = 'A'
            st.rerun()
        if st.button("B  🍷  I've explored a few wines and I'm starting to know what I like.", type="primary" if q1_ans == 'B' else "secondary", use_container_width=True):
            st.session_state.answers['q1'] = 'B'
            st.rerun()
        if st.button("C  🗺️ Ready to explore. I'm open to something a little more adventurous.", type="primary" if q1_ans == 'C' else "secondary", use_container_width=True):
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
        if st.button("A  🌿  Keep it green. I'm a vegetarian.", type="primary" if q2_ans == 'A' else "secondary", use_container_width=True):
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
        if st.button("C  🔥  Bring on the authentic K-spice!", type="primary" if q4_ans == 'C' else "secondary", use_container_width=True):
            st.session_state.answers['q4'] = 'C'
            st.rerun()

    # Spacing before CTA landing button
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # Landing CTA Button: Only active/visible after an option is selected
    if st.button("SEE MY PAIRING 🍷",key="see_pairing", type="primary", use_container_width=True):
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
    

# Brand-styled email dialog with a light-gray validation message
@st.dialog(" ")
def show_email_modal():
    """Renders the white email dialog using the PairAnything palette."""
    
    st.markdown("""
        <style>
        /* Style the dialog panel, not its full-screen overlay. */
        div[role="dialog"], section[data-testid="stDialog"],
        section[data-testid="stDialog"] > div {
            background-color: var(--pa-white) !important;
            color: var(--pa-mineshaft) !important;
            border-radius: 16px !important;
            font-family: var(--pa-font) !important;
        }
        div[role="dialog"] {
            border: 1px solid var(--pa-sable-beige) !important;
            color-scheme: light;
        }
        div[role="dialog"] div[data-testid="stButton"] > button,
        section[data-testid="stDialog"] div[data-testid="stButton"] > button {
            background-color: var(--pa-burgundy) !important;
            border-color: var(--pa-burgundy) !important;
            color: var(--pa-white) !important;
            border-radius: 8px !important;
        }
        div[role="dialog"] div[data-testid="stButton"] > button:hover,
        section[data-testid="stDialog"] div[data-testid="stButton"] > button:hover {
            background-color: var(--pa-red) !important;
            border-color: var(--pa-red) !important;
        }
        div[role="dialog"] div[data-testid="stButton"] > button p,
        section[data-testid="stDialog"] div[data-testid="stButton"] > button p {
            color: var(--pa-white) !important;
            -webkit-text-fill-color: var(--pa-white) !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
        }
        div[role="dialog"] button[aria-label="Close"],
        div[role="dialog"] button[aria-label="Close"] svg,
        div[role="dialog"] button[aria-label="Close"] span,
        section[data-testid="stDialog"] button[aria-label="Close"],
        section[data-testid="stDialog"] button[aria-label="Close"] svg,
        section[data-testid="stDialog"] button[aria-label="Close"] span {
            color: var(--pa-burgundy) !important;
        }
        div[role="dialog"] button[aria-label="Close"]:focus-visible {
            outline: 2px solid var(--pa-burgundy) !important;
            outline-offset: 2px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🎯 (var(--pa-burgundy))font color
    # ---------------------------------------------------------
    
    
    st.markdown("""
        <div style="text-align: center; padding-top: 0px;">
            <div style="font-family: Montserrat, Arial, sans-serif; font-size: 2.2rem; font-weight: 800; color: var(--pa-burgundy) !important; -webkit-text-fill-color: var(--pa-burgundy) !important; line-height: 1.1; margin-bottom: 1.2rem;">
                Seoul<br>&amp; Sip
            </div>
            <p style="color: var(--pa-burgundy) !important; -webkit-text-fill-color: var(--pa-burgundy) !important; font-size: 0.95rem; margin-bottom: 1.5rem; line-height: 1.4;">
                Enter your email to get your personalized<br>pairing results.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # enter email
    user_email = st.text_input("EMAIL", placeholder="yourname@email.com", label_visibility="collapsed")
    
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    
    # send button
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
            
    # error message
    if st.session_state.get('email_error', False):
        st.markdown("""
            <div style="background-color: var(--pa-light-gray); color: var(--pa-burgundy); padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; font-weight: 700; margin-top: 10px; margin-bottom: 10px; text-align: left; display: flex; align-items: center; gap: 8px; border: 1px solid var(--pa-red);">
                <span style="color: var(--pa-burgundy) !important; -webkit-text-fill-color: var(--pa-burgundy) !important;">⚠️</span>
                <span style="color: var(--pa-burgundy) !important; -webkit-text-fill-color: var(--pa-burgundy) !important;">Please enter your email address.</span>
            </div>
        """, unsafe_allow_html=True)
            
    # privacy
    st.markdown("""
        <div style="text-align: center; margin-top: 15px; font-size: 0.8rem; color: var(--pa-burgundy) !important; -webkit-text-fill-color: var(--pa-burgundy) !important;">
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
    wine_name = matched_wine.get('Wine', 'Selected Wine')
    food_en = matched_food.get('food_name_en', 'Korean Dish')
    food_kr = matched_food.get('food_name', '')

    # Store text summary for email delivery function
    st.session_state.pairing_result = f"Wine: {wine_name} | Pairing Dish: {food_en} ({food_kr})"

    # Brand-colored "Seoul & Sip" text header
    st.markdown('<div class="brand-logo">Seoul<br>& Sip</div>', unsafe_allow_html=True)
    
    # Montserrat ExtraBold main title
    st.markdown('<div class="main-title">Your Perfect Pairing</div>', unsafe_allow_html=True)
    
    # 1. Types of wine images
    wine_type_images = {
        1: "https://images.pexels.com/photos/1123260/pexels-photo-1123260.jpeg?auto=compress&cs=tinysrgb&w=600", 
        2: "https://images.unsplash.com/photo-1558001373-7b93ee48ffa0?auto=format&fit=crop&w=600&q=80", 
        3: "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=600&q=80", 
        4: "https://images.unsplash.com/photo-1613477581402-306fa9dc6b95?q=80&w=774&auto=format&fit=crop"
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
        # 1. Extract URL and apply Google Search fallback logic (same as email)
        wine_link = matched_wine.get('info_url_x', '#')
        if pd.isna(wine_link) or str(wine_link).strip() == '' or str(wine_link) == 'nan':
            # If link is missing, fallback to Google Search with the wine name
            wine_link = "https://www.google.com/search?q=" + str(wine_name).replace(" ", "+")

        # 2. Wine Card Rendering (Adding the purchase button inside HTML)
        html_col1 = f"""<div class="result-card" style="min-height: 380px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 15px; border-radius: 12px; background-color: var(--pa-light-gray);">
<div style="width: 100%; border-radius: 8px; overflow: hidden; margin-bottom: 15px;">
<img src="{generated_img_url}" style="width: 100%; object-fit: cover; aspect-ratio: 4/3; display: block; border-radius: 8px;" />
</div>
<div style="text-align: center; margin-top: auto; padding-bottom: 10px; width: 100%;">
<div style="font-size: 1.1rem; font-weight: 700; color: var(--pa-mineshaft); text-transform: uppercase; letter-spacing: 0.5px;">{wine_name}</div>
<div style="font-size: 0.85rem; font-style: italic; color: var(--pa-dove-gray); margin-top: 4px; text-transform: uppercase; margin-bottom: 15px;">{winery_display}</div>
<!-- View & Buy Wine Button (Burgundy background, White text) -->
<a class="wine-purchase-link" href="{wine_link}" target="_blank" style="display: inline-block; width: 90%; background-color: var(--pa-burgundy); color: var(--pa-white); padding: 8px 0; border-radius: 6px; font-weight: bold; font-size: 0.85rem; text-decoration: none; letter-spacing: 0.5px; transition: opacity 0.3s;">
    VIEW & BUY WINE
</a>
</div>
</div>"""
        st.markdown(html_col1, unsafe_allow_html=True)
        
    with col2:
        # Extract food image file
        food_filename = matched_food.get("image_file")

        if pd.isna(food_filename) or not str(food_filename).strip():
            food_filename = matched_food.get("food_image_file")

        food_filename = str(food_filename).strip()

        food_img_path = IMAGE_DIR / food_filename
        food_img_src = get_image_base64(food_img_path)
        
        # Fallback image if local file is missing
        if not food_img_src:
            food_img_src = "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=600"

        # Food Card Rendering
        html_col2 = f"""<div class="result-card" style="min-height: 380px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 15px; border-radius: 12px; background-color: var(--pa-light-gray);">
<div style="width: 100%; border-radius: 8px; overflow: hidden; margin-bottom: 15px;">
<img src="{food_img_src}"
            style="width: 100%;
                    object-fit: cover; aspect-ratio: 4/3; display: block;
                    border-radius: 8px;" />
</div>
<div style="text-align: center; margin-top: auto; padding-bottom: 10px;">
<div style="font-size: 1.1rem; font-weight: bold; color: var(--pa-mineshaft);">{food_en}</div>
<div style="font-size: 0.85rem; color: var(--pa-dove-gray); margin-top: 4px;">{food_kr}</div>
</div>
</div>"""

        st.markdown(html_col2, unsafe_allow_html=True)

    # ==========================================
    # 📊 RADAR CHART VISUALIZATION
    # ==========================================
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: var(--pa-mineshaft); text-align: center; font-family: Montserrat, Arial, sans-serif; font-size: 1.5rem; font-weight: 700; margin-bottom: 5px;'>Flavor Profile Match</h3>", unsafe_allow_html=True)
    
    # Helper function to handle numeric scaling safely (0~5 scale)
    def safe_scale(val, default=1.0):
        try:
            num = float(val)
            return min(max(num, 0.0), 5.0) # Cap at 5.0 maximum
        except (ValueError, TypeError):
            return default

    # Intuitive axis categories for the radar chart
    categories = ['Acidity', 'Body & Richness', 'Sweetness', 'Tannin & Spice', 'Umami']

    # Exact column name matching from CSV files
    wine_stats = [
        safe_scale(matched_wine.get('acidity', 2.0)),               
        safe_scale(matched_wine.get('light/bold (body)', 2.0)),     
        safe_scale(matched_wine.get('dry/sweetness', 1.0)),         
        safe_scale(matched_wine.get('tannins', 2.0)),               
        1.0  # Wine has no Umami column, so fix baseline to 1.0
    ]

    food_stats = [
        min(safe_scale(matched_food.get('Acidity', 2.0)) * 1.2, 5.0),               
        min(safe_scale(matched_food.get('Richness', 2.0)) * 1.2, 5.0),              
        min(safe_scale(matched_food.get('Sweetness', 1.0)) * 1.2, 5.0),             
        min(safe_scale(matched_food.get('Spiciness_Heat', 2.0)) * 1.2, 5.0),        
        min(safe_scale(matched_food.get('Umami', 2.0)) * 1.2, 5.0)                  
    ]

    fig = go.Figure()

    # Brand-colored series. Dash/marker differences keep them distinguishable.
    # The original data arrays, axes and 0-5 scale are unchanged.
    fig.add_trace(go.Scatterpolar(
        r=wine_stats,
        theta=categories,
        fill='toself',
        name="Wine Profile",
        mode="lines+markers",
        line_color=BRAND_COLORS["burgundy"],
        line=dict(width=2.5),
        marker=dict(size=5, symbol="circle"),
        fillcolor='rgba(149, 25, 1, 0.12)'
    ))

    fig.add_trace(go.Scatterpolar(
        r=food_stats,
        theta=categories,
        fill='toself',
        name="Food Profile",
        mode="lines+markers",
        line_color=BRAND_COLORS["red"],
        line=dict(width=2.5, dash="dot"),
        marker=dict(size=5, symbol="diamond"),
        fillcolor='rgba(208, 1, 27, 0.09)'
    ))

    fig.update_layout(
        template="plotly_white",
        font=dict(family=BRAND_FONT, color=BRAND_COLORS["mineshaft"]),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                color=BRAND_COLORS["dove_gray"],
                gridcolor=BRAND_COLORS["sable_beige"],
                linecolor=BRAND_COLORS["light_gray"],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                color=BRAND_COLORS["mineshaft"],
                gridcolor=BRAND_COLORS["sable_beige"],
                linecolor=BRAND_COLORS["light_gray"]
            ),
            bgcolor=BRAND_COLORS["white"]
        ),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.25,
            xanchor="center", x=0.5,
            font=dict(family=BRAND_FONT, color=BRAND_COLORS["mineshaft"])
        ),
        paper_bgcolor=BRAND_COLORS["white"],
        plot_bgcolor=BRAND_COLORS["white"],
        hoverlabel=dict(
            bgcolor=BRAND_COLORS["white"],
            font=dict(family=BRAND_FONT, color=BRAND_COLORS["mineshaft"])
        ),
        margin=dict(l=40, r=40, t=20, b=20)
    )

    # Keep Streamlit's default chart theme from replacing the brand styling.
    st.plotly_chart(fig, use_container_width=True, theme=None)

        # ==========================================
    # 📝 PAIRING SCORE & RATIONALE
    # ==========================================

    pairing_score = st.session_state.get('pairing_score')
    pairing_components = st.session_state.get(
        'pairing_components',
        {}
    )

    body_match = pairing_components.get('body_match', 0)
    acidity_balance = pairing_components.get('acidity_balance', 0)
    sweetness_spice = pairing_components.get('sweetness_spice', 0)
    tannin_compatibility = pairing_components.get(
        'tannin_compatibility',
        0
    )

    # ==========================================
    # Existing wine description
    # ==========================================
    wine_type = str(matched_wine.get('wine_type', 'wine'))

    if wine_type.isdigit() or wine_type == '3' or wine_type == 'nan':
        wine_type = 'wine'

    key_flavors = matched_wine.get('key flavors', '')

    if pd.isna(key_flavors) or key_flavors == '':
        flavor_str = "its balanced structure"
    else:
        flavor_str = (
            f"its distinct notes of "
            f"{str(key_flavors).lower()}"
        )

    pairing_notes = matched_wine.get('pairing_notes', '')

    if not pd.isna(pairing_notes) and pairing_notes != '':
        if ',' in str(pairing_notes):
            western_dishes = ", ".join(
                [
                    dish.strip()
                    for dish in str(pairing_notes).split(',')[:3]
                ]
            )

            base_rationale = (
                f"<b>{wine_name}</b> is traditionally paired with "
                f"dishes such as {western_dishes}. "
                f"Its profile, including {flavor_str}, also works well "
                f"with <b>{food_en}</b>."
            )

        else:
            base_rationale = (
                f"<b>{wine_name}</b> brings {flavor_str} to this pairing. "
                f"{pairing_notes}"
            )

    else:
        base_rationale = (
            f"<b>{wine_name}</b>, with {flavor_str}, "
            f"creates a balanced match with <b>{food_en}</b>."
        )

    # ==========================================
    # Score summary generated by the same model
    # that selected the pairing
    # ==========================================
    if pairing_score is not None:

        score_summary = f"""
        <div style="
            margin-bottom: 1.2rem;
            padding-bottom: 1.1rem;
            border-bottom: 1px solid {BRAND_COLORS['sable_beige']};
        ">
            <div style="
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                color: {BRAND_COLORS['burgundy']};
                margin-bottom: 4px;
            ">
                MODEL PAIRING SCORE
            </div>

            <div style="
                font-size: 2rem;
                font-weight: 800;
                color: {BRAND_COLORS['mineshaft']};
                margin-bottom: 12px;
            ">
                {pairing_score:.1f}
                <span style="
                    font-size: 0.9rem;
                    font-weight: 400;
                    color: {BRAND_COLORS['dove_gray']};
                ">
                    / 100
                </span>
            </div>

            <div style="font-size: 0.85rem; line-height: 1.8;">
                <b>Body &amp; Richness</b>: {body_match:.0f}/100<br>
                <b>Acidity Balance</b>: {acidity_balance:.0f}/100<br>
                <b>Sweetness &amp; Spice</b>: {sweetness_spice:.0f}/100<br>
                <b>Tannin Compatibility</b>: {tannin_compatibility:.0f}/100
            </div>
        </div>
        """

    else:
        score_summary = ""

    rationale_text = f"""
        {score_summary}

        <div>
            <b>Why this pairing works</b><br>
            {base_rationale}
        </div>
    """

    st.session_state.rationale_text = rationale_text

    st.markdown(
        f"""
        <div style="
            background-color: var(--pa-light-gray);
            color: var(--pa-mineshaft);
            border: 1px solid var(--pa-sable-beige);
            border-radius: 12px;
            padding: 1.5rem;
            font-family: Montserrat, Arial, sans-serif;
            font-size: 0.95rem;
            line-height: 1.6;
        ">
            {rationale_text}

            <br><br>

            <span style="
                color: var(--pa-dove-gray);
                font-size: 0.85rem;
            ">
                Dish details:
                {matched_food.get('food_description_en', '')}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Equalized 1:1 Action Buttons
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("EMAIL MY PAIRING", key="email_my_pairing", use_container_width=True):
            show_email_modal()
            
    with col_btn2:
        if st.button("START OVER", use_container_width=True):
            # Complete reset of saved session state for a fresh quiz start
            st.session_state.answers = {}
            if 'matched_wine' in st.session_state:
                del st.session_state.matched_wine
            if 'matched_food' in st.session_state:
                del st.session_state.matched_food
            if 'pairing_score' in st.session_state:
                del st.session_state.pairing_score
            if 'pairing_components' in st.session_state:
                del st.session_state.pairing_components
            if 'rationale_text' in st.session_state:
                del st.session_state.rationale_text
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