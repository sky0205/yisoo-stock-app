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
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36061", layout="wide")
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

st.title("🧐 이수할아버지의 냉정 진단기 v36061")
display_global_risk(); st.divider()

# ==============================================================================
# ★ [메인 화면 상단: 종목 / 수동입력 / 평단가 4칸 통합 입력창]
# ==============================================================================
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

        # ==============================================================================
        # ★ [현재가(p) 수동 입력 최우선 채택 스위치 연산]
        # ==============================================================================
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
                if len(df) >= 2:
                    prev_p = float(df['Close'].iloc[-2])
                elif len(df) == 1:
                    prev_p = float(df['Close'].iloc[-1])
                else:
                    prev_p = p

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

            # --- [거래량 및 시간보정 연산 장치] ---
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

            # 보조지표 연산
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

            # ★ [손절가 5% 고정 원칙 적용: 할아버지의 엄격한 손절 룰 반영]
            # 진바닥 1단계 진입 시 매수가 대비 -5% 또는 전저점/5일선 기준 중 더 촘촘한 방어선 선택
            stop_loss_price = p * 0.95
            stop_loss_label = f"진바닥 입질가 대비 -5% 칼손절({stop_loss_price:{fmt_p}}{currency})"

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
                f"&nbsp;&nbsp;<span style='color:#D32F2F; font-weight:bold;'>🔴 5일선: {ma5_str}</span> | "
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

            is_down_trend_v = (p < prev_p) and (p_chg < 0)
            is_bearish_candle = p < prev_p

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
                    "META": "메타", "IONQ": "아이온큐", "CPNG": "쿠팡", "NFLX": "넷플릭스",
                    "SKHY": "SK하이닉스"
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

            # --- [거래량 전황 판정] ---
            if is_manual_mode:
                v_status, v_adv = "수동검증", f"⚡ <b>[프리장/수동 연산]</b> 수동 입력 시세를 기준으로 정밀 검증 중이외다."
            elif vol_strength >= 150:
                if not is_down_trend_v:
                    v_status, v_adv = "과열폭발", f"🔥 <b>[화력폭발]</b> 시간보정 강도 {vol_strength:.1f}점! 바닥 거래량 폭발 또는 본진 진격 중이오."
                else:
                    v_status, v_adv = "역배열투매", f"🚨 <b>[역배열/하방 투매과열]</b> 시간보정 강도 {vol_strength:.1f}점! 하방 압력 속 투매 물량 폭발 중이니 절대 칼날을 잡지 마시게."
            elif vol_strength >= 100: 
                if not is_down_trend_v:
                    v_status, v_adv = "매집시작", f"🚀 <b>[매집시작]</b> 시간보정 강도 {vol_strength:.1f}점! 화력이 차오르네."
                else:
                    v_status, v_adv = "역배열과열", f"⚠️ <b>[역배열과열]</b> 시간보정 강도 {vol_strength:.1f}점! 하락 추세 속 속임수 음봉 거래량 주의."
            elif vol_strength >= 80: 
                v_status, v_adv = "정상화력", f"⚔️ <b>[정상화력]</b> 시간보정 강도 {vol_strength:.1f}점! 기세가 뻣뻣하구먼."
            else: 
                v_status, v_adv = "거래절벽", f"🧊 <b>[거래절벽]</b> 시간보정 강도 {vol_strength:.1f}점! 수급이 마르고 동력이 없으니 속지 마시게."
            
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량 전황: {v_status} ({'수동 연산 모드' if is_manual_mode else f'실시간 {v_ratio:.1f}% / 5일평균대비'})</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            bb_bot_series = (df['Close'] <= (low_b * 1.02)).astype(int)
            rsi_bot_series = (rsi_series <= 35).astype(int)
            will_bot_series = (will_series <= -80).astype(int)
            bottom_score_series = bb_bot_series + rsi_bot_series + will_bot_series
            
            bottom_score = bottom_score_series.iloc[-1]
            recent_bottom_memory = (bottom_score_series.iloc[-3:].max() >= 2)

            is_uptrend = (p >= mid_line) or (ma20_slope > 0)
            
            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            bias_ma20 = ((p - mid_line) / mid_line) * 100 if mid_line > 0 else 0

            # --- [손절 조건 검증] ---
            is_stop_loss_triggered = False
            stop_reason = ""
            if user_avg_price > 0 and p < stop_loss_price:
                is_stop_loss_triggered = True
                stop_reason = f"보유 평단가 대비 손절 마지노선(-5%) 붕괴"
            elif (recent_bottom_memory or bottom_score >= 2) and p < stop_loss_price:
                is_stop_loss_triggered = True
                stop_reason = f"진바닥 방어선(-5%) 이탈 붕괴"

            # ==============================================================================
            # ★ [할아버지 3단계 매수 & 성벽 음봉 매도 로직 이식]
            # ==============================================================================
            # 1단계: 진바닥 입질 매수 (지표 2개 이상 터치 + 거래량 유입)
            is_bottom_entry_signal = (bottom_score >= 2) and (vol_strength >= 80)

            # 2단계: 진바닥 탈출 추가 매수 (5일선 위 안착)
            is_escape_buy_signal = is_ma5_safe and (bottom_score >= 1 or recent_bottom_memory)

            # 3단계: 눌림목 추가 매수 (5일선, 20일선 위 안착 + 밴드폭 넉넉함)
            p_will = 1 if will_val <= -50 else 0
            p_bb = 1 if (mid_line * 0.98 <= p <= mid_line * 1.01) else 0
            p_rsi = 1 if (40 <= rsi_val <= 55) else 0
            pullback_rebound_score = p_will + p_bb + p_rsi
            is_pullback_buy_signal = (p >= mid_line) and is_ma5_safe and (pullback_rebound_score >= 2) and (vol_strength >= 80) and (bandwidth >= 25.0)

            # 성벽 위 및 목표선 도달 / 음봉 매도 로직
            target_price_100 = up_b
            is_on_the_wall = (p >= target_price_100 * 0.95) and (p < target_price_100)
            is_target_reached = p >= target_price_100

            if bottom_score >= 2:
                bottom_status_str = f"<b>(진바닥 지표 {bottom_score}개 터치 달성!)</b>"
                if is_stop_loss_triggered:
                    bottom_action_str = f"➔ <b>[비상 후퇴]</b> 방어선(-5%) 붕괴로 매수 금지"
                elif vol_strength < 80:
                    bottom_action_str = f"➔ <b>[입질 대기]</b> 지표 충족이나 거래량 부족({vol_strength:.1f}점)으로 매수 보류"
                else:
                    bottom_action_str = f"➔ <b>[1단계 진바닥 입질 매수]</b> 지표 충족 + 거래량 유입! 소량 입질 매수 시작 (손절 -5% 설정)"
            else:
                bottom_status_str = "<b>(조건 미흡)</b>"
                bottom_action_str = "➔ <b>[관망]</b> 진바닥 지표 조건 미충족"

            if bandwidth < 25.0 and p >= mid_line:
                pullback_status_str = f"<b>(밴드폭 협소 {bandwidth:.1f}%)</b>"
                pullback_action_str = "➔ <b>[매수 보류]</b> 밴드폭 25% 미만으로 먹을 자리가 부족하여 승수 확대 금지"
            else:
                pullback_status_str = f"<b>(조건 만족 / 밴드폭 {bandwidth:.1f}%)</b>"
                if is_pullback_buy_signal:
                    pullback_action_str = "➔ <b>[3단계 눌림목 추가 매수]</b> 5·20일선 위 안착 + 승수 확대 진격!"
                else:
                    pullback_action_str = "➔ <b>[돌파/안착 대기]</b> 상방 공방 및 이격 조율 중 관망"

          # --- [최종 결론 판정: 성벽 위 음봉 매도 반영 최우선] ---
            if is_stop_loss_triggered:
                final_code = "STOP_LOSS_ALERT"
                final_adv = f"🚨 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[{stop_reason}]</b> 방어선 완전 함락! 미련을 버리고 즉시 전량 칼손절 후퇴하시게."
            elif is_on_the_wall and is_bearish_candle:
                final_code = "RED_SELL_WARNING"
                final_adv = f"🔴 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[성벽 위 음봉 발생]</b> 성벽 위 공방 중 음봉이 떨어졌으니, 목표선 미도달이라도 선제적 익절로 수익을 지키시게!"
            elif is_target_reached:
                final_code = "RED_SELL_TARGET"
                final_adv = f"🔴 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[수확 목표선 도달]</b> 성벽 위 목표선 도달 완료! 즉시 분할 익절 및 전량 매도로 수익 확정하시게."
            elif is_on_the_wall:
                final_code = "YELLOW_CAUTION"
                final_adv = f"🟡 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[성벽 위 진입 및 공방]</b> 추격 매수는 절대 금지하고, 매도 준비 및 경계 태세를 갖추시게!"
            elif is_bottom_entry_signal and not is_stop_loss_triggered:
                final_code = "BOTTOM_ENTRY"
                final_adv = f"🟢 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[진바닥 입질 매수]</b> 주요 지표 터치 + 거래량 유입! 소량 입질 매수 시작 (손절선 -5% 설정)."
            elif is_escape_buy_signal and not is_stop_loss_triggered:
                final_code = "ESCAPE_BUY"
                final_adv = f"🟢 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[진바닥 탈출 매수]</b> 거래량이 실리며 5일선 위 안착 성공! 추가 매수로 배팅 확대."
            elif is_pullback_buy_signal and not is_stop_loss_triggered:
                final_code = "PULLBACK_BUY"
                final_adv = f"🔵 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[눌림목 추가 매수]</b> 5일선·20일선 위 안정적 안착 및 활주로 확보! 승수 확대."
            else:
                final_code = "WAIT_GENERAL"
                final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 조건 미충족 상태이므로 뇌동매매를 금하고 관망세 유지하시게!"

            indicator_verify_text = (
                f"{ma_price_summary}<br>"
                f"• <b>[추세 정밀 판독]:</b> {trend_status}<br>"
                f"• <b>[지표 검증 연산]</b><br>"
                f"   - <b>진바닥 입질 동조:</b> {bottom_score}개 터치 {bottom_status_str} {bottom_action_str}<br>"
                f"   - <b>눌림목 동조:</b> {pullback_rebound_score}/3점 {pullback_status_str} {pullback_action_str}"
                f"{squeeze_info_str}"
            )

            if user_avg_price <= 0:
                holder_guide_msg = f"현재 추세 탐색 및 방향 정립 구간이니 성벽({defense_line:{fmt_p}}{currency})이나 5일선 사수 여부를 확인하며 차분히 보유 판단을 내리시게. (★ <b>손절 마지노선: {stop_loss_label}</b>)"
            else:
                profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                if p >= user_avg_price:
                    holder_guide_msg = (
                        f"📈 <b>[수익권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} / 수익률: +{profit_rate:.2f}%)]</b><br>"
                        f"• 5일선({ma5_val:{fmt_p}}{currency}) 사수 여부를 주시하시고, 수확 목표선({target_price_100:{fmt_p}}{currency})까지 자신 있게 홀딩하시게.<br>"
                        f"• 성벽 위에서 음봉이 떨어지거나 꺾이면 지체 없이 선제적 익절로 수익을 확정하시게."
                    )
                else:
                    holder_guide_msg = (
                        f"📉 <b>[손실권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} / 손실률: {profit_rate:.2f}%)]</b><br>"
                        f"• <b>5일선({ma5_val:{fmt_p}}{currency}) 아래에서는 추측 추가 매수(물타기)를 절대 금지하네.</b><br>"
                        f"• 손절 마지노선(-5% 또는 방어선) 이탈 시 미련 없이 칼손절 후퇴하시게."
                    )

            # 신호등 박스 색상 및 문구 매핑
            if final_code == "STOP_LOSS_ALERT":
                sig = "🚨 [비상 손절] 방어선(-5%) 붕괴! 전량 칼손절 후퇴!"
                col = "#D32F2F"
                s_adv = f"• <b>[긴급 집행] {stop_reason}!</b> 추가 손실을 막기 위해 미련 없이 즉시 전량 칼손절 후퇴하시게."
            elif final_code == "RED_SELL_TARGET":
                sig = "🔴 [매도] 수확 목표선 도달! 이익실현 타점!"
                col = "#D32F2F"
                s_adv = (
                    "• 🎯 <b>[수확 완료] 수확 목표선에 늠름하게 도달했네!</b> 물량 30~50%를 "
                    "매도하여 수익을 확실하게 챙기시게.<br>• ✋ <b>[미보유자]</b> 고가 추격 "
                    "매수 절대 금지!"
                )

            elif final_code == "RED_SELL_WARNING":
              sig = "🔴 [매도] 성벽 위 음봉 발생! 선제적 익절 권유"
              col = "#D32F2F"
              s_adv = (
                  "• ⚠️ <b>[경계 익절]</b> 성벽 위 공방 중 음봉이 떨어졌네! 목표선 미도달이나"
                  " 기세 꺾이기 전에 <b>선제적 분할 매도</b>로 수익을 지키시게."
              )
            elif final_code == "YELLOW_CAUTION":
              sig = "🟠 [경계] 성벽 위 공방 / 매도 준비!"
              col = "#EF6C00"  # 진한 오렌지색으로 변경하여 관망과 확실히 구분
              s_adv = (
                  "• <b>[경계 태세]</b> 성벽 위 진입! 추격 매수는 철저히 차단하고, <b>수확"
                  " 목표선 도달 시 매도할 준비</b>를 하시게."
              )
            elif final_code == "RED_SELL_WARNING":
              sig = "🔴 [매도] 성벽 위 음봉 발생! 선제적 익절 권유"
              col = "#D32F2F"
              s_adv = (
                  "• ⚠️ <b>[경계 익절]</b> 성벽 위 공방 중 <b>음봉(하락)</b>이 떨어졌네! 목표선"
                  " 도달 전이라도 기세가 꺾이기 전에 <b>선제적 분할 매도</b>로 수익을"
                  " 단디 챙기시게."
              )
            elif final_code == "BOTTOM_ENTRY":
                sig = "🟢 [매수] 1단계 진바닥 입질 매수 (소량)"
                col = "#388E3C" 
                s_adv = f"• <b>[입질 진격]</b> 진바닥 터치 + 거래량 유입 포착! 소량 씨앗 뿌리기 진격 (손절 -5% 철저 준수)."
            elif final_code == "ESCAPE_BUY":
                sig = "🟢 [매수] 2단계 진바닥 탈출 추가 매수 (5일선 위)"
                col = "#2E7D32" 
                s_adv = f"• <b>[추가 진격]</b> 거래량이 실리며 5일선 위 안착 성공! 배팅 비중을 늘려 밭을 다짐."
            elif final_code == "PULLBACK_BUY":
                sig = "🔵 [매수] 3단계 눌림목 추가 매수 (승수 확대)"
                col = "#1976D2" 
                s_adv = f"• <b>[승수 확대]</b> 5일선·20일선 위 안착 및 활주로 확보 완료! 알짜배기 추가 매수."
            else:
                sig = "🟡 [관망] 조건 미충족 / 뇌동매매 금지"
                col = "#FBC02D"
                s_adv = f"• <b>[관망 유지]</b> 확실한 바닥 신호나 매수/매도 조건이 맞을 때까지 손가락을 묶고 대기하시게."

            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><div class='signal-subtext'>{s_adv}</div></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선 (볼린저하단)</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선 (볼린저상단)</p><p style='color:#D32F2F; font-size:32px;'>{format(target_price_100, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            if defense_line > up_b:
                def_status = f"성벽({defense_line:{fmt_p}}{currency})이 수확목표선({up_b:{fmt_p}}{currency})보다 높은 <b>[고점 매물대]</b> 구역이오! 1차 수확선에서 짧게 익절하고 관망하시게."
            elif p >= defense_line:
                if p >= prev_p and p >= ma5_val:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 위에서 5일선 기세를 타고 <b>위로 진격 중</b>이네! 든든한 방어선을 등지고 계속 밀어붙이시게."
                else:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 위에는 있으나 단기 기세가 <b>숨고르기 중</b>이네! 성벽 위 음봉 발생 시 선제적 익절을 준비하시게."
            else:
                if is_ma5_safe:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래에 있으나, 단기 5일선<b>(생명선)을 사수</b>하며 반격의 시동을 거는 중이네!"
                else:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래로 함락된 채 기세마저 밑으로 처박히고 있네! <b>절대 칼을 뽑지 마시게.</b>"

            if m_l > s_l:
                macd_strategy_msg = "<b>🔥 엔진 정회전 완료 (순풍 구역)</b><br>• <b>역할:</b> 상승 모멘텀 유지.<br>• <b>진단:</b> 엔진 정회전 완료! 바닥 입질 후 성벽을 향해 본대 진격 신호탄이 터졌네."
            else:
                if m_l > s_l:
                    macd_strategy_msg = "<b>🔥 엔진 정회전 완료 (순풍 구역)</b><br>• <b>역할:</b> 상승 모멘텀 유지.<br>• <b>진단:</b> 엔진 정회전 완료! 바닥 입질 후 성벽을 향해 본대 진격 가능구역이오."
                else:
                    macd_strategy_msg = "⚙️ <b>엔진 역회전 상태</b><br>• <b>역할:</b> 하락 조정 모멘텀.<br>• <b>진단:</b> " + ("🚀 [엔진 시동] 역회전폭 급감! 바닥에서 다시 고개를 치켜드는 <b>반격의 시동을 거는 밸브 개방 구역</b>이네." if m_l > s_l else "⚠️ 역회전 심화! 엔진 거꾸로 도는 차니 절대 진입 금지이오.")
            st.markdown(f"""<div class='trend-card'>
<div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) {'아래로 이탈했으니 종가 안착 전까진 손가락을 묶으시게.' if not is_ma5_safe else '위에 안착하여 단기 전투선이 살아있네. 본진 진격 가능구역이오.'}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>2. 성벽 사수 및 공방 확인</span><br>
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
            
            # --- 하단 4대 핵심 지표 박스 ---
            i1, i2, i3, i4 = st.columns(4)
            
            with i1:
                if final_code == "BOTTOM_ENTRY":
                    bb_diag = f"🔴 <b>[1단계 진바닥 입질 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 과매도 바닥권 선취매.<br>• <b>진단:</b> 지표 터치 + 거래량 유입! 소량 입질 매수 시작 (손절 -5% 설정)."
                elif final_code == "ESCAPE_BUY":
                    bb_diag = f"🟢 <b>[2단계 진바닥 탈출 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 5일선 안착 후 배팅 확대.<br>• <b>진단:</b> 거래량 실리며 5일선 위 안착 성공! 추가 매수로 비중 확대."
                elif final_code == "PULLBACK_BUY":
                    bb_diag = f"🔵 <b>[3단계 눌림목 추가 매수 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 추세 속 승수 확대.<br>• <b>진단:</b> 5·20일선 위 안정적 안착 및 활주로 확보로 알짜배기 추가 매수 집행."
                elif final_code in ["RED_SELL_TARGET", "RED_SELL_WARNING"]:
                    bb_diag = f"🔴 <b>[성벽 위 수확 및 음봉 익절 구간]</b><br>• <b>역할:</b> 고점 수익 확정.<br>• <b>진단:</b> 목표선 도달 또는 성벽 위 음봉 발생으로 선제적 익절 실행."
                elif final_code == "YELLOW_CAUTION":
                    bb_diag = f"🟡 <b>[성벽 위 경계 및 추격 차단 구역]</b><br>• <b>역할:</b> 고가 추격 매수 원천 차단.<br>• <b>진단:</b> 성벽 위 공방 중이므로 신규 매수를 금지하고 익절 타이밍을 노림."
                else:
                    bb_diag = f"⚖️ <b>[관망 및 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 뇌동매매 방지.<br>• <b>진단:</b> 명확한 바닥/추세 신호가 뜰 때까지 손가락을 묶고 관망 유지."
                
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세/위치)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2:
                rsi_trend = "▲ 상승" if rsi_val > rsi_prev else ("▼ 하락" if rsi_val < rsi_prev else "─ 변동없음")
                if rsi_val >= 60: 
                    r_status = f"<b>👿 불지옥 과열권</b><br>• <b>역할:</b> 매수 에너지 고갈 경보.<br>• <b>진단:</b> 과열 구간 진입, 성벽 위 익절 및 차익 실현을 준비하시게."
                elif rsi_val <= 35: 
                    r_status = f"<b>🧊 냉골 바닥권</b><br>• <b>역할:</b> 진바닥 수급 에너지 감지.<br>• <b>진단:</b> 바닥권 지표 터치 및 거래량 유입 시 1단계 입질 매수 타이밍."
                else: 
                    r_status = f"<b>⚖️ 적정 온도 구간</b><br>• <b>역할:</b> 에너지 충전 및 눌림목 동조.<br>• <b>진단:</b> 에너지 충전 중. 보조지표 고개 돌림을 주시하시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (매수 온도)</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{rsi_val:.2f} <span style='font-size:22px; color:#333333;'>({rsi_trend})</span></p><p class='ind-diag'>{r_status}</p></div>", unsafe_allow_html=True)
            
            with i3:
                will_trend = "▲ 상승" if will_val > will_prev else ("▼ 하락" if will_val < will_prev else "─ 변동없음")
                if will_val >= -20: 
                    w_status = "<b>🚀 상방 돌파 도전 구역</b><br>• <b>역할:</b> 단기 상향 압력 측정.<br>• <b>진단:</b> 성벽 위 목표선 근접 구역이오. 음봉 발생 시 선제적 매도 대비."
                elif will_val <= -80:
                    w_status = "<b>🏳️ 개미 항복 구역</b><br>• <b>역할:</b> 세력 선취매 및 반전 포착.<br>• <b>진단:</b> 🧊 <b>[바닥 침체]</b> -80 밑 투매 진행 중! 지표 동조 및 거래량 유입 시 입질 대기."
                else: 
                    w_status = "<b>⚖️ 중간 지대</b><br>• <b>역할:</b> 추세 방향 탐색.<br>• <b>진단:</b> 상/하방 방향 탐색 중."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R (민감 반전)</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{will_val:.2f} <span style='font-size:22px; color:#333333;'>({will_trend})</span></p><p class='ind-diag'>{w_status}</p></div>", unsafe_allow_html=True)
            
            with i4:
                if m_l > s_l:
                    m_diag = "<b>🔥 엔진 정회전 완료</b><br>• <b>역할:</b> 상승 모멘텀 유지.<br>• <b>진단:</b> 엔진 정회전! 성벽 사수하며 자신 있게 추세 진격하시게."
                else:
                    m_diag = "<b>⚙️ 엔진 역회전 상태</b><br>• <b>역할:</b> 하락 조정 모멘텀.<br>• <b>진단:</b> 역회전 심화! 섣부른 매수를 금지하고 관망하시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (추세 엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
