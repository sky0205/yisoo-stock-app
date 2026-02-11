import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도·그래프 진단기")

# 데이터를 기억해서 멈춤을 방지하는 기능
@st.cache_data(ttl=600)
def get_safe_data(ticker):
    try:
        df = yf.download(ticker, period="1y", multi_level_index=False)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).lower() for col in df.columns]
        return df
    except:
        return None

# 2. 검색 기록 및 종목 사전
if 'history' not in st.session_state: st.session_state['history'] = []
stock_dict = {
    "삼성전자": "005930.KS", "유한양행": "000100.KS", "실리콘투": "247020.KQ",
    "현대차": "005380.KS", "아이온큐": "IONQ", "넷플릭스": "NFLX"
}

st.info("💡 종목명(유한양행) 혹은 코드(000100.KS)를 입력하세요.")

# 3. 입력창
user_input = st.text_input("종목 검색", value="유한양행").strip()
ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    with st.spinner(f"'{user_input}' 분석 중..."):
        df = get_safe_data(ticker)
        
        if df is not None and 'close' in df.columns:
            # 검색 기록 저장
            if user_input not in st.session_state['history']:
                st.session_state['history'].insert(0, user_input)

            close = df['close']
            
            # --- 지표 계산 ---
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))

            # Williams %R
            willr = -100 * (df['high'].rolling(14).max() - close) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())

            # 볼린저 밴드
            sma20 = close.rolling(20).mean()
            std20 = close.rolling(20).std()
            upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)

            # --- 결과 출력 ---
            is_korea = ticker.endswith(".KS") or ticker.endswith(".KQ")
            unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
            curr_p = close.iloc[-1]
            
            st.subheader(f"🔍 {user_input} ({ticker}) 분석 결과")
            st.metric(label="현재가", value=f"{fmt.format(curr_p)} {unit}")
            
            # 4. 종합 판독
            c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
            c_up, c_low = upper_bb.iloc[-1], lower_bb.iloc[-1]
            
            if curr_p <= c_low and c_rsi <= 35 and c_will <= -80:
                st.error("🚨 [강력 매수] 모든 지표가 바닥권입니다!")
            elif curr_p >= c_up and c_rsi >= 65 and c_will >= -20:
                st.success("💰 [매도 권장] 모든 지표가 고점권입니다!")
            else:
                st.warning("🟡 [관망] 현재는 신호 대기 중입니다.")

            # 5. [추가] 주가 및 볼린저 밴드 그래프
            st.write("---")
            st.subheader("📈 주가 흐름 및 볼린저 밴드 (최근 100일)")
            
            # 그래프용 데이터 정리
            chart_data = pd.DataFrame({
                '현재가': close,
                '상단선': upper_bb,
                '하단선': lower_bb,
                '중심선(20일)': sma20
            }).tail(100) # 최근 100일치만 보여줌
            
            st.line_chart(chart_data) # 스트림릿 전용 선 그래프
            
            # 지표 수치 요약
            col1, col2, col3 = st.columns(3)
            col1.write(f"📊 RSI: {c_rsi:.1f}")
            col2.write(f"📊 윌리엄: {c_will:.1f}")
            col3.write(f"🏠 밴드 하단: {fmt.format(c_low)}{unit}")

# 6. 최근 검색 기록
if st.session_state['history']:
    st.write("---")
    st.write("🕒 최근 검색: " + ", ".join(st.session_state['history'][:5]))
