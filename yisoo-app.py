import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

import streamlit as st

# [재료 1] 글로벌 리스크 지표 함수
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 종합 전황 (90% 승률 필터)")
    
    try:
        # [실시간 획득] 나스닥(^IXIC), S&P500(^GSPC), 10년물 국채(^TNX)
        nasdaq = yf.Ticker("^IXIC").fast_info
        sp500 = yf.Ticker("^GSPC").fast_info
        tnx = yf.Ticker("^TNX").fast_info
        
        # 지수 계산 (값과 등락률)
        n_val, n_chg = round(nasdaq.last_price, 2), round(((nasdaq.last_price - nasdaq.previous_close) / nasdaq.previous_close) * 100, 2)
        s_val, s_chg = round(sp500.last_price, 2), round(((sp500.last_price - sp500.previous_close) / sp500.previous_close) * 100, 2)
        t_val, t_chg = round(tnx.last_price, 2), round(tnx.last_price - tnx.previous_close, 3)
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        with col1:
            st.metric("나스닥 (NASDAQ)", f"{n_val:,}", f"{n_chg}%", delta_color="inverse")
        with col2:
            st.metric("S&P 500", f"{s_val:,}", f"{s_chg}%", delta_color="inverse")
        with col3:
            st.metric("미 국채 10년물", f"{t_val}%", f"{t_chg}bp", delta_color="inverse")
        
        with col4:
            # [할배의 종합 판독] 3대 지수를 묶어서 한마디!
            if n_chg < 0 and s_chg < 0 and t_chg > 0:
                st.error("🚨 **[초비상]** 지수는 폭락하고 금리는 치솟네! 이건 홍수 수준일세. 보따리 꽁꽁 묶고 정박하시게!")
            elif n_chg < 0 or s_chg < 0:
                st.warning("⚠️ **[주의]** 미국 하늘에 먹구름이 끼었구먼. 국장 상승은 '가짜 해'일 확률이 높으니 속지 마시게!")
            elif n_chg > 0 and s_chg > 0 and t_chg < 0:
                st.success("✅ **[기회]** 하늘도 맑고 돈줄(금리)도 풀렸네! 거래량 터지는 놈 위주로 부라리고 보시게!")
            else:
                st.info("🧐 **[관망]** 장세가 혼조세구먼. 섣불리 움직이지 말고 낚싯대만 던져두게.")
                
    except Exception as e:
        st.error("글로벌 지수 데이터를 불러오지 못했습니다.")

# [재료 2] 호가창 허수 판독 함수
def hoka_check(bid_res, ask_res):
    if bid_res > ask_res * 1.5:
        return "🚨 호가창 허수 주의! (매수잔량 과다로 개미 유인 중)"
    return "✅ 호가창 전황 안정적"
# 1. 화면 구성 (기존 v36056 스타일 유지)
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

st.title("👨‍🦳 이수할아버지의 냉정 진단기 v36056")
us_advice = display_global_risk()
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

            # 거래량 분석
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            price_up = p > prev_p
            
            if v_ratio < 100:
                v_status = "💤 거래침체"
                v_advice = "🚨 <b>가짜 상승!</b> 거래량 없이 오르는 건 빈집에 바람 드는 격이니 절대 속지 마십시오." if price_up else \
                           "⏳ <b>눈치보기 중.</b> 파는 사람도 없으니 바닥 확인될 때까지 섣불리 물타지 마십시오."
            elif 100 <= v_ratio < 200:
                v_status = "📈 거래증가"
                v_advice = "✅ <b>관심 집중.</b> 거래량이 실리며 오르니 기세가 붙고 있습니다. 정찰병 파견 검토하십시오." if price_up else \
                           "⚠️ <b>물량 출회.</b> 누군가 던지기 시작했으니 하단 성벽 사수 여부를 부라리고 보십시오."
            else:
                v_status = "🔥 거래폭발"
                v_advice = "🚀 <b>세력 진격!</b> 큰손들이 문 부수고 들어왔습니다. 장대양봉이면 진격 수위를 높이십시오." if price_up else \
                           "💣 <b>투매 발생!</b> 아비규환이니 지하실 열리기 전에 일단 보따리 싸서 대피하십시오."

            # 지표 계산 로직
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
            h14 = df['High'].rolling(window=14).max().iloc[-1]; l14 = df['Low'].rolling(window=14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]
            up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            buy_score = sum([p <= low_b, rsi_val <= 35, will_val <= -75]); sell_score = sum([p >= up_b, rsi_val >= 65, will_val >= -20])
            is_new_high = p >= year_high * 0.98; is_new_low = p <= year_low * 1.02
            trend_desc = "정배열 상승 가도" if (m_l > s_l and p > mid_line) else "역배열 하락 늪" if (m_l < s_l and p < mid_line) else "횡보 및 안개 정국"

            # 상단 표시
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt)} {currency} (전일비: {p-prev_p:+.0f})</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_advice}</div></div>", unsafe_allow_html=True)

            if buy_score >= 2: sig, color = "🔴 매수권 진입", "#D32F2F"
            elif sell_score >= 2: sig, color = "🟢 매도권 진입", "#388E3C"
            elif is_new_high: sig, color = "🔥 신고가 돌파", "#E65100"
            else: sig, color = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {color};'><span class='signal-text'>{sig}</span></div>", unsafe_allow_html=True)

            # 4. 실전 필살 대응 전략
            st.markdown(f"""<div class='trend-card'>
                <div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>● <b>추세 진단:</b> 현재 장부는 <span style='color:#D32F2F;'>{trend_desc}</span> 상태로 판독되구먼요.</div>
                <div class='trend-item'>● <b>수비 상태:</b> 성벽({format(defense_line, fmt)} {currency}) {'함락! 후퇴하십시오.' if p < defense_line else '사수 중입니다.'}</div>
               <div class='trend-item'>
    <div class='trend-item'>
    ● <b>필살 조언:</b><br>
    <span style='color:#FF0000; font-weight:bold; font-size:1.2em; background-color:#000000; padding:3px 5px; border-radius:3px; display:inline-block; margin:5px 0;'>{us_advice}</span><br>
    <span class='advice-highlight'>{'⚠️ 신고가 추격 시: ' + format(p*0.95, fmt) + ' ' + currency + ' 이탈 시 손절!'}</span>
</div>
                </div>""", unsafe_allow_html=True)

            # 5. 가격 전략 카드 (중앙선 추가)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선(하단)</p><p class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선(상단)</p><p class='val-main' style='color:#D32F2F;'>{format(up_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽 (방어선)</p><p class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</p></div>", unsafe_allow_html=True)

            # 6. 네 기둥 지수란 (볼린저 밴드 중앙선 기준 보완)
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                if p >= up_b: bb_pos, bb_color = "🔥 폭주", "#D32F2F"
                elif p <= low_b: bb_pos, bb_color = "📉 추락", "#1976D2"
                elif p > mid_line: bb_pos, bb_color = "⚖️ 눈치보기(상)", "#388E3C"
                else: bb_pos, bb_color = "⚖️ 눈치보기(하)", "#E65100"
                
                bb_diag = f"● 현재 **중앙선({format(mid_line, fmt)}) 위**에서 기세를 타는 중입니다. 상단 성벽 돌파 시도는 긍정적이나, 실패 시 중앙선까지 밀릴 수 있으니 주의하십시오." if bb_pos=="⚖️ 눈치보기(상)" else \
                          f"● 현재 **중앙선({format(mid_line, fmt)}) 아래**에서 빌빌대고 있습니다. 기운이 빠져 하단 성벽까지 밀릴 위험이 크니 섣부른 진격은 금물입니다." if bb_pos=="⚖️ 눈치보기(하)" else \
                          f"● 성벽 밖 **과열 권역**입니다. 평균 회귀 본능에 의해 조만간 차익 실현 소나기가 올 수 있으니 보따리 쌀 준비를 하십시오." if bb_pos=="🔥 폭주" else \
                          f"● 하단 성벽이 무너진 **공포 구간**입니다. 투매 비명소리가 잦아들 때까지 절대 칼날을 잡지 마십시오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-status' style='color:{bb_color};'>{bb_pos}</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2: # RSI
                r_stat = "👺 불지옥" if rsi_val > 65 else "🧊 냉골" if rsi_val < 35 else "미지근"
                r_diag = f"● 온도 {rsi_val:.2f}로 **탐욕의 불지옥** 직전입니다. 남들이 환호할 때 냉정하게 분할 매도로 수익을 확정 지으십시오." if r_stat=="👺 불지옥" else \
                         f"● 온도 {rsi_val:.2f}의 **냉골 상태**입니다. 지수가 30 근처까지 완전히 식어버릴 때까지 낚싯대만 던져두고 기다리십시오." if r_stat=="🧊 냉골" else \
                         f"● 매수와 매도가 팽팽한 **줄다리기** 중입니다. 방향성 없는 싸움에 끼어들어 수수료만 버리지 마십시오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams %R
                w_status = "🧨 광기폭발" if will_val > -35 else "🏳️ 개미항복" if will_val < -65 else "중간지대"
                w_diag = f"● **불나방 광기(-20↑)** 직전입니다! 지수 {will_val:.2f}는 천장 근처이니 추격하지 말고 후퇴를 준비하십시오." if will_val > -35 else \
                         f"● **항복 지점(-75↓)** 근처입니다. 지수 {will_val:.2f}로 바닥권이니 이제 분할 매수 보따리를 푸십시오." if will_val < -65 else \
                         f"● 현재 지수 {will_val:.2f}로 **안개 속**입니다. 방향이 정해질 때까지 자중하며 째려만 보십시오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                macd_status = "▲ 상승엔진" if m_l > s_l else "▼ 하강엔진"
                macd_diag = f"● **상승 엔진**이 힘차게 돌고 있으나, 상단 성벽 저항을 이겨내는지 확인하며 진격 수위를 조절하십시오." if m_l > s_l else \
                           f"● **하강 엔진**으로 역회전 중입니다. 섣부른 진격보다는 포구에 정박하여 폭풍우가 지나가길 기다리는 게 상책입니다."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{macd_status}</p><p class='ind-diag'>{macd_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"오류: {e}")
