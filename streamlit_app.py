import streamlit as st
import google.generativeai as genai
import ccxt
import pandas as pd

# تنظیمات اصلی صفحه با استایل حرفه‌ای صرافی
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", page_icon="📊", layout="wide")

# اعمال فونت و استایل‌های فوق‌العاده شیک CSS برای ظاهر پلتفرم ترید
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;500;800&display=swap');
    * { font-family: 'Vazirmatn', sans-serif !important; }
    .reportview-container { background: #0B0E11; color: #EAECEF; }
    h1 { color: #F3BA2F; text-align: center; font-weight: 800; font-size: 28px; margin-bottom: 25px; }
    h2, h3 { color: #F3BA2F; font-weight: 500; }
    .stButton>button {
        background: linear-gradient(135deg, #F3BA2F 0%, #D49B00 100%); color: #0B0E11; 
        font-weight: bold; width: 100%; border-radius: 8px; font-size: 15px; height: 45px; border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(243, 186, 47, 0.3); }
    .btn-balance>button { background: #2B3139 !important; color: #F3BA2F !important; border: 1px solid #F3BA2F !important; }
    .btn-spot>button { background: linear-gradient(135deg, #02C076 0%, #018F57 100%) !important; color: white !important; }
    .btn-futures>button { background: linear-gradient(135deg, #CD2026 0%, #A11318 100%) !important; color: white !important; }
    .card { background-color: #161A1E; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; margin-bottom: 15px; }
    .crypto-table { width: 100%; border-collapse: collapse; margin-top: 15px; direction: rtl; }
    .crypto-table th { background-color: #1F2226; color: #848E9C; text-align: right; padding: 12px; font-size: 14px; }
    .crypto-table td { padding: 12px; border-bottom: 1px solid #2B3139; font-size: 15px; text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🪐 اتاق فرمان هوشمند و سامانه معاملات زنده غلامرضا مهدوی</h1>", unsafe_allow_html=True)

# مدیریت حافظه کلیدها در مرورگر
if 'gemini_key' not in st.session_state: st.session_state['gemini_key'] = ""
if 'xt_key' not in st.session_state: st.session_state['xt_key'] = ""
if 'xt_secret' not in st.session_state: st.session_state['xt_secret'] = ""
if 'last_signal' not in st.session_state: st.session_state['last_signal'] = {}

# منوی سمت چپ برای کلیدهای امنیتی
st.sidebar.markdown("<h3 style='text-align: center;'>🔑 کلیدهای امنیتی</h3>", unsafe_allow_html=True)
GEMINI_API_KEY = st.sidebar.text_input("کلید Gemini API:", value=st.session_state['gemini_key'], type="password")
XT_API_KEY = st.sidebar.text_input("کلید XT API Key:", value=st.session_state['xt_key'], type="password")
XT_SECRET_KEY = st.sidebar.text_input("کلید XT Secret Key:", value=st.session_state['xt_secret'], type="password")

st.session_state['gemini_key'] = GEMINI_API_KEY
st.session_state['xt_key'] = XT_API_KEY
st.session_state['xt_secret'] = XT_SECRET_KEY

# چیدمان ستونی و حرفه‌ای بخش تنظیمات اصلی
st.markdown("<div class='card'><h3>🛠️ تنظیمات و رصد زنده بازار</h3>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    symbol_input = st.text_input("🪙 نام ارز دیجیتال (مثلاً BTC, ETH, SOL):", "BTC").upper().strip()
with col_b:
    timeframe = st.selectbox("⏳ بازه زمانی رصد بازار (تایم‌فریم):", ["1m", "5m", "15m", "1h", "2h", "4h", "1d"], index=3)

custom_command = st.text_area("📝 دستورات اختصاصی به زبان فارسی (اختیاری):", placeholder="مثلاً: بگو روند بازار در میان‌مدت صعودی است یا نزولی؟")
st.markdown("</div>", unsafe_allow_html=True)

# تابع اتصال به صرافی XT
def get_xt_instance():
    return ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})

# تابع استخراج و محاسبه اندیکاتورهای واقعی بازار
def fetch_real_indicators(pair, tf):
    exchange = get_xt_instance()
    ticker = exchange.fetch_ticker(pair)
    ohlcv = exchange.fetch_ohlcv(pair, timeframe=tf, limit=50)
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    
    # محاسبه اندیکاتورهای دقیق ریاضی
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA30'] = df['close'].rolling(window=30).mean()
    
    return ticker, df.iloc[-1]

# ردیف دکمه‌های عملیاتی اصلی با استایل صرافی
st.markdown("<h3>🚀 منوی فرمان‌های زنده صرافی</h3>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="btn-balance">', unsafe_allow_html=True)
    btn_bal = st.button("💰 دریافت مانده حساب")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="btn-spot">', unsafe_allow_html=True)
    btn_spot = st.button("🟢 سیگنال اسپات")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="btn-futures">', unsafe_allow_html=True)
    btn_futures = st.button("🔴 سیگنال فیوچرز")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    btn_positions = st.button("📂 پوزیشن‌های باز زنده")

# پیاده‌سازی دریافت واقعی موجودی حساب
if btn_bal:
    if not XT_API_KEY or not XT_SECRET_KEY:
        st.error("❌ لطفاً ابتدا کلیدهای API صرافی XT را در سمت چپ وارد کنید.")
    else:
        try:
            exchange = get_xt_instance()
            balance = exchange.fetch_balance()
            usdt_free = balance.get('USDT', {}).get('free', 0.0)
            st.markdown(f"""
            <div class='card' style='border-right: 5px solid #F3BA2F;'>
                <span style='font-size: 18px; font-weight: bold; color: #F3BA2F;'>موجودی حساب زنده صرافی XT:</span>
                <span style='font-size: 22px; font-weight: bold; margin-right: 15px;'>{usdt_free:.2f} USDT</span>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ خطا در دریافت موجودی از صرافی: {e}")

# پیاده‌سازی سیگنال اسپات و فیوچرز کاملاً واقعی با Gemini 2.5
if btn_spot or btn_futures:
    if not GEMINI_API_KEY or not XT_API_KEY or not XT_SECRET_KEY:
        st.error("❌ برای شروع تحلیل، لطفاً تمام کلیدهای سمت چپ را کامل کنید.")
    else:
        mode = "Spot" if btn_spot else "Futures"
        with st.spinner(f"⏳ در حال تحلیل زنده بازار {symbol_input} در تایم‌فریم {timeframe}..."):
            try:
                pair = f"{symbol_input}/USDT"
                ticker, indicators = fetch_real_indicators(pair, timeframe)
                genai.configure(api_key=GEMINI_API_KEY)
                
                market_text = (
                    f"Asset: {pair} | Interval: {timeframe}\n"
                    f"Live Price: {ticker['last']} USDT ({ticker['percentage']}%)\n"
                    f"RSI (14): {indicators['RSI']:.2f} | MA10: {indicators['MA10']:.2f} | MA30: {indicators['MA30']:.2f}\n"
                )
                
                prompt = (
                    f"تو یک دستیار ترید ارشد و فوق‌حرفه‌ای هستی. پاسخ را صمیمانه با 'سلام غلامرضا جان!' شروع کن.\n"
                    f"دیتای زنده بازار را تحلیل کن و یک سیگنال دقیق و صریح برای بازار **{mode}** صادر کن.\n"
                    f"فرمت خروجی باید کاملاً منظم و شامل نوع پوزیشن، قیمت ورود عددی، حد سودها و حد ضرر باشد.\n"
                )
                if btn_futures:
                    prompt += "به عنوان یک تریدر حرفه‌ای، لوریج مناسب و پیشنهادی را هم ذکر کن.\n"
                if custom_command:
                    prompt += f"به این درخواست اختصاصی کاربر هم پاسخ بده: {custom_command}\n"
                
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(f"{prompt}\n\nData:\n{market_text}")
                
                # ثبت اطلاعات سیگنال در حافظه برای اجرای سریع سفارش
                st.session_state['last_signal'] = {
                    'symbol': pair,
                    'price': float(ticker['last']),
                    'mode': mode
                }
                
                st.markdown(f"""
                <div style="background-color: #161A1E; padding: 25px; border-radius: 12px; border-right: 8px solid #F3BA2F; direction: rtl; text-align: right; line-height: 1.8; margin-top: 15px;">
                    <h3 style="color: #F3BA2F; margin-top:0;">📊 خروجی رصد هوشمند اتاق فرمان ({mode})</h3>
                    <div style="font-size: 16px; color: #EAECEF;">{response.text.replace('\n', '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ خطا در زیر نظر گرفتن بازار: {e}")

# پیاده‌سازی بخش نمایش گرافیکی پوزیشن‌های باز زنده صرافی
if btn_positions:
    if not XT_API_KEY or not XT_SECRET_KEY:
        st.error("❌ ابتدا کلیدهای صرافی XT را وارد کنید.")
    else:
        try:
            exchange = get_xt_instance()
            # دریافت پوزیشن‌های فیوچرز از صرافی
            positions = exchange.fetch_positions()
            active_positions = [p for p in positions if float(p.get('contracts', 0)) > 0]
            
            st.markdown("<h3>📂 لیست پوزیشن‌های باز زنده شما در صرافی</h3>", unsafe_allow_html=True)
            if not active_positions:
                st.info("ℹ️ در حال حاضر هیچ پوزیشن باز فعالی در صرافی XT یافت نشد.")
            else:
                html_table = "<table class='crypto-table'><tr><th>نماد ارز</th><th>نوع پوزیشن</th><th>حجم معامله</th><th>قیمت ورود</th><th>سود / زیان (PnL)</th></tr>"
                for pos in active_positions:
                    # رفع خطای سینتکس با قرار دادن کوتیشن برای مقادیر رنگ‌ها
                    side_color = "#02C076" if pos['side'] == 'long' else "#CD2026"
                    pnl_val = float(pos.get('unrealizedPnl', 0))
                    pnl_color = "#02C076" if pnl_val >= 0 else "#CD2026"
                    html_table += f"""
                    <tr>
                        <td style='font-weight: bold;'>{pos['symbol']}</td>
                        <td style='color: {side_color}; font-weight: bold;'>{pos['side'].upper()}</td>
                        <td>{pos['contracts']}</td>
                        <td>{pos['entryPrice']} USDT</td>
                        <td style='color: {pnl_color}; font-weight: bold;'>{pnl_val:.2f} USDT</td>
                    </tr>
                    """
                html_table += "</table>"
                st.markdown(html_table, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ خطا در استخراج پوزیشن‌ها از صرافی: {e}")

# منوی جدید اجرای سیگنال زنده و بستن پوزیشن‌ها
if st.session_state['last_signal']:
    sig = st.session_state['last_signal']
    st.markdown("---")
    st.markdown(f"<div class='card'><h3>🛒 ۳. سیستم مدیریت پوزیشن و اجرای زنده ({sig['symbol']})</h3>", unsafe_allow_html=True)
    
    col_x, col_y = st.columns(2)
    with col_x:
        st.markdown('<div class="btn-spot">', unsafe_allow_html=True)
        btn_exec = st.button("⚡ اجرای سریع سیگنال دریافتی بازار")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_y:
        st.markdown('<div class="btn-futures">', unsafe_allow_html=True)
        btn_close = st.button("🛑 بستن فوری تمام پوزیشن‌های این ارز")
        st.markdown('</div>', unsafe_allow_html=True)
        
    if btn_exec:
        try:
            exchange = get_xt_instance()
            # ارسال سفارش مارکت (قیمت لحظه‌ای) بر اساس حداقل حجم مجاز
            order = exchange.create_market_buy_order(sig['symbol'], 0.001) if sig['mode'] == 'Spot' else exchange.create_market_order(sig['symbol'], 'buy', 0.001)
            st.success(f"✅ سیگنال با موفقیت روی قیمت بازار اجرا شد! شناسه سفارش: {order['id']}")
        except Exception as e:
            st.error(f"❌ خطا در اجرای سریع سفارش: {e}")
            
    if btn_close:
        try:
            exchange = get_xt_instance()
            order = exchange.create_market_sell_order(sig['symbol'], 0.001)
            st.success(f"🛑 دستور بستن پوزیشن با موفقیت به صرافی XT ارسال شد. شناسه: {order['id']}")
        except Exception as e:
            st.error(f"❌ خطا در بستن پوزیشن: {e}")
            
    st.markdown("</div>", unsafe_allow_html=True)