import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (어르신 원본 스타일 100% 보존)
st.set_page_config(page_title="이수할아버지 분석기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .title-text { font-size: 32px !important; color: #1565C0 !important; margin: 15px 0 10px 0; display: block; border-left: 8px solid #1565C0; padding-left: 12px; }
    .info-card { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 3px solid #CFD8DC; margin-bottom: 25px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .trend-item { font-size: 23px !important; line-height: 2.0; margin-bottom: 12px; }
    .advice-highlight { color: #D32F2F !important; font-size: 26px !important; text-decoration: underline; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    [data-testid="stMetricValue"] { font-size: 55px !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# 글로벌 지수 판독 (어르신 캐릭터 100% 강화)
def display_global_risk():
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        t_chg = (tnx.last_price / tnx.previous_close - 1) * 100
        st.markdown("<span class='title-text'>🌍 글로벌 시장 종합 전황</span>", unsafe_allow_html=True)
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.0f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500", f"{sp500.last_price:,.0f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년", f"{tnx.last_price:.2f}%", f"{t_chg:+.2f}%")
        advice = f"✅ **[미장 쾌청: 진격!]** 기세가 좋구먼!" if n_chg > 0.5 else f"🚨 **[긴급 상황: 정박!]** 비명 소리 나네!" if n_chg < -1.0 else "🧐 **[안개 정국: 관망]** 지표 끝단을 기다리시게."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
        st.markdown("</div>", unsafe_allow_html=True)
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("👴 이수할아버지의 냉정 진단기 v36056")
display_global_risk()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "CPNG")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365); end_date = datetime.now()
        if symbol.isdigit():
            df = fdr.DataReader(symbol, start_date, end_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]; currency = "원"; fmt = ",.0f" 
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date)
            name = ticker.info.get('shortName', symbol); currency = "$"; fmt = ",.2f"
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            year_high = float(df['Close'].max()); year_low = float(df['Close'].min())
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # [복구] 현재 주가 헤더
            st.markdown(f"""
                <div class='stock-header'>
                    <p style='font-size:32px; color:#1565C0; margin-bottom:5px;'>📈 현재 주가 진황</p>
                    <p style='font-size:35px; color:#455A64; margin:0;'>{name} ({symbol})</p>
                    <p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt)} {currency} (전일비: {p-prev_p:+.2f})</p>
                </div>""", unsafe_allow_html=True)
            
            # 지수 계산 및 볼린저 밴드
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]

            trend_desc = "정배열 상승 가도" if (m_l > s_l and p > mid_line) else "역배열 하락 늪" if (m_l < s_l and p < mid_line) else "횡보 및 안개 정국"

            # [수정 완료] 볼린저 밴드 돌파 상태에 따른 필살 조언 로직
            if p >= up_b:
                advice_text = "💰 **[과열 경보]** 성벽 밖으로 튀어나갔네! 탐욕 버리고 익절 수익을 빳빳하게 챙기시게."
            elif p <= low_b:
                advice_text = "🛡️ **[바닥 포착]** 하단 성벽 근처일세! 겁내지 말고 분할 매수 보따리를 푸시게."
            else:
                advice_text = "🎣 낚싯대만 던져두고 지표 끝단이나 바닥권을 차분히 기다리시게."

            st.markdown(f"""<div class='trend-card'>
                <div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>● <b>추세 진단:</b> 현재 장부는 <span style='color:#D32F2F;'>{trend_desc}</span> 상태로 판독되구먼요.</div>
                <div class='trend-item'>● <b>수비 상태:</b> 성벽({format(defense_line, fmt)} {currency}) {'함락! 후퇴하십시오.' if p < defense_line else '사수 중입니다.'}</div>
                <div class='trend-item'>● <b>필살 조언:</b> <span class='advice-highlight'>{advice_text}</span></div>
                </div>""", unsafe_allow_html=True)

            # 나머지 어르신 원본 100% 보존
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            v_label = "💤 거래침체"; v_adv = "🚨 <b>가짜 상승 주의!</b>" if p > prev_p and v_ratio < 100 else "✅ 세력 발자국 추적 중."
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; color:#0D47A1;'>📊 거래량 전황: {v_ratio:.1f}%</div><div style='font-size:20px; color:#1565C0;'>{v_adv}</div></div>", unsafe_allow_html=True)

            if p >= up_b or rsi_val >= 65: sig, col = "🟢 매도권 진입", "#388E3C"
            elif p <= low_b or rsi_val <= 35: sig, col = "🔴 매수권 진입", "#D32F2F"
            else: sig, col = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {col};'><span style='font-size:65px; color:white;'>{sig}</span></div>", unsafe_allow_html=True)

            # 가격 카드 및 4대 지수 훈수 (원본 보존)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽 (방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt)}</p></div>", unsafe_allow_html=True)

            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>Bollinger (기세)</p><p class='ind-diag'>● **[상단 돌파!]** 하늘 찌르네! 익절 준비 하시게.</p></div>", unsafe_allow_html=True)
            with i2:
                st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.1f}</p><p class='ind-diag'>● 지수 {rsi_val:.1f}로 **👺 불지옥** 문턱일세! 익절가 잡으시게.</p></div>", unsafe_allow_html=True)
            with i3:
                h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
                st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.1f}</p><p class='ind-diag'>● 지수 {will_val:.1f}로 **🏳️ 개미 항복** 구간! 보따리 푸시게.</p></div>", unsafe_allow_html=True)
            with i4:
                st.markdown(f"<div class='ind-box'><p style='font-size:26px; color:#1976D2;'>MACD (엔진)</p><p class='ind-diag'>● {'엔진 정회전! 기세 좋구먼.' if m_l > s_l else '엔진 **역회전** 중! 절대 속지 마시게.'}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
