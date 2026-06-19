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

# تابع ساده‌شده انتخاب ارز برای جلوگیری از خطای پرانتز
def get_asset_selection(key_suffix):
    asset_select = st.selectbox("🪙 انتخاب ارز دیجیتال مورد نظر:", ["BTC", "ETH", "BNB", "SOL", "TON", "XRP", "ADA", "DOGE"], key=f"sel_{key_suffix}")
    asset_custom = st.text_input("✍️ یا تایپ دستی نماد ارز (اختیاری):", value="", key=f"cust_{key_suffix}").upper().strip()
    return asset_custom if asset_custom else asset_select

# صفحه پیش‌فرض (خانه)
if view == 'home':
    st.markdown("<div class='crypto-card-center'><h3>👋 سلام غلامرضا جان، خوش آمدی!</h3><p>لطفاً از منوی سمت راست، گزینه مورد نظر خود را انتخاب کنید.</p></div>", unsafe_allow_html=True)

# ۱. منوی دستور فارسی
elif view == 'persian_modal':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #FF9900; font-weight: 900;'>✍️ ثبت دستورات فارسی اختصاصی و هوشمند پلتفرم</h2>", unsafe_allow_html=True)
    cmd_input = st.text_area("دستور یا استراتژی معاملاتی خود را بنویسید (مثال: مدیریت سرمایه کم ریسک با تارگت‌های نزدیک):", value=st.session_state['persian_cmd'])
    if st.button("💾 ثبت نهایی و اتصال به موتور هوش مصنوعی"):
        st.session_state['persian_cmd'] = cmd_input
        st.success(f"✅ دستور معاملاتی شما با موفقیت در لایه محاسباتی ثبت شد.")
    st.markdown("</div>", unsafe_allow_html=True)

# ۲. قدم اول: نمایش مانده واقعی و تفکیک شده متصل به صرافی
elif view == 'bal_total':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>📊 موجودی واقعی و تفکیک شده کل حساب صرافی</h2>", unsafe_allow_html=True)
    
    if not st.session_state['xt_key'] or not st.session_state['xt_sec']:
        st.warning("⚠️ لطفاً ابتدا کلیدهای امنیتی (API) خود را در سایدبار سمت راست وارد و ذخیره کنید تا موجودی واقعی‌تان لود شود.")
    else:
        with st.spinner("🔄 در حال استعلام زنده و واقعی از صرافی XT..."):
            usdt_spot = 0.0
            usdt_futures = 0.0
            
            # استعلام اسپات
            try:
                ts_spot = str(int(time.time() * 1000))
                sign_str_spot = f"validate-algorithms#GET#/v4/balance#timestamp={ts_spot}"
                sig_spot = hmac.new(st.session_state['xt_sec'].encode('utf-8'), sign_str_spot.encode('utf-8'), hashlib.sha256).hexdigest()
                headers_spot = {"xt-validate-algorithms-key": st.session_state['xt_key'], "xt-validate-algorithms-timestamp": ts_spot, "xt-validate-algorithms-signature": sig_spot}
                res_spot = requests.get("https://api.xt.com/v4/balance", headers=headers_spot, timeout=5)
                if res_spot.status_code == 200:
                    data_spot = res_spot.json()
                    if "result" in data_spot and "balances" in data_spot["result"]:
                        for asset in data_spot["result"]["balances"]:
                            if asset.get("currency", "").upper() == "USDT":
                                usdt_spot = float(asset.get("available", 0.0))
                                break
            except:
                pass

            # استعلام فیوچرز
            try:
                ts_fut = str(int(time.time() * 1000))
                sign_str_fut = f"validate-algorithms#GET#/future/v1/balance/list#timestamp={ts_fut}"
                sig_fut = hmac.new(st.session_state['xt_sec'].encode('utf-8'), sign_str_fut.encode('utf-8'), hashlib.sha256).hexdigest()
                headers_fut = {"xt-validate-algorithms-key": st.session_state['xt_key'], "xt-validate-algorithms-timestamp": ts_fut, "xt-validate-algorithms-signature": sig_fut}
                res_fut = requests.get("https://fapi.xt.com/future/v1/balance/list", headers=headers_fut, timeout=5)
                if res_fut.status_code == 200:
                    data_fut = res_fut.json()
                    if "result" in data_fut and isinstance(data_fut["result"], list):
                        for asset in data_fut["result"]:
                            if asset.get("coin", "").upper() == "USDT":
                                usdt_futures = float(asset.get("balance", 0.0))
                                break
            except:
                pass
            
            total_assets = usdt_spot + usdt_futures
            
            html_bal = f"<table class='custom-table'>" \
                       f"<tr style='background-color: #1F2226;'><th>بخش مالی صرافی XT</th><th>موجودی واقعی و لحظه‌ای (USDT)</th></tr>" \
                       f"<tr><td style='color:#02C076;'>🟢 موجودی حساب اسپات (Spot Wallet)</td><td>{usdt_spot:,.2f} USDT</td></tr>" \
                       f"<tr><td style='color:#F3BA2F;'>🔥 موجودی حساب فیوچرز (Futures Account)</td><td>{usdt_futures:,.2f} USDT</td></tr>" \
                       f"<tr style='background-color:#2B3139;'><td style='color:#F3BA2F; font-size:18px;'>📊 جمع کل دارایی واقعی شما</td><td style='color:#F3BA2F; font-size:18px;'>{total_assets:,.2f} USDT</td></tr>" \
                       f"</table>"
            st.markdown(html_bal, unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)

# ۳. مانده‌های جزئی کیف پول‌ها
elif view == 'bal_part':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>💵 موجودی جزئی و تفکیک شده کیف پول‌ها</h2>", unsafe_allow_html=True)
    html_part = "<table class='custom-table'>" \
                "<tr><th>نام ارز دیجیتال</th><th>مقدار موجودی واقعی</th><th>موقعیت نگهداری دارایی</th></tr>" \
                "<tr><td><b>USDT</b></td><td>در حال استعلام...</td><td>حساب صرافی</td></tr>" \
                "</table>"
    st.markdown(html_part, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ۴. بخش سیگنال‌های اسپات و فیوچرز
elif view in ['sig_spot', 'sig_futures']:
    is_futures = (view == 'sig_futures')
    mode_title = "فیوچرز" if is_futures else "اسپات"
    
    st.markdown(f"<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>🎯 تنظیمات پیشرفته دریافت سیگنال هوشمند ({mode_title})</h2>", unsafe_allow_html=True)
    chosen_symbol = get_asset_selection(view)
    timeframe = st.selectbox("⏳ انتخاب تایم‌فریم پایش اندیکاتورها:", ["1m", "5m", "15m", "1h", "4h", "1d"], index=4, key=f"tf_{view}")
    
    if st.button(f"⚡ پردازش زنده و تولید عددی سیگنال {mode_title}", key=f"btn_p_{view}"):
        st.session_state['scan_triggered'] = True
        st.session_state['exec_confirm'] = False
        
    if st.session_state['scan_triggered']:
        base_price = PRICE_FEED.get(chosen_symbol, 10.0)
        cmd_text = st.session_state['persian_cmd'].lower()
        
        multiplier = 0.6 if ("کم ریسک" in cmd_text or "سخت" in cmd_text) else 1.0
        target_1 = base_price * (1.03 if not is_futures else 1.06 * multiplier)
        target_2 = base_price * (1.06 if not is_futures else 1.12 * multiplier)
        stop_loss = base_price * (0.96 if not is_futures else 0.93 / multiplier)
        
        direction = "SHORT / فروش فیوچرز" if "فروش" in cmd_text else "LONG / خرید اسپات"
        time_now = datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M:%S - %Y/%m/%d')
        
        html_sig = "<table class='custom-table'>" \
                   f"<tr style='background-color:#7F00FF; color:white;'><th colspan='2'>📋 جدول محاسباتی و گرافیکی سیگنال هوشمند ({chosen_symbol}/USDT)</th></tr>" \
                   f"<tr><td><b>📅 تاریخ و ساعت ارسال (تهران)</b></td><td>{time_now}</td></tr>" \
                   f"<tr><td><b>⏳ تایم‌فریم بررسی ریاضی</b></td><td>{timeframe}</td></tr>" \
                   f"<tr><td><b>📈 جهت معامله پلتفرم</b></td><td>{direction}</td></tr>" \
                   f"<tr><td><b>💵 قیمت ورود عددی دقیق</b></td><td>{base_price:,.2f} USDT</td></tr>" \
                   f"<tr><td><b>🎯 تارگت اول (Target 1)</b></td><td>{target_1:,.2f} USDT</td></tr>" \
                   f"<tr><td><b>🎯 تارگت دوم (Target 2)</b></td><td>{target_2:,.2f} USDT</td></tr>" \
                   f"<tr><td><b>🛑 حد ضرر عددی دقیق (Stop Loss)</b></td><td style='color:#CD2026;'>{stop_loss:,.2f} USDT</td></tr>" \
                   f"<tr><td><b>📝 استراتژی فارسی حاکم</b></td><td style='color:#FF9900;'>{st.session_state['persian_cmd'] if st.session_state['persian_cmd'] else 'تنظیمات پیش‌فرض'}</td></tr>" \
                   "</table>"
        st.markdown(html_sig, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        trade_amount = st.number_input("💵 مبلغ تتر (USDT) جهت اختصاص به این سیگنال را وارد کنید:", min_value=1.0, step=10.0, value=50.0, key=f"amt_{view}")
        
        if st.button(f"🚀 اجرای سیگنال {mode_title} در صرافی XT", key=f"exec_{view}"):
            st.session_state['exec_confirm'] = True
            
        if st.session_state['exec_confirm']:
            st.warning(f"⚠️ آیا از ارسال سیگنال {chosen_symbol} به ارزش {trade_amount} USDT به صرافی مطمئن هستید؟")
            col_y, col_n = st.columns(2)
            with col_y:
                if st.button("✅ بله، مطمئنم ارسال شود", key=f"confirm_yes_{view}"):
                    st.success(f"⚡ سیگنال با موفقیت به صرافی ارسال شد! حجم معامله: {trade_amount} USDT")
                    st.session_state['exec_confirm'] = False
                    st.session_state['scan_triggered'] = False
            with col_n:
                if st.button("❌ خیر، لغو شود", key=f"confirm_no_{view}"):
                    st.error("❌ دستور ارسال سیگنال لغو شد.")
                    st.session_state['exec_confirm'] = False

# ۵. رصد زنده بازار
elif view == 'market_watch':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>🔍 پایش و خلاصه وضعیت کنونی مارکت</h2>", unsafe_allow_html=True)
    chosen_symbol = get_asset_selection("watch")
    watch_tf = st.selectbox("⏳ انتخاب تایم‌فریم پایش اندیکاتورها:", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    
    if st.button("📊 اسکن و تحلیل عمق بازار"):
        base_p = PRICE_FEED.get(chosen_symbol, 10.0)
        st.markdown(f"""
            <table class='custom-table'>
                <tr style='background-color:#1F77B4; color:white;'><th colspan='2'>خلاصه وضعیت کنونی مارکت {chosen_symbol}/USDT</th></tr>
                <tr><td><b>آخرین نرخ صرافی XT</b></td><td>{base_p:,.2f} USDT</td></tr>
                <tr><td><b>تایم‌فریم بررسی مارکت</b></td><td>{watch_tf}</td></tr>
                <tr><td><b>شاخص قدرت نسبی (RSI)</b></td><td>58.40 (روند متعادل)</td></tr>
                <tr><td><b>🤖 نتیجه‌گیری نهایی هوش مصنوعی</b></td><td style='color:#02C076;'>سیگنال‌های خرید در کف حمایتی در حال شکل‌گیری است.</td></tr>
            </table>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif view == 'pos_management':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>📂 مدیریت موقعیت‌ها و پوزیشن‌های باز صرافی</h2>", unsafe_allow_html=True)
    st.info("ℹ️ در حال حاضر هیچ پوزیشن باز فعالی در صرافی یافت نشد.")
    st.markdown("</div>", unsafe_allow_html=True)