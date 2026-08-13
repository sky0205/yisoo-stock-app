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
    """비밀번호를 확인하는 함수"""
    def password_entered():
        if st.session_state["password"] == "1578":  # 비밀번호 1578
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 비밀번호 기억 삭제
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

if not check_password():
    st.stop()

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

st.title("🧐 이수할아버지의 냉정 진단기 v36060")
display_global_risk(); st.divider()

col_symbol, col_manual, col_avg, col_btn = st.columns([1.8, 1.8, 1.8, 1.2])

with col_symbol:
    symbol = st.text_input("📊 종목번호 또는 티커", "005930").strip()

with col_manual:
    manual_price_str = st.text_input(
        "⚡ 프리장/수동 실시간가 (선택)", 
        value="", 
        help="프리장이나 주간거래 가격을 직접 적으시면 정규장 시세 대신 우선 적용합니다. (지우고 빈칸으로 만드시면 자동 시세 복귀)"
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
                
            try:
                info = ticker.fast_info
                auto_p = getattr(info, 'last_price', float(df['Close'].iloc[-1]))
                v_curr = getattr(info, 'last_volume', float(df['Volume'].iloc[-1]))
                us_prev_p = info.previous_close
            except:
                pass
            
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
                st.warning("⚠️ 올바른 숫자 형식으로 입력해 주십시오. (자동 시세로 연산합니다)")
                p = auto_p
        else:
            p = auto_p

        if df.empty:
            st.warning(f"⚠️ [{symbol}] 종목의 데이터를 불러오지 못했구먼. 종목번호를 다시 확인하거나 잠시 후 다시 시도해 주시게.")
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

            if is_manual_mode:
                vol_strength = 100.0
            else:
                vol_strength = vol_strength_auto

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

            # ★ [5일선 이격도(+3% 초과) 계산]: 이격 과열 여부 판단
            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            is_ma5_over_extended = (bias_ma5 > 3.0)

            # ★ [추세 모멘텀 플래그]: 5일선 이격 과열(+3% 이상)이면 상승장이라도 매수 금지 대상
            is_uptrend_momentum = (ma5_val > mid_line) and (p >= ma5_val) and (p_chg >= 0) and (not is_ma5_over_extended)

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
            elif ma5_val > mid_line: trend_status = "🌱 <b>[단기 반등 초입]</b> 5일선이 20일선 돌파! 상방 반전 시도 중"
            elif ma5_val < mid_line: trend_status = "📉 <b>[단기 조정 국면]</b> 5일선이 20일선 밑으로 밀려 숨고르기 중"
            else: trend_status = "⚖️ <b>[추세 혼조]</b> 방향 탐색 중"

            ma_price_summary = (
                f"<br>• 📌 <b>[주요 이동평균선 현황]</b><br>"
                f"&nbsp;&nbsp;<span style='color:#D32F2F; font-weight:bold;'>🔴 5일선: {ma5_str} (이격도: {bias_ma5:+.1f}% / 손절선: {surge_stop_price:{fmt_p}}{currency})</span> | "
                f"<span style='color:#1976D2; font-weight:bold;'>🔵 20일선: {ma20_str}</span> | "
                f"<span style='color:#388E3C; font-weight:bold;'>🟢 60일선: {ma60_str}</span> | "
                f"<span style='color:#7B1FA2; font-weight:bold;'>🟣 120일선: {ma120_str}</span><br>"
            )

            if is_squeeze:
                squeeze_info_str = f"<br>• ⚡ <b>[밴드폭 극초축소({bandwidth:.1f}%)]</b> 에너지가 바짝 응축되었구먼! 얕은 조정 후 폭발할 수 있으니 돌파 시 정면 대응하시게."
            elif bandwidth < 25.0:
                squeeze_info_str = f"<br>• 🟡 <b>[밴드폭 협소({bandwidth:.1f}%)]</b> 밴드폭이 25% 미만이오! 먹을 자리가 부족하니 섣부른 진입을 자제하시게."
            else:
                squeeze_info_str = f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 활주로가 넉넉히 트였으니 정석 눌림목 타점을 공략하시게."

            is_down_trend_v = (p < prev_p) and (p_chg < 0) and not is_uptrend_momentum

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
                us_vault = {
                    "TSLA": "테슬라", "NVDA": "엔비디아", "AAPL": "애플", 
                    "MSFT": "마이크로소프트", "AMZN": "아마존", "GOOGL": "알파벳A", 
                    "META": "메타", "IONQ": "아이온큐", "CPNG": "쿠팡", "NFLX": "넷플릭스"
                }
                tk = symbol.upper()
                kor_name = us_vault.get(tk, None)
                if not kor_name:
                    try:
                        info_dict = ticker.info
                        kor_name = info_dict.get('longName', info_dict.get('shortName', tk))
                    except: kor_name = tk
                final_display_name = f"{kor_name} ({tk})"

            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'><p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{final_display_name}</p><p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>", unsafe_allow_html=True)

            if is_manual_mode:
                v_status, v_adv = "수동검증", f"⚡ <b>[프리장/수동 연산]</b> 수동 입력 시세를 기준으로 이격도 및 매수 타점을 정밀 검증 중이외다."
            elif vol_strength_auto >= 150:
                if not is_down_trend_v:
                    v_status, v_adv = "과열폭발", f"🔥 <b>[화력폭발]</b> 시간보정 강도 {vol_strength_auto:.1f}점! 양봉 화력 실린 본진 진격 중이오."
                else:
                    v_status, v_adv = "역배열투매", f"🚨 <b>[역배열/하방 투매과열]</b> 시간보정 강도 {vol_strength_auto:.1f}점! 하방 압력 속 투매 물량 폭발 중이니 절대 칼날을 잡지 마시게."
            elif vol_strength_auto >= 100: 
                if not is_down_trend_v:
                    v_status, v_adv = "매집시작", f"🚀 <b>[매집시작]</b> 시간보정 강도 {vol_strength_auto:.1f}점! 화력이 차오르네."
                else:
                    v_status, v_adv = "역배열과열", f"⚠️ <b>[역배열과열]</b> 시간보정 강도 {vol_strength_auto:.1f}점! 하락 추세 속 속임수 음봉 거래량 주의."
            elif vol_strength_auto >= 80: 
                v_status, v_adv = "정상화력", f"⚔️ <b>[정상화력]</b> 시간보정 강도 {vol_strength_auto:.1f}점! 기세가 빳빳하구먼."
            else: 
                v_status, v_adv = "거래절벽", f"🧊 <b>[거래절벽]</b> 시간보정 강도 {vol_strength_auto:.1f}점! 수급이 마르고 동력이 없으니 속지 마시게."
            
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량 전황: {v_status} ({'수동 연산 모드' if is_manual_mode else f'실시간 {v_ratio:.1f}% / 5일평균대비'})</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            bb_bot_series = (df['Close'] <= (low_b * 1.02)).astype(int)
            rsi_bot_series = (rsi_series <= 35).astype(int)
            will_bot_series = (will_series <= -80).astype(int)
            bottom_score_series = bb_bot_series + rsi_bot_series + will_bot_series
            
            bottom_score = bottom_score_series.iloc[-1]
            recent_bottom_memory = (bottom_score_series.iloc[-3:].max() >= 2)

            is_uptrend = (p >= mid_line) or (ma20_slope > 0)
            is_breakout = (p_chg >= 7.0) and (vol_strength >= 120) and is_ma5_safe and (p >= up_b * 0.98 or p >= defense_line)

            bias_ma20 = ((p - mid_line) / mid_line) * 100 if mid_line > 0 else 0

            is_stop_loss_triggered = False
            stop_reason = ""
            if user_avg_price > 0 and p < stop_loss_price:
                is_stop_loss_triggered = True
                stop_reason = f"보유 평단가 대비 손절 마지노선({stop_loss_label}) 붕괴"
            elif (recent_bottom_memory or bottom_score >= 2) and p < stop_loss_price:
                is_stop_loss_triggered = True
                stop_reason = f"진바닥 방어선({stop_loss_label}) 붕괴"
            elif is_uptrend and p < mid_line and not is_ma5_safe and not is_uptrend_momentum:
                is_stop_loss_triggered = True
                stop_reason = f"20일선 중앙 성벽선({mid_line:{fmt_p}}{currency}) 이탈 붕괴"

            is_bottom_disparity_safe = (0 <= bias_ma5 <= 3.0)
            is_bottom_buy_raw = ((recent_bottom_memory or bottom_score >= 2) and is_ma5_safe and is_bottom_disparity_safe)

            if bottom_score == 3:
                bottom_status_str = "<b>(오늘 진바닥 3점 만점 달성!)</b>"
                if is_stop_loss_triggered:
                    bottom_action_str = f"➔ <b>[비상 후퇴]</b> 방어선 붕괴로 매수 금지"
                elif vol_strength < 80:
                    bottom_action_str = f"➔ <b>[관망]</b> 바닥 지표는 포착되었으나 거래량 부족({vol_strength:.1f}점)으로 매수 보류"
                elif bias_ma5 > 3.0:
                    bottom_action_str = f"➔ <b>[관망]</b> 5일선 대비 +3% 초과 이격 과열로 추격 매수 보류"
                elif is_ma5_safe:
                    bottom_action_str = f"➔ <b>[1단계 매수 실행]</b> 진바닥 3점 달성 + 일봉 5일선 종가 안착 완료! 20% 선취매 진격"
                else:
                    bottom_action_str = f"➔ <b>[진입 대기]</b> 진바닥 3점 달성! 일봉 5일선 상향 안착 시 20% 매수 시작"
            elif recent_bottom_memory or bottom_score >= 2:
                bottom_status_str = "<b>(최근 3일 내 바닥권 2점 이상 기록 유효!)</b>"
                if is_stop_loss_triggered:
                    bottom_action_str = f"➔ <b>[비상 후퇴]</b> 방어선 붕괴로 매수 금지"
                elif vol_strength < 80:
                    bottom_action_str = f"➔ <b>[관망]</b> 최근 바닥 기록은 유효하나 거래량 부족({vol_strength:.1f}점)으로 매수 보류"
                elif bias_ma5 > 3.0:
                    bottom_action_str = f"➔ <b>[관망]</b> 5일선 대비 +3% 초과 이격 과열로 추격 매수 보류"
                elif is_ma5_safe:
                    bottom_action_str = f"➔ <b>[1단계 매수 실행]</b> 바닥권 기록 포착 후 일봉 5일선 종가 안착 완료! 20% 선취매 진격"
                else:
                    bottom_action_str = f"➔ <b>[진입 대기]</b> 최근 바닥권 기록 유효. 일봉 5일선 종가 안착 시 20% 매수 시작"
            else:
                bottom_status_str = "<b>(조건 미흡)</b>"
                bottom_action_str = "➔ <b>[관망]</b> 매수 보류, 실시간 지표 모니터링 유지"

            bb_top = 1 if p >= (up_b * 0.995) else 0
            rsi_top = 1 if rsi_val >= 60 else 0
            williams_top = 1 if will_val >= -20 else 0 
            top_score = bb_top + rsi_top + williams_top

            m_diff_curr, m_diff_prev = m_l - s_l, m_p - s_p
            is_engine_reverse = (m_l < s_l)
            is_macd_turning = (m_l < s_l and m_diff_curr > m_diff_prev)

            # ★ [성벽 돌파 국면과 진짜 수확선 도달 국면 구분 계산]
            is_near_target = (p >= up_b * 0.98) # 수확 목표선 2% 이내
            is_near_wall = (p >= defense_line * 0.99) and (p < up_b * 0.98) # 성벽 돌파 공방 중

            is_bearish_alignment = (ma5_val < mid_line and ma60_val < ma120_val)
            
            if (not is_uptrend and not is_uptrend_momentum) or (p < mid_line and not is_uptrend_momentum) or (bandwidth < 25.0 and not is_uptrend_momentum):
                pullback_rebound_score = 0
                if bandwidth < 25.0 and is_uptrend and p >= mid_line and not is_uptrend_momentum:
                    pullback_status_str = f"<b>(밴드폭 협소 {bandwidth:.1f}%)</b>"
                    pullback_action_str = "➔ <b>[매수 보류]</b> 밴드폭 25% 미만으로 먹을 자리가 부족하여 승순 확대 금지"
                else:
                    pullback_status_str = "<b>(국면 불일치)</b>"
                    if is_bearish_alignment and not is_ma5_safe and not is_uptrend_momentum:
                        pullback_action_str = "➔ <b>[눌림목 불가]</b> 하락/바닥 국면으로 관망"
                    else:
                        pullback_action_str = "➔ <b>[돌파 대기]</b> 상방 공방 및 이격 조율 중 관망"
            else:
                p_will = 1 if will_val <= -50 else 0
                p_bb = 1 if (mid_line * 0.98 <= p <= mid_line * 1.01) or is_uptrend_momentum else 0
                p_rsi = 1 if (40 <= rsi_val <= 55) or is_uptrend_momentum else 0
                pullback_rebound_score = p_will + p_bb + p_rsi
                
                if pullback_rebound_score >= 2 or is_uptrend_momentum:
                    pullback_status_str = f"<b>(조건 만족 / 밴드폭 {bandwidth:.1f}%)</b>"
                    if vol_strength < 80 and not is_uptrend_momentum: 
                        pullback_action_str = f"➔ <b>[관망]</b> 조건 충족이나 거래량 부족({vol_strength:.1f}점)으로 매수 보류"
                    elif bias_ma20 > 5.0 and not is_uptrend_momentum: 
                        pullback_action_str = f"➔ <b>[관망]</b> 20일선 이격 과열로 매수 보류"
                    elif is_ma5_safe or is_uptrend_momentum: 
                        pullback_action_str = f"➔ <b>[2단계 승순 확대]</b> 밴드폭 25% 이상 활주로 확보! 30% 추가 진격"
                    else: 
                        pullback_action_str = f"➔ <b>[진입 대기]</b> 5일선 안착 대기"
                else:
                    pullback_status_str = "<b>(조건 미흡)</b>"
                    pullback_action_str = "➔ <b>[관망]</b>"

            is_true_pullback_buy = (
                (p >= mid_line or is_uptrend_momentum) 
                and (is_ma5_safe or is_uptrend_momentum) 
                and ((pullback_rebound_score >= 2) or is_uptrend_momentum)
                and (vol_strength >= 80 or is_uptrend_momentum)
                and (bandwidth >= 25.0 or is_uptrend_momentum)
                and (not is_ma5_over_extended)
            )

            # ★ [최종 판독 분기점]: 성벽 돌파 중인 경우와 진짜 목표선 도달/이격 과열 구분
            if is_stop_loss_triggered:
                final_code = "STOP_LOSS_ALERT"
                final_adv = f"🚨 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[{stop_reason}]</b> 방어선 완전 함락! 미련을 버리고 즉시 전량 칼손절 후퇴하시게."
            elif is_new_high:
                final_code = "NEW_HIGH"
                final_adv = f"🚀 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[52주 신고가(무주공산)]</b> 영역 진격 중! 5일선 사수 기준 대응하시게!"
            elif is_new_low:
                final_code = "NEW_LOW"
                final_adv = f"🚨 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[52주 신저가(칼날 하락)]</b> 구역 전개! 무조건 관망하시게!"
            elif is_near_target: # 진짜 수확 목표선 코앞일 때만 경고
                final_code = "SELL_ZONE"
                final_adv = f"🟢 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>수확 목표선 코앞(과열권)</b>이오! <b>[미보유자] 추격매수 절대 금지</b>, [보유자]는 분할 익절 및 5일선 기준 홀딩하시게! (★ <b>방어선: {stop_loss_label}</b>)"
            elif is_near_wall: # 성벽 돌파 시도 중일 때는 진격 유지
                final_code = "WALL_BREAKOUT"
                final_adv = f"🔵 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>현재 성벽({defense_line:{fmt_p}}{currency}) 돌파 공방 중!</b> 기세를 살려 돌파하는지 5일선 기준으로 살피시게. (★ <b>방어선: {stop_loss_label}</b>)"
            elif is_bottom_buy_raw and vol_strength >= 80 and not is_ma5_over_extended:
                final_code = "BOTTOM_BUY"
                final_adv = f"🔴 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). [진바닥 기록 + 5일선 안착] 성공! <b>[1단계 진바닥 선취매 20% 진격 타점]</b>이시네. (★ <b>손절선: {stop_loss_label}</b>)"
            elif is_breakout and p >= mid_line: 
                final_code = "BREAKOUT" 
                final_adv = f"🟢 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[상투 과열권 수급 돌파]</b> 분출 중! 보유자는 분할 익절, 미보유자는 추격 금지! (★ <b>방어선: {stop_loss_label}</b>)"
            elif is_ma5_over_extended:
                final_code = "OVER_EXTENDED"
                final_adv = f"🟡 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>5일선 이격도가 +{bias_ma5:.1f}%로 +3%를 초과하여 과다 이격 상태</b>이오! 고무줄 과열이므로 신규 추격매수를 철통 차단하고 <b>[관망]</b>하시게! (★ <b>방어선: {stop_loss_label}</b>)"
            elif is_true_pullback_buy:
                final_code = "PULLBACK_BUY"
                final_adv = f"🔵 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>상승 추세 모멘텀 및 5일/20일선 안착 빳빳함!</b> <b>[추세 유지 및 승순 확대 30% 진격 타점]</b>이시네. (★ <b>방어선: {stop_loss_label}</b>)"
            else:
                final_code = "WAIT_GENERAL"
                if is_down_trend_v:
                    final_adv = f"🟡 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 현재 <b>하방 압력 및 하락세</b>이므로 섣부른 진입을 철통 차단하고 <b>[관망]</b>하시게! (★ <b>방어선: {stop_loss_label}</b>)"
                elif bandwidth < 25.0 and p >= mid_line:
                    final_adv = f"🟡 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>밴드폭이 {bandwidth:.1f}%로 25% 미만</b>이오! 상단 목표선이 가까워 먹을 자리가 부족하므로 눌림목 매수를 잠그고 <b>[관망]</b>하시게! (★ <b>방어선: {stop_loss_label}</b>)"
                elif pullback_rebound_score < 2 and p >= mid_line:
                    final_adv = f"🟡 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 화력은 살아있으나 지표 동조 점수가 미흡하므로 <b>[관망]</b>하시게! (★ <b>방어선: {stop_loss_label}</b>)"
                else:
                    final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 이격 과열 및 지표 동조 대기로 관망 중일세! (★ <b>방어선: {stop_loss_label}</b>)"

            indicator_verify_text = (
                f"{ma_price_summary}<br>"
                f"• <b>[추세 정밀 판독]:</b> {trend_status}<br>"
                f"• <b>[지표 검증 연산]</b><br>"
                f"   - <b>진바닥 동조:</b> {bottom_score}/3점 {bottom_status_str} {bottom_action_str}<br>"
                f"   - <b>눌림목 동조:</b> {pullback_rebound_score}/3점 {pullback_status_str} {pullback_action_str}"
                f"{squeeze_info_str}"
            )

            if user_avg_price <= 0:
                if is_down_trend_v:
                    holder_guide_msg = f"현재 하방 압력 및 하락 추세 구간이므로 신규 진입을 철통같이 금하고 관망하시게. (★ <b>현재 기준 손절 마지노선: {stop_loss_label}</b>)"
                else:
                    holder_guide_msg = f"현재 추세 탐색 및 방향 정립 구간이니 성벽({defense_line:{fmt_p}}{currency})이나 5일선 사수 여부를 확인하며 차분히 보유 판단을 내리시게. (★ <b>현재 기준 손절 마지노선: {stop_loss_label}</b>)"
            else:
                profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                is_low_safe_holder = (user_avg_price <= prev_low_20) or (profit_rate >= 15.0)

                if p >= user_avg_price:
                    if is_low_safe_holder:
                        holder_guide_msg = (
                            f"📈 <b>[안전마진 확보 저가 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} / 수익률: +{profit_rate:.2f}%)]</b><br>"
                            f"• 이미 바닥에서 든든하게 쥐고 계신 효자 물량이니, 단기 5일선 흔들림이나 전저점에 연연하지 마시게.<br>"
                            f"• 수확 목표선({up_b:{fmt_p}}{currency})까지 느긋하게 홀딩하시고, 추후 중기 생명선인 <b>20일선({ma20_str})</b>을 완전히 이탈할 때 비로소 수익 실현을 고민하시게."
                        )
                    else:
                        holder_guide_msg = (
                            f"📈 <b>[수익권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} / 수익률: +{profit_rate:.2f}%)]</b><br>"
                            f"• 현재 5일선({ma5_val:{fmt_p}}{currency}) 사수 여부를 주시하시게. 단기 변동성에 수익을 반납하지 않도록 본절가/익절선을 설정하시게.<br>"
                            f"• 5일선 안착 시 수확 목표선({up_b:{fmt_p}}{currency})까지 자신감 있게 홀딩하시고, 이탈 시 일부 분할 익절로 대응하시게. (★ <b>필수 방어선: {stop_loss_label}</b>)"
                        )
                else:
                    holder_guide_msg = (
                        f"📉 <b>[손실권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} / 손실률: {profit_rate:.2f}%)]</b><br>"
                        f"• <b>5일선({ma5_val:{fmt_p}}{currency}) 아래에서는 절대로 추측 추가 매수(물타기)를 하지 마시게.</b> 손가락을 묶고 차분히 대기하시게.<br>"
                        f"• 손절 마지노선({stop_loss_label}) 이탈 시 추가 손실 방지를 위한 전량 손절 후퇴를 집행하시고 현금을 지키시게."
                    )

            if final_code == "STOP_LOSS_ALERT":
                sig = "🚨 [비상 손절] 방어선 붕괴! 전량 손절 후퇴!"
                col = "#D32F2F" 
                s_adv = f"• <b>[긴급 집행] {stop_reason}!</b> 추가 손실을 막기 위해 미련 없이 즉시 전량 칼손절 후퇴하시게."
            elif final_code == "SELL_ZONE":
                sig = "🟢 [상단 주의] 추격매수 금지 / 수확 목표선 코앞!"
                col = "#388E3C" 
                s_adv = f"• <b>[미보유자] ✋ 탐욕의 끝단이오! 추격매수 절대 금지!</b><br>• <b>[보유자]</b> 목표선 인접이므로 분할 익절하며 5일선 기준 홀딩<br>• 🚀 <b>[필수 방어선]</b> {stop_loss_label}"
            elif final_code == "WALL_BREAKOUT":
                sig = "🔵 [성벽 돌파 공방] 기세 유지 진격!"
                col = "#1E88E5"
                s_adv = f"• <b>[성벽 돌파 공방 중]</b> 현재 성벽({defense_line:{fmt_p}}{currency}) 돌파 시도 중이오. 기세를 살려 돌파하는지 5일선 기준으로 살피시게.<br>• 🚀 <b>[필수 방어선]</b> {stop_loss_label}"
            elif final_code == "OVER_EXTENDED":
                sig = "🟡 [이격 과열 관망] 5일선 +3% 초과!"
                col = "#FBC02D"
                s_adv = f"• ⚠️ <b>5일선 이격도가 +{bias_ma5:.1f}%로 과다 이격 상태</b>이므로 신규 추격매수를 금하고 <b>[관망]</b>하시게.<br>• 🚀 <b>[방어선]</b> {stop_loss_label}"
            elif final_code == "BREAKOUT":
                sig = "🟢 [상투 돌파] 푸른 수확 / 분할 익절 타점!"
                col = "#388E3C" 
                s_adv = f"• <b>[보유자] 💰 상투 과열권 수급 폭발! 물량 30~50% 1차 분할 익절(수익 확정)</b><br>• <b>[미보유자] ✋ 추격매수 절대 금지!</b><br>• 🚀 <b>[필수 방어선]</b> {stop_loss_label}"
            elif final_code == "BOTTOM_BUY":
                sig = "🔴 [매수] 1단계 진바닥 선취매! (20% 진격)"
                col = "#D32F2F" 
                s_adv = f"• <b>[미보유자] 🎯 [진바닥 기록 + 일봉 5일선 안착] 1차 선취매 20% 진격!</b><br>• <b>[손절 마지노선]</b> 🚀 {stop_loss_label}"
            elif final_code == "PULLBACK_BUY":
                sig = "🔵 [상승 추세 유지] 5일/20일선 안착 본진 진격!"
                col = "#1976D2" 
                s_adv = f"• <b>[기보유자/진입자] 🎯 [상승 모멘텀 유지 + 5일/20일선 안착] 기세 타며 홀딩 및 진격!</b><br>• <b>[손절 마지노선]</b> 🚀 {stop_loss_label}"
            else: 
                if is_down_trend_v:
                    sig = "🟡 [관망] 하방 압력 및 추세 이탈 경계"
                    col = "#C0CA33" 
                    s_adv = f"• ⚠️ 현재 하방 압력 및 하락세이므로 손가락을 묶고 <b>[관망]</b>하시게.<br>• 🚀 <b>[방어선]</b> {stop_loss_label}"
                else:
                    sig = "🟡 [관망] 방향 탐색 / 상방 기세 유지 대기"
                    col = "#FBC02D"
                    if bandwidth < 25.0 and p >= mid_line:
                        s_adv = f"• ⚠️ 밴드폭이 {bandwidth:.1f}%로 25% 미만이오니 <b>[관망]</b>하시게.<br>• 🚀 <b>[방어선]</b> {stop_loss_label}"
                    elif is_ma5_over_extended:
                        s_adv = f"• ⚠️ 5일선 이격 과열(+{bias_ma5:.1f}%)로 고무줄 늘어났으니 추격매수 금지 및 <b>[관망]</b>하시게.<br>• 🚀 <b>[방어선]</b> {stop_loss_label}"
                    else:
                        s_adv = f"• ⚠️ 이격 과열 및 지표 동조 대기로 관망 중일세.<br>• 🚀 <b>[방어선]</b> {stop_loss_label}"

            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><div class='signal-subtext'>{s_adv}</div></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선 (볼린저하단)</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선 (볼린저상단)</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            if defense_line > up_b:
                def_status = f"성벽({defense_line:{fmt_p}}{currency})이 수확목표선({up_b:{fmt_p}}{currency})보다 높은 <b>[고점 매물대]</b> 구역이오! 1차 수확선에서 짧게 익절하고 관망하시게."
            elif p >= defense_line:
                if p >= prev_p and p >= ma5_val:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 위에서 5일선 기세를 타고 <b>위로 진격 중</b>이네! 든든한 방어선을 등지고 계속 밀어붙이시게."
                else:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 위에는 있으나 단기 기세가 <b>숨고르기 중</b>이네! 5일선 안착 여부를 관망하시게."
            else:
                if is_ma5_safe:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래에 있으나, 단기 5일선<b>(생명선)을 사수</b>하며 성벽 탈환을 위한 반격의 시동을 거는 중이네!"
                else:
                    if p > prev_p and m_l >= s_l:
                        def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래(지하실)이나, 엔진 시동을 걸며 <b>지하실 탈출 시도 중</b>이네!"
                    else:
                        def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래로 함락된 채 기세마저 밑으로 처박히고 있네! <b>절대 칼을 뽑지 마시게.</b>"

            if m_l > s_l:
                if p < defense_line:
                    macd_strategy_msg = "<b>🔥 엔진 정회전 완료 (준비된 불꽃)</b><br>• <b>역할:</b> 상승 모멘텀 유지.<br>• <b>진단:</b> 성벽 아래에 있으나 엔진이 정회전으로 힘차게 돌고 있네! 성벽 돌파를 위해 아래에서 에너지를 바짝 응축하며 밀어 올리는 <b>강력한 준비 엔진 구역</b>이오."
                else:
                    macd_strategy_msg = "<b>🔥 엔진 정회전 완료 (순풍 구역)</b><br>• <b>역할:</b> 상승 모멘텀 유지.<br>• <b>진단:</b> 엔진 정회전 완료! 성벽 위에서 방어선을 등지고 본대 진격 신호탄이 터졌네."
            else:
                macd_strategy_msg = "<b>⚙️ 엔진 역회전 상태</b><br>• <b>역할:</b> 하락 조정 모멘텀.<br>• <b>진단:</b> " + ("🚀 [엔진 시동] 역회전폭 급감! 바닥에서 다시 고개를 치켜드는 <b>반격의 시동을 거는 밸브 개방 구역</b>이네." if is_macd_turning else "⚠️ 역회전 심화! 엔진 거꾸로 도는 차니 절대 진입 금지이오.")

            st.markdown(f"""<div class='trend-card'>
<div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 이격도({bias_ma5:+.1f}%) 상태이네. {'(+3% 초과 과다이격으로 관망 필요)' if is_ma5_over_extended else '안전 범위 내 진격 가능 구역이오.'}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>2. 성벽 사수 확인</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{def_status}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>3. 중장기 추세 진단 및 지표 동조 현황</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{indicator_verify_text}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>4. 엔진(MACD) 확인</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{macd_strategy_msg}</span>
</div>
<div style='margin-bottom: 25px;'>
<span style='color: #D32F2F; font-weight: 900; font-size: 24px;'>5. 🛡️ [보유자 전용] 실전 행동 가이드</span><br>
<span style='color: #2E7D32; font-weight: bold; font-size: 20px;'>👉 {holder_guide_msg}</span>
</div>
<hr style='border:1px solid #FFEBEE; margin: 20px 0;'>
<div class='final-msg'>
{final_adv}
</div>
</div>""", unsafe_allow_html=True)

            st.divider()
            
            i1, i2, i3, i4 = st.columns(4)
            
            with i1:
                if final_code == "BOTTOM_BUY":
                    bb_diag = f"🔴 <b>[진바닥 선취매 공략 구간] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 바닥권 과매도 및 5일선 안착 검증.<br>• <b>진단:</b> 진바닥 포착 후 5일선 안착 완료! 1단계 선취매(20%) 집행 구역이오."
                elif final_code == "STOP_LOSS_ALERT":
                    bb_diag = f"🚨 <b>[방어선 붕괴 비상 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 손절 마지노선 이탈 감지.<br>• <b>진단:</b> 주요 방어선이 무너졌으니 전량 칼손절 후퇴하시게."
                elif is_ma5_over_extended:
                    bb_diag = f"🟡 <b>[5일선 이격 과열 관망 구역] (이격도: +{bias_ma5:.1f}%)</b><br>• <b>역할:</b> 5일선 대비 +3% 초과 과다 이격 차단.<br>• <b>진단:</b> 고무줄이 너무 팽팽해졌으니 추격매수를 멈추고 이격이 좁혀질 때까지 <b>[관망]</b>하시게."
                elif is_near_target: 
                    bb_diag = f"👺 <b>[수확 목표선(상단) 과열 경계] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 주가 상단 한계선 접촉 및 탐욕 차단.<br>• <b>진단:</b> 상단선에 바짝 붙은 탐욕의 끝단이니 신규 진입을 철저히 금지하시게."
                elif final_code == "WALL_BREAKOUT":
                    bb_diag = f"🔵 <b>[성벽 돌파 공방 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 성벽 돌파 시도 중.<br>• <b>진단:</b> 성벽 근처에서 상방 돌파 공방 중이오. 5일선 기준 기세를 주시하시게."
                elif final_code == "PULLBACK_BUY":
                    bb_diag = f"🔵 <b>[상승 추세 유지 및 지지 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 상승 추세 속 상방 기세 유지.<br>• <b>진단:</b> 5일선 이격 과열 없이 우상향 진격 중이므로 추세를 믿고 홀딩하는 구역이오."
                elif is_breakout: 
                    bb_diag = f"🚀 <b>[상투 과열권 수급 돌파] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 상단 저항선 돌파 강도 측정.<br>• <b>진단:</b> 상투 과열권 돌파! 보유자는 분할 익절, 미보유자는 추격 금지."
                elif is_down_trend_v:
                    bb_diag = f"📉 <b>[하방 압력 및 중앙선 이탈 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 하락 추세 속 리스크 관리.<br>• <b>진단:</b> 하방 압력 국면이므로 관망하시게."
                else:
                    bb_diag = f"🔥 <b>[방향 탐색 및 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 이격 조율 모니터링.<br>• <b>진단:</b> 이격 과열 해소 및 지표 동조를 차분히 주시하시게."
                
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세/위치)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2:
                rsi_trend = "▲ 상승" if rsi_val > rsi_prev else ("▼ 하락" if rsi_val < rsi_prev else "─ 변동없음")
                is_div = p > prev_p and rsi_val < rsi_prev and not is_uptrend_momentum
                if rsi_val >= 60: 
                    r_status = f"<b>👿 불지옥 과열권</b><br>• <b>역할:</b> 매수 에너지 고갈 경보.<br>• <b>진단:</b> {'🚨 [가짜 상승] 주가 상승에도 RSI 하락! 세력 속임수니 대피하시게.' if is_div else ('🚀 [강한 상승 에너지] 상승 추세 속 상방 문턱을 두드리는 추진력 구역이오.' if is_uptrend_momentum else '과열 구간 진입, 차익 실현을 준비하시게.')}"
                elif rsi_val <= 35: 
                    r_status = f"<b>🧊 냉골 바닥권</b><br>• <b>역할:</b> 진바닥 수급 에너지 감지.<br>• <b>진단:</b> {'🔥 [온도 상승] 바닥 탈출 신호 포착! 일봉 5일선 안착 시 1단계 선취매(20%) 타점 판독.' if rsi_val > rsi_prev else '매수 에너지 고갈 중. 지속 관망하시게.'}"
                else: 
                    r_status = f"<b>⚖️ 적정 온도 구간</b><br>• <b>역할:</b> 에너지 충전 및 눌림목 동조.<br>• <b>진단:</b> {'🚨 [다이버전스] 가짜 기세니 속지 마시게.' if is_div else '에너지 충전 중. 보조지표 고개 돌림을 주시하시게.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (매수 온도)</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{rsi_val:.2f} <span style='font-size:22px; color:#333333;'>({rsi_trend})</span></p><p class='ind-diag'>{r_status}</p></div>", unsafe_allow_html=True)
            
            with i3:
                will_trend = "▲ 상승" if will_val > will_prev else ("▼ 하락" if will_val < will_prev else "─ 변동없음")
                if will_val >= -20: 
                    if final_code == "PULLBACK_BUY" or (m_l > s_l and is_ma5_safe) or is_uptrend_momentum:
                        w_status = "<b>🚀 상방 돌파 도전 구역</b><br>• <b>역할:</b> 단기 상향 압력 측정.<br>• <b>진단:</b> 엔진이 정회전하며 위로 치고 나가는 기세이므로, 단기 천장 지표(-20 위)는 단순 과열이 아니라 <b>상방 문턱을 두드리며 밀어 올리는 강한 추진력</b>이오."
                    else:
                        w_status = "<b>🚩 단기 천장 과열 경계</b><br>• <b>역할:</b> 단기 상투 가장 빠르게 포착.<br>• <b>진단:</b> 지수가 천장권에 진입했으나 타 지표 여유가 있으므로 추세 유지 여부를 관망하시게."
                elif will_val >= -35: 
                    if final_code == "PULLBACK_BUY" or (m_l > s_l and is_ma5_safe) or is_uptrend_momentum:
                        w_status = "<b>⚔️ 상방 압력 집중 구간</b><br>• <b>역할:</b> 상승 에너지 도달 확인.<br>• <b>진단:</b> 상승 추세 속 단기 저항대에 진입했으나, 5일선/20일선 안착 상태이므로 <b>추세 연장 및 승순 확대 흐름과 일치</b>하오."
                    else:
                        w_status = "<b>⚠️ 천장 근접 경계</b><br>• <b>역할:</b> 상단 매도 타점 예보.<br>• <b>진단:</b> 고점 징후 포착 중이니 매수 금지, 분할 매도 준수하시게."
                elif will_val <= -80:
                    if will_val > will_prev and is_ma5_safe:
                        w_status = "<b>🏳️ 개미 항복 구역</b><br>• <b>역할:</b> 세력 선취매 및 반전 포착.<br>• <b>진단:</b> 🚀 <b>[항복 후 반격]</b> -80 위로 고개 듦! 1단계 진바닥 선취매 신호 포착."
                    else:
                        w_status = "<b>🏳️ 개미 항복 구역</b><br>• <b>역할:</b> 세력 선취매 및 반전 포착.<br>• <b>진단:</b> 🧊 <b>[바닥 침체]</b> -80 밑 투매 진행 중! 일봉 5일선 종가 안착 전까진 매수 금지이외다."
                elif will_val <= -65: 
                    w_status = f"<b>📉 낙폭 과대 지대</b><br>• <b>역할:</b> 눌림목 반등 타점 감지.<br>• <b>진단:</b> {'🌱 하락 브레이크 포착! 반등 동조 점수 가산 중.' if will_val > will_prev else '하락 가속 중! 손가락을 묶으시게.'}"
                else: 
                    w_status = "<b>⚖️ 중간 지대</b><br>• <b>역할:</b> 추세 방향 탐색.<br>• <b>진단:</b> 상/하방 방향 탐색 중. 20일선 지지 여부를 지켜보시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R (민감 반전)</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{will_val:.2f} <span style='font-size:22px; color:#333333;'>({will_trend})</span></p><p class='ind-diag'>{w_status}</p></div>", unsafe_allow_html=True)
            
            with i4:
                if m_l > s_l:
                    m_diag = "<b>🔥 엔진 정회전 완료</b><br>• <b>역할:</b> 상승 모멘텀 유지.<br>• <b>진단:</b> " + ("성벽 돌파를 위해 아래에서 에너지를 바짝 응축하며 밀어 올리는 <b>강력한 준비 엔진 구역</b>이오." if p < defense_line else "엔진 정회전! 성벽 사수하며 자신 있게 추세 진격하시게.")
                else:
                    m_diag = "<b>⚙️ 엔진 역회전 상태</b><br>• <b>역할:</b> 하락 조정 모멘텀.<br>• <b>진단:</b> " + ("🚀 [엔진 시동] 역회전폭 급감! 반격의 시동을 거는 중이니 5일선 위에서의 안착 유지 여부를 주시하시게." if is_macd_turning else "⚠️ 역회전 심화! 엔진 거꾸로 도는 차니 절대 진입 금지이오.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (추세 엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
