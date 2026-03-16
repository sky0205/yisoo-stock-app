import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 디자인 (가독성 및 통합성 극대화)
st.set_page_config(page_title="v36056 냉정진단기 Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    
    /* 1. 메인 제목: 장부의 얼굴 (가장 크고 시원하게) */
    .header-container {
        background-color: #0D47A1;
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 10px solid #1565C0;
    }
    .main-title { 
        font-size: 65px !important; 
        color: #FFFFFF !important; 
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* 2. 글로벌 전황 통합 박스: 깔끔하게 정돈 */
    .global-unified-box { 
        background-color: #263238; 
        color: #FFFFFF; 
        padding: 30px; 
        border-radius: 15px; 
        border: 4px solid #455A64; 
        margin-bottom: 30px; 
    }
    .global-header { 
        font-size: 28px !important; 
        color: #81D4FA !important; 
        border-bottom: 2px solid #546E7A; 
        padding-bottom: 15px; 
        margin-bottom: 20px; 
    }
    .global-item-text { font-size: 26px !important; }
    
    /* 3. 전략 + 진단 통합 박스: 단단한 무쇠 박스 */
    .unified-strategy-box { 
        background-color: #FFFFFF; 
        padding: 40px; 
        border-radius: 20px; 
        border: 7px solid #D32F2F; 
        margin: 25px 0; 
        box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
    }
    .strategy-title { 
        font-size: 36px !important; 
        color: #D32F2F !important; 
        border-bottom: 4px solid #FFEBEE; 
        padding-bottom: 15px; 
        margin-bottom: 25px; 
    }
    .diagnosis-content { 
        font-size: 25px !important; 
        color: #B71C1C !important; 
        line-height: 1.8; 
        background-color: #FFF8F1; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 12px solid #D32F2F; 
        margin-bottom: 25px; 
    }
    
    /* 기타 스타일 유지 */
    .stock-header { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border-left: 12px solid #1E88E5; margin-bottom: 20px; }
    .signal-box { padding: 35px; border-radius: 20px; text-align: center; margin-bottom: 25px; }
    .signal-text { font-size: 65px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .vol-box { background-color: #E3F2FD; padding: 30px; border-radius: 15px; border: 5px solid #1E88E5; margin-bottom: 25px; }
    .price-card { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 4px solid #CFD8DC; text-align: center; }
    .val-main { font-size: 45px !important; color: #D32F2F !important; display: block; }
    .ind-box { background-color: #FFFFFF; padding: 30px; border-radius: 15px; border: 3px solid #90A4AE; min-height: 450px; }
    .ind-value { font-size: 65px !important; color: #B71C1C !important; text-align: center; display: block; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# 1. 메인 제목 출력
st.markdown("<div class='header-container'><p class='main-title'>👴 이수할아버지 냉정 진단기 v36056</p></div>", unsafe_allow_html=True)

# 2. 글로벌 전황 데이터 수집 및 출력
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
        <div style='display: flex; justify-content: space-around; align-items: center; padding: 10px 0;'>
            <div class='global-item-text'>나스닥(NASDAQ): <span style='color:{"#EF5350" if nas_pct > 0 else "#42A5F5"};'>{nas_val:,.2f} ({nas_pct:+.2f}%)</span></div>
            <div class='global-item-text'>S&P 500: <span style='color:{"#EF5350" if nas_pct > 0 else "#42A5F5"};'>{sp_val:,.2f} ({sp_pct:+.2f}%)</span></div>
            <div class='global-item-text'>미국채 10년 금리: <span style='color:{"#EF5350" if tnx_pct > 0 else "#42A5F5"};'>{tnx_val:,.2f} ({tnx_pct:+.2f}%)</span></div>
        </div>
        <hr style='border:1px dashed #546E7A; margin: 20px 0;'>
        <div style='font-size:20px; color:#CFD8DC; line-height:1.6;'>
            <b>👴 냉정 평가:</b> 미장 거품은 여전히 위태롭고, 금리라는 비수가 우리 목을 겨누고 있구먼. 국장은 사지가 묶인 격이니 절대 섣부른 낙관은 금물일세.
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
            st.markdown(f"<div class='stock-header'><p style='font-size:38px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:50px; color:{color_p}; margin:0;'>{format(p, fmt)} {currency} <span style='font-size:32px;'> (전일비: {format(diff, diff_fmt)})</span></p></div>", unsafe_allow_html=True)

            # [신호등]
            buy_score = sum([p <= low_b, rsi_val <= 35, will_val <= -75])
            sell_score = sum([p >= up_b, rsi_val >= 65, will_val >= -20])
            if buy_score >= 2: sig, color = "🔴 매수권 진입", "#D32F2F"
            elif sell_score >= 2: sig, color = "🟢 매도권 진입", "#388E3C"
            else: sig, color = "🟡 관망 및 대기", "#FBC02D"
            st.markdown(f"<div class='signal-box' style='background-color: {color};'><span class='signal-text'>{sig}</span></div>", unsafe_allow_html=True)

            # [1. 거래량 전황]
            v_ratio = (df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()) * 100
            st.markdown(f"<div class='vol-box'><div style='font-size:35px; color:#0D47A1; margin-bottom:12px;'>📊 1. 거래량 전황: {v_ratio:.1f}%</div><div style='font-size:22px; line-height:1.6; background-color:white; padding:15px; border-radius:10px; border-left:8px solid #1E88E5;'>{'🚨 가짜 상승! 거래량 없는 반등에 속지 마셔.' if p > prev_p and v_ratio < 100 else '⚠️ 물량이 쏟아지니 성벽 사수를 보셔.' if p < prev_p and v_ratio > 150 else '⏳ 눈치싸움 중이니 대기하셔.'}</div></div>", unsafe_allow_html=True)

            # [2. 필살 대응 전략 및 냉정 진단 통합 박스]
            st.markdown(f"""
                <div class='unified-strategy-box'>
                    <div class='strategy-title'>⚔️ 2. 필살 대응 전략 및 냉정 진단</div>
                    <div class='diagnosis-content'>
                        <b>⚠️ [냉정 진단]:</b> 현재 주가가 Bollinger Band 중앙선(<b>{format(mid_line, fmt)}</b>) 위에서 알짱거리지만, 
                        이는 추세 전환이 아니라 <b>'데드 캣 바운스'</b>의 전형입니다. 
                        RSI 지표가 <b>{rsi_val:.1f}</b>로 여전히 미지근하다는 것은, 시장에 낀 거품이 다 빠지지 않았음을 뜻합니다.
                    </div>
                    <div style='font-size:24px; line-height:1.8; color:#333;'>
                        ● <b>필살 지침:</b> 가짜 반등에 속지 마시게. 지표가 바닥 심해로 잠수하며 
                        개미들이 투항할 때까지 독하게 기다려야 하네. 지금은 <b>함정 수사</b>의 시간이야.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # [3. 매수 매도 성벽]
            st.subheader("🛡️ 3. 매수 매도 성벽")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p style='font-size:25px;'>⚖️ 공략 대기선(하단)</p><span class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</span></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p style='font-size:25px;'>🎯 수확 목표선(상단)</p><span class='val-main' style='color:#D32F2F;'>{format(up_b, fmt)}</span></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p style='font-size:25px;'>🛡️ 방어 성벽 (93% 선)</p><span class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</span></div>", unsafe_allow_html=True)

            # [4. 네 기둥 지수 상세 진단]
            st.subheader("🏗️ 4. 네 기둥 지수 상세 진단")
            i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Bollinger Bands</p><span class='ind-value'>{format(mid_line, fmt)}</span><p style='font-size:20px;'>● 중앙선 {'위에서 기세는 있으나' if p > mid_line else '아래로 꺾여 기운이 없구먼.'} 상단 성벽({format(up_b, fmt)}) 돌파 여부를 보게나.</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ RSI (상대강도)</p><span class='ind-value'>{rsi_val:.1f}</span><p style='font-size:20px;'>● 현재 수치 <b>{rsi_val:.1f}</b>일세. 30 이하로 식을 때까지 총을 아끼게.</p></div>", unsafe_allow_html=True)
            with i3: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Williams %R</p><span class='ind-value'>{will_val:.1f}</span><p style='font-size:20px;'>● 수치 <b>{will_val:.1f}</b>는 개미들의 항복 지점을 보여주네. -80 아래가 진짜 바닥일세.</p></div>", unsafe_allow_html=True)
            with i4: st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ MACD (추세엔진)</p><span class='ind-value' style='font-size:50px !important;'>{'▲ 상승' if m_l > s_l else '▼ 하락'}</span><p style='font-size:20px;'>● 엔진이 {'정방향' if m_l > s_l else '역회전'} 중이야. 맥점을 독하게 째려보게나.</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"장부를 불러올 수 없구먼 (오류: {e})")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 최종 정돈본 적용 완료")
