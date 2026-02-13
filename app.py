import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 화면 설정
st.set_page_config(page_title="이수 투자비책 v9", layout="wide")

# [메모리 설정] 검색 기록과 종목명-코드 매핑 정보를 저장합니다.
if 'history' not in st.session_state:
    st.session_state.history = ["삼성전자", "아이온큐", "엔비디아", "유한양행"]
if 'name_map' not in st.session_state:
    # 기본 매핑 정보 (선생님이 자주 보시는 것들)
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX", "에스피지": "058610.KQ"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F0F2F6; padding: 15px; border-radius: 10px; border: 1px solid #D1D5DB; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 45px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    </style>
    """, unsafe_allow_html=True)

# 한글 종목명 가져오기 함수 (한국 주식용)
def get_kr_name(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        name = soup.select_one(".wrap_company h2 a").text
        return name
    except: return None

# 데이터 가져오기 함수
@st.cache_data(ttl=60)
def get_analysis_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if data.empty: return None
        data.columns = [c.lower() for c in data.columns]
        return data
    except: return None

st.title("📈 이수 할아버지의 '기억하는' 투자 분석기")

# [검색부] 자동완성 및 직접 입력
st.subheader("🔍 종목명, 번호(6자리), 또는 영어 티커를 입력하세요")
user_input = st.selectbox(
    "검색창 (한 번 검색하면 이름으로 저장됩니다):",
    options=st.session_state.history,
    index=None,
    placeholder="예: 005930, NVDA, 아이온큐...",
    key="search_box"
)

# 직접 입력을 위한 보조 칸 (리스트에 없을 때 사용)
direct_input = st.text_input("새로운 종목 직접 입력 (위 목록에 없을 때만):", value="")
final_input = direct_input if direct_input else user_input

if final_input:
    # 1. 티커 변환 로직
    # A. 이미 아는 이름인 경우
    if final_input in st.session_state.name_map:
        ticker = st.session_state.name_map[final_input]
        display_name = final_input
    # B. 숫자 6자리인 경우 (국장)
    elif final_input.isdigit() and len(final_input) == 6:
        # 코스피인지 코스닥인지 확인하기 위해 이름 찾기 시도
        found_name = get_kr_name(final_input)
        if found_name:
            # 우선 코스피(.KS)로 시도해보고 안되면 코스닥(.KQ)으로 (간단화)
            ticker = final_input + ".KS"
            display_name = found_name
        else:
            ticker = final_input + ".KS" # 기본값
            display_name = final_input
    # C. 그 외 (미장 티커)
    else:
        ticker = final_input.upper()
        display_name = final_input.upper()

    # 2. 데이터 분석 실행
    df = get_analysis_data(ticker)
    
    # 한국 주식인데 .KS로 안 나올 경우 .KQ로 재시도
    if df is None and ".KS" in ticker:
        ticker = ticker.replace(".KS", ".KQ")
        df = get_analysis_data(ticker)

    if df is not None:
        # 3. 새로운 종목 정보 저장 (이름 기억하기)
        # 미장의 경우 한글 이름을 찾기 어려우므로 티커 그대로 저장하거나 
        # 선생님이 자주 보시는 미장은 제가 수동으로 매핑해두었습니다.
        if display_name not in st.session_state.history:
            st.session_state.history.insert(0, display_name)
        if display_name not in st.session_state.name_map:
            st.session_state.name_map[display_name] = ticker

        # [지표 계산 및 화면 출력 - 기존 로직과 동일]
        close = df['close']; high = df['high']; low = df['low']
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()) * -100
        ema12 = close.ewm(span=12, adjust=False).mean(); ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26; sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); lower = ma20 - (std20 * 2)

        curr_p = close.iloc[-1]; curr_rsi = rsi.iloc[-1]; curr_wr = w_r.iloc[-1]; macd_up = macd.iloc[-1] > macd.iloc[-2]

        st.markdown(f"<p class='big-font'>{display_name} ({ticker}): {curr_p:,.2f}</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("RSI (상대강도)", f"{curr_rsi:.1f}")
        c2.metric("윌리엄 %R", f"{curr_wr:.1f}")
        c3.metric("MACD 에너지", "상승세" if macd_up else "하락세")

        st.write("---")
        is_cheap = curr_rsi <= 35 or curr_wr <= -80
        if is_cheap:
            if macd_up: st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출!) 🚨</div>", unsafe_allow_html=True)
            else: st.markdown("<div style='background-color:#FFF4E5; color:#FFA000; border-color:#FFA000;' class='status-box'>✋ 싸지만 대기 (하락 중)</div>", unsafe_allow_html=True)
        elif curr_rsi >= 70 or curr_wr >= -20:
            st.markdown("<div style='background-color:#EEFFEE; color:#2E7D32; border-color:#2E7D32;' class='status-box'>💰 익절 권장 (과열 구간) 💰</div>", unsafe_allow_html=True)
        else: st.markdown("<div style='background-color:#F0F2F6; color:#31333F; border-color:#D1D5DB;' class='status-box'>🟡 관망 (보통 상태) 🟡</div>", unsafe_allow_html=True)

        st.line_chart(pd.DataFrame({'주가': close, '밴드하단': lower}).tail(80))
        st.line_chart(pd.DataFrame({'MACD': macd, '시그널': sig}).tail(80))
    else:
        st.error(f"'{final_input}' 데이터를 가져올 수 없습니다.")

# 사이드바 관리
if st.sidebar.button("검색 기록 초기화"):
    st.session_state.history = ["삼성전자", "아이온큐", "엔비디아"]
    st.rerun()
