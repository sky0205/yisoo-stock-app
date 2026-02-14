import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기 v75", layout="wide")

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "유한양행": "000100.KS",
        "엔비디아": "NVDA", "아이온큐": "IONQ", "쿠팡": "CPNG", "넷플릭스": "NFLX"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F0F2F6; padding: 20px; border-radius: 12px; border: 1px solid #D1D5DB; }
    .big-font { font-size:38px !important; font-weight: bold; color: #111827; margin-bottom: 20px; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; margin: 20px 0; border: 4px solid; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 가져오기 (가장 강력한 수리 로직 포함)
@st.cache_data(ttl=60)
def get_grand_data_v75(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is None or df.empty: return None
        
        # 이름표 정리
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        df.columns = [str(c).lower().replace(" ", "").strip() for c in df.columns]
        
        # 날짜 정렬 및 인덱스 초기화
        df = df.reset_index()
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 1]
            
        return df.sort_values('Date').ffill().dropna()
    except:
        return None

# UI 시작
st.title("👨‍💻 이수할아버지의 주식분석기 v75 (v20 복원판)")
st.write("---")

sel_name = st.selectbox("📋 종목을 선택하세요", options=list(st.session_state.name_map.keys()), index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_grand_data_v75(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_grand_data_v75(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        # 지표 계산
        close = df['close']
        high = df.get('high', close); low = df.get('low', close)
        
        # 1. RSI
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        # 2. Williams %R
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        
        # 3. MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        
        # 4. Bollinger Bands
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_bb = ma20 + (std20 * 2)
        lower_bb = ma20 - (std20 * 2)
        
        curr_p = close.iloc[-1]; y_high = close.max()

        # 보고서 상단 지표
        st.markdown(f"<p class='big-font'>{sel_name} 프리미엄 분석 보고서</p>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        m4.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 신호등 박스
        st.write("---")
        if rsi_val.iloc[-1] <= 35 or w_r.iloc[-1] <= -80:
            st.markdown("<div style='background-color:#FFEEEE; color:#CC0000; border-color:#CC0000;' class='signal-box'>🚨 강력 매수 (바닥 탈출 신호) 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='signal-box'>📈 신고가 돌파 (추세 상승 중) 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F9FAFB; color:#4B5563; border-color:#D1D5DB;' class='signal-box'>🟡 관망 및 대기 (추세 주시) 🟡</div>", unsafe_allow_html=True)

        # 그래프 섹션 1: 주가 및 볼린저 밴드
        st.write("### 📊 주가 추세 및 볼린저 밴드 (회색: 주가 통로)")
        chart_df = df[['Date', 'close']].tail(120).copy()
        chart_df['Upper'] = upper_bb.tail(120)
        chart_df['Lower'] = lower_bb.tail(120)
        chart_df['MA20'] = ma20.tail(120)
        
        base = alt.Chart(chart_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        band = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#111827', strokeWidth=3).encode(y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF4444', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((band + line + ma_line).properties(height=450), use_container_width=True)

        # 그래프 섹션 2: MACD
        st.write("### 📉 MACD 추세선 (파란선이 주황선 위에 있어야 상승세)")
        macd_df = pd.DataFrame({
            'Date': chart_df['Date'],
            'MACD': macd_line.tail(120),
            'Signal': signal_line.tail(120)
        })
        m_base = alt.Chart(macd_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        m_line = m_base.mark_line(color='#2563EB', strokeWidth=2).encode(y='MACD:Q')
        s_line = m_base.mark_line(color='#F59E0B', strokeWidth=2).encode(y='Signal:Q')
        st.altair_chart((m_line + s_line).properties(height=250), use_container_width=True)
        
    else:
        st.error("데이터를 불러오는 중입니다. 잠시만 기다려 주세요.")

if st.sidebar.button("🗑️ 초기화"):
    st.session_state.clear()
    st.rerun()
