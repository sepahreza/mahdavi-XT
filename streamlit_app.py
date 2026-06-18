import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# تنظیمات اصلی صفحه
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", layout="wide")

# استایل اختصاصی برای راست‌چین کردن کامل و تمیز
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    /* راست‌چین کردن کل محیط */
    html, body, [class*="css"] { direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif !important; }
    
    /* تنظیم سایدبار به سمت راست */
    [data-testid="stSidebar"] { direction: rtl; text-align: right; background-color: #161A1E !important; }
    
    /* رنگ دکمه‌ها */
    div.stButton > button { width: 100%; border-radius: 8px; margin-bottom: 5px; }
    
    /* کاردها */
    .metric-card { background: #1E2329; padding: 15px; border-radius: 10px; border-right: 5px solid #F3BA2F; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# سیستم حافظه پایدار
if 'keys' not in st.session_state: st.session_state['keys'] = {'g': '', 'xk': '', 'xs': ''}
if 'view' not in st.session_state: st.session_state['view'] = 'home'

# --- منوی سمت راست (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🔑 کلیدهای امنیتی")
    st.session_state['keys']['g'] = st.text_input("Gemini API", value=st.session_state['keys']['g'], type="password")
    st.session_state['keys']['xk'] = st.text_input("XT API Key", value=st.session_state['keys']['xk'], type="password")
    st.session_state['keys']['xs'] = st.text_input("XT Secret Key", value=st.session_state['keys']['xs'], type="password")
    
    st.markdown("---")
    st.markdown("### 🚀 عملیات زنده")
    if st.button("💰 مانده کلی حساب"): st.session_state['view'] = 'bal_total'
    if st.button("💵 مانده ارزی (جزئی)"): st.session_state['view'] = 'bal_part'
    if st.button("🟢 سیگنال خرید/فروش"): st.session_state['view'] = 'signal'
    if st.button("📂 مدیریت پوزیشن‌ها"): st.session_state['view'] = 'pos'

# --- محتوای اصلی ---
st.title("🪐 اتاق فرمان هوشمند غلامرضا مهدوی")

if st.session_state['view'] == 'bal_total':
    st.markdown("<div class='metric-card'><h3>مانده کلی حساب</h3><p>موجودی کل شما محاسبه شد...</p></div>", unsafe_allow_html=True)
elif st.session_state['view'] == 'pos':
    st.subheader("پوزیشن‌های باز")
    df = pd.DataFrame({'نماد': ['BTC/USDT'], 'وضعیت': ['LONG'], 'ریسک': ['کم ریسک']})
    st.table(df)
elif st.session_state['view'] == 'signal':
    st.subheader("سیگنال هوشمند")
    tz = pytz.timezone('Asia/Tehran')
    st.write(f"⏰ زمان تهران: {datetime.now(tz).strftime('%H:%M:%S')}")
    st.info("در حال تحلیل فاندامنتال و اندیکاتورها...")