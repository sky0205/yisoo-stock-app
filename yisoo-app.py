import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

# --- [보급로 최적화 캐싱 장치: 반응속도 극대화 조율] ---
@st.cache_data(ttl=3600)
def load_krx_listing():
    try: return fdr.StockListing('KRX')
    except: return pd.DataFrame()

@st.cache_data(ttl=10) # 10초 단위로 신선도 유지
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

# 1. 스타일 및 화면 구성
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
    
    div.stButton > button {
        background: linear-gradient(90deg, #1A237E 0%, #283593 100%) !important;
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: bold !important;
        padding: 10px 15px !important;
        height: 46px !important;
        border-radius: 8px !important;
        border: 2px solid #FFEB3B !important;
        width: 100% !important;
        box-shadow: 0 3px 6px rgba(26, 35, 126, 0.3) !important;
        cursor: pointer !important;
        margin-top: 0px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #283593 100%, #3F51B5 100%) !important;
        color: #FFEB3B !important;
        border-color: #FFFFFF !important;
    }
    div.stButton > button * {
        color: #FFFFFF !important;
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def display_global_risk():
    st.markdown("### 🌍 글로벌 5대 지수 및 환율·국채 종합 전황")
    try:
        data = fetch_global_market()
        n_chg = (data["n_last"] / data["n_prev"] - 1) * 100
        s_chg = (data["s_last"] / data["s_prev"] - 1) * 100
        d_chg = (data["d_last"] / data["d_prev"] - 1) * 100
        tnx_val, tnx_chg = data["t_last"], (data["t_last"] / data["t_prev"] - 1) * 100
        u_val, u_chg = data["u_last"], (data["u_last"] / data["u_prev"] - 1) * 100
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("나스닥 (NASDAQ)", f"{data['n_last']:,.2f}", f"{n_chg:+.2f}%")
        c2.metric("S&P 500 (SPX)", f"{data['s_last']:,.2f}", f"{s_chg:+.2f}%")
        c3.metric("다우존스 (DJI)", f"{data['d_last']:,.2f}", f"{d_chg:+.2f}%")
        c4.metric("미 국채 10년 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
        c5.metric("원/달러 환율", f"{u_val:,.2f}원", f"{u_chg:+.2f}%")
        
        macro_alerts = []
        if tnx_val >= 4.5: macro_alerts.append(f"🚨 [금리 발작] 국채 금리 {tnx_val:.3f}% 돌파!")
        if u_val >= 1500: macro_alerts.append(f"☠️ [환율 대공황 비상] 원/달러 {u_val:,.2f}원! 1,500원선 완전 붕괴!")
        elif u_val >= 1480: macro_alerts.append(f"☠️ [환율 초비상] 원/달러 {u_val:,.2f}원!")
        elif u_val >= 1450: macro_alerts.append(f"🚨 [환율 격랑] 원/달러 {u_val:,.2f}원!")
        elif u_val >= 1400: macro_alerts.append(f"⚠️ [환율 경계] 원/달러 {u_val:,.2f}원!")
        
        if u_chg > 0.3: macro_alerts.append(f"📈 [환율 급등] 오늘 환율 {u_chg:+.2f}% 치솟는 중!")
        elif u_chg < -0.3: macro_alerts.append(f"📉 [환율 안정] 환율 {u_chg:+.2f}% 진정세.")
        
        if macro_alerts: adv = " ".join(macro_alerts)
        elif n_chg > 0.5 and tnx_chg < 0: adv = "🔥 [골디락스 진입] 지수 상승과 금리 하락, 기세 타시게."
        else: adv = "🧐 [눈치싸움 중] 세력들이 간 보고 있구먼."
        st.info(f"🧐 이수 할배의 글로벌 판독: {adv}")
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36060")
display_global_risk(); st.divider()

col_symbol, col_manual, col_avg, col_btn = st.columns([1.8, 1.8, 1.8, 1.2])

with col_symbol:
    symbol = st.text_input("📊 종목번호 또는 티커", "005930").strip()

with col_manual:
    manual_price_str = st.text_input(
        "⚡ 프리장/수동 실시간가 (선택)", 
        value="", 
        help="프리장이나 주간거래 가격을 직접 적으시면 정규장 시세 대신 우선 적용합니다."
    ).strip()

with col_avg:
    user_avg_price = st.number_input(
        "💡 보유 평단가 (미보유 시 0)",
        min_value=0.0,
        value=0.0,
        step=100.0,
        help="평단가를 입력하시면 수익권/손실권 맞춤형 실전 대응 가이드를 제공합니다."
    )

with col_btn:
    st.write("") 
    st.write("") 
    if st.button("🔄 정밀 분석"):
        st.rerun()

if symbol:
    try:
        try: start_date = datetime.now() - timedelta(days=500)
        except Exception: start_date = datetime.now(ZoneInfo('UTC')) - timedelta(days=500)
            
        is_kr = symbol.isdigit()
        
        try:
            now_tz = ZoneInfo('Asia/Seoul') if is_kr else ZoneInfo('America/New_York')
            now_local = datetime.now(now_tz)
        except Exception:
            utc_now = datetime.now(ZoneInfo('UTC'))
            now_local = utc_now.astimezone(ZoneInfo('Asia/Seoul') if is_kr else ZoneInfo('America/New_York'))

        df = pd.DataFrame()
        auto_p, v_curr = 0.0, 0.0
        us_prev_p = None

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
                api_url = f"https://m.stock.naver.com/api/stock/{symbol}/basic"
                headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)'}
                res = requests.get(api_url, headers=headers, timeout=1)
                if res.status_code == 200:
                    data = res.json()
                    auto_p = float(data['closePrice'].replace(",", ""))
                    v_curr = float(data['accumulatedTradingVolume'].replace(",", ""))
                    kr_fetched = True
            except: pass

            if not kr_fetched:
                try:
                    url = f"https://finance.naver.com/item/main.naver?code={symbol}"
                    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=2)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    auto_p = float(soup.select_one(".no_today .blind").text.replace(",", ""))
                    v_curr = float(soup.select(".no_info .blind")[3].text.replace(",", ""))
                    kr_fetched = True
                except:
                    if not df.empty:
                        auto_p = float(df['Close'].iloc[-1])
                        v_curr = float(df['Volume'].iloc[-1])
        else:
            currency, fmt_p = "$", ",.2f"
            ticker = yf.Ticker(symbol.upper())
            try: df = ticker.history(start=start_date)
            except Exception: df = ticker.history(period="1y")
                
            try:
                info = ticker.fast_info
                auto_p = getattr(info, 'last_price', float(df['Close'].iloc[-1]))
                v_curr = getattr(info, 'last_volume', float(df['Volume'].iloc[-1]))
                us_prev_p = info.previous_close
            except: pass
            
            if auto_p == 0.0 and not df.empty:
                auto_p = float(df['Close'].iloc[-1])
                v_curr = float(df['Volume'].iloc[-1])

        is_manual_mode = False
        if manual_price_str:
            try:
                parsed_val = float(manual_price_str.replace(",", "").replace("$", ""))
                if parsed_val > 0:
                    p = parsed_val
                    is_manual_mode = True
                    st.info(f"💡 **[수동 입력 모드]** 현재가를 **{p:{fmt_p}}{currency}** 기준으로 정밀 연산합니다.")
                else: p = auto_p
            except ValueError:
                st.warning("⚠️ 올바른 숫자 형식으로 입력해 주십시오.")
                p = auto_p
        else: p = auto_p

        if df.empty:
            st.warning(f"⚠️ [{symbol}] 종목의 데이터를 불러오지 못했구먼.")
        else:
            df = df.ffill().dropna()
            df.index = pd.to_datetime(df.index).date
            today_date = now_local.date()

            if not is_kr and us_prev_p and us_prev_p > 0: prev_p = us_prev_p
            else:
                if today_date in df.index:
                    temp_df = df.loc[df.index < today_date]
                    prev_p = float(temp_df['Close'].iloc[-1]) if not temp_df.empty else float(df['Close'].iloc[0])
                else: prev_p = float(df['Close'].iloc[-1]) if len(df) > 0 else p

            if today_date in df.index:
                df.loc[today_date, 'Close'] = p
                df.loc[today_date, 'Volume'] = v_curr
                if p > df.loc[today_date, 'High']: df.loc[today_date, 'High'] = p
                if p < df.loc[today_date, 'Low']: df.loc[today_date, 'Low'] = p
            else:
                new_row = pd.DataFrame({'Open': [p], 'High': [p], 'Low': [p], 'Close': [p], 'Volume': [v_curr]}, index=[today_date])
                df = pd.concat([df, new_row])

            v_avg5 = float(df['Volume'].iloc[-6:-1].mean()) if len(df) >= 6 else float(df['Volume'].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            p_diff = p - prev_p
            p_chg = (p_diff / prev_p) * 100 if prev_p > 0 else 0
            
            if is_kr:
                m_start = now_local.replace(hour=9, minute=0, second=0, microsecond=0)
                m_end = now_local.replace(hour=15, minute=30, second=0, microsecond=0)
                total_minutes = 390
            else:
                m_start = now_local.replace(hour=9, minute=30, second=0, microsecond=0)
                m_end = now_local.replace(hour=16, minute=0, second=0, microsecond=0)
                total_minutes = 390

            if m_start <= now_local <= m_end and now_local.weekday() < 5:
                elapsed = max(10, (now_local - m_start).seconds / 60)
                vol_strength_auto = min(1000, v_ratio / (elapsed / total_minutes))
            else: vol_strength_auto = v_ratio 

            vol_strength = 100.0 if is_manual_mode else vol_strength_auto

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
            up_b = mid_line + (df['Std'].iloc[-1] * 2)
            low_b = mid_line - (df['Std'].iloc[-1] * 2)

            bandwidth = ((up_b - low_b) / mid_line) * 100 if mid_line > 0 else 0
            is_squeeze = (bandwidth <= 10.0)
            
            ma5_val = df['MA5'].iloc[-1] if len(df) >= 5 else mid_line
            ma60_val = df['MA60'].iloc[-1] if len(df) >= 60 else mid_line
            ma120_val = df['MA120'].iloc[-1] if len(df) >= 120 else mid_line
            ma20_slope = (df['MA20'].iloc[-1] - df['MA20'].iloc[-5]) if len(df) >= 5 else 0
            
            prev_low_20 = float(df['Low'].iloc[-21:-1].min()) if len(df) > 20 else float(df['Low'].min())
            is_above_ma20 = (p >= mid_line)

            is_surge_bottom = (p_chg >= 5.0) or (vol_strength >= 150)
            surge_stop_price = ma5_val * 0.97
            
            if is_surge_bottom:
                stop_loss_price = surge_stop_price
                stop_loss_label = f"단기 트레이딩용 5일선-3%({surge_stop_price:{fmt_p}}{currency})"
            else:
                stop_loss_price = prev_low_20
                stop_loss_label = f"전저점 마지노선({prev_low_20:{fmt_p}}{currency})"

            defense_link_idx = min(21, len(df))
            defense_line = float(df['High'].iloc[-defense_link_idx:-1].max()) * 0.93 if len(df) > 1 else p * 0.93

            high_52w = float(df['High'].rolling(window=250, min_periods=1).max().iloc[-1])
            low_52w = float(df['Low'].rolling(window=250, min_periods=1).min().iloc[-1])
            is_new_high = (p >= high_52w * 0.99)
            is_new_low = (p <= low_52w * 1.01)

            is_bullish = (ma5_val > mid_line and mid_line > ma60_val and ma60_val > ma120_val)
            is_bearish = (ma5_val < mid_line and mid_line < ma60_val and ma60_val < ma120_val)
            is_ma5_safe = (p >= ma5_val)

            ma5_str = f"{ma5_val:{fmt_p}}{currency}"
            ma20_str = f"{mid_line:{fmt_p}}{currency}"
            ma60_str = f"{ma60_val:{fmt_p}}{currency}"
            ma120_str = f"{ma120_val:{fmt_p}}{currency}"

            if is_bullish: trend_status = "🔥 <b>[대세 정배열]</b> 완벽한 우상향 성벽 구축 완료"
            elif is_bearish: trend_status = "⚠️ <b>[대세 역배열]</b> 지하실 향하는 하락 추세"
            elif ma5_val > mid_line: trend_status = "🌱 <b>[단기 반등 초입]</b> 5일선이 20일선 돌파!"
            elif ma5_val < mid_line: trend_status = "📉 <b>[단기 조정 국면]</b> 5일선이 20일선 밑으로 밀려 숨고르기 중"
            else: trend_status = "⚖️ <b>[추세 혼조]</b> 방향 탐색 중"

            ma_price_summary = (
                f"<br>• 📌 <b>[주요 이동평균선 현황]</b><br>"
                f"&nbsp;&nbsp;<span style='color:#D32F2F; font-weight:bold;'>🔴 5일선: {ma5_str}</span> | "
                f"<span style='color:#1976D2; font-weight:bold;'>🔵 20일선: {ma20_str}</span> | "
                f"<span style='color:#388E3C; font-weight:bold;'>🟢 60일선: {ma60_str}</span> | "
                f"<span style='color:#7B1FA2; font-weight:bold;'>🟣 120일선: {ma120_str}</span><br>"
            )

            if is_squeeze: squeeze_info_str = f"<br>• ⚡ <b>[밴드폭 극초축소({bandwidth:.1f}%)]</b> 에너지가 바짝 응축되었구먼!"
            elif bandwidth <= 15.0: squeeze_info_str = f"<br>• 🔍 <b>[밴드폭 축소({bandwidth:.1f}%)]</b> 힘을 모으는 구간이오."
            else: squeeze_info_str = f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 일반 변동성 국면이오."

            if is_kr:
                core_vault = {"005930": "삼성전자", "000660": "SK하이닉스", "033100": "제룡전기", "257720": "실리콘투", "058610": "에스피지"}
                final_display_name = core_vault.get(symbol, f"국내종목 ({symbol})")
                if symbol not in core_vault:
                    try:
                        url = f"https://finance.naver.com/item/main.naver?code={symbol}"
                        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=1)
                        soup = BeautifulSoup(res.text, 'html.parser')
                        final_display_name = soup.select_one(".wrap_company h2 a").text.strip()
                    except:
                        try:
                            df_krx_backup = load_krx_listing()
                            final_display_name = df_krx_backup[df_krx_backup['Code'] == symbol]['Name'].values[0]
                        except: pass
            else:
                us_vault = {"TSLA": "테슬라", "NVDA": "엔비디아", "AAPL": "애플", "MSFT": "마이크로소프트", "IONQ": "아이온큐"}
                tk = symbol.upper()
                kor_name = us_vault.get(tk, tk)
                final_display_name = f"{kor_name} ({tk})"

            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'><p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{final_display_name}</p><p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>", unsafe_allow_html=True)

            if is_manual_mode: v_status, v_adv = "수동검증", f"⚡ <b>[수동 연산 모드]</b>"
            elif vol_strength_auto >= 150: v_status, v_adv = "과열폭발", f"🔥 <b>[화력폭발]</b>"
            elif vol_strength_auto >= 100: v_status, v_adv = "매집시작", f"🚀 <b>[매집시작]</b>"
            elif vol_strength_auto >= 80: v_status, v_adv = "정상화력", f"⚔️ <b>[정상화력]</b>"
            else: v_status, v_adv = "거래절벽", f"🧊 <b>[거래절벽]</b>"
            
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량 전황: {v_status}</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            bb_bot_series = (df['Close'] <= (low_b * 1.02)).astype(int)
            rsi_bot_series = (rsi_series <= 35).astype(int)
            will_bot_series = (will_series <= -80).astype(int)
            bottom_score_series = bb_bot_series + rsi_bot_series + will_bot_series
            
            bottom_score = bottom_score_series.iloc[-1]
            recent_bottom_memory = (bottom_score_series.iloc[-3:].max() >= 2)

            is_uptrend = (p >= mid_line) or (ma20_slope > 0)
            is_breakout = (p_chg >= 7.0) and (vol_strength >= 120) and is_ma5_safe 

            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            bias_ma20 = ((p - mid_line) / mid_line) * 100 if mid_line > 0 else 0

            is_stop_loss_triggered = False
            stop_reason = ""
            if user_avg_price > 0 and p < stop_loss_price:
                is_stop_loss_triggered = True
                stop_reason = f"보유 평단가 대비 손절 마지노선 붕괴"
            elif (recent_bottom_memory or bottom_score >= 2) and p < stop_loss_price:
                is_stop_loss_triggered = True
                stop_reason = f"진바닥 방어선 붕괴"
            elif is_uptrend and p < mid_line and not is_ma5_safe:
                is_stop_loss_triggered = True
                stop_reason = f"20일선 중앙 성벽선 이탈 붕괴"

            if bottom_score == 3:
                bottom_status_str = "<b>(오늘 진바닥 3점 만점 달성!)</b>"
                bottom_action_str = f"➔ <b>[1단계 매수 실행]</b> 선취매 진격"
            elif recent_bottom_memory or bottom_score >= 2:
                bottom_status_str = "<b>(최근 바닥권 기록 유효)</b>"
                bottom_action_str = f"➔ <b>[진입 대기]</b> 5일선 안착 시 매수"
            else:
                bottom_status_str = "<b>(조건 미흡)</b>"
                bottom_action_str = "➔ <b>[관망]</b>"

            bb_top = 1 if p >= (up_b * 0.995) else 0
            rsi_top = 1 if rsi_val >= 60 else 0
            williams_top = 1 if will_val >= -20 else 0 
            top_score = bb_top + rsi_top + williams_top

            m_diff_curr, m_diff_prev = m_l - s_l, m_p - s_p
            is_engine_reverse = (m_l < s_l)
            is_macd_turning = (m_l < s_l and m_diff_curr > m_diff_prev)

            margin_to_target = (up_b - p) / p if p > 0 else 0
            is_too_close_to_top = margin_to_target < 0.02

            is_bottom_disparity_safe = (0 <= bias_ma5 <= 3.0)
            is_bottom_buy_raw = ((recent_bottom_memory or bottom_score >= 2) and is_ma5_safe and is_bottom_disparity_safe)
            is_trend_buy_raw = ((p >= mid_line) and (ma5_val >= mid_line) and is_ma5_safe and (0 <= bias_ma20 <= 3.0) and not is_too_close_to_top)

            # =========================================================================
            # ★ [최종 결론 연동 - 5일선 이격 과열 및 20일선 위치 정밀 반영]
            # =========================================================================
            if is_stop_loss_triggered:
                final_code = "STOP_LOSS_ALERT"
                final_adv = f"🚨 <b>[최종 결론]</b> <b>[{stop_reason}]</b> 방어선 함락! 즉시 전량 칼손절 후퇴하시게!"
            elif is_new_high:
                final_code = "NEW_HIGH"
                final_adv = f"🚀 <b>[최종 결론]</b> <b>[52주 신고가]</b> 영역 진격 중! 트레일링 스탑으로 대응하시게!"
            elif is_new_low:
                final_code = "NEW_LOW"
                final_adv = f"🚨 <b>[최종 결론]</b> <b>[52주 신저가]</b> 구역 전개! 무조건 관망하시게!"
            elif is_bottom_buy_raw and vol_strength >= 80:
                final_code = "BOTTOM_BUY"
                final_adv = f"🔴 <b>[최종 결론]</b> [진바닥 기록 + 5일선 안착] 성공! <b>[1단계 진바닥 선취매 20% 진격]</b> 타점이시네."
            elif is_breakout and p >= mid_line: 
                final_code = "BREAKOUT" 
                final_adv = f"🟢 <b>[최종 결론]</b> 장대양봉 <b>[수급 돌파]</b> 분출! 보유자는 분할 익절, 미보유자는 추격 금지!"
            elif is_too_close_to_top or top_score >= 2 or p >= up_b:
                final_code = "SELL_ZONE"
                final_adv = f"🟢 <b>[최종 결론]</b> 과열권 진입! <b>[보유자]는 분할 매도로 수익 확정</b>에 들어가시게!"
            elif is_trend_buy_raw and vol_strength >= 80:
                final_code = "PULLBACK_BUY"
                final_adv = f"🔵 <b>[최종 결론]</b> 20일선 지지 및 눌림목 완성! <b>[2단계 승순 확대 30% 진격]</b> 타점이시네."
            else:
                final_code = "WAIT_GENERAL"
                if bias_ma5 > 3.0 and p < mid_line:
                    final_adv = f"🧐 <b>[최종 결론]</b> <b>20일선 아래에 있으나, 단기 5일선 위에서 +3% 초과 이격 과열 상태</b>이오! 음봉 숨고르기 중이므로 추격매수를 철통 차단하고 🟡 <b>[관망]</b>하시게. (★ <b>방어선: {stop_loss_label}</b>)"
                elif bias_ma5 > 3.0 or bias_ma20 > 3.0:
                    final_adv = f"🧐 <b>[최종 결론]</b> <b>+3% 초과 단기 이격 과열</b> 상태이오! 추격매수를 철통 차단하고 🟡 <b>[관망 및 보유자 홀딩]</b>하시게. (★ <b>방어선: {stop_loss_label}</b>)"
                elif p >= mid_line and is_ma5_safe:
                    final_adv = f"🧐 <b>[최종 결론]</b> 주가가 20일선 및 5일선 위에 있으나 수급 동력이 부족하네. 관망하시게! (★ <b>방어선: {stop_loss_label}</b>)"
                else:
                    final_adv = f"🧐 <b>[최종 결론]</b> 20일선 아래 하락 추세이므로 느긋하게 관망 모드를 유지하시게! (★ <b>방어선: {stop_loss_label}</b>)"

            # =========================================================================
            # ★ [눌림목 동조 채점 - 최종 결론 '관망' 기조 동기화]
            # =========================================================================
            if (not is_uptrend) or (p < mid_line):
                pullback_rebound_score = 0
                pullback_status_str = "<b>(국면 불일치)</b>"
                pullback_action_str = "➔ <b>[눌림목 불가]</b> 하락/바닥 국면으로 관망"
            else:
                p_will = 1 if will_val <= -50 else 0
                p_bb = 1 if (mid_line * 0.98 <= p <= mid_line * 1.01) else 0
                p_rsi = 1 if (40 <= rsi_val <= 55) else 0
                pullback_rebound_score = p_will + p_bb + p_rsi
                
                if pullback_rebound_score == 3:
                    pullback_status_str = "<b>(조건 만족)</b>"
                    if vol_strength < 80: pullback_action_str = "➔ <b>[관망]</b> 거래량 부족으로 매수 보류"
                    elif bias_ma20 > 3.0: pullback_action_str = "➔ <b>[관망]</b> 20일선 이격 과열로 매수 보류"
                    elif is_ma5_safe: pullback_action_str = "➔ <b>[2단계 승순 확대]</b> 30% 추가 진격"
                    else: pullback_action_str = "➔ <b>[진입 대기]</b> 5일선 안착 대기"
                elif pullback_rebound_score == 2:
                    pullback_status_str = "<b>(부분 만족)</b>"
                    if final_code == "WAIT_GENERAL": pullback_action_str = "➔ <b>[관망 유지]</b> 수급 동력 부족으로 유보"
                    else: pullback_action_str = "➔ <b>[정찰 매수 가능]</b> 비중 10% 진입"
                else:
                    pullback_status_str = "<b>(조건 미흡)</b>"
                    pullback_action_str = "➔ <b>[관망]</b>"

            indicator_verify_text = (
                f"{ma_price_summary}<br>"
                f"• <b>[추세 정밀 판독]:</b> {trend_status}<br>"
                f"• <b>[지표 검증 연산]</b><br>"
                f"   - <b>진바닥 동조:</b> {bottom_score}/3점 {bottom_status_str} {bottom_action_str}<br>"
                f"   - <b>눌림목 동조:</b> {pullback_rebound_score}/3점 {pullback_status_str} {pullback_action_str}"
                f"{squeeze_info_str}"
            )

            if user_avg_price <= 0:
                holder_guide_msg = f"현재 추세 탐색 구간이니 성벽({defense_line:{fmt_p}}{currency})이나 5일선 사수 여부를 확인하시게. (★ <b>손절 마지노선: {stop_loss_label}</b>)"
            else:
                profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                if p >= user_avg_price:
                    holder_guide_msg = f"📈 <b>[수익권 보유자 (수익률: +{profit_rate:.2f}%)]</b> 5일선 사수 여부를 주시하며 수확 목표선까지 홀딩하시게."
                else:
                    holder_guide_msg = f"📉 <b>[손실권 보유자 (손실률: {profit_rate:.2f}%)]</b> 5일선 아래에서 절대 물타기를 하지 말고 대기하시게."

            if final_code == "STOP_LOSS_ALERT":
                sig = "🚨 [비상 손절] 방어선 붕괴! 전량 손절 후퇴!"
                col = "#D32F2F" 
                s_adv = f"• <b>{stop_reason}!</b> 즉시 전량 손절 후퇴하시게."
            elif final_code == "SELL_ZONE":
                sig = "🟢 [매도] 푸른 수확 / 이익실현 타점!"
                col = "#388E3C" 
                s_adv = f"• <b>수확 목표 달성! 물량 분할 매도 집행!</b>"
            elif final_code == "BREAKOUT":
                sig = "🟢 [수급 돌파] 분할 익절 타점!"
                col = "#388E3C" 
                s_adv = f"• <b>수급 폭발! 1차 분할 익절 및 추격 금지!</b>"
            elif final_code == "BOTTOM_BUY":
                sig = "🔴 [매수] 1단계 진바닥 선취매! (20% 진격)"
                col = "#D32F2F" 
                s_adv = f"• <b>[진바닥 + 5일선 안착] 1차 선취매 20% 진격!</b>"
            elif final_code == "PULLBACK_BUY":
                sig = "🔵 [눌림목 매수] 2단계 승순 확대! (30% 추가)"
                col = "#1976D2" 
                s_adv = f"• <b>[20일선 눌림목 안착] 승순 확대 30% 진격!</b>"
            else: 
                sig = "🟡 [관망] 방향 탐색 / 음봉 숨고르기 대기"
                col = "#FBC02D" 
                if bias_ma5 > 3.0 and p < mid_line:
                    s_adv = f"• ⚠️ 20일선 아래이나 5일선 위에서 +3% 초과 이격 과열 상태! 음봉 숨고르기 중이므로 추격 매수 금지 및 <b>[관망]</b>.<br>• 🚀 <b>[방어선]</b> {stop_loss_label}"
                else:
                    s_adv = f"• ⚠️ 이격 과열 및 수급 동력 부족으로 관망 중일세.<br>• 🚀 <b>[방어선]</b> {stop_loss_label}"

            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><div class='signal-subtext'>{s_adv}</div></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선 (볼린저하단)</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선 (볼린저상단)</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            st.markdown(f"""<div class='trend-card'>
<div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) {'아래로 밀렸으니 숨고르기 완료를 기다리시게.' if not is_ma5_safe else '위에 안착해 있네.'}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>2. 중장기 추세 진단 및 지표 동조 현황</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{indicator_verify_text}</span>
</div>
<hr style='border:1px solid #FFEBEE; margin: 20px 0;'>
<div class='final-msg'>
{final_adv}
</div>
</div>""", unsafe_allow_html=True)

            st.divider()
            
            # =========================================================================
            # ★ [하단 4대 핵심 지표 박스 복구 완료]
            # =========================================================================
            i1, i2, i3, i4 = st.columns(4)
            
            # --- 1. Bollinger (기세 & 위치) ---
            with i1:
                if final_code == "BOTTOM_BUY":
                    bb_diag = f"🔴 <b>[진바닥 선취매 공략 구간] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 바닥권 과매도 및 5일선 안착 검증.<br>• <b>진단:</b> 진바닥 기록 포착 후 5일선 종가 안착 완료! 1단계 선취매(20%) 집행 구역이오."
                elif final_code == "PULLBACK_BUY":
                    bb_diag = f"🔵 <b>[20일선 눌림목 공략 구간] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 상승 추세 속 눌림목 지지 검증.<br>• <b>진단:</b> 20일선 지지 안착 확인 완료! 2단계 승순 확대(30%) 진격 구역이오."
                elif final_code == "STOP_LOSS_ALERT":
                    bb_diag = f"🚨 <b>[방어선 붕괴 비상 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 손절 마지노선 이탈 감지.<br>• <b>진단:</b> 주요 방어선이 무너졌으니 미련 없이 전량 칼손절 후퇴하시게."
                elif p >= up_b: 
                    bb_diag = f"👺 <b>[수확 목표선(상단) 과열] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 주가 상단 한계선 접촉.<br>• <b>진단:</b> 탐욕의 끝단이니 신규 매수를 금지하고 익절을 집행하시게."
                elif is_breakout: 
                    bb_diag = f"🚀 <b>[수급 돌파 분출] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 20일선 및 볼린저 돌파 강도 측정.<br>• <b>진단:</b> 장대양봉 강력 돌파! 보유자는 분할 수확(매도)하고, 미보유자는 추격매수를 절대 금하시게."
                elif is_squeeze: 
                    bb_diag = f"⚡ <b>[에너지 극초축소 (Squeeze)] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 에너지 응축 및 변동성 폭발 예보.<br>• <b>진단:</b> 밴드가 바짝 좁아졌구먼! 조만간 위/아래 방향성 폭발이 임박했으니 5일선 돌파 전까진 관망하시게."
                elif p <= low_b: 
                    bb_diag = f"🧊 <b>[공략 대기선(하단) 바닥] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 과매도 진바닥 측정.<br>• <b>진단:</b> 지하실 지점이오. 일봉 5일선 종가 안착 시 1단계 선취매(20%)로 대응하시게."
                elif p >= mid_line: 
                    if final_code == "WAIT_GENERAL":
                        bb_diag = f"🔥 <b>[20일 중앙선 지지 / 관망] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 눌림목 및 추세 유지 판단.<br>• <b>진단:</b> 중앙선 위에서 이격 과열 및 숨고르기 중이므로 관망 중이오."
                    else:
                        bb_diag = f"🔥 <b>[20일 중앙선 지지] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 눌림목 및 추세 유지 판단.<br>• <b>진단:</b> 중앙선 지지 완료!" if is_ma5_safe else f"⚠️ <b>[20일선 위 5일선 이탈] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 단기 기세 둔화 감지."
                else: 
                    bb_diag = f"🏹 <b>[20일선 하단 반격] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 하단 추세 전환 시도.<br>• <b>진단:</b> 20일선 아래이나 5일선 위 이격 과열 및 음봉 숨고르기 중이오." if bias_ma5 > 3.0 and p < mid_line else (f"🏹 <b>[20일선 하단 반격] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 하단 추세 전환 시도." if is_ma5_safe else f"🏠 <b>[추세 하락 국면] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 관망 모드 유지.")
            
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세/위치)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            # --- 2. RSI (매수 온도) ---
            with i2:
                rsi_trend = "▲ 상승" if rsi_val > rsi_prev else ("▼ 하락" if rsi_val < rsi_prev else "─ 변동없음")
                is_div = p > prev_p and rsi_val < rsi_prev
                if rsi_val >= 60: 
                    r_status = f"<b>👿 불지옥 과열권</b><br>• <b>역할:</b> 매수 에너지 고갈 경보.<br>• <b>진단:</b> {'🚨 [가짜 상승] 다이버전스 발생!' if is_div else '과열 구간 진입.'}"
                elif rsi_val <= 35: 
                    r_status = f"<b>🧊 냉골 바닥권</b><br>• <b>역할:</b> 진바닥 수급 에너지 감지.<br>• <b>진단:</b> 바닥 탈출 시도 중."
                else: 
                    r_status = f"<b>⚖️ 적정 온도 구간</b><br>• <b>역할:</b> 에너지 충전 및 눌림목 동조.<br>• <b>진단:</b> {'🚨 [다이버전스] 가짜 기세니 속지 마시게.' if is_div else '에너지 충전 중.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (매수 온도)</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{rsi_val:.2f} <span style='font-size:22px; color:#333333;'>({rsi_trend})</span></p><p class='ind-diag'>{r_status}</p></div>", unsafe_allow_html=True)
            
            # --- 3. Williams %R (민감 반전) ---
            with i3:
                will_trend = "▲ 상승" if will_val > will_prev else ("▼ 하락" if will_val < will_prev else "─ 변동없음")
                if will_val >= -20: w_status = "<b>🚩 천장 광기 구역</b><br>• <b>진단:</b> 최고점 광기 진입!"
                elif will_val >= -35: w_status = "<b>⚠️ 천장 근접 경계</b><br>• <b>진단:</b> 고점 징후 포착."
                elif will_val <= -80: w_status = "<b>🏳️ 개미 항복 구역</b><br>• <b>진단:</b> 바닥 침체 및 투매 구간."
                elif will_val <= -65: w_status = "<b>📉 낙폭 과대 지대</b><br>• <b>진단:</b> 반등 타점 감지."
                else: w_status = "<b>⚖️ 중간 지대</b><br>• <b>진단:</b> 방향 탐색 중."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R (민감 반전)</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{will_val:.2f} <span style='font-size:22px; color:#333333;'>({will_trend})</span></p><p class='ind-diag'>{w_status}</p></div>", unsafe_allow_html=True)
            
            # --- 4. MACD (추세 엔진) ---
            with i4:
                if m_l > s_l: m_diag = "<b>🔥 엔진 정회전 완료</b><br>• <b>진단:</b> 상승 모멘텀 유지."
                else: m_diag = "<b>⚙️ 엔진 역회전 상태</b><br>• <b>진단:</b> 하락 조정 모멘텀."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (추세 엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 오류 발생: {e}")
