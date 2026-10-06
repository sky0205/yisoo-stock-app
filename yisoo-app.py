import html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
import os

st.set_page_config(page_title="이수할아버지의 냉정 진단기 최종본", layout="wide")

# --- 🔒 자물쇠(비밀번호) 보안 장치 ---
def check_password():
    correct_pw = str(st.secrets.get("APP_PASSWORD", "1111"))

    def password_entered():
        if st.session_state["password"] == correct_pw:
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

if not check_password():
    st.stop()

# --- [보급로 최적화 캐싱 장치] ---
@st.cache_data(ttl=300)
def fetch_global_market():
    tickers = {"n": "^IXIC", "s": "^GSPC", "d": "^DJI", "t": "^TNX", "u": "USDKRW=X"}
    results = {}
    for k, tk in tickers.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}?interval=1d&range=1d"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
            meta = res.json()["chart"]["result"][0]["meta"]
            results[f"{k}_last"] = float(meta["regularMarketPrice"])
            results[f"{k}_prev"] = float(meta["chartPreviousClose"])
        except Exception:
            results[f"{k}_last"], results[f"{k}_prev"] = 0.0, 0.0
    return results

# --- [종목명 해독 통합 함수 (중복 제거용)] ---
def get_stock_name(symbol, is_kr):
    if is_kr:
        clean_sym = str(symbol).strip().zfill(6)
        core_vault = {
            "005930": "삼성전자", "000660": "SK하이닉스", "033100": "제룡전기",
            "257720": "실리콘투", "058610": "에스피지", "010140": "삼성중공업",
            "068270": "셀트리온", "272210": "한화시스템", "101490": "에스앤에스텍",
            "051600": "한전KPS", "064350": "현대로템", "032300": "솔리드", "050890": "솔리드"
        }
        if clean_sym in core_vault:
            return core_vault[clean_sym]
        
        if not os.path.exists("krx_list.csv"):
            return f"국내종목 ({clean_sym})"
            
        try:
            try:
                with open("krx_list.csv", "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open("krx_list.csv", "r", encoding="cp949", errors="ignore") as f:
                    lines = f.readlines()
            
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    c1 = parts[0].strip().replace('"', '')
                    c2 = parts[1].strip().replace('"', '')
                    if c1.zfill(6) == clean_sym: return c2
                    elif c2.zfill(6) == clean_sym: return c1
        except Exception:
            pass
        return f"국내종목 ({clean_sym})"
    else:
        us_vault = {
            "TSLA": "테슬라", "NVDA": "엔비디아", "AAPL": "애플", "MSFT": "마이크로소프트",
            "AMZN": "아마존", "GOOGL": "알파벳A", "META": "메타", "IONQ": "아이온큐",
            "CPNG": "쿠팡", "NFLX": "넷플릭스", "SKHY": "SK하이닉스", "INTC": "인텔",
            "BE": "블룸에너지", "RKLB": "로켓랩", "AVGO": "브로드컴", "LRCX": "램리서치",
        }
        tk = symbol.upper()
        if tk in us_vault: 
            return f"{us_vault[tk]} ({tk})"
        try:
            info_dict = yf.Ticker(tk).info
            kor_name = info_dict.get("longName", info_dict.get("shortName", tk))
            return f"{kor_name} ({tk})"
        except Exception:
            return tk

# 1. 스타일 및 화면 구성
st.markdown(
    """
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-box * { color: #FFFFFF !important; }
    .signal-text { font-size: 44px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .signal-subtext { font-size: 22px !important; color: #FFFFFF !important; line-height: 1.6; margin-top: 10px; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 12px; border: 2.5px solid #CFD8DC; text-align: center; box-shadow: 1px 1px 6px rgba(0,0,0,0.05); }
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
    """,
    unsafe_allow_html=True,
)

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

        avg_us_chg = (n_chg + s_chg + d_chg) / 3
        pos_cnt = sum([n_chg > 0, s_chg > 0, d_chg > 0])
        neg_cnt = sum([n_chg < 0, s_chg < 0, d_chg < 0])

        if pos_cnt == 3: market_mood = "미 3대 지수 동반 훈풍 속 안도 랠리!" if avg_us_chg >= 1.0 else "미 3대 지수 일제히 상승 마감!"
        elif neg_cnt == 3: market_mood = "미 3대 지수 동반 급락으로 투심 냉각!" if avg_us_chg <= -1.0 else "미 3대 지수 일제히 하락 (전면 약세 국면)!"
        else: market_mood = "미 3대 지수 혼조세 속 숨고르기 진행!"

        macro_alerts = []
        if tnx_val >= 4.5: macro_alerts.append(f"🚨 [금리 발작] 국채 금리 {tnx_val:.3f}% 돌파!")
        elif tnx_val <= 3.8: macro_alerts.append(f"🌱 [금리 안정] 국채 금리 {tnx_val:.3f}% 안정권 진입")

        if u_val >= 1450: macro_alerts.append(f"🚨 [환율 격랑] 원/달러 {u_val:,.2f}원! 초위험 고환율 비상!")
        elif u_val >= 1400: macro_alerts.append(f"⚠️ [환율 경계] 원/달러 {u_val:,.2f}원 1,400원대 고착화 압박!")
        elif u_val >= 1380: macro_alerts.append(f"⚡ [환율 분기점] 원/달러 {u_val:,.2f}원! 외인 눈치보기")
        elif u_val <= 1330: macro_alerts.append(f"💵 [환율 우호] 원/달러 {u_val:,.2f}원 하향 안정세")

        if u_chg > 0.3: macro_alerts.append(f"📈 오늘 환율 {u_chg:+.2f}% 치솟는 중!")
        elif u_chg < -0.3: macro_alerts.append(f"📉 오늘 환율 {u_chg:+.2f}% 진정세")

        if tnx_val >= 4.5 or u_val >= 1380: strategy = "외인 수급 이탈 우려로 상단 저항이 강하니 추격매수 금지, 5일선 및 방어선 위주로 보수적 대응하시게."
        elif avg_us_chg > 0.5 and tnx_val < 4.2 and u_val < 1350: strategy = "매크로 환경이 우호적이니 거래량 실린 정석 눌림목 주도주 위주로 적극 공략하시게."
        else: strategy = "장 초반 뇌동매매를 삼가고 지표 동조와 5일선 안착 여부를 확인하며 기민하게 대응하시게."

        macro_text = " | ".join(macro_alerts) if macro_alerts else "매크로 특이 동향 없음"
        st.info(f"🧐 **이수 할배의 글로벌 판독:** {market_mood}!\n\n- {macro_text}\n- 💡 **[대응 전략]** {strategy}")
    except Exception:
        st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 최종본 (원본 뼈대 100% 복구 + 족쇄 탑재)")
display_global_risk()
st.divider()

# ==============================================================================
# ★ [상단: 종목 / HTS 전일종가 / 미장 프리시세 / 보유 평단가 / 호가잔량]
# ==============================================================================
col_symbol, col_prev, col_pre_us, col_avg, col_ask, col_bid, col_btn = st.columns([1.4, 1.2, 1.2, 1.2, 1.1, 1.1, 0.8])

with col_symbol:
    raw_symbol_input = st.text_input("📊 종목번호", "LRCX")
    symbol = raw_symbol_input.strip()

with col_prev:
    manual_prev_price_str = st.text_input("🎯 HTS 전일종가", value="", help="국장/미장 전일 기준가").strip()

with col_pre_us:
    manual_pre_price_str = st.text_input("🇺🇸 미장 프리(Pre) 시세", value="", help="미장 프리마켓 실시간 가격 입력 시 수급 페널티 제외 반영").strip()

with col_avg:
    user_avg_price = st.number_input("💡 보유 평단가", min_value=0.0, value=0.0, step=100.0, help="맞춤형 가이드 제공")

with col_ask:
    manual_ask = st.number_input("🔴 총매도잔량", min_value=0.0, value=0.0, step=1.0, format="%.2f")

with col_bid:
    manual_bid = st.number_input("🔵 총매수잔량", min_value=0.0, value=0.0, step=1.0, format="%.2f")

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
            start_date = datetime.now(ZoneInfo("UTC")) - timedelta(days=500)

        is_kr = symbol.isdigit()
        kst_tz = ZoneInfo("Asia/Seoul")
        ny_tz = ZoneInfo("America/New_York")
        now_local = datetime.now(kst_tz) if is_kr else datetime.now(ny_tz)

        df = pd.DataFrame()
        auto_p, v_curr = 0.0, 0.0
        us_prev_p = None
        start_dt_str = start_date.strftime("%
