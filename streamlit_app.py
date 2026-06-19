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

st.title("🪐 اتاق فرمان هوشمند غلامرضا مهدوی")

# پایدارسازی وضعیت سیستم
init_states = {
    'gemini': '', 
    'xt_key': '', 
    'xt_sec': '', 
    'current_view': 'home', 
    'persian_cmd': '', 
    'exec_confirm': False, 
    'scan_triggered': False
}
for k, v in init_states.items():
    if k not in st.session_state: 
        st.session_state[k] = v

PRICE_FEED = {"BTC": 67320.0, "ETH": 3555.0, "BNB": 588.0, "SOL": 149.2, "TON": 7.25, "XRP": 0.50, "ADA": 0.39, "DOGE": 0.12}

# سایدبار تنظیمات و منوها
with st.sidebar:
    st.header("🛠️ تنظیمات پلتفرم")
    with st.expander("🔑 کلیدهای امنیتی (API)"):
        g_inp = st.text_input("Gemini API Key", value=st.session_state['gemini'], type="password")
        k_inp = st.text_input("XT API Key", value=st.session_state['xt_key'], type="password")
        s_inp = st.text_input("XT Secret Key", value=st.session_state['xt_sec'], type="password")
        if st.button("💾 ذخیره کلیدها"):
            st.session_state['gemini'] = g_inp
            st.session_state['xt_key'] = k_inp
            st.session_state['xt_sec'] = s_inp
            st.success("✅ ذخیره شد.")

    st.header("🚀 منوی عملیات زنده")
    if st.button("💰 مانده کلی حساب"): 
        st.session_state['current_view'] = 'bal_total'
    if st.button("✍️ دستور فارسی هوش مصنوعی"): 
        st.session_state['current_view'] = 'persian_modal'

view = st.session_state['current_view']

if view == 'home':
    st.subheader("👋 سلام غلامرضا جان، خوش آمدی!")
    st.write("لطفاً از منوی سمت راست، گزینه مورد نظر خود را انتخاب کنید.")

elif view == 'persian_modal':
    st.subheader("✍️ ثبت دستورات فارسی اختصاصی و هوشمند پلتفرم")
    cmd_input = st.text_area("دستور یا استراتژی معاملاتی خود را بنویسید:", value=st.session_state['persian_cmd'])
    if st.button("💾 ثبت نهایی"):
        st.session_state['persian_cmd'] = cmd_input
        st.success("✅ دستور معاملاتی با موفقیت ثبت شد.")

elif view == 'bal_total':
    st.subheader("📊 موجودی واقعی و تفکیک شده کل حساب صرافی")
    
    if not st.session_state['xt_key'] or not st.session_state['xt_sec']:
        st.warning("⚠️ لطفاً ابتدا کلیدهای امنیتی (API) خود را در سایدبار سمت راست وارد و ذخیره کنید.")
    else:
        with st.spinner("🔄 در حال استعلام نهایی موجودی از سرور رسمی sapi.xt.com..."):
            usdt_spot = 0.0
            usdt_futures = 0.0
            
            # استعلام اسپات
            try:
                ts_spot = str(int(time.time() * 1000))
                path_spot = "/v4/balance"
                sign_str_spot = f"#{ts_spot}#GET#{path_spot}"
                sig_spot = hmac.new(st.session_state['xt_sec'].encode('utf-8'), sign_str_spot.encode('utf-8'), hashlib.sha256).hexdigest()
                
                headers_spot = {
                    "xt-validate-key": st.session_state['xt_key'],
                    "xt-validate-timestamp": ts_spot,
                    "xt-validate-signature": sig_spot
                }
                res_spot = requests.get(f"https://sapi.xt.com{path_spot}", headers=headers_spot, timeout=5)
                if res_spot.status_code == 200:
                    data_spot = res_spot.json()
                    if "result" in data_spot and isinstance(data_spot["result"], list):
                        for asset in data_spot["result"]:
                            if asset.get("currency", "").upper() == "USDT":
                                usdt_spot = float(asset.get("available", 0.0))
                                break
                else:
                    st.error(f"خطای اسپات: {res_spot.status_code}")
            except Exception as e:
                st.error(f"خطای اتصال اسپات: {str(e)}")

            # نمایش موجودی
            st.metric(label="🟢 موجودی حساب اسپات (Spot Wallet)", value=f"{usdt_spot:,.2f} USDT")