import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 디자인 (모바일 최적화 및 시인성 보강)
st.set_page_config(page_title="v36056 냉정진단기 Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    
    /* 제목 및 글로벌 통합 */
    .header-container { background-color: #0D47A1; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border-bottom: 4px solid #1565C0; }
    .main-title { font-size: 24px !important; color: #FFFFFF !important; margin: 0; }
    
    /* 글로벌 전황 통합 박스 */
    .global-unified-box { background-color: #263238; color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #455A64; margin-bottom: 20px; }
    .global-header { font-size: 18px !important; color: #81D4FA !important; border-bottom: 1px solid #546E7A; padding-bottom: 8px; margin-bottom: 10px; }
    .global-item-text { font-size: 15px !important; margin-bottom: 5px; }
    .global-item-label { color: #B0BEC5 !important; }
    
    /* 2. 필승전략 + 냉정진단 통합 박스 */
    .unified-strategy-box { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 4px solid #D32F2F; margin: 15px 0; }
    .strategy-title { font-size: 20px !important; color: #D32F2F !important; border-bottom: 2px solid #FFEBEE; padding-bottom: 8px; margin-bottom: 12px; }
    .diagnosis-content { font-size: 16px !important; color: #B71C1C !important; line-height: 1.6; background-color: #FFF8F1; padding: 15px; border-radius: 8px; border-left: 8px solid #D32F2F; margin-bottom: 12px; }
    
    /* 3. 매수매도 성벽 박스 */
    .price-wall-container { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border: 3px solid #1E88E5; margin-bottom: 20px; }
    .price-card { background-color: #F8F9FA; padding: 12px; border-radius: 10px; border: 1.5px solid #CFD8DC; text-align: center; }
    
    /* 4. 네 기둥 지수 상세 진단 */
    .ind-box { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border: 2px solid #90A4AE; min-height: 380px; margin-bottom: 10px; }
    .ind-title { font-size: 18px !important; color: #1976D2 !important; border-bottom: 1px solid #EEEEEE; padding-bottom: 8px; margin-bottom: 10px; }
    .ind-value { font-size: 38px !important; color: #B71C1C !important; text-align: center; display: block; margin: 8px 0; }
    .ind-diag { font-size: 14px !important; color: #333333 !important; line-height: 1.6; background-color: #FDFDFD; padding: 10px; border-radius: 5px; border-left: 5px solid #D32F2F; }
    
    /* 수치 스타일 */
    .stock-header { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border-left: 8px solid #1E88E5; margin-bottom: 15px; }
    .signal-text { font-size: 28px !important; color: white !important; }
    .val-main { font-size: 24px !important; color: #D32F2F !important; display: block; }
    </style>
    """, unsafe_allow_html=True)

# [메인 제목]
st.markdown("<div class='header-container'><p class='main-title'>👴 이수할아버지 냉정 진단기 v36056</p></div>", unsafe_allow_html=True)

# 0. 글로벌 전황 통합 보고 (데이터 수집 강화)
def get_global_data(ticker):
    try:
        g_df = yf.download(ticker, period="5d", progress=False)
        if not g_df.empty:
            curr = g_df['Close'].iloc[-1].item()
            prev = g_df['Close'].iloc[-2].item()
            pct = ((curr - prev) / prev) * 100
            return f"{curr:,.2f}", pct
        return "장부 지연", 0
    except:
        return "통신 오류", 0

n_v, n_p = get_global_data("^IXIC"); s_v, s_p = get_global_data("^GSPC"); t_v, t_p = get_global_data("^TNX")

st.markdown(f"""
    <div class='global-unified-box'>
        <div class='global-header'>🌎 0. 글로벌 전황 통합 보고</div>
        <div style='display: flex; flex-wrap: wrap; justify-content: space-around; text-align: center;'>
            <div class='global-item-text'><span class='global-item-label'>나스닥(NASDAQ):</span> <span style='color:{"#EF5350" if n_p > 0 else "#42A5F5"};'>{n_v} ({n_p:+.2f}%)</span></div>
            <div class='global-item-text'><span class='global-item-label'>S&P 500:</span> <span style='color:{"#EF5350" if s_p > 0 else "#42A5F5"};'>{s_v} ({s_p:+.2f}%)</span></div>
            <div class='global-item-text'><span class='global-item-label'>미국채 10년 금리:</span> <span style='color:{"#EF5350" if t_p > 0 else "#42A5F5"};'>{t_v} ({t_p:+.2f}%)</span></div>
        </div>
        <hr style='border:1px dashed #546E7A; margin: 10px 0;'>
        <div style='font-size:14px; color:#CFD8DC;'>
            <b>👴 냉정 평가:</b> 금리가 비정상으로 보이면 장부가 졸고 있는 것이니 새로고침 하셔. 금리는 언제나 우리 목을 노리는 비수라는 걸 잊지 마시게.
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

            # [종목 헤더]
            st.markdown(f"<div class='stock-header'><p style='font-size:20px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:26px; color:{'#D32F2F' if diff > 0 else '#1976D2'}; margin:0;'>{format(p, fmt)} {currency} <span style='font-size:16px;'>({format(diff, diff_fmt)})</span></p></div>", unsafe_allow_html=True)

            # [종합 신호등]
            buy_score = sum([p <= low_b * 1.01, rsi_val <= 35, will_val <= -75]); sell_score = sum([p >= up_b * 0.99, rsi_val >= 65, will_val >= -25])
            sig, color = ("🔴 매수권 진입", "#D32F2F") if buy_score >= 2 else ("🟢 매도권 진입", "#388E3C") if sell_score >= 2 else ("🟡 관망 및 대기", "#FBC02D")
            st.markdown(f"<div style='padding:15px; border-radius:10px; text-align:center; background-color:{color}; margin-bottom:15px;'><span class='signal-text'>{sig}</span></div>", unsafe_allow_html=True)

            # [1. 거래량 전황]
            v_ratio = (df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()) * 100
            st.markdown(f"<div class='vol-box'><div style='font-size:20px; color:#0D47A1; margin-bottom:5px;'>📊 1. 거래량 전황: {v_ratio:.1f}%</div><div style='font-size:15px;'>{'🚨 가짜 상승! 속지 마셔.' if p > prev_p and v_ratio < 100 else '⚠️ 물량 쏟아지니 성벽 보셔.' if p < prev_p and v_ratio > 150 else '⏳ 대기하셔.'}</div></div>", unsafe_allow_html=True)

            # [2. 필승 전략 및 냉정 진단 (통합 박스)]
            st.markdown(f"""
                <div class='unified-strategy-box'>
                    <div class='strategy-title'>⚔️ 2. 필살 대응 전략 및 냉정 진단</div>
                    <div class='diagnosis-content'>
                        <b>⚠️ [냉정 진단]:</b> 현재 주가가 중앙선({format(mid_line, fmt)}) 위에서 알짱거리지만, 이는 추세 전환이 아니라 <b>'데드 캣 바운스'</b>의 전형입니다. RSI <b>{rsi_val:.1f}</b>는 거품이 덜 빠졌음을 뜻해.
                    </div>
                    <div style='font-size:16px; color:#333;'>● <b>지침:</b> 속지 마시게. 지표가 바닥 심해로 잠수하며 개미들이 투항할 때까지 독하게 기다려야 하네. 지금은 <b>함정 수사</b>의 시간이야.</div>
                </div>
                """, unsafe_allow_html=True)

            # [3. 매수 매도 성벽 (박스 유지)]
            st.markdown("<div class='price-wall-container'><div style='font-size:18px; color:#1E88E5; margin-bottom:12px;'>🛡️ 3. 매수 매도 성벽 (Price Wall)</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>⚖️ 공략(하단)</p><span class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</span></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>🎯 수확(상단)</p><span class='val-main' style='color:#D32F2F;'>{format(up_b, fmt)}</span></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p style='font-size:15px;'>🛡️ 성벽(93%)</p><span class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # [4. 네 기둥 지수 상세 진단]
            st.subheader("🏗️ 4. 네 기둥 지수 상세 진단")
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_txt = "⚠️ 하단 돌파! 실리콘투처럼 하단 근처면 비명소리가 그칠 때까지 기다려야 해." if p <= low_b * 1.01 else "⚖️ 중앙선 아래서 빌빌대네." if p < mid_line else "📈 중앙선 위에서 기세 타네."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Bollinger (기세)</p><span style='font-size:13px; color:#546E7A;'>[중앙선 가격]</span><span class='ind-value'>{format(mid_line, fmt)}</span><div class='ind-diag'>● {bb_txt}<br>하단 성벽인 {format(low_b, fmt)}선 사수 여부가 진짜 맥점일세.</div></div>", unsafe_allow_html=True)
            with i2: # RSI
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ RSI (온도)</p><span style='font-size:13px; color:#546E7A;'>[현재 지수]</span><span class='ind-value'>{rsi_val:.1f}</span><div class='ind-diag'>● 현재 온도 <b>{rsi_val:.1f}</b>일세. 30 이하로 완전히 식어버릴 때까지 총을 아끼게. 지표가 미지근할 때 덤비면 화상 입는 법이야.</div></div>", unsafe_allow_html=True)
            with i3: # Williams
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Williams (심리)</p><span style='font-size:13px; color:#546E7A;'>[현재 지수]</span><span class='ind-value'>{will_val:.1f}</span><div class='ind-diag'>● 수치 <b>{will_val:.1f}</b>일세. -80 아래 심해로 잠수하며 모든 개미가 항복을 선언할 때, 그때가 진짜 기회임을 명심하게.</div></div>", unsafe_allow_html=True)
            with i4: # MACD
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ MACD (엔진)</p><span style='font-size:13px; color:#546E7A;'>[엔진 상태]</span><span class='ind-value' style='font-size:26px !important;'>{'▲ 상승' if m_l > s_l else '▼ 하락'}</span><div class='ind-diag'>● 엔진 {'정방향' if m_l > s_l else '역회전'} 중일세. 엔진이 멈추고 방향을 틀 때까지는 아무리 좋은 소식이 들려도 장부를 믿으셔.</div></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"장부 오류: {e}")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 모바일 최종 정밀본")
