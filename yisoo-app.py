import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 및 스타일 ---
st.set_page_config(page_title="v36000 마스터", layout="wide")

# 종목 DB (여기에 추가하면 자동으로 불러옵니다)
stock_db = {
    "005930": {"name": "삼성전자", "market": "국장 (KR)", "target": 210000.0},
    "000100": {"name": "유한양행", "market": "국장 (KR)", "target": 135000.0},
    "NVDA": {"name": "엔비디아", "market": "미장 (US)", "target": 195.00},
    "IONQ": {"name": "아이온큐", "market": "미장 (US)", "target": 39.23},
    "AAPL": {"name": "애플", "market": "미장 (US)", "target": 250.00},
    "000660": {"name": "SK하이닉스", "market": "국장 (KR)", "target": 250000.0}
}

# 세션 상태 초기화
if 'ticker' not in st.session_state: st.session_state['ticker'] = "005930"

st.markdown("""
    <style>
    .big-price { font-size: 45px !important; font-weight: 800; color: #E74C3C; margin-bottom: 10px; }
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; color: white !important; line-height: 1.2; margin-bottom: 20px; }
    .signal-content { font-size: 48px; font-weight: 900; display: block; margin-top: 5px; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 30px; font-weight: 700; margin-bottom: 25px; }
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; margin-bottom: 30px; color: #1E1E1E !important; }
    .stButton>button { width: 100%; height: 65px; font-size: 24px; font-weight: 800; background-color: #1E1E1E; color: white; border-radius: 12px; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 데이터 엔진 ---
def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        p = soup.select_one(".no_today .blind").text.replace(",", "")
        return int(p)
    except: return None

@st.cache_data(ttl=60)
def get_tech_analysis(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty: return None
        close = df['Close']
        ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
        delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g/l)))
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        wr = (h14 - close) / (h14 - l14) * -100
        e12 = close.ewm(span=12).mean(); e26 = close.ewm(span=26).mean(); macd = (e12 - e26) - (e12 - e26).ewm(span=9).mean()
        return {"p": float(close.iloc[-1]), "up": float(ma20.iloc[-1]+std.iloc[-1]*2), "dn": float(ma20.iloc[-1]-std.iloc[-1]*2), 
                "rsi": float(rsi.iloc[-1]), "wr": float(wr.iloc[-1]), "macd": float(macd.iloc[-1])}
    except: return None

# --- [2] 메인 설정창 (한 번에 보기 & 자동 연동) ---
st.title("🏆 이수할아버지 v36000 마스터")

# 1. 코드 입력 (이게 기준이 됩니다)
t_code = st.text_input("🔢 종목 코드(6자리) 또는 미장 티커를 입력하세요", value=st.session_state['ticker'])

# DB에서 정보 매칭
info = stock_db.get(t_code, {"name": "새 종목", "market": "국장 (KR)", "target": 0.0})

# 2. 한 줄 설정 (자동으로 값이 채워짐)
c1, c2, c3 = st.columns([2, 1.5, 2.5])
with c1: in_name = st.text_input("📍 종목명", value=info["name"])
with c2: in_market = st.selectbox("🌎 시장", ["국장 (KR)", "미장 (US)"], index=0 if info["market"]=="국장 (KR)" else 1)
with c3: in_target = st.number_input("💎 적정주가", value=float(info["target"]), step=0.1)

# 분석 버튼
if st.button("🚀 실시간 정밀 분석 시작"):
    st.session_state['analyzed'] = True
    st.session_state['ticker'] = t_code # 현재 입력값 저장
    
    # 데이터 호출
    y_ticker = t_code + (".KS" if "KR" in in_market else "")
    tech = get_tech_analysis(y_ticker)
    price = get_naver_price(t_code) if "KR" in in_market else (tech["p"] if tech else None)

    if price and tech:
        st.markdown("---")
        # 현재가 표시부 (사라졌던 현주가 복구!)
        cur = "원" if "KR" in in_market else "$"
        f_p = f"{format(int(price), ',')} {cur}" if "KR" in in_market else f"{cur}{price:,.2f}"
        f_tg = f"{format(int(in_target), ',')} {cur}" if "KR" in in_market else f"{cur}{in_target:,.2f}"
        
        st.markdown(f"<p class='big-price'>🔍 {in_name} ({t_code}) 현재가: {f_p}</p>", unsafe_allow_html=True)

        # 신호등
        if tech['rsi'] > 70 or price > tech['up']:
            bg, status = "#28A745", "🟢 매도 검토 (과열)"
        elif price < in_target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립)"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 설정된 적정주가: {f_tg}</div>", unsafe_allow_html=True)

        # 요약 및 지표
        st.markdown("### 📝 이수할아버지 추세 분석")
        sum_msg = "에너지가 위로 분출되어 밴드 상단을 뚫고 있습니다." if price > tech['up'] else "바닥을 확인하며 에너지를 모으는 중입니다."
        st.markdown(f"<div class='summary-box'><b>진단결과:</b> 현재 {in_name}은(는) {sum_msg}<br>RSI {round(tech['rsi'],1)}는 {'과열 상태입니다. 욕심을 줄이세요.' if tech['rsi']>70 else '바닥 구간입니다. 용기를 내보세요.' if tech['rsi']<35 else '안정적인 흐름입니다.'}</div>", unsafe_allow_html=True)

        # 상세 진단표 (실시간 비교)
        b_diag = "⚠️ 상단 돌파 (과열)" if price > tech['up'] else "✅ 하단 지입 (바닥)" if price < tech['dn'] else "밴드 내 안정적 주행"
        f_up = f"{tech['up']:,.2f}" if "US" in in_market else f"{round(tech['up'],0):,.0f}"
        f_dn = f"{tech['dn']:,.2f}" if "US" in in_market else f"{round(tech['dn'],0):,.0f}"

        st.table(pd.DataFrame({
            "핵심 지표": ["Bollinger Band", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{f_up} / {f_dn}", f"{round(tech['rsi'],1)}", f"{round(tech['wr'],1)}", f"{round(tech['macd'],3)}"],
            "상세 진단 (현지수 비교)": [b_diag, "과열" if tech['rsi']>70 else "바닥" if tech['rsi']<30 else "보통", "단기천장" if tech['wr']>-20 else "단기바닥" if tech['wr']<-80 else "보통", "상승세" if tech['macd']>0 else "하락세"]
        }))
    else:
        st.error(f"❌ '{t_code}' 데이터를 가져올 수 없습니다. 코드를 다시 확인해 주세요!")
