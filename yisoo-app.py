import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (v36056 스타일 유지)
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-main-text { font-size: 32px !important; color: #0D47A1 !important; margin-bottom: 10px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .trend-item { font-size: 23px !important; line-height: 2.0; margin-bottom: 12px; }
    .advice-highlight { color: #D32F2F !important; font-size: 26px !important; text-decoration: underline; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .val-main { font-size: 32px !important; color: #333; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 480px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-status { font-size: 32px !important; color: #D32F2F !important; margin-bottom: 10px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# [상단] 글로벌 지수 및 국채 현황 상세 진단
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info
        sp500 = yf.Ticker("^GSPC").fast_info
        tnx = yf.Ticker("^TNX").fast_info 
        
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500", f"{sp500.last_price:,.2f}", f"{(sp500.last_price / sp500.previous_close - 1) * 100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx.last_price:.3f}%", f"{(tnx.last_price - tnx.previous_close)*100:+.2f}bp")
        
        advice = "🚨 [소나기] 폭락 중 정박!" if n_chg < -0.5 else "✅ [쾌청] 성벽 확인 후 진격!" if n_chg > 0.5 else "🧐 [안개] 낚싯대만 던져두시게."
        st.info(f"👓👴 이수 할배의 글로벌 판독: {advice}")
    except:
        st.error("⚠️ 글로벌 데이터 판독 불가")

# [제목] 무테안경 회백색 영감님 캐릭터 적용
st.title("👓👴 이수할아버지의 냉정 진단기 v36056")
display_global_risk()
st.divider()

symbol = st.text_input("📊 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365); end_date = datetime.now()
        if symbol.isdigit(): # 국내 주식
            df = fdr.DataReader(symbol, start_date, end_date); currency = "원"
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            fmt_p = ",.0f"; fmt_chg = "+,.0f" 
        else: # 미국 주식
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); currency = "$"
            name = ticker.info.get('shortName', symbol); fmt_p = ",.2f"; fmt_chg = "+,.2f"
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            year_high = float(df['Close'].max()); year_low = float(df['Close'].min())
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # 기술 지표 계산
            v_ratio = (df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()) * 100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # [수세 진단 로직] 볼린저 밴드 중앙선 기준
            if p > mid_line and m_l > s_l:
                trend_desc = f"현재 중앙선({format(mid_line, fmt_p)}) 위에서 기세를 올리는 **정배열 상승 가도**일세."
            elif p < mid_line and m_l < s_l:
                trend_desc = f"중앙선({format(mid_line, fmt_p)}) 아래로 밀려버린 **역배열 하락 늪**이니 주의하시게."
            else:
                trend_desc = f"중앙선 부근에서 힘겨루기 중인 **안개 정국**이구먼."

            # 화면 출력
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, fmt_chg)})</p></div>", unsafe_allow_html=True)
            
            # [수정] 필살 대응 전략 (추세 진단 내용 보강)
            st.markdown(f"""<div class='trend-card'>
                <div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>● <b>추세 진단:</b> {trend_desc}</div>
                <div class='trend-item'>● <b>수비 상태:</b> 성벽({format(defense_line, fmt_p)} {currency}) {'함락! 후퇴!' if p < defense_line else '사수 중.'}</div>
                <div class='trend-item'>● <b>필살 조언:</b> <span class='advice-highlight'>{'⚠️ 신고가 추격 시: ' + format(p*0.95, fmt_p) + ' ' + currency + ' 이탈 시 손절!' if p >= year_high * 0.98 else '낚싯대만 던져두고 지표 바닥권을 기다리십시오.'}</span></div>
                </div>""", unsafe_allow_html=True)

            # 가격 전략 카드
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선(하단)</p><p class='val-main' style='color:#388E3C;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선(상단)</p><p class='val-main' style='color:#D32F2F;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽 (방어선)</p><p class='val-main' style='color:#E65100;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # 네 기둥 지수 상세 진단 (Bollinger 중앙선 강조)
            i1, i2, i3, i4 = st.columns(4)
            with i1: 
                bb_diag = f"중앙선({format(mid_line, fmt_p)}) 위 기세 사수 중." if p > mid_line else f"중앙선 하향 이탈, 하단 성벽 주시."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-status'>{'📈 상' if p > mid_line else '📉 하'}</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p class='ind-status'>진단중</p></div>", unsafe_allow_html=True)
            with i3: st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p class='ind-status'>판독중</p></div>", unsafe_allow_html=True)
            with i4: st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{'▲ 상승' if m_l > s_l else '▼ 하락'}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 오류: {e}")
