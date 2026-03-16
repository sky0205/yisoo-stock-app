import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (v36056 스타일 완벽 유지)
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
    .advice-highlight { color: #D32F2F !important; font-size: 26px !important; text-decoration: underline; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .val-main { font-size: 32px !important; color: #333; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-status { font-size: 32px !important; color: #D32F2F !important; margin-bottom: 10px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

# [상단] 글로벌 지표 상세 진단
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
        
        advice = "🚨 [미장 소나기] 폭락 중! 정박하시게!" if n_chg < -0.5 else "✅ [미장 쾌청] 성벽 확인 후 진격!" if n_chg > 0.5 else "🧐 [안개 정국] 낚싯대만 던져두십시오."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
        return advice
    except:
        st.error("⚠️ 글로벌 데이터 판독 불가")

# 제목 (캐릭터: 젠틀한 할배 유지)
st.title("🧐 이수할아버지의 냉정 진단기 v36056")
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
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            price_up = p > prev_p
            
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(window=14).max().iloc[-1]; l14 = df['Low'].rolling(window=14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            # [신호등 점수]
            buy_score = sum([p <= low_b, rsi_val <= 35, will_val <= -75]); sell_score = sum([p >= up_b, rsi_val >= 65, will_val >= -20])

            # 화면 출력 시작
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, fmt_chg)})</p></div>", unsafe_allow_html=True)
            
            # 거래량 분석
            v_status = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            v_adv = "🚨 <b>가짜 상승!</b> 거래량 없는 상승은 빈집에 바람 드는 격이니 절대 속지 마십시오." if price_up and v_ratio < 100 else "✅ 관심 집중!"
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 신호등 박스
            if buy_score >= 2: sig, color = "🔴 매수권 진입", "#D32F2F"
            elif sell_score >= 2: sig, color = "🟢 매도권 진입", "#388E3C"
            elif p >= year_high * 0.98: sig, color = "🔥 신고가 돌파", "#E65100"
            else: sig, color = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {color};'><span class='signal-text'>{sig}</span></div>", unsafe_allow_html=True)

            # 필살 대응 전략
            trend_desc = "정배열 상승 가도" if (p > mid_line and m_l > s_l) else "역배열 하락 늪"
            st.markdown(f"""<div class='trend-card'>
                <div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>● <b>추세 진단:</b> 현재 장부는 <span style='color:#D32F2F;'>{trend_desc}</span> 상태로 판독되구먼요.</div>
                <div class='trend-item'>● <b>수비 상태:</b> 성벽({format(defense_line, fmt_p)} {currency}) {'함락! 후퇴하십시오.' if p < defense_line else '사수 중입니다.'}</div>
                <div class='trend-item'>● <b>필살 조언:</b> <span class='advice-highlight'>{'⚠️ 신고가 추격 시: ' + format(p*0.95, fmt_p) + ' ' + currency + ' 이탈 시 손절!' if p >= year_high * 0.98 else '낚싯대만 던져두고 지표 바닥권을 기다리십시오.'}</span></div>
                </div>""", unsafe_allow_html=True)

            # 가격 전략 카드
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선(하단)</p><p class='val-main' style='color:#388E3C;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선(상단)</p><p class='val-main' style='color:#D32F2F;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽 (방어선)</p><p class='val-main' style='color:#E65100;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

           # [핵심 수선] 네 기둥 지수 상세 진단 (현실 밀착형 훈수)
            i1, i2, i3, i4 = st.columns(4)
            
            with i1: # Bollinger (기세)
                if p >= up_b: bb_pos, bb_color = "🔥 폭주", "#D32F2F"
                elif p <= low_b: bb_pos, bb_color = "📉 추락", "#1976D2"
                elif p > mid_line: bb_pos, bb_color = "⚖️ 눈치보기(상)", "#388E3C"
                else: bb_pos, bb_color = "⚖️ 눈치보기(하)", "#E65100"
                
                bb_diag = f"● **중앙선({format(mid_line, fmt_p)}) 위**일세. 기세는 살아있으나 상단 성벽 돌파 못 하면 소나기 오니 조심하시게!" if bb_pos=="⚖️ 눈치보기(상)" else \
                          f"● **중앙선({format(mid_line, fmt_p)}) 아래**일세. 힘이 다 빠졌구먼. 하단 성벽 무너지면 미련 없이 던지시게!" if bb_pos=="⚖️ 눈치보기(하)" else \
                          f"● 성벽 밖 **과열 권역**일세! 곧 차익 실현 매물이 쏟아질 테니 보따리 쌀 준비나 하시게." if bb_pos=="🔥 폭주" else \
                          f"● 하단 성벽이 무너진 **공포 구간**일세. 비명 소리가 잦아들 때까지 절대 칼날을 잡지 마시게!"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-status' style='color:{bb_color};'>{bb_pos}</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2: # RSI (온도)
                r_stat = "👺 불지옥" if rsi_val > 65 else "🧊 냉골" if rsi_val < 35 else "미지근"
                r_diag = f"● 온도 {rsi_val:.2f}의 **불지옥**일세! 남들 환호하며 올라탈 때 냉정하게 팔고 나오시게." if r_stat=="👺 불지옥" else \
                         f"● 온도 {rsi_val:.2f}의 **냉골**일세. 바닥에서 얼음 깨지는 소리 들릴 때까지 낚싯대만 던져두시게." if r_stat=="🧊 냉골" else \
                         f"● 매수-매도가 팽팽한 **줄다리기** 중일세. 방향성 없는 싸움에 끼어들어 수수료만 버리지 마시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            
            with i3: # Williams %R (천장/바닥)
                w_status = "🧨 천장광기" if will_val > -25 else "🏳️ 바닥항복" if will_val < -75 else "중간지대"
                w_diag = f"● 지수 {will_val:.2f}로 **천장 끝단**일세! 불나방들이 꼬이는 자리니 절대 추격 매수는 금물이야." if w_status=="🧨 천장광기" else \
                         f"● 지수 {will_val:.2f}로 **바닥권**일세. 개미들이 다 털리고 나갈 때니 분할 매수 보따리를 푸시게." if w_status=="🏳️ 바닥항복" else \
                         f"● 현재 **안개 속**일세. -20을 뚫는지, -80으로 처박히는지 확인하고 움직여도 안 늦어."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            
            with i4: # MACD (엔진)
                macd_status = "▲ 상승엔진" if m_l > s_l else "▼ 하강엔진"
                macd_diag = f"● **상승 엔진** 가동 중이나 성벽 저항을 보시게. 함부로 풀악셀 밟다가는 엔진 과부하 걸리네." if m_l > s_l else \
                            f"● **하강 엔진**으로 역회전 중일세! 섣불리 진격하지 말고 폭풍우가 지나가길 기다리는 게 상책이야."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{macd_status}</p><p class='ind-diag'>{macd_diag}</p></div>", unsafe_allow_html=True)
    except Exception as e: st.error(f"👵 아이구! 오류가 났네: {e}")
