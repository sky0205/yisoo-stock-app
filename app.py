import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import altair as alt

# 1. 고대비 스타일
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; color: black; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p { color: #1E3A8A !important; font-weight: bold; }
    .trend-text { font-size: 20px; line-height: 1.6; color: #1E293B !important; padding: 20px; background: #F1F5F9; border-left: 8px solid #1E3A8A; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 통합 분석기 v850")

# 2. 종목코드 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    try:
        # 데이터 가져오기 (시작 날짜 지정으로 안정성 강화)
        df = fdr.DataReader(symbol, '2025-01-01')
        
        if df is not None and not df.empty:
            df = df.tail(100).reset_index()
            # 모든 컬럼명을 소문자로 통일
            df.columns = [str(c).lower() for c in df.columns]
            
            # 날짜 컬럼 강제 지정
            if 'date' not in df.columns:
                df.rename(columns={df.columns[0]: 'date'}, inplace=True)
            
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"

            # 3. 지표 계산
            ma20 = close.rolling(20).mean()
            std20 = close.rolling(20).std()
            df['upper'] = ma20 + (std20 * 2)
            df['lower'] = ma20 - (std20 * 2)
            
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            
            exp12 = close.ewm(span=12, adjust=False).mean(); exp26 = close.ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()

            # 4. 신호등 출력
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"📢 {symbol} 분석 (현재가: {price_txt})")
            
            if rsi < 35 or curr_p <= df['lower'].iloc[-1]:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
            elif rsi > 65 or curr_p >= df['upper'].iloc[-1]:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

            # 5. 볼린저 밴드 그래프 (여백 최적화)
            base = alt.Chart(df).encode(x=alt.X('date:T', title='날짜'))
            band = base.mark_area(opacity=0.2, color='#94A3B8').encode(
                y=alt.Y('lower:Q', scale=alt.Scale(zero=False)),
                y2='upper:Q'
            )
            line = base.mark_line(color='#1E40AF', size=3).encode(y='close:Q')
            st.altair_chart(band + line, use_container_width=True)

            # 6. 추세 정밀 진단
            st.write("### 📉 추세 정밀 진단")
            trend_msg = "📈 **상승 추세:** 매수 세력이 강해지고 있습니다." if macd.iloc[-1] > signal.iloc[-1] else "📉 **하락 추세:** 매도 압력이 있으니 저점을 확인하세요."
            st.markdown(f"<div class='trend-text'><b>단기 방향:</b> {trend_msg}<br><b>종합 판단:</b> RSI {rsi:.1f} 기준으로 현재는 {'과열' if rsi > 70 else '침체' if rsi < 30 else '안정'} 상태입니다.</div>", unsafe_allow_html=True)
    except:
        st.error("⚠️ 데이터를 불러오지 못했습니다. 종목코드나 requirements.txt를 확인해 주세요.")
