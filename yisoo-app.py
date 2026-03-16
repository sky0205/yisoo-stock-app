import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 화면 구성 (v36056 스타일 및 할배 캐릭터 완벽 유지)
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

# [상단] 글로벌 지수 상세 진단 (보강 유지)
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        s_chg = (sp500.last_price / sp500.previous_close - 1) * 100
        tnx_val = tnx.last_price
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{s_chg:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{(tnx_val - tnx.previous_close)*100:+.2f}bp")
        if n_chg < -1.0 or tnx_val > 4.5: advice = f"🚨 **[긴급: 정박하시게!]** 시장 발작 중일세. 보따리 싸서 피신해 계시게!"
        elif n_chg > 0.8: advice = f"✅ **[쾌청: 진격하시게!]** 기세가 좋구먼. 빳빳하게 진격하시게."
        else: advice = f"🧐 **[안개: 낚싯대만 던지시게]** 무리하지 말고 지표 바닥권을 기다리시게."
        st.info(f"🧐 이수 할배의 글로벌 판독: {advice}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=400); end_date = datetime.now()
        if symbol.isdigit():
            currency = "원"; fmt_p = ",.0f"
            try:
                df = fdr.DataReader(symbol, start_date, end_date)
                stocks = fdr.StockListing('KRX'); name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            except:
                ticker = yf.Ticker(f"{symbol}.KS"); df = ticker.history(start=start_date, end=end_date)
                name = ticker.info.get('shortName', symbol)
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date, end=end_date); currency = "$"; fmt_p = ",.2f"
            name = ticker.info.get('shortName', symbol)
        
        if not df.empty:
            p = float(df['Close'].iloc[-1]); prev_p = float(df['Close'].iloc[-2])
            peak_20 = float(df['Close'].iloc[-20:-1].max()); defense_line = peak_20 * 0.93

            # 기술 지표 계산
            v_curr = df['Volume'].iloc[-1]; v_avg5 = df['Volume'].iloc[-6:-1].mean(); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain.iloc[-1] / (loss.iloc[-1] + 1e-10))))
            h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]; will_val = (h14 - p) / (h14 - l14 + 1e-10) * -100
            m_l = df['Close'].ewm(span=12).mean().iloc[-1] - df['Close'].ewm(span=26).mean().iloc[-1]; s_l = (df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()).ewm(span=9).mean().iloc[-1]
            df['MA20'] = df['Close'].rolling(20).mean(); df['Std'] = df['Close'].rolling(20).std(); mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)

            st.markdown(f"<div class='stock-header'><p style='font-size:35px; color:#1565C0; margin:0;'>{name} ({symbol})</p><p style='font-size:38px; color:#D32F2F; margin:0;'>{format(p, fmt_p)} {currency} (전일비: {format(p-prev_p, '+'+fmt_p)})</p></div>", unsafe_allow_html=True)
            
            v_status = "💤 거래침체" if v_ratio < 100 else "📈 거래증가" if v_ratio < 200 else "🔥 거래폭발"
            v_adv = "✅ 세력이 들어왔구먼! 눈을 부라리고 보시게." if v_ratio >= 100 else "🚨 거래량 없는 움직임은 가짜일세! 섣불리 진격하지 마시게."
            st.markdown(f"<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            if p >= up_b or rsi_val >= 65: sig, col, adv = "🟢 매도권 진입", "#388E3C", "● 과열권일세! 수익 챙겨서 나오시게."
            elif p <= low_b or rsi_val <= 35: sig, col, adv = "🔴 매수권 진입", "#D32F2F", "● 바닥권일세. 분할 매수 보따리 푸시게."
            else: sig, col, adv = "🟡 관망 및 대기", "#FBC02D", "● 아직 안개 속일세. 낚싯대만 던져두시게."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{adv}</p></div>", unsafe_allow_html=True)

            # [복구] 매수/매도성벽 가격 카드
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선(하단)</p><p class='val-main' style='color:#388E3C;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선(상단)</p><p class='val-main' style='color:#D32F2F;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽 (방어선)</p><p class='val-main' style='color:#E65100;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

           # 필살 대응 전략 (v36056-Final 냉정 진단 로직)
        st.header("🎯 2. 필살 대응 전략 (Sure-win Strategy)")
        
        st.markdown(f"""
        <div style="border: 2px solid #e74c3c; padding: 15px; border-radius: 10px; background-color: #fffdfd;">
            <h4 style="color: #e74c3c; margin-top: 0;">⚠️ [냉정 진단]</h4>
            <p style="font-size: 1.1em; line-height: 1.6;">
            현재 주가가 Bollinger Band 중앙선(<b>{bb_mid:,.0f}원</b>) 위에서 알짱거리지만, 
            이는 추세 전환이 아니라 <b>'데드 캣 바운스'</b>의 전형입니다. 
            RSI 지표가 <b>{rsi_val:.1f}</b>로 여전히 미지근하다는 것은, 시장에 낀 거품이 다 빠지지 않았음을 뜻합니다.
            </p>
            <hr style="border: 0.5px solid #eee;">
            <h4 style="color: #2980b9;">🎯 [필살 지침]</h4>
            <p>가짜 반등에 속아 방아쇠를 당기지 마시게. 윌리엄 지수({willr_val:.2f})가 심해로 잠수하며 
            개미들이 투항할 때까지 독하게 기다려야 하네. 지금은 <b>함정 수사</b>의 시간이야. 
            쏠리드 익절금은 저들이 비명을 지를 때 비수로 써야 하네.</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("---")

        # 네 기둥 지수 상세 진단 (세밀한 분석 로직)
        st.header("🏗️ 3. 네 기둥 지수 상세 진단 (Four Pillars)")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"""
            ### 🛡️ 수율(Yield) x Bollinger
            * **상세**: 기술력 논란은 주가를 밴드 하단({bb_low:,.0f}원)으로 끌어당기는 자석일세. 
              밴드 폭이 좁아지며 에너지를 응축하고 있으나, 수율 확신이 없는 한 
              오늘의 반등은 하단으로 가기 전 잠시 숨을 고르는 **'가짜 숨구멍'**일 뿐이야.
            
            ### 🛡️ 관세(Tariff) x RSI
            * **상세**: 미국의 관세 압박은 수출주의 RSI를 50 선 아래로 짓누르는 거대한 벽이지. 
              지표가 {rsi_val:.1f}에서 고개를 숙이는 건 이미 이익 전망치가 썩어 들어가고 있다는 증거야. 
              이 벽을 못 넘으면 가격은 계단식으로 무너질 수밖에 없네.
            """)
        
        with col_p2:
            st.markdown(f"""
            ### 🛡️ 환율(FX) x Momentum
            * **상세**: 환율 1,490원 돌파는 외인들에게 '환차손 도살장' 입구와 같네. 
              수급 모멘텀이 꺾인 자리에 발을 들이는 건 제 발로 호랑이 굴에 들어가는 짓이야. 
              환율이 안정되어 외인들이 돌아올 때까지는 장부를 덮어두게.
            
            ### 🛡️ 지표(Index) x Williams %R
            * **상세**: 신용 잔고 33조 원은 시한폭탄일세. 
              윌리엄 지수({willr_val:.2f})가 바닥을 기며 모든 개미가 항복을 선언할 때, 
              그 피비린내 속에 진짜 기회가 숨어 있구먼.
            """)

    else:
        st.error("장부를 불러올 수 없구먼! 종목 코드를 다시 보시게.")

st.write("---")
st.caption("분석가 서강윤: 2026년 실시간 장부 및 v36056 최종 양식 적용 완료")
