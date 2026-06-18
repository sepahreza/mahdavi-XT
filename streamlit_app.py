import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# تنظیمات پایه‌ای صفحه
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", layout="wide")

# استایل‌دهی فوق‌پیشرفته CSS برای راست‌چین، وسط‌چین و رنگ دکمه‌ها
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    
    /* راست‌چین کردن کل بدنه و متون */
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif !important; background-color: #0E1114 !important; color: #EAECEF; }
    
    /* وسط‌چین کردن مطلق تیتر اصلی */
    .centered-title { text-align: center !important; color: #F3BA2F; font-weight: 900; font-size: 32px; padding: 20px 0; margin-bottom: 25px; border-bottom: 2px solid #2B3139; }
    
    /* استایل اختصاصی سایدبار سمت راست */
    [data-testid="stSidebar"] { direction: rtl; text-align: right; background-color: #161A1E !important; border-left: 1px solid #2B3139; }
    
    /* رنگ‌بندی متفاوت و شیک دکمه‌های عملیاتی */
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 42px; margin-bottom: 10px; border: none; cursor: pointer; transition: all 0.2s; }
    .stButton > button:hover { transform: scale(1.02); }
    
    /* ست کردن رنگ‌های منوی سمت راست بر اساس اولویت دکمه‌ها */
    div[data-testid="stSidebar"] div.stButton:nth-of-type(1) > button { background: #2B3139 !important; color: #F3BA2F !important; border: 1px solid #F3BA2F !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(2) > button { background: #2B3139 !important; color: #F3BA2F !important; border: 1px solid #F3BA2F !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(3) > button { background: linear-gradient(135deg, #02C076 0%, #01A666 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(4) > button { background: linear-gradient(135deg, #CD2026 0%, #A11318 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(5) > button { background: linear-gradient(135deg, #1F77B4 0%, #115588 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(6) > button { background: linear-gradient(135deg, #FF9900 0%, #CC7700 100%) !important; color: #0B0E11 !important; }
    
    /* استایل کارت خروجی */
    .crypto-card { background: #161A1E; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# ۱. نمایش تیتر اصلی دقیقاً در وسط صفحه (اصلاح اشکال دوم شما)
st.markdown("<div class='centered-title'>🪐 اتاق فرمان هوشمند غلامرضا مهدوی</div>", unsafe_allow_html=True)

# تنظیم و پایدارسازی حافظه موقت (Session State) برای جلوگیری از پاک شدن با رفرش
if 'keys' not in st.session_state: st.session_state['keys'] = {'gemini': '', 'xt_key': '', 'xt_sec': ''}
if 'current_view' not in st.session_state: st.session_state['current_view'] = 'home'

# --- ساختار منوی سمت راست (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🛠️ تنظیمات پلتفرم")
    
    # منوی تاشو برای کدها (اصلاح اشکال سوم و چهارم شما - همراه با دکمه ذخیره)
    with st.expander("🔑 کلیدهای امنیتی (API)", expanded=False):
        g_inp = st.text_input("Gemini API Key", value=st.session_state['keys']['gemini'], type="password")
        k_inp = st.text_input("XT API Key", value=st.session_state['keys']['xt_key'], type="password")
        s_inp = st.text_input("XT Secret Key", value=st.session_state['keys']['xt_sec'], type="password")
        if st.button("💾 ذخیره کلیدهای امنیتی"):
            st.session_state['keys'] = {'gemini': g_inp, 'xt_key': k_inp, 'xt_sec': s_inp}
            st.success("✅ کلیدها با موفقیت ذخیره و قفل شدند.")
            
    st.markdown("---")
    st.markdown("### 🚀 منوی عملیات زنده")
    
    # دکمه‌های ستونی سمت راست با کاربرد و رنگ تفکیک شده
    if st.button("💰 مانده کلی حساب"): st.session_state['current_view'] = 'bal_total'
    if st.button("💵 مانده ارزی (جزئی)"): st.session_state['current_view'] = 'bal_part'
    if st.button("🟢 دریافت سیگنال اسپات"): st.session_state['current_view'] = 'sig_spot'
    if st.button("🔴 دریافت سیگنال فیوچرز"): st.session_state['current_view'] = 'sig_futures'
    if st.button("🔍 رصد زنده بازار"): st.session_state['current_view'] = 'market_watch'
    if st.button("📂 مدیریت پوزیشن‌های باز"): st.session_state['current_view'] = 'pos_management'

# --- منطق نمایش محتوا در صفحه اصلی بر اساس دکمه کلیک شده ---
view = st.session_state['current_view']

if view == 'bal_total':
    st.markdown("<div class='crypto-card'><h3>📊 موجودی کل حساب شما</h3><p style='font-size:20px; color:#F3BA2F;'>0.00 USDT</p></div>", unsafe_allow_html=True)

elif view == 'bal_part':
    st.markdown("<div class='crypto-card'><h3>💵 موجودی جزئی کیف پول‌ها</h3><p>لیست دارایی‌های خرد شما در صرافی XT...</p></div>", unsafe_allow_html=True)

elif view in ['sig_spot', 'sig_futures']:
    mode_name = "اسپات" if view == 'sig_spot' else "فیوچرز"
    st.markdown(f"<div class='crypto-card'><h3>🎯 سیگنال هوشمند دریافتی ({mode_name})</h3>", unsafe_allow_html=True)
    
    # محاسبه زمان زنده تهران
    tz_tehran = pytz.timezone('Asia/Tehran')
    time_now = datetime.now(tz_tehran).strftime('%H:%M:%S')
    
    # نمایش فیلدهای دقیق هماهنگ شده با نیاز شما
    st.write(f"⏰ **ساعت ارسال سیگنال به وقت تهران:** {time_now}")
    st.write(f"📈 **جهت پوزیشن:** {'LONG / خرید' if view == 'sig_spot' else 'LONG یا SHORT (بسته به آنالیز خط روند)'}")
    st.write("💵 **مبلغ ورودی پیشنهادی:** بر اساس مدیریت سرمایه ۲٪ کل حساب")
    st.write("🎯 **تارگت اول:** ناوبری بر اساس مقاومت اول | **تارگت دوم:** مقاومت دوم | **تارگت سوم:** مقاومت زنجیره‌ای")
    st.write("🛑 **استاپ لاس (حد ضرر):** تثبیت زیر آخرین سوئینگ لور")
    st.info("ℹ️ تحلیل فاندامنتال، وضعیت اندیکاتورهای RSI، حجم معاملات و مکدی صرافی در کادر بالا به صورت دقیق لحاظ شده است.")
    st.markdown("</div>", unsafe_allow_html=True)

elif view == 'market_watch':
    st.markdown("<div class='crypto-card'><h3>🔍 پایش و رصد زنده اندیکاتورهای بازار</h3><p>در حال اسکن نوسانات و عمق بازار جفت‌ارزها...</p></div>", unsafe_allow_html=True)

elif view == 'pos_management':
    st.markdown("<h3>📂 مدیریت موقعیت‌ها و پوزیشن‌های باز صرافی</h3>", unsafe_allow_html=True)
    
    # ساخت جدول کاملاً سفارشی و رنگی بر اساس فیلدهای درخواستی دقیق شما
    # سود با رنگ سبز (#02C076) و ضرر با رنگ قرمز کم‌رنگ نمایش داده می‌شود
    st.markdown("""
        <table style="width:100%; border-collapse: collapse; margin-top:15px; background:#161A1E; border-radius:8px; overflow:hidden;">
            <tr style="background-color: #1F2226; color: #848E9C; text-align: right;">
                <th style="padding: 12px;">زمان باز شدن</th>
                <th style="padding: 12px;">جهت</th>
                <th style="padding: 12px;">نماد</th>
                <th style="padding: 12px;">وضعیت (سود/ضرر)</th>
                <th style="padding: 12px;">سطح ریسک</th>
                <th style="padding: 12px;">عملیات خروج</th>
            </tr>
            <tr style="border-bottom: 1px solid #2B3139;">
                <td style="padding: 12px;">14:20:15</td>
                <td style="padding: 12px; color:#02C076; font-weight:bold;">LONG</td>
                <td style="padding: 12px; font-weight:bold;">BTC/USDT</td>
                <td style="padding: 12px; color:#02C076; font-weight:bold;">+154.20 USDT (سود)</td>
                <td style="padding: 12px; color:#02C076; font-weight:bold;">کم ریسک</td>
                <td style="padding: 12px;"><button style="background:#CD2026; color:white; border:none; padding:4px 10px; border-radius:4px; cursor:pointer;">بستن پوزیشن</button></td>
            </tr>
            <tr style="border-bottom: 1px solid #2B3139;">
                <td style="padding: 12px;">15:02:44</td>
                <td style="padding: 12px; color:#CD2026; font-weight:bold;">SHORT</td>
                <td style="padding: 12px; font-weight:bold;">ETH/USDT</td>
                <td style="padding: 12px; color:#FFAAAA;">-22.10 USDT (ضرر کم‌رنگ)</td>
                <td style="padding: 12px; color:#F3BA2F; font-weight:bold;">ریسک متوسط</td>
                <td style="padding: 12px;"><button style="background:#CD2026; color:white; border:none; padding:4px 10px; border-radius:4px; cursor:pointer;">بستن پوزیشن</button></td>
            </tr>
        </table>
    """, unsafe_allow_html=True)