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
    
    .header-container { background-color: #0D47A1; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border-bottom: 4px solid #1565C0; }
    .main-title { font-size: 24px !important; color: #FFFFFF !important; margin: 0; }
    
    .global-unified-box { background-color: #263238; color: #FFFFFF; padding: 20px; border-radius: 12px; border: 2px solid #455A64; margin-bottom: 20px; }
    .global-header { font-size: 20px !important; color: #81D4FA !important; border-bottom: 1px solid #546E7A; padding-bottom: 8px; margin-bottom: 12px; }
    .global-item-container { display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center; }
    .global-item { padding: 10px; min-width: 120px; }
    .global-item-label { font-size: 16px !important; color: #B0BEC5 !important; display: block; margin-bottom: 5px; }
    .global-item-val { font-size: 18px !important; }
    
    .unified-strategy-box { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 4px solid #D32F2F; margin: 15px 0; }
    .diagnosis-content { font-size: 17px !important; color: #B71C1C !important; line-height: 1.6; background-color: #FFF8F1; padding: 15px; border-radius: 8px; border-left: 8px solid #D32F2F; margin-bottom: 10px; }
    
    .price-wall-container { background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .price-card { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1.5px solid #CFD8DC; text-align: center; }
    
    .ind-box { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #90A4AE; min-height: 400px; margin-bottom: 10px; }
    .ind-title { font-size: 18px !important; color: #1976D2 !important; border-bottom: 1px solid #EEEEEE; padding-bottom: 5px; margin-bottom: 10px; }
    .ind-value { font-size: 35px !important; color: #B71C1C !important; text-align: center; display: block; margin: 5px 0; }
    .ind-diag { font-size: 14px !important; color: #333333 !important; line-height: 1.6; background-color: #FDFDFD; padding: 12px; border-radius: 5px; border-left: 5px solid #D32F2F; }
    
    .stock-header { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border-left: 8px solid #1E88E5; margin-bottom: 15px; }
    .val-main { font-size: 26px !important; color: #D32F2F !important; display: block; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-container'><p class='main-title'>👴 이수할아버지 냉정 진단기 v36056</p></div>", unsafe_allow_html=True)

# 0. 글로벌 전황 보고 (데이터 수집 강화)
def get_global_data(ticker):
    try:
        # 최근 5일 데이터를 가져와서 가장 최신 값을 사용 (휴장일 대비)
        g_df = yf.download(ticker, period="5d", progress=False)
        if not g_df.empty:
            curr = g_df['Close'].iloc[-1].item()
            prev = g_df['Close'].iloc[-2].item()
            pct = ((curr - prev) / prev) * 100
            return f"{curr:,.2f}", f"{pct:+.2f}%", pct
        return "데이터 없음", "0.00%", 0
    except:
        return "장부 지연", "0.00%", 0

n_v, n_p_str, n_p = get_global_data("^IXIC")
s_v, s_p_str, s_p = get_global_data("^GSPC")
t_v, t_p_str, t_p = get_global_data("^TNX")

st.markdown(f"""
    <div class='global-unified-box'>
        <div class='global-header'>🌎 0. 글로벌 전황 통합 보고</div>
        <div class='global-item-container'>
            <div class='global-item'>
                <span class='global-item-label'>나스닥 (NASDAQ)</span>
                <span class='global-item-val' style='color:{"#EF5350" if n_p > 0 else "#42A5F5"};'>{n_v} ({n_p_str})</span>
            </div>
            <div class='global-item'>
                <span class='global-item-label'>S&P 500 (지수)</span>
                <span class='global-item-val' style='color:{"#EF5350" if s_p > 0 else "#42A5F5"};'>{s_v} ({s_p_str})</span>
            </div>
            <div class='global-item'>
                <span class='global-item-label'>미국채 10년 금리</span>
                <span class='global-item-val' style='color:{"#EF5350" if t_p > 0 else "#42A5F5"};'>{t_v} ({t_p_str})</span>
            </div>
        </div>
        <hr style='border:1px dashed #546E7A; margin: 15px 0;'>
        <div style='font-size:15px; color:#CFD8DC;'>
            <b>👴 냉정 평가:</b> 금리가 0.00으로 보이면 장부가 잠시 졸고 있는 것이니 새로고침 하시게. 금리는 언제나 우리 목을 노리는 비수라는 걸 잊지 마셔.
        </div>
    </div>
    """, unsafe_allow_html=True)

# 이하 종목 분석 로직 동일 (어르신이 원하시는 종목 입력창)
symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")
# ... (중략) ...
# 이 부분은 어르신이 쓰시던 이전의 완벽한 로직을 그대로 유지하시되, 
# 상단 글로벌 데이터 부분만 위 코드로 갈아 끼우시면 됩니다.
