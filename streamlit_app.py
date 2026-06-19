import streamlit as st
import pandas as pd
import requests
import time
import hmac
import hashlib
from datetime import datetime
import pytz

# تنظیمات اصلی صفحه
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", layout="wide")

# استایل‌دهی سراسری، بزرگ کردن فونت زیرمجموعه‌ها، فواصل و رفع تداخل سایدبار
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif !important; background-color: #0E1114 !important; color: #EAECEF; }
    
    .stSelectbox label, .stTextInput label, .stTextArea label, p, span, div, label { font-family: 'Vazirmatn', sans-serif !important; font-size: 17px !important; font-weight: 700 !important; }
    
    [data-testid="stSidebar"] { direction: rtl; text-align: right; background-color: #161A1E !important; border-left: 1px solid #2B3139; padding-top: 5px !important; }
    
    /* رفع تداخل منوی کلیدها در سایدبار */
    div[data-testid="stSidebar"] .stExpander { background-color: #1C2024 !important; border: 1px solid #F3BA2F !important; border-radius: 6px !important; padding: 5px !important; margin-bottom: 5px !important; }
    div[data-testid="stSidebar"] .stExpander summary p { font-size: 14px !important; color: #F3BA2F !important; font-weight: bold !important; display: inline-block !important; }
    
    .sidebar-title-live { text-align: center !important; color: #F3BA2F !important; font-weight: 900 !important; font-size: 16px !important; margin-top: 25px !important; margin-bottom: 15px !important; padding: 6px; background-color: #1F2226; border-radius: 6px; width: 100%; }
    .sidebar-title-settings { text-align: center !important; color: #848E9C !important; font-weight: bold !important; font-size: 14px !important; margin-top: 5px !important; margin-bottom: 10px !important; padding: 4px; background-color: #191B1F; border-radius: 6px; width: 100%; }
    
    [data-testid="stSidebar"] .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 38px; margin-top: 4px !important; margin-bottom: 4px !important; border: none; cursor: pointer; font-size: 14px !important; }
    
    div[data-testid="stSidebar"] div.stButton:nth-of-type(1) > button { background: #2B3139 !important; color: #F3BA2F !important; border: 1px solid #F3BA2F !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(2) > button { background: #2B3139 !important; color: #F3BA2F !important; border: 1px solid #F3BA2F !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(3) > button { background: linear-gradient(135deg, #02C076 0%, #01A666 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(4) > button { background: linear-gradient(135deg, #CD2026 0%, #A11318 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(5) > button { background: linear-gradient(135deg, #1F77B4 0%, #115588 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(6) > button { background: linear-gradient(135deg, #555555 0%, #333333 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(7) > button { background: #FF9900 !important; color: #0B0E11 !important; height: 40px !important; }
    
    .stButton > button[key^="btn_p_"] { background: linear-gradient(135deg, #7F00FF 0%, #E100FF 100%) !important; color: white !important; font-size: 18px !important; height: 48px !important; border-radius: 10px !important; border: 1px solid #F3BA2F !important; box-shadow: 0 0 15px rgba(127,0,255,0.6) !important; margin-top: 15px !important; width: 100% !important; }
    .stButton > button[key^="exec_"] { background: linear-gradient(135deg, #02C076 0%, #009955 100%) !important; color: white !important; font-size: 18px !important; height: 46px !important; border-radius: 10px !important; margin-top: 15px !important; width: 100% !important; border: 1px solid #EAECEF !important; }
    
    /* جداول لوکس گرافیکی و تراز وسط بدون باگ متن خام */
    table.custom-table { width:100% !important; border-collapse: collapse !important; margin-top:15px !important; background:#161A1E !important; border-radius:12px !important; overflow:hidden !important; border: 1px solid #2B3139 !important; }
    table.custom-table th { background-color: #1F2226 !important; color: #F3BA2F !important; text-align: center !important; padding: 15px !important; font-size: 17px !important; font-weight: bold !important; border: 1px solid #2B3139 !important; }
    table.custom-table td { padding: 14px !important; border: 1px solid #2B3139 !important; text-align: center !important; font-size: 16px !important; font-weight: bold !important; color: #EAECEF !important; }
    .crypto-card-center { background: #161A1E; padding: 25px; border-radius: 12px; border: 1px solid #2B3139; margin-top: 20px; text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# پایدارسازی کلیدها و منوهای فعال در سیستم برای جلوگیری از پرش صفحه
init_states = {
    'gemini': '', 'xt_key': '', 'xt_sec': '', 'current_view': 'home', 
    'persian_cmd': '', 'exec_confirm': False, 'scan_triggered': False
}
for k, v in init_states.items():
    if k not in st.session_state: st.session_state[k] = v

PRICE_FEED = {"BTC": 67320.0, "ETH": 3555.0, "BNB": 588.0, "SOL": 149.2, "TON": 7.25, "XRP": 0.50, "ADA": 0.39, "DOGE": 0.12}

# هدر اصلی تراز وسط پلتفرم
st.markdown("<h1 style='text-align: center; color: #F3BA2F; font-size: 32px; font-weight: 900; padding-bottom: 20px; border-bottom: 2px solid #2B3139;'>🪐 اتاق فرمان هوشمند غلامرضا مهدوی</h1>", unsafe_allow_html=True)

# --- منوی سمت راست (SIDEBAR) ---
with st.sidebar:
    st.markdown("<div class='sidebar-title-settings'>🛠️ تنظیمات پلتفرم</div>", unsafe_allow_html=True)
    
    with st.expander("🔑 کلیدهای امنیتی (API)"):
        g_inp = st.text_input("Gemini API Key", value=st.session_state['gemini'], type="password")
        k_inp = st.text_input("XT API Key", value=st.session_state['xt_key'], type="password")
        s_inp = st.text_input("XT Secret Key", value=st.session_state['xt_sec'], type="password")
        if st.button("💾 ذخیره کلیدها"):
            st.session_state['gemini'] = g_inp
            st.session_state['xt_key'] = k_inp
            st.session_state['xt_sec'] = s_inp
            st.success("✅ ذخیره شد.")

    st.markdown("<div class='sidebar-title-live'>🚀 منوی عملیات زنده</div>", unsafe_allow_html=True)
    if st.button("💰 مانده کلی حساب"): st.session_state['current_view'] = 'bal_total'; st.session_state['exec_confirm'] = False; st.session_state['scan_triggered'] = False
    if st.button("💵 مانده ارزی (جزئی)"): st.session_state['current_view'] = 'bal_part'; st.session_state['exec_confirm'] = False; st.session_state['scan_triggered'] = False
    if st.button("🟢 دریافت سیگنال اسپات"): st.session_state['current_view'] = 'sig_spot'; st.session_state['exec_confirm'] = False; st.session_state['scan_triggered'] = False
    if st.button("🔴 دریافت سیگنال فیوچرز"): st.session_state['current_view'] = 'sig_futures'; st.session_state['exec_confirm'] = False; st.session_state['scan_triggered'] = False
    if st.button("🔍 رصد زنده بازار"): st.session_state['current_view'] = 'market_watch'; st.session_state['exec_confirm'] = False; st.session_state['scan_triggered'] = False
    if st.button("📂 مدیریت پوزیشن‌های باز"): st.session_state['current_view'] = 'pos_management'; st.session_state['exec_confirm'] = False; st.session_state['scan_triggered'] = False
    if st.button("✍️ دستور فارسی هوش مصنوعی"): st.session_state['current_view'] = 'persian_modal'; st.session_state['exec_confirm'] = False; st.session_state['scan_triggered'] = False

view = st.session_state['current_view']

def get_asset_selection(key_suffix):
    col_x, col_y = st.columns([2, 1])
    with col_x: asset_select = st.selectbox("🪙 انتخاب ارز دیجیتال مورد نظر از لیست صرافی:",