import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (어르신 전용 고대비 및 가독성 최적화)
st.set_page_config(page_title="이수할아버지 분석기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    
    /* 상단 헤더 */
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    
    /* 거래량 박스 */
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-main-text { font-size: 32px !important; color: #0D47A1 !important; margin-bottom: 10px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }

    /* 대형 신호등 */
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 65px !important; font-weight: 900 !important; color: #FFFFFF !important; }

    /* 필살 대응 전략 카드 */
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .trend-item { font-size: 23px !important; line-height: 2.0; margin-bottom: 12px; }
    .advice-highlight { color: #D32F2F !important; font-size: 26px !important; text-decoration: underline; }

    /* 가격 전략 카드 */
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .val-main { font-size: 32px !important; color: #333; }
    
    /* 지수 상세 박스 */
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 500px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-status { font-size: 32px !important; color: #D32F2F !important; margin-bottom: 10px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    </style>
    """, unsafe_allow_html=True)

st.title("👴 이수할아버지의 냉정 진단기 v36056")
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
            p = float(df['Close'].iloc[-1]); year_high = float(df['Close'].max()); year_low = float(df['Close'].min())
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # 거래량 분석
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            v_status = "🔥 거래폭발" if v_ratio >= 200 else "📈 거래증가" if v_ratio >= 120 else "💤 거래침체" if v_ratio <= 70 else "⚖️ 보통"

            # 지표 계산 로직
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
            h14 = df['High'].rolling(window=14).max().iloc[-1]; l14 = df['Low'].rolling(window=14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            up_b = df['MA20'].iloc[-1] + (df['Std'].iloc[-1] * 2); low_b = df['MA20'].iloc[-1] - (df['Std'].iloc[-1] * 2)

            # 신호등 점수 (냉정 진단 65 / -75 기준 적용)
            buy_score = sum([p <= low_b, rsi_val <= 35, will_val <= -75]); sell_score = sum([p >= up_b, rsi_val >= 65, will_val >= -20])
            is_new_high = p >= year_high * 0.98; is_new_low = p <= year_low * 1.02

            # 추세 진단 보완
            trend_desc = "횡보 및 안개 정국"
            if m_l > s_l and p > df['MA20'].iloc[-1]: trend_desc = "정배열 상승 가도"
            elif m_l < s_l and p < df['MA20'].iloc[-1]: trend_desc = "역배열 하락 늪"

            # 1~3. 상단 헤더, 거래량, 신호등 표시
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt)} {currency}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>● <b>진격 기준:</b> 200% 이상 폭발 시 세력 진입 간주 (추격 가능)<br>● <b>주의 사항:</b> 거래량 100% 미만인데 오르는 건 '가짜'이니 속지 마십시오.</div></div>", unsafe_allow_html=True)

            if buy_score >= 2: sig, color = "🔴 매수권 진입", "#D32F2F"
            elif sell_score >= 2: sig, color = "🟢 매도권 진입", "#388E3C"
            elif is_new_high: sig, color = "🔥 신고가 돌파", "#E65100"
            else: sig, color = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {color};'><span class='signal-text'>{sig}</span></div>", unsafe_allow_html=True)

            # 4. 실전 필살 대응 전략 (추세 보완)
            st.markdown(f"""<div class='trend-card'>
                <div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>● <b>추세 진단:</b> 현재 장부는 <span style='color:#D32F2F;'>{trend_desc}</span> 상태로 판독되구먼요.</div>
                <div class='trend-item'>● <b>수비 상태:</b> 성벽({format(defense_line, fmt)} {currency}) {'함락! 후퇴하십시오.' if p < defense_line else '사수 중입니다.'}</div>
                <div class='trend-item'>● <b>필살 조언:</b> <span class='advice-highlight'>{'⚠️ 신고가 추격 시: ' + format(p*0.95, fmt) + ' ' + currency + ' 이탈 시 손절!' if is_new_high else '📉 신저가 구간: ' + format(p, fmt) + ' ~ ' + format(year_low*0.95, fmt) + ' 사이 3회 분할 매수!' if is_new_low else '낚싯대만 던져두고 지표 바닥권을 기다리십시오.'}</span></div>
                </div>""", unsafe_allow_html=True)

            # 5. 가격 전략 카드
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선(매수)</p><p class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선(매도)</p><p class='val-main' style='color:#D32F2F;'>{format(up_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽 (방어선)</p><p class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</p></div>", unsafe_allow_html=True)

            # 6. 네 기둥 지수란 (심화 진단 적용)
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_pos = "🔥 폭주" if p>=up_b else "📉 추락" if p<=low_b else "⚖️ 눈치보기"
                bb_diag = f"● 성벽 중간에서 **방향성 탐색 중**입니다. 상단({format(up_b, fmt)}) 돌파 실패 시 실망 매물이 쏟아질 수 있으니 자중하십시오." if bb_pos=="⚖️ 눈치보기" else \
                          f"● 성벽 밖 **과열 권역**입니다. 평균 회귀 본능에 의해 곧 차익 실현 소나기가 올 수 있으니 보따리 쌀 준비를 하십시오." if bb_pos=="🔥 폭주" else \
                          f"● 하단 성벽이 무너진 **공포 구간**입니다. 투매 비명소리가 잦아들 때까지 절대 칼날을 잡지 마십시오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-status'>{bb_pos}</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)

            with i2: # RSI
                r_stat = "👺 불지옥" if rsi_val > 65 else "🧊 냉골" if rsi_val < 35 else "미지근"
                r_diag = f"● 온도 {rsi_val:.2f}로 **탐욕의 불지옥** 직전입니다. 남들이 환호할 때 냉정하게 분할 매도로 수익을 확정 지으십시오." if r_stat=="👺 불지옥" else \
                         f"● 온도 {rsi_val:.2f}의 **냉골 상태**입니다. 지수가 30 근처까지 완전히 식어버릴 때까지 낚싯대만 던져두고 기다리십시오." if r_stat=="🧊 냉골" else \
                         f"● 매수와 매도가 팽팽한 **줄다리기** 중입니다. 방향성 없는 싸움에 끼어들어 수수료만 버리지 마십시오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)

            with i3: # Williams %R
                w_status = "🧨 광기폭발" if will_val > -20 else "🏳️ 개미항복" if will_val < -75 else "추락중"
                w_diag = f"● **불나방 광기**가 절정입니다! 세력들이 물량을 떠넘길 채비를 하고 있으니 뒤도 돌아보지 말고 후퇴하십시오." if w_status=="🧨 광기폭발" else \
                         f"● 드디어 **개미들이 항복**한 바닥권입니다. 공포가 극에 달했을 때가 기회이니 분할 매수 보따리를 푸십시오." if w_status=="🏳️ 개미항복" else \
                         f"● 지표가 **자유낙하 중**입니다. 어설픈 낙주 매매는 자살행위이니 비명소리가 시장에 가득 찰 때까지 기다리십시오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)

            with i4: # MACD
                macd_status = "▲ 상승엔진" if m_l > s_l else "▼ 하강엔진"
                macd_diag = f"● **상승 엔진**이 힘차게 돌고 있으나, 상단 성벽 저항을 이겨내는지 확인하며 진격 수위를 조절하십시오." if m_l > s_l else \
                           f"● **하강 엔진**으로 역회전 중입니다. 섣부른 진격보다는 포구에 정박하여 폭풍우가 지나가길 기다리는 게 상책입니다."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{macd_status}</p><p class='ind-diag'>{macd_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"오류: {e}")
