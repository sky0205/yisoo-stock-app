import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 디자인 (모바일 최적화 및 지수 설명 칸 유지)
st.set_page_config(page_title="v36056 냉정진단기 Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    
    .header-container { background-color: #0D47A1; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border-bottom: 4px solid #1565C0; }
    .main-title { font-size: 24px !important; color: #FFFFFF !important; margin: 0; }
    
    .global-unified-box { background-color: #263238; color: #FFFFFF; padding: 20px; border-radius: 12px; border: 2px solid #455A64; margin-bottom: 20px; }
    .global-header { font-size: 18px !important; color: #81D4FA !important; border-bottom: 1px solid #546E7A; padding-bottom: 8px; margin-bottom: 10px; }
    .global-item-text { font-size: 15px !important; margin-bottom: 5px; }
    .global-item-label { color: #B0BEC5 !important; }
    
    .volume-box-unified { background-color: #E3F2FD; padding: 20px; border-radius: 12px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    
    .unified-strategy-box { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 4px solid #D32F2F; margin: 15px 0; }
    .diagnosis-content { font-size: 16px !important; color: #B71C1C !important; line-height: 1.6; background-color: #FFF8F1; padding: 15px; border-radius: 8px; border-left: 8px solid #D32F2F; margin-bottom: 12px; }
    
    .price-wall-container { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border: 3px solid #1E88E5; margin-bottom: 20px; }
    .price-card { background-color: #F8F9FA; padding: 12px; border-radius: 10px; border: 1.5px solid #CFD8DC; text-align: center; }
    
    .ind-box { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border: 2px solid #90A4AE; min-height: 480px; margin-bottom: 15px; }
    .ind-title { font-size: 18px !important; color: #1976D2 !important; border-bottom: 1px solid #EEEEEE; padding-bottom: 8px; margin-bottom: 10px; }
    .ind-value { font-size: 38px !important; color: #B71C1C !important; text-align: center; display: block; margin: 8px 0; }
    .ind-diag { font-size: 14px !important; color: #333333 !important; line-height: 1.7; background-color: #FDFDFD; padding: 12px; border-radius: 5px; border-left: 6px solid #D32F2F; }
    
    .stock-header { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border-left: 8px solid #1E88E5; margin-bottom: 15px; }
    .val-main { font-size: 24px !important; color: #D32F2F !important; display: block; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-container'><p class='main-title'>👴 이수할아버지 냉정 진단기 v36056</p></div>", unsafe_allow_html=True)

# 0. 글로벌 전황 보고 (분석 내용 보완)
def get_global_data(ticker):
    try:
        g_df = yf.download(ticker, period="5d", progress=False)
        if not g_df.empty:
            curr = g_df['Close'].iloc[-1].item()
            prev = g_df['Close'].iloc[-2].item()
            pct = ((curr - prev) / prev) * 100
            return f"{curr:,.2f}", pct
        return "장부 지연", 0
    except: return "통신 오류", 0

n_v, n_p = get_global_data("^IXIC"); s_v, s_p = get_global_data("^GSPC"); t_v, t_p = get_global_data("^TNX")

st.markdown(f"""
    <div class='global-unified-box'>
        <div class='global-header'>🌎 0. 글로벌 전황 통합 보고</div>
        <div style='display: flex; flex-wrap: wrap; justify-content: space-around; text-align: center;'>
            <div class='global-item-text'><span class='global-item-label'>나스닥(NASDAQ):</span> <span style='color:{"#EF5350" if n_p > 0 else "#42A5F5"};'>{n_v} ({n_p:+.2f}%)</span></div>
            <div class='global-item-text'><span class='global-item-label'>S&P 500:</span> <span style='color:{"#EF5350" if s_p > 0 else "#42A5F5"};'>{s_v} ({s_p:+.2f}%)</span></div>
            <div class='global-item-text'><span class='global-item-label'>미국채 10년 금리:</span> <span style='color:{"#EF5350" if t_p > 0 else "#42A5F5"};'>{t_v} ({t_p:+.2f}%)</span></div>
        </div>
        <hr style='border:1px dashed #546E7A; margin: 15px 0;'>
        <div style='font-size:16px; color:#CFD8DC; line-height:1.6;'>
            <b>👴 냉정 평가:</b> 미장 지수는 거품 위에서 줄타기 중이고, 국채 금리는 언제든 우리 목을 겨눌 비수가 될 수 있네. 국장은 사지가 묶인 격이니 절대 섣불리 진격하지 마시게.
        </div>
    </div>
    """, unsafe_allow_html=True)

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365)
        if symbol.isdigit():
            df = fdr.DataReader(symbol, start_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            currency, fmt, diff_fmt = "원", ",.0f", "+,.0f" 
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            name = ticker.info.get('shortName', symbol); currency, fmt, diff_fmt = "$", ",.2f", "+,.2f"
        
        if not df.empty:
            p, prev_p = float(df['Close'].iloc[-1]), float(df['Close'].iloc[-2]); diff = p - prev_p
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if (loss.iloc[-1] != 0) else 100
            h14, l14 = df['High'].rolling(window=14).max().iloc[-1], df['Low'].rolling(window=14).min().iloc[-1]
            will_val = (h14 - p) / (h14 - l14) * -100 if (h14 - l14) != 0 else 0
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            st.markdown(f"<div class='stock-header'><p style='font-size:20px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:26px; color:{'#D32F2F' if diff > 0 else '#1976D2'}; margin:0;'>{format(p, fmt)} {currency} <span style='font-size:16px;'>({format(diff, diff_fmt)})</span></p></div>", unsafe_allow_html=True)

            buy_score = sum([p <= low_b * 1.03, rsi_val <= 35, will_val <= -75]); sell_score = sum([p >= up_b * 0.99, rsi_val >= 65, will_val >= -25])
            sig, color = ("🔴 매수권 진입", "#D32F2F") if buy_score >= 2 else ("🟢 매도권 진입", "#388E3C") if sell_score >= 2 else ("🟡 관망 및 대기", "#FBC02D")
            st.markdown(f"<div style='padding:15px; border-radius:10px; text-align:center; background-color:{color}; margin-bottom:15px;'><span style='font-size:28px; color:white;'>{sig}</span></div>", unsafe_allow_html=True)

            # 1. 거래량 전황
            v_ratio = (df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()) * 100
            if p > prev_p: v_advice = "📈 <b>주포의 진격:</b> 거래량이 실린 상승일세. 외인/기관이 벽을 뚫고 있으니 기세가 살아있구먼." if v_ratio > 150 else "🚨 <b>가짜 축제:</b> 거래량 없이 가격만 올렸어. 개미 꼬시는 함정이니 절대 쫓지 마셔." if v_ratio < 80 else "⏳ <b>간보기 상승:</b> 적당한 거래량으로 눈치 보는 중이야."
            else: v_advice = "⚠️ <b>도살장 입구:</b> 거래량 터진 하락이야. 주포들이 보따리 쌌으니 지하실 구경하기 싫으면 엎드리셔." if v_ratio > 150 else "💤 <b>무관심 하락:</b> 파는 놈도 사는 놈도 없어. 매수세가 마른 형국이니 바닥 성벽만 째려보게나." if v_ratio < 80 else "📉 <b>계단식 하락:</b> 야금야금 물량이 쏟아지고 있구먼."
            
            st.markdown(f"<div class='volume-box-unified'><div style='font-size:20px; color:#0D47A1; margin-bottom:8px;'>📊 1. 거래량 전황: {v_ratio:.1f}%</div><div style='font-size:15px; line-height:1.6;'>{v_advice}</div></div>", unsafe_allow_html=True)

            # 2. 필살 전략 + 냉정 진단
            st.markdown(f"""
                <div class='unified-strategy-box'>
                    <div style='font-size:20px; color:#D32F2F; border-bottom:2px solid #FFEBEE; padding-bottom:8px; margin-bottom:12px;'>⚔️ 2. 필살 대응 전략 및 냉정 진단</div>
                    <div class='diagnosis-content'>
                        <b>⚠️ [냉정 진단]:</b> 현재 주가는 볼린저 중앙선({format(mid_line, fmt)}){'을 하회하여 하단 성벽으로 끌려가는 중일세.' if p < mid_line * 0.97 else ' 위에서 알짱거리지만 데드 캣 바운스일 뿐이야.' if p > mid_line * 1.03 else ' 근처에서 눈치만 보며 미지적대고 있구먼.'} RSI <b>{rsi_val:.1f}</b>는 거품이 덜 빠졌음을 뜻해.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 3. 매수매도 성벽
            st.markdown("<div class='price-wall-container'><div style='font-size:18px; color:#1E88E5; margin-bottom:12px;'>🛡️ 3. 매수 매도 성벽 (Price Wall)</div>", unsafe_allow_html=True)
            cw1, cw2, cw3 = st.columns(3)
            with cw1: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>⚖️ 공략(하단)</p><span class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</span></div>", unsafe_allow_html=True)
            with cw2: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>🎯 수확(상단)</p><span class='val-main' style='color:#D32F2F;'>{format(up_b, fmt)}</span></div>", unsafe_allow_html=True)
            with cw3: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>🛡️ 성벽(93%)</p><span class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 4. 네 기둥 지수 상세 진단 (보강된 설명 유지)
            st.subheader("🏗️ 4. 네 기둥 지수 상세 진단")
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                if p <= low_b * 1.03: bb_txt = "⚠️ 하단 성벽 바짝 붙었구먼! 비명이 들릴 때까지 기다려."
                elif p < mid_line * 0.97: bb_txt = "📉 중앙선 뚫리고 하단 성벽으로 끌려가는 중이야."
                elif p > mid_line * 1.03: bb_txt = "📈 중앙선 위에서 기세 타나 가짜 상승을 경계해."
                else: bb_txt = "⚖️ 중앙선 근처에서 눈치만 보며 미지적대고 있네."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Bollinger (기세)</p><span style='font-size:13px; color:#546E7A;'>[중앙선 가격]</span><span class='ind-value'>{format(mid_line, fmt)}</span><div class='ind-diag'>● <b>판독:</b> {bb_txt}<br>볼린저는 주가의 '변동 폭'이네. 하단({format(low_b, fmt)})에 붙었다는 건 과매도 상태지만, 밴드가 벌어지면 지옥문이 열리는 격이니 성벽 사수를 독하게 확인하시게.</div></div>", unsafe_allow_html=True)
            with i2: # RSI
                if rsi_val < 35: r_txt = "🧊 냉골 공포 구간이야. 낚싯줄 던질 준비하게."
                elif rsi_val > 65: r_txt = "👺 불지옥 탐욕 권역일세. 보따리 쌀 준비하게."
                else: r_txt = "미지근한 줄다리기 중일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ RSI (온도)</p><span style='font-size:13px; color:#546E7A;'>[현재 지수]</span><span class='ind-value'>{rsi_val:.1f}</span><div class='ind-diag'>● <b>판독:</b> {r_txt}<br>지수가 50을 못 넘으면 힘이 없는 법이야. 관세 리스크 등 부정적 지표가 짓누르고 있다면 RSI가 30 근처로 식을 때까지 총을 아껴야 화상을 안 입네.</div></div>", unsafe_allow_html=True)
            with i3: # Williams
                if will_val < -80: w_txt = "🏳️ 개미 항복 지점일세. 매집 시기야."
                elif will_val > -20: w_txt = "🧨 광기 폭발! 상투 잡지 마셔."
                else: w_txt = "중간 지대에서 간 보는 중이야."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Williams (심리)</p><span style='font-size:13px; color:#546E7A;'>[현재 지수]</span><span class='ind-value'>{will_val:.1f}</span><div class='ind-diag'>● <b>판독:</b> {w_txt}<br>윌리엄은 바닥을 귀신같이 잡아내지. -80 아래 심해로 잠수할 때가 진짜 개미들이 털리는 시점이니, 그 비명 소리가 들릴 때 장부를 다시 펼치시게.</div></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_txt = "🚀 상승 엔진 가동 중일세." if m_l > s_l else "💣 하강 엔진 가동 중이야."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ MACD (추세)</p><span style='font-size:13px; color:#546E7A;'>[엔진 상태]</span><span class='ind-value' style='font-size:26px !important;'>{'▲ 상승' if m_l > s_l else '▼ 하락'}</span><div class='ind-diag'>● <b>판독:</b> {m_txt}<br>엔진이 역회전 중일 때는 아무리 좋은 기사가 나도 믿지 마셔. 추세 마디가 바뀌고 시그널선 위로 올라타야 비로소 배가 움직이는 법일세.</div></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"장부 오류: {e}")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 최종 정밀 보완본")
