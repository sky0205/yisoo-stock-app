import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도·볼린저 진단기")

# 1. 검색 기록 저장을 위한 바구니
if 'history' not in st.session_state:
    st.session_state['history'] = []

stock_dict = {
    "삼성전자": "005930.KS",
    "실리콘투": "247020.KQ",
    "아이온큐": "IONQ",
    "넷플릭스": "NFLX",
    "엔비디아": "NVDA"
}

st.info("💡 종목명(삼성전자, 실리콘투) 혹은 코드(IONQ)를 입력하세요.")

# 2. 종목 입력 및 코드 변환
user_input = st.text_input("종목을 검색하세요", value="실리콘투").strip()
ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    try:
        # 3. 데이터 불러오기 (볼린저 밴드를 위해 기간을 1년으로 넉넉히 가져옵니다)
        data = yf.download(ticker, period="1y", multi_level_index=False)
        
        if data.empty:
            st.error(f"❌ '{user_input}' 데이터를 찾을 수 없습니다.")
        else:
            # 검색 성공 시 기록 저장
            if user_input not in st.session_state['history']:
                st.session_state['history'].insert(0, user_input)
            
            df = data.copy()
            df.columns = [str(col).lower() for col in df.columns]
            close = df['close']
            
            # --- [지표 계산 시작] ---
            # (1) RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))

            # (2) Williams %R
            willr = -100 * (df['high'].rolling(14).max() - close) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())

            # (3) 볼린저 밴드 (20일 이동평균선 기준)
            sma20 = close.rolling(window=20).mean()
            std20 = close.rolling(window=20).std()
            upper_bb = sma20 + (std20 * 2)
            lower_bb = sma20 - (std20 * 2)
            # ------------------------

            # 화폐 단위 설정
            is_korea = ticker.endswith(".KS") or ticker.endswith(".KQ")
            unit = "원" if is_korea else "달러($)"
            price_format = "{:,.0f}" if is_korea else "{:,.2f}"

            # 결과 출력
            curr_p = close.iloc[-1]
            st.subheader(f"🔍 {user_input} ({ticker}) 분석 결과")
            st.metric(label="현재가", value=f"{price_format.format(curr_p)} {unit}")
            
            # 신호 분석 (RSI, Williams %R, 볼린저 밴드 종합)
            c_rsi, c_will, c_upper, c_lower = rsi.iloc[-1], willr.iloc[-1], upper_bb.iloc[-1], lower_bb.iloc[-1]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"📊 **보조지표 상태**")
                st.write(f"- RSI: {c_rsi:.2f}")
                st.write(f"- Williams %R: {c_will:.2f}")
            with col2:
                st.write(f"🏠 **볼린저 밴드 위치**")
                st.write(f"- 상단선: {price_format.format(c_upper)} {unit}")
                st.write(f"- 하단선: {price_format.format(c_lower)} {unit}")

            # 종합 신호 판단
            if curr_p <= c_lower and c_rsi <= 30:
                st.error("🚨 [강력 매수] 주가가 볼린저 하단선에 닿았고 RSI도 바닥입니다!")
            elif curr_p >= c_upper and c_rsi >= 70:
                st.success("💰 [매도 권장] 주가가 볼린저 상단선을 뚫었고 과열 상태입니다!")
            else:
                st.warning("🟡 [관망] 현재 밴드 내에서 안정적으로 움직이고 있습니다.")

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

# 4. 최근 검색 기록 버튼
if st.session_state['history']:
    st.write("---")
    st.write("🕒 **최근 검색한 종목 (다시 검색하려면 입력창에 써주세요)**")
    st.write(", ".join(st.session_state['history'][:5]))
