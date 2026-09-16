import html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
import pandas as pd
import requests
import streamlit as st
import yfinance as yf


st.set_page_config(
    page_title="이수할아버지의 냉정 진단기 v36085", layout="wide"
)

# --- 🔒 자물쇠(비밀번호) 보안 장치 ---
def check_password():
    """비밀번호를 확인하는 함수 (st.secrets 호환 보안 보수)"""
    correct_pw = str(st.secrets.get("APP_PASSWORD", "1111"))

    def password_entered():
        if st.session_state["password"] == correct_pw:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.subheader("🔒 이수할아버지의 냉정 진단기 - 보안 접속")
        st.text_input(
            "비밀번호를 입력하시구먼요:",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False
    elif not st.session_state["password_correct"]:
        st.subheader("🔒 이수할아버지의 냉정 진단기 - 보안 접속")
        st.text_input(
            "비밀번호를 입력하시구먼요:",
            type="password",
            on_change=password_entered,
            key="password",
        )
        st.error("😕 비밀번호가 틀렸사옵니다. 다시 확인하시구먼요!")
        return False
    else:
        return True


if not check_password():
    st.stop()


# --- [보급로 최적화 캐싱 장치: 반응속도 극대화 조율] ---
@st.cache_data(ttl=3600)
def load_krx_listing():
    try:
        return fdr.StockListing("KRX")
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=10)
def fetch_global_market():
    nasdaq = yf.Ticker("^IXIC").fast_info
    sp500 = yf.Ticker("^GSPC").fast_info
    dow = yf.Ticker("^DJI").fast_info
    tnx = yf.Ticker("^TNX").fast_info
    usdkrw = yf.Ticker("USDKRW=X").fast_info
    return {
        "n_last": nasdaq.last_price,
        "n_prev": nasdaq.previous_close,
        "s_last": sp500.last_price,
        "s_prev": sp500.previous_close,
        "d_last": dow.last_price,
        "d_prev": dow.previous_close,
        "t_last": tnx.last_price,
        "t_prev": tnx.previous_close,
        "u_last": usdkrw.last_price,
        "u_prev": usdkrw.previous_close,
    }


# --- [호가창 실시간 매도/매수 잔량 수집 및 수급 압력 산출 함수] ---
def fetch_kr_orderbook(symbol):
    """국내 주식 호가 데이터."""
    return {
        "ask": 0.0,
        "bid": 0.0,
        "ratio": None,
        "ok": False,
        "msg": "실시간 호가 API 미연결",
    }


# 1. 스타일 및 화면 구성
st.markdown(
    """
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-box * { color: #FFFFFF !important; }
    .signal-text { font-size: 44px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .signal-subtext { font-size: 22px !important; color: #FFFFFF !important; line-height: 1.6; margin-top: 10px; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 12px; border: 2.5px solid #CFD8DC; text-align: center; box-shadow: 1px 1px 6px rgba(0,0,0,0.05); }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 540px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 24px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 19px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 12px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .final-msg { color: #D32F2F !important; font-size: 24px !important; font-weight: 900 !important; line-height: 1.5 !important; }
    
    div.stButton > button {
        background: linear-gradient(90deg, #1A237E 0%, #283593 100%) !important;
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: bold !important;
        padding: 10px 15px !important;
        height: 46px !important;
        border-radius: 8px !important;
        border: 2px solid #FFEB3B !important;
        width: 100% !important;
        box-shadow: 0 3px 6px rgba(26, 35, 126, 0.3) !important;
        cursor: pointer !important;
        margin-top: 0px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #283593 100%, #3F51B5 100%) !important;
        color: #FFEB3B !important;
        border-color: #FFFFFF !important;
    }
    div.stButton > button * {
        color: #FFFFFF !important;
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def display_global_risk():
    st.markdown("### 🌍 글로벌 5대 지수 및 환율·국채 종합 전황")
    try:
        data = fetch_global_market()
        n_chg = (data["n_last"] / data["n_prev"] - 1) * 100
        s_chg = (data["s_last"] / data["s_prev"] - 1) * 100
        d_chg = (data["d_last"] / data["d_prev"] - 1) * 100
        tnx_val, tnx_chg = (
            data["t_last"],
            (data["t_last"] / data["t_prev"] - 1) * 100,
        )
        u_val, u_chg = data["u_last"], (data["u_last"] / data["u_prev"] - 1) * 100

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("나스닥 (NASDAQ)", f"{data['n_last']:,.2f}", f"{n_chg:+.2f}%")
        c2.metric("S&P 500 (SPX)", f"{data['s_last']:,.2f}", f"{s_chg:+.2f}%")
        c3.metric("다우존스 (DJI)", f"{data['d_last']:,.2f}", f"{d_chg:+.2f}%")
        c4.metric("미 국채 10년 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
        c5.metric("원/달러 환율", f"{u_val:,.2f}원", f"{u_chg:+.2f}%")

        avg_us_chg = (n_chg + s_chg + d_chg) / 3
        pos_cnt = sum([n_chg > 0, s_chg > 0, d_chg > 0])
        neg_cnt = sum([n_chg < 0, s_chg < 0, d_chg < 0])

        if pos_cnt == 3:
            market_mood = (
                "미 3대 지수 동반 훈풍 속 안도 랠리!"
                if avg_us_chg >= 1.0
                else "미 3대 지수 일제히 상승 마감!"
            )
        elif neg_cnt == 3:
            market_mood = (
                "미 3대 지수 동반 급락으로 투심 냉각!"
                if avg_us_chg <= -1.0
                else "미 3대 지수 일제히 하락 (전면 약세 국면)!"
            )
        else:
            market_mood = "미 3대 지수 혼조세 속 숨고르기 진행!"

        macro_alerts = []
        if tnx_val >= 4.5:
            macro_alerts.append(f"🚨 [금리 발작] 국채 금리 {tnx_val:.3f}% 돌파!")
        elif tnx_val <= 3.8:
            macro_alerts.append(f"🌱 [금리 안정] 국채 금리 {tnx_val:.3f}% 안정권 진입")

        if u_val >= 1450:
            macro_alerts.append(
                f"🚨 [환율 격랑] 원/달러 {u_val:,.2f}원! 초위험 고환율 비상!"
            )
        elif u_val >= 1400:
            macro_alerts.append(
                f"⚠️ [환율 경계] 원/달러 {u_val:,.2f}원 1,400원대 고착화 압박!"
            )
        elif u_val >= 1380:
            macro_alerts.append(
                f"⚡ [환율 분기점] 원/달러 {u_val:,.2f}원! 외인 눈치보기"
            )
        elif u_val <= 1330:
            macro_alerts.append(
                f"💵 [환율 우호] 원/달러 {u_val:,.2f}원 하향 안정세"
            )

        if u_chg > 0.3:
            macro_alerts.append(f"📈 오늘 환율 {u_chg:+.2f}% 치솟는 중!")
        elif u_chg < -0.3:
            macro_alerts.append(f"📉 오늘 환율 {u_chg:+.2f}% 진정세")

        if tnx_val >= 4.5 or u_val >= 1380:
            strategy = "외인 수급 이탈 우려로 상단 저항이 강하니 추격매수 금지, 5일선 및 방어선 위주로 보수적 대응하시게."
        elif avg_us_chg > 0.5 and tnx_val < 4.2 and u_val < 1350:
            strategy = "매크로 환경이 우호적이니 거래량 실린 정석 눌림목 주도주 위주로 적극 공략하시게."
        else:
            strategy = "장 초반 뇌동매매를 삼가고 지표 동조와 5일선 안착 여부를 끝까지 확인 후 진입하시게."

        macro_text = " | ".join(macro_alerts) if macro_alerts else "매크로 특이 동향 없음"

        st.info(
            f"🧐 **이수 할배의 글로벌 판독:** {market_mood}!\n\n- {macro_text}\n- 💡 **[대응 전략]** {strategy}"
        )
    except Exception:
        st.error("⚠️ 글로벌 데이터 호출 불가")


st.title("🧐 이수할아버지의 냉정 진단기 v36085 (KRX 일봉 종가 사수 완성본)")
display_global_risk()
st.divider()

# ==============================================================================
# ★ [상단: 종목 / 평단가 / HTS 매도·매수잔량 통합 입력창]
# ==============================================================================
col_symbol, col_avg, col_ask, col_bid, col_btn = st.columns(
    [2.0, 1.5, 1.5, 1.5, 1.0]
)

with col_symbol:
    raw_symbol_input = st.text_input("📊 종목번호", "050890")
    symbol = raw_symbol_input.strip()

with col_avg:
    user_avg_price = st.number_input(
        "💡 보유 평단가",
        min_value=0.0,
        value=0.0,
        step=100.0,
        help="평단가를 적으시면 맞춤형 가이드를 제공합니다.",
    )

with col_ask:
    manual_ask = st.number_input(
        "🔴 총매도잔량",
        min_value=0.0,
        value=0.0,
        step=1.0,
        format="%.2f",
        help="HTS 총매도잔량 (x1,000 주)",
    )

with col_bid:
    manual_bid = st.number_input(
        "🔵 총매수잔량",
        min_value=0.0,
        value=0.0,
        step=1.0,
        format="%.2f",
        help="HTS 총매수잔량 (x1,000 주)",
    )

with col_btn:
    st.write("")
    st.write("")
    if st.button("🔄 분석"):
        st.rerun()



if symbol:
    try:
        try:
            start_date = datetime.now() - timedelta(days=500)
        except Exception:
            start_date = datetime.now(ZoneInfo("UTC")) - timedelta(days=500)

        is_kr = symbol.isdigit()

        kst_tz = ZoneInfo("Asia/Seoul")
        ny_tz = ZoneInfo("America/New_York")
        kst_now = datetime.now(kst_tz)
        now_local = kst_now if is_kr else datetime.now(ny_tz)

        df = pd.DataFrame()
        auto_p, v_curr = 0.0, 0.0

        if is_kr:
            currency, fmt_p = "원", ",.0f"
            clean_symbol = symbol.zfill(6)
            
            # ★ [KRX 일봉 데이터 수집]: FinanceDataReader를 통해 순수 일봉 장부 로드
            try:
                df = fdr.DataReader(clean_symbol, start=start_date.strftime("%Y-%m-%d"))
            except Exception:
                pass

            if df.empty:
                try:
                    df = yf.Ticker(f"{clean_symbol}.KS").history(start=start_date)
                    if df.empty:
                        df = yf.Ticker(f"{clean_symbol}.KQ").history(start=start_date)
                except Exception:
                    pass

            # 실시간 현재가 및 거래량 취득
            try:
                api_url = f"https://m.stock.naver.com/api/stock/{clean_symbol}/basic"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                res = requests.get(api_url, headers=headers, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    auto_p = float(str(data["closePrice"]).replace(",", ""))
                    v_curr = float(str(data["accumulatedTradingVolume"]).replace(",", ""))
            except Exception:
                if not df.empty:
                    auto_p = float(df["Close"].iloc[-1])
                    v_curr = float(df["Volume"].iloc[-1])
        else:
            currency, fmt_p = "$", ",.2f"
            tk_upper = symbol.upper()
            ticker = yf.Ticker(tk_upper)

            try:
                df = ticker.history(start=start_date)
            except Exception:
                df = ticker.history(period="1y")

            try:
                info = ticker.fast_info
                auto_p = getattr(info, "last_price", float(df["Close"].iloc[-1]))
                v_curr = getattr(info, "last_volume", float(df["Volume"].iloc[-1]))
            except Exception:
                if not df.empty:
                    auto_p = float(df["Close"].iloc[-1])
                    v_curr = float(df["Volume"].iloc[-1])

        # 호가창 잔량 기본 설정
        multiplier = 1000.0 if is_kr else 1.0

        if manual_ask > 0 and manual_bid > 0:
            calc_ratio = round(manual_ask / manual_bid, 2)
            display_ask = manual_ask * multiplier
            display_bid = manual_bid * multiplier
            ob_data = {
                "ask": display_ask,
                "bid": display_bid,
                "ratio": calc_ratio,
                "ok": True,
                "msg": "HTS 직접입력",
            }
        elif manual_ask > 0 or manual_bid > 0:
            ob_data = {
                "ask": manual_ask * multiplier,
                "bid": manual_bid * multiplier,
                "ratio": None,
                "ok": False,
                "msg": "HTS 매도·매수잔량을 모두 입력해야 분석 가능",
            }
        else:
            ob_data = {"ask": 0.0, "bid": 0.0, "ratio": None, "ok": False, "msg": "실시간 호가 API 미연결"}

        p = auto_p

        if df.empty:
            st.warning(f"⚠️ [{symbol}] 종목의 데이터를 불러오지 못했구먼. 종목번호를 다시 확인해 주시게.")
        else:
            df = df.ffill().dropna()
            df.index = pd.to_datetime(df.index).date
            today_date = now_local.date()

            # ==================================================================
            # ★ [KRX 정규장 닻 고정 완성]: 일봉 장부에서 '순수 직전 영업일 종가'를 정확히 추출하여 전일 종가 고정
            # ==================================================================
            try:
                df_sorted = df.sort_index()
                if today_date in df_sorted.index:
                    df_past = df_sorted.drop(today_date, errors="ignore")
                else:
                    df_past = df_sorted
                    
                if len(df_past) >= 1:
                    prev_p = float(df_past["Close"].iloc[-1])
                else:
                    prev_p = p
            except Exception:
                prev_p = float(df["Close"].iloc[-2]) if len(df) >= 2 else p

            # 오늘 날짜 시세 반영 (데이터프레임 업데이트)
            if today_date in df.index:
                df.loc[today_date, "Close"] = p
                df.loc[today_date, "Volume"] = v_curr
                if p > df.loc[today_date, "High"]:
                    df.loc[today_date, "High"] = p
                if p < df.loc[today_date, "Low"]:
                    df.loc[today_date, "Low"] = p
            else:
                new_row = pd.DataFrame(
                    {
                        "Open": [p],
                        "High": [p],
                        "Low": [p],
                        "Close": [p],
                        "Volume": [v_curr],
                    },
                    index=[today_date],
                )
                df = pd.concat([df, new_row])

            # 거래량 연산
            v_avg5 = float(df["Volume"].iloc[-6:-1].mean()) if len(df) >= 6 else float(df["Volume"].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0

            # 전일비 및 등락률 연산 (KRX 정규장 닻 기준)
            p_diff = p - prev_p
            p_chg = (p_diff / prev_p) * 100 if prev_p > 0 else 0

            if is_kr:
                m_start = now_local.replace(hour=9, minute=0, second=0, microsecond=0)
                m_end = now_local.replace(hour=20, minute=0, second=0, microsecond=0)
                total_minutes = 660
            else:
                m_start = now_local.replace(hour=9, minute=30, second=0, microsecond=0)
                m_end = now_local.replace(hour=16, minute=0, second=0, microsecond=0)
                total_minutes = 390

            if m_start <= now_local <= m_end and now_local.weekday() < 5:
                elapsed = max(10, (now_local - m_start).seconds / 60)
                vol_strength_auto = min(1000, v_ratio / (elapsed / total_minutes))
            else:
                vol_strength_auto = v_ratio

            vol_strength = vol_strength_auto

            today_open = float(df["Open"].iloc[-1])
            today_high = float(df["High"].iloc[-1])
            today_low = float(df["Low"].iloc[-1])
            is_down_trend_v = (p < prev_p) and (p_chg < 0)
            is_candle_bearish = p_chg < 0

            day_candle_range = max(0.01, today_high - today_low)
            upper_tail_len = today_high - p
            is_long_upper_tail = (upper_tail_len >= day_candle_range * 0.35) and (today_high > today_open)

            # 보조지표 연산 (기준: 20/2, 14/6, 14/9)
            delta = df["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val, rsi_prev = rsi_series.iloc[-1], rsi_series.iloc[-2]

            h14, l14 = df["High"].rolling(14).max(), df["Low"].rolling(14).min()
            will_series = (h14 - df["Close"]) / (h14 - l14 + 1e-10) * -100
            will_val, will_prev = will_series.iloc[-1], will_series.iloc[-2]

            macd = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
            sig_line = macd.ewm(span=9).mean()
            m_l, s_l, m_p, s_p = macd.iloc[-1], sig_line.iloc[-1], macd.iloc[-2], sig_line.iloc[-2]

            curr_diff = m_l - s_l
            prev_diff = m_p - s_p
            is_macd_bullish = m_l > s_l

            is_macd_accelerating = is_macd_bullish and (curr_diff >= prev_diff)
            is_macd_decelerating = is_macd_bullish and (curr_diff < prev_diff)
            is_macd_recovering = (not is_macd_bullish) and (curr_diff > prev_diff)
            is_macd_reverse_deepening = (not is_macd_bullish) and (curr_diff <= prev_diff)

            df["MA5"] = df["Close"].rolling(5).mean()
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA60"] = df["Close"].rolling(60).mean()
            df["MA120"] = df["Close"].rolling(120).mean()
            df["Std"] = df["Close"].rolling(20).std()

            mid_line = float(df["MA20"].iloc[-1]) if pd.notna(df["MA20"].iloc[-1]) else p
            std_val = float(df["Std"].iloc[-1]) if pd.notna(df["Std"].iloc[-1]) else 0.0
            up_b = mid_line + (std_val * 2)
            low_b = mid_line - (std_val * 2)

            if len(df) >= 2 and pd.notna(df["MA20"].iloc[-2]) and pd.notna(df["Std"].iloc[-2]):
                prev_mid_line = float(df["MA20"].iloc[-2])
                prev_std_val = float(df["Std"].iloc[-2])
                prev_up_b = prev_mid_line + (prev_std_val * 2)
                prev_low_b = prev_mid_line - (prev_std_val * 2)
                prev_bandwidth = ((prev_up_b - prev_low_b) / prev_mid_line) * 100 if prev_mid_line > 0 else 0
            else:
                prev_up_b = up_b
                prev_bandwidth = 0

            bandwidth = ((up_b - low_b) / mid_line) * 100 if mid_line > 0 else 0
            is_band_expanding = (up_b > prev_up_b) and (bandwidth >= prev_bandwidth)

            ma5_val = float(df["MA5"].iloc[-1]) if (len(df) >= 5 and pd.notna(df["MA5"].iloc[-1])) else p
            ma60_val = float(df["MA60"].iloc[-1]) if (len(df) >= 60 and pd.notna(df["MA60"].iloc[-1])) else mid_line
            ma120_val = float(df["MA120"].iloc[-1]) if (len(df) >= 120 and pd.notna(df["MA120"].iloc[-1])) else ma60_val
            is_ma5_safe = p >= ma5_val
            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            bias_ma20 = ((p - mid_line) / mid_line) * 100 if mid_line > 0 else 0

            is_ma_tangled = False
            if not (ma5_val > mid_line > ma60_val > ma120_val or ma5_val < mid_line < ma60_val < ma120_val):
                is_ma_tangled = True

            bb_bot_check = p <= (low_b * 1.02)
            rsi_cold_check = rsi_val <= 35
            will_cold_check = will_val <= -80
            temp_bottom_score = int(bb_bot_check) + int(rsi_cold_check) + int(will_cold_check)

            if is_ma_tangled and is_ma5_safe and vol_strength >= 75.0 and bandwidth >= 12.0 and (rsi_val <= 35 or temp_bottom_score >= 2 or (p_chg >= 0.0 and p >= mid_line)):
                is_ma_tangled = False

            ma20_safe_threshold = mid_line * 1.002
            is_ma20_buffer_safe = p >= ma20_safe_threshold

            ob_ratio_val = ob_data.get("ratio")
            has_manual_ob = manual_ask > 0 and manual_bid > 0
            ob_ratio_available = ob_ratio_val is not None and float(ob_ratio_val) > 0 and has_manual_ob
    
            if not is_kr and not has_manual_ob:
                ob_status_msg = "💡 <b>미장 자동 호가 미제공</b> (수동 입력 시에만 HTS 잔량비 연산 가동)"
                is_orderbook_safe = True
            elif ob_ratio_available:
                ob_ratio_val = float(ob_ratio_val)
                ask_formatted = f"{ob_data.get('ask', 0.0):,.0f}"
                bid_formatted = f"{ob_data.get('bid', 0.0):,.0f}"
                if ob_ratio_val > 2.8:
                    ob_status_msg = f"🚨 <b>[매도벽 과다 저항]</b> 잔량비 <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted}주 / 매수:{bid_formatted}주)"
                    is_orderbook_safe = False
                elif ob_ratio_val >= 1.5:
                    ob_status_msg = f"🟡 <b>[매도 우위 공방]</b> 잔량비 <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted}주 / 매수:{bid_formatted}주)"
                    is_orderbook_safe = False
                elif ob_ratio_val >= 1.0:
                    ob_status_msg = f"⚖️ <b>[정상 공방 호가]</b> 잔량비 <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted}주 / 매수:{bid_formatted}주)"
                    is_orderbook_safe = True
                else:
                    ob_status_msg = f"🟢 <b>[매수 우위 호가]</b> 잔량비 <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted}주 / 매수:{bid_formatted}주)"
                    is_orderbook_safe = True
            elif manual_ask > 0 or manual_bid > 0:
                ob_status_msg = "⚠️ <b>[호가 입력 불완전]</b> 총매도·총매수잔량을 모두 입력해야 합니다."
                is_orderbook_safe = False
            else:
                ob_status_msg = "💡 <b>HTS 총매도·매수잔량을 입력하면 입력값 기준 호가 분석을 가동합니다.</b>"
                is_orderbook_safe = True

            if bandwidth < 12.0:
                is_bandwidth_ok = False
                bw_diag_msg = f"밴드폭 극소({bandwidth:.1f}%) 에너지 응축 중"
                squeeze_info_str = f"<br>• ⚡ <b>[밴드폭 극소({bandwidth:.1f}%)]</b> 에너지가 바짝 응축 중이오."
            elif 12.0 <= bandwidth < 20.0:
                if p >= ma5_val:
                    is_bandwidth_ok = True
                    bw_diag_msg = f"밴드폭 응축돌파({bandwidth:.1f}%)"
                    squeeze_info_str = f"<br>• 🟢 <b>[밴드폭 응축돌파({bandwidth:.1f}%)]</b> 상방 분출 초입."
                else:
                    is_bandwidth_ok = False
                    bw_diag_msg = f"밴드폭 응축({bandwidth:.1f}%) 돌파 대기"
                    squeeze_info_str = f"<br>• ⏳ <b>[밴드폭 응축({bandwidth:.1f}%)]</b> 돌파 대기."
            else:
                is_bandwidth_ok = True
                bw_diag_msg = f"밴드폭 넉넉함({bandwidth:.1f}%)"
                squeeze_info_str = f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 진폭 확보."

            candle_range = max(0.01, today_high - today_low)
            lower_tail = min(today_open, p) - today_low
            body_len = abs(today_open - p)

            is_pure_bullish_candle = p >= today_open
            is_bottom_lower_tail = ((lower_tail >= candle_range * 0.45) or (lower_tail >= body_len * 1.3)) and (p_chg >= 0.0)
            is_valid_bottom_candle = (is_pure_bullish_candle or is_bottom_lower_tail) and (not is_down_trend_v)

            is_trend_lower_tail = ((lower_tail >= candle_range * 0.45) or (lower_tail >= body_len * 1.3)) and (p >= ma5_val) and (p_chg >= -1.5)
            is_valid_buy_candle = is_pure_bullish_candle or is_trend_lower_tail
            is_bearish_candle = (p < today_open) and (not is_trend_lower_tail)

            tr1 = df["High"] - df["Low"]
            tr2 = (df["High"] - df["Close"].shift(1)).abs()
            tr3 = (df["Low"] - df["Close"].shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr_14 = float(tr.rolling(14).mean().iloc[-1]) if len(df) >= 14 else float(tr.mean())

            atr_ratio = (atr_14 / ma5_val) if ma5_val > 0 else 0.03
            dynamic_stop_rate = max(0.02, min(0.05, atr_ratio))
            dynamic_stop_pct = dynamic_stop_rate * 100
            dynamic_stop_price = ma5_val * (1 - dynamic_stop_rate)

            prev_low = float(df["Low"].iloc[-61:-1].min()) if len(df) > 60 else float(df["Low"].min())
            is_below_ma5 = p < ma5_val

            if not is_below_ma5:
                stop_loss_price = dynamic_stop_price
                stop_loss_label = f"🛡️ 단기 추세 체크포인트: 5일선 -{dynamic_stop_pct:.1f}% 이탈 시 관망({stop_loss_price:{fmt_p}}{currency})"
            else:
                stop_loss_price = prev_low
                stop_loss_label = f"🚨 칼손절 경보: 전저점 이탈 마지노선({stop_loss_price:{fmt_p}}{currency})"

            defense_link_idx = min(21, len(df))
            raw_defense = float(df["High"].iloc[-defense_link_idx:-1].max()) * 0.93 if len(df) > 1 else p * 0.93
            defense_line = max(raw_defense, mid_line)
            wait_line = low_b * 1.02

            is_bullish = ma5_val > mid_line and mid_line > ma60_val and ma60_val > ma120_val
            is_bearish = ma5_val < mid_line and mid_line < ma60_val and ma60_val < ma120_val
            is_down_trend_structural = is_bearish or (p < mid_line and mid_line <= ma60_val)
            is_ma5_safe = p >= ma5_val

            ma5_str = f"{ma5_val:{fmt_p}}{currency}"
            ma20_str = f"{mid_line:{fmt_p}}{currency}"
            ma60_str = f"{ma60_val:{fmt_p}}{currency}"
            ma120_str = f"{ma120_val:{fmt_p}}{currency}"

            if is_bullish:
                trend_status = "🔥 <b>[대세 정배열]</b> 완벽한 우상향 성벽 구축 완료"
            elif is_bearish:
                trend_status = "⚠️ <b>[대세 역배열]</b> 지하실 향하는 하락 추세"
            elif ma5_val > mid_line:
                trend_status = "🌱 <b>[단기 반등 초입]</b> 5일선이 20일선 돌파!"
            elif ma5_val < mid_line:
                trend_status = "📉 <b>[단기 조정 국면]</b> 5일선이 20일선 밑으로 밀림"
            else:
                trend_status = "⚖️ <b>[추세 혼조]</b> 방향 탐색 중"

            def generate_ma_hierarchy(df, current_price):
              try:
                ma_5 = df["MA5"].iloc[-1]
                ma_20 = df["MA20"].iloc[-1]
                ma_60 = df["MA60"].iloc[-1]
                ma_120 = df["MA120"].iloc[-1]
              except Exception:
                ma_5, ma_20, ma_60, ma_120 = 0, 0, 0, 0
              
              ma_dict = {"120일": ma_120, "60일": ma_60, "20일": ma_20, "5일": ma_5, "현재가": current_price}
              sorted_items = sorted(ma_dict.items(), key=lambda x: x[1], reverse=True)
              hierarchy_parts = [f'<span style="color:#ff6600; font-weight:bold;">현재가({current_price:{fmt_p}}{currency})</span>' if name == "현재가" else name for name, price in sorted_items]
              return f"&nbsp;&nbsp;&nbsp;&nbsp;<b>[이평선 층위]</b> {' > '.join(hierarchy_parts)}"

            ma_price_summary = f"<br>• 📌 <b>[주요 이동평균선 현황]</b><br>&nbsp;&nbsp;&nbsp;<span style='color:#D32F2F; font-weight:bold;'>🔴 5일선: {ma5_str} (이격: {bias_ma5:+.1f}%)</span> | <span style='color:#1976D2;'>🔵 20일선: {ma20_str}</span> | <span style='color:#388E3C;'>🟢 60일선: {ma60_str}</span> | <span style='color:#7B1FA2;'>🟣 120일선: {ma120_str}</span><br>"
            ma_price_summary += generate_ma_hierarchy(df, p)

            core_vault = {
                "005930": "삼성전자", "000660": "SK하이닉스", "033100": "제룡전기", "257720": "실리콘투",
                "058610": "에스피지", "010140": "삼성중공업", "068270": "셀트리온", "272210": "한화시스템",
                "101490": "에스앤에스텍", "051600": "한전KPS", "064350": "현대로템", "032300": "솔리드", "050890": "솔리드"
            }
            final_display_name = core_vault.get(symbol.zfill(6), f"국내종목 ({symbol})")
            safe_display_name = html.escape(final_display_name)

            target_price_100 = up_b
            is_target_reached = p >= (target_price_100 * 0.98)
            is_band_riding = is_target_reached and is_band_expanding and is_ma5_safe and (not is_bearish_candle)

            # ==================================================================
            # ★ [상단 대형 현재주가현황 전광판]
            # ==================================================================
            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(
                f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>"
                f"<p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{safe_display_name}</p>"
                f"<p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>",
                unsafe_allow_html=True,
            )

            # 3열 핵심 가격 카드
            c_wait, c_def, c_tgt = st.columns(3)
            with c_wait:
                wait_diff = ((p - wait_line) / wait_line) * 100 if wait_line > 0 else 0
                wait_color = "#E65100" if p <= wait_line * 1.03 else "#1565C0"
                st.markdown(f"<div class='price-card' style='border-top: 5px solid {wait_color}; margin-top: 10px;'><div style='font-size: 20px; color: #37474F;'>🎯 공략대기선 (볼린저 바닥선)</div><div style='font-size: 30px; color: {wait_color}; margin: 8px 0;'>{wait_line:{fmt_p}}{currency}</div><div style='font-size: 17px; color: {wait_color};'>바닥 상회 ({wait_diff:+.1f}%)</div></div>", unsafe_allow_html=True)
            with c_def:
                def_diff = ((p - defense_line) / defense_line) * 100 if defense_line > 0 else 0
                def_color = "#2E7D32" if p >= defense_line else "#D32F2F"
                st.markdown(f"<div class='price-card' style='border-top: 5px solid {def_color}; margin-top: 10px;'><div style='font-size: 20px; color: #37474F;'>🛡️ 성벽 (최후 방어선)</div><div style='font-size: 30px; color: {def_color}; margin: 8px 0;'>{defense_line:{fmt_p}}{currency}</div><div style='font-size: 17px; color: {def_color};'>성벽 수성 ({def_diff:+.1f}%)</div></div>", unsafe_allow_html=True)
            with c_tgt:
                tgt_diff = ((target_price_100 - p) / p) * 100 if p > 0 else 0
                tgt_color = "#6A1B9A" if is_band_riding else "#1565C0"
                st.markdown(f"<div class='price-card' style='border-top: 5px solid {tgt_color}; margin-top: 10px;'><div style='font-size: 20px; color: #37474F;'>🏆 수확 목표선 (볼린저 상단)</div><div style='font-size: 30px; color: {tgt_color}; margin: 8px 0;'>{target_price_100:{fmt_p}}{currency}</div><div style='font-size: 17px; color: {tgt_color};'>상승 여력 {tgt_diff:+.1f}%</div></div>", unsafe_allow_html=True)

            st.write("")
            is_positive_day = p >= prev_p if prev_p > 0 else False

            if vol_strength >= 150:
                v_status, v_adv = "과열폭발", f"🔥 <b>[화력폭발]</b> 강도 {vol_strength:.1f}점!"
            elif vol_strength >= 100:
                v_status, v_adv = "매집시작", f"🚀 <b>[매집시작]</b> 강도 {vol_strength:.1f}점!"
            else:
                v_status, v_adv = "거래 숨고르기", f"🧊 <b>[거래 숨고르기]</b> 강도 {vol_strength:.1f}점!"

            st.markdown(
                f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량 전환: {v_status} (실시간 {v_ratio:.1f}% / 5일평균대비)</div>"
                f"<div style='font-size:18px; color:#37474F; background:#FFFFFF; padding:10px; border-radius:8px; border-left:6px solid #1976D2; margin-bottom:10px;'>{v_adv}</div>"
                f"<div style='font-size: 18px; color: #37474F; background: #FFFFFF; padding: 10px; border-radius: 8px; border-left: 6px solid #FF9800;'>🎯 <b>[호가창 잔량 공방]</b> {ob_status_msg}</div></div>",
                unsafe_allow_html=True,
            )

            # 지표 연산
            low_b_val = low_b.iloc[-1] if hasattr(low_b, "iloc") else low_b
            b_val = 1 if df["Close"].iloc[-1] <= (low_b_val * 1.02) else 0
            r_val = 1 if rsi_series.iloc[-1] <= 30 else 0
            w_val = 1 if will_series.iloc[-1] <= -80 else 0
            bottom_score = int(b_val + r_val + w_val)

            rsi_pullback_val = 1 if (40.0 <= rsi_series.iloc[-1] <= 60.0) else 0
            will_pullback_val = 1 if (-60.0 <= will_series.iloc[-1] <= -40.0) else 0
            bb_center_val = 1 if (mid_line * 0.98 <= p <= mid_line * 1.02) else 0
            pullback_rebound_score = int(rsi_pullback_val + will_pullback_val + bb_center_val)

            is_stop_loss_triggered = (user_avg_price > 0 and p < stop_loss_price)

            if is_stop_loss_triggered:
                final_code = "STOP_LOSS_ALERT"
                sig = "🚨 [비상 손절] 방어선 붕괴! 전량 칼손절 후퇴!"
                col = "#D32F2F"
                final_adv = "• <b>[최종 결론]</b> 손절 마지노선 이탈! 즉시 전량 칼손절 후퇴하시게."
            elif is_long_upper_tail and (p >= defense_line or p >= mid_line):
                final_code = "LONG_TAIL_WARNING"
                sig = "🟡 [위꼬리 저항 경계] 고점 매물 출회"
                col = "#F57C00"
                final_adv = "• <b>[최종 결론]</b> 긴 위꼬리 저항 포착! 섣부른 추격매수 금지."
            elif is_band_riding:
                final_code = "BAND_RIDING_HARVEST"
                sig = "🟣 [1차 수확 / 잔여 밴드 추종] 상방 확장 중!"
                col = "#6A1B9A"
                final_adv = "• <b>[최종 결론]</b> 50% 익절 후 5일선 기준 잔여 물량 홀딩."
            elif p >= (target_price_100 * 0.98) or is_target_reached:
                final_code = "RED_SELL_TARGET"
                sig = "🔴 [목표 도달] 수학 목표선 저항! 50% 수확!"
                col = "#D32F2F"
                final_adv = "• <b>[최종 결론]</b> 상단 목표 도달 완료. 50% 물량 기계적 수확."
            elif p >= defense_line:
                final_code = "BREAKOUT_ATTACK"
                sig = "🟢 [성벽 위 진격] 상방 랠리 추종 구역"
                col = "#2E7D32"
                final_adv = "• <b>[최종 결론]</b> 성벽 위 안착 진격 중. 5일선 사수하며 추세 홀딩."
            else:
                final_code = "WAIT_GENERAL"
                sig = "🟡 [관망] 조건 미충족 / 뇌동매매 금지"
                col = "#FBC02D"
                final_adv = "• <b>[최종 결론]</b> 조건 미충족 상태이므로 냉정하게 관망 유지."

            st.markdown(f"<div class='signal-box' style='background-color: {col};'><div class='signal-text'>{sig}</div><div class='signal-subtext'>{final_adv}</div></div>", unsafe_allow_html=True)

            indicator_verify_text = f"{ma_price_summary}<br>• <b>[추세 정밀 판독]:</b> {trend_status}<br>• <b>[지표 검증 연산]</b><br>• <b>진바닥 점수:</b> {bottom_score}점 | <b>눌림목 점수:</b> {pullback_rebound_score}점 {squeeze_info_str}"
            holder_guide_msg = f"현재가({p:{fmt_p}}{currency}) 기준 성벽({defense_line:{fmt_p}}{currency})과 5일선({ma5_val:{fmt_p}}{currency}) 사수 여부를 냉정히 주시하시게."
            ma5_guide_text = f"5일선({ma5_val:{fmt_p}}{currency}) 종가 이탈 여부를 칼같이 체크하시게."
            def_status = f"성벽({defense_line:{fmt_p}}{currency}) 방어선 유효."
            base_macd_desc = "<b>⚙️ MACD 엔진 가동 중</b>"

            st.markdown(
                f"""<div class='trend-card'><div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
                <div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{ma5_guide_text}</span></div>
                <div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>2. 성벽 사수 및 공방 확인</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{def_status}</span></div>
                <div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>3. 중장기 추세 진단 및 지표 동조 현황</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{indicator_verify_text}</span></div>
                <div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>4. 엔진(MACD) 확인</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{base_macd_desc}</span></div>
                <div style='margin-bottom: 25px;'><span style='color: #D32F2F; font-weight: 900; font-size: 24px;'>5. 🛡️ [보유자 전용] 실전 행동 가이드</span><br><span style='color: #2E7D32; font-weight: bold; font-size: 20px;'>👉 {holder_guide_msg}</span></div>
                <hr style='border:1px solid #FFEBEE; margin: 20px 0;'><div class='final-msg'>{final_adv}</div></div>""",
                unsafe_allow_html=True,
            )

            st.divider()

            # 하단 4대 핵심 지표 박스
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger</p><p class='ind-diag'>밴드폭: {bandwidth:.1f}%<br>{bw_diag_msg}</p></div>", unsafe_allow_html=True)
            with i2:
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (매수 온도)</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{rsi_val:.2f}</p><p class='ind-diag'>지표 온도 정상 작동 중</p></div>", unsafe_allow_html=True)
            with i3:
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{will_val:.2f}</p><p class='ind-diag'>민감 반전 지표 연산 중</p></div>", unsafe_allow_html=True)
            with i4:
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (추세 엔진)</p><p class='ind-diag'>{base_macd_desc}</p></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"👵 아이구! 오류: {e}")
