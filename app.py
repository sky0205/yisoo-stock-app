import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 및 대형 글자 스타일 설정
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 42px; font-weight: bold; color: black; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p, span { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 21px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F8FAFC; border-left: 12px solid #1E3A8A; border-radius: 12px; margin-top: 20px; }
    .history-item { padding: 10px; border-bottom: 1px solid #EEE; font-size: 18px; color: #475569; }
    </style>
    """, unsafe_allow_html=True)

# 2. 검색 기록 저장소
if 'history' not in st.session_state:
    st.session_state['history'] = []

st.title("👨‍💻 이수할아버지의 추세 분석기 v1500")

# 3. 종목코드 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol)
        if df is not None and not df.empty:
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            # 종목명 찾기
            stock_name = symbol
            try:
                krx = fdr.StockListing('KRX')
                name_row = krx[krx['Code'] == symbol]
                if not name_row.empty: stock_name = name_row.iloc[0]['Name']
            except: pass

            df = df.tail(120)
            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 지표 계산: RSI, Williams %R, MACD
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
            
            exp12 = close.ewm(span=12, adjust=False).mean(); exp26 = close.ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()

            # 4. 상단 출력
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"🏢 {stock_name} ({symbol})")
            st.write(f"## 현재가: {price_txt}")

            # 5. 신호등
            if rsi < 35 or wr < -80:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 (바닥)</div>", unsafe_allow_html=True)
            elif rsi > 65 or wr > -20:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 (고점)</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기 (중립)</div>", unsafe_allow_html=True)

            # 6. 지수 테이블
            st.write("### 📋 4대 전문 지표 정밀 진단")
            st.table(pd.DataFrame({
                "지표 항목": ["현재가", "RSI 강도", "Williams %R", "MACD 추세"],
                "분석 수치": [price_txt, f"{rsi:.1f}", f"{wr:.1f}", "상승" if macd.iloc[-1] > signal.iloc[-1] else "하락"],
                "기술적 판단": ["-", "저점" if rsi < 30 else "고점" if rsi > 70 else "중립", "매수권" if wr < -80 else "보통", "안정" if macd.iloc[-1] > signal.iloc[-1] else "주의"]
            }))

            # 7. 추세 정밀 진단 (요청하신 기능)
            st.write("### 📉 종합 추세 및 전략 분석")
            macd_status = "📈 **골든크로스 발생:** 단기 상승 에너지가 강해지는 추세입니다." if macd.iloc[-1] > signal.iloc[-1] else "📉 **데드크로스 발생:** 매도 압력이 우세하여 하락 추세가 지속되고 있습니다."
            rsi_status = "매수세가 유입되는 바닥권" if rsi < 40 else "안정적인 흐름" if rsi < 60 else "과열이 우려되는 고점권"
            
            st.markdown(f"""
            <div class='trend-card'>
                <b>1. 추세 방향:</b> {macd_status}<br>
                <b>2. 현재 강도:</b> RSI {rsi:.1f}로 현재 시장은 {rsi_status}입니다.<br>
                <b>3. 매매 시점:</b> Williams %R {wr:.1f} 기준으로 {"지금이 분할 매수 적기입니다." if wr < -80 else "추격 매수보다는 눌림목을 기다려야 합니다."}
            </div>
            """, unsafe_allow_html=True)
    except:
        st.error("데이터를 가져오는 중 오류가 발생했습니다.")

# 8. 검색 기록
st.write("---")
st.subheader("📜 오늘 검색한 종목 리스트")
for item in st.session_state['history'][:10]:
    st.markdown(f"<div class='history-item'>✅ {item}</div>", unsafe_allow_html=True)
