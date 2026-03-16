import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (v36056 스타일 유지)
st.set_page_config(page_title="이수할아버지 분석기 v36056", layout="wide")
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
    .advice-highlight { color: #D32F2F !important; font-size: 26px !important; text-decoration: underline; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .val-main { font-size: 32px !important; color: #333; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-status { font-size: 32px !important; color: #D32F2F !important; margin-bottom: 10px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# [추가] 글로벌 지수 상세 진단 함수
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 종합 전황 (실시간 진단)")
    try:
        # 다우지수, S&P 500, 나스닥 실시간 데이터 호출
        dow = yf.Ticker("^DJI").fast_info
        sp5 = yf.Ticker("^GSPC").fast_info
        nas = yf.Ticker("^IXIC").fast_info
        
        d_chg = (dow.last_price / dow.previous_close - 1) * 100
        s_chg = (sp5.last_price / sp5.previous_close - 1) * 100
        n_chg = (nas.last_price / nas.previous_close - 1) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("다우 존스 (DOW)", f"{dow.last_price:,.2f}", f"{d_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp5.last_price:,.2f}", f"{s_chg:.2f}%")
        c3.metric("나스닥 (NASDAQ)", f"{nas.last_price:,.2f}", f"{n_chg:.2f}%")
        
        # 미장 전황 판독 조언 생성
        if n_chg < -0.5:
            return "🚨 [미장 소나기] 미 증시 폭락 중! 홍수 속에 핀 꽃은 금방 시드네. 보수적으로 대응하십시오."
        elif n_chg > 0.5:
            return "✅ [미장 쾌청] 미 증시 훈풍 중! 하늘이 맑으니 성벽 사수 여부 보고 진격 수위를 높이십시오."
        else:
            return "🧐 [안개 정국] 미 증시 혼조세구먼. 섣불리 움직이지 말고 낚싯대만 던져두십시오."
    except:
        return "⚠️ [데이터 오류] 글로벌 전황 판독 불가"

st.title("👴 이수할아버지의 냉정 진단기 v36056")

# 글로벌 전황 먼저 표시
us_advice = display_global_risk()
st.divider()

symbol = st.text_input("📊 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365); end_date = datetime.now()
        if symbol.isdigit(): # 국내 주식
            df = fdr.DataReader(symbol, start_date, end_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            currency = "원"; fmt = ",.0f" 
        else: # 미국 주식
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date)
            name = ticker.info.get('shortName', symbol); currency = "$"; fmt = ",.2f"
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            year_high = float(df['Close'].max()); year_low = float(df['Close'].min())
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # 거래량 및 지표 계산 (어르신 기존 로직 유지)
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            price_up = p > prev_p
            
            # 거래량 판독 로직
            if v_ratio < 100:
                v_status = "💤 거래침체"
                v_advice = "🚨 <b>가짜 상승!</b> 거래량 없는 상승은 빈집에 바람 드는 격이니 절대 속지 마십시오." if price_up else "⏳ <b>눈치보기 중.</b> 파는 사람도 없으니 바닥 확인될 때까지 섣불리 물타지 마십시오."
            elif 100 <= v_ratio < 200:
                v_status = "📈 거래증가"
                v_advice = "✅ <b>관심 집중.</b> 거래량이 실리며 오르니 기세가 붙고 있습니다." if price_up else "⚠️ <b>물량 출회.</b> 누군가 던지기 시작했으니 하단 성벽 사수 여부를 보십시오."
            else:
                v_status = "🔥 거래폭발"
                v_advice = "🚀 <b>세력 진격!</b> 큰손들이 문 부수고 들어왔습니다." if price_up else "💣 <b>투매 발생!</b> 아비규환이니 보따리 싸서 대피하십시오."

            # 지표 계산 (RSI, Williams, MACD, BB)
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(window=14).max().iloc[-1]; l14 = df['Low'].rolling(window=14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            buy_score = sum([p <= low_b, rsi_val <= 35, will_val <= -75]); sell_score = sum([p >= up_b, rsi_val >= 65, will_val >= -20])
            is_new_high = p >= year_high * 0.98; is_new_low = p <= year_low * 1.02
            trend_desc = "정배열 상승 가도" if (m_l > s_l and p > mid_line) else "역배열 하락 늪" if (m_l < s_l and p < mid_line) else "횡보 및 안개 정국"

            # 화면 출력 시작
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt)} {currency} (전일비: {p-prev_p:+.2f})</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_advice}</div></div>", unsafe_allow_html=True)

            # 매수/매도 신호
            if buy_score >= 2: sig, color = "🔴 매수권 진입", "#D32F2F"
            elif sell_score >= 2: sig, color = "🟢 매도권 진입", "#388E3C"
            elif is_new_high: sig, color = "🔥 신고가 돌파", "#E65100"
            else: sig, color = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {color};'><span class='signal-text'>{sig}</span></div>", unsafe_allow_html=True)

            # [수정] 4. 실전 필살 대응 전략 (미장 전황 및 종목 상황 통합)
            st.markdown(f"""<div class='trend-card'>
                <div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>● <b>글로벌 전황:</b> {us_advice}</div>
                <div class='trend-item'>● <b>추세 진단:</b> {name}은(는) 현재 <span style='color:#D32F2F;'>{trend_desc}</span> 상태로 판독되구먼요.</div>
                <div class='trend-item'>● <b>수비 상태:</b> 성벽({format(defense_line, fmt)} {currency}) {'함락! 후퇴하십시오.' if p < defense_line else '사수 중입니다.'}</div>
                <div class='trend-item'>● <b>필살 조언:</b> <span class='advice-highlight'>{'⚠️ 신고가 추격 시: ' + format(p*0.95, fmt) + ' ' + currency + ' 이탈 시 손절!' if is_new_high else '📉 신저가 구간: ' + format(p, fmt) + ' ~ ' + format(year_low*0.95, fmt) + ' 사이 3회 분할 매수!' if is_new_low else '낚싯대만 던져두고 지표 바닥권을 기다리십시오.'}</span></div>
                </div>""", unsafe_allow_html=True)

            # 가격 전략 카드
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선(하단)</p><p class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선(상단)</p><p class='val-main' style='color:#D32F2F;'>{format(up_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽 (방어선)</p><p class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</p></div>", unsafe_allow_html=True)

            # 네 기둥 지수 상세 (하단부)
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = f"중앙선({format(mid_line, fmt)}) 위 기세를 타는 중." if p > mid_line else f"중앙선({format(mid_line, fmt)}) 아래 하락 압박 중."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p></div>", unsafe_allow_html=True)
            with i3: # Williams
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{'▲ 상승' if m_l > s_l else '▼ 하락'}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류가 났네: {e}")
