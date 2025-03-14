import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import streamlit as st


@st.cache_data(ttl="12h")
def load_data():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']
    
    try:
        # Try local development environment first
        credentials = ServiceAccountCredentials.from_json_keyfile_name('gs_credentials.json', scope)
    except:
        # If local file not found, use Streamlit secrets
        credentials_dict = st.secrets['gcp_service_account']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    
    client = gspread.authorize(credentials)
    
    try:
        # Try local environment spreadsheet URL
        spreadsheet = client.open_by_url(os.getenv('link_sheet'))
    except:
        # If not found, use Streamlit secrets
        spreadsheet = client.open_by_url(st.secrets['link_sheet'])
        
    worksheet = spreadsheet.get_worksheet(0)
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
    df = df.dropna(subset=['Word','Pinyin','Meaning', 'Meaning 2'])
    return df