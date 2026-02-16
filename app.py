import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import altair as alt

# 1. 고대비 & 화이트 테마 설정
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; color: black; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p, span { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 20px; line-height: 1.6; color: #1E293B !important; padding: 20px; background: #F1F5F9; border-left: 8px solid #1E3A8A; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 '불사조' 통합 분석기 v900")

# 2. 종목코드 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol, '2025-01-01')
        if df is not None and not df.empty:
            df = df.tail(100).reset_index()
            df.columns = [str(c).lower() for c in df.columns]
            if 'date' not in df.columns: df.rename(columns={df.columns[0]: 'date'}, inplace=True)
            
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"

            # 3. 기술적 지표 계산
            # Bollinger Bands: $MA_{20} \pm 2\sigma$
            ma20 = close.rolling(20).mean()
            std20 = close.rolling(20).std()
            df['upper'] = ma20 + (std20 * 2)
            df['lower'] = ma20 - (std20 * 2)
            
            # RSI: $RSI = 100 - \frac{100}{1 + RS}$
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            
            # Williams %R
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
            
            exp12 = close.ewm(span=12).mean(); exp26 = close.ewm(span=26).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9).mean()

            # 4. [신호등 출력]
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"📢 {symbol} 분석 (현재가: {price_txt})")
            
            if rsi < 35 or curr_p <= df['lower'].iloc[-1]:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
            elif rsi > 65 or curr_p >= df['upper'].iloc[-1]:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

            # 5. [지수 분석 테이블] - 다시 추가됨
            st.write("### 📋 4대 전문 지표 정밀 진단")
            summary = pd.DataFrame({
                "지표 항목": ["현재가", "RSI 강도", "Williams %R", "밴드 위치"],
                "분석 수치": [price_txt, f"{rsi:.1f}", f"{wr:.1f}", "하단 돌파" if curr_p < df['lower'].iloc[-1] else "상단 돌파" if curr_p > df['upper'].iloc[-1] else "밴드 내 횡보"],
                "판단": ["-", "저점" if rsi < 30 else "고점" if rsi > 70 else "중립", "매수권" if wr < -80 else "보통", "안정" if df['lower'].iloc[-1] < curr_p < df['upper'].iloc[-1] else "주의"]
            })
            st.table(summary)

            # 6. [볼린저 밴드 구름 그래프]
            st.write("### 📈 주가 및 볼린저 밴드 추세 (흰 바탕 구름형)")
            base = alt.Chart(df).encode(x=alt.X('date:T', title='날짜'))
            # 밴드 구름 (영역)
            band = base.mark_area(opacity=0.3, color='#94A3B8').encode(
                y=alt.Y('lower:Q', scale=alt.Scale(zero=False), title='가격'),
                y2='upper:Q'
            )
            # 현주가 라인
            line = base.mark_line(color='#1E40AF', size=4).encode(y='close:Q')
            st.altair_chart(band + line, use_container_width=True)

            # 7. [추세 정밀 진단]
            st.write("### 📉 추세 및 매매 전략")
            trend_msg = "📈 **상승 추세:** 매수세가 우세합니다." if macd.iloc[-1] > signal.iloc[-1] else "📉 **하락 추세:** 조정 가능성이 큽니다."
            st.markdown(f"<div class='trend-card'><b>단기 추세:</b> {trend_msg}<br><b>전략:</b> 볼린저 밴드 하단 구름에 닿을 때 분할 매수를 검토하세요.</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ 데이터를 불러오지 못했습니다. 종목코드를 다시 확인해 주세요.")
