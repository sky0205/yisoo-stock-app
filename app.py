import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import traceback

# 1. 화면 설정
st.set_page_config(page_title="Isu Stock Analyzer v65", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "유한양행": "000100.KS",
        "엔비디아": "NVDA", "아이온큐": "IONQ", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 가져오기 (가장 원시적이고 튼튼한 방식)
@st.cache_data(ttl=60)
def get_data_v65(ticker):
    try:
        # [수리] 최대한 단순하게 데이터를 요청합니다.
        data = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        
        if data is None or data.empty:
            return None
            
        # [핵심] 최근 야후 금융의 2층 이름표를 1층으로 합치는 강제 수술
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(-1)
            
        # 모든 이름표를 소문자로 통일
        data.columns = [str(c).lower().strip() for c in data.columns]
        
        # 날짜 순서 정렬
        return data.sort_index().ffill().dropna()
    except Exception as e:
        # 에러가 나면 화면에 어떤 에러인지 기록해둡니다.
        st.session_state['error_log'] = traceback.format_exc()
        return None

# 3. UI 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v65")
st.write("---")

h_list = list(st.session_state.name_map.keys())
sel_name = st.selectbox("📋 분석할 종목 선택", options=h_list, index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_data_v65(t_ticker)
    
    # 한국 주식 재시도 (.KS -> .KQ)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_data_v65(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        # 종가(Close) 찾기
        close = df['close'] if 'close' in df.columns else df.iloc[:, 0]
        high = df.get('high', close)
        low = df.get('low', close)
        
        # [지표 계산] RSI, 윌리엄 %R, MACD
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        # 윌리엄 %R: $$W\%R = \frac{High_{max} - Close}{High_{max} - Low_{min}} \times -100$$
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        
        # MACD
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        signal = macd.ewm(span=9, adjust=False).mean()
        
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        y_high = close.max(); curr_p = close.iloc[-1]

        # 4. 결과 출력
        st.markdown(f"<p class='big-font'>{sel_name} 분석 보고서</p>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 5. 신호등
        st.write("---")
        if rsi_val.iloc[-1] <= 35 or w_r.iloc[-1] <= -80:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B;' class='status-box'>🚨 강력 매수 구간 (바닥권) 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32;' class='status-box'>📈 추세 상승 중 (수익 극대화) 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 6. 그래프 섹션
        st.write("### 📊 주가 및 볼린저 밴드")
        c_df = pd.DataFrame({'Date': df.index, 'Close': close, 'Upper': upper, 'Lower': lower, 'MA20': ma20}).tail(100).reset_index()
        base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#1E1E1E', strokeWidth=2).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
        st.altair_chart((band + line).properties(height=400), use_container_width=True)
        
        st.write("### 📉 MACD 추세")
        m_df = pd.DataFrame({'Date': df.index, 'MACD': macd, 'Signal': signal}).tail(100).reset_index()
        m_base = alt.Chart(m_df).encode(x=alt.X('Date:T'))
        st.altair_chart((m_base.mark_line(color='blue').encode(y='MACD:Q') + m_base.mark_line(color='orange').encode(y='Signal:Q')).properties(height=150), use_container_width=True)

    else:
        st.error("⚠️ 데이터를 가져오지 못했습니다.")
        with st.expander("🛠️ 정밀 진단 보고서 (여기를 눌러 내용을 알려주세요)"):
            if 'error_log' in st.session_state:
                st.code(st.session_state['error_log'])
            else:
                st.write("연결 시도 중 에러가 발생하지 않았으나 데이터가 비어있습니다. 야후 서버 점검 중일 수 있습니다.")

if st.sidebar.button("🗑️ 리셋"):
    st.session_state.clear()
    st.rerun()
