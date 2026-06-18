import streamlit as st
import google.generativeai as genai
import ccxt
import pandas as pd

# تنظیمات ظاهر صفحه به حالت تاریک و صرافی
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", page_icon="📊", layout="centered")

st.markdown("""
    <style>
    .reportview-container { background: #0B0E11; }
    h1 { color: #F3BA2F; text-align: center; font-family: 'Tahoma'; font-size: 26px; }
    h2, h3 { color: #EAECEF; font-family: 'Tahoma'; }
    .stButton>button {
        background-color: #F3BA2F; color: #0B0E11; font-weight: bold;
        width: 100%; border-radius: 8px; font-size: 16px; height: 45px;
    }
    .balance-btn>button { background-color: #2B3139; color: #F3BA2F; border: 1px solid #F3BA2F; }
    .spot-btn>button { background-color: #02C076; color: white; }
    .futures-btn>button { background-color: #CD2026; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🪐 اتاق فرمان هوشمند و سامانه معاملات زنده غلامرضا مهدوی")

# قفل کردن کلیدها در حافظه مرورگر برای جلوگیری از حذف با رفرش
if 'gemini_key' not in st.session_state: st.session_state['gemini_key'] = ""
if 'xt_key' not in st.session_state: st.session_state['xt_key'] = ""
if 'xt_secret' not in st.session_state: st.session_state['xt_secret'] = ""

# بخش دریافت کلیدها در منوی سمت چپ
st.sidebar.header("🔑 تنظیمات کلیدهای امنیتی")
GEMINI_API_KEY = st.sidebar.text_input("کلید Gemini API:", value=st.session_state['gemini_key'], type="password")
XT_API_KEY = st.sidebar.text_input("کلید XT API Key:", value=st.session_state['xt_key'], type="password")
XT_SECRET_KEY = st.sidebar.text_input("کلید XT Secret Key:", value=st.session_state['xt_secret'], type="password")

st.session_state['gemini_key'] = GEMINI_API_KEY
st.session_state['xt_key'] = XT_API_KEY
st.session_state['xt_secret'] = XT_SECRET_KEY

# ابزارهای کنترل بازار و انتخاب ارز
st.header("🛠️ ۱. تنظیمات بازار و دارایی")
col_a, col_b, col_c = st.columns(3)
with col_a:
    symbol_input = st.text_input("🪙 نام ارز (BTC, ETH, SOL):", "BTC").upper().strip()
with col_b:
    timeframe = st.selectbox("⏳ زیر نظر گرفتن بازار (تایم‌فریم):", ["1m", "5m", "15m", "1h", "2h", "4h", "1d"])
with col_c:
    trade_amount = st.number_input("💵 حجم معامله (USDT):", min_value=5.0, value=10.0, step=1.0)

# کادر دستورات اختصاصی به زبان فارسی
custom_command = st.text_area("📝 دریافت سایر دستورات با زبان فارسی (اختیاری):", placeholder="مثلاً: بگو آیا الان زمان مناسبی برای ورود پله‌ای هست یا خیر؟")

st.markdown("---")

# تابع محاسبه اندیکاتورها برای زیر نظر گرفتن بازار
def get_market_data(pair, tf):
    exchange = ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})
    ticker = exchange.fetch_ticker(pair)
    ohlcv = exchange.fetch_ohlcv(pair, timeframe=tf, limit=50)
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    
    # اندیکاتورها
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA30'] = df['close'].rolling(window=30).mean()
    
    return ticker, df.iloc[-1]

# دکمه‌های عملیاتی اتاق فرمان
st.header("🚀 ۲. عملیات و صدور فرمان")
col1, col2, col3 = st.columns(3)

# بخش دریافت مانده حساب
with col1:
    st.markdown('<div class="balance-btn">', unsafe_allow_html=True)
    check_balance = st.button("💰 دریافت مانده حساب XT")
    st.markdown('</div>', unsafe_allow_html=True)

# بخش سیگنال اسپات
with col2:
    st.markdown('<div class="spot-btn">', unsafe_allow_html=True)
    get_spot = st.button("🟢 دریافت سیگنال اسپات")
    st.markdown('</div>', unsafe_allow_html=True)

# بخش سیگنال فیوچرز
with col3:
    st.markdown('<div class="futures-btn">', unsafe_allow_html=True)
    get_futures = st.button("🔴 دریافت سیگنال فیوچرز")
    st.markdown('</div>', unsafe_allow_html=True)

# پردازش دکمه دریافت مانده
if check_balance:
    if not XT_API_KEY or not XT_SECRET_KEY:
        st.error("❌ ابتدا کلیدهای صرافی XT را در سمت چپ وارد کنید.")
    else:
        try:
            exchange = ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})
            balance = exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0.0)
            st.info(f"💵 موجودی آزاد شما در صرافی XT: {usdt_balance:.2f} USDT")
        except Exception as e:
            st.error(f"خطا در دریافت موجودی: {e}")

# پردازش سیگنال‌ها و تحلیل بازار
if get_spot or get_futures:
    if not GEMINI_API_KEY or not XT_API_KEY or not XT_SECRET_KEY:
        st.error("❌ لطفاً ابتدا تمام کلیدهای API را در منوی سمت چپ وارد کنید.")
    else:
        mode_text = "اسپات (Spot)" if get_spot else "فیوچرز (Futures)"
        with st.spinner(f"⏳ در حال زیر نظر گرفتن بازار در تایم‌فریم {timeframe} برای سیگنال {mode_text}..."):
            try:
                pair = f"{symbol_input}/USDT"
                ticker, last_row = get_market_data(pair, timeframe)
                genai.configure(api_key=GEMINI_API_KEY)
                
                market_info = (
                    f"Market: {pair} | Timeframe: {timeframe}\n"
                    f"Current Price: {ticker['last']} USDT ({ticker['percentage']}%)\n"
                    f"RSI: {last_row['RSI']:.2f} | MA10: {last_row['MA10']:.2f} | MA30: {last_row['MA30']:.2f}\n"
                )
                
                system_instruction = (
                    f"تو یک دستیار ترید فوق‌حرفه‌ای هستی. حتماً پاسخ را با 'سلام غلامرضا جان!' شروع کن.\n"
                    f"بر اساس دیتای بازار، یک تحلیل صریح و یک سیگنال دقیق مخصوص بازار **{mode_text}** صادر کن.\n"
                    f"باید شامل: ۱. نوع پوزیشن ۲. قیمت ورود ۳. حد سودها ۴. حد ضرر قطعی باشد.\n"
                )
                if get_futures:
                    system_instruction += "چون سیگنال فیوچرز است، لوریج (Leverage) پیشنهادی و مناسب را هم ذکر کن.\n"
                if custom_command:
                    system_instruction += f"ضمناً به این درخواست فارسی کاربر هم دقیق پاسخ بده: {custom_command}\n"
                
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(f"{system_instruction}\n\nData:\n{market_info}")
                
                st.session_state['last_price'] = ticker['last']
                st.session_state['symbol'] = pair
                
                st.markdown(f"""
                <div style="background-color: #161A1E; color: #EAECEF; padding: 25px; border-radius: 12px; border-right: 10px solid #F3BA2F; font-family: 'Tahoma'; direction: rtl; text-align: right; line-height: 1.8;">
                    <h3 style="color: #F3BA2F; margin-top: 0;">📊 سیگنال خروجی اتاق فرمان مهدوی ({mode_text})</h3>
                    <div>{response.text.replace('\n', '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ خطا در تحلیل: {e}")

# بخش سوم: تایید و ارسال سفارش به صرافی
if 'last_price' in st.session_state:
    st.markdown("---")
    st.header("🛒 ۳. تایید نهایی و ارسال سفارش به صرافی XT")
    current_pair = st.session_state['symbol']
    suggested_price = st.session_state['last_price']
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        order_type = st.selectbox("نوع سفارش:", ["Limit (قیمت ثابت)", "Market (قیمت لحظه‌ای)"])
    with col_p2:
        final_price = st.number_input("قیمت معامله (USDT):", value=float(suggested_price), step=0.01)
        
    amount_to_trade = trade_amount / final_price
    st.warning(f" مقدار معامله: {amount_to_trade:.6f} {current_pair}")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🟢 ارسال دستور خرید به صرافی"):
            try:
                exchange = ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})
                order = exchange.create_market_buy_order(current_pair, amount_to_trade) if order_type == "Market (قیمت لحظه‌ای)" else exchange.create_limit_buy_order(current_pair, amount_to_trade, final_price)
                st.success(f"✅ سفارش خرید ثبت شد! شناسه: {order['id']}")
            except Exception as e: st.error(f"خطا: {e}")
    with col_b2:
        if st.button("🔴 ارسال دستور فروش به صرافی"):
            try:
                exchange = ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})
                order = exchange.create_market_sell_order(current_pair, amount_to_trade) if order_type == "Market (قیمت لحظه‌ای)" else exchange.create_limit_sell_order(current_pair, amount_to_trade, final_price)
                st.success(f"✅ سفارش فروش ثبت شد! شناسه: {order['id']}")
            except Exception as e: st.error(f"خطا: {e}")