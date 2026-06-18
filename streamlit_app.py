import streamlit as st
import google.generativeai as genai
import ccxt
import pandas as pd

# تنظیمات ظاهر صفحه به حالت تاریک و صرافی
st.set_page_config(page_title="اتاق فرمان غلامرضا جان", page_icon="📊", layout="centered")

st.markdown("""
    <style>
    .reportview-container { background: #0B0E11; }
    h1 { color: #F3BA2F; text-align: center; font-family: 'Tahoma'; }
    .stButton>button {
        background-color: #F3BA2F; color: #0B0E11; font-weight: bold;
        width: 100%; border-radius: 8px; font-size: 18px; height: 50px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🪐 اتاق فرمان و صدور سیگنال")

# کادرهای دریافت کلید امنیتی و کادر سوال
GEMINI_API_KEY = st.text_input("🔑 کلید Gemini API را وارد کنید:", type="password")
XT_API_KEY = st.text_input("🔑 کلید XT API Key را وارد کنید:", type="password")
XT_SECRET_KEY = st.text_input("🔑 کلید XT Secret Key را وارد کنید:", type="password")

st.markdown("---")
User_Command = st.text_area("📝 دستور یا سوال خود را اینجا بنویسید:", "سیگنال بیت‌کوئین در تایم‌فریم ۱ ساعته با جزئیات کامل")

def calculate_rsi(series, period=14):
    try:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    except:
        return pd.Series([50] * len(series))

if st.button("🚀 دریافت سیگنال و تحلیل زنده"):
    if not GEMINI_API_KEY or not XT_API_KEY or not XT_SECRET_KEY:
        st.error("❌ لطفاً ابتدا تمام کلیدهای API را در کادرهای بالا وارد کنید.")
    else:
        with st.spinner("⏳ در حال استخراج دیتای زنده صرافی XT و تحلیل هوش مصنوعی..."):
            try:
                exchange = ccxt.xt({'apiKey': XT_API_KEY, 'secret': XT_SECRET_KEY, 'enableRateLimit': True})
                genai.configure(api_key=GEMINI_API_KEY)
                
                ticker = exchange.fetch_ticker('BTC/USDT')
                ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=50)
                df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                
                df['MA10'] = df['close'].rolling(window=10).mean()
                df['MA30'] = df['close'].rolling(window=30).mean()
                df['RSI'] = calculate_rsi(df['close'])
                
                btc_intelligence = (
                    f"Live Technical Data (BTC/USDT - 1h):\n"
                    f"- Last Price: {ticker['last']} USDT\n"
                    f"- 24h Change: {ticker['percentage']}%\n"
                    f"- Current RSI (1h): {df['RSI'].iloc[-1]:.2f}\n"
                    f"- MA10 (1h): {df['MA10'].iloc[-1]:.2f}\n"
                    f"- MA30 (1h): {df['MA30'].iloc[-1]:.2f}\n"
                )

                system_instruction = (
                    "تو یک دستیار ترید فوق‌حرفه‌ای، صمیمی و کاملاً صریح هستی. حاشیه نرو و مقدمه اضافی نچین. "
                    "پاسخ تو به هر سوالی باید بسیار کوتاه، تمیز، دقیق و مستقیم باشد. "
                    "حتماً و بدون استثنا پاسخ خود را با عبارت صمیمی 'سلام غلامرضا جان!' شروع کن.\n\n"
                    "اگر کاربر سیگنال خواست، باید دقیقاً یک قالب منظم شامل موارد زیر با قیمت‌های عددی واقعی بر اساس دیتای دریافتی تحویل دهی:\n"
                    "۱. نوع سیگنال (خرید/فروش/صبر)\n"
                    "۲. قیمت دقیق ورود (Entry Price)\n"
                    "۳. هدف یا قیمت خروج (Take Profit - حداقل یک یا دو تارگت)\n"
                    "۴. حد ضرر قطعی (Stop Loss)\n"
                    "پاسخ باید منظم باشد."
                )
                
                final_prompt = f"{system_instruction}\n\n{btc_intelligence}\n\nسوال کاربر: {User_Command}"
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(final_prompt)
                
                formatted_text = response.text.replace("\n", "<br>")
                st.markdown(f"""
                <div style="background-color: #161A1E; color: #EAECEF; padding: 25px; border-radius: 12px; border-right: 10px solid #F3BA2F; font-family: 'Tahoma', sans-serif; line-height: 1.9; direction: rtl; text-align: right;">
                    <h3 style="color: #F3BA2F; margin-top: 0; font-size: 22px;">📊 پاسخ مستقیم و کامل اتاق فرمان</h3>
                    <div style="font-size: 20px; font-weight: bold;">{formatted_text}</div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ خطا در ارتباط با صرافی یا هوش مصنوعی: {e}")