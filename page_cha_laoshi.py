import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from collect_data import load_data
from config import *
import os
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

def show_cha_laoshi_page():
    # Get current language translations from session state
    txt = TRANSLATIONS[st.session_state.language]

    # st.markdown(f"[{txt['update_word']}](https://docs.google.com/forms/d/e/1FAIpQLSe8_TXpak9Jm1tgGUevXMMuK9tDXYnDs0-CWQNKpYx_Z-M2gg/viewform?usp=header)")

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

    # Create two columns: main content (left) and results (right)
    left_col, right_col = st.columns([2, 1])

    # Selection interface before starting game
    with left_col:
        if not st.session_state.game_active:
            # Selection mode
            selection_mode = st.radio(
                txt["select_range"],
                [txt["all_vocab"], txt["by_levels"], txt["by_lectures"]]
            )
            
            filtered_df = df.copy()
            
            if selection_mode == txt["by_levels"]:
                available_levels = sorted(df['Level'].unique())
                col1, col2 = st.columns(2)
                with col1:
                    start_level = st.selectbox(f"{txt['choose_level']} {txt['from']}", available_levels)
                with col2:
                    end_level = st.selectbox(f"{txt['choose_level']} {txt['to']}", 
                                           [lvl for lvl in available_levels if lvl >= start_level],
                                           index=len([lvl for lvl in available_levels if lvl >= start_level])-1)
                filtered_df = df[df['Level'].between(start_level, end_level)]
            
            elif selection_mode == txt["by_lectures"]:
                available_levels = sorted(df['Level'].unique())
                selected_level = st.selectbox(txt["choose_level"], available_levels)
                available_lectures = sorted(df[df['Level'] == selected_level]['Lecture'].unique())
                
                col1, col2 = st.columns(2)
                with col1:
                    start_lecture = st.selectbox(f"{txt['choose_lecture']} {txt['from']}", available_lectures)
                with col2:
                    end_lecture = st.selectbox(f"{txt['choose_lecture']} {txt['to']}", 
                                             [lec for lec in available_lectures if lec >= start_lecture],
                                             index=len([lec for lec in available_lectures if lec >= start_lecture])-1)
                
                filtered_df = df[(df['Level'] == selected_level) & 
                                (df['Lecture'].between(start_lecture, end_lecture))]
            
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
                
                # Clear previous question states
                for key in list(st.session_state.keys()):
                    if key.startswith('question_') or key.startswith('pinyin_similarity_') or key.startswith('meaning_similarity_') or key.startswith('question_score_') or key.startswith('user_pinyin_') or key.startswith('user_meaning_'):
                        del st.session_state[key]

        # Game interface
        if st.session_state.game_active and st.session_state.current_index < len(st.session_state.current_words):
            current_word = st.session_state.current_words.iloc[st.session_state.current_index]
            
            # Display current progress - ensure total_questions is not zero
            progress = (st.session_state.current_index + 1) / st.session_state.total_questions if st.session_state.total_questions > 0 else 0
            st.progress(progress)
            st.write(f"{txt['question']} {st.session_state.current_index + 1} {txt['of']} {st.session_state.total_questions}")
            
            # Display the Chinese character
            st.markdown(f"## {txt['chinese_char']}")
            st.markdown(f"# {current_word['Word']}")
            
            # Get user input
            user_pinyin = st.text_input(txt["enter_pinyin"], key=f"pinyin_{st.session_state.current_index}")
            user_meaning = st.text_input(txt["enter_meaning"], key=f"meaning_{st.session_state.current_index}")
            
            # Action buttons
            check_col, next_col, change_col = st.columns(3)
            
            with check_col:
                if st.button(txt["check_answer"]):
                    # Check if this question has already been answered
                    question_key = f"question_{st.session_state.current_index}_answered"
                    if question_key not in st.session_state:
                        # First time answering this question
                        st.session_state[question_key] = True
                        
                        # Calculate similarity scores
                        pinyin_similarity = string_similarity(str(user_pinyin), str(current_word['Pinyin']), is_pinyin=True)
                        meaning_similarity = string_similarity(str(user_meaning), str(current_word['Meaning']))
                        
                        # Calculate question score
                        question_score = (pinyin_similarity * 5 + meaning_similarity * 2) / 7
                        st.session_state.score += question_score
                        
                        # Store the results for display
                        st.session_state[f"pinyin_similarity_{st.session_state.current_index}"] = pinyin_similarity
                        st.session_state[f"meaning_similarity_{st.session_state.current_index}"] = meaning_similarity
                        st.session_state[f"question_score_{st.session_state.current_index}"] = question_score
                        st.session_state[f"user_pinyin_{st.session_state.current_index}"] = user_pinyin
                        st.session_state[f"user_meaning_{st.session_state.current_index}"] = user_meaning
                    else:
                        # Question already answered, use stored results
                        pinyin_similarity = st.session_state[f"pinyin_similarity_{st.session_state.current_index}"]
                        meaning_similarity = st.session_state[f"meaning_similarity_{st.session_state.current_index}"]
                        question_score = st.session_state[f"question_score_{st.session_state.current_index}"]
                        user_pinyin = st.session_state[f"user_pinyin_{st.session_state.current_index}"]
                        user_meaning = st.session_state[f"user_meaning_{st.session_state.current_index}"]
                    
                    # Store results to display in right column
                    st.session_state.show_results = True
                    st.session_state.current_results = {
                        'pinyin_similarity': pinyin_similarity,
                        'meaning_similarity': meaning_similarity,
                        'question_score': question_score,
                        'user_pinyin': user_pinyin,
                        'user_meaning': user_meaning,
                        'current_word': current_word
                    }
            
            with next_col:
                if st.button(txt["next_question"]):
                    st.session_state.current_index += 1
                    # Reset results display for new question
                    if 'show_results' in st.session_state:
                        del st.session_state.show_results
                    if 'current_results' in st.session_state:
                        del st.session_state.current_results
                    st.rerun()
            
            with change_col:
                if st.button(txt["change_range"]):
                    st.session_state.game_active = False
                    st.rerun()

    # Right column for results
    with right_col:
        if 'show_results' in st.session_state and st.session_state.show_results and 'current_results' in st.session_state:
            results = st.session_state.current_results
            
            st.subheader(txt["results_header"])
            
            # Pinyin result
            if int(results['pinyin_similarity']) == 100:
                st.write(f"✅ **{txt['correct_pinyin']}** {results['current_word']['Pinyin']}")
            else:
                st.write(f"**{txt['correct_pinyin']}** {results['user_pinyin']} → {results['current_word']['Pinyin']}✅")
            
            # Meaning result
            if int(results['meaning_similarity']) >= 80:
                st.write(f"✅ **{txt['correct_meaning']}** {results['user_meaning']}")
            else:
                st.write(f"**{txt['correct_meaning']}** {results['user_meaning']} → {results['current_word']['Meaning']}✅")
            
            # Score
            if results['question_score'] >= 80:
                st.success(f"**{txt['question_score']}** {results['question_score']:.0f}%")
            elif results['question_score'] >= 50:
                st.warning(f"**{txt['question_score']}** {results['question_score']:.0f}%")
            else:
                st.error(f"**{txt['question_score']}** {results['question_score']:.0f}%")
            
            st.markdown("---")
            
            # Reference link
            lang_code = "en" if st.session_state.language == "English" else "vi"
            st.markdown(f"[{txt['learn_more_link']}](https://hanzii.net/search/word/{results['current_word']['Word']}?hl={lang_code})")

    # Show final score when game is complete
    with right_col:
        if st.session_state.game_active and st.session_state.current_index >= st.session_state.total_questions:
            final_score = st.session_state.score / st.session_state.total_questions
            
            # Simple final results
            st.subheader(txt["practice_complete"])
            
            # Final score with simple color coding
            if final_score >= 80:
                st.success(f"**{txt['final_score']}** {final_score:.1f}%")
            elif final_score >= 50:
                st.warning(f"**{txt['final_score']}** {final_score:.1f}%")
            else:
                st.error(f"**{txt['final_score']}** {final_score:.1f}%")
            
            # Action button
            if st.button(txt["start_new_practice"]):
                st.session_state.game_active = False
                st.rerun()
