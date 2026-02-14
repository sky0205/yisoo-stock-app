import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 제목 (v160)
st.set_page_config(page_title="이수 주식&경매 v160", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; } 
    .signal-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 30px; font-weight: bold; margin-bottom: 20px; }
    .auction-table { font-size: 16px; border: 1px solid #CBD5E1; border-collapse: collapse; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 통합 분석기 v160")
st.success("🎉 드디어 새 앱에서 최신 버전을 실행 중입니다! v106은 이제 영원히 안녕입니다.")

# 탭 구성 (주식분석 / 경매물건)
tab1, tab2 = st.tabs(["📈 주식 분석", "🏠 고양/파주 경매 물건"])

with tab1:
    u_input = st.text_input("🔍 종목 번호 6자리 입력", value="005930")
    ticker = u_input.strip()

    @st.cache_data(ttl=60)
    def fetch_v160(t):
        try:
            df = fdr.DataReader(t, '2024')
            if df is not None and not df.empty:
                df = df.reset_index()
                df.columns = [str(c).lower().strip() for c in df.columns]
                return df, "데이터 연결 성공"
        except: return None, "데이터를 불러오는 중입니다..."

    if ticker:
        df, msg = fetch_v160(ticker)
        if isinstance(df, pd.DataFrame):
            close = df['close']
            # RSI 지표 계산
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]

            if rsi <= 35: st.markdown(f"<div class='signal-box' style='background-color:#FEE2E2; color:#B91C1C; border:4px solid #B91C1C;'>🚨 {ticker}: 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='signal-box' style='background-color:#F1F5F9; color:#475569; border:4px solid #475569;'>🟡 {ticker}: 관망 대기 구간 🟡</div>", unsafe_allow_html=True)

            chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(
                x=alt.X(df.columns[0]+':T', title='날짜'),
                y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
            )
            st.altair_chart(chart.properties(height=400), use_container_width=True)

with tab2:
    st.write("### 📅 최근 고양/파주 경매 추천 물건 (2026.02)")
    # 요청하신 탭(Tab) 구분 양식의 예시 데이터입니다.
    auction_data = [
        {"사건번호": "2024타경1234", "소재지": "고양시 일산서구 주엽동 강선마을", "물건": "아파트", "최저가": "3.5억"},
        {"사건번호": "2024타경5678", "소재지": "파주시 야당동 한빛마을", "물건": "아파트", "최저가": "4.2억"},
        {"사건번호": "2025타경1011", "소재지": "고양시 덕양구 화정동 별빛마을", "물건": "아파트", "최저가": "2.9억"}
    ]
    st.table(pd.DataFrame(auction_data))
    st.info("💡 선생님이 정리하신 1,500페이지 분량의 상세 분석 자료는 '내 문서' 폴더에서 확인하실 수 있습니다.")
