import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import altair as alt

# 1. 고대비 & 대형 글자 스타일
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; color: black; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p { color: #1E3A8A !important; }
    .trend-text { font-size: 22px; line-height: 1.6; color: #333333 !important; padding: 15px; background: #F8FAFC; border-left: 5px solid #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 글로벌 매매 분석기")

# 2. 종목 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", "NVDA").strip().upper()

if symbol:
    df = fdr.DataReader(symbol)
    if not df.empty:
        df = df.tail(120)
        close = df['Close']
        
        # 단위 설정 (숫자면 원, 영문이면 $)
        unit = "원" if symbol.isdigit() or symbol.endswith('.KS') or symbol.endswith('.KQ') else "$"
        
        # 3. 지표 계산 (Bollinger, RSI, MACD)
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        df['Upper'] = ma20 + (std20 * 2); df['Lower'] = ma20 - (std20 * 2)
        
        diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
        
        exp12 = close.ewm(span=12, adjust=False).mean(); exp26 = close.ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()
        
        # 4. [신호등 출력]
        st.write("---")
        curr_p = close.iloc[-1]
        price_display = f"{curr_p:,.0f}{unit}" if unit == "원" else f"{unit}{curr_p:,.2f}"
        st.subheader(f"📢 {symbol} 분석 결과 (현재가: {price_display})")
        
        if rsi < 35 or curr_p <= df['Lower'].iloc[-1]:
            st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
        elif rsi > 65 or curr_p >= df['Upper'].iloc[-1]:
            st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

        # 5. [볼린저 밴드 그래프]
        df_p = df.reset_index()
        base = alt.Chart(df_p).encode(x='Date:T')
        band = base.mark_area(opacity=0.15, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#1E40AF', size=3).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
        st.altair_chart(band + line, use_container_width=True)

        # 6. [추세 분석 및 지표 표]
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 📋 핵심 지표")
            summary = pd.DataFrame({
                "항목": ["RSI", "MACD 추세", "밴드 위치"],
                "값": [f"{rsi:.1f}", "상승" if macd.iloc[-1] > signal.iloc[-1] else "하락", "하단" if curr_p < ma20.iloc[-1] else "상단"]
            })
            st.table(summary)
            
        with col2:
            st.write("### 📉 추세 정밀 진단")
            trend_msg = "상승 압력이 강해지는 중입니다." if macd.iloc[-1] > signal.iloc[-1] else "하락 추세가 지속되고 있습니다."
            vol_msg = "변동성이 커지고 있어 주의가 필요합니다." if (df['Upper'] - df['Lower']).iloc[-1] > (df['Upper'] - df['Lower']).mean() else "안정적인 흐름을 보입니다."
            st.markdown(f"<div class='trend-text'><b>단기 방향:</b> {trend_msg}<br><b>변동성:</b> {vol_msg}<br><b>판단:</b> 지표상 골든크로스가 발생할 때까지 대기하세요.</div>", unsafe_allow_html=True)
