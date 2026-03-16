import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 디자인 (수치 강조형)
st.set_page_config(page_title="v36056 냉정진단기 Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .global-card { background-color: #263238; color: #FFFFFF; padding: 12px; border-radius: 10px; text-align: center; border: 1px solid #455A64; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .diagnosis-box { border: 2px solid #D32F2F; padding: 20px; border-radius: 10px; background-color: #FFF8F1; margin-bottom: 20px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; margin-bottom: 20px; }
    .val-main { font-size: 36px !important; color: #D32F2F !important; margin: 10px 0; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 450px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 24px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 19px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .ind-value { font-size: 45px !important; color: #B71C1C !important; text-align: center; display: block; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👴 이수할아버지의 냉정 진단기 v36056 (지표 정밀형)")

# 2. 글로벌 전황 보고
g1, g2, g3 = st.columns(3)
def get_global(ticker, name):
    try:
        g_df = yf.download(ticker, period="2d", progress=False)
        curr = g_df['Close'].iloc[-1].item()
        prev = g_df['Close'].iloc[-2].item()
        pct = ((curr - prev) / prev) * 100
        color = "#EF5350" if pct > 0 else "#42A5F5"
        return f"<div class='global-card'>{name}<br><span style='font-size:22px; color:{color};'>{curr:,.2f} ({pct:+.2f}%)</span></div>"
    except: return f"<div class='global-card'>{name}<br>장부 지연</div>"

g1.markdown(get_global("^IXIC", "NASDAQ (나스닥)"), unsafe_allow_html=True)
g2.markdown(get_global("^GSPC", "S&P 500 (지수)"), unsafe_allow_html=True)
g3.markdown(get_global("^TNX", "US 10Y (국채 금리)"), unsafe_allow_html=True)

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=365)
        if symbol.isdigit(): # 국내
            df = fdr.DataReader(symbol, start_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            currency = "원"; fmt = ",.0f" 
        else: # 해외
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            name = ticker.info.get('shortName', symbol); currency = "$"; fmt = ",.2f"
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            
            # 지표 계산 로직
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)
            
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1]))) if loss.iloc[-1] != 0 else 100
            
            h14 = df['High'].rolling(window=14).max().iloc[-1]; l14 = df['Low'].rolling(window=14).min().iloc[-1]
            will_val = (h14 - p) / (h14 - l14) * -100 if (h14 - l14) != 0 else 0
            
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]
            s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            peak_p = float(df['Close'].iloc[-20:].max()); defense_line = peak_p * 0.93

            # 1. 거래량 전황
            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt)} {currency}</p></div>", unsafe_allow_html=True)
            v_ratio = (df['Volume'].iloc[-1] / df['Volume'].iloc[-6:-1].mean()) * 100
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 1. 거래량 전황: {v_ratio:.1f}%</div><div class='vol-sub-text'>장부의 숫자는 속이지 못하네. {'가짜 상승이니 절대 쫓지 마셔.' if p > prev_p and v_ratio < 100 else '누군가 던지기 시작했으니 성벽 사수를 보셔.' if p < prev_p and v_ratio > 150 else '폭풍 전야의 정막일세. 대기하셔.'}</div></div>", unsafe_allow_html=True)

            # 2. 필살 대응 전략 (냉정 진단)
            st.markdown("<div class='trend-card'><div class='trend-title'>⚔️ 2. 필살 대응 전략 (Sure-win Strategy)</div>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='diagnosis-box'>
                <p style='font-size:24px; color:#D32F2F; margin-bottom:10px;'>⚠️ [냉정 진단]</p>
                <p style='font-size:21px; line-height:1.7;'>
                현재 주가가 Bollinger Band 중앙선(<b>{format(mid_line, fmt)}</b>) 위에서 알짱거리지만, 
                이는 추세 전환이 아니라 <b>'데드 캣 바운스'</b>의 전형입니다. 
                RSI 지표가 <b>{rsi_val:.1f}</b>로 여전히 미지근하다는 것은, 시장에 낀 거품이 다 빠지지 않았음을 뜻합니다.
                </p>
                <hr style='border:1px dashed #D32F2F;'>
                <p style='font-size:20px;'>● <b>필살 지침:</b> 가짜 반등에 속지 마시게. 윌리엄 지수가 바닥 심해로 잠수할 때까지 독하게 기다려야 하네.</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 3. 매수 매도 성벽 (복구 완료)
            st.subheader("🛡️ 3. 매수 매도 성벽 (Price Strategy)")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선(하단)</p><p class='val-main'>{format(low_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선(상단)</p><p class='val-main'>{format(up_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 방어 성벽 (93% 선)</p><p class='val-main'>{format(defense_line, fmt)}</p></div>", unsafe_allow_html=True)

            # 4. 네 기둥 지수 상세 진단 (지수 중심 정밀화)
            st.subheader("🏗️ 4. 네 기둥 지수 상세 진단 (Pure Technical Analysis)")
            i1, i2, i3, i4 = st.columns(4)
            
            with i1: # Bollinger Bands
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Bollinger Bands</p><span class='ind-value'>{format(mid_line, fmt)}</span><p class='ind-diag'>● 현재 가격이 중앙선 {'위에서 기세를 유지 중이나' if p > mid_line else '아래에서 기운을 잃었구먼.'} 상단({format(up_b, fmt)})과 하단({format(low_b, fmt)})의 이격도를 보며 에너지 응축을 살피게.</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ RSI (상대강도)</p><span class='ind-value'>{rsi_val:.1f}</span><p class='ind-diag'>● 현재 강도는 <b>{rsi_val:.1f}</b>일세. 30 이하로 완전히 식어버릴 때까지 기다리게. 50 선 근처에서 비실거리는 건 아직 에너지가 부족하다는 증거야.</p></div>", unsafe_allow_html=True)
            with i3: # Williams %R
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ Williams %R</p><span class='ind-value'>{will_val:.1f}</span><p class='ind-diag'>● 지표 수치 <b>{will_val:.1f}</b>는 개미들의 항복 시점을 말해주네. -80 아래 심해로 잠수하며 비명소리가 들릴 때가 진짜 기회일세.</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ MACD (추세엔진)</p><span class='ind-value'>{'상승' if m_l > s_l else '하락'}</span><p class='ind-diag'>● 엔진이 {'힘차게 도는 중이나' if m_l > s_l else '역회전 중이야.'} 시그널선과의 간격이 좁아지는지 부라리고 보게나. 추세의 마디가 바뀌는 지점이 맥점일세.</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"장부를 불러올 수 없구먼 (오류: {e})")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 최종 양식(지표 정밀형) 적용")
