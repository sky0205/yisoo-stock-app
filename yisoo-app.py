import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

# --- 🔒 자물쇠(비밀번호) 보안 장치 ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "1578":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.subheader("🔒 이수할아버지의 냉정 진단기 - 보안 접속")
        st.text_input("비밀번호를 입력하시구먼요:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.subheader("🔒 이수할아버지의 냉정 진단기 - 보안 접속")
        st.text_input("비밀번호를 입력하시구먼요:", type="password", on_change=password_entered, key="password")
        st.error("😕 비밀번호가 틀렸사옵니다. 다시 확인하시구먼요!")
        return False
    else:
        return True

if not check_password(): st.stop()

@st.cache_data(ttl=3600)
def load_krx_listing():
    try: return fdr.StockListing('KRX')
    except: return pd.DataFrame()

@st.cache_data(ttl=10)
def fetch_global_market():
    nasdaq = yf.Ticker("^IXIC").fast_info
    sp500 = yf.Ticker("^GSPC").fast_info
    dow = yf.Ticker("^DJI").fast_info
    tnx = yf.Ticker("^TNX").fast_info
    usdkrw = yf.Ticker("USDKRW=X").fast_info
    return {
        "n_last": nasdaq.last_price, "n_prev": nasdaq.previous_close,
        "s_last": sp500.last_price, "s_prev": sp500.previous_close,
        "d_last": dow.last_price, "d_prev": dow.previous_close,
        "t_last": tnx.last_price, "t_prev": tnx.previous_close,
        "u_last": usdkrw.last_price, "u_prev": usdkrw.previous_close
    }

st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36060", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-box * { color: #FFFFFF !important; }
    .signal-text { font-size: 48px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .signal-subtext { font-size: 22px !important; color: #FFFFFF !important; line-height: 1.6; margin-top: 10px; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 540px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 24px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 19px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 12px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .final-msg { color: #D32F2F !important; font-size: 24px !important; font-weight: 900 !important; line-height: 1.5 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧐 이수할아버지의 냉정 진단기 v36060")

col_symbol, col_manual, col_avg, col_btn = st.columns([1.8, 1.8, 1.8, 1.2])
with col_symbol: symbol = st.text_input("📊 종목번호 또는 티커", "005930").strip()
with col_manual: manual_price_str = st.text_input("⚡ 프리장/수동 실시간가 (선택)", value="").strip()
with col_avg: user_avg_price = st.number_input("💡 보유 평단가 (미보유 시 0)", min_value=0.0, value=0.0, step=100.0)
with col_btn:
    st.write(""); st.write("")
    if st.button("🔄 정밀 분석"): st.rerun()

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500)
        is_kr = symbol.isdigit()
        now_local = datetime.now(ZoneInfo('Asia/Seoul') if is_kr else ZoneInfo('America/New_York'))

        df = pd.DataFrame(); auto_p, v_curr = 0.0, 0.0; us_prev_p = None

        if is_kr:
            currency, fmt_p = "원", ",.0f"
            try: df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            except: pass
            if df.empty:
                try:
                    df = yf.Ticker(f"{symbol}.KS").history(start=start_date)
                    if df.empty: df = yf.Ticker(f"{symbol}.KQ").history(start=start_date)
                except: pass
            kr_fetched = False
            try:
                res = requests.get(f"https://m.stock.naver.com/api/stock/{symbol}/basic", headers={'User-Agent': 'Mozilla/5.0'}, timeout=1)
                if res.status_code == 200:
                    data = res.json()
                    auto_p = float(data['closePrice'].replace(",", ""))
                    v_curr = float(data['accumulatedTradingVolume'].replace(",", ""))
                    kr_fetched = True
            except: pass
            if not kr_fetched:
                try:
                    res = requests.get(f"https://finance.naver.com/item/main.naver?code={symbol}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=2)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    auto_p = float(soup.select_one(".no_today .blind").text.replace(",", ""))
                    v_curr = float(soup.select(".no_info .blind")[3].text.replace(",", ""))
                except:
                    if not df.empty: auto_p, v_curr = float(df['Close'].iloc[-1]), float(df['Volume'].iloc[-1])
        else:
            currency, fmt_p = "$", ",.2f"
            ticker = yf.Ticker(symbol.upper())
            try: df = ticker.history(start=start_date)
            except: df = ticker.history(period="1y")
            try:
                info = ticker.fast_info
                auto_p = getattr(info, 'last_price', float(df['Close'].iloc[-1]))
                v_curr = getattr(info, 'last_volume', float(df['Volume'].iloc[-1]))
                us_prev_p = info.previous_close
            except: pass
            if auto_p == 0.0 and not df.empty: auto_p, v_curr = float(df['Close'].iloc[-1]), float(df['Volume'].iloc[-1])

        is_manual_mode = False
        if manual_price_str:
            try:
                parsed_val = float(manual_price_str.replace(",", "").replace("$", ""))
                if parsed_val > 0: p, is_manual_mode = parsed_val, True
                else: p = auto_p
            except: p = auto_p
        else: p = auto_p

        if df.empty:
            st.warning(f"⚠️ [{symbol}] 종목의 데이터를 불러오지 못했구먼.")
        else:
            df = df.ffill().dropna()
            df.index = pd.to_datetime(df.index).date
            today_date = now_local.date()

            prev_p = us_prev_p if (not is_kr and us_prev_p and us_prev_p > 0) else (float(df.loc[df.index < today_date, 'Close'].iloc[-1]) if (today_date in df.index and not df.loc[df.index < today_date].empty) else float(df['Close'].iloc[-1]))

            if today_date in df.index:
                df.loc[today_date, 'Close'] = p
                df.loc[today_date, 'Volume'] = v_curr
                if p > df.loc[today_date, 'High']: df.loc[today_date, 'High'] = p
                if p < df.loc[today_date, 'Low']: df.loc[today_date, 'Low'] = p
            else:
                df = pd.concat([df, pd.DataFrame({'Open': [p], 'High': [p], 'Low': [p], 'Close': [p], 'Volume': [v_curr]}, index=[today_date])])

            v_avg5 = float(df['Volume'].iloc[-6:-1].mean()) if len(df) >= 6 else float(df['Volume'].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            p_diff, p_chg = p - prev_p, ((p - prev_p) / prev_p) * 100 if prev_p > 0 else 0
            
            vol_strength = 100.0 if is_manual_mode else v_ratio

            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val, rsi_prev = rsi_series.iloc[-1], rsi_series.iloc[-2]
            
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            will_series = (h14 - df['Close']) / (h14 - l14 + 1e-10) * -100
            will_val, will_prev = will_series.iloc[-1], will_series.iloc[-2]
            
            macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
            sig_line = macd.ewm(span=9).mean()
            m_l, s_l, m_p, s_p = macd.iloc[-1], sig_line.iloc[-1], macd.iloc[-2], sig_line.iloc[-2]
            
            df['MA5'] = df['Close'].rolling(5).mean()
            df['MA20'] = df['Close'].rolling(20).mean()
            df['MA60'] = df['Close'].rolling(60).mean()
            df['MA120'] = df['Close'].rolling(120).mean()
            df['Std'] = df['Close'].rolling(20).std()
            
            mid_line = df['MA20'].iloc[-1]
            up_b, low_b = mid_line + (df['Std'].iloc[-1] * 2), mid_line - (df['Std'].iloc[-1] * 2)
            bandwidth = ((up_b - low_b) / mid_line) * 100 if mid_line > 0 else 0
            is_squeeze = (bandwidth <= 10.0)
            
            ma5_val = df['MA5'].iloc[-1] if len(df) >= 5 else mid_line
            ma60_val = df['MA60'].iloc[-1] if len(df) >= 60 else mid_line
            ma120_val = df['MA120'].iloc[-1] if len(df) >= 120 else mid_line
            ma20_slope = (df['MA20'].iloc[-1] - df['MA20'].iloc[-5]) if len(df) >= 5 else 0
            
            prev_low_20 = float(df['Low'].iloc[-21:-1].min()) if len(df) > 20 else float(df['Low'].min())
            
            # ★ [핵심 제어 변수 연산]
            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            is_ma5_over_extended = (bias_ma5 > 3.0) # 5일선 이격 +3% 초과 과열
            is_uptrend_momentum = (ma5_val > mid_line) and (p >= ma5_val) and (p_chg >= 0) and (not is_ma5_over_extended)

            is_surge_bottom = (p_chg >= 5.0) or (vol_strength >= 150)
            surge_stop_price = ma5_val * 0.97
            stop_loss_price = surge_stop_price if is_surge_bottom else prev_low_20
            stop_loss_label = f"단기 트레이딩용 5일선-3%({surge_stop_price:{fmt_p}}{currency})" if is_surge_bottom else f"전저점 마지노선({prev_low_20:{fmt_p}}{currency})"

            defense_link_idx = min(21, len(df))
            defense_line = float(df['High'].iloc[-defense_link_idx:-1].max()) * 0.93 if len(df) > 1 else p * 0.93

            is_bullish = (ma5_val > mid_line and mid_line > ma60_val and ma60_val > ma120_val)
            is_bearish = (ma5_val < mid_line and mid_line < ma60_val and ma60_val < ma120_val)
            is_ma5_safe = (p >= ma5_val)

            trend_status = "🔥 <b>[대세 정배열]</b>" if is_bullish else ("⚠️ <b>[대세 역배열]</b>" if is_bearish else "🌱 <b>[단기 반등 초입]</b>" if ma5_val > mid_line else "📉 <b>[단기 조정 국면]</b>")
            ma_price_summary = f"<br>• 📌 <b>[주요 이평선]</b> 5일선: {ma5_val:{fmt_p}}{currency} (이격도: {bias_ma5:+.1f}%) | 20일선: {mid_line:{fmt_p}}{currency}<br>"

            is_down_trend_v = (p < prev_p) and (p_chg < 0) and not is_uptrend_momentum

            # 종목명 처리
            final_display_name = f"국내종목 ({symbol})" if is_kr else f"미국티커 ({symbol.upper()})"

            st.markdown("### 📊 현재주가현황")
            st.markdown(f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'><p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{final_display_name}</p><p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)</p></div>", unsafe_allow_html=True)

            bb_bot_series = (df['Close'] <= (low_b * 1.02)).astype(int)
            rsi_bot_series = (rsi_series <= 35).astype(int)
            will_bot_series = (will_series <= -80).astype(int)
            bottom_score_series = bb_bot_series + rsi_bot_series + will_bot_series
            bottom_score = bottom_score_series.iloc[-1]
            recent_bottom_memory = (bottom_score_series.iloc[-3:].max() >= 2)

            is_stop_loss_triggered = (user_avg_price > 0 and p < stop_loss_price) or ((recent_bottom_memory or bottom_score >= 2) and p < stop_loss_price)

            is_bottom_disparity_safe = (0 <= bias_ma5 <= 3.0)
            is_bottom_buy_raw = ((recent_bottom_memory or bottom_score >= 2) and is_ma5_safe and is_bottom_disparity_safe)

            bottom_status_str = "<b>(조건 만족)</b>" if bottom_score >= 2 else "<b>(조건 미흡)</b>"
            bottom_action_str = "➔ 진바닥 매수 검토" if bottom_score >= 2 else "➔ 관망"

            pullback_rebound_score = 2 if is_uptrend_momentum else 0
            pullback_status_str = "<b>(조건 만족)</b>" if pullback_rebound_score >= 2 else "<b>(조건 미흡)</b>"
            pullback_action_str = "➔ 눌림목 진격" if pullback_rebound_score >= 2 else "➔ 관망"
            squeeze_info_str = f"<br>• ⚡ <b>[밴드폭 {bandwidth:.1f}%]</b>"

            is_true_pullback_buy = (p >= mid_line or is_uptrend_momentum) and (is_ma5_safe or is_uptrend_momentum) and (not is_ma5_over_extended)

            # ★ [최종 판독 분기점: 철저한 우선순위 적용]
            is_near_target = (p >= up_b * 0.98) # 수확 목표선 코앞
            is_near_wall = (p >= defense_line * 0.99) and (p < up_b * 0.98) # 성벽 돌파 공방 중

            if is_stop_loss_triggered:
                final_code, col = "STOP_LOSS_ALERT", "#D32F2F"
            elif is_ma5_over_extended: # ★ 1순위: 5일선 +3% 초과 과다 이격 시 무조건 관망
                final_code, col = "OVER_EXTENDED", "#FBC02D"
            elif is_near_target: # ★ 2순위: 수확 목표선 도달 시 매도/추격금지
                final_code, col = "SELL_ZONE", "#388E3C"
            elif is_near_wall: # ★ 3순위: 성벽 돌파 시도 중일 때 진격 유지
                final_code, col = "WALL_BREAKOUT", "#1E88E5"
            elif is_bottom_buy_raw and vol_strength >= 80:
                final_code, col = "BOTTOM_BUY", "#D32F2F"
            elif is_true_pullback_buy or is_uptrend_momentum:
                final_code, col = "PULLBACK_BUY", "#1976D2"
            else:
                final_code, col = "WAIT_GENERAL", "#FBC02D"

            # [최종 결론 메시지 결합]
            if final_code == "STOP_LOSS_ALERT":
                sig, s_adv = "🚨 [비상 손절] 방어선 붕괴!", f"방어선 함락! 전량 손절 후퇴하시게. (방어선: {stop_loss_label})"
            elif final_code == "OVER_EXTENDED":
                sig, s_adv = "🟡 [이격 과열 관망]", f"5일선 이격도가 +{bias_ma5:.1f}%로 +3%를 초과하여 과다 이격 상태이오! 추격매수를 금하고 <b>[관망]</b>하시게. (방어선: {stop_loss_label})"
            elif final_code == "SELL_ZONE":
                sig, s_adv = "🟢 [수확 목표선 코앞]", f"과열권 진입! 미보유자 추격매수 절대 금지, 보유자는 분할 익절하시게. (방어선: {stop_loss_label})"
            elif final_code == "WALL_BREAKOUT":
                sig, s_adv = "🔵 [성벽 돌파 공방]", f"현재 성벽({defense_line:{fmt_p}}{currency}) 돌파 공방 중! 기세를 살려 5일선 기준으로 살피시게. (방어선: {stop_loss_label})"
            elif final_code == "BOTTOM_BUY":
                sig, s_adv = "🔴 [진바닥 선취매]", f"진바닥 기록 + 5일선 안착! 1차 선취매 진격 타점. (손절선: {stop_loss_label})"
            elif final_code == "PULLBACK_BUY":
                sig, s_adv = "🔵 [상승 추세 진격]", f"상승 모멘텀 유지! 자신 있게 홀딩 및 진격하시게. (방어선: {stop_loss_label})"
            else:
                sig, s_adv = "🟡 [관망]", f"방향 탐색 및 지표 대기 중. (방어선: {stop_loss_label})"

            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><div class='signal-subtext'>{s_adv}</div></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            indicator_verify_text = f"{ma_price_summary}<br>• <b>[추세 정밀 판독]:</b> {trend_status}"
            holder_guide_msg = f"현재 추세 탐색 및 5일선 사수 여부를 확인하며 대응하시게. (손절선: {stop_loss_label})"

            st.markdown(f"""<div class='trend-card'>
<div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 이격도</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>현재 5일선 대비 이격도: {bias_ma5:+.1f}% {'(과다이격 관망)' if is_ma5_over_extended else '(안전 진격)'}</span>
</div>
<div style='margin-bottom: 25px;'>
<span style='color: #D32F2F; font-weight: 900; font-size: 24px;'>2. 🛡️ [보유자 전용] 실전 행동 가이드</span><br>
<span style='color: #2E7D32; font-weight: bold; font-size: 20px;'>👉 {holder_guide_msg}</span>
</div>
<hr style='border:1px solid #FFEBEE; margin: 20px 0;'>
<div class='final-msg'>{s_adv}</div>
</div>""", unsafe_allow_html=True)

            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger</p><p class='ind-diag'>상태: {final_code}</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{rsi_val:.2f}</p><p class='ind-diag'>온도 점검 완료</p></div>", unsafe_allow_html=True)
            with i3: st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{will_val:.2f}</p><p class='ind-diag'>민감 반전 체크</p></div>", unsafe_allow_html=True)
            with i4: st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD</p><p class='ind-diag'>엔진 정/역회전 감지</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
