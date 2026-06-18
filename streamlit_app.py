import streamlit as st
import google.generativeai as genai
import ccxt
import pandas as pd

# ۱. تنظیمات پایه‌ای صفحه
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", page_icon="📊", layout="wide")

# ۲. استایل‌دهی فوق‌العاده شیک و مدرن تیره صرافی با راست‌چین کامل
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;500;800&display=swap');
    * { font-family: 'Vazirmatn', sans-serif !important; direction: rtl !important; text-align: right !important; }
    .reportview-container { background: #0B0E11; color: #EAECEF; }
    
    /* استایل تیتر اصلی */
    .main-title { color: #F3BA2F; text-align: center !important; font-weight: 800; font-size: 28px; margin-bottom: 30px; }
    
    /* باکس‌های اطلاعاتی و کارت‌ها */
    .card { background-color: #161A1E; padding: 20px; border-radius: 12px; border: 1px solid #2B3139; margin-bottom: 20px; }
    
    /* استایل همگانی دکمه‌ها */
    .stButton>button {
        background: linear-gradient(135deg, #F3BA2F 0%, #D49B00 100%); color: #0B0E11 !important; 
        font-weight: bold; width: 100%; border-radius: 8px; font-size: 15px; height: 45px; border: none;
        transition: all 0.3s ease; cursor: pointer;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(243, 186, 47, 0.4); }
    
    /* دکمه‌های رنگی اختصاصی */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton>button { background: #2B3139 !important; color: #F3BA2F !important; border: 1px solid #F3BA2F !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton>button { background: linear-gradient(135deg, #02C076 0%, #018F57 100%) !important; color: white !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton>button { background: linear-gradient(135deg, #CD2026 0%, #A11318 100%) !important; color: white !important; }
    
    /* جدول پوزیشن‌ها */
    .crypto-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .crypto-table th { background-color: #1F2226; color: #848E9C; padding: 12px; font-size: 14px; }
    .crypto-table td { padding: 12px; border-bottom: 1px solid #2B3139; font-size: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🪐 اتاق فرمان هوشمند و سامانه معاملات زنده غلامرضا مهدوی</div>", unsafe_allow_html=True)

# ۳. مدیریت و قفل کردن داده‌ها در حافظه مرورگر (حلوگیری از حذف با رفرش)
for key in ['gemini_key', 'xt_key', 'xt_secret', 'last_price', 'symbol', 'mode', 'signal_output']:
    if key not in st.session_state:
        st.session_state[key] = "" if 'key' in key or 'output' in key or 'symbol' in key else 0.0

# ۴. بخش کلیدهای امنیتی (به صورت دکمه بازشونده شیک در سمت راست بالا)
with st.expander("🔑 تنظیمات و پیکربندی کلیدهای امنیتی API (کلیک کنید)"):
    gemini_inp = st.text_input("کلید Gemini API:", value=st.session_state['gemini_key'], type="password")
    xt_key_inp = st.text_input("کلید XT API Key:", value=st.session_state['xt_key'], type="password")
    xt_sec_inp = st.text_input("کلید XT Secret Key:", value=st.session_state['xt_secret'], type="password")
    if st.button("💾 ذخیره و قفل کردن کلیدها"):
        st.session_state['gemini_key'] = gemini_inp
        st.session_state['xt_key'] = xt_key_inp
        st.session_state['xt_secret'] = xt_sec_inp
        st.success("✅ کلیدها با موفقیت در حافظه مرورگر قفل شدند. منو را ببندید.")

# بارگذاری کلیدهای تایید شده
GEMINI_API_KEY = st.session_state['gemini_key']
XT_API_KEY = st.session_state['xt_key']
XT_SECRET_KEY = st.session_state['xt_secret']

# ۵. کارت تنظیمات رصد واقعی بازار
st.markdown("<div class='card'><h3>🛠️ رصد زنده و پایش بازار</h3>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    symbol_input = st.text_input("🪙 نام ارز دیجیتال (مثلاً BTC یا ETH):", "BTC").upper().strip()
with col_b:
    timeframe = st.selectbox("⏳ بازه زمانی پایش (تایم‌فریم):", ["1m", "5m", "15m", "1h", "2h", "4h", "1d"], index=3)

custom_command = st.text_area("📝 دستورات اختصاصی به زبان فارسی (اختیاری):", placeholder="مثلاً: آیا اندیکاتورها اشباع خرید نشان می‌دهند؟")
st.markdown("</div>", unsafe_allow_html=True)

# توابع عملیاتی صرافی XT
def get_xt_instance():
    return ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})

def fetch_real_indicators(pair, tf):
    exchange = get_xt_instance()
    ticker = exchange.fetch_ticker(pair)
    ohlcv = exchange.fetch_ohlcv(pair, timeframe=tf, limit=50)
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA30'] = df['close'].rolling(window=30).mean()
    
    return ticker, df.iloc[-1]

# ۶. چیدمان کاملاً منظم و راست‌چین دکمه‌های اصلی فرمان
st.markdown("<h3>🚀 منوی عملیات زنده اتاق فرمان</h3>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1: btn_bal = st.button("💰 دریافت مانده حساب")
with col2: btn_spot = st.button("🟢 سیگنال اسپات")
with col3: btn_futures = st.button("🔴 سیگنال فیوچرز")
with col4: btn_positions = st.button("📂 پوزیشن‌های باز زنده")

# عملیات ۱: دریافت مانده حساب واقعی
if btn_bal:
    if not XT_API_KEY: st.error("❌ ابتدا کلیدهای صرافی را وارد و ذخیره کنید.")
    else:
        try:
            exchange = get_xt_instance()
            balance = exchange.fetch_balance()
            usdt_free = balance.get('USDT', {}).get('free', 0.0)
            st.markdown(f"<div class='card' style='border-right: 5px solid #F3BA2F;'><b>موجودی زنده حساب صرافی:</b> {usdt_free:.2f} USDT</div>", unsafe_allow_html=True)
        except Exception as e: st.error(f"❌ خطا: {e}")

# عملیات ۲ و ۳: سیگنال‌دهی هوشمند بر اساس دیتای ۱۰۰٪ واقعی بازار
if btn_spot or btn_futures:
    if not GEMINI_API_KEY or not XT_API_KEY: st.error("❌ ابتدا کلیدهای منوی بالا را تنظیم و ذخیره کنید.")
    else:
        st.session_state['mode'] = "Spot" if btn_spot else "Futures"
        pair = f"{symbol_input}/USDT"
        st.session_state['symbol'] = pair
        
        with st.spinner(f"⏳ در حال رصد زنجیره‌ای بازار {pair}..."):
            try:
                ticker, indicators = fetch_real_indicators(pair, timeframe)
                genai.configure(api_key=GEMINI_API_KEY)
                
                st.session_state['last_price'] = float(ticker['last'])
                
                market_text = f"Asset: {pair} | TF: {timeframe}\nPrice: {ticker['last']} USDT\nRSI: {indicators['RSI']:.2f} | MA10: {indicators['MA10']:.2f}\n"
                prompt = f"تو دستیار ارشد مهدوی هستی. پاسخ را با 'سلام غلامرضا جان!' شروع کن. دیتای فوق را تحلیل فنی کن و سیگنال ورود/خروج صریح برای {st.session_state['mode']} بده."
                if custom_command: prompt += f"\nدرخواست کاربر: {custom_command}"
                
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(f"{prompt}\n\nData:\n{market_text}")
                st.session_state['signal_output'] = response.text
            except Exception as e: st.error(f"❌ خطا در رصد بازار: {e}")

# نمایش خروجی پایدار سیگنال (حتی بعد از رفرش صفحه غیب نمی‌شود)
if st.session_state['signal_output']:
    st.markdown(f"""
    <div style="background-color: #161A1E; padding: 20px; border-radius: 12px; border-right: 6px solid #F3BA2F; margin-top:15px;">
        <h3 style="color: #F3BA2F; margin-top:0;">📊 تحلیل و رصد هوشمند ({st.session_state['mode']})</h3>
        <div>{st.session_state['signal_output'].replace('\n', '<br>')}</div>
    </div>
    """, unsafe_allow_html=True)

# عملیات ۴: نمایش پوزیشن‌های باز
if btn_positions:
    if not XT_API_KEY: st.error("❌ ابتدا کلیدها را ست کنید.")
    else:
        try:
            exchange = get_xt_instance()
            positions = exchange.fetch_positions()
            active_positions = [p for p in positions if float(p.get('contracts', 0)) > 0]
            
            if not active_positions: st.info("ℹ️ هیچ پوزیشن فعالی در صرافی یافت نشد.")
            else:
                html_table = "<table class='crypto-table'><tr><th>نماد</th><th>نوع</th><th>حجم</th><th>قیمت ورود</th><th>سود و زیان (PnL)</th></tr>"
                for pos in active_positions:
                    s_col = "#02C076" if pos['side'] == 'long' else "#CD2026"
                    p_val = float(pos.get('unrealizedPnl', 0))
                    p_col = "#02C076" if p_val >= 0 else "#CD2026"
                    html_table += f"<tr><td><b>{pos['symbol']}</b></td><td style='color:{s_col};'>{pos['side'].upper()}</td><td>{pos['contracts']}</td><td>{pos['entryPrice']}</td><td style='color:{p_col};'>{p_val:.2f} USDT</td></tr>"
                html_table += "</table>"
                st.markdown(html_table, unsafe_allow_html=True)
        except Exception as e: st.error(f"❌ خطا: {e}")

# ۷. بخش اجرای سفارش زنده و بستن پوزیشن (همیشه پایدار و گوش به فرمان)
if st.session_state['last_price'] > 0:
    st.markdown("---")
    st.markdown(f"<div class='card'><h3>🛒 ۳. اجرای عملیاتی دستورات صرافی روی ({st.session_state['symbol']})</h3>", unsafe_allow_html=True)
    st.write(f"آخرین قیمت رصد شده مارکت: **{st.session_state['last_price']} USDT**")
    
    col_x, col_y = st.columns(2)
    with col_x: btn_exec = st.button("⚡ اجرای سریع سیگنال دریافتی بازار (خرید/ورود)")
    with col_y: btn_close = st.button("🛑 بستن فوری پوزیشن‌های این ارز (فروش/خروج)")
        
    if btn_exec:
        try:
            exchange = get_xt_instance()
            order = exchange.create_market_buy_order(st.session_state['symbol'], 0.001) if st.session_state['mode'] == 'Spot' else exchange.create_market_order(st.session_state['symbol'], 'buy', 0.001)
            st.success(f"✅ دستور ورود با موفقیت ارسال شد. شناسه: {order['id']}")
        except Exception as e: st.error(f"❌ خطا در اجرا: {e}")
            
    if btn_close:
        try:
            exchange = get_xt_instance()
            order = exchange.create_market_sell_order(st.session_state['symbol'], 0.001)
            st.success(f"🛑 دستور خروج/بستن با موفقیت ارسال شد. شناسه: {order['id']}")
        except Exception as e: st.error(f"❌ خطا در بستن: {e}")
    st.markdown("</div>", unsafe_allow_html=True)