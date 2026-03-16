import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 디자인 (제목 강조 및 글로벌 통합형)
st.set_page_config(page_title="v36056 냉정진단기 Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    /* 제목 글씨 크게 */
    .main-title { font-size: 50px !important; color: #0D47A1 !important; margin-bottom: 20px; text-align: center; border-bottom: 5px solid #1E88E5; padding-bottom: 10px; }
    /* 글로벌 전황 하나로 통합 */
    .global-unified-box { background-color: #263238; color: #FFFFFF; padding: 25px; border-radius: 15px; border: 3px solid #455A64; margin-bottom: 25px; }
    .global-item { font-size: 24px !important; margin-bottom: 10px; }
    /* 나머지 스타일 유지 */
    .stock-header { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 60px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .diagnosis-box { border: 2px solid #D32F2F; padding: 20px; border-radius: 10px; background-color: #FFF8F1; margin-bottom: 20px; }
    .price-card { background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 3px solid #CFD8DC; text-align: center; margin-bottom: 20px; }
    .val-main { font-size: 42px !important; color: #D32F2F !important; display: block; }
    .ind-box { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 420px; margin-bottom: 15px; }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 12px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .ind-value { font-size: 60px !important; color: #B71C1C !important; text-align: center; display: block; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>👴 이수할아버지 냉정 진단기 v36056</div>", unsafe_allow_html=True)

# 2. 글로벌 전황 통합 보고 (하나의 박스로 구현)
def get_global_data(ticker):
    try:
        g_df = yf.download(ticker, period="2d", progress=False)
        curr = g_df['Close'].iloc[-1].item()
        prev = g_df['Close'].iloc[-2].item()
        pct = ((curr - prev) / prev) * 100
        return curr, pct
    except: return 0, 0

nas_val, nas_pct = get_global_data("^IXIC")
sp_val, sp_pct = get_global_data("^GSPC")
tnx_val, tnx_pct = get_global_data("^TNX")

st.markdown(f"""
    <div class='global-unified-box'>
        <h2 style='color:#81D4FA; border-bottom:2px solid #546E7A; padding-bottom:10px;'>🌎 0. 글로벌 전황 통합 보고</h2>
        <div style='display: flex; justify-content: space-around; padding-top:15px;'>
            <div class='global-item'>나스닥(NASDAQ): <span style='color:{"#EF5350" if nas_pct > 0 else "#42A5F5"};'>{nas_val:,.2f} ({nas_pct:+.2f}%)</span></div>
            <div class='global-item'>S&P 500: <span style='color:{"#EF5350" if sp_pct > 0 else "#42A5F5"};'>{sp_val:,.2f} ({sp_pct:+.2f}%)</span></div>
            <div class='global-item'>미국채 10년 금리: <span style='color:{"#EF5350" if tnx_pct > 0 else "#42A5F5"};'>{tnx_val:,.2f} ({tnx_pct:+.2f}%)</span></div>
        </div>
        <hr style='border:1px dashed #546E7A;'>
        <div style='font-size:18px; color:#CFD8DC;'>
            <b>👴 냉정 평가:</b> 미장 거품이 여전하고 금리가 비수가 되어 돌아오니, 국장은 사지가 마비된 형국일세. 섣부른 낙관은 금물이야.
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
            currency = "원"; fmt = ",.0f"; diff_fmt = "+,.0f" 
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            name = ticker.info.get('shortName', symbol); currency = "$"; fmt = ",.2f"; diff_fmt = "+,.2f"
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2]); diff = p - prev_p
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if (loss.iloc[-1] != 0) else 100
            h14 = df['High'].rolling(window=14).max().iloc[-1]; l14 = df['Low'].rolling(window=14).min().iloc[-1]
            will_val = (h14 - p) / (h14 - l14) * -100 if (h14 - l14) != 0 else 0
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # [종목 헤더]
            color_p = "#D32F2F" if diff > 0 else "#1976D2"
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:45px; color:{color_p}; margin:0;'>{format(p, fmt)} {currency} <span style='font-size:28px;'> (전일비: {format(diff, diff_fmt)})</span></p></div>", unsafe_allow_html=True)

            # [신호등]
            buy_score = sum([p <= low_b, rsi_val <= 35, will_val <= -75])
            sell_score = sum([p >= up_b, rsi_val >= 65, will_val >= -20])
            if buy_score >= 2: sig, color = "🔴 매수권 진입", "#D32F2F"
            elif sell_score >= 2: sig, color = "🟢 매도권 진입", "#388E3C"
            else: sig, color = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {color};'><span class='signal-text'>{sig}</span></div>", unsafe_allow_html=True)

            # 1. 거래량 전황
            v_ratio = (df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()) * 100
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; color:#0D47A1; margin-bottom:10px;'>📊 1. 거래량 전황: {v_ratio:.1f}%</div><div style='font-size:20px; line-height:1.6; background-color:white; padding:12px; border-radius:8px; border-left:6px solid #1E88E5;'>{'🚨 가짜 상승! 거래량 없는 반등에 속지 마셔.' if p > prev_p and v_ratio < 100 else '⚠️ 물량이 쏟아지니 성벽 사수를 보셔.' if p < prev_p and v_ratio > 150 else '⏳ 눈치싸움 중이니 대기하셔.'}</div></div>", unsafe_allow_html=True)

            # 2. 필살 대응 전략
            st.markdown("<div class='trend-card'><div class='trend-title'>⚔️ 2. 필살 대응 전략</div>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='diagnosis-box'>
                <p style='font-size:24px; color:#D32F2F; margin-bottom:10px;'>⚠️ [냉정 진단]</p>
                <p style='font-size:22px; line-height:1.7;'>
                냉정 진단: 현재 주가가 Bollinger Band 중앙선(<b>{format(mid_line, fmt)}</b>) 위에서 알짱거리지만, 
                이는 추세 전환이 아니라 <b>'데드 캣 바운스'</b>의 전형입니다. 
                RSI 지표가 <b>{rsi_val:.1f}</b>로 여전히 미지근하다는 것은, 시장에 낀 거품이 다 빠지지 않았음을 뜻합니다.
                </p>
                <hr style='border:1px dashed #D32F2F;'>
                <p style='font-size:21px;'>● <b>필살 지침:</b> 가짜 반등에 속지 마시게. 지표가 바닥 심해로 잠수할 때까지 독하게 기다려야 하네.</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 3. 매수 매도 성벽
            st.subheader("🛡️ 3. 매수 매도 성벽")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p style='font-size:22px;'>⚖️ 공략 대기선(하단)</p><span class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</span></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p style='font-size:22px;'>🎯 수확 목표선(상단)</p><span class='val-main' style='color:#D32F2F;'>{format(up_b, fmt)}</span></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p style='font-size:22px;'>🛡️ 방어 성벽 (93% 선)</p><span class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</span></div>", unsafe_allow_html=True)

            # 4. 네 기둥 지수 상세 진단
            st.subheader("🏗️ 4. 네 기둥 지수 상세 진단")
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Bollinger Bands</p><span class='ind-value'>{format(mid_line, fmt)}</span><p class='ind-diag'>● 중앙선 {'위에서 기세는 있으나' if p > mid_line else '아래로 꺾여 기운이 없구먼.'} 상단 성벽({format(up_b, fmt)}) 돌파 여부를 보게나.</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ RSI (상대강도)</p><span class='ind-value'>{rsi_val:.1f}</span><p class='ind-diag'>● 현재 수치 <b>{rsi_val:.1f}</b>일세. 30 이하로 식을 때까지 총을 아끼게. 과열권 진입 시엔 보따리 쌀 준비를 하셔.</p></div>", unsafe_allow_html=True)
            with i3: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Williams %R</p><span class='ind-value'>{will_val:.1f}</span><p class='ind-diag'>● 수치 <b>{will_val:.1f}</b>는 개미들의 항복 지점을 보여주네. -80 아래로 잠수할 때가 진짜 바닥일세.</p></div>", unsafe_allow_html=True)
            with i4: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ MACD (추세엔진)</p><span class='ind-value' style='font-size:45px !important;'>{'▲ 상승' if m_l > s_l else '▼ 하락'}</span><p class='ind-diag'>● 엔진이 {'정방향' if m_l > s_l else '역회전'} 중이야. 추세 마디가 바뀌는 맥점을 독하게 째려보게나.</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"장부를 불러올 수 없구먼 (오류: {e})")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 최종 양식(글로벌 통합+제목강조) 적용")
