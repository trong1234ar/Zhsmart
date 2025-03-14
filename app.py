import streamlit as st
import pandas as pd
import random
from difflib import SequenceMatcher
from collect_data import load_data
from config import *
import re



# Page configuration
st.set_page_config(
    page_title="ZhSmart",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://github.com/trong1234ar/zhsmart',
        'Report a bug': "mailto:trongntdseb@gmail.com",
        'About': """
        # ZhSmart - Chinese Learning App
        
        A vocabulary learning application designed for Chinese language students.
        Features:
        - Practice vocabulary by level or lecture
        - Instant feedback on pronunciation and meaning
        - Progress tracking and scoring
        - Flexible learning modes
        """
    }
)

def remove_tone_marks(pinyin):
    """Remove tone marks from pinyin."""
    tone_marks = {
        'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
        'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
        'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
        'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
        'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
        'ǖ': 'ü', 'ǘ': 'ü', 'ǚ': 'ü', 'ǜ': 'ü', 'ü': 'u'
    }
    return ''.join(tone_marks.get(c, c) for c in pinyin.lower())

def string_similarity(a, b, is_pinyin=False):
    """Calculate string similarity with special handling for pinyin."""
    if is_pinyin:
        # Remove tone marks and spaces for pinyin comparison
        a = remove_tone_marks(''.join(a.lower().split()))
        b = remove_tone_marks(''.join(b.lower().split()))
        return 100 if a == b else 0  # Exact match required for pinyin without tones
    else:
        # Normal similarity check for meanings
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

# Initialize language selection in session state
if 'language' not in st.session_state:
    st.session_state.language = "English"

# Language selector in sidebar
st.selectbox(
    "Language/Ngôn ngữ:",
    ["English", "Tiếng Việt"],
    key="language"
)

# Get current language translations
txt = TRANSLATIONS[st.session_state.language]

# Initialize session state variables
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

if not st.session_state.initialized:
    st.session_state.current_words = None
    st.session_state.score = 0
    st.session_state.current_index = 0
    st.session_state.total_questions = 10
    st.session_state.game_active = False
    st.session_state.initialized = True
    st.session_state.filtered_df = None

# Main app
st.title(txt["app_title"])

# Load data
df = load_data()
if st.session_state.language == "English":
    df = df.drop(columns=['Meaning 2'])
else:
    df = df.drop(columns=['Meaning'])
    df = df.rename(columns={'Meaning 2': 'Meaning'})
# st.write(len(df))

# Selection interface before starting game
if not st.session_state.game_active:
    # Selection mode
    selection_mode = st.radio(
        txt["select_range"],
        [txt["all_vocab"], txt["by_levels"], txt["by_lectures"]]
    )
    
    filtered_df = df.copy()
    
    if selection_mode == txt["by_levels"]:
        available_levels = sorted(df['Level'].unique())
        selected_level = st.selectbox(txt["choose_level"], available_levels)
        filtered_df = df[df['Level'] == selected_level]
    elif selection_mode == txt["by_lectures"]:
        available_levels = sorted(df['Level'].unique())
        selected_level = st.selectbox(txt["choose_level"], available_levels)
        available_lectures = sorted(df[df['Level'] == selected_level]['Lecture'].unique())
        selected_lecture = st.selectbox(txt["choose_lecture"], available_lectures)
        filtered_df = df[(df['Level'] == selected_level) & (df['Lecture'] == selected_lecture)]
    
    # Display number of available words
    st.write(f"{txt['num_words']} {len(filtered_df)}")
    
    try:
        num_questions = st.slider(txt["num_questions"], 
                                min_value=1, 
                                max_value=len(filtered_df), 
                                value=min(10, len(filtered_df)))
    except:
        st.warning(txt["not_enough_words"])
    
    if st.button(txt["start_practice"]):
        # Store filtered dataframe in session state
        st.session_state.filtered_df = filtered_df
        # Randomly select words from filtered dataset
        st.session_state.current_words = filtered_df.sample(n=num_questions).reset_index(drop=True)
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.total_questions = num_questions
        st.session_state.game_active = True
        # st.experimental_rerun()

# Game interface
if st.session_state.game_active and st.session_state.current_index < len(st.session_state.current_words):
    current_word = st.session_state.current_words.iloc[st.session_state.current_index]
    
    # Display current progress - ensure total_questions is not zero
    progress = (st.session_state.current_index + 1) / st.session_state.total_questions if st.session_state.total_questions > 0 else 0
    st.progress(progress)
    st.write(f"{txt['question']} {st.session_state.current_index + 1} {txt['of']} {st.session_state.total_questions}")
    
    # Display the Chinese character
    st.header(f"{txt['chinese_char']} {current_word['Word']}")
    
    # Get user input
    user_pinyin = st.text_input(txt["enter_pinyin"], key=f"pinyin_{st.session_state.current_index}")
    user_meaning = st.text_input(txt["enter_meaning"], key=f"meaning_{st.session_state.current_index}")
    check_col, next_col, change_col = st.columns(3)
    with check_col:
        if st.button(txt["check_answer"]):
            # Calculate similarity scores
            pinyin_similarity = string_similarity(str(user_pinyin), str(current_word['Pinyin']), is_pinyin=True)
            meaning_similarity = string_similarity(str(user_meaning), str(current_word['Meaning']))
            
            # Display correct answers and similarity scores
            st.markdown(f"**{txt['correct_pinyin']}** {current_word['Pinyin']}")
            st.write(f"{txt['your_pinyin']} {pinyin_similarity:.1f}%")
            st.markdown(f"**{txt['correct_meaning']}** {current_word['Meaning']}")
            st.write(f"{txt['your_meaning']} {meaning_similarity:.1f}%")
            
            # Update score (average of pinyin and meaning accuracy)
            question_score = (pinyin_similarity + meaning_similarity) / 2
            st.session_state.score += question_score
    with next_col:
        if st.button(txt["next_question"]):
            st.session_state.current_index += 1
            if st.session_state.current_index < st.session_state.total_questions:
                st.rerun()
    with change_col:
        if st.button(txt["change_range"]):
            st.session_state.game_active = False
            st.rerun()

# Show final score when game is complete
if st.session_state.game_active and st.session_state.current_index >= st.session_state.total_questions:
    final_score = st.session_state.score / st.session_state.total_questions
    
    if final_score >= 80:
        st.success(txt["outstanding"].format(score=final_score))
    elif final_score > 50:
        st.warning(txt["good_progress"].format(score=final_score))
    else:
        st.error(txt["keep_practicing"].format(score=final_score))
    
    if st.button(txt["start_new"]):
        st.session_state.game_active = False
        st.rerun()
