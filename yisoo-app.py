import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 및 CSS (v36056 스타일 유지 및 보강)
st.set_page_config(page_title="이수할아버지 분석기 v36056-Final", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .global-card { background-color: #263238; color: #FFFFFF; padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: center; border: 1px solid #455A64; }
    .stock-header { background-color: #FFFFFF; padding: 18px; border-radius: 12px; border-left: 10px solid #1E88E5; margin-bottom: 15px; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-main-text { font-size: 32px !important; color: #0D47A1 !important; margin-bottom: 10px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 480px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 24px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 18px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .diagnosis-highlight { background-color: #FFEBEE; padding: 15px; border-radius: 10px; border: 2px dashed #D32F2F; margin-bottom: 20px; font-size: 22px !important; color: #B71C1C !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("👴 이수할아버지의 냉정 진단기 v36056-Final")

# 2. 전 세계 전황 보고 (Nasdaq, S&P 500, 미국채 금리)
st.subheader("🌎 글로벌 전황 요약")
g1, g2, g3 = st.columns(3)

def get_global(ticker, name):
    try:
        g_df = yf.download(ticker, period="2d", progress=False)
        curr = g_df['Close'].iloc[-1].item()
        prev = g_df['Close'].iloc[-2].item()
        diff = curr - prev
        pct = (diff / prev) * 100
        color = "#EF5350" if diff > 0 else "#42A5F5"
        return f"<div class='global-card'>{name}<br><span style='font-size:24px; color:{color};'>{curr:,.2f} ({pct:+.2f}%)</span></div>"
    except: return f"<div class='global-card'>{name}<br>데이터 통신 불가</div>"

g1.markdown(get_global("^IXIC", "NASDAQ (나스닥)"), unsafe_allow_html=True)
g2.markdown(get_global("^GSPC", "S&P 500 (지수)"), unsafe_allow_html=True)
g3.markdown(get_global("^TNX", "US 10Y (미국채 10년 금리)"), unsafe_allow_html=True)

symbol = st.text_input("📊 분석할 종목번호 또는 티커를 넣으셔", "005930")

if symbol:
    try:
        # 데이터 수집 (2026년 실시간 장부 기준)
        start_date = datetime.now() - timedelta(days=365)
        if symbol.isdigit(): # 국내 주식
            df = fdr.DataReader(symbol, start_date)
            stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            currency = "원"; fmt = ",.0f" 
        else: # 미국 주식
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            name = ticker.info.get('shortName', symbol); currency = "$"; fmt = ",.2f"
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            
            # 보조지표 계산 (20/2, 14/9, 14/6)
            df['MA20'] = df['Close'].rolling(window=20).mean(); df['Std'] = df['Close'].rolling(window=20).std()
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)
            
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(window=14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
            
            h14 = df['High'].rolling(window=14).max().iloc[-1]; l14 = df['Low'].rolling(window=14).min().iloc[-1]
            will_val = (h14 - p) / (h14 - l14) * -100 if (h14 - l14) != 0 else 0

            # 1. 거래량 전황
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean()
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            v_status = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            v_advice = "🚨 <b>가짜 상승!</b> 주인(외인)은 나가는데 머슴(기관)이 억지로 막고 있구먼. 속지 마셔." if (p > prev_p and v_ratio < 100) else "⚠️ <b>도살장 전조.</b> 거래량이 실린 하락이야. 보따리 챙겨서 대피하셔." if (p < prev_p and v_ratio > 150) else "⏳ 안개 정국이니 방아쇠에서 손 떼고 대기하셔."

            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt)} {currency}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 1. 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_advice}</div></div>", unsafe_allow_html=True)

            # 2. 필살 대응 전략 (냉정 진단 추가)
            st.markdown("<div class='trend-card'><div class='trend-title'>⚔️ 2. 필살 대응 전략 (Sure-win Strategy)</div>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='diagnosis-highlight'>
                <b>⚠️ [냉정 진단]:</b> 현재 주가가 Bollinger Band 중앙선({format(mid_line, fmt)}) 위에서 알짱거리지만, 
                이는 추세 전환이 아니라 <b>'데드 캣 바운스'</b>의 전형입니다. 
                RSI 지표가 <b>{rsi_val:.1f}</b>로 여전히 미지근하다는 것은, 시장에 낀 거품이 다 빠지지 않았음을 뜻합니다.
                </div>
                <div style='font-size:22px; line-height:1.8;'>
                ● <b>전략 지침:</b> 가짜 반등에 속아 방아쇠를 당기지 마시게. 윌리엄 지수({will_val:.1f})가 심해로 잠수하며 
                개미들이 투항할 때까지 독하게 기다려야 하네. 지금은 <b>함정 수사</b>의 시간이야. 
                쏠리드 익절금은 저들이 비명을 지를 때 비수로 써야 하네.
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 3. 네 기둥 지수 상세 진단 (보강된 로직)
            st.header("🏗️ 3. 네 기둥 지수 상세 진단 (Four Pillars)")
            i1, i2, i3, i4 = st.columns(4)
            
            with i1: # 수율 x Bollinger
                bb_diag = f"현재 중앙선({format(mid_line, fmt)}) 위에서 버티는 척하나, 수율 확신이 없는 한 오늘의 움직임은 하단({format(low_b, fmt)})으로 가기 전 잠시 숨을 고르는 <b>'가짜 숨구멍'</b>일 뿐이야."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ 수율(Yield) x Bollinger</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2: # 관세 x RSI
                r_diag = f"온도 {rsi_val:.1f}도. 관세 압박이라는 거대한 벽이 RSI 50 선 위로 고개를 못 들게 짓누르고 있구먼. 이 벽을 못 넘으면 장부는 계단식으로 무너질 수밖에 없네."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ 관세(Tariff) x RSI</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
                
            with i3: # 환율 x Momentum
                m_diag = "환율 1,490원 돌파는 외인들에게 '탈출 버튼'이야. 수급 모멘텀이 꺾인 자리에 발을 들이는 건 도살장에 제 발로 들어가는 것과 같으니 환율이 안정될 때까지 장부를 덮어두게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ 환율(FX) x Momentum</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)
                
            with i4: # 지표 x Williams %R
                w_diag = f"지수 {will_val:.1f}. 신용 잔고 33조 원은 시한폭탄일세. 윌리엄 지수가 -90 근처에서 횡보하며 모든 개미가 항복을 선언할 때, 그 피비린내 속에 진짜 기회가 숨어 있구먼."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>🛡️ 지표(Index) x Williams%R</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"장부를 불러올 수 없구먼: {e}")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 최종 양식(글로벌 전황 포함) 적용 완료")
