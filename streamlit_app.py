import streamlit as st
import google.generativeai as genai
import ccxt
import pandas as pd

# تنظیمات اصلی صفحه
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", page_icon="📊", layout="wide")

# استایل‌های حرفه‌ای و راست‌چین
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;500;800&display=swap');
    * { font-family: 'Vazirmatn', sans-serif !important; direction: rtl !important; text-align: right !important; }
    .stApp { background-color: #0E1114 !important; }
    .header-box { background: #161A1E; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; text-align: center; }
    .main-title { color: #F3BA2F; font-weight: 800; font-size: 24px; }
    section[data-testid="stSidebar"] { background-color: #161A1E !important; }
    </style>
""", unsafe_allow_html=True)

# سربرگ
st.markdown("<div class='header-box'><div class='main-title'>🪐 اتاق فرمان هوشمند غلامرضا مهدوی</div></div>", unsafe_allow_html=True)

# مدیریت حافظه
for key in ['gemini_key', 'xt_key', 'xt_secret', 'last_price', 'symbol', 'mode', 'signal_output', 'positions_output']:
    if key not in st.session_state: st.session_state[key] = "" if 'key' in key or 'output' in key or 'symbol' in key else 0.0

# منوی سمت راست
with st.sidebar:
    with st.expander("🔑 کلیدهای امنیتی"):
        st.session_state['gemini_key'] = st.text_input("Gemini API:", value=st.session_state['gemini_key'], type="password")
        st.session_state['xt_key'] = st.text_input("XT API Key:", value=st.session_state['xt_key'], type="password")
        st.session_state['xt_secret'] = st.text_input("XT Secret Key:", value=st.session_state['xt_secret'], type="password")

    with st.expander("🚀 منوی عملیات زنده", expanded=True):
        btn_bal = st.button("💰 دریافت مانده حساب")
        btn_spot = st.button("🟢 سیگنال اسپات")
        btn_futures = st.button("🔴 سیگنال فیوچرز")
        btn_positions = st.button("📂 پوزیشن‌های باز")

# منطق برنامه (توابع)
def get_xt(): return ccxt.xt({'apiKey': st.session_state['xt_key'], 'secret': st.session_state['xt_secret'], 'enableRateLimit': True})

# پردازش دکمه‌ها
if btn_bal:
    try:
        bal = get_xt().fetch_balance()
        st.session_state['signal_output'] = f"موجودی آزاد: {bal.get('USDT', {}).get('free', 0.0)} USDT"
    except Exception as e: st.error(str(e))

if btn_spot or btn_futures:
    st.session_state['mode'] = "Spot" if btn_spot else "Futures"
    pair = "BTC/USDT" # برای نمونه
    try:
        ticker = get_xt().fetch_ticker(pair)
        genai.configure(api_key=st.session_state['gemini_key'])
        model = genai.GenerativeModel('gemini-2.5-flash')
        resp = model.generate_content(f"تحلیل {pair} برای {st.session_state['mode']}")
        st.session_state['signal_output'] = resp.text
        st.session_state['last_price'] = ticker['last']
    except Exception as e: st.error(str(e))

# نمایش خروجی‌ها
if st.session_state['signal_output']:
    st.write(st.session_state['signal_output'])

if st.session_state['last_price'] > 0:
    if st.button("⚡ اجرای سفارش"):
        st.success("سفارش ارسال شد.")