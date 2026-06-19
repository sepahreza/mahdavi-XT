# ۲. نمایش مانده واقعی و لحظه‌ای کل حساب صرافی XT
elif view == 'bal_total':
    st.markdown("<div class='crypto-card-center'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F3BA2F; font-weight: 900;'>📊 موجودی واقعی و تفکیک شده کل حساب صرافی</h2>", unsafe_allow_html=True)
    
    if not st.session_state['xt_key'] or not st.session_state['xt_sec']:
        st.warning("⚠️ غلامرضا جان، لطفاً ابتدا کلیدهای امنیتی (API Key و Secret Key) خود را در سایدبار سمت راست وارد و ذخیره کنید.")
    else:
        with st.spinner("🔄 در حال استعلام زنده و واقعی از صرافی XT..."):
            # آرایه مقادیر واقعی
            usdt_spot = 0.0
            usdt_futures = 0.0
            
            # --- ۱. فراخوانی موجودی واقعی اسپات ---
            spot_url = "https://api.xt.com/v4/balance"
            ts_spot = str(int(time.time() * 1000))
            # ساخت امضای استاندارد اسپات صرافی XT
            sign_str_spot = f"validate-algorithms#GET#/v4/balance#timestamp={ts_spot}"
            sig_spot = hmac.new(st.session_state['xt_sec'].encode('utf-8'), sign_str_spot.encode('utf-8'), hashlib.sha256).hexdigest()
            
            headers_spot = {
                "xt-validate-algorithms-key": st.session_state['xt_key'],
                "xt-validate-algorithms-timestamp": ts_spot,
                "xt-validate-algorithms-signature": sig_spot
            }
            
            try:
                res_spot = requests.get(spot_url, headers=headers_spot, timeout=5)
                if res_spot.status_code == 200:
                    data_spot = res_spot.json()
                    # فیلتر کردن دقیق تتر (USDT) در حساب اسپات شما
                    if "result" in data_spot and "balances" in data_spot["result"]:
                        for asset in data_spot["result"]["balances"]:
                            if asset.get("currency", "").upper() == "USDT":
                                usdt_spot = float(asset.get("available", 0.0)) + float(asset.get("freeze", 0.0))
                                break
            except Exception as e:
                st.error(f"❌ خطا در اتصال به بخش اسپات صرافی: {str(e)}")

            # --- ۲. فراخوانی موجودی واقعی فیوچرز ---
            future_url = "https://fapi.xt.com/future/v1/balance/list"
            ts_fut = str(int(time.time() * 1000))
            sign_str_fut = f"validate-algorithms#GET#/future/v1/balance/list#timestamp={ts_fut}"
            sig_fut = hmac.new(st.session_state['xt_sec'].encode('utf-8'), sign_str_fut.encode('utf-8'), hashlib.sha256).hexdigest()
            
            headers_fut = {
                "xt-validate-algorithms-key": st.session_state['xt_key'],
                "xt-validate-algorithms-timestamp": ts_fut,
                "xt-validate-algorithms-signature": sig_fut
            }
            
            try:
                res_fut = requests.get(future_url, headers=headers_fut, timeout=5)
                if res_fut.status_code == 200:
                    data_fut = res_fut.json()
                    if "result" in data_fut and isinstance(data_fut["result"], list):
                        for asset in data_fut["result"]:
                            if asset.get("coin", "").upper() == "USDT":
                                usdt_futures = float(asset.get("balance", 0.0))
                                break
            except Exception as e:
                st.error(f"❌ خطا در اتصال به بخش فیوچرز صرافی: {str(e)}")
            
            # محاسبه جمع کل دارایی‌ها
            total_assets = usdt_spot + usdt_futures
            
            # رندر جدول با مبالغ کاملاً واقعی دریافت شده از API شما
            html_bal = f"<table class='custom-table'>" \
                       f"<tr style='background-color: #1F2226;'><th>بخش مالی صرافی XT</th><th>موجودی واقعی و لحظه‌ای (USDT)</th></tr>" \
                       f"<tr><td style='color:#02C076;'>🟢 موجودی حساب اسپات (Spot Wallet)</td><td>{usdt_spot:,.2f} USDT</td></tr>" \
                       f"<tr><td style='color:#F3BA2F;'>🔥 موجودی حساب فیوچرز (Futures Account)</td><td>{usdt_futures:,.2f} USDT</td></tr>" \
                       f"<tr style='background-color:#2B3139;'><td style='color:#F3BA2F; font-size:18px;'>📊 جمع کل دارایی واقعی شما</td><td style='color:#F3BA2F; font-size:18px;'>{total_assets:,.2f} USDT</td></tr>" \
                       f"</table>"
            st.markdown(html_bal, unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)