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

# --- ⚔️ 켈리 공식(Kelly Criterion) 정밀 자금관리 연산 장치 ---
def calculate_kelly_size(win_rate, win_loss_ratio, fraction=0.5):
    b = win_loss_ratio
    p = win_rate
    q = 1.0 - p
    f_star = (p * b - q) / b
    
    if f_star <= 0:
        return 0.0 # 기대값이 음수이면 매수 금지 (0%)
    
    safe_kelly = min(30.0, f_star * fraction * 100)
    return round(safe_kelly, 1)

# 1. 스타일 및 화면 구성
st.set_page_config(page_title="이수할아버지의 냉정 진단기", layout="wide")
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
        if tnx_val >= 4.5: 
            macro_alerts.append(f"🚨 [금리 발작] 국채 금리 {tnx_val:.3f}% 돌파!")
        
        if u_val >= 1500:
            macro_alerts.append(f"☠️ [환율 대공황 비상] 원/달러 {u_val:,.2f}원! 1,500원선 완전 붕괴! 과거 1,550원 악몽 재현, 국가 경제 및 증시 전면 초토화 경보!")
        elif u_val >= 1480:
            macro_alerts.append(f"☠️ [환율 초비상] 원/달러 {u_val:,.2f}원! 1,480원 임계점 폭풍 돌파, 외인 자금 대이탈 경보!")
        elif u_val >= 1450:
            macro_alerts.append(f"🚨 [환율 격랑] 원/달러 {u_val:,.2f}원! 1,480원 고지를 목전에 둔 마지노선 위협!")
        elif u_val >= 1400:
            macro_alerts.append(f"⚠️ [환율 경계] 원/달러 {u_val:,.2f}원! 1,400원대 고착화 주의!")
        
        if u_chg > 0.3:
            macro_alerts.append(f"📈 [환율 급등] 오늘 환율 {u_chg:+.2f}% 치솟는 중!")
        elif u_chg < -0.3:
            macro_alerts.append(f"📉 [환율 안정] 환율 {u_chg:+.2f}% 진정세.")
        
        if macro_alerts:
            adv = " ".join(macro_alerts)
        elif n_chg > 0.5 and tnx_chg < 0:
            adv = "🔥 [골디락스 진입] 지수 상승과 금리 하락, 기세 타시게."
        else:
            adv = "🧐 [눈치싸움 중] 세력들이 간 보고 있구먼."
        st.info(f"🧐 이수 할배의 글로벌 판독: {adv}")
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기")
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
        step=100.0
    )

with col_btn:
    st.write("") 
    st.write("") 
    if st.button("🔄 정밀 분석"):
        st.rerun()

if symbol:
    try:
        try:
            start_date = datetime.now() - timedelta(days=500)
        except Exception:
            start_date = datetime.now(ZoneInfo('UTC')) - timedelta(days=500)
            
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
            try:
                df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            except:
                pass
            
            if df.empty:
                try:
                    df = yf.Ticker(f"{symbol}.KS").history(start=start_date)
                    if df.empty:
                        df = yf.Ticker(f"{symbol}.KQ").history(start=start_date)
                except:
                    pass

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
            except:
                pass

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
            
                try:
                    df = ticker.history(start=start_date)
                except Exception:
                    df = ticker.history(period="1y")
                
            # 1. 가격(auto_p) 추출
                auto_p = 0.0
                try:
                    info = ticker.fast_info
                    auto_p = float(getattr(info, 'last_price', 0.0) or 0.0)
                except:
                    pass
            
                if (auto_p <= 0 or auto_p != auto_p) and not df.empty:
                    auto_p = float(df['Close'].iloc[-1])

            # 2. 실시간 거래량(v_curr) 추출 (거래량이 0인 빈 행 철저 필터링)
                v_curr = 0.0
                try:
                    info = ticker.fast_info
                    v_curr = float(getattr(info, 'last_volume', 0.0) or 0.0)
                except:
                    pass

                if v_curr <= 0 or v_curr != v_curr:
                    try:
                        todays_data = ticker.history(period='1d', interval='1m', prepost=True)
                        if not todays_data.empty and todays_data['Volume'].sum() > 0:
                            v_curr = float(todays_data['Volume'].sum())
                    except:
                        pass

                if (v_curr <= 0 or v_curr != v_curr) and not df.empty and 'Volume' in df.columns:
                    valid_vols = df['Volume'][df['Volume'] > 0]
                    if not valid_vols.empty:
                        v_curr = float(valid_vols.iloc[-1])
                    else:
                        v_curr = float(df['Volume'].iloc[-1])
            
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
                else:
                    p = auto_p
            except ValueError:
                p = auto_p
        else:
            p = auto_p

        if df.empty:
            st.warning(f"⚠️ [{symbol}] 종목의 데이터를 불러오지 못했구먼.")
        else:
            df = df.ffill().dropna()
            df.index = pd.to_datetime(df.index).date
            today_date = now_local.date()

            if not is_kr and us_prev_p and us_prev_p > 0:
                prev_p = us_prev_p
            else:
                if today_date in df.index:
                    temp_df = df.loc[df.index < today_date]
                    prev_p = float(temp_df['Close'].iloc[-1]) if not temp_df.empty else float(df['Close'].iloc[0])
                else:
                    prev_p = float(df['Close'].iloc[-1]) if len(df) > 0 else p

            if today_date in df.index:
                df.loc[today_date, 'Close'] = p
                df.loc[today_date, 'Volume'] = v_curr
                if p > df.loc[today_date, 'High']: df.loc[today_date, 'High'] = p
                if p < df.loc[today_date, 'Low']: df.loc[today_date, 'Low'] = p
            else:
                new_row = pd.DataFrame({
                    'Open': [p], 'High': [p], 'Low': [p], 'Close': [p], 'Volume': [v_curr]
                }, index=[today_date])
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
            else:
                vol_strength_auto = v_ratio 

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
            elif ma5_val < mid_line: trend_status = "📉 <b>[단기 조정 국면]</b> 5일선이 20일선 밑으로 밀림"
            else: trend_status = "⚖️ <b>[추세 혼조]</b> 방향 탐색 중"

            ma_price_summary = (
                f"<br>• 📌 <b>[주요 이동평균선 현황]</b><br>"
                f"&nbsp;&nbsp;<span style='color:#D32F2F; font-weight:bold;'>🔴 5일선: {ma5_str}</span> | "
                f"<span style='color:#1976D2; font-weight:bold;'>🔵 20일선: {ma20_str}</span> | "
                f"<span style='color:#388E3C; font-weight:bold;'>🟢 60일선: {ma60_str}</span> | "
                f"<span style='color:#7B1FA2; font-weight:bold;'>🟣 120일선: {ma120_str}</span><br>"
            )

            if is_squeeze:
                squeeze_info_str = f"<br>• ⚡ <b>[밴드폭 극초축소({bandwidth:.1f}%)]</b> 에너지가 바짝 응축되었습니다."
            elif bandwidth < 25.0:
                squeeze_info_str = f"<br>• 🟡 <b>[밴드폭 협소({bandwidth:.1f}%)]</b> 먹을 자리가 부족합니다."
            else:
                squeeze_info_str = f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 활주로가 트였습니다."

            is_down_trend_v = (p < prev_p) and (p_chg < 0)

            if is_kr:
                core_vault = {"005930": "삼성전자", "000660": "SK하이닉스", "033100": "제룡전기", "257720": "실리콘투", "058610": "에스피지"}
                final_display_name = core_vault.get(symbol, f"국내종목 ({symbol})")
            else:
                us_vault = {"TSLA": "테슬라", "NVDA": "엔비디아", "AAPL": "애플", "MSFT": "마이크로소프트", "IONQ": "아이온큐"}
                tk = symbol.upper()
                final_display_name = f"{us_vault.get(tk, tk)} ({tk})"

            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'><p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{final_display_name}</p><p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>", unsafe_allow_html=True)

            bb_bot_series = (df['Close'] <= (low_b * 1.02)).astype(int)
            rsi_bot_series = (rsi_series <= 35).astype(int)
            will_bot_series = (will_series <= -80).astype(int)
            bottom_score_series = bb_bot_series + rsi_bot_series + will_bot_series
            
            bottom_score = bottom_score_series.iloc[-1]
            recent_bottom_memory = (bottom_score_series.iloc[-3:].max() >= 2)

            is_uptrend = (p >= mid_line) or (ma20_slope > 0)
            is_breakout = (p_chg >= 7.0) and (vol_strength >= 120) and is_ma5_safe and (p >= up_b * 0.98 or p >= defense_line)

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

            is_bottom_disparity_safe = (0 <= bias_ma5 <= 3.0)
            is_bottom_buy_raw = ((recent_bottom_memory or bottom_score >= 2) and is_ma5_safe and is_bottom_disparity_safe)

            bb_top = 1 if p >= (up_b * 0.995) else 0
            rsi_top = 1 if rsi_val >= 60 else 0
            williams_top = 1 if will_val >= -20 else 0 
            top_score = bb_top + rsi_top + williams_top

            m_diff_curr, m_diff_prev = m_l - s_l, m_p - s_p
            is_macd_turning = (m_l < s_l and m_diff_curr > m_diff_prev)

            margin_to_target = (up_b - p) / p if p > 0 else 0
            is_too_close_to_target = margin_to_target < 0.02

            is_bearish_alignment = (ma5_val < mid_line and ma60_val < ma120_val)
            
            if (not is_uptrend) or (p < mid_line) or (bandwidth < 25.0):
                pullback_rebound_score = 0
            else:
                p_will = 1 if will_val <= -50 else 0
                p_bb = 1 if (mid_line * 0.98 <= p <= mid_line * 1.01) else 0
                p_rsi = 1 if (40 <= rsi_val <= 55) else 0
                pullback_rebound_score = p_will + p_bb + p_rsi

            is_true_pullback_buy = (
                (p >= mid_line) 
                and is_ma5_safe 
                and (pullback_rebound_score >= 2)
                and (vol_strength >= 80)
                and (bandwidth >= 25.0)
            )

            if is_stop_loss_triggered:
                final_code = "STOP_LOSS_ALERT"
                final_adv = f"🚨 <b>[최종 결론]</b> 방어선 함락! 미련 없이 전량 손절 후퇴하시게."
            elif is_new_high:
                final_code = "NEW_HIGH"
                final_adv = f"🚀 <b>[최종 결론]</b> 52주 신고가 영역 진격 중!"
            elif is_new_low:
                final_code = "NEW_LOW"
                final_adv = f"🚨 <b>[최종 결론]</b> 52주 신저가 구역 전개! 관망하시게."
            elif is_bottom_buy_raw and vol_strength >= 80:
                final_code = "BOTTOM_BUY"
                final_adv = f"🔴 <b>[최종 결론]</b> 진바닥 선취매 20% 진격 타점."
            elif is_breakout and p >= mid_line: 
                final_code = "BREAKOUT" 
                final_adv = f"🟢 <b>[최종 결론]</b> 상투 과열권 수급 돌파 분출!"
            elif is_too_close_to_target or top_score >= 2 or p >= up_b:
                final_code = "SELL_ZONE"
                final_adv = f"🟢 <b>[최종 결론]</b> 수확 목표선 진입! 분할 매도 시행."
            elif is_true_pullback_buy:
                final_code = "PULLBACK_BUY"
                final_adv = f"🔵 <b>[최종 결론]</b> 2단계 승순 확대 30% 진격 타점."
            else:
                final_code = "WAIT_GENERAL"
                final_adv = f"🟡 <b>[최종 결론]</b> 방향 탐색 중이므로 관망하시게."

            indicator_verify_text = f"{ma_price_summary}<br>• <b>[추세 정밀 판독]:</b> {trend_status}"

            if user_avg_price <= 0:
                holder_guide_msg = f"현재 추세 탐색 및 방향 정립 구간이오니 차분히 보유 판단을 내리시게. (★ <b>손절선: {stop_loss_label}</b>)"
            else:
                profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                if p >= user_avg_price:
                    holder_guide_msg = f"📈 <b>수익권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} / 수익률: +{profit_rate:.2f}%)</b><br>• 수확 목표선까지 홀딩하시고 20일선 이탈 시 수익 실현을 고민하시게."
                else:
                    holder_guide_msg = f"📉 <b>손실권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} / 손실률: {profit_rate:.2f}%)</b><br>• 5일선 아래에서 추가 매수를 금하고 손절선을 엄수하시게."

            st.markdown(f"<div class='signal-box' style='background-color:#1E88E5;'><p class='signal-text'>🧐 이수할아버지의 냉정 진단기</p><div class='signal-subtext'>{final_adv}</div></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선 (하단)</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선 (상단)</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            st.markdown(f"""<div class='trend-card'>
<div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>현재가({p:{fmt_p}}{currency})와 5일선({ma5_val:{fmt_p}}{currency}) 위치를 확인하시게.</span>
</div>
<div style='margin-bottom: 25px;'>
<span style='color: #D32F2F; font-weight: 900; font-size: 24px;'>2. 🛡️ 실전 행동 가이드</span><br>
<span style='color: #2E7D32; font-weight: bold; font-size: 20px;'>👉 {holder_guide_msg}</span>
</div>
</div>""", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
