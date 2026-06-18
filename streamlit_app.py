import streamlit as st
import google.generativeai as genai
import ccxt
import pandas as pd

# تنظیمات ظاهر صفحه به حالت تاریک و صرافی
st.set_page_config(page_title="اتاق فرمان پیشرفته غلامرضا جان", page_icon="📊", layout="centered")

st.markdown("""
    <style>
    .reportview-container { background: #0B0E11; }
    h1 { color: #F3BA2F; text-align: center; font-family: 'Tahoma'; }
    .stButton>button {
        background-color: #F3BA2F; color: #0B0E11; font-weight: bold;
        width: 100%; border-radius: 8px; font-size: 18px; height: 45px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🪐 اتاق فرمان هوشمند و سامانه معاملات زنده")

# قفل کردن کلیدها در حافظه مرورگر برای جلوگیری از حذف با رفرش
if 'gemini_key' not in st.session_state: st.session_state['gemini_key'] = ""
if 'xt_key' not in st.session_state: st.session_state['xt_key'] = ""
if 'xt_secret' not in st.session_state: st.session_state['xt_secret'] = ""

# بخش دریافت کلیدها در منوی سمت چپ
st.sidebar.header("🔑 تنظیمات کلیدهای امنیتی")
GEMINI_API_KEY = st.sidebar.text_input("کلید Gemini API:", value=st.session_state['gemini_key'], type="password")
XT_API_KEY = st.sidebar.text_input("کلید XT API Key:", value=st.session_state['xt_key'], type="password")
XT_SECRET_KEY = st.sidebar.text_input("کلید XT Secret Key:", value=st.session_state['xt_secret'], type="password")

# به روز رسانی حافظه در صورت تغییر ورودی‌ها
st.session_state['gemini_key'] = GEMINI_API_KEY
st.session_state['xt_key'] = XT_API_KEY
st.session_state['xt_secret'] = XT_SECRET_KEY

# بخش انتخاب ارز و اندیکاتورها
col1, col2, col3 = st.columns(3)
with col1:
    symbol_input = st.text_input("🪙 نام ارز (مثلاً BTC یا ETH):", "BTC").upper().strip()
with col2:
    timeframe = st.selectbox("⏳ تایم‌فریم تحلیل:", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
with col3:
    trade_amount = st.number_input("💵 حجم معامله (USDT):", min_value=5.0, value=10.0, step=1.0)

st.markdown("---")

def calculate_indicators(df):
    try:
        # محاسبه RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # محاسبه میانگین‌های متحرک (MA)
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA30'] = df['close'].rolling(window=30).mean()
        
        # محاسبه باندهای بولینگر (Bollinger Bands)
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        df['BB_std'] = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
        df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)
        return df
    except:
        return df

# اجرای تحلیل و استخراج دیتای صرافی
if st.button("🚀 ۱. استخراج دیتای زنده و تحلیل هوش مصنوعی"):
    if not GEMINI_API_KEY or not XT_API_KEY or not XT_SECRET_KEY:
        st.error("❌ لطفاً ابتدا تمام کلیدهای API را در منوی سمت چپ (Sidebar) وارد کنید.")
    else:
        with st.spinner(f"⏳ در حال استخراج دیتای زنده {symbol_input}/USDT و تحلیل اندیکاتورها..."):
            try:
                pair = f"{symbol_input}/USDT"
                exchange = ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})
                genai.configure(api_key=GEMINI_API_KEY)
                
                ticker = exchange.fetch_ticker(pair)
                ohlcv = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=50)
                df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                
                df = calculate_indicators(df)
                
                market_intelligence = (
                    f"Live Market Data ({pair} - {timeframe}):\n"
                    f"- Current Price: {ticker['last']} USDT\n"
                    f"- 24h Change: {ticker['percentage']}%\n"
                    f"- RSI (14): {df['RSI'].iloc[-1]:.2f}\n"
                    f"- MA10: {df['MA10'].iloc[-1]:.2f}\n"
                    f"- MA30: {df['MA30'].iloc[-1]:.2f}\n"
                    f"- Bollinger Upper: {df['BB_upper'].iloc[-1]:.2f}\n"
                    f"- Bollinger Lower: {df['BB_lower'].iloc[-1]:.2f}\n"
                    f"- 24h Volume: {ticker['baseVolume']:.2f}\n"
                )

                system_instruction = (
                    "تو یک دستیار ترید فوق‌حرفه‌ای و کاملاً صریح هستی. حاشیه نرو. "
                    "حتماً پاسخ خود را با عبارت صمیمی 'سلام غلامرضا جان!' شروع کن.\n"
                    "تحلیل فنی دقیقی از اندیکاتورهای داده شده ارائه بده و سپس یک سیگنال دقیق با فرمت زیر بساز:\n"
                    "۱. نوع سیگنال (خرید/فروش/صبر)\n"
                    "۲. قیمت دقیق ورود (Entry Price)\n"
                    "۳. حد سود (Take Profit)\n"
                    "۴. حد ضرر قطعی (Stop Loss)"
                )
                
                final_prompt = f"{system_instruction}\n\n{market_intelligence}\n\nدرخواست: تحلیل کامل ارز و صدور سیگنال."
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(final_prompt)
                
                st.session_state['last_price'] = ticker['last']
                st.session_state['symbol'] = pair
                
                formatted_text = response.text.replace("\n", "<br>")
                st.markdown(f"""
                <div style="background-color: #161A1E; color: #EAECEF; padding: 25px; border-radius: 12px; border-right: 10px solid #F3BA2F; font-family: 'Tahoma'; line-height: 1.9; direction: rtl; text-align: right;">
                    <h3 style="color: #F3BA2F; margin-top: 0; font-size: 22px;">📊 پاسخ مستقیم اتاق فرمان</h3>
                    <div style="font-size: 18px;">{formatted_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ خطا در پردازش اطلاعات: {e}")

# بخش دوم: قرار دادن سفارش با تایید غلامرضا جان
if 'last_price' in st.session_state:
    st.markdown("---")
    st.header("🛒 ۲. بخش صدور و تایید نهایی سفارش صرافی")
    
    current_pair = st.session_state['symbol']
    suggested_price = st.session_state['last_price']
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        order_type = st.selectbox("نوع سفارش:", ["Limit (قیمت ثابت)", "Market (قیمت لحظه‌ای)"])
    with col_p2:
        final_price = st.number_input("قیمت خرید/فروش (USDT):", value=float(suggested_price), step=0.01)
        
    amount_to_trade = trade_amount / final_price
    st.warning(f"⚠️ مقدار محاسبه شده برای معامله: {amount_to_trade:.6f} از ارز {current_pair}")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button(f"🟢 تایید نهایی: ارسال دستور خرید به صرافی XT", key="buy_btn"):
            with st.spinner("🚀 در حال ارسال سفارش خرید به صرافی XT..."):
                try:
                    exchange = ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})
                    if order_type == "Market (قیمت لحظه‌ای)":
                        order = exchange.create_market_buy_order(current_pair, amount_to_trade)
                    else:
                        order = exchange.create_limit_buy_order(current_pair, amount_to_trade, final_price)
                    st.success(f"✅ سفارش خرید با موفقیت ثبت شد! شناسه سفارش: {order['id']}")
                except Exception as e:
                    st.error(f"❌ خطا در ارسال سفارش خرید: {e}")
                    
    with col_b2:
        if st.button(f"🔴 تایید نهایی: ارسال دستور فروش به صرافی XT", key="sell_btn"):
            with st.spinner("🚀 در حال ارسال سفارش فروش به صرافی XT..."):
                try:
                    exchange = ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})
                    if order_type == "Market (قیمت لحظه‌ای)":
                        order = exchange.create_market_sell_order(current_pair, amount_to_trade)
                    else:
                        order = exchange.create_limit_sell_order(current_pair, amount_to_trade, final_price)
                    st.success(f"✅ سفارش فروش با موفقیت ثبت شد! شناسه سفارش: {order['id']}")
                except Exception as e:
                    st.error(f"❌ خطا در ارسال سفارش فروش: {e}")