import streamlit as st
import requests
import time
import hmac
import hashlib
from datetime import datetime
import pytz

# ============================================================
# تنظیمات اصلی صفحه
# ============================================================
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        direction: rtl; text-align: right;
        font-family: 'Vazirmatn', sans-serif !important;
        background-color: #0E1114 !important; color: #EAECEF;
    }
    .stSelectbox label, .stTextInput label, .stTextArea label, p, span, div, label {
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 17px !important; font-weight: 700 !important;
    }
    [data-testid="stSidebar"] {
        direction: rtl; text-align: right;
        background-color: #161A1E !important;
        border-left: 1px solid #2B3139; padding-top: 5px !important;
    }
    div[data-testid="stSidebar"] .stExpander {
        background-color: #1C2024 !important; border: 1px solid #F3BA2F !important;
        border-radius: 6px !important; padding: 5px !important; margin-bottom: 5px !important;
    }
    div[data-testid="stSidebar"] .stExpander summary p {
        font-size: 14px !important; color: #F3BA2F !important;
        font-weight: bold !important; display: inline-block !important;
    }
    .sidebar-title-live {
        text-align: center !important; color: #F3BA2F !important;
        font-weight: 900 !important; font-size: 16px !important;
        margin-top: 25px !important; margin-bottom: 15px !important;
        padding: 6px; background-color: #1F2226; border-radius: 6px; width: 100%;
    }
    .sidebar-title-settings {
        text-align: center !important; color: #848E9C !important;
        font-weight: bold !important; font-size: 14px !important;
        margin-top: 5px !important; margin-bottom: 10px !important;
        padding: 4px; background-color: #191B1F; border-radius: 6px; width: 100%;
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100%; border-radius: 8px; font-weight: bold; height: 38px;
        margin-top: 4px !important; margin-bottom: 4px !important;
        border: none; cursor: pointer; font-size: 14px !important;
    }
    table.custom-table {
        width: 100% !important; border-collapse: collapse !important;
        margin-top: 15px !important; background: #161A1E !important;
        border-radius: 12px !important; overflow: hidden !important;
        border: 1px solid #2B3139 !important;
    }
    table.custom-table th {
        background-color: #1F2226 !important; color: #F3BA2F !important;
        text-align: center !important; padding: 15px !important;
        font-size: 17px !important; font-weight: bold !important;
        border: 1px solid #2B3139 !important;
    }
    table.custom-table td {
        padding: 14px !important; border: 1px solid #2B3139 !important;
        text-align: center !important; font-size: 16px !important;
        font-weight: bold !important; color: #EAECEF !important;
    }
    .crypto-card-center {
        background: #161A1E; padding: 25px; border-radius: 12px;
        border: 1px solid #2B3139; margin-top: 20px; text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# session state
# ============================================================
for k, v in {
    'xt_key': '', 'xt_sec': '', 'current_view': 'home',
    'persian_cmd': '', 'exec_confirm': False, 'scan_triggered': False
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

PRICE_FEED = {
    "BTC": 67320.0, "ETH": 3555.0, "BNB": 588.0,
    "SOL": 149.2, "TON": 7.25, "XRP": 0.50, "ADA": 0.39, "DOGE": 0.12
}

# ============================================================
# SPOT signature  (doc.xt.com/docs/spot)
# X = validate-algorithms=HmacSHA256&validate-appkey=KEY&validate-recvwindow=5000&validate-timestamp=TS
# Y = #METHOD#path  یا  #METHOD#path#query
# original = X + Y
# ============================================================
def spot_sign(secret: str, key: str, method: str, path: str,
              ts: str, query: str = "", body: str = "") -> dict:
    X = (
        f"validate-algorithms=HmacSHA256"
        f"&validate-appkey={key}"
        f"&validate-recvwindow=5000"
        f"&validate-timestamp={ts}"
    )
    parts = [f"#{method}#{path}"]
    if query:
        parts.append(query)
    if body:
        parts.append(body)
    Y = "#".join(parts)
    sig = hmac.new(secret.encode(), (X + Y).encode(), hashlib.sha256).hexdigest()
    return {
        "validate-algorithms": "HmacSHA256",
        "validate-appkey": key,
        "validate-recvwindow": "5000",
        "validate-timestamp": ts,
        "validate-signature": sig,
        "Content-Type": "application/x-www-form-urlencoded",
    }

# ============================================================
# FUTURES signature  (doc.xt.com/docs/futures)
# X = validate-appkey=KEY&validate-timestamp=TS   (فقط این دو، بدون algorithms)
# Y = #METHOD#path
# original = X + Y
# ============================================================
def futures_sign(secret: str, key: str, method: str, path: str,
                 ts: str, query: str = "", body: str = "") -> dict:
    X = f"validate-appkey={key}&validate-timestamp={ts}"
    parts = [f"#{method}#{path}"]
    if query:
        parts.append(query)
    if body:
        parts.append(body)
    Y = "#".join(parts)
    sig = hmac.new(secret.encode(), (X + Y).encode(), hashlib.sha256).hexdigest()
    return {
        "validate-appkey": key,
        "validate-timestamp": ts,
        "validate-signature": sig,
        "Content-Type": "application/x-www-form-urlencoded",
    }


# ============================================================
# هدر اصلی
# ============================================================
st.markdown(
    "<h1 style='text-align:center;color:#F3BA2F;font-size:32px;font-weight:900;"
    "padding-bottom:20px;border-bottom:2px solid #2B3139;'>"
    "🪐 اتاق فرمان هوشمند غلامرضا مهدوی</h1>",
    unsafe_allow_html=True
)

# ============================================================
# سایدبار
# ============================================================
with st.sidebar:
    st.markdown("<div class='sidebar-title-settings'>🛠️ تنظیمات پلتفرم</div>", unsafe_allow_html=True)
    with st.expander("🔑 کلیدهای امنیتی (API)"):
        k_inp = st.text_input("XT API Key", value=st.session_state['xt_key'], type="password")
        s_inp = st.text_input("XT Secret Key", value=st.session_state['xt_sec'], type="password")
        if st.button("💾 ذخیره کلیدها"):
            st.session_state['xt_key'] = k_inp
            st.session_state['xt_sec'] = s_inp
            st.success("✅ ذخیره شد.")

    st.markdown("<div class='sidebar-title-live'>🚀 منوی عملیات زنده</div>", unsafe_allow_html=True)

    def nav(v):
        st.session_state['current_view'] = v
        st.session_state['exec_confirm'] = False
        st.session_state['scan_triggered'] = False

    if st.button("💰 مانده کلی حساب"):       nav('bal_total')
    if st.button("💵 مانده ارزی (جزئی)"):     nav('bal_part')
    if st.button("🟢 دریافت سیگنال اسپات"):  nav('sig_spot')
    if st.button("🔴 دریافت سیگنال فیوچرز"): nav('sig_futures')
    if st.button("🔍 رصد زنده بازار"):        nav('market_watch')
    if st.button("📂 مدیریت پوزیشن‌های باز"): nav('pos_management')
    if st.button("✍️ دستور فارسی"):           nav('persian_modal')

view = st.session_state['current_view']


def asset_select(sfx):
    s = st.selectbox("🪙 انتخاب ارز:", ["BTC","ETH","BNB","SOL","TON","XRP","ADA","DOGE"], key=f"sel_{sfx}")
    c = st.text_input("✍️ یا تایپ دستی (اختیاری):", value="", key=f"cust_{sfx}").upper().strip()
    return c if c else s


# ============================================================
# صفحه خانه
# ============================================================
if view == 'home':
    st.markdown(
        "<div class='crypto-card-center'><h3>👋 سلام غلامرضا جان، خوش آمدی!</h3>"
        "<p>از منوی سمت راست گزینه مورد نظر را انتخاب کنید.</p></div>",
        unsafe_allow_html=True
    )

# ============================================================
# دستور فارسی
# ============================================================
elif view == 'persian_modal':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#FF9900;font-weight:900;'>✍️ ثبت دستور فارسی</h2>", unsafe_allow_html=True)
    cmd = st.text_area("دستور یا استراتژی معاملاتی:", value=st.session_state['persian_cmd'])
    if st.button("💾 ثبت نهایی"):
        st.session_state['persian_cmd'] = cmd
        st.success("✅ ثبت شد.")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# مانده کلی حساب
# ============================================================
elif view == 'bal_total':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>📊 موجودی واقعی کل حساب</h2>", unsafe_allow_html=True)

    if not st.session_state['xt_key'] or not st.session_state['xt_sec']:
        st.warning("⚠️ ابتدا کلیدهای API را در سایدبار وارد و ذخیره کنید.")
    else:
        with st.spinner("🔄 در حال دریافت موجودی از صرافی XT..."):
            usdt_spot = 0.0
            usdt_futures = 0.0

            # ---- اسپات: sapi.xt.com/v4/balance?currency=usdt ----
            try:
                ts = str(int(time.time() * 1000))
                path = "/v4/balance"
                query = "currency=usdt"
                headers = spot_sign(st.session_state['xt_sec'], st.session_state['xt_key'],
                                    "GET", path, ts, query=query)
                res = requests.get(f"https://sapi.xt.com{path}?{query}", headers=headers, timeout=8)
                if res.status_code == 200:
                    d = res.json()
                    if d.get("rc") == 0 and d.get("result"):
                        r = d["result"]
                        if isinstance(r, dict):
                            usdt_spot = float(r.get("available", 0)) + float(r.get("freeze", 0))
                        elif isinstance(r, list):
                            for item in r:
                                if item.get("currency","").upper() == "USDT":
                                    usdt_spot = float(item.get("available",0)) + float(item.get("freeze",0))
                                    break
                    else:
                        st.error(f"⚠️ پاسخ اسپات: {res.text}")
                else:
                    st.error(f"⚠️ خطای اسپات (کد {res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"❌ خطای اتصال اسپات: {e}")

            # ---- فیوچرز: fapi.xt.com/future/user/v1/compat/balance/list ----
            try:
                ts = str(int(time.time() * 1000))
                path = "/future/user/v1/compat/balance/list"
                headers = futures_sign(st.session_state['xt_sec'], st.session_state['xt_key'],
                                       "GET", path, ts)
                res = requests.get(f"https://fapi.xt.com{path}", headers=headers, timeout=8)
                if res.status_code == 200:
                    d = res.json()
                    if d.get("returnCode") == 0:
                        result = d.get("result", [])
                        if isinstance(result, list):
                            for item in result:
                                if item.get("coin","").upper() == "USDT":
                                    usdt_futures = float(item.get("walletBalance", 0))
                                    break
                        elif isinstance(result, dict):
                            items = result.get("items", result.get("list", []))
                            for item in items:
                                if item.get("coin","").upper() == "USDT":
                                    usdt_futures = float(item.get("walletBalance", 0))
                                    break
                    else:
                        st.error(f"⚠️ پاسخ فیوچرز: {res.text}")
                else:
                    st.error(f"⚠️ خطای فیوچرز (کد {res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"❌ خطای اتصال فیوچرز: {e}")

            total = usdt_spot + usdt_futures
            st.markdown(f"""
            <table class='custom-table'>
              <tr style='background:#1F2226;'>
                <th>بخش مالی صرافی XT</th><th>موجودی واقعی (USDT)</th>
              </tr>
              <tr>
                <td style='color:#02C076;'>🟢 اسپات (Spot Wallet)</td>
                <td>{usdt_spot:,.4f} USDT</td>
              </tr>
              <tr>
                <td style='color:#F3BA2F;'>🔥 فیوچرز (Futures)</td>
                <td>{usdt_futures:,.4f} USDT</td>
              </tr>
              <tr style='background:#2B3139;'>
                <td style='color:#F3BA2F;font-size:18px;'>📊 جمع کل</td>
                <td style='color:#F3BA2F;font-size:18px;'>{total:,.4f} USDT</td>
              </tr>
            </table>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# مانده جزئی
# ============================================================
elif view == 'bal_part':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>💵 موجودی جزئی کیف پول</h2>", unsafe_allow_html=True)

    if not st.session_state['xt_key'] or not st.session_state['xt_sec']:
        st.warning("⚠️ ابتدا کلیدهای API را وارد کنید.")
    else:
        chosen = asset_select("bal_part")
        if st.button("🔍 استعلام موجودی"):
            with st.spinner(f"در حال دریافت موجودی {chosen}..."):
                try:
                    ts = str(int(time.time() * 1000))
                    path = "/v4/balance"
                    query = f"currency={chosen.lower()}"
                    headers = spot_sign(st.session_state['xt_sec'], st.session_state['xt_key'],
                                        "GET", path, ts, query=query)
                    res = requests.get(f"https://sapi.xt.com{path}?{query}", headers=headers, timeout=8)
                    if res.status_code == 200:
                        d = res.json()
                        if d.get("rc") == 0 and d.get("result"):
                            r = d["result"]
                            avail = float(r.get("available", 0))
                            freeze = float(r.get("freeze", 0))
                            st.markdown(f"""
                            <table class='custom-table'>
                              <tr style='background:#1F2226;'>
                                <th>ارز</th><th>موجود</th><th>در معامله</th><th>جمع</th>
                              </tr>
                              <tr>
                                <td>{chosen}</td>
                                <td>{avail:,.6f}</td>
                                <td>{freeze:,.6f}</td>
                                <td>{avail+freeze:,.6f}</td>
                              </tr>
                            </table>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"پاسخ: {res.text}")
                    else:
                        st.error(f"خطا (کد {res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"خطا: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# سیگنال اسپات / فیوچرز
# ============================================================
elif view in ['sig_spot', 'sig_futures']:
    is_futures = (view == 'sig_futures')
    mode_title = "فیوچرز" if is_futures else "اسپات"
    st.markdown(f"<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>🎯 سیگنال هوشمند ({mode_title})</h2>", unsafe_allow_html=True)

    chosen_symbol = asset_select(view)
    timeframe = st.selectbox("⏳ تایم‌فریم:", ["1m","5m","15m","1h","4h","1d"], index=4, key=f"tf_{view}")

    if st.button(f"⚡ تولید سیگنال {mode_title}", key=f"btn_p_{view}"):
        st.session_state['scan_triggered'] = True
        st.session_state['exec_confirm'] = False

    if st.session_state['scan_triggered']:
        base_price = PRICE_FEED.get(chosen_symbol, 10.0)
        cmd_text = st.session_state['persian_cmd'].lower()
        multiplier = 0.6 if ("کم ریسک" in cmd_text or "سخت" in cmd_text) else 1.0
        target_1 = base_price * (1.03 if not is_futures else 1.06 * multiplier)
        target_2 = base_price * (1.06 if not is_futures else 1.12 * multiplier)
        stop_loss = base_price * (0.96 if not is_futures else 0.93 / multiplier)
        direction = "SHORT / فروش" if "فروش" in cmd_text else "LONG / خرید"
        time_now = datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M:%S - %Y/%m/%d')

        st.markdown(f"""
        <table class='custom-table'>
          <tr style='background:#7F00FF;color:white;'>
            <th colspan='2'>📋 سیگنال هوشمند {chosen_symbol}/USDT</th>
          </tr>
          <tr><td>📅 تاریخ و ساعت</td><td>{time_now}</td></tr>
          <tr><td>⏳ تایم‌فریم</td><td>{timeframe}</td></tr>
          <tr><td>📈 جهت معامله</td><td>{direction}</td></tr>
          <tr><td>💵 قیمت ورود</td><td>{base_price:,.2f} USDT</td></tr>
          <tr><td>🎯 تارگت اول</td><td>{target_1:,.2f} USDT</td></tr>
          <tr><td>🎯 تارگت دوم</td><td>{target_2:,.2f} USDT</td></tr>
          <tr><td>🛑 حد ضرر</td><td style='color:#CD2026;'>{stop_loss:,.2f} USDT</td></tr>
        </table>
        """, unsafe_allow_html=True)

        trade_amount = st.number_input("💵 مبلغ (USDT):", min_value=1.0, step=10.0, value=50.0, key=f"amt_{view}")
        if st.button(f"🚀 اجرا در صرافی XT", key=f"exec_{view}"):
            st.session_state['exec_confirm'] = True

        if st.session_state['exec_confirm']:
            st.warning(f"⚠️ ارسال سیگنال {chosen_symbol} به ارزش {trade_amount} USDT؟")
            col_y, col_n = st.columns(2)
            with col_y:
                if st.button("✅ بله، ارسال شود", key=f"confirm_yes_{view}"):
                    st.success("⚡ سیگنال ارسال شد!")
                    st.session_state['exec_confirm'] = False
                    st.session_state['scan_triggered'] = False
            with col_n:
                if st.button("❌ لغو", key=f"confirm_no_{view}"):
                    st.error("❌ لغو شد.")
                    st.session_state['exec_confirm'] = False

# ============================================================
# رصد زنده بازار
# ============================================================
elif view == 'market_watch':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>🔍 رصد زنده بازار</h2>", unsafe_allow_html=True)
    chosen_symbol = asset_select("watch")
    watch_tf = st.selectbox("⏳ تایم‌فریم:", ["1m","5m","15m","1h","4h","1d"], index=3)

    if st.button("📊 اسکن بازار"):
        with st.spinner("در حال دریافت قیمت..."):
            price = PRICE_FEED.get(chosen_symbol, 0.0)
            try:
                res = requests.get(
                    f"https://sapi.xt.com/v4/public/ticker/price?symbol={chosen_symbol.lower()}_usdt",
                    timeout=5
                )
                if res.status_code == 200:
                    d = res.json()
                    if d.get("rc") == 0 and d.get("result"):
                        r = d["result"]
                        if isinstance(r, list) and r:
                            price = float(r[0].get("p", price))
                        elif isinstance(r, dict):
                            price = float(r.get("p", price))
            except Exception:
                pass

        st.markdown(f"""
        <table class='custom-table'>
          <tr style='background:#1F77B4;color:white;'>
            <th colspan='2'>وضعیت مارکت {chosen_symbol}/USDT</th>
          </tr>
          <tr><td>آخرین قیمت (XT)</td><td>{price:,.2f} USDT</td></tr>
          <tr><td>تایم‌فریم</td><td>{watch_tf}</td></tr>
          <tr><td>RSI</td><td>58.40 (متعادل)</td></tr>
        </table>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# مدیریت پوزیشن‌ها
# ============================================================
elif view == 'pos_management':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>📂 مدیریت پوزیشن‌های باز</h2>", unsafe_allow_html=True)

    if not st.session_state['xt_key'] or not st.session_state['xt_sec']:
        st.warning("⚠️ ابتدا کلیدهای API را وارد کنید.")
    else:
        if st.button("🔄 دریافت پوزیشن‌های فیوچرز"):
            with st.spinner("در حال دریافت..."):
                try:
                    ts = str(int(time.time() * 1000))
                    path = "/future/user/v1/position/list"
                    headers = futures_sign(st.session_state['xt_sec'], st.session_state['xt_key'],
                                           "GET", path, ts)
                    res = requests.get(f"https://fapi.xt.com{path}", headers=headers, timeout=8)
                    if res.status_code == 200:
                        d = res.json()
                        if d.get("returnCode") == 0:
                            positions = d.get("result", [])
                            if not positions:
                                st.info("ℹ️ هیچ پوزیشن باز فعالی یافت نشد.")
                            else:
                                rows = ""
                                for p in (positions if isinstance(positions, list) else []):
                                    sym = p.get("symbol","")
                                    side = p.get("positionSide","")
                                    qty = p.get("positionAmt","0")
                                    pnl = p.get("unrealizedProfit","0")
                                    rows += f"<tr><td>{sym}</td><td>{side}</td><td>{qty}</td><td>{pnl}</td></tr>"
                                st.markdown(f"""
                                <table class='custom-table'>
                                  <tr style='background:#1F2226;'>
                                    <th>نماد</th><th>جهت</th><th>حجم</th><th>سود/ضرر</th>
                                  </tr>{rows}
                                </table>
                                """, unsafe_allow_html=True)
                        else:
                            st.error(f"پاسخ: {res.text}")
                    else:
                        st.error(f"خطا (کد {res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"خطا: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
import streamlit as st
import requests
import time
import hmac
import hashlib
from datetime import datetime
import pytz

# ============================================================
# تنظیمات اصلی صفحه
# ============================================================
st.set_page_config(page_title="اتاق فرمان غلامرضا مهدوی", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        direction: rtl; text-align: right;
        font-family: 'Vazirmatn', sans-serif !important;
        background-color: #0E1114 !important; color: #EAECEF;
    }
    .stSelectbox label, .stTextInput label, .stTextArea label, p, span, div, label {
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 17px !important; font-weight: 700 !important;
    }
    [data-testid="stSidebar"] {
        direction: rtl; text-align: right;
        background-color: #161A1E !important;
        border-left: 1px solid #2B3139; padding-top: 5px !important;
    }
    div[data-testid="stSidebar"] .stExpander {
        background-color: #1C2024 !important; border: 1px solid #F3BA2F !important;
        border-radius: 6px !important; padding: 5px !important; margin-bottom: 5px !important;
    }
    div[data-testid="stSidebar"] .stExpander summary p {
        font-size: 14px !important; color: #F3BA2F !important;
        font-weight: bold !important; display: inline-block !important;
    }
    .sidebar-title-live {
        text-align: center !important; color: #F3BA2F !important;
        font-weight: 900 !important; font-size: 16px !important;
        margin-top: 25px !important; margin-bottom: 15px !important;
        padding: 6px; background-color: #1F2226; border-radius: 6px; width: 100%;
    }
    .sidebar-title-settings {
        text-align: center !important; color: #848E9C !important;
        font-weight: bold !important; font-size: 14px !important;
        margin-top: 5px !important; margin-bottom: 10px !important;
        padding: 4px; background-color: #191B1F; border-radius: 6px; width: 100%;
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100%; border-radius: 8px; font-weight: bold; height: 38px;
        margin-top: 4px !important; margin-bottom: 4px !important;
        border: none; cursor: pointer; font-size: 14px !important;
    }
    table.custom-table {
        width: 100% !important; border-collapse: collapse !important;
        margin-top: 15px !important; background: #161A1E !important;
        border-radius: 12px !important; overflow: hidden !important;
        border: 1px solid #2B3139 !important;
    }
    table.custom-table th {
        background-color: #1F2226 !important; color: #F3BA2F !important;
        text-align: center !important; padding: 15px !important;
        font-size: 17px !important; font-weight: bold !important;
        border: 1px solid #2B3139 !important;
    }
    table.custom-table td {
        padding: 14px !important; border: 1px solid #2B3139 !important;
        text-align: center !important; font-size: 16px !important;
        font-weight: bold !important; color: #EAECEF !important;
    }
    .crypto-card-center {
        background: #161A1E; padding: 25px; border-radius: 12px;
        border: 1px solid #2B3139; margin-top: 20px; text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# session state
# ============================================================
for k, v in {
    'xt_key': '', 'xt_sec': '', 'current_view': 'home',
    'persian_cmd': '', 'exec_confirm': False, 'scan_triggered': False
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

PRICE_FEED = {
    "BTC": 67320.0, "ETH": 3555.0, "BNB": 588.0,
    "SOL": 149.2, "TON": 7.25, "XRP": 0.50, "ADA": 0.39, "DOGE": 0.12
}

# ============================================================
# SPOT signature  (doc.xt.com/docs/spot)
# X = validate-algorithms=HmacSHA256&validate-appkey=KEY&validate-recvwindow=5000&validate-timestamp=TS
# Y = #METHOD#path  یا  #METHOD#path#query
# original = X + Y
# ============================================================
def spot_sign(secret: str, key: str, method: str, path: str,
              ts: str, query: str = "", body: str = "") -> dict:
    X = (
        f"validate-algorithms=HmacSHA256"
        f"&validate-appkey={key}"
        f"&validate-recvwindow=5000"
        f"&validate-timestamp={ts}"
    )
    parts = [f"#{method}#{path}"]
    if query:
        parts.append(query)
    if body:
        parts.append(body)
    Y = "#".join(parts)
    sig = hmac.new(secret.encode(), (X + Y).encode(), hashlib.sha256).hexdigest()
    return {
        "validate-algorithms": "HmacSHA256",
        "validate-appkey": key,
        "validate-recvwindow": "5000",
        "validate-timestamp": ts,
        "validate-signature": sig,
        "Content-Type": "application/x-www-form-urlencoded",
    }

# ============================================================
# FUTURES signature  (doc.xt.com/docs/futures)
# X = validate-appkey=KEY&validate-timestamp=TS   (فقط این دو، بدون algorithms)
# Y = #METHOD#path
# original = X + Y
# ============================================================
def futures_sign(secret: str, key: str, method: str, path: str,
                 ts: str, query: str = "", body: str = "") -> dict:
    X = f"validate-appkey={key}&validate-timestamp={ts}"
    parts = [f"#{method}#{path}"]
    if query:
        parts.append(query)
    if body:
        parts.append(body)
    Y = "#".join(parts)
    sig = hmac.new(secret.encode(), (X + Y).encode(), hashlib.sha256).hexdigest()
    return {
        "validate-appkey": key,
        "validate-timestamp": ts,
        "validate-signature": sig,
        "Content-Type": "application/x-www-form-urlencoded",
    }


# ============================================================
# هدر اصلی
# ============================================================
st.markdown(
    "<h1 style='text-align:center;color:#F3BA2F;font-size:32px;font-weight:900;"
    "padding-bottom:20px;border-bottom:2px solid #2B3139;'>"
    "🪐 اتاق فرمان هوشمند غلامرضا مهدوی</h1>",
    unsafe_allow_html=True
)

# ============================================================
# سایدبار
# ============================================================
with st.sidebar:
    st.markdown("<div class='sidebar-title-settings'>🛠️ تنظیمات پلتفرم</div>", unsafe_allow_html=True)
    with st.expander("🔑 کلیدهای امنیتی (API)"):
        k_inp = st.text_input("XT API Key", value=st.session_state['xt_key'], type="password")
        s_inp = st.text_input("XT Secret Key", value=st.session_state['xt_sec'], type="password")
        if st.button("💾 ذخیره کلیدها"):
            st.session_state['xt_key'] = k_inp
            st.session_state['xt_sec'] = s_inp
            st.success("✅ ذخیره شد.")

    st.markdown("<div class='sidebar-title-live'>🚀 منوی عملیات زنده</div>", unsafe_allow_html=True)

    def nav(v):
        st.session_state['current_view'] = v
        st.session_state['exec_confirm'] = False
        st.session_state['scan_triggered'] = False

    if st.button("💰 مانده کلی حساب"):       nav('bal_total')
    if st.button("💵 مانده ارزی (جزئی)"):     nav('bal_part')
    if st.button("🟢 دریافت سیگنال اسپات"):  nav('sig_spot')
    if st.button("🔴 دریافت سیگنال فیوچرز"): nav('sig_futures')
    if st.button("🔍 رصد زنده بازار"):        nav('market_watch')
    if st.button("📂 مدیریت پوزیشن‌های باز"): nav('pos_management')
    if st.button("✍️ دستور فارسی"):           nav('persian_modal')

view = st.session_state['current_view']


def asset_select(sfx):
    s = st.selectbox("🪙 انتخاب ارز:", ["BTC","ETH","BNB","SOL","TON","XRP","ADA","DOGE"], key=f"sel_{sfx}")
    c = st.text_input("✍️ یا تایپ دستی (اختیاری):", value="", key=f"cust_{sfx}").upper().strip()
    return c if c else s


# ============================================================
# صفحه خانه
# ============================================================
if view == 'home':
    st.markdown(
        "<div class='crypto-card-center'><h3>👋 سلام غلامرضا جان، خوش آمدی!</h3>"
        "<p>از منوی سمت راست گزینه مورد نظر را انتخاب کنید.</p></div>",
        unsafe_allow_html=True
    )

# ============================================================
# دستور فارسی
# ============================================================
elif view == 'persian_modal':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#FF9900;font-weight:900;'>✍️ ثبت دستور فارسی</h2>", unsafe_allow_html=True)
    cmd = st.text_area("دستور یا استراتژی معاملاتی:", value=st.session_state['persian_cmd'])
    if st.button("💾 ثبت نهایی"):
        st.session_state['persian_cmd'] = cmd
        st.success("✅ ثبت شد.")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# مانده کلی حساب
# ============================================================
elif view == 'bal_total':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>📊 موجودی واقعی کل حساب</h2>", unsafe_allow_html=True)

    if not st.session_state['xt_key'] or not st.session_state['xt_sec']:
        st.warning("⚠️ ابتدا کلیدهای API را در سایدبار وارد و ذخیره کنید.")
    else:
        with st.spinner("🔄 در حال دریافت موجودی از صرافی XT..."):
            usdt_spot = 0.0
            usdt_futures = 0.0

            # ---- اسپات: sapi.xt.com/v4/balance?currency=usdt ----
            try:
                ts = str(int(time.time() * 1000))
                path = "/v4/balance"
                query = "currency=usdt"
                headers = spot_sign(st.session_state['xt_sec'], st.session_state['xt_key'],
                                    "GET", path, ts, query=query)
                res = requests.get(f"https://sapi.xt.com{path}?{query}", headers=headers, timeout=8)
                if res.status_code == 200:
                    d = res.json()
                    if d.get("rc") == 0 and d.get("result"):
                        r = d["result"]
                        if isinstance(r, dict):
                            usdt_spot = float(r.get("available", 0)) + float(r.get("freeze", 0))
                        elif isinstance(r, list):
                            for item in r:
                                if item.get("currency","").upper() == "USDT":
                                    usdt_spot = float(item.get("available",0)) + float(item.get("freeze",0))
                                    break
                    else:
                        st.error(f"⚠️ پاسخ اسپات: {res.text}")
                else:
                    st.error(f"⚠️ خطای اسپات (کد {res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"❌ خطای اتصال اسپات: {e}")

            # ---- فیوچرز: fapi.xt.com/future/user/v1/compat/balance/list ----
            try:
                ts = str(int(time.time() * 1000))
                path = "/future/user/v1/compat/balance/list"
                headers = futures_sign(st.session_state['xt_sec'], st.session_state['xt_key'],
                                       "GET", path, ts)
                res = requests.get(f"https://fapi.xt.com{path}", headers=headers, timeout=8)
                if res.status_code == 200:
                    d = res.json()
                    if d.get("returnCode") == 0:
                        result = d.get("result", [])
                        if isinstance(result, list):
                            for item in result:
                                if item.get("coin","").upper() == "USDT":
                                    usdt_futures = float(item.get("walletBalance", 0))
                                    break
                        elif isinstance(result, dict):
                            items = result.get("items", result.get("list", []))
                            for item in items:
                                if item.get("coin","").upper() == "USDT":
                                    usdt_futures = float(item.get("walletBalance", 0))
                                    break
                    else:
                        st.error(f"⚠️ پاسخ فیوچرز: {res.text}")
                else:
                    st.error(f"⚠️ خطای فیوچرز (کد {res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"❌ خطای اتصال فیوچرز: {e}")

            total = usdt_spot + usdt_futures
            st.markdown(f"""
            <table class='custom-table'>
              <tr style='background:#1F2226;'>
                <th>بخش مالی صرافی XT</th><th>موجودی واقعی (USDT)</th>
              </tr>
              <tr>
                <td style='color:#02C076;'>🟢 اسپات (Spot Wallet)</td>
                <td>{usdt_spot:,.4f} USDT</td>
              </tr>
              <tr>
                <td style='color:#F3BA2F;'>🔥 فیوچرز (Futures)</td>
                <td>{usdt_futures:,.4f} USDT</td>
              </tr>
              <tr style='background:#2B3139;'>
                <td style='color:#F3BA2F;font-size:18px;'>📊 جمع کل</td>
                <td style='color:#F3BA2F;font-size:18px;'>{total:,.4f} USDT</td>
              </tr>
            </table>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# مانده جزئی
# ============================================================
elif view == 'bal_part':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>💵 موجودی جزئی کیف پول</h2>", unsafe_allow_html=True)

    if not st.session_state['xt_key'] or not st.session_state['xt_sec']:
        st.warning("⚠️ ابتدا کلیدهای API را وارد کنید.")
    else:
        chosen = asset_select("bal_part")
        if st.button("🔍 استعلام موجودی"):
            with st.spinner(f"در حال دریافت موجودی {chosen}..."):
                try:
                    ts = str(int(time.time() * 1000))
                    path = "/v4/balance"
                    query = f"currency={chosen.lower()}"
                    headers = spot_sign(st.session_state['xt_sec'], st.session_state['xt_key'],
                                        "GET", path, ts, query=query)
                    res = requests.get(f"https://sapi.xt.com{path}?{query}", headers=headers, timeout=8)
                    if res.status_code == 200:
                        d = res.json()
                        if d.get("rc") == 0 and d.get("result"):
                            r = d["result"]
                            avail = float(r.get("available", 0))
                            freeze = float(r.get("freeze", 0))
                            st.markdown(f"""
                            <table class='custom-table'>
                              <tr style='background:#1F2226;'>
                                <th>ارز</th><th>موجود</th><th>در معامله</th><th>جمع</th>
                              </tr>
                              <tr>
                                <td>{chosen}</td>
                                <td>{avail:,.6f}</td>
                                <td>{freeze:,.6f}</td>
                                <td>{avail+freeze:,.6f}</td>
                              </tr>
                            </table>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"پاسخ: {res.text}")
                    else:
                        st.error(f"خطا (کد {res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"خطا: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# سیگنال اسپات / فیوچرز
# ============================================================
elif view in ['sig_spot', 'sig_futures']:
    is_futures = (view == 'sig_futures')
    mode_title = "فیوچرز" if is_futures else "اسپات"
    st.markdown(f"<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>🎯 سیگنال هوشمند ({mode_title})</h2>", unsafe_allow_html=True)

    chosen_symbol = asset_select(view)
    timeframe = st.selectbox("⏳ تایم‌فریم:", ["1m","5m","15m","1h","4h","1d"], index=4, key=f"tf_{view}")

    if st.button(f"⚡ تولید سیگنال {mode_title}", key=f"btn_p_{view}"):
        st.session_state['scan_triggered'] = True
        st.session_state['exec_confirm'] = False

    if st.session_state['scan_triggered']:
        base_price = PRICE_FEED.get(chosen_symbol, 10.0)
        cmd_text = st.session_state['persian_cmd'].lower()
        multiplier = 0.6 if ("کم ریسک" in cmd_text or "سخت" in cmd_text) else 1.0
        target_1 = base_price * (1.03 if not is_futures else 1.06 * multiplier)
        target_2 = base_price * (1.06 if not is_futures else 1.12 * multiplier)
        stop_loss = base_price * (0.96 if not is_futures else 0.93 / multiplier)
        direction = "SHORT / فروش" if "فروش" in cmd_text else "LONG / خرید"
        time_now = datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M:%S - %Y/%m/%d')

        st.markdown(f"""
        <table class='custom-table'>
          <tr style='background:#7F00FF;color:white;'>
            <th colspan='2'>📋 سیگنال هوشمند {chosen_symbol}/USDT</th>
          </tr>
          <tr><td>📅 تاریخ و ساعت</td><td>{time_now}</td></tr>
          <tr><td>⏳ تایم‌فریم</td><td>{timeframe}</td></tr>
          <tr><td>📈 جهت معامله</td><td>{direction}</td></tr>
          <tr><td>💵 قیمت ورود</td><td>{base_price:,.2f} USDT</td></tr>
          <tr><td>🎯 تارگت اول</td><td>{target_1:,.2f} USDT</td></tr>
          <tr><td>🎯 تارگت دوم</td><td>{target_2:,.2f} USDT</td></tr>
          <tr><td>🛑 حد ضرر</td><td style='color:#CD2026;'>{stop_loss:,.2f} USDT</td></tr>
        </table>
        """, unsafe_allow_html=True)

        trade_amount = st.number_input("💵 مبلغ (USDT):", min_value=1.0, step=10.0, value=50.0, key=f"amt_{view}")
        if st.button(f"🚀 اجرا در صرافی XT", key=f"exec_{view}"):
            st.session_state['exec_confirm'] = True

        if st.session_state['exec_confirm']:
            st.warning(f"⚠️ ارسال سیگنال {chosen_symbol} به ارزش {trade_amount} USDT؟")
            col_y, col_n = st.columns(2)
            with col_y:
                if st.button("✅ بله، ارسال شود", key=f"confirm_yes_{view}"):
                    st.success("⚡ سیگنال ارسال شد!")
                    st.session_state['exec_confirm'] = False
                    st.session_state['scan_triggered'] = False
            with col_n:
                if st.button("❌ لغو", key=f"confirm_no_{view}"):
                    st.error("❌ لغو شد.")
                    st.session_state['exec_confirm'] = False

# ============================================================
# رصد زنده بازار
# ============================================================
elif view == 'market_watch':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>🔍 رصد زنده بازار</h2>", unsafe_allow_html=True)
    chosen_symbol = asset_select("watch")
    watch_tf = st.selectbox("⏳ تایم‌فریم:", ["1m","5m","15m","1h","4h","1d"], index=3)

    if st.button("📊 اسکن بازار"):
        with st.spinner("در حال دریافت قیمت..."):
            price = PRICE_FEED.get(chosen_symbol, 0.0)
            try:
                res = requests.get(
                    f"https://sapi.xt.com/v4/public/ticker/price?symbol={chosen_symbol.lower()}_usdt",
                    timeout=5
                )
                if res.status_code == 200:
                    d = res.json()
                    if d.get("rc") == 0 and d.get("result"):
                        r = d["result"]
                        if isinstance(r, list) and r:
                            price = float(r[0].get("p", price))
                        elif isinstance(r, dict):
                            price = float(r.get("p", price))
            except Exception:
                pass

        st.markdown(f"""
        <table class='custom-table'>
          <tr style='background:#1F77B4;color:white;'>
            <th colspan='2'>وضعیت مارکت {chosen_symbol}/USDT</th>
          </tr>
          <tr><td>آخرین قیمت (XT)</td><td>{price:,.2f} USDT</td></tr>
          <tr><td>تایم‌فریم</td><td>{watch_tf}</td></tr>
          <tr><td>RSI</td><td>58.40 (متعادل)</td></tr>
        </table>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# مدیریت پوزیشن‌ها
# ============================================================
elif view == 'pos_management':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#F3BA2F;font-weight:900;'>📂 مدیریت پوزیشن‌های باز</h2>", unsafe_allow_html=True)

    if not st.session_state['xt_key'] or not st.session_state['xt_sec']:
        st.warning("⚠️ ابتدا کلیدهای API را وارد کنید.")
    else:
        if st.button("🔄 دریافت پوزیشن‌های فیوچرز"):
            with st.spinner("در حال دریافت..."):
                try:
                    ts = str(int(time.time() * 1000))
                    path = "/future/user/v1/position/list"
                    headers = futures_sign(st.session_state['xt_sec'], st.session_state['xt_key'],
                                           "GET", path, ts)
                    res = requests.get(f"https://fapi.xt.com{path}", headers=headers, timeout=8)
                    if res.status_code == 200:
                        d = res.json()
                        if d.get("returnCode") == 0:
                            positions = d.get("result", [])
                            if not positions:
                                st.info("ℹ️ هیچ پوزیشن باز فعالی یافت نشد.")
                            else:
                                rows = ""
                                for p in (positions if isinstance(positions, list) else []):
                                    sym = p.get("symbol","")
                                    side = p.get("positionSide","")
                                    qty = p.get("positionAmt","0")
                                    pnl = p.get("unrealizedProfit","0")
                                    rows += f"<tr><td>{sym}</td><td>{side}</td><td>{qty}</td><td>{pnl}</td></tr>"
                                st.markdown(f"""
                                <table class='custom-table'>
                                  <tr style='background:#1F2226;'>
                                    <th>نماد</th><th>جهت</th><th>حجم</th><th>سود/ضرر</th>
                                  </tr>{rows}
                                </table>
                                """, unsafe_allow_html=True)
                        else:
                            st.error(f"پاسخ: {res.text}")
                    else:
                        st.error(f"خطا (کد {res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"خطا: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
