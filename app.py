import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 앱 제목 및 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")
st.title("📈 나만의 매수·매도 타이밍 진단기")

# 2. 종목 입력 (기본: 삼성전자)
ticker = st.text_input("종목 코드를 입력하세요 (예: 005930.KS)", value="005930.KS").strip()

if ticker:
    try:
        # 3. 데이터 가져오기 (멀티인덱스 방지 설정 추가)
        df = yf.download(ticker, period="1y")
        
        if df.empty:
            st.warning("데이터를 불러오지 못했습니다. 종목 코드를 확인해 주세요.")
        else:
            # [핵심] 최근 yfinance 버전의 이름표 오류 강제 수정
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.columns = [str(col).lower() for col in df.columns]
            
            # 4. 종가 데이터 선택 (이름이 'close' 혹은 'adj close'인 것 찾기)
            close = df['close'] if 'close' in df.columns else df.iloc[:, 3]
            
            # 5. 지표 직접 계산
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            
            # Williams %R
            high_14 = df['high'].rolling(14).max()
            low_14 = df['low'].rolling(14).min()
            willr = -100 * (high_14 - close) / (high_14 - low_14)

            # 6. 결과 화면 출력
            curr_p = close.iloc[-1]
            st.metric(label=f"{ticker} 현재가", value=f"{int(curr_p):,}원")
            
            c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
            
            if c_rsi <= 30 and c_will <= -80:
                st.error("🚨 [강력 매수] 바닥권 신호입니다! 적극 검토해 보세요.")
            elif c_rsi >= 70 and c_will >= -20:
                st.success("💰 [매도 권장] 과열권 신호입니다! 수익 실현을 고려해 보세요.")
            else:
                st.warning("🟡 [관망] 현재는 신호 대기 중입니다.")
            
            # 상세 수치 표
            st.write("---")
            st.table({
                "지표명": ["RSI (상대강도)", "Williams %R (윌리엄)"],
                "현재 수치": [f"{c_rsi:.2f}", f"{c_will:.2f}"],
                "판단": ["공포(매수기회)" if c_rsi < 30 else "과열(매도준비)" if c_rsi > 70 else "적정",
                        "바닥권" if c_will < -80 else "천장권" if c_will > -20 else "적정"]
            })
            
    except Exception as e:
        st.info("데이터를 동기화 중입니다. 잠시만 기다려 주세요.")

          
