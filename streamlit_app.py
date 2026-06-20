def spot_sign(secret_key, method, path, params=None):
    """امضای صحیح برای sapi.xt.com (Spot)"""
    timestamp = str(int(time.time() * 1000))
    query = ""
    if params:
        sorted_p = sorted(params.items())
        query = "&".join([f"{k}={v}" for k, v in sorted_p])
    
    # فرمت رسمی XT Spot V4
    sign_str = f"#{timestamp}#{method}#{path}"
    if query:
        sign_str += f"#{query}"
    
    signature = hmac.new(
        secret_key.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return timestamp, signature, query

def get_xt_balances():
    api_key = st.session_state['xt_key']
    api_secret = st.session_state['xt_sec']
    
    if not api_key or not api_secret:
        return None, "API_MISSING"
    
    try:
        method = "GET"
        path = "/v4/balances"
        base_url = "https://sapi.xt.com"
        
        timestamp, signature, query = spot_sign(api_secret, method, path)
        
        headers = {
            "validate-appkey": api_key,
            "validate-timestamp": timestamp,
            "validate-signature": signature,
            "Content-Type": "application/json"
        }
        
        res = requests.get(f"{base_url}{path}", headers=headers, timeout=8)
        
        if res.status_code != 200:
            return None, f"HTTP {res.status_code}: {res.text[:200]}"
        
        data = res.json()
        
        if data.get('rc') != 0:
            return None, f"خطای API: {data.get('msg', data)}"
        
        raw = data.get('result', [])
        # result ممکنه dict باشه با کلید balances
        if isinstance(raw, dict):
            raw = raw.get('balances', raw.get('assets', []))
        
        live_assets = []
        for asset in raw:
            avail = float(asset.get('availableAmount', asset.get('available', 0)))
            frozen = float(asset.get('frozenAmount', asset.get('freeze', 0)))
            qty = avail + frozen
            if qty > 0:
                coin = asset.get('currency', asset.get('coin', '')).upper()
                price = get_live_price(coin) if coin != "USDT" else 1.0
                live_assets.append({
                    "currency": coin,
                    "type": "🟢 حساب اسپات (Spot)",
                    "balance": qty,
                    "value_usdt": qty * price
                })
        
        return live_assets, "SUCCESS"
    
    except Exception as e:
        return None, f"خطای اتصال: {str(e)}"