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
page = st.sidebar.selectbox(
    "Chọn một trang:",
    ["📚 Luyện tập",  "🎮 Chế độ chưa mở"]
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

# Get current language translations
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

if page == "📚 Luyện tập":
    show_vocabulary_review_page()

elif page == "🎮 Chế độ chưa mở":
    # Password protection for Practice Mode
    if not st.session_state.authenticated:
        st.title(txt["practice_mode_protected"])
        st.markdown(txt["password_protected_message"])
        load_dotenv()
        # Password input
        try:
            # Try local environment spreadsheet URL
            pass_word = os.getenv('pass_word')
            
        except:
            # If not found, use Streamlit secrets
            pass_word = st.secrets['pass_word']
        password = st.text_input(txt["password_label"], type="password")
        
        # Check password (you can change this to any password you want)
        if st.button(txt["login_button"]):
            if password.lower() == pass_word:  # Change this password
                st.session_state.authenticated = True
                st.success(txt["access_granted"])
                st.rerun()
            else:
                st.error(txt["incorrect_password"])
        
    else:
        # Show logout option
        if st.sidebar.button(txt["logout_button"]):
            st.session_state.authenticated = False
            st.rerun()
        
        show_cha_laoshi_page()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
### {txt['support']}
- [{txt['report_bug']}](https://forms.gle/UmH1FR6CsRw4w3t4A)
""")
