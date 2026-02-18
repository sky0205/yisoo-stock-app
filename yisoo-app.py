import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 및 스타일 (시인성 및 에러 방지) ---
st.set_page_config(page_title="v36000 마스터", layout="wide")

# 종목 DB: 여기에 추가하면 코드 입력 시 자동 연동됩니다.
stock_db = {
    "005930": {"name": "삼성전자", "market": "국장 (KR)", "target": 210000.0},
    "000100": {"name": "유한양행", "market": "국장 (KR)", "target": 135000.0},
    "NVDA": {"name": "엔비디아", "market": "미장 (US)", "target": 195.00},
    "IONQ": {"name": "아이온큐", "market": "미장 (US)", "target": 39.23},
    "AAPL": {"name": "애플", "market": "미장 (US)", "target": 250.00},
    "000660": {"name": "SK하이닉스", "market": "국장 (KR)", "target": 250000.0}
}

st.markdown("""
    <style>
    .big-price { font-size: 45px !important; font-weight: 800; color: #E74C3C; margin-bottom: 5px; }
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; color: white !important; line-height: 1.2; margin-bottom: 20px; }
    .signal-content { font-size: 48px; font-weight: 900; display: block; margin-top: 5px; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 30px; font-weight: 700; margin-bottom: 25px; }
    /* 요약 박스: 글자색을 검정색(#000000)으로 강제 고정하여 시인성 확보 */
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; margin-bottom: 30px; border-radius: 0 15px 15px 0; color: #000000 !important; }
    .summary-box b { color: #000000 !important; font-weight: 800; }
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

# --- [2] 메인 설정창 (실시간 연동 로직) ---
st.title("🏆 이수할아버지 v36000 마스터")

# 코드 입력창 (여기에 005930이나 NVDA를 넣으시면 됩니다)
t_code = st.text_input("🔢 종목 코드(6자리) 또는 미장 티커를 입력하세요", value="005930")

# DB에서 정보 매칭 (없으면 기본값)
info = stock_db.get(t_code, {"name": "새 종목", "market": "국장 (KR)", "target": 0.0})

# 가로 배치 설정창 (코드 입력 시 실시간으로 바뀝니다)
c1, c2, c3 = st.columns([2, 1.5, 2.5])
with c1: in_name = st.text_input("📍 종목명", value=info["name"])
with c2: in_market = st.selectbox("🌎 시장", ["국장 (KR)", "미장 (US)"], index=0 if info["market"]=="국장 (KR)" else 1)
with c3: in_target = st.number_input("💎 적정주가", value=float(info["target"]), step=0.1)

# 분석 실행
if st.button("🚀 실시간 정밀 분석 시작"):
    st.markdown("---")
    y_ticker = t_code + (".KS" if "KR" in in_market else "")
    tech = get_tech_analysis(y_ticker)
    
    # 국장 데이터 보충 (코스닥 확인)
    if "KR" in in_market and not tech:
        tech = get_tech_analysis(t_code + ".KQ")
    
    price = get_naver_price(t_code) if "KR" in in_market else (tech["p"] if tech else None)

    if price and tech:
        cur = "원" if "KR" in in_market else "$"
        f_p = f"{format(int(price), ',')} {cur}" if "KR" in in_market else f"{cur}{price:,.2f}"
        f_tg = f"{format(int(in_target), ',')} {cur}" if "KR" in in_market else f"{cur}{in_target:,.2f}"
        
        # 1. 현재가 표시 (상단에 큼직하게)
        st.markdown(f"<p class='big-price'>🔍 {in_name} ({t_code}) 현재가: {f_p}</p>", unsafe_allow_html=True)

        # 2. 2단 지능형 신호등
        if tech['rsi'] > 70 or price > tech['up']:
            bg, status = "#28A745", "🟢 매도 검토 (과열 구간)"
        elif price < in_target * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회 구간)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립 구간)"
        
        # 신호등 HTML (따옴표 에러 방지를 위해 한 줄로 구성)
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 설정된 적정주가: {f_tg}</div>", unsafe_allow_html=True)

        # 3. 추세 분석 요약 (글자색 검정 고정)
        st.markdown("### 📝 추세 분석 요약")
        sum_msg = "에너지가 위로 분출되어 밴드 상단을 넘보고 있습니다." if price > tech['up'] else "바닥을 확인하며 지지력을 테스트 중입니다."
        st.markdown(f"<div class='summary-box'><b>이수할아버지 의견:</b> 현재 {in_name}은(는) {sum_msg}<br>RSI {round(tech['rsi'],1)}는 {'과열 상태입니다' if tech['rsi']>70 else '바닥 구간입니다' if tech['rsi']<35 else '안정권'}입니다.</div>", unsafe_allow_html=True)

        # 4. 상세 지표 분석표 (실시간 비교 진단)
        b_diag = "⚠️ 상단 돌파 (과열)" if price > tech['up'] else "✅ 하단 지입 (바닥)" if price < tech['dn'] else "밴드 내 안정적 주행"
        f_up = f"{tech['up']:,.2f}" if "US" in in_market else f"{round(tech['up'],0):,.0f}"
        f_dn = f"{tech['dn']:,.2f}" if "US" in in_market else f"{round(tech['dn'],0):,.0f}"

        idx_df = pd.DataFrame({
            "핵심 지표": ["Bollinger Band", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{f_up} / {f_dn}", f"{round(tech['rsi'],1)}", f"{round(tech['wr'],1)}", f"{round(tech['macd'],3)}"],
            "현 주가 대비 상세 진단": [b_diag, "과열(70↑)" if tech['rsi']>70 else "바닥(30↓)" if tech['rsi']<30 else "보통", "단기천장" if tech['wr']>-20 else "단기바닥" if tech['wr']<-80 else "보통", "전진 가속" if tech['macd']>0 else "하락 압력"]
        })
        st.table(idx_df)
    else:
        st.error(f"❌ '{t_code}' 데이터를 가져올 수 없습니다. 코드와 시장(KR/US)을 확인해 주세요!")
