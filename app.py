import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 및 초대형 글자 스타일
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 40px; border-radius: 20px; text-align: center; font-size: 45px; font-weight: bold; color: black; border: 12px solid; margin-bottom: 30px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 22px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F8FAFC; border-left: 10px solid #1E3A8A; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 통합 분석기 (v1100)")

# 2. 종목 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    try:
        # 데이터 가져오기
        df = fdr.DataReader(symbol)
        if df is not None and not df.empty:
            df = df.tail(30)
            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 3. 지수 계산
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100

            # 4. 출력: 현재가와 신호등
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"📢 {symbol} 분석 (현재가: {price_txt})")
            
            if rsi < 35 or wr < -80:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
            elif rsi > 65 or wr > -20:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

            # 5. 지수 테이블 (사라졌던 자료)
            st.write("### 📋 4대 전문 지표 진단")
            st.table(pd.DataFrame({
                "지표 항목": ["현재가", "RSI 강도", "Williams %R", "추세"],
                "분석 수치": [price_txt, f"{rsi:.1f}", f"{wr:.1f}", "상승" if rsi > 50 else "하락"],
                "판단": ["-", "저점" if rsi < 30 else "고점" if rsi > 70 else "중립", "매수권" if wr < -80 else "보통", "안정"]
            }))

            # 6. 추세 분석
            st.write("### 📉 종합 추세 분석")
            st.markdown(f"<div class='trend-card'>현재 {symbol}은(는) RSI {rsi:.1f} 수준으로 {'과열 상태입니다. 분할 익절을 고려하세요.' if rsi > 70 else '바닥을 다지는 중입니다. 추가 매수를 고려하세요.' if rsi < 30 else '안정적인 흐름을 유지하고 있습니다.'}</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ 데이터를 찾을 수 없습니다. 종목코드를 확인해 주세요.")
    except:
        st.info("🔄 데이터를 불러오는 중입니다. 잠시만 기다려 주시거나 종목코드를 다시 입력해 주세요.")
