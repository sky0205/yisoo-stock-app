import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. 화면 구성 및 할배 캐릭터 스타일 (완벽 유지)
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-main-text { font-size: 32px !important; color: #0D47A1 !important; margin-bottom: 10px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 65px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .trend-item { font-size: 23px !important; line-height: 2.0; margin-bottom: 12px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 지표 실시간 연동 (그대로 유지)
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황 (미장 실시간 분석)")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        tnx_val = tnx.last_price; tnx_chg = (tnx_val / tnx.previous_close - 1) * 100
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
        if n_chg > 0.5 and tnx_chg < 0: advice = f"✅ **[미장 쾌청: 진격!]** 나스닥 불 뿜고 금리도 안정세일세! 기세 타고 진격하시게."
        elif n_chg < -1.0: advice = f"🚨 **[긴급 상황: 정박!]** 나스닥 급락 중이니 성벽 무너지기 전에 보따리 싸서 피신하시게."
        elif tnx_val > 4.3: advice = "⚠️ **[금리 비상: 관망]** 국채 금리 너무 높네! 성벽 위태로우니 무리한 진격은 금물일세."
        else: advice = "🧐 **[안개 정국: 관망]** 지표 끝단을 기다리시게."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500); end_date = datetime.now()
        is_kr = symbol.isdigit()
        if is_kr:
            now_local = datetime.now(pytz.timezone('Asia/Seoul')); currency = "원"; fmt_p = ",.0f"
            df = fdr.DataReader(symbol, start_date, end_date); stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
        else:
            now_local = datetime.now(pytz.timezone('US/Eastern')); ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); currency = "$"; fmt_p = ",.2f"; name = ticker.info.get('shortName', symbol)
        
        is_opening = 9 <= now_local.hour <= 11

        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); p_chg = ((p / prev_p) - 1) * 100
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            peak_20 = float(df['Close'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            # 기술 지표 계산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            m_l = df['Close'].ewm(span=5).mean().iloc[-1] - df['Close'].ewm(span=35).mean().iloc[-1]; s_l = (df['Close'].ewm(span=5).mean() - df['Close'].ewm(span=35).mean()).ewm(span=5).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # [수정] 어르신 명하신 대로 제목만 정갈하게 추가
            st.markdown("### 📊 현재주가현황")
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, '+'+fmt_p)} / {p_chg:+.2f}%)</p></div>", unsafe_allow_html=True)
            
            # 81번 줄 근처: 거래량 상세 판독 (기존 로직 보강)
    v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"

    # 94번 줄 근처: 볼린저 및 윌리엄 상세 설명 로직
    # 볼린저 상세 설명 (b_adv)
    if p >= up_b * 0.98:
        b_adv = "🔥 성벽(상단선) 돌파 중! 기세가 하늘을 찌르는구먼."
    elif p >= mid_b:
        b_adv = "📈 중앙선 위에서 안착! 성벽을 향해 진격 중일세."
    else:
        b_adv = "⚖️ 중앙선 아래서 빌빌대고 있구먼. 성벽 사수 확인하시게."

    # 윌리엄 상세 설명 (w_adv)
    if w_r >= -20:
        w_adv = "🚩 천장 문고리 잡았네! 과열 구간이니 수확 준비 하시게."
    elif w_r >= -50:
        w_adv = "🚀 중간 지대 돌파! 바닥 탈출해서 기운차게 달리는 중일세."
    else:
        w_adv = "⚓ 바닥권이거나 아직 힘이 부족하구먼. 갈피를 잡는지 보시게."
else: 
    sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", f"⚪ {b_adv} {w_adv}"background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # 필살 대응 전략 및 최종 결론 (원본 보존)
            adv1 = f"1. **진격 금지:** RSI가 {rsi_val:.2f}로 아직 60을 향해 고개를 들지 않았네. 섣불리 뛰어들지 마시게." if rsi_val < 60 else "1. **기세 타기:** RSI가 60을 돌파하며 불이 붙었구먼!"
            adv2 = f"2. **성벽 사수 확인:** 현재 주가가 성벽({format(defense_line, fmt_p)}) {'아래' if p < defense_line else '위'}일세. {'함락됐으니 지하실 조심하시게.' if p < defense_line else '사수 중이니 진격의 발판 삼으시게.'}"
            adv3 = f"3. **엔진(MACD) 확인:** 엔진이 아직 **역회전** 중이라네! 절대 속지 마시게!" if m_l < s_l else "3. **엔진 정회전:** 엔진 시동 걸렸구먼!"
            if p >= up_b or rsi_val >= 60: final_adv = "💰 **[최종 결론]** 탐욕의 끝자락일세. **분할 매도**하여 수익을 빳빳하게 챙기시게!"
            elif p <= low_b or rsi_val <= 35: final_adv = "🛡️ **[최종 결론]** 공포가 극에 달한 바닥권일세. **분할 매수**로 보따리를 푸시게!"
            elif p < defense_line: final_adv = "🧐 **[최종 결론]** 성벽이 위태롭네. 사수 확인 전까지는 **관망하며 기다리시게!**"
            else: final_adv = "📈 **[최종 결론]** 추세 살아있구먼. 성벽 사수 확인하며 **보유(홀딩)**하시게!"

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)

            # [복구 완벽] 네 기둥 지수 상세 분석 (원본 문구 보존)
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = f"● **[비상: 상단 돌파!]** 하늘 찌르는구먼! 탐욕 버리고 수확(익절) 준비 하시게." if p >= up_b else f"● **[비상: 하단 돌파!]** 바닥권일세! 지지받고 고개 들면 진짜 진격 기회일세." if p <= low_b else f"● 중앙선 아래서 빌빌대고 있구먼. 성벽 사수 확인 전까지는 낚싯대만 던지시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI (60 이상 불지옥 반영)
                r_diag = f"● 지수 {rsi_val:.2f}로 **👺 불지옥** 문턱일세! 천장에 다 왔으니 익절가 빳빳하게 잡으시게." if rsi_val >= 60 else f"● 지수 {rsi_val:.2f}로 **🧊 냉골** 상태일세! 남들 무서울 때 우리는 냉정하게 바닥을 보시게." if rsi_val <= 35 else f"● 지수 {rsi_val:.2f}로 탐욕과 공포 사이 중립 기어 넣고 눈치싸움 중일세. 지표 끝단을 기다리시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams
                w_diag = f"● 지수 {will_val:.2f}로 **🏳️ 개미 항복** 구간일세! 보따리 푸시게. 여기서 고개 들면 무조건 진격일세!" if will_val < -80 else f"● 지수 {will_val:.2f}로 **🧨 천장 광기** 구간일세! 언제 비수 꽂힐지 모르니 매섭게 보시게." if will_val > -20 else f"● 현재 중간지대일세. 바닥인지 천장인지 갈피를 못 잡고 있구먼."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diag = "● 엔진이 정회전 중일세! 기세 붙었으니 성벽 사수 여부를 보시게." if m_l > s_l else f"● 엔진이 **역회전** 중이네! 거꾸로 도는 차에 올라타면 안 되는 법일세. 함부로 키 잡지 마시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
