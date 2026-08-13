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
    """비밀번호 1578 확인 함수"""
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

# --- [보급로 최적화] ---
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
    return {"n_last": nasdaq.last_price, "n_prev": nasdaq.previous_close, "s_last": sp500.last_price, "s_prev": sp500.previous_close, "d_last": dow.last_price, "d_prev": dow.previous_close, "t_last": tnx.last_price, "t_prev": tnx.previous_close, "u_last": usdkrw.last_price, "u_prev": usdkrw.previous_close}

# 1. 스타일 구성
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36060", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 48px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .signal-subtext { font-size: 22px !important; color: #FFFFFF !important; margin-top: 10px; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 540px; }
</style>""", unsafe_allow_html=True)

st.title("🧐 이수할아버지의 냉정 진단기 v36060")
symbol = st.text_input("📊 종목번호", "005930").strip()
manual_price_str = st.text_input("⚡ 수동 실시간가", value="").strip()
user_avg_price = st.number_input("💡 평단가", min_value=0.0, value=0.0)

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
            
            ma5_val = df['MA5'].iloc[-1] if len(df) >= 5 else mid_line
            ma60_val = df['MA60'].iloc[-1] if len(df) >= 60 else mid_line
            ma120_val = df['MA120'].iloc[-1] if len(df) >= 120 else mid_line
            ma20_slope = (df['MA20'].iloc[-1] - df['MA20'].iloc[-5]) if len(df) >= 5 else 0
            prev_low_20 = float(df['Low'].iloc[-21:-1].min()) if len(df) > 20 else float(df['Low'].min())
            
            # ★ 이격도 및 핵심 변수
            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            is_ma5_over_extended = (bias_ma5 > 3.0) # 5일선 이격 +3% 초과 과열
            
            # 20일선 위 안착 기본 전제
            is_above_ma20 = (p >= mid_line)
            is_uptrend_momentum = is_above_ma20 and (ma5_val > mid_line) and (p >= ma5_val) and (p_chg >= 0) and (not is_ma5_over_extended)

            defense_link_idx = min(21, len(df))
            defense_line = float(df['High'].iloc[-defense_link_idx:-1].max()) * 0.93 if len(df) > 1 else p * 0.93

            stop_loss_price = ma5_val * 0.97 if (p_chg >= 5.0 or vol_strength >= 150) else prev_low_20
            stop_loss_label = f"5일선-3%" if (p_chg >= 5.0 or vol_strength >= 150) else f"전저점 마지노선"

            is_stop_loss_triggered = (user_avg_price > 0 and p < stop_loss_price) or (p < stop_loss_price and not is_above_ma20)

            # ★ [수정된 정밀 국면 판독: 성벽 위/아래 구분 및 거래절벽 차단]
            is_near_target = (p >= up_b * 0.98) # 수확 목표선 코앞
            
            # 성벽 돌파 공방: 가격이 성벽 '밑'이거나 근처(98%~102%)이면서, 이미 성벽 위로 한참 올라간 상태가 아니고, 거래량이 최소 80점 이상(거래절벽 아님)일 때만 인정!
            is_near_wall = (defense_line * 0.98 <= p <= defense_line * 1.02) and (p < up_b * 0.98) and (vol_strength >= 80)
            
            # 성벽 위 안착 상태 (이미 성벽보다 가격이 높은데 목표선 도달은 아닐 때)
            is_above_wall = (p > defense_line * 1.02) and (p < up_b * 0.98) and is_above_ma20

            # 진바닥/눌림목 조건 (반드시 20일선 위 및 거래절벽 차단)
            is_bottom_buy_raw = (p >= mid_line) and is_ma5_safe and (0 <= bias_ma5 <= 3.0) and (vol_strength >= 80)
            is_true_pullback_buy = is_above_ma20 and is_ma5_safe and (vol_strength >= 80) and (bandwidth >= 25.0) and (not is_ma5_over_extended)

            # ★ [최종 판독 분기점: 엄격한 우선순위]
            if is_stop_loss_triggered:
                final_code, col = "STOP_LOSS_ALERT", "#D32F2F"
                final_adv = f"🚨 <b>[최종 결론]</b> 방어선 붕괴! 즉시 칼손절 후퇴하시게."
            elif is_ma5_over_extended: # 1순위: 5일선 이격 +3% 초과 과다 이격
                final_code, col = "OVER_EXTENDED", "#FBC02D"
                final_adv = f"🟡 <b>[최종 결론]</b> 5일선 이격도 +{bias_ma5:.1f}%로 +3% 과다 이격! 추격매수 금지하고 <b>[관망]</b>하시게."
            elif is_near_target: # 2순위: 수확 목표선 코앞
                final_code, col = "SELL_ZONE", "#388E3C"
                final_adv = f"🟢 <b>[최종 결론]</b> 수확 목표선 코앞(과열권)! 추격매수 절대 금지, 보유자는 분할 익절하시게."
            elif is_near_wall: # 3순위: 거래량이 붙은 진짜 성벽 돌파 공방
                final_code, col = "WALL_BREAKOUT", "#1E88E5"
                final_adv = f"🔵 <b>[최종 결론]</b> 성벽({defense_line:{fmt_p}}{currency}) 돌파 공방 중 (화력 충족)! 5일선 기준 기세를 살피시게."
            elif is_above_wall and is_uptrend_momentum: # 4순위: 성벽 위 안착 후 상승 추세 진격
                final_code, col = "PULLBACK_BUY", "#1976D2"
                final_adv = f"🔵 <b>[최종 결론]</b> 성벽 위 안착 완료 + 20일선 위 상승 모멘텀! <b>[본진 진격 타점]</b>이시네."
            elif is_true_pullback_buy and (is_uptrend_momentum or p >= mid_line):
                final_code, col = "PULLBACK_BUY", "#1976D2"
                final_adv = f"🔵 <b>[최종 결론]</b> 20일선 위 정석 눌림목 및 5일선 안착! <b>[진격 타점]</b>이시네."
            else:
                final_code, col = "WAIT_GENERAL", "#FBC02D"
                final_adv = f"🟡 <b>[최종 결론]</b> 방향 탐색 및 화력 대기 중이므로 <b>[관망]</b>하시게."

            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{final_code}</p><div class='signal-subtext'>{final_adv}</div></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 오류: {e}")
