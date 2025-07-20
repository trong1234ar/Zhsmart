import streamlit as st
from page_cha_laoshi import show_cha_laoshi_page
from page_vocabulary_review import show_vocabulary_review_page
from config import TRANSLATIONS
import os
from dotenv import load_dotenv
# Page configuration
st.set_page_config(
    page_title="ZhSmart",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/trong1234ar/zhsmart',
        'Report a bug': "https://forms.gle/UmH1FR6CsRw4w3t4A",
        'About': """
        # ZhSmart - Chinese Learning App
        
        A comprehensive vocabulary learning application designed for Chinese language students.
        
        ## Features:
        - **Practice Mode**: Interactive vocabulary practice by level or lecture
        - **Vocabulary Review**: Browse, search, and review vocabulary with statistics
        - **Instant feedback** on pronunciation and meaning
        - **Progress tracking** and scoring
        - **Flexible learning modes**
        - **Multi-language support** (English/Vietnamese)
        """
    }
)

# Initialize authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Sidebar navigation
st.sidebar.title("🌿 ZhSmart")
st.sidebar.markdown("---")

# Page selection

# Get current language translations before using in sidebar

# Sidebar navigation
st.sidebar.title("🌿 ZhSmart")
st.sidebar.markdown("---")

# Page selection
page = st.sidebar.selectbox(
    "Chọn một trang:",
    ["📚 Luyện tập", "🌿HSK T103"]
)

# Language selector in sidebar
st.sidebar.markdown("---")
# st.sidebar.subheader("")
language = st.sidebar.selectbox(
    "🌐",
    ["Tiếng Việt", "English"],
    key="sidebar_language"
)

# Update session state language
if 'language' not in st.session_state:
    st.session_state.language = language
elif st.session_state.language != language:
    st.session_state.language = language

txt = TRANSLATIONS[st.session_state.language]


# Main content area
# if page == "🏠 Trang chủ":
#     st.title(txt["welcome_title"])
#     st.markdown(txt["welcome_description"])
    
#     st.markdown("---")
    
#     st.markdown(txt["what_you_can_do"])
    
#     st.markdown(f"**{txt['vocabulary_review_title']}**")
#     st.markdown(txt["vocabulary_review_desc"])
    
#     st.markdown(f"**{txt['practice_mode_title']}**")
#     st.markdown(txt["practice_mode_desc"])
    
    
#     st.markdown("---")
    
#     st.markdown(txt["ready_to_start"])
if "show_new_func" not in st.session_state:
    st.toast(txt["hsk_t103_opened"])
    st.session_state["show_new_func"] = True

if page == "📚 Luyện tập":
    show_vocabulary_review_page()

elif page == txt["hsk_t103_title"]:
    st.info(txt["hsk_t103_description"])
    show_cha_laoshi_page()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
### {txt['support']}
- [{txt['report_bug']}](https://forms.gle/UmH1FR6CsRw4w3t4A)
""")
