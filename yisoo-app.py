import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (v36056 스타일 및 할배 캐릭터 복구)
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
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-status { font-size: 32px !important; color: #D32F2F !important; margin-bottom: 10px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# [상단] 글로벌 지수 및 미 국채 현황 상세 진단
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info
        sp500 = yf.Ticker("^GSPC").fast_info
        tnx = yf.Ticker("^TNX").fast_info 
        
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        s_chg = (sp500.last_price / sp500.previous_close - 1) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{s_chg:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx.last_price:.3f}%", f"{(tnx.last_price - tnx.previous_close)*100:+.2f}bp")
        
        # [수정] 글로벌 전황 판독 조언 보강
        if n_chg < -0.5:
            advice = "🚨 [미장 소나기] 미 증시 폭락 중! 성벽 안으로 대피하고 정박하시게!"
        elif n_chg > 0.5:
            advice = "✅ [미장 쾌청] 미 증시 훈풍 중! 하늘이 맑으니 성벽 사수 여부 보고 진격하시게."
        else:
            advice = "🧐 [안개 정국] 미 증시 혼조세구먼. 섣불리 움직이지 말고 낚싯대만 던져두십시오."
            
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
        return advice
    except:
        return "⚠️ [데이터 오류] 글로벌 전황 판독 불가"

# 제목 (캐릭터 수정: 무테안경을 쓴 회백색 젠틀 할아버지)
st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk() 
st.divider()

symbol = st.text_input("📊 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365); end_date = datetime.now()
        if symbol.isdigit(): # 국내 주식
            df = fdr.DataReader(symbol, start_date, end_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            currency = "원"; fmt_p = ",.0f"; fmt_chg = "+,.0f" 
        else: # 미국 주식
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date)
            name = ticker.info.get('shortName', symbol); currency = "$"; fmt_p = ",.2f"; fmt_chg = "+,.2f"
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            year_high = float(df['Close'].max()); year_low = float(df['Close'].min())
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # [부활] 거래량 분석 로직
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            price_up = p > prev_p
            
            if v_ratio < 100:
                v_status, v_adv = "💤 거래침체", "🚨 <b>가짜 상승!</b> 거래량 없는 상승은 빈집에 바람 드는 격이니 절대 속지 마십시오." if price_up else "⏳ <b>눈치보기 중.</b> 바닥 확인될 때까지 섣불리 물타지 마십시오."
            elif 100 <= v_ratio < 200:
                v_status, v_adv = "📈 거래증가", "✅ <b>관심 집중.</b> 거래량이 실리며 오르니 기세가 붙고 있습니다." if price_up else "⚠️ <b>물량 출회.</b> 누군가 던지기 시작했으니 하단 성벽 사수 여부를 보십시오."
            else:
                v_status, v_adv = "🔥 거래폭발", "🚀 <b>세력 진격!</b> 큰손들이 문 부수고 들어왔습니다." if price_up else "💣 <b>투매 발생!</b> 아비규환이니 보따리 싸서 대피하십시오."

            # 기술 지표 및 추세 진단 로직
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # [수정] 필살 대응 전략 내 추세 진단 보완
            trend_desc = f"현재 **중앙선({format(mid_line, fmt_p)}) 위** 기세를 탄 정배열 상승세" if (p > mid_line and m_l > s_l) else f"**중앙선({format(mid_line, fmt_p)}) 아래**로 밀린 역배열 하락세"

            # 화면 출력
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, fmt_chg)})</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 필살 대응 전략
            st.markdown(f"""<div class='trend-card'>
                <div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>● <b>추세 진단:</b> {trend_desc}로 판독되구먼요.</div>
                <div class='trend-item'>● <b>수비 상태:</b> 성벽({format(defense_line, fmt_p)} {currency}) {'함락! 후퇴하십시오.' if p < defense_line else '사수 중입니다.'}</div>
                <div class='trend-item'>● <b>필살 조언:</b> <span class='advice-highlight'>{'⚠️ 신고가 추격 시: ' + format(p*0.95, fmt_p) + ' ' + currency + ' 이탈 시 손절!' if p >= year_high * 0.98 else '낚싯대만 던져두고 지표 바닥권을 기다리십시오.'}</span></div>
                </div>""", unsafe_allow_html=True)

            # 6. 네 기둥 지수 상세 진단 (어르신 전용 보강본)
            i1, i2, i3, i4 = st.columns(4)
            
            with i1: # Bollinger 상세
                bb_pos = "🔥 폭주" if p >= up_b else "📉 추락" if p <= low_b else "⚖️ 눈치보기"
                bb_diag = f"● 현재 **중앙선({format(mid_line, fmt_p)}) 아래**에서 빌빌대고 있으니 하단 성벽 무너지면 미련 없이 보따리 싸시게!" if p <= mid_line else \
                          f"● 현재 **중앙선({format(mid_line, fmt_p)}) 위**에서 기세를 타는 중일세. 상단 성벽 돌파 여부를 눈을 부라리고 보시게!"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-status' style='color:#D32F2F;'>{bb_pos}</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2: # RSI 상세
                rsi_stat = "👺 불지옥" if rsi_val > 65 else "🧊 냉골" if rsi_val < 35 else "미지근"
                rsi_diag = f"● 현재 **{rsi_stat}** 상태일세. 탐욕과 공포 사이에서 냉정하게 판단하시게. 섣부른 진격은 패가망신의 지름길이야."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{rsi_diag}</p></div>", unsafe_allow_html=True)
            
            with i3: # Williams %R 상세
                w_stat = "🧨 광기" if will_val > -35 else "🏳️ 항복" if will_val < -65 else "중간지대"
                w_diag = f"● 현재 지수 {will_val:.2f}로 **{w_stat}** 구간 근처일세. 과매수와 과매도 사이의 변곡점을 매섭게 째려보고 있구먼."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            
            with i4: # MACD 상세
                macd_status = "▲ 상승엔진" if m_l > s_l else "▼ 하강엔진"
                macd_diag = f"● 현재 **{macd_status}**으로 역회전 혹은 가속 중일세. 추세의 엔진이 어느 쪽으로 도는지 냉정하게 판독 중이야."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{macd_status}</p><p class='ind-diag'>{macd_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류가 났네: {e}")
