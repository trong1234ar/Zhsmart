import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from config import *
import re

def load_hsk_data():
    """Load HSK vocabulary data from CSV file."""
    try:
        df = pd.read_csv('hsk_vocab_full.csv')
        return df
    except FileNotFoundError:
        st.error("File hsk_vocab_full.csv not found!")
        return pd.DataFrame()

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
        # Remove only spaces for pinyin comparison
        a_no_space = ''.join(a.lower().split())
        b_no_space = ''.join(b.lower().split())
        if a_no_space == b_no_space:
            return 100  # Exact match ignoring spaces
        # Remove tone marks for fuzzy match
        a_no_tone = remove_tone_marks(a_no_space)
        b_no_tone = remove_tone_marks(b_no_space)
        if a_no_tone == b_no_tone:
            return 80  # Match without tones but not exact
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100
    else:
        # Normal similarity check for meanings
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

def show_practice_tab(df, txt):
    """Show practice tab with quiz functionality."""
    st.header("🎯 Practice Mode")
    left_col, right_col = st.columns([1, 1])

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

    # Selection interface before starting game
    with left_col:
        if not st.session_state.game_active:
            # Level selection
            available_levels = sorted(df['level'].unique())
            selected_level = st.selectbox(f"{txt['choose_level']}", available_levels)
            
            # Filter by level
            filtered_df = df[df['level'] == selected_level]
            
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
        
        # Create two columns: main content (left) and results (right)
        
        
        with left_col:
            # Display current progress
            progress = (st.session_state.current_index + 1) / st.session_state.total_questions if st.session_state.total_questions > 0 else 0
            st.progress(progress)
            st.write(f"{txt['question']} {st.session_state.current_index + 1} {txt['of']} {st.session_state.total_questions}")
            
            # Display the Chinese character
            st.markdown(f"## {txt['chinese_char']}")
            st.markdown(f"# {current_word['vocab']}")
            
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
                        pinyin_similarity = string_similarity(str(user_pinyin), str(current_word['vocab_pinyin']), is_pinyin=True)
                        meaning_similarity = string_similarity(str(user_meaning), str(current_word['meaning']))
                        
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
        
        # Right column for results and examples
        with right_col:
            if 'show_results' in st.session_state and st.session_state.show_results and 'current_results' in st.session_state:
                results = st.session_state.current_results
                
                st.subheader(txt["results_header"])
                
                # Pinyin result
                if int(results['pinyin_similarity']) == 100:
                    st.write(f"✅ **{txt['correct_pinyin']}** {results['current_word']['vocab_pinyin']}")
                else:
                    st.write(f"**{txt['correct_pinyin']}** {results['user_pinyin']} ({results['pinyin_similarity']:.0f}%) → {results['current_word']['vocab_pinyin']}")
                
                # Meaning result
                if int(results['meaning_similarity']) >= 80:
                    st.write(f"✅ **{txt['correct_meaning']}** {results['user_meaning']}")
                else:
                    st.write(f"**{txt['correct_meaning']}** {results['user_meaning']} ({results['meaning_similarity']:.0f}%)→ {results['current_word']['meaning']}")
                
                # Score
                if results['question_score'] >= 80:
                    st.success(f"**{txt['question_score']}** {results['question_score']:.0f}%")
                elif results['question_score'] >= 50:
                    st.warning(f"**{txt['question_score']}** {results['question_score']:.0f}%")
                else:
                    st.error(f"**{txt['question_score']}** {results['question_score']:.0f}%")
                
                st.markdown("---")
                
                # Show example if available
                if pd.notna(results['current_word']['example']) and results['current_word']['example'].strip():
                    st.subheader(txt["example_header"])
                    st.subheader(f"**{results['current_word']['example']}**")
                    st.write(f"*{results['current_word']['example_pinyin']}*")
                    st.write(f"*{results['current_word']['example_meaning']}*")
                
                # Reference link
                lang_code = "en" if st.session_state.language == "English" else "vi"
                st.markdown(f"[{txt['learn_more_link']}](https://hanzii.net/search/word/{results['current_word']['vocab']}?hl={lang_code})")

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

def show_review_tab(df, txt):
    """Show review tab with search and statistics."""
    st.header("📚 Review Mode")
    
    # Search and filter section at the top
    st.subheader(txt["search_vocabulary"])
    
    search_col1, search_col2 = st.columns(2)
    
    with search_col1:
        search_term = st.text_input(txt["search_placeholder"])
    
    with search_col2:
        level_filter = st.selectbox(txt["filter_by_level"], [txt["all"]] + sorted(df['level'].unique().tolist()))
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_term:
        mask = (df['vocab'].str.contains(search_term, case=False, na=False) |
                df['vocab_pinyin'].str.contains(search_term, case=False, na=False) |
                df['meaning'].str.contains(search_term, case=False, na=False))
        filtered_df = filtered_df[mask]
    
    if level_filter != txt["all"]:
        filtered_df = filtered_df[filtered_df['level'] == level_filter]
    
    # Display results
    st.subheader(f"{txt['results']} ({len(filtered_df)} {txt['words']})")
    
    if len(filtered_df) > 0:
        # Show first 10 results with pagination
        page_size = 10
        total_pages = (len(filtered_df) + page_size - 1) // page_size
        
        if 'review_current_page' not in st.session_state:
            st.session_state.review_current_page = 0
        
        page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
        
        with page_col1:
            if st.button(txt["previous"]) and st.session_state.review_current_page > 0:
                st.session_state.review_current_page -= 1
        
        with page_col2:
            st.write(f"{txt['page']} {st.session_state.review_current_page + 1} {txt['of_pages']} {total_pages}")
        
        with page_col3:
            if st.button(txt["next"]) and st.session_state.review_current_page < total_pages - 1:
                st.session_state.review_current_page += 1
        
        start_idx = st.session_state.review_current_page * page_size
        end_idx = min(start_idx + page_size, len(filtered_df))
        page_df = filtered_df.iloc[start_idx:end_idx]
        st.markdown("""
            <style>
            .big-expander .streamlit-expanderHeader {
                font-size: 1.5rem !important;
            }
            </style>
        """, unsafe_allow_html=True)
        # Display vocabulary cards with examples
        for idx, row in page_df.iterrows():
            with st.expander(f"{row['vocab']} ({row['vocab_pinyin']})"):
                # Main vocabulary info
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{txt['chinese']}** {row['vocab']}")
                    st.write(f"**{txt['pinyin']}** {row['vocab_pinyin']}")
                    st.write(f"**{txt['meaning']}** {row['meaning']}")                
                with col2:
                    # Example section
                    if pd.notna(row['example']) and row['example'].strip():
                        st.write(f"**{txt['example_label']}**")
                        st.write(f"**{row['example']}**")
                        st.write(f"*{row['example_pinyin']}*")
                        st.write(f"*{row['example_meaning']}*")
                    else:
                        st.write(f"**{txt['no_example']}**")
                
                # Add reference link
                lang_code = "en" if st.session_state.language == "English" else "vi"
                st.markdown(f"[{txt['learn_more_hanzii']}](https://hanzii.net/search/word/{row['vocab']}?hl={lang_code})")
    else:
        st.warning(txt["no_vocabulary_found"])
    
    # Statistics section at the bottom
    st.markdown("---")
    st.subheader(txt["vocabulary_statistics"])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(txt["total_words"], len(df))
    
    with col2:
        st.metric(txt["hsk_levels"], len(df['level'].unique()))
    
    with col3:
        avg_words_per_level = len(df) / len(df['level'].unique())
        st.metric(txt["avg_words_per_level"], f"{avg_words_per_level:.1f}")
    
    with col4:
        st.metric(txt["with_examples"], len(df[df['example'].notna()]))
    
    # Level distribution
    st.subheader(txt["words_by_hsk_level"])
    level_counts = df['level'].value_counts().sort_index()
    st.bar_chart(level_counts)

def show_vocabulary_review_page():
    txt = TRANSLATIONS[st.session_state.language]
    st.title(txt["vocabulary_review_header"])
    
    # st.markdown(txt["vocabulary_review_welcome"])
    # st.markdown(txt["vocabulary_review_description"])
    
    # Load data
    df = load_hsk_data()
    if df.empty:
        return
    
    # Prepare data based on language
    if st.session_state.language == "English":
        # Use English translations
        df['meaning'] = df['vocab_trans_en']
        df['example_meaning'] = df['example_trans_en']
    else:
        # Use Vietnamese translations
        df['meaning'] = df['vocab_trans_vi']
        df['example_meaning'] = df['example_trans_vi']
    
    # Create tabs
    tab1, tab2 = st.tabs([txt["practice_tab"], txt["review_tab"]])
    
    with tab1:
        show_practice_tab(df, txt)
    
    with tab2:
        show_review_tab(df, txt) 