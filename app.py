import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도·볼린저 진단기")

# 1. 검색 기록 바구니
if 'history' not in st.session_state:
    st.session_state['history'] = []

# 2. 똑똑한 사전 (유한양행 및 주요 종목 대거 추가)
stock_dict = {
    "삼성전자": "005930.KS",
    "유한양행": "000100.KS",
    "실리콘투": "247020.KQ",
    "카카오": "035720.KS",
    "NAVER": "035420.KS",
    "쿠팡": "CPNG",
    "아이온큐": "IONQ",
    "넷플릭스": "NFLX",
    "엔비디아": "NVDA",
    "테슬라": "TSLA"
}

st.info("💡 종목명(예: 유한양행)을 입력하거나, 사전에 없는 종목은 코드(예: 000660.KS)를 직접 입력하세요.")

# 3. 입력창 (빈칸 제거 및 대문자 변환 자동화)
user_input = st.text_input("종목을 입력하세요", value="유한양행").strip()
ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    with st.spinner(f"'{user_input}' 데이터를 분석 중입니다..."):
        try:
            # 4. 데이터 불러오기 (에러 방지를 위해 방식을 더 꼼꼼하게 수정)
            df = yf.download(ticker, period="1y", multi_level_index=False)
            
            if df is None or df.empty:
                st.error(f"❌ '{user_input}' 데이터를 찾을 수 없습니다. 한국 주식은 코드 뒤에 .KS(코스피)나 .KQ(코스닥)를 꼭 붙여주세요.")
            else:
                # 검색 기록 저장
                if user_input not in st.session_state['history']:
                    st.session_state['history'].insert(0, user_input)
                
                # 데이터 이름표 정리
                df.columns = [str(col).lower() for col in df.columns]
                close = df['close']
                
                # --- 지표 계산 ---
                # (1) RSI
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss)))

                # (2) Williams %R
                high_14 = df['high'].rolling(14).max()
                low_14 = df['low'].rolling(14).min()
                willr = -100 * (high_14 - close) / (high_14 - low_14)

                # (3) 볼린저 밴드
                sma20 = close.rolling(20).mean()
                std20 = close.rolling(20).std()
                upper_bb = sma20 + (std20 * 2)
                lower_bb = sma20 - (std20 * 2)

                # 화폐 설정
                is_korea = ticker.endswith(".KS") or ticker.endswith(".KQ")
                unit = "원" if is_korea else "달러($)"
                p_format = "{:,.0f}" if is_korea else "{:,.2f}"

                # 결과 출력
                curr_p = close.iloc[-1]
                st.subheader(f"🔍 {user_input} ({ticker}) 분석")
                st.metric(label="현재가", value=f"{p_format.format(curr_p)} {unit}")
                
                c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
                c_upper, c_lower = upper_bb.iloc[-1], lower_bb.iloc[-1]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"📊 **보조지표**")
                    st.write(f"- RSI: {c_rsi:.2f}")
                    st.write(f"- Williams %R: {c_will:.2f}")
                with col2:
                    st.write(f"🏠 **볼린저 밴드**")
                    st.write(f"- 상단: {p_format.format(c_upper)} {unit}")
                    st.write(f"- 하단: {p_format.format(c_lower)} {unit}")

                # 종합 신호
                if curr_p <= c_lower and c_rsi <= 35:
                    st.error("🚨 [강력 매수] 바닥권 신호입니다!")
                elif curr_p >= c_upper and c_rsi >= 65:
                    st.success("💰 [매도 권장] 과열권 신호입니다!")
                else:
                    st.warning("🟡 [관망] 현재는 신호 대기 중입니다.")

        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다. (코드 확인 필요)")

# 5. 검색 기록
if st.session_state['history']:
    st.write("---")
    st.write("🕒 **최근 검색 기록:** " + ", ".join(st.session_state['history'][:5]))
        
       
        
