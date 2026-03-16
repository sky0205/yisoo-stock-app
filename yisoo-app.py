import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 디자인 (모바일 최적화 및 폰트 축소)
st.set_page_config(page_title="v36056 냉정진단기 Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    
    /* 1. 메인 제목: 모바일 배려하여 축소 */
    .header-container {
        background-color: #0D47A1;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 4px solid #1565C0;
    }
    .main-title { 
        font-size: 28px !important; 
        color: #FFFFFF !important; 
        margin: 0;
    }
    
    /* 2. 글로벌 전황 통합 박스 (이름표 및 크기 조절) */
    .global-unified-box { 
        background-color: #263238; 
        color: #FFFFFF; 
        padding: 15px; 
        border-radius: 10px; 
        border: 2px solid #455A64; 
        margin-bottom: 20px; 
    }
    .global-header { 
        font-size: 18px !important; 
        color: #81D4FA !important; 
        border-bottom: 1px solid #546E7A; 
        padding-bottom: 8px; 
        margin-bottom: 10px; 
    }
    .global-item-text { font-size: 16px !important; margin-bottom: 5px; }
    .global-item-label { color: #B0BEC5 !important; }
    
    /* 3. 전략 + 진단 통합 박스 */
    .unified-strategy-box { 
        background-color: #FFFFFF; 
        padding: 20px; 
        border-radius: 12px; 
        border: 4px solid #D32F2F; 
        margin: 15px 0; 
    }
    .strategy-title { font-size: 22px !important; color: #D32F2F !important; border-bottom: 2px solid #FFEBEE; padding-bottom: 8px; margin-bottom: 15px; }
    .diagnosis-content { 
        font-size: 17px !important; color: #B71C1C !important; line-height: 1.6; 
        background-color: #FFF8F1; padding: 15px; border-radius: 8px; 
        border-left: 8px solid #D32F2F; margin-bottom: 15px; 
    }
    
    /* 기타 수치들 크기 조절 */
    .stock-header { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border-left: 8px solid #1E88E5; margin-bottom: 15px; }
    .signal-box { padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
    .signal-text { font-size: 32px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .vol-box { background-color: #E3F2FD; padding: 20px; border-radius: 12px; border: 3px solid #1E88E5; margin-bottom: 20px; }
    .val-main { font-size: 30px !important; color: #D32F2F !important; display: block; }
    .ind-box { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 2px solid #90A4AE; min-height: 350px; margin-bottom: 10px; }
    .ind-value { font-size: 40px !important; color: #B71C1C !important; text-align: center; display: block; margin: 10px 0; }
    .ind-diag { font-size: 16px !important; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

# 1. 제목 출력
st.markdown("<div class='header-container'><p class='main-title'>👴 이수할아버지 냉정 진단기 v36056</p></div>", unsafe_allow_html=True)

# 2. 글로벌 전황 데이터 수집
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
        <div class='global-header'>🌎 0. 글로벌 전황 통합 보고</div>
        <div class='global-item-text'><span class='global-item-label'>나스닥(NASDAQ):</span> <span style='color:{"#EF5350" if nas_pct > 0 else "#42A5F5"};'>{nas_val:,.2f} ({nas_pct:+.2f}%)</span></div>
        <div class='global-item-text'><span class='global-item-label'>S&P 500:</span> <span style='color:{"#EF5350" if sp_pct > 0 else "#42A5F5"};'>{sp_val:,.2f} ({sp_pct:+.2f}%)</span></div>
        <div class='global-item-text'><span class='global-item-label'>미국채 10년 금리:</span> <span style='color:{"#EF5350" if tnx_pct > 0 else "#42A5F5"};'>{tnx_val:,.2f} ({tnx_pct:+.2f}%)</span></div>
        <hr style='border:1px dashed #546E7A; margin: 10px 0;'>
        <div style='font-size:15px; color:#CFD8DC;'>
            <b>👴 평가:</b> 미장은 거품 위태롭고 금리는 비수가 될 수 있네. 국장은 사지 묶인 격이니 섣부른 낙관 금물일세.
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

            # 헤더
            color_p = "#D32F2F" if diff > 0 else "#1976D2"
            st.markdown(f"<div class='stock-header'><p style='font-size:24px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:32px; color:{color_p}; margin:0;'>{format(p, fmt)} {currency} <span style='font-size:20px;'> ({format(diff, diff_fmt)})</span></p></div>", unsafe_allow_html=True)

            # 신호등
            buy_score = sum([p <= low_b, rsi_val <= 35, will_val <= -75]); sell_score = sum([p >= up_b, rsi_val >= 65, will_val >= -20])
            if buy_score >= 2: sig, color = "🔴 매수권 진입", "#D32F2F"
            elif sell_score >= 2: sig, color = "🟢 매도권 진입", "#388E3C"
            else: sig, color = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {color};'><span class='signal-text'>{sig}</span></div>", unsafe_allow_html=True)

            # 1. 거래량
            v_ratio = (df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()) * 100
            st.markdown(f"<div class='vol-box'><div style='font-size:22px; color:#0D47A1; margin-bottom:8px;'>📊 1. 거래량 전황: {v_ratio:.1f}%</div><div style='font-size:16px;'>{'🚨 가짜 상승! 속지 마셔.' if p > prev_p and v_ratio < 100 else '⚠️ 물량 쏟아지니 성벽 보셔.' if p < prev_p and v_ratio > 150 else '⏳ 대기하셔.'}</div></div>", unsafe_allow_html=True)

            # 2. 필살 대응 전략 및 냉정 진단 (통합 박스)
            st.markdown(f"""
                <div class='unified-strategy-box'>
                    <div class='strategy-title'>⚔️ 2. 필살 대응 전략 및 냉정 진단</div>
                    <div class='diagnosis-content'>
                        <b>⚠️ [냉정 진단]:</b> 주가가 중앙선(<b>{format(mid_line, fmt)}</b>) 위이나, <b>'데드 캣 바운스'</b>일 뿐일세. RSI <b>{rsi_val:.1f}</b>는 거품 여전함을 뜻해.
                    </div>
                    <div style='font-size:17px; color:#333;'>● <b>지침:</b> 속지 마시게. 지표 잠수할 때까지 독하게 기다려야 하네.</div>
                </div>
                """, unsafe_allow_html=True)

            # 3. 매수 매도 성벽
            st.subheader("🛡️ 3. 매수 매도 성벽")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p style='font-size:18px;'>⚖️ 공략(하단)</p><span class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</span></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p style='font-size:18px;'>🎯 수확(상단)</p><span class='val-main' style='color:#D32F2F;'>{format(up_b, fmt)}</span></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p style='font-size:18px;'>🛡️ 성벽(93%)</p><span class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</span></div>", unsafe_allow_html=True)

            # 4. 네 기둥 지수 상세 진단
            st.subheader("🏗️ 4. 네 기둥 지수 상세 진단")
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Bollinger</p><span style='font-size:16px;'>[중앙선]</span><span class='ind-value'>{format(mid_line, fmt)}</span><p class='ind-diag'>● 중앙선 {'위' if p > mid_line else '아래'}일세.</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ RSI</p><span style='font-size:16px;'>[지수]</span><span class='ind-value'>{rsi_val:.1f}</span><p class='ind-diag'>● 강도 <b>{rsi_val:.1f}</b>일세. 30 대기하게.</p></div>", unsafe_allow_html=True)
            with i3: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Williams</p><span style='font-size:16px;'>[지수]</span><span class='ind-value'>{will_val:.1f}</span><p class='ind-diag'>● 수치 <b>{will_val:.1f}</b>, -80 대기하게.</p></div>", unsafe_allow_html=True)
            with i4: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ MACD</p><span style='font-size:16px;'>[엔진]</span><span class='ind-value' style='font-size:30px !important;'>{'▲ 상승' if m_l > s_l else '▼ 하락'}</span><p class='ind-diag'>● 엔진 {'정방향' if m_l > s_l else '역회전'} 중일세.</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"장부 오류: {e}")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 모바일 최적화본")
