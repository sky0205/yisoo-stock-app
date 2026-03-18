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
    .ind-box { background-color: #FFFFFF; padding: 15px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 320px; margin-bottom: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
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
        advice = "🧐 지표 끝단을 기다리시게."
        if n_chg > 0.5 and tnx_chg < 0: advice = "✅ **[미장 쾌청]** 진격하시게."
        elif n_chg < -1.0: advice = "🚨 **[긴급 상황]** 피신하시게."
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
            # [재료 준비] 85번 줄 핵심 지표 계산
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); p_chg = ((p / prev_p) - 1) * 100
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            peak_20 = float(df['Close'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            # 기술 지표 계산 (배신 및 기세 로직 포함)
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val = rsi_series.iloc[-1]; rsi_prev = rsi_series.iloc[-2]
            
            h14_s = df['High'].rolling(14).max(); l14_s = df['Low'].rolling(14).min()
            will_series = (h14_s - df['Close']) / (h14_s - l14_s + 1e-10) * -100
            will_val = will_series.iloc[-1]; will_prev = will_series.iloc[-2]

            exp1 = df['Close'].ewm(span=12, adjust=False).mean(); exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_series = exp1 - exp2; sig_series = macd_series.ewm(span=9, adjust=False).mean()
            m_l = macd_series.iloc[-1]; s_l = sig_series.iloc[-1]
            m_prev_l = macd_series.iloc[-2]; s_prev_l = sig_series.iloc[-2]

            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # [출력] 현재주가현황
            st.markdown("### 📊 현재주가현황")
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, '+'+fmt_p)} / {p_chg:+.2f}%)</p></div>", unsafe_allow_html=True)
            
            # 거래량 판독
            v_label = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            v_adv = f"✅ 현재 5일 평균 대비 거래율 {v_ratio:.1f}%로 세력의 발자국을 추적 중일세."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_label} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권 진입", "#388E3C", "● 👺 불지옥 문턱일세! 익절하시게."
            elif p <= low_b or rsi_val <= 35: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 🧊 바닥권일세. 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세. 지표 끝단을 기다리시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            # --- [복구 완료] 매수매도 성벽 ---
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

           # [v36056] 필승 대응 전략: 진격 논리 및 상세 훈수 통합
            st.markdown(f"<div class='trend-card'><div class='trend-title'>⚔️ {name} v36056 필승 대응 전략</div>", unsafe_allow_html=True)
            
            # 1. 지표의 배신 감지 (최우선)
            is_divergence = p > prev_p and rsi_val < rsi_prev
            w_momentum = (will_val - will_prev)
            m_status = "정회전" if m_l > s_l else "역회전"
            m_diff = m_l - s_l; m_diff_prev = m_prev_l - s_prev_l

            if is_divergence:
                # 배신이 떴을 때는 경고 위주로 진격 내용을 구성하네
                st.warning(f"""
                    🚨 **[진격 중단: 지표의 배신 포착]**
                    * 현재 주가는 오르나 온도가 식었으니 가짜 상승(불 트랩)일세.
                    * 성벽({defense_line:,.0f}) 사수보다 보따리 챙기는 게 우선이니 분할 매도로 수익을 빳빳하게 확정하시게!
                """)
            
            elif w_momentum > 10:
                # 기세가 폭발했을 때 진격 내용을 안으로 넣었네
                st.info(f"""
                    🔥 **[진격 개시: 기세 폭발 및 성문 돌파]**
                    * 윌리엄 시그널이 성문을 부쐈으니 노도와 같은 기세로 진격하시게!
                    * 엔진이 {m_status}일지라도 이 정도 기세면 단기 천정까지는 무난히 밀어붙일 걸세.
                    * **필승 전략:** 성벽({defense_line:,.0f})을 뒤로하고 수익 극대화에만 집중하시게!
                """)
                
            else:
                # 평시 성벽 사수 여부에 따른 상세 진격 전략
                if p > mid_line:
                    m_advice = "엔진까지 정회전이니 거칠 것이 없네!" if m_l > s_l else "엔진 역회전폭 급감 중이니 곧 시동이 걸릴 걸세."
                    st.success(f"""
                        📈 **[안정적 진격: 성벽 사수 중]**
                        * 현재 중앙선 위에서 빳빳하게 버티며 진격의 기틀을 다지고 있네.
                        * 엔진 상태: {m_status} ({m_advice})
                        * **필승 전략:** 흔들리지 말고 홀딩하며 세력의 발자국을 끝까지 추적하시게!
                    """)
                else:
                    m_advice = "엔진 역회전 심화 중이니 절대 칼 뽑지 마시게." if m_diff <= m_diff_prev else "엔진이 회복 채비 중이나 아직 성문 밖일세."
                    st.error(f"""
                        📉 **[진격 불가: 성문 함락 및 자숙]**
                        * 성벽 밑으로 가라앉았으니 소나기는 피하는 게 상책일세.
                        * 엔진 상태: {m_status} ({m_advice})
                        * **필승 전략:** 보따리 풀지 말고 관망하며 지표 끝단이 고개 들 때까지 기다리시게!
                    """)
            
            st.markdown("</div>", unsafe_allow_html=True)
            # 네 기둥 지수 상세 분석
            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = "🏰 **[성벽 사수]** 중앙선 안착했네." if p > mid_line else "🏚️ **[성벽 함락]** 성벽 밑일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                r_diag = f"● 지수 {rsi_val:.2f}: {'🚨 배신 포착!' if is_divergence else '정상 온도 흐름일세.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams
                w_diag = f"● 지수 {will_val:.2f}: {'🔥 기세 폭발!' if w_momentum > 10 else '기세 유지 중일세.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diff = m_l - s_l; m_diff_prev = m_prev_l - s_prev_l
                m_diag = "● 엔진 **정회전**! 홀딩하시게." if m_l > s_l else ("● 엔진 **역회전폭 급감**! 정회전 채비 중일세." if m_diff > m_diff_prev else "● 엔진 **역회전 심화**! 아직은 시기상조네.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
