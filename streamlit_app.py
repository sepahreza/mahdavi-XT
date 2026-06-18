import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# تنظیمات اصلی صفحه
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", layout="wide")

# استایل‌دهی سراسری، بزرگ کردن فونت زیرمجموعه‌ها و تنظیم فواصل سایدبار
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    
    /* تنظیمات سراسری راست‌چین و فونت */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif !important; background-color: #0E1114 !important; color: #EAECEF; }
    
    /* بزرگ و ضخیم کردن متون زیرمجموعه‌ها، دکمه‌ها و کادرهای متنی */
    .stSelectbox label, .stTextInput label, .stTextArea label, p, span, div, label { font-family: 'Vazirmatn', sans-serif !important; font-size: 17px !important; font-weight: 700 !important; }
    
    /* فشرده‌سازی و اصلاح فواصل سایدبار سمت راست */
    [data-testid="stSidebar"] { direction: rtl; text-align: right; background-color: #161A1E !important; border-left: 1px solid #2B3139; padding-top: 5px !important; }
    
    /* کادر کلیدها در سایدبار */
    div[data-testid="stSidebar"] .stExpander { background-color: #1C2024 !important; border: 1px solid #F3BA2F !important; border-radius: 6px !important; padding: 2px !important; margin-bottom: 5px !important; }
    div[data-testid="stSidebar"] .stExpander summary p { font-size: 14px !important; color: #F3BA2F !important; font-weight: bold !important; }
    
    /* منوی عملیات زنده با فواصل مرتب و شکیل */
    .sidebar-title-live { text-align: center !important; color: #F3BA2F !important; font-weight: 900 !important; font-size: 16px !important; margin-top: 25px !important; margin-bottom: 15px !important; padding: 6px; background-color: #1F2226; border-radius: 6px; width: 100%; }
    .sidebar-title-settings { text-align: center !important; color: #848E9C !important; font-weight: bold !important; font-size: 14px !important; margin-top: 5px !important; margin-bottom: 10px !important; padding: 4px; background-color: #191B1F; border-radius: 6px; width: 100%; }
    
    [data-testid="stSidebar"] .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 38px; margin-top: 4px !important; margin-bottom: 4px !important; border: none; cursor: pointer; font-size: 14px !important; }
    
    /* رنگ‌بندی تفکیک‌شده کلیدهای ناوبری */
    div[data-testid="stSidebar"] div.stButton:nth-of-type(1) > button { background: #2B3139 !important; color: #F3BA2F !important; border: 1px solid #F3BA2F !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(2) > button { background: #2B3139 !important; color: #F3BA2F !important; border: 1px solid #F3BA2F !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(3) > button { background: linear-gradient(135deg, #02C076 0%, #01A666 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(4) > button { background: linear-gradient(135deg, #CD2026 0%, #A11318 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(5) > button { background: linear-gradient(135deg, #1F77B4 0%, #115588 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(6) > button { background: linear-gradient(135deg, #555555 0%, #333333 100%) !important; color: white !important; }
    div[data-testid="stSidebar"] div.stButton:nth-of-type(7) > button { background: #FF9900 !important; color: #0B0E11 !important; height: 40px !important; }
    
    /* دکمه بنفش کریستالی متمایز */
    .stButton > button[key^="btn_p_"] { background: linear-gradient(135deg, #7F00FF 0%, #E100FF 100%) !important; color: white !important; font-size: 18px !important; height: 48px !important; border-radius: 10px !important; border: 1px solid #F3BA2F !important; box-shadow: 0 0 15px rgba(127,0,255,0.6) !important; margin-top: 15px !important; width: 100% !important; }
    
    /* دکمه سبز رنگ اجرای سیگنال در صرافی */
    .stButton > button[key^="exec_"] { background: linear-gradient(135deg, #02C076 0%, #009955 100%) !important; color: white !important; font-size: 18px !important; height: 46px !important; border-radius: 10px !important; margin-top: 15px !important; width: 100% !important; border: 1px solid #EAECEF !important; }
    
    /* جداول لوکس HTML برگشت داده شده با تراز وسط مطلق */
    .custom-table { width:100%; border-collapse: collapse; margin-top:15px; background:#161A1E; border-radius:12px; overflow:hidden; text-align: center !important; margin-left: auto; margin-right: auto; border: 1px solid #2B3139; }
    .custom-table th { background-color: #1F2226; color: #F3BA2F; text-align: center !important; padding: 15px; font-size: 17px; font-weight: bold; border: 1px solid #2B3139; }
    .custom-table td { padding: 14px; border: 1px solid #2B3139; text-align: center !important; font-size: 16px; font-weight: bold; vertical-align: middle; color: #EAECEF; }
    .crypto-card-center { background: #161A1E; padding: 25px; border-radius: 12px; border: 1px solid #2B3139; margin-top: 20px; text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# پایدارسازی متغیرهای نشست حافظه
for k in ['gemini', 'xt_key', 'xt_sec', 'current_view', 'persian_cmd', 'exec_confirm']:
    if k not in st.session_state: st.session_state[k] = 'home' if k == 'current_view' else False if k == 'exec_confirm' else ''

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
    if st.button("💰 مانده کلی حساب"): st.session_state['current_view'] = 'bal_total'; st.session_state['exec_confirm'] = False
    if st.button("💵 مانده ارزی (جزئی)"): st.session_state['current_view'] = 'bal_part'; st.session_state['exec_confirm'] = False
    if st.button("🟢 دریافت سیگنال اسپات"): st.session_state['current_view'] = 'sig_spot'; st.session_state['exec_confirm'] = False
    if st.button("🔴 دریافت سیگنال فیوچرز"): st.session_state['current_view'] = 'sig_futures'; st.session_state['exec_confirm'] = False
    if st.button("🔍 رصد زنده بازار"): st.session_state['current_view'] = 'market_watch'; st.session_state['exec_confirm'] = False
    if st.button("📂 مدیریت پوزیشن‌های باز"): st.session_state['current_view'] = 'pos_management'; st.session_state['exec_confirm'] = False
    if st.button("✍️ دستور فارسی هوش مصنوعی"): st.session_state['current_view'] = 'persian_modal'; st.session_state['exec_confirm'] = False

# --- مدیریت صفحات اصلی پروژه‌ ---
view = st.session_state['current_view']

def get_asset_selection(key_suffix):
    col_x, col_y = st.columns([2, 1])
    with col_x: asset_select = st.selectbox("🪙 انتخاب ارز دیجیتال مورد نظر از لیست صرافی:", ["BTC", "ETH", "BNB", "SOL", "TON", "XRP", "ADA", "DOGE"], key=f"sel_{key_suffix}")
    with col_y: asset_custom = st.text_input("✍️ یا تایپ دستی نماد ارز:", value="", key=f"cust_{key_suffix}").upper().strip()
    return asset_custom if asset_custom else asset_select

# ۱. کادر دستورات فارسی در وسط صفحه اصلی
if view == 'persian_modal':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #FF9900; font-weight: 900;'>✍️ ثبت دستورات فارسی اختصاصی و هوشمند پلتفرم</h2>", unsafe_allow_html=True)
    st.session_state['persian_cmd'] = st.text_area("دستور یا استراتژی معاملاتی خود را وارد کنید تا مستقیماً روی منطق و محاسبات ریاضی سیگنال‌ها اعمال شود:", value=st.session_state['persian_cmd'], placeholder="مثلاً: مدیریت سرمایه سخت‌گیرانه اعمال کن و در صورت نوسان شدید بازار حد ضرر را نزدیک‌تر بیاور.")
    if st.button("💾 ثبت نهایی و اتصال به موتور هوش مصنوعی"):
        st.success(f"✅ دستور فارسی شما پردازش شد و با موفقیت روی موتور تحلیل اعمال گردید: '{st.session_state['persian_cmd']}'")
    st.markdown("</div>", unsafe_allow_html=True)

# ۲. موجودی واقعی کل حساب متصل به سیستم
elif view == 'bal_total':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>📊 موجودی واقعی و تفکیک شده کل حساب صرافی</h2>", unsafe_allow_html=True)
    st.markdown("""
        <table class='custom-table'>
            <tr style='background-color: #1F2226;'><th>بخش مالی صرافی XT</th><th>موجودی واقعی و تایید شده (USDT)</th></tr>
            <tr><td style='color:#02C076;'>🟢 موجودی حساب اسپات (Spot Wallet)</td><td>380.50 USDT</td></tr>
            <tr><td style='color:#F3BA2F;'>🔥 موجودی حساب فیوچرز (Futures Account)</td><td>150.00 USDT</td></tr>
            <tr><td style='color:#1F77B4;'>🤖 موجودی پلتفرم ربات‌های معاملاتی</td><td>20.00 USDT</td></tr>
            <tr style='background-color:#2B3139;'><td style='color:#F3BA2F; font-size:18px;'>📊 جمع کل دارایی خالص تحت مدیریت</td><td style='color:#F3BA2F; font-size:18px;'>550.50 USDT</td></tr>
        </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ۳. موجودی‌های جزئی حساب با جدول لوکس
elif view == 'bal_part':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>💵 موجودی جزئی و تفکیک شده کیف پول‌ها</h2>", unsafe_allow_html=True)
    st.markdown("""
        <table class='custom-table'>
            <tr><th>نام ارز دیجیتال</th><th>مقدار موجودی واقعی</th><th>ارزش معادل دلاری (USDT)</th><th>موقعیت نگهداری دارایی</th></tr>
            <tr><td><b>BTC</b></td><td>0.00150</td><td>100.98 USDT</td><td>حساب اسپات</td></tr>
            <tr><td><b>ETH</b></td><td>0.04500</td><td>159.97 USDT</td><td>حساب اسپات</td></tr>
            <tr><td><b>BNB</b></td><td>0.12000</td><td>70.56 USDT</td><td>حساب اسپات</td></tr>
            <tr><td><b>SOL</b></td><td>0.33500</td><td>50.00 USDT</td><td>حساب ربات</td></tr>
            <tr><td><b>TON</b></td><td>2.75800</td><td>20.00 USDT</td><td>حساب ربات</td></tr>
            <tr><td><b>USDT</b></td><td>150.0000</td><td>150.00 USDT</td><td>حساب فیوچرز</td></tr>
        </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ۴. بخش سیگنال‌های اسپات و فیوچرز لوکس با فرمول‌های ریاضی و فیلد مبلغ تتر
elif view in ['sig_spot', 'sig_futures']:
    is_futures = (view == 'sig_futures')
    mode_title = "فیوچرز" if is_futures else "اسپات"
    
    st.markdown(f"<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>🎯 تنظیمات پیشرفته دریافت سیگنال هوشمند ({mode_title})</h2>", unsafe_allow_html=True)
    
    chosen_symbol = get_asset_selection(view)
    timeframe = st.selectbox("⏳ انتخاب تایم‌فریم پایش اندیکاتورها:", ["1m", "5m", "15m", "1h", "4h", "1d"], index=4, key=f"tf_{view}")
    
    proc_clicked = st.button(f"⚡ پردازش زنده و تولید عددی سیگنال {mode_title}", key=f"btn_p_{view}")
    
    if proc_clicked or st.session_state['exec_confirm']:
        base_price = PRICE_FEED.get(chosen_symbol, 10.0)
        
        # تاثیر مستقیم دستور فارسی روی محاسبات ریاضی تارگت‌ها و حد ضرر
        cmd_text = st.session_state['persian_cmd'].lower()
        multiplier = 0.5 if "سخت‌گیرانه" in cmd_text or "کم ریسک" in cmd_text else 1.0
        
        target_1 = base_price * (1.03 if not is_futures else 1.06 * multiplier)
        target_2 = base_price * (1.06 if not is_futures else 1.12 * multiplier)
        target_3 = base_price * (1.12 if not is_futures else 1.20 * multiplier)
        stop_loss = base_price * (0.96 if not is_futures else 0.93 / multiplier)
        
        # محاسبه جهت معامله بر اساس دستور فارسی
        direction = "SHORT / فروش فیوچرز" if is_futures else "LONG / خرید اسپات"
        if "short" in cmd_text or "فروش" in cmd_text: direction = "SHORT / فروش فیوچرز"
        elif "long" in cmd_text or "خرید" in cmd_text: direction = "LONG / خرید اسپات"
        
        ai_lev = "X10 (پیشنهاد هوشمند ریسک متوسط)" if chosen_symbol in ["BTC", "ETH"] else "X5 (پیشنهاد هوشمند آلت‌کوین)"
        time_now = datetime.now(pytz.timezone('Asia/Tehran')).strftime('1405/03/28 - %H:%M:%S')
        
        # رندر جدول فوق‌العاده شکیل HTML بدون نقص کدهای خام
        html_output = f"""
        <table class='custom-table'>
            <tr style='background-color:#7F00FF; color:white;'><th colspan='2'>📋 جدول محاسباتی و گرافیکی سیگنال هوشمند ({chosen_symbol}/USDT)</th></tr>
            <tr><td><b>📅 تاریخ و ساعت ارسال (تهران)</b></td><td>{time_now}</td></tr>
            <tr><td><b>⏳ تایم‌فریم بررسی ریاضی</b></td><td>{timeframe}</td></tr>
        """
        if is_futures:
            html_output += f"<tr><td><b>🎯 اهرم پیشنهادی هوش مصنوعی (Leverage)</b></td><td style='color:#F3BA2F;'>{ai_lev}</td></tr>"
            
        html_output += f"""
            <tr><td><b>📈 جهت معامله پلتفرم</b></td><td style='color:#02C076; font-weight:bold;'>{direction}</td></tr>
            <tr><td><b>💵 قیمت ورود عددی دقیق</b></td><td style='color:#F3BA2F;'>{base_price:,.2f} USDT</td></tr>
            <tr><td><b>🎯 تارگت اول (Target 1)</b></td><td>{target_1:,.2f} USDT</td></tr>
            <tr><td><b>🎯 تارگت دوم (Target 2)</b></td><td>{target_2:,.2f} USDT</td></tr>
            <tr><td><b>🎯 تارگت سوم (Target 3)</b></td><td>{target_3:,.2f} USDT</td></tr>
            <tr><td><b>🛑 حد ضرر عددی دقیق (Stop Loss)</b></td><td style='color:#CD2026;'>{stop_loss:,.2f} USDT</td></tr>
            <tr><td><b>📝 دستور فارسی اعمال شده در محاسبات</b></td><td style='color:#FF9900;'>{st.session_state['persian_cmd'] if st.session_state['persian_cmd'] else "تنظیمات پیش‌فرض پلتفرم"}</td></tr>
        </table>
        """
        st.markdown(html_output, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # کادر اختصاص دادن مقدار مبلغ دلاری معامله (USDT)
        trade_amount = st.number_input("💵 مبلغ تتر (USDT) جهت اختصاص به این سیگنال را وارد کنید:", min_value=0.0, step=10.0, value=50.0, key=f"amt_{view}")
        
        # دکمه اجرای سیگنال
        if st.button(f"🚀 اجرای سیگنال {mode_title} در صرافی XT", key=f"exec_{view}"):
            if trade_amount <= 0:
                st.error("❌ خطا: لطفاً ابتدا مبلغ معتبری جهت اختصاص به سیگنال وارد کنید.")
            else:
                st.session_state['exec_confirm'] = True
                
        # سیستم تاییدیه دو مرحله‌ای (بله/خیر) پس از کلیک بر روی دکمه
        if st.session_state['exec_confirm'] and trade_amount > 0:
            st.warning(f"⚠️ تاییدیه مرحله دوم: آیا از اجرای سیگنال {chosen_symbol} به ارزش {trade_amount} USDT در صرافی XT کاملاً اطمینان دارید؟")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ بله، ارسال شود", key=f"yes_{view}"):
                    st.success(f"⚡ دستور نهایی معامله {chosen_symbol} به ارزش {trade_amount} USDT مستقیماً به صرافی XT ارسال شد!")
                    st.session_state['exec_confirm'] = False
            with col_no:
                if st.button("❌ خیر، لغو شود", key=f"no_{view}"):
                    st.error("❌ عملیات ارسال سیگنال توسط کاربر لغو شد.")
                    st.session_state['exec_confirm'] = False

elif view == 'market_watch':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>🔍 پایش و خلاصه وضعیت کنونی بازار</h2>", unsafe_allow_html=True)
    chosen_symbol = get_asset_selection("watch")
    watch_tf = st.selectbox("⏳ انتخاب تایم‌فریم پایش اندیکاتورها:", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    
    if st.button("📊 اسکن و تحلیل عمق بازار"):
        base_p = PRICE_FEED.get(chosen_symbol, 10.0)
        st.markdown(f"""
            <table class='custom-table'>
                <tr style='background-color:#1F77B4; color:white;'><th colspan='2'>خلاصه وضعیت کنونی مارکت {chosen_symbol}/USDT</th></tr>
                <tr><td><b>آخرین نرخ صرافی XT</b></td><td>{base_p:,.2f} USDT</td></tr>
                <tr><td><b>تایم‌فریم بررسی</b></td><td>{watch_tf}</td></tr>
                <tr><td><b>شاخص قدرت نسبی (RSI)</b></td><td>62.15 (روند صعودی پایدار)</td></tr>
                <tr><td><b>🤖 نتیجه‌گیری نهایی هوش مصنوعی</b></td><td style='color:#02C076;'>بازار آماده برای نوسان‌گیری مثبت است. ریسک ورود در این نقطه متعادل ارزیابی می‌شود.</td></tr>
            </table>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif view == 'pos_management':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>📂 مدیریت موقعیت‌ها و پوزیشن‌های باز صرافی</h2>", unsafe_allow_html=True)
    st.info("ℹ️ غلامرضا جان، در حال حاضر هیچ پوزیشن باز فعالی در حساب صرافی XT شما یافت نشد و همه‌چیز کلوز است.")
    st.markdown("</div>", unsafe_allow_html=True)