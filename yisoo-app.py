import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# 1. 주식 분석기 연산 및 전략 생성 함수
# ---------------------------------------------------------
def run_stock_analysis(df, ticker_name="종목명", current_time_str="실시간"):
    """
    [이수 할배 주식분석기]
    - 기존 5일선, 20일선, 성벽, 볼린저밴드, RSI, Williams %R, MACD 연산 유지
    - [신규 반영] 52주 신고가(무주공산) / 52주 신저가(칼날 하락) 최우선 대응 전략
    """
    
    # ---------------------------------------------------------
    # 가. 기초 가격 및 수치 연산 (기존 틀 유지)
    # ---------------------------------------------------------
    p = df['Close'].iloc[-1]
    prev_p = df['Close'].iloc[-2]
    change_p = p - prev_p
    change_rate = (change_p / prev_p) * 100
    
    fmt_p = ",.0f" if p > 1000 else ",.2f"
    
    # 이동평균선
    ma5_val = df['Close'].rolling(window=5).mean().iloc[-1]
    ma20_val = df['Close'].rolling(window=20).mean().iloc[-1]
    ma60_val = df['Close'].rolling(window=60).mean().iloc[-1]
    ma120_val = df['Close'].rolling(window=120).mean().iloc[-1]
    
    # 성벽(20일 최고가 x 0.93) 및 볼린저밴드
    high20 = df['High'].rolling(window=20).max().iloc[-1]
    defense_line = high20 * 0.93
    
    std20 = df['Close'].rolling(window=20).std().iloc[-1]
    up_b = ma20_val + (2 * std20)
    low_b = ma20_val - (2 * std20)
    
    # ---------------------------------------------------------
    # [신규 추가] 52주(약 250일) 신고가 / 신저가 연산
    # ---------------------------------------------------------
    high_52w = df['High'].rolling(window=250, min_periods=1).max().iloc[-1]
    low_52w = df['Low'].rolling(window=250, min_periods=1).min().iloc[-1]
    
    is_new_high = p >= high_52w * 0.99  # 52주 신고가 영역 (돌파 또는 1% 이내 근접)
    is_new_low = p <= low_52w * 1.01   # 52주 신저가 영역 (갱신 또는 1% 이내 근접)
    
    # ---------------------------------------------------------
    # 나. 보조지표 연산 (RSI, Williams %R, MACD, 거래량)
    # ---------------------------------------------------------
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_val = (100 - (100 / (1 + rs))).iloc[-1]
    
    # Williams %R (14)
    high14 = df['High'].rolling(window=14).max().iloc[-1]
    low14 = df['Low'].rolling(window=14).min().iloc[-1]
    w_r = ((high14 - p) / (high14 - low14)) * -100
    
    # MACD (12, 26, 9)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    m_l = macd_line.iloc[-1]
    s_l = signal_line.iloc[-1]
    is_macd_turning = (m_l > s_l) and (macd_line.iloc[-2] <= signal_line.iloc[-2])
    
    # 거래량 보정강도
    vol_5m = df['Volume'].rolling(window=5).mean().iloc[-1]
    vol_curr = df['Volume'].iloc[-1]
    vol_strength = (vol_curr / vol_5m) * 100 if vol_5m > 0 else 100.0
    
    # 상태 플래그 및 점수
    is_ma5_safe = p >= ma5_val
    is_bearish = (ma5_val < ma20_val < ma60_val < ma120_val)
    is_reverse_shrinking = (p > prev_p) and (df['Volume'].iloc[-1] < df['Volume'].iloc[-2])
    
    top_score = 0
    if rsi_val >= 60: top_score += 1
    if w_r >= -20: top_score += 1
    if p >= up_b * 0.98: top_score += 1
    
    bottom_score = 0
    if rsi_val <= 35: bottom_score += 1
    if w_r <= -80: bottom_score += 1
    if p <= low_b * 1.02: bottom_score += 1

    # ---------------------------------------------------------
    # 다. 실전 필살 대응 전략 멘트 생성 (기존 틀 유지)
    # ---------------------------------------------------------
    # 1. 단기 생명선 사수
    if is_ma5_safe:
        strategy_1 = f"현재가({p:{fmt_p}})가 5일선({ma5_val:{fmt_p}}) 위에 안착하여 단기 전투선이 살아있네."
    else:
        strategy_1 = f"현재가({p:{fmt_p}})가 5일선({ma5_val:{fmt_p}}) 아래로 처박혀 단기 기세가 꺾였네! 경계하시게."

    # 2. 성벽 사수 확인
    if defense_line > up_b:
        strategy_2 = f"⚠️ <b>[고점 매물대 주의]</b> 성벽({defense_line:{fmt_p}})이 수확목표선({up_b:{fmt_p}})보다 위에 버티고 있소! 1차 수확선에서 짧게 익절하고 관망하는 것이 상책이오."
    elif p >= defense_line:
        if p >= prev_p and is_ma5_safe:
            strategy_2 = f"성벽({defense_line:{fmt_p}}) 위에서 5일선 기세를 타고 <b>위로 진격 중</b>이네! 든든한 방어선을 등지고 계속 밀어붙이시게."
        else:
            strategy_2 = f"성벽({defense_line:{fmt_p}}) 위에는 있으나 단기 기세가 <b>숨고르기 중</b>이네! 5일선 안착 여부를 관망하시게."
    else:
        if is_ma5_safe:
            strategy_2 = f"성벽({defense_line:{fmt_p}}) 아래에 있으나, 단기 5일선<b>(생명선)을 사수</b>하며 성벽 탈환을 위한 반격의 시동을 거는 중이네!"
        else:
            if p > prev_p and m_l >= s_l:
                strategy_2 = f"성벽({defense_line:{fmt_p}}) 아래(지하실)이나, 엔진 시동을 걸며 <b>지하실 탈출 시도 중</b>이네!"
            else:
                strategy_2 = f"성벽({defense_line:{fmt_p}}) 아래로 함락된 채 기세마저 밑으로 처박히고 있네! <b>절대 칼을 뽑지 마시게.</b>"

    # 3. 중장기 추세 진단
    if is_bearish:
        strategy_3 = f"🚨 [대세 역배열] 지하실 향하는 하락 추세 (5일선: {ma5_val:{fmt_p}} | 20일선: {ma20_val:{fmt_p}} | 60일선: {ma60_val:{fmt_p}} | 120일선: {ma120_val:{fmt_p}})"
    elif ma5_val > ma20_val and ma20_val > ma60_val:
        strategy_3 = f"🔥 [대세 정배열] 탄탄한 대풍년 추세 (5일선: {ma5_val:{fmt_p}} | 20일선: {ma20_val:{fmt_p}} | 60일선: {ma60_val:{fmt_p}})"
    else:
        strategy_3 = f"🌱 [단기 반등 초입] 상방 반전 시도 중 (5일선: {ma5_val:{fmt_p}} | 20일선: {ma20_val:{fmt_p}} | 60일선: {ma60_val:{fmt_p}})"

    # 4. 엔진(MACD) 확인
    if m_l > s_l:
        if p >= defense_line:
            strategy_4 = "엔진 정회전 완료! 성벽을 등지고 본대 진격 신호탄이 터졌네."
        else:
            strategy_4 = "엔진 정회전이나 성벽 아래(지하실)이므로 헛바퀴 주의! 성벽 회복 전까지 추격 금지."
    else:
        strategy_4 = "엔진 역회전 중! 동력이 꺼지고 있으니 진격을 멈추고 후퇴를 준비하시게."

    # ---------------------------------------------------------
    # 라. 최종 결론(final_adv) 로직 (신고가/신저가 반영)
    # ---------------------------------------------------------
    is_trend_buy = (p >= defense_line) and is_ma5_safe and (35 <= rsi_val < 58) and (top_score == 0)

    # [신규 추가] 52주 신고가 / 신저가 최우선 판정
    if is_new_high:
        final_adv = f"🚀 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[52주 신고가(무주공산)]</b> 영역 진격 중! 매물대는 없으나 과열 위험이 높으니 추격매수는 엄금하고, 5일선 사수 기준 트레일링 스탑(분할 익절)으로 대응하시게!"

    elif is_new_low:
        final_adv = f"🚨 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[52주 신저가(칼날 하락)]</b> 구역 전개! 바닥을 알 수 없는 지하실 진입이오. 단기 반등에 속지 말고 5일선 안착 및 쌍바닥 확인 전까지 무조건 관망하시게!"

    # 기존 결론 로직 연결
    elif top_score >= 2 or p >= up_b * 0.99 or rsi_val >= 60:
        if vol_strength >= 150 and p > defense_line:
            final_adv = f"🚀 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 화력 폭발하며 성벽 돌파 중! 목표선 근처 분할 익절 준비하시게."
        else:
            final_adv = f"💰 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 다중 과열권 및 수학기 진입! 욕심 버리고 야금야금 분할 익절 시작!"

    elif is_trend_buy:
        final_adv = f"🚀 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 성벽 탈환 후 눌림목 안착 완료! <b>[추세 진격 타점]</b>이시네, 본대 진격 준비하시게!"

    elif bottom_score >= 2 and is_ma5_safe and (is_reverse_shrinking or is_macd_turning or m_l >= s_l):
        final_adv = f"🎯 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 다중 바닥 및 5일선 안착 포착! <b>[바닥 선취매 타점]</b>이시네, 소량 진격하시게!"

    else:
        if not is_ma5_safe and bottom_score >= 2:
            final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 바닥 지표는 들어왔으나 5일선 이탈 중일세. 무조건 관망 및 대기!"
        elif m_l < s_l:
            if is_macd_turning:
                final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 중간 지대에서 엔진 회복 시도 중일세. 5일선 사수 여부 관망하시게!"
            else:
                final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 중간 지대이나 엔진 역회전 중일세. 무조건 관망 및 대기!"
        else:
            if p <= (low_b * 1.02):
                final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 엔진은 살았으나 볼린저 하단 근접 중일세. 바닥 안착 관망하시게!"
            else:
                final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 엔진 정회전이나 추세 탐색 중일세. 무조건 관망 및 대기!"

    return {
        "strategy_1": strategy_1,
        "strategy_2": strategy_2,
        "strategy_3": strategy_3,
        "strategy_4": strategy_4,
        "final_adv": final_adv,
        "metrics": {
            "p": p, "prev_p": prev_p, "change_p": change_p, "change_rate": change_rate,
            "low_b": low_b, "up_b": up_b, "defense_line": defense_line,
            "rsi": rsi_val, "w_r": w_r, "vol_strength": vol_strength
        }
    }


# ---------------------------------------------------------
# 2. UI 및 실시간 시세 조회 버튼 구현 (Streamlit 전용)
# ---------------------------------------------------------
st.set_page_config(page_title="이수 할배 주식분석기", layout="wide")

st.title("⚔️ 이수 할배 필살 주식분석기")

# 입력 구역
ticker_input = st.text_input("분석할 종목명 또는 티커를 입력하시게:", value="삼성중공업")

st.markdown("---")

# ---------------------------------------------------------
# [신규 추가] 실시간 시세 조회 대형 버튼 (시인성 극대화 CSS)
# ---------------------------------------------------------
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #1a237e !important;
        color: #ffffff !important;
        font-size: 22px !important;
        font-weight: bold !important;
        padding: 16px 30px !important;
        border-radius: 12px !important;
        border: 2px solid #3f51b5 !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        cursor: pointer !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #283593 !important;
        color: #ffeb3b !important;
        border-color: #ffeb3b !important;
    }
    </style>
""", unsafe_allow_html=True)

# 시세조회 버튼
fetch_button = st.button("🔍 [실시간 시세 조회 및 정밀 분석 실행]")

# ---------------------------------------------------------
# 버튼 클릭 시 분석 실행 및 결과 화면 출력
# ---------------------------------------------------------
if fetch_button:
    with st.spinner("실시간 장부를 눈 부라리고 뜯어보는 중이네..."):
        # ※ 실제 사용 시 이곳에 yfinance / FinanceDataReader 등의 데이터 호출 코드가 연동됩니다.
        # df = fetch_realtime_df(ticker_input) 
        
        # 임시 데이터프레임 예시 (실제 연동 시 제거)
        # result = run_stock_analysis(df, ticker_name=ticker_input)
        
        st.success(f"[{ticker_input}] 실시간 장부 분석 완료!")
        
        # 결과 표시 구역 (예시 출력 구조)
        # st.markdown(result["final_adv"], unsafe_allow_html=True)
