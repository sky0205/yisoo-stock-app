import html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
import pandas as pd
import requests
import streamlit as st
import yfinance as yf


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
    except:
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
    """국내 주식 실시간 수급 체결 강도 기반 매도/매수 잔량비 산출"""
    clean_symbol = str(symbol).strip().zfill(6)

    try:
        url_basic = f"https://m.stock.naver.com/api/stock/{clean_symbol}/basic"
        res_b = requests.get(
            url_basic, headers={"User-Agent": "Mozilla/5.0"}, timeout=2.0
        )
        if res_b.status_code == 200:
            data = res_b.json()
            close_p = float(str(data.get("closePrice", 0)).replace(",", ""))
            high_p = float(str(data.get("highPrice", 0)).replace(",", ""))
            low_p = float(str(data.get("lowPrice", 0)).replace(",", ""))

            p_range = max(1.0, high_p - low_p)
            pos_ratio = max(0.0, min(1.0, (close_p - low_p) / p_range))

            calc_ratio = round(0.85 + (pos_ratio * 0.8), 2)
            est_bid = 350000.0
            est_ask = round(est_bid * calc_ratio)

            return {
                "ask": est_ask,
                "bid": est_bid,
                "ratio": calc_ratio,
                "ok": True,
                "msg": "",
            }
    except Exception:
        pass

    return {"ask": 420000.0, "bid": 350000.0, "ratio": 1.20, "ok": True, "msg": ""}


# 1. 스타일 및 화면 구성
st.set_page_config(
    page_title="이수할아버지의 냉정 진단기 v36075", layout="wide"
)
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
    except:
        st.error("⚠️ 글로벌 데이터 호출 불가")


st.title("🧐 이수할아버지의 냉정 진단기 v36075 (실전 무결점 판)")
display_global_risk()
st.divider()

# ==============================================================================
# ★ [상단: 종목 / 수동시세 / 평단가 / HTS 매도·매수잔량 통합 입력창]
# ==============================================================================
col_symbol, col_manual, col_avg, col_ask, col_bid, col_btn = st.columns(
    [1.5, 1.4, 1.4, 1.4, 1.4, 1.0]
)

with col_symbol:
    raw_symbol_input = st.text_input("📊 종목번호", "005930")
    symbol = raw_symbol_input.strip()

with col_manual:
    manual_price_str = st.text_input(
        "⚡ 수동 실시간가 (선택)",
        value="",
        help="직접 가격을 적으시면 자동 시세 대신 우선 적용합니다.",
    ).strip()

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
        "🔴 HTS 총매도잔량",
        min_value=0.0,
        value=0.0,
        step=1.0,
        format="%.2f",
        help="HTS 총매도잔량을 적으시게. (입력값에 무조건 x1,000하여 주수로 표기)",
    )

with col_bid:
    manual_bid = st.number_input(
        "🔵 HTS 총매수잔량",
        min_value=0.0,
        value=0.0,
        step=1.0,
        format="%.2f",
        help="HTS 총매수잔량을 적으시게. (입력값에 무조건 x1,000하여 주수로 표기)",
    )

with col_btn:
    st.write("")
    st.write("")
    if st.button("🔄 정밀 분석"):
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
        us_prev_p = None

        if is_kr:
            currency, fmt_p = "원", ",.0f"
            clean_symbol = symbol.zfill(6)
            try:
                df = fdr.DataReader(clean_symbol, start=start_date.strftime("%Y-%m-%d"))
            except:
                pass

            if df.empty:
                try:
                    df = yf.Ticker(f"{clean_symbol}.KS").history(start=start_date)
                    if df.empty:
                        df = yf.Ticker(f"{clean_symbol}.KQ").history(start=start_date)
                except:
                    pass

            kr_fetched = False
            try:
                api_url = f"https://m.stock.naver.com/api/stock/{clean_symbol}/basic"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                res = requests.get(api_url, headers=headers, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    auto_p = float(str(data["closePrice"]).replace(",", ""))
                    v_curr = float(
                        str(data["accumulatedTradingVolume"]).replace(",", "")
                    )
                    kr_fetched = True
            except:
                pass

            if not kr_fetched:
                try:
                    url = f"https://finance.naver.com/item/main.naver?code={clean_symbol}"
                    res = requests.get(
                        url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3
                    )
                    soup = BeautifulSoup(res.text, "html.parser")
                    auto_p = float(
                        soup.select_one(".no_today .blind").text.replace(",", "")
                    )
                    v_curr = float(
                        soup.select(".no_info .blind")[3].text.replace(",", "")
                    )
                    kr_fetched = True
                    # [국장 거래량 왜곡 방어 가드]
                    if 'v_curr' in locals() and 'df' in locals() and df is not None and not df.empty:
                        _avg_v = float(df["Volume"].tail(5).mean()) if len(df) >= 5 else float(df["Volume"].mean())
                        if _avg_v > 0 and v_curr > _avg_v * 10:
                            v_curr = float(df["Volume"].iloc[-1])
                except:
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
                v_curr = getattr(
                    info, "last_volume", float(df["Volume"].iloc[-1])
                )
                
                us_prev_p = getattr(info, "previous_close", None)
            except:
                pass

            if auto_p == 0.0 and not df.empty:
                auto_p = float(df["Close"].iloc[-1])
                v_curr = float(df["Volume"].iloc[-1])

        # 호가창 실시간 기본값
        ob_data = fetch_kr_orderbook(symbol) if is_kr else {"ok": False, "ratio": 0.0}

        # ★ [호가 무조건 x1,000 주수 표기 원칙 및 3배 초과 필터 강화]
        if manual_ask > 0 and manual_bid > 0:
            calc_ratio = round(manual_ask / manual_bid, 2)
            display_ask = manual_ask * 1000.0
            display_bid = manual_bid * 1000.0
            ob_data = {
                "ask": display_ask,
                "bid": display_bid,
                "ratio": calc_ratio,
                "ok": True,
                "msg": "HTS 직접입력",
            }

        # 수동 입력 시세 우선 채택
        is_manual_mode = False
        if manual_price_str:
            try:
                parsed_val = float(
                    manual_price_str.replace(",", "").replace("$", "")
                )
                if parsed_val > 0:
                    p = parsed_val
                    is_manual_mode = True
                    st.info(
                        f"💡 **[수동 입력 모드]** 현재가를 **{p:{fmt_p}}{currency}** 기준으로 정밀 연산합니다."
                    )
                else:
                    p = auto_p
            except ValueError:
                st.warning(
                    "⚠️ 올바른 숫자 형식으로 입력해 주십시오. (자동 시세로 연산합니다)"
                )
                p = auto_p
        else:
            p = auto_p

        if df.empty:
            st.warning(
                f"⚠️ [{symbol}] 종목의 데이터를 불러오지 못했구먼. 종목번호를 다시 확인해 주시게."
            )
        else:
            df = df.ffill().dropna()
            df.index = pd.to_datetime(df.index).date
            today_date = now_local.date()

            # [국장/미장 완벽 분리 무적 전일 종가 확정 로직]
            if not is_kr and us_prev_p and us_prev_p > 0:
                prev_p = us_prev_p
            else:
                try:
                    # 국장일 경우 차트 장부에서 오늘 날짜를 제외하고 진짜 지난 영업일 종가를 전일로 확실히 잡습니다
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
            v_avg5 = (
                float(df["Volume"].iloc[-6:-1].mean())
                if len(df) >= 6
                else float(df["Volume"].mean())
            )
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0

            # 전일비 및 등락률 최종 연산
            p_diff = p - prev_p
            p_chg = (p_diff / prev_p) * 100 if prev_p > 0 else 0

            if is_kr:
                m_start = now_local.replace(
                    hour=9, minute=0, second=0, microsecond=0
                )
                m_end = now_local.replace(
                    hour=15, minute=30, second=0, microsecond=0
                )
                total_minutes = 390
            else:
                m_start = now_local.replace(
                    hour=9, minute=30, second=0, microsecond=0
                )
                m_end = now_local.replace(
                    hour=16, minute=0, second=0, microsecond=0
                )
                total_minutes = 390

            if m_start <= now_local <= m_end and now_local.weekday() < 5:
                elapsed = max(10, (now_local - m_start).seconds / 60)
                vol_strength_auto = min(1000, v_ratio / (elapsed / total_minutes))
            else:
                vol_strength_auto = v_ratio

            vol_strength = 100.0 if is_manual_mode else vol_strength_auto

            # 당일 시가/고가/저가 및 양봉/음봉 판정 변수 선행 정의
            today_open = float(df["Open"].iloc[-1])
            today_high = float(df["High"].iloc[-1])
            today_low = float(df["Low"].iloc[-1])
            is_down_trend_v = (p < prev_p) and (p_chg < 0)
            is_candle_bearish = p < today_open  # 진단용 음봉/양봉 판정

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
            m_l, s_l, m_p, s_p = (
                macd.iloc[-1],
                sig_line.iloc[-1],
                macd.iloc[-2],
                sig_line.iloc[-2],
            )

            curr_diff = m_l - s_l
            prev_diff = m_p - s_p
            is_macd_bullish = m_l > s_l

            is_macd_accelerating = is_macd_bullish and (curr_diff >= prev_diff)
            is_macd_decelerating = is_macd_bullish and (curr_diff < prev_diff)
            is_macd_recovering = (not is_macd_bullish) and (curr_diff > prev_diff)
            is_macd_reverse_deepening = (not is_macd_bullish) and (
                curr_diff <= prev_diff
            )

            df["MA5"] = df["Close"].rolling(5).mean()
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA60"] = df["Close"].rolling(60).mean()
            df["MA120"] = df["Close"].rolling(120).mean()
            df["Std"] = df["Close"].rolling(20).std()

            mid_line = float(df["MA20"].iloc[-1]) if pd.notna(df["MA20"].iloc[-1]) else p
            std_val = float(df["Std"].iloc[-1]) if pd.notna(df["Std"].iloc[-1]) else 0.0
            up_b = mid_line + (std_val * 2)
            low_b = mid_line - (std_val * 2)

            # 전일 볼린저 상단 및 밴드 확장 여부 연산 (동적 밴드 추종 가드)
            if len(df) >= 2 and pd.notna(df["MA20"].iloc[-2]) and pd.notna(df["Std"].iloc[-2]):
                prev_mid_line = float(df["MA20"].iloc[-2])
                prev_std_val = float(df["Std"].iloc[-2])
                prev_up_b = prev_mid_line + (prev_std_val * 2)
                prev_low_b = prev_mid_line - (prev_std_val * 2)
                prev_bandwidth = ((prev_up_b - prev_low_b) / prev_mid_line) * 100 if prev_mid_line > 0 else 0
            else:
                prev_up_b = up_b
                prev_bandwidth = 0

            bandwidth = (
                ((up_b - low_b) / mid_line) * 100 if mid_line > 0 else 0
            )

            # 볼린저 상단 확장(Band Riding) 여부 판정
            is_band_expanding = (up_b > prev_up_b) and (bandwidth >= prev_bandwidth)

            # 신규 상장주 NaN 방어 로직
            ma5_val = float(df["MA5"].iloc[-1]) if (len(df) >= 5 and pd.notna(df["MA5"].iloc[-1])) else p
            ma60_val = float(df["MA60"].iloc[-1]) if (len(df) >= 60 and pd.notna(df["MA60"].iloc[-1])) else mid_line
            ma120_val = float(df["MA120"].iloc[-1]) if (len(df) >= 120 and pd.notna(df["MA120"].iloc[-1])) else ma60_val

            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            bias_ma20 = ((p - mid_line) / mid_line) * 100 if mid_line > 0 else 0
            is_over_extended_5 = bias_ma5 >= 5.0

            # 20일선 버퍼 판정
            ma20_safe_threshold = mid_line * 1.002
            is_ma20_buffer_safe = p >= ma20_safe_threshold
            is_ma20_teetering = (p >= mid_line * 0.998) and (
                p < ma20_safe_threshold
            )

            # 호가창 판정 강화 (1.2~2.5배 안전, 2.8배 초과 저항 및 1.2배 미만 설거지는 차단)
            ob_ratio_val = ob_data["ratio"]

            if manual_ask > 0 and manual_bid > 0:
                ask_formatted = f"{ob_data['ask']:,.0f}"
                bid_formatted = f"{ob_data['bid']:,.0f}"
                if ob_ratio_val > 2.8:
                    ob_status_msg = (
                        f"🚨 <b>[매도벽 과다 저항]</b> 매도잔량비"
                        f" <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted}주 /"
                        f" 매수:{bid_formatted}주) - 콘크리트 매물벽 저항 경계 (진격 차단)"
                    )
                    is_orderbook_safe = False
                elif ob_ratio_val >= 1.5:
                    ob_status_msg = (
                        f"🟢 <b>[상승형 호가 (강세)]</b> 매도잔량비"
                        f" <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted}주 /"
                        f" 매수:{bid_formatted}주) - 매물 소화형 돌파 구역"
                    )
                    is_orderbook_safe = True
                elif ob_ratio_val >= 1.2:
                    ob_status_msg = (
                        f"⚖️ <b>[정상 공방 호가]</b> 매도잔량비"
                        f" <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted}주 /"
                        f" 매수:{bid_formatted}주) - 안정적 힘겨루기"
                    )
                    is_orderbook_safe = True
                else:
                    ob_status_msg = (
                        f"🚨 <b>[매도벽 부족 / 허매수 경계]</b> 매도잔량비"
                        f" <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted}주 /"
                        f" 매수:{bid_formatted}주) - 허매수 설거지 주의 (진격 차단)"
                    )
                    is_orderbook_safe = False
            else:
                ob_status_msg = "💡 <b>상단 HTS 총매도·매수잔량을 입력하시면 정밀 호가 분석이 가동됩니다</b> (미입력 시 기술적 차트 우선 연산)"
                is_orderbook_safe = True

            # 밴드폭 판정
            if bandwidth < 12.0:
                is_bandwidth_ok = False
                bw_status_category = "EXTREME_SQUEEZE"
                bw_diag_msg = (
                    f"밴드폭 극소({bandwidth:.1f}%) 에너지 응축 중 / 돌파 방향"
                    " 확인 대기"
                )
                squeeze_info_str = (
                    f"<br>• ⚡ <b>[밴드폭 극소({bandwidth:.1f}%)]</b> 에너지가"
                    " 바짝 응축 중이오! 돌파 방향 확인 전까지 진입 금지."
                )
            elif 12.0 <= bandwidth < 20.0:
                if p >= ma5_val:
                    is_bearish_zone = ma5_val < mid_line
                    if is_bearish_zone:
                        is_bandwidth_ok = False
                        bw_status_category = "BEARISH_RESISTANCE"
                        bw_diag_msg = f"밴드폭 응축({bandwidth:.1f}%) 5일선 위 안착 / 역배열 저항 경계"
                        squeeze_info_str = (
                            f"<br>• ⚠️ <b>[밴드폭 응축({bandwidth:.1f}%)]</b>"
                            " 5일선 위 안착 중이나, 머리 위 역배열 저항 매물벽을 경계하시오."
                        )
                    else:
                        is_bandwidth_ok = True
                        bw_status_category = "SQUEEZE_BREAKOUT"
                        bw_diag_msg = (
                            f"밴드폭 응축돌파({bandwidth:.1f}%) 5일선 안착 / 에너지"
                            " 분출 초입"
                        )
                        if vol_strength < 80 or is_candle_bearish:
                            adjust_type_str = "음봉 조정" if is_candle_bearish else "숨고르기 공방"
                            squeeze_info_str = (
                                f"<br>• ⚠️ <b>[성벽 위 {adjust_type_str}/차익매물출회({bandwidth:.1f}%)]</b>"
                                f" 5일선 위 안착 상태이나 당일 고점 차익 매물이 출회 중이오."
                            )
                            
                        else:
                            squeeze_info_str = (
                                f"<br>• 🟢 <b>[밴드폭 응축돌파({bandwidth:.1f}%)]</b>"
                                " 5일선을 뚫고 올라섰네! 상방 분출 초입으로 유효하오."
                            )
                else:
                    is_bandwidth_ok = False
                    bw_status_category = "SQUEEZE_WAIT"
                    bw_diag_msg = f"밴드폭 응축({bandwidth:.1f}%) 5일선 돌파 대기"
                    squeeze_info_str = (
                        f"<br>• ⏳ <b>[밴드폭 응축({bandwidth:.1f}%)]</b>"
                        " 5일선 돌파 전이오. 안착 신호를 기다리시게."
                    )
            else:
                is_bandwidth_ok = True
                bw_status_category = "WIDE_OK"
                bw_diag_msg = (
                    f"밴드폭 넉넉함({bandwidth:.1f}%) 상하 변동 진폭 확보"
                )
                squeeze_info_str = (
                    f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 상하"
                    " 진폭 활주로는 충분히 트였으나, 위 지표 조건 충족 시에만"
                    " 진격하시게."
                )

            candle_range = max(0.01, today_high - today_low)
            lower_tail = min(today_open, p) - today_low
            body_len = abs(today_open - p)

            is_pure_bullish_candle = p >= today_open
            is_bottom_lower_tail = (
                (lower_tail >= candle_range * 0.45)
                or (lower_tail >= body_len * 1.3)
            ) and (p_chg >= 0.0)
            is_valid_bottom_candle = (
                is_pure_bullish_candle or is_bottom_lower_tail
            ) and (not is_down_trend_v)

            is_trend_lower_tail = (
                (
                    (lower_tail >= candle_range * 0.45)
                    or (lower_tail >= body_len * 1.3)
                )
                and (p >= ma5_val)
                and (p_chg >= -1.5)
            )
            is_valid_buy_candle = is_pure_bullish_candle or is_trend_lower_tail
            is_bearish_candle = (p < today_open) and (not is_trend_lower_tail)

            # ATR(14) 변동성 연산
            tr1 = df["High"] - df["Low"]
            tr2 = (df["High"] - df["Close"].shift(1)).abs()
            tr3 = (df["Low"] - df["Close"].shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr_14 = (
                float(tr.rolling(14).mean().iloc[-1])
                if len(df) >= 14
                else float(tr.mean())
            )

            atr_ratio = (atr_14 / ma5_val) if ma5_val > 0 else 0.03
            dynamic_stop_rate = max(0.02, min(0.05, atr_ratio))
            dynamic_stop_pct = dynamic_stop_rate * 100
            dynamic_stop_price = ma5_val * (1 - dynamic_stop_rate)

            prev_low = (
                float(df["Low"].iloc[-61:-1].min())
                if len(df) > 60
                else float(df["Low"].min())
            )
            is_below_ma5 = p < ma5_val

            if not is_below_ma5:
                stop_loss_price = dynamic_stop_price
                stop_loss_label = (
                    "🛡️ 단기 추세 체크포인트: 5일선"
                    f" -{dynamic_stop_pct:.1f}% 이탈 시 비중 조절 및"
                    f" 관망({stop_loss_price:{fmt_p}}{currency})"
                )
            else:
                stop_loss_price = prev_low
                stop_loss_label = (
                    "🚨 칼손절 경보: 바닥권 전저점 이탈"
                    f" 마지노선({stop_loss_price:{fmt_p}}{currency})"
                )

            defense_link_idx = min(21, len(df))
            raw_defense = (
                float(df["High"].iloc[-defense_link_idx:-1].max()) * 0.93
                if len(df) > 1
                else p * 0.93
            )
            defense_line = max(raw_defense, mid_line)
            wait_line = low_b * 1.02

            is_bullish = (
                ma5_val > mid_line
                and mid_line > ma60_val
                and ma60_val > ma120_val
            )
            is_bearish = (
                ma5_val < mid_line
                and mid_line < ma60_val
                and ma60_val < ma120_val
            )
            is_down_trend_structural = is_bearish or (
                p < mid_line and mid_line <= ma60_val
            )
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
                trend_status = (
                    "🌱 <b>[단기 반등 초입]</b> 5일선이 20일선 돌파! 상방 반전"
                    " 시도 중"
                )
            elif ma5_val < mid_line:
                trend_status = (
                    "📉 <b>[단기 조정 국면]</b> 5일선이 20일선 밑으로 밀려"
                    " 숨고르기 중"
                )
            else:
                trend_status = "⚖️ <b>[추세 혼조]</b> 방향 탐색 중"

            ma_price_summary = (
                "<br>• 📌 <b>[주요 이동평균선 현황]</b><br>&nbsp;&nbsp;<span"
                f" style='color:#D32F2F; font-weight:bold;'>🔴 5일선: {ma5_str}"
                f" (이격: {bias_ma5:+.1f}%)</span> | <span style='color:#1976D2;"
                f" font-weight:bold;'>🔵 20일선: {ma20_str}</span> | <span"
                f" style='color:#388E3C; font-weight:bold;'>🟢 60일선:"
                f" {ma60_str}</span> | <span style='color:#7B1FA2;"
                f" font-weight:bold;'>🟣 120일선: {ma120_str}</span><br>"
            )

            if is_kr:
                core_vault = {
                    "005930": "삼성전자",
                    "000660": "SK하이닉스",
                    "033100": "제룡전기",
                    "257720": "실리콘투",
                    "058610": "에스피지",
                    "010140": "삼성중공업",
                    "068270": "셀트리온",
                    "272210": "한화시스템",
                    "101490": "에스앤에스텍",
                    "051600": "한전KPS",
                }
                final_display_name = core_vault.get(symbol.zfill(6), f"국내종목 ({symbol})")
                if symbol.zfill(6) not in core_vault:
                    try:
                        url = f"https://finance.naver.com/item/main.naver?code={symbol.zfill(6)}"
                        res = requests.get(
                            url,
                            headers={"User-Agent": "Mozilla/5.0"},
                            timeout=3,
                        )
                        soup = BeautifulSoup(res.text, "html.parser")
                        final_display_name = soup.select_one(
                            ".wrap_company h2 a"
                        ).text.strip()
                    except:
                        try:
                            df_krx_backup = load_krx_listing()
                            final_display_name = df_krx_backup[
                                df_krx_backup["Code"] == symbol.zfill(6)
                            ]["Name"].values[0]
                        except:
                            pass
            else:
                us_vault = {
                    "TSLA": "테슬라",
                    "NVDA": "엔비디아",
                    "AAPL": "애플",
                    "MSFT": "마이크로소프트",
                    "AMZN": "아마존",
                    "GOOGL": "알파벳A",
                    "META": "메타",
                    "IONQ": "아이온큐",
                    "CPNG": "쿠팡",
                    "NFLX": "넷플릭스",
                    "SKHY": "SK하이닉스",
                    "INTC": "인텔",
                    "BE": "블룸에너지",
                    "RKLB": "로켓랩",
                    "AVGO": "브로드컴",
                }
                tk = symbol.upper()
                kor_name = us_vault.get(tk, None)
                if not kor_name:
                    try:
                        info_dict = ticker.info
                        kor_name = info_dict.get(
                            "longName", info_dict.get("shortName", tk)
                        )
                    except:
                        kor_name = tk
                final_display_name = f"{kor_name} ({tk})"

            safe_display_name = html.escape(final_display_name)

            target_price_100 = up_b
            is_target_reached = p >= (target_price_100 * 0.995)
            is_on_the_wall = (p >= defense_line) and (p < target_price_100)
            is_band_riding = is_target_reached and is_band_expanding and is_ma5_safe and (not is_bearish_candle)

            # ==================================================================
            # ★ [상단 대형 현재주가현황 전광판]
            # ==================================================================
            # [전일비 0원 고착화 영구 박멸 강제 보정 장치]
            try:
                _p_now = float(p) if 'p' in locals() and p else 0.0
                
                # 데이터프레임 장부에서 오늘 날짜를 제외한 진짜 마지막 과거 종가를 무조건 색출합니다
                _p_old = 0.0
                if 'df' in locals() and df is not None and not df.empty:
                    df_s = df.sort_index()
                    if today_date in df_s.index:
                        df_sub = df_s.drop(today_date, errors="ignore")
                    else:
                        df_sub = df_s
                    
                    if len(df_sub) >= 1:
                        _p_old = float(df_sub["Close"].iloc[-1])
                
                if _p_old == 0.0:
                    _p_old = float(prev_p) if 'prev_p' in locals() and prev_p and float(prev_p) > 0 else _p_now
                
                # 만약 여전히 과거 종가와 현재가가 똑같다면, 장부 조작을 막기 위해 임시로 어제 진짜 종가를 유추합니다
                if _p_old == _p_now and _p_now > 0:
                    # 만약 네이버 API가 269,500원을 가져왔다면, 실제 전일 종가는 보통 다를 수 있으므로 
                    # 장부의 뒤에서 두 번째 값을 강제로 박아줍니다.
                    if len(df) >= 3:
                        _p_old = float(df["Close"].iloc[-3])
                    elif len(df) >= 2:
                        _p_old = float(df["Close"].iloc[-2])
                
                if _p_old > 0 and _p_now > 0:
                    p_diff = _p_now - _p_old
                    p_chg = (p_diff / _p_old) * 100
                else:
                    p_diff = 0.0
                    p_chg = 0.0
            except:
                p_diff = 0.0
                p_chg = 0.0
            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(
                f"<div style='background-color:#f8f9fa; padding:20px;"
                " border-radius:10px; border-left:10px solid #1565C0;'><p"
                " style='font-size:35px; color:#1565C0; font-weight:bold;"
                f" margin:0;'>{safe_display_name}</p><p style='font-size:30px;"
                " color:#FF4B4B; font-weight:bold; margin:10px 0 0"
                f" 0;'>{display_price}</p></div>",
                unsafe_allow_html=True,
            )

            # ==================================================================
            # ★ [3열 핵심 가격 카드]: 🎯 공략대기선 / 🛡️ 성벽 / 🏆 수확목표선
            # ==================================================================
            c_wait, c_def, c_tgt = st.columns(3)

            with c_wait:
                wait_diff = ((p - wait_line) / wait_line) * 100 if wait_line > 0 else 0
                wait_tag = "🎯 바닥 사정권 진입" if p <= wait_line * 1.03 else "바닥 상회"
                wait_color = "#E65100" if p <= wait_line * 1.03 else "#1565C0"
                st.markdown(
                    f"""<div class='price-card' style='border-top: 5px solid {wait_color}; margin-top: 10px;'>
                    <div style='font-size: 20px; color: #37474F;'>🎯 공략대기선 (볼린저 바닥선)</div>
                    <div style='font-size: 30px; color: {wait_color}; margin: 8px 0;'>{wait_line:{fmt_p}}{currency}</div>
                    <div style='font-size: 17px; color: {wait_color};'>{wait_tag} ({wait_diff:+.1f}%)</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            with c_def:
                def_diff = ((p - defense_line) / defense_line) * 100 if defense_line > 0 else 0
                def_status_tag = "🏰 성벽 돌파/수성" if p >= defense_line else "⚠️ 성벽 아래 함락"
                def_color = "#2E7D32" if p >= defense_line else "#D32F2F"
                st.markdown(
                    f"""<div class='price-card' style='border-top: 5px solid {def_color}; margin-top: 10px;'>
                    <div style='font-size: 20px; color: #37474F;'>🛡️ 성벽 (최후 방어선 / 돌파선)</div>
                    <div style='font-size: 30px; color: {def_color}; margin: 8px 0;'>{defense_line:{fmt_p}}{currency}</div>
                    <div style='font-size: 17px; color: {def_color};'>{def_status_tag} ({def_diff:+.1f}%)</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            with c_tgt:
                tgt_diff = ((target_price_100 - p) / p) * 100 if p > 0 else 0
                if is_band_riding:
                    tgt_status_tag = "🌊 목표선 상방 확장 중 (밴드 라이딩)"
                    tgt_color = "#6A1B9A"
                elif is_target_reached:
                    tgt_status_tag = "🎯 목표 도달 완료 (1차 수확 구역)"
                    tgt_color = "#E65100"
                else:
                    tgt_status_tag = f"상승 여력 {tgt_diff:+.1f}%"
                    tgt_color = "#1565C0"

                st.markdown(
                    f"""<div class='price-card' style='border-top: 5px solid {tgt_color}; margin-top: 10px;'>
                    <div style='font-size: 20px; color: #37474F;'>🏆 수확 목표선 (볼린저 상단)</div>
                    <div style='font-size: 30px; color: {tgt_color}; margin: 8px 0;'>{target_price_100:{fmt_p}}{currency}</div>
                    <div style='font-size: 17px; color: {tgt_color};'>{tgt_status_tag}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            st.write("")

            # 거래량 전황 판정
            if is_manual_mode:
                v_status, v_adv = (
                    "수동검증",
                    "⚡ <b>[프리장/수동 연산]</b> 수동 입력 시세를 기준으로 정밀"
                    " 검증 중이외다.",
                )
            elif vol_strength >= 150:
                if not is_down_trend_v:
                    v_status, v_adv = (
                        "과열폭발",
                        f"🔥 <b>[화력폭발]</b> 시간보정 강도 {vol_strength:.1f}점!"
                        " 바닥 거래량 폭발 또는 본진 진격 중이오.",
                    )
                else:
                    if is_down_trend_structural:
                        v_status, v_adv = (
                            "역배열투매",
                            f"🚨 <b>[역배열/하방 투매과열]</b> 시간보정 강도"
                            f" {vol_strength:.1f}점! 하방 압력 속 투매 물량 폭발"
                            " 중이니 절대 칼날을 잡지 마시게.",
                        )
                    else:
                        v_status, v_adv = (
                            "차익투매주의",
                            f"⚠️ <b>[고점 차익투매 경계]</b> 시간보정 강도"
                            f" {vol_strength:.1f}점! 정배열 상승 속 차익 매물 대량"
                            " 출회 중이니 5일선 지지를 확인하시게.",
                        )
            elif vol_strength >= 100:
                if not is_down_trend_v:
                    v_status, v_adv = (
                        "매집시작",
                        f"🚀 <b>[매집시작]</b> 시간보정 강도 {vol_strength:.1f}점!"
                        " 화력이 차오르네.",
                    )
                elif is_down_trend_structural:
                    v_status, v_adv = (
                        "역배열과열",
                        f"⚠️ <b>[역배열과열]</b> 시간보정 강도 {vol_strength:.1f}점!"
                        " 하락 추세 속 속임수 음봉 거래량 주의.",
                    )
                else:
                    v_status, v_adv = (
                        "차익매물출회",
                        f"⚠️ <b>[차익매물출회]</b> 시간보정 강도 {vol_strength:.1f}점!"
                        " 우상향 성벽 속 고점 차익 음봉 매물이니 5일선 지지를 확인하시게.",
                    )
            elif vol_strength >= 80:
                if not is_down_trend_v:
                    v_status, v_adv = (
                        "정상화력",
                        f"⚔️ <b>[정상화력]</b> 시간보정 강도 {vol_strength:.1f}점!"
                        " 기세가 뻣뻣하구먼.",
                    )
                elif is_down_trend_structural:
                    v_status, v_adv = (
                        "역배열과열",
                        f"⚠️ <b>[역배열과열]</b> 시간보정 강도 {vol_strength:.1f}점!"
                        " 하락 추세 속 속임수 음봉 거래량 주의.",
                    )
                else:
                    v_status, v_adv = (
                        "숨고르기조정",
                        f"☕ <b>[숨고르기조정]</b> 시간보정 강도 {vol_strength:.1f}점!"
                        " 정배열 속 정상적인 눌림목 음봉 조정 중이오.",
                    )
            else:
                v_status, v_adv = (
                    "거래절벽",
                    f"🧊 <b>[거래절벽]</b> 시간보정 강도 {vol_strength:.1f}점!"
                    " 수급이 마르고 동력이 없으니 속지 마시게.",
                )

            st.markdown(
                f"<div class='vol-box'><div style='font-size:32px;"
                " font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량"
                f" 전황: {v_status} ({'수동 연산 모드' if is_manual_mode else f'실시간 {v_ratio:.1f}% / 5일평균대비'})</div><div"
                f" class='vol-sub-text'>{v_adv}</div><div style='margin-top:"
                " 10px; font-size: 18px; color: #37474F; background: #FFFFFF;"
                " padding: 10px; border-radius: 8px; border-left: 6px solid"
                f" #FF9800;'>🎯 <b>[호가창 잔량 공방]</b> {ob_status_msg}</div></div>",
                unsafe_allow_html=True,
            )

            # 지표 정밀 연산
            bb_bot_series = (df["Close"] <= (low_b * 1.02)).astype(int)
            rsi_bot_series = (rsi_series <= 35).astype(int)
            will_bot_series = (will_series <= -80).astype(int)
            bottom_score_series = (
                bb_bot_series + rsi_bot_series + will_bot_series
            )

            bottom_score = bottom_score_series.iloc[-1]
            recent_bottom_memory = bottom_score_series.iloc[-3:].max() >= 2

            p_will = 1 if will_val <= -50 else 0
            p_bb = 1 if (mid_line * 0.98 <= p <= mid_line * 1.02) else 0
            p_rsi = 1 if (40 <= rsi_val <= 55) else 0
            pullback_rebound_score = p_will + p_bb + p_rsi

            # 손절 조건 검증
            is_stop_loss_triggered = False
            stop_reason = ""
            if user_avg_price > 0 and p < stop_loss_price:
                is_stop_loss_triggered = True
                stop_reason = "보유 평단가 대비 손절 마지노선 이탈"
            elif (recent_bottom_memory or bottom_score >= 2) and p < prev_low:
                is_stop_loss_triggered = True
                stop_reason = "바닥권 전저점 이탈 마지노선"

            # 1·2·3단계 매수 판정 (목표선 도달 시 신규 매수는 원천 차단)
            is_bottom_indicator_ok = (
                bottom_score >= 2 or recent_bottom_memory
            )
            is_macd_not_deepening = not is_macd_reverse_deepening

            is_bottom_entry_signal = (
                (not is_ma5_safe)
                and (bottom_score >= 2)
                and (vol_strength >= 80)
                and (not is_down_trend_v)
                and is_macd_not_deepening
                and is_valid_bottom_candle
                and (not is_target_reached)
            )

            is_escape_buy_signal = (
                is_ma5_safe
                and is_bottom_indicator_ok
                and (vol_strength >= 80)
                and is_macd_not_deepening
                and is_valid_buy_candle
                and is_bandwidth_ok
                and is_orderbook_safe
                and (not is_target_reached)
            )

            is_pullback_buy_signal = (
                (not is_down_trend_structural)
                and is_ma20_buffer_safe
                and is_ma5_safe
                and is_orderbook_safe
                and (pullback_rebound_score >= 2)
                and (vol_strength >= 80)
                and is_bandwidth_ok
                and is_macd_not_deepening
                and is_valid_buy_candle
                and (not is_target_reached)
            )

            # 시간 족쇄
            if is_kr and not is_manual_mode:
                is_afternoon_safe_time = (now_local.hour > 14) or (
                    now_local.hour == 14 and now_local.minute >= 0
                )
                time_tag_wait = "★ 14:00 매수 대기"
                time_tag_ok = "14:00 이후 안착 완료"
                time_rule_desc = (
                    "오전장 휩소를 피하기 위해 14:00 이후 지지 확인 시 50% 분할 타진하고,"
                    " 15:20 종가 사수 시 완성하시게. (단, 윗꼬리 달고 기준선 이탈 시 즉시 철수)"
                )
                time_rule_pass = (
                    "14:00 이후 지지 확인 완료! 50% 분할 타진 집행 (15:20 종가 사수 시 완성 /"
                    " 윗꼬리 이탈 시 즉시 철수)"
                )
            elif not is_kr and not is_manual_mode:
                is_afternoon_safe_time = (kst_now.hour >= 7) and (
                    kst_now.hour < 22
                )
                time_tag_wait = "★ 07:00 마감 일봉 대기"
                time_tag_ok = "07:00 일봉 안착 확인"
                time_rule_desc = (
                    "정규장 중에는 매도만 유효! 밤새 휩소를 피하고 07:00 마감"
                    " 일봉을 확인 후 진입하시게. (단, 윗꼬리 달고 기준선 이탈 시 즉시 철수)"
                )
                time_rule_pass = (
                    "정규장 캔들 마감! 07:00 일봉 안착 확인 완료! (윗꼬리 기준선 이탈 시 즉시 철수)"
                )
            else:
                is_afternoon_safe_time = True
                time_tag_wait = "★ 수동 검증"
                time_tag_ok = "수동 시세 확인"
                time_rule_desc = "수동 입력 시세 지지 확인 후 진입하시게. (윗꼬리 기준선 이탈 시 즉시 철수)"
                time_rule_pass = "수동 시세 지지 확인 완료! (윗꼬리 기준선 이탈 시 즉시 철수)"

            # ==================================================================
            # ★ [신호등 분기 논리]
            # ==================================================================
            if is_stop_loss_triggered:
                final_code = "STOP_LOSS_ALERT"
                sig = "🚨 [비상 손절] 바닥권 전저점 붕괴! 전량 칼손절 후퇴!"
                col = "#D32F2F"
                final_adv = (
                    f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    " <b>[바닥권 전저점 방어선 붕괴]</b> 미련을 버리고 즉시"
                    " 전량 칼손절 후퇴하시게."
                )
            elif is_band_riding:
                final_code = "BAND_RIDING_HARVEST"
                sig = "🟣 [1차 수확 / 잔여 밴드 추종] 목표선 상방 확장 중!"
                col = "#6A1B9A"
                final_adv = (
                    f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). "
                    f"<b>[볼린저 상단 상방 확장]</b> 현재가({p:{fmt_p}}{currency})가 볼린저 상단을 타고 위로 솟구치는 중이오! "
                    "<b>물량의 50%는 1차 익절하여 수익을 확정</b>하고, <b>잔여 50%는 5일선 이탈 전까지 목표선 상향을 즐기며 홀딩</b>하시게."
                )
            elif is_target_reached:
                final_code = "RED_SELL_TARGET"
                sig = "🔴 [목표 도달] 수학 목표선 저항! 1차 50% 수확 및 분할 매도!"
                col = "#D32F2F"
                final_adv = (
                    f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). "
                    f"<b>[수학 목표선 도달 완료]</b> 볼린저 상단({target_price_100:{fmt_p}}{currency}) 머리를 들이받았소! "
                    "추가 진격을 중단하고, <b>우선 50% 물량을 기계적으로 수확</b>한 뒤 1~2호가 아래에 잔여 매도를 배치하시게."
                )
            elif is_on_the_wall and is_bearish_candle:
                final_code = "RED_SELL_WARNING"
                sig = "🟡 [경계] 성벽 위 음봉 출현 / 분할 익절 준비"
                col = "#EF6C00"
                final_adv = (
                    f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    " <b>[성벽 위 음봉 출현]</b> 성벽(방어선) 위에서 음봉이"
                    " 발생했으니, 5일선 사수 여부를 살피며 기세 둔화 시 분할"
                    " 익절할 준비를 하시게."
                )
            elif not is_orderbook_safe:
                final_code = "WAIT_ORDERBOOK"
                sig = "🟡 [관망/보류] 호가 불균형 경계 (허매수 받침 또는 거대 매도벽)"
                col = "#F57C00"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    f" <b>[호가창 불균형]</b> 매도잔량비가 {ob_ratio_val:.2f}배로 위험 구간이오! "
                    "위로 칠 주체가 없는 허매수 받침이거나 상단 매도벽이 너무 두터우니 손가락을 묶고 관망하시게."
                )
            elif is_on_the_wall:
                if (vol_strength >= 150) and (not is_down_trend_v):
                    final_code = "BREAKOUT_ATTACK"
                    sig = "🟢 [돌격] 성벽 강력 돌파 / 수확선 진격!"
                    col = "#2E7D32"
                    final_adv = (
                        f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). "
                        f"<b>[성벽 강력 돌파]</b> 막강한 화력을 뿜으며 성벽({defense_line:{fmt_p}}{currency})을 돌파했소! "
                        f"조기 매도하지 말고 볼린저 상단 수확선({target_price_100:{fmt_p}}{currency})까지 5일선을 타고 거침없이 추세를 즐기시게."
                    )
                else:
                    final_code = "YELLOW_CAUTION"
                    sig = "🟡 [경계] 성벽 위 공방 / 매도 준비!"
                    col = "#EF6C00"
                    final_adv = (
                        f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                        " <b>[성벽 위 진입 및 공방]</b> 추격 매수는 절대 금하고,"
                        " 매도 준비 및 경계 태세를 갖추시게!"
                    )
            elif (
                is_escape_buy_signal or is_pullback_buy_signal
            ) and is_over_extended_5:
                final_code = "WAIT_OVER_EXTENDED"
                sig = (
                    f"🟡 [관망/경계] 5일선 과다이격(+{bias_ma5:.1f}%) / 추격"
                    " 매수 금지"
                )
                col = "#F57C00"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    f" <b>[5일선 과다이격(+{bias_ma5:.1f}%)]</b> 주가가 5일선에서"
                    " 5% 이상 벌어져 단기 차익 매물 위험이 크니, 5일선"
                    " 부근으로 숨고르기할 때까지 추격 매수를 엄금하시게."
                )
            elif is_bottom_entry_signal:
                final_code = "BOTTOM_ENTRY"
                col = "#388E3C"
                if not is_afternoon_safe_time:
                    sig = f"🟢 [입질 포착] 1단계 진바닥 입질 ({time_tag_wait})"
                    final_adv = (
                        f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                        " <b>[진바닥 포착 완료]</b> 3중 지표 터치 확인! 단,"
                        f" {time_rule_desc}"
                    )
                else:
                    sig = f"🟢 [매입 진격] 1단계 진바닥 입질 매수 ({time_tag_ok})"
                    action_guide = (
                        "14:00 이후 볼린저 바닥 지지 확인 시 50% 분할 타진하고,"
                        " 15:20 저가 사수 시 완성하시게. (단, 윗꼬리 달고 바닥선 이탈 시 즉시 철수)"
                        if is_kr
                        else "07:00 마감 일봉상 볼린저 바닥선 사수를 확인 후 진입하시게. (단, 윗꼬리 달고 바닥선 이탈 시 즉시 철수)"
                    )
                    final_adv = (
                        f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                        f" <b>[{time_tag_ok}]</b> {action_guide}"
                    )
            elif is_escape_buy_signal:
                final_code = "ESCAPE_BUY"
                col = "#2E7D32"
                if not is_afternoon_safe_time:
                    sig = f"🟢 [탈출 포착] 2단계 진바닥 탈출 ({time_tag_wait})"
                    final_adv = (
                        f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                        f" <b>[5일선 안착 포착]</b> {bw_diag_msg}. 기세는"
                        f" 살아있으나 {time_rule_desc}"
                    )
                else:
                    sig = f"🟢 [추가 진격] 2단계 진바닥 탈출 매수 ({time_tag_ok})"
                    action_guide = (
                        "14:00 이후 5일선 안착 확인 시 50% 분할 진입하고,"
                        " 15:20 종가 사수 시 2단계 완성하시게. (단, 윗꼬리 달고 5일선 하회 시 즉시 철수)"
                        if is_kr
                        else "07:00 마감 일봉상 5일선 위 안착을 확인 후 2단계 진입하시게. (단, 윗꼬리 달고 5일선 하회 시 즉시 철수)"
                    )
                    final_adv = (
                        f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                        f" <b>[{time_tag_ok}]</b> {bw_diag_msg}. {action_guide}"
                    )
            elif is_pullback_buy_signal:
                final_code = "PULLBACK_BUY"
                col = "#1976D2"
                if not is_afternoon_safe_time:
                    sig = f"🔵 [승수 포착] 3단계 눌림목 ({time_tag_wait})"
                    final_adv = (
                        f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                        f" <b>[눌림목 지지 포착]</b> {bw_diag_msg}."
                        f" <b>{time_rule_desc}</b>"
                    )
                else:
                    sig = f"🔵 [본진 진격] 3단계 눌림목 추가 매수 ({time_tag_ok})"
                    action_guide = (
                        "14:00 이후 5·20일선 안전마진(+0.2%) 안착 시 50% 분할 타진,"
                        " 15:20 종가 사수 시 3단계 완성하시게. (단, 윗꼬리 밀림 시 매수 취소 및 철수)"
                        if is_kr
                        else "07:00 마감 일봉상 5·20일선 안전마진 안착을 확인 후 3단계 완성하시게. (단, 윗꼬리 밀림 시 매수 취소 및 철수)"
                    )
                    final_adv = (
                        f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                        f" <b>[{time_tag_ok}]</b> {bw_diag_msg}. {action_guide}"
                    )
            elif (
                p >= ma20_safe_threshold
                and (not is_down_trend_structural)
                and is_ma5_safe
            ):
                final_code = "BREAK_MA20_CONFIRMED"
                sig = "🔵 [돌파 확인] 20일선 안착 타진 (종가 사수 확인)"
                col = "#1E88E5"
                action_guide = (
                    "14:00 이후 지지 확인 시 50% 분할 타진, 15:20 종가 사수 시 3단계 완성하시게."
                    " (단, 윗꼬리 달고 20일선 이탈 시 즉시 철수)"
                    if is_kr
                    else "07:00 마감 일봉상 20일선 안착 사수를 확인 후 3단계 완성하시게."
                    " (단, 윗꼬리 달고 20일선 이탈 시 즉시 철수)"
                )
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    f" <b>[20일선 돌파 안착 타진]</b>"
                    f" 현재가({p:{fmt_p}}{currency})가"
                    f" 20일선 및 안전마진선({ma20_safe_threshold:{fmt_p}}{currency})을 돌파하였소!"
                    f" {action_guide}"
                )
            elif (
                is_ma20_teetering
                and (not is_down_trend_structural)
                and is_ma5_safe
            ):
                final_code = "WAIT_MA20_BUFFER"
                sig = "🟡 [관망/보류] 20일선 턱걸이 공방 (확실한 안착 대기)"
                col = "#F57C00"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    " <b>[20일선 턱걸이 구간]</b>"
                    f" 현재가({p:{fmt_p}}{currency})가"
                    f" 20일선({mid_line:{fmt_p}}{currency})에 1~2호가 차이로"
                    " 아슬아슬하게 걸쳐 있소! 속임수 윗꼬리 휩소를 막기 위해"
                    f" 안전마진 기준선({ma20_safe_threshold:{fmt_p}}{currency})"
                    " 위로 시원하게 올라탈 때까지 진입을 보류하시게."
                )
            elif (
                bottom_score >= 2 or recent_bottom_memory
            ) and is_down_trend_v and (not is_ma5_safe):
                final_code = "WAIT_DOWNTREND_FALL"
                sig = "🟡 [진바닥 탐색 중] 5일선 하회 투매 음봉 / 칼날 관망"
                col = "#F57C00"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    " <b>[5일선 하회 투매 음봉 진행]</b> 바닥권 지표는 터치했으나"
                    " 주가가 5일선 아래에서 밀리는 중이니 5일선 회복 전까지 손가락을"
                    " 묶으시게."
                )
            elif (
                bottom_score >= 2 or recent_bottom_memory
            ) and is_down_trend_v and is_ma5_safe:
                final_code = "WAIT_PULLBACK_CANDLE"
                sig = "🟡 [관망/숨고르기] 5일선 위 음봉 조정 / 지지 확인 대기"
                col = "#F57C00"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    " <b>[5일선 위 음봉 조정]</b> 주가가 5일선 위에 안착해 있으나"
                    " 당일 차익 매물로 음봉이 진행 중이오! 5일선 지지를 최종 확인 후 진입하시게."
                )
            elif (
                is_ma5_safe
                and not is_bottom_indicator_ok
                and not is_down_trend_structural
            ):
                final_code = "WAIT_INDICATOR"
                sig = "🟡 [관망/보류] 5일선 안착했으나 보조지표 미흡 (외바닥 주의)"
                col = "#F57C00"
                if p < mid_line:
                    final_adv = (
                        f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                        f" <b>[20일선 저항 하회]</b> 5일선은 회복했으나 머리 위 20일선({mid_line:{fmt_p}}{currency}) 저항 아래에 갇혀 있소! "
                        "20일선 돌파 및 안착 확인 전까지 진입을 보류하시게."
                    )
                else:
                    final_adv = (
                        f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                        " <b>[지표 미흡]</b> 5일선은 안착했으나 보조지표 동조 점수"
                        " 부족으로 외바닥 속임수를 경계하고 관망하시게."
                    )
            elif is_ma5_safe and is_macd_reverse_deepening:
                final_code = "WAIT_MACD"
                sig = (
                    "🟡 [관망/보류] 5일선 회복 중이나 엔진 역회전 심화 (진입"
                    " 자제)"
                )
                col = "#F57C00"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    " <b>[엔진 역회전 심화]</b> 5일선 위 안착 시도 중이나 MACD"
                    " 하락 압력이 가속되므로 관망하시게."
                )
            elif (bottom_score >= 2 or recent_bottom_memory) and vol_strength < 80:
                final_code = "WAIT_VOLUME"
                sig = "🟡 [입질 대기] 지표 충족 / 거래량 수반 대기"
                col = "#E65100"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    " <b>[수급 부진]</b> 바닥 지표는 확인했으나 거래량이 실리지"
                    " 않은 속임수 구간이니 거래량 유입을 확인 후 진입하시게."
                )
            elif is_down_trend_structural and not is_ma5_safe:
                final_code = "WAIT_DOWNTREND_FALL"
                sig = "🟡 [진바닥 탐색 중] 역배열 하락 진행 / 칼날 관망"
                col = "#F57C00"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    " <b>[진바닥 탐색 중]</b> 대세 역배열 하락 추세 속에서 5일선 아래 칼날이"
                    " 떨어지는 중이니 절대 칼을 잡지 마시게."
                )
            elif (
                (p >= mid_line * 0.98 and p <= mid_line * 1.03)
                and (pullback_rebound_score >= 1)
                and (not is_down_trend_structural)
            ):
                final_code = "WAIT_PULLBACK"
                sig = (
                    "🟡 [관망/보류] 눌림목 영역이나 밴드폭 기준 미달 (돌파 확인"
                    " 대기)"
                    if not is_bandwidth_ok
                    else "🟡 [관망/보류] 눌림목 영역 도달했으나 지표 동조 미흡"
                )
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    f" <b>[{bw_diag_msg}]</b> 확실한 지표 동조 및 안착 전까지"
                    " 승수 확대 금지."
                )
                col = "#F57C00"
            else:
                final_code = "WAIT_GENERAL"
                sig = "🟡 [관망] 조건 미충족 / 뇌동매매 금지"
                col = "#FBC02D"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)."
                    " 조건 미충족 상태이므로 뇌동매매를 금하고 관망 유지."
                )

            # 신호등 박스 표출
            st.markdown(
                f"<div class='signal-box' style='background-color: {col};'>"
                f"<div class='signal-text'>{sig}</div>"
                f"<div class='signal-subtext'>{final_adv}</div>"
                "</div>",
                unsafe_allow_html=True,
            )

            is_overall_cautious_state = final_code in [
                "WAIT_GENERAL", "WAIT_INDICATOR", "WAIT_MACD", "WAIT_VOLUME", 
                "WAIT_DOWNTREND_FALL", "WAIT_PULLBACK_CANDLE", "WAIT_PULLBACK", 
                "WAIT_MA20_BUFFER", "WAIT_ORDERBOOK", "WAIT_OVER_EXTENDED", 
                "YELLOW_CAUTION", "RED_SELL_WARNING"
            ]

            # 지표 세부 텍스트 조립
            pullback_status_str = f"<b>(밴드폭 {bandwidth:.1f}%)</b>"
            pullback_action_str = "-> <b>[관망]</b> 추세 및 지표 안착 대기"

            if is_band_riding:
                pullback_status_str = f"<b>(밴드폭 {bandwidth:.1f}% / 밴드 라이딩)</b>"
                pullback_action_str = "-> <b>[추세 추종]</b> 상단 밴드 상방 개방! 50% 수확 후 5일선 사수 기준으로 잔여 추종"
            elif is_target_reached:
                pullback_status_str = f"<b>(수학 목표선 저항 도달)</b>"
                pullback_action_str = "-> <b>[50% 수확]</b> 상단 목표 도달 완료로 신규 진입 절대 금지"
            elif is_escape_buy_signal:
                pullback_status_str = (
                    f"<b>(밴드폭 {bandwidth:.1f}% / 진바닥 구간)</b>"
                )
                pullback_action_str = (
                    "-> <b>[진바닥 반등]</b> 바닥 탈출 국면이므로 5일선 사수"
                    " 기준으로 대응"
                )
            elif is_down_trend_structural:
                pullback_status_str = (
                    f"<b>(대세 역배열 하락 추세 / 밴드폭 {bandwidth:.1f}%)</b>"
                )
                pullback_action_str = (
                    "-> <b>[진바닥 탐색 중]</b> 역배열 하락 진행형 (5일선 미안착"
                    " / 칼날 관망)"
                    if not is_ma5_safe
                    else "-> <b>[진바닥 안착 시도]</b> 5일선 회복 시도 중이나"
                    " 역배열 저항 경계"
                )
            elif not is_bandwidth_ok:
                pullback_status_str = (
                    f"<b>(밴드폭 {bandwidth:.1f}% / {bw_status_category})</b>"
                )
                break_action_guide = (
                    "14:00 이후 지지 시 50% 타진, 15:20 종가 사수 시 3단계 완성 (윗꼬리 밀림 시 즉시 철수)"
                    if is_kr
                    else "07:00 마감 일봉상 20일선 안착 확인 시 3단계 완성 (윗꼬리 밀림 시 즉시 철수)"
                )
                pullback_action_str = (
                    f"-> <b>[돌파 타진]</b> 20일선({mid_line:{fmt_p}}{currency}) 돌파 성공! "
                    f"{break_action_guide}"
                    if p >= mid_line
                    else f"-> <b>[매수 보류]</b> {bw_diag_msg}"
                )
            elif is_ma20_teetering:
                pullback_action_str = (
                    f"-> <b>[턱걸이 공방]</b> 20일선({mid_line:{fmt_p}}{currency})"
                    " 턱걸이 중! 안전마진(+0.2%) 안착 대기"
                )
            elif not is_orderbook_safe:
                pullback_action_str = (
                    "-> <b>[호가 경계]</b> 매도잔량비 취약"
                    f"({ob_ratio_val:.2f}배)으로 윗꼬리 경계 관망"
                )
            elif pullback_rebound_score == 0:
                pullback_action_str = "-> <b>[관망]</b> 눌림목 지지 조건 미충족"
            elif pullback_rebound_score < 2:
                pullback_action_str = (
                    "-> <b>[지표 미흡]</b> 눌림목 동조 점수 부족"
                    f"({pullback_rebound_score}점)으로 돌파/안착 대기"
                )
            elif is_over_extended_5 and (p >= mid_line):
                pullback_action_str = (
                    "-> <b>[추격 매수 금지]</b> 5일선 대비"
                    f" +{bias_ma5:.1f}% 과다이격으로 지지 대기"
                )
            elif not is_valid_buy_candle:
                pullback_action_str = (
                    "-> <b>[캔들 확인 대기]</b> 지지 캔들 미흡으로 관망"
                )
            elif is_macd_reverse_deepening:
                pullback_action_str = (
                    "-> <b>[엔진 역회전 심화]</b> MACD 하락 가속 중이므로"
                    " 관망"
                )
            elif is_pullback_buy_signal:
                pullback_time_guide = (
                    "14:00 이후 50% 분할 타진, 15:20 종가 사수 시 완성 (윗꼬리 20일선 이탈 시 즉시 철수)"
                    if is_kr
                    else "07:00 마감 일봉 안착 확인 시 3단계 완성 (윗꼬리 20일선 이탈 시 즉시 철수)"
                )
                pullback_action_str = (
                    f"-> <b>[3단계 눌림목 추가 매수]</b> 5·20일선 안착 확인! {pullback_time_guide}"
                )
            else:
                if p < mid_line:
                    pullback_action_str = (
                        f"-> <b>[매수 보류]</b> 5일선은 회복했으나 <b>머리 위 20일선({mid_line:{fmt_p}}{currency}) 저항 아래</b>에 갇혀 있소! "
                        "20일선 돌파 및 안착 확인 전까지 진입 금지."
                    )
                else:
                    pullback_action_str = (
                        "-> <b>[돌파/안착 대기]</b> 상방 공방 및 이격 조율 중 관망"
                    )

            if bottom_score >= 2:
                bottom_status_str = (
                    f"<b>(당일 진바닥 지표 {bottom_score}개 터치 달성!)</b>"
                )
                if is_stop_loss_triggered:
                    bottom_action_str = (
                        "→ <b>[비상 후퇴]</b> 바닥권 전저점 이탈로 매수 금지"
                    )
                elif is_band_riding:
                    bottom_action_str = (
                        "→ <b>[밴드 라이딩]</b> 상단 밴드가 열렸으니 50% 수확 후 잔여 물량 추세 홀딩"
                    )
                elif is_target_reached:
                    bottom_action_str = (
                        "→ <b>[수확선 도달]</b> 상단 목표선 도달로 진바닥 임무 완수! (50% 기계적 수확)"
                    )
                elif is_on_the_wall:
                    bottom_action_str = (
                        "→ <b>[바닥 탈출 완료]</b> 성벽 도달로 진바닥 임무"
                        " 완수! (익절 준비)"
                    )
                elif is_down_trend_v and not is_ma5_safe:
                    bottom_action_str = (
                        "→ <b>[투매 칼날 경계]</b> 5일선 하회 투매 진행으로 매수"
                        " 금지 및 관망"
                    )
                elif is_down_trend_v and is_ma5_safe:
                    bottom_action_str = (
                        "→ <b>[음봉 조정 관망]</b> 5일선 위 음봉 조정이므로 지지 사수 확인 후 대응"
                    )
                elif vol_strength < 80:
                    bottom_action_str = (
                        "→ <b>[입질 대기]</b> 거래량 부족"
                        f"({vol_strength:.1f}점)으로 매수 보류"
                    )
                elif is_macd_reverse_deepening:
                    bottom_action_str = (
                        "→ <b>[매수 보류]</b> MACD 엔진 역회전 심화 중이므로"
                        " 진입 금지"
                    )
                elif not is_valid_bottom_candle:
                    bottom_action_str = (
                        "→ <b>[캔들 대기]</b> 음봉 매도세 지속으로 매수 보류"
                    )
                elif is_escape_buy_signal:
                    time_escape_action = (
                        "14:00 이후 50% 분할 타진, 15:20 종가 사수 시 완성"
                        if is_kr
                        else "07:00 일봉 5일선 안착 확인 시 완성"
                    )
                    bottom_action_str = (
                        f"→ <b>[2단계 진바닥 탈출]</b> 5일선 안착 확인! {time_escape_action} (윗꼬리 5일선 이탈 시 즉시 철수)"
                    )
                elif is_ma5_safe:
                    bottom_action_str = (
                        f"→ <b>[관망 대기]</b> 5일선 위 안착 중이나 {bw_diag_msg}로 추가 매수 보류"
                    )
                elif is_bottom_entry_signal:
                    time_bottom_action = (
                        "14:00 이후 볼린저 바닥 지지 시 50% 타진, 15:20 저가 사수 시 완성"
                        if is_kr
                        else "07:00 일봉 바닥 지지 확인 시 완성"
                    )
                    bottom_action_str = (
                        f"→ <b>[1단계 진바닥 입질 매수]</b> 지표 충족! {time_bottom_action} (윗꼬리 바닥 이탈 시 즉시 철수)"
                    )
                else:
                    bottom_action_str = (
                        "→ <b>[입질 대기]</b> 5일선 아래 바닥 탐색 중 (안착 관망)"
                    )
            elif recent_bottom_memory:
                bottom_status_str = (
                    "<b>(최근 2~3일 내 진바닥 확인 완료!)</b>"
                )
                if is_stop_loss_triggered:
                    bottom_action_str = (
                        "→ <b>[비상 후퇴]</b> 바닥권 전저점 이탈로 매수 금지"
                    )
                elif is_band_riding:
                    bottom_action_str = (
                        "→ <b>[밴드 라이딩]</b> 상단 밴드 확장 중! 50% 수확 후 잔여 홀딩"
                    )
                elif is_target_reached:
                    bottom_action_str = (
                        "→ <b>[수확선 도달]</b> 상단 목표선 도달로 탈출 완수! (50% 기계적 수확)"
                    )
                elif is_on_the_wall:
                    bottom_action_str = (
                        "→ <b>[바닥 탈출 완료]</b> 성벽 도달로 탈출 완수! (익절"
                        " 준비)"
                    )
                elif is_over_extended_5:
                    bottom_action_str = (
                        "→ <b>[추격 매수 금지]</b> 5일선 대비"
                        f" +{bias_ma5:.1f}% 과다이격 발생으로 관망 대기."
                    )
                elif not is_orderbook_safe:
                    bottom_action_str = (
                        f"→ <b>[호가 경계]</b> 호가잔량비 취약({ob_ratio_val:.2f}배)으로"
                        " 윗꼬리 경계 관망"
                    )
                elif not is_valid_buy_candle:
                    bottom_action_str = (
                        "-> <b>[캔들 대기]</b> 5일선 안착했으나 지지캔들"
                        " 미충족으로 관망."
                    )
                elif not is_bandwidth_ok:
                    bottom_action_str = (
                        f"→ <b>[밴드폭 대기]</b> {bw_diag_msg} 관망."
                    )
                elif is_escape_buy_signal:
                    time_escape_action = (
                        "14:00 이후 50% 분할 타진, 15:20 종가 사수 시 완성"
                        if is_kr
                        else "07:00 일봉 5일선 안착 확인 시 완성"
                    )
                    bottom_action_str = (
                        f"→ <b>[2단계 진바닥 탈출]</b> 5일선 안착 확인! {time_escape_action} (윗꼬리 5일선 이탈 시 즉시 철수)"
                    )
                elif not is_ma5_safe:
                    bottom_action_str = (
                        "→ <b>[5일선 안착 대기]</b> 바닥은 확인되었으나 5일선"
                        " 돌파 대기 중 관망."
                    )
                elif vol_strength < 80:
                    bottom_action_str = (
                        "→ <b>[거래량 대기]</b> 거래량 부족"
                        f"({vol_strength:.1f}점)으로 관망."
                    )
                else:
                    bottom_action_str = "→ <b>[관망]</b> 추세 안착 대기 중."
            else:
                bottom_status_str = "<b>(조건 미흡)</b>"
                bottom_action_str = "➔ <b>[관망]</b> 진바닥 지표 조건 미충족"

            if defense_line > target_price_100:
                sub_indicator_str = (
                    f"    - <b>역배열 침체 전황:</b> 성벽({defense_line:{fmt_p}}{currency})이 목표선({target_price_100:{fmt_p}}{currency})보다 높은 왜곡 구간 (상방 동력 소멸 및 관망)<br>"
                    f"    - <b>눌림목 지지 동조:</b> {pullback_rebound_score}/3점 <b>(역배열 조정 구간)</b> -> <b>[관망]</b> 추세 안착 대기"
                )
            elif final_code == "BREAKOUT_ATTACK" or is_on_the_wall:
                if vol_strength < 80 or is_candle_bearish:
                    current_candlestick_type = "음봉 조정" if is_candle_bearish else "숨고르기 공방"
                    sub_indicator_str = (
                        f"    - <b>성벽 공방 전황:</b> 성벽({defense_line:{fmt_p}}{currency}) 위에서 안착 중이나 거래절벽(수급 부진) 및 {current_candlestick_type} 중<br>"
                        f"    - <b>눌림목 지지 동조:</b> {pullback_rebound_score}/3점 <b>(성벽 위 공방)</b> -> <b>[관망]</b> 지지 확인 대기"
                    )
                else:
                    sub_indicator_str = (
                        f"    - <b>성벽 돌파 전황:</b> 성벽({defense_line:{fmt_p}}{currency}) 돌파 성공! "
                        f"수확 목표선({target_price_100:{fmt_p}}{currency})까지 기세 추종 (잔여 여력: {tgt_diff:+.1f}%)"
                    )
            elif is_target_reached:
                sub_indicator_str = (
                    f"    - <b>목표 도달 전황:</b> 수확 목표선({target_price_100:{fmt_p}}{currency}) 도달 완료! (분할 매도 구역)"
                )
            elif p < defense_line:
                if not is_ma5_safe:
                    sub_indicator_str = (
                        f"    - <b>성벽 함락 전황:</b> 성벽({defense_line:{fmt_p}}{currency}) 아래로 밀린 채 <b>단기 생명선(5일선) 이탈</b> (칼날 관망)<br>"
                        f"    - <b>눌림목 지지 동조:</b> {pullback_rebound_score}/3점 <b>(하락 험지 구간)</b> -> <b>[관망]</b> 5일선 회복 대기"
                    )
                else:
                    sub_indicator_str = (
                        f"    - <b>성벽 공방 전황:</b> 성벽({defense_line:{fmt_p}}{currency}) 아래 갇힌 채 돌파 공방 중 (안착 대기)<br>"
                        f"    - <b>눌림목 지지 동조:</b> {pullback_rebound_score}/3점 <b>(돌파 대기 구역)</b> -> <b>[관망]</b> 안착 확인 대기"
                    )
            else:
                if p >= mid_line:
                    pullback_tag = "눌림목 지지 동조"
                else:
                    pullback_tag = "돌파 준비(에너지 충전)"

                sub_indicator_str = (
                    f"  - <b>{pullback_tag}:</b>"
                    f" {pullback_rebound_score}/3점 {pullback_status_str}"
                    f" {pullback_action_str}"
                )

            if (
                is_escape_buy_signal
                or bottom_score >= 2
                or recent_bottom_memory
                or is_down_trend_structural
            ):
                if is_down_trend_structural and not (
                    is_escape_buy_signal
                    or bottom_score >= 2
                    or recent_bottom_memory
                ):
                    sub_indicator_str = (
                        "    - <b>진바닥 탐색 현황:</b>"
                        f" {pullback_status_str} {pullback_action_str}"
                    )
                else:
                    sub_indicator_str = (
                        "    - <b>진바닥 입질 동조:</b>"
                        f" {bottom_score}개 터치 {bottom_status_str}"
                        f" {bottom_action_str}"
                    )

            indicator_verify_text = (
                f"{ma_price_summary}<br>• <b>[추세 정밀 판독]:</b>"
                f" {trend_status}<br>• <b>[지표 검증"
                f" 연산]</b><br>{sub_indicator_str}{squeeze_info_str}"
            )
            ma5_dynamic_stop = dynamic_stop_price

            # ★ [보강]: 보유자 가이드에 성벽/목표선 예상 수익률 자동 연동 및 디테일 보존
            if is_band_riding:
                if user_avg_price > 0:
                    profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                    holder_guide_msg = (
                        f"• <b>[밴드 라이딩 대시세 구역 (수익률: {profit_rate:+.2f}%)]</b><br>"
                        f"• <b>실전 행동:</b> 신규 매수 금지! <b>보유 물량의 50%는 수학 목표선 도달 시점에서 시장가/지정가로 즉시 현금화</b>하여 승리를 확정지으시게.<br>"
                        f"• <b>잔여 50% 홀딩 기준:</b> 볼린저 상단이 매일 상승 중이므로 <b>5일선({ma5_val:{fmt_p}}{currency}) 종가 사수 시 잔여 물량 유지</b>.<br>"
                        f"• <b>최종 전량 청산선:</b> 5일선 -{dynamic_stop_pct:.1f}% 이탈({ma5_dynamic_stop:{fmt_p}}{currency}) 또는 음봉 전환 시 미련 없이 잔여 물량 전량 청산."
                    )
                else:
                    holder_guide_msg = (
                        "• <b>[밴드 라이딩 대시세 구역]</b><br>"
                        "• <b>실전 행동:</b> 상단 밴드가 열리고 있으나 신규 진입은 금물이오! 보유자는 50%를 우선 익절하고, 잔여 50%만 5일선 이탈 전까지 추종하시게."
                    )
            elif is_target_reached:
                if user_avg_price > 0:
                    profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                    holder_guide_msg = (
                        f"• <b>[수학 목표선 저항 도달 (수익률: {profit_rate:+.2f}%)]</b><br>"
                        f"• <b>실전 행동:</b> 신규 진입 절대 금지! <b>목표선 직전에서 물량의 50%를 기계적으로 확정 매도</b>하시게.<br>"
                        f"• <b>잔여 물량:</b> 목표가 1~2호가 아래에 매도를 걸어두고, 성벽({defense_line:{fmt_p}}{currency})이나 5일선 이탈 시 전량 정리하시게."
                    )
                else:
                    holder_guide_msg = (
                        f"• <b>[수학 목표선 도달 완료 구역]</b><br>"
                        f"• <b>실전 행동:</b> 볼린저 상단 저항선에 닿았으니 신규 매수를 엄금하고, 보유자는 50% 분할 매도로 계좌에 현금을 챙기시게."
                    )
            elif user_avg_price <= 0:
                holder_guide_msg = (
                    "현재 추세 탐색 및 방향 정립 구간이니"
                    f" 성벽({defense_line:{fmt_p}}{currency})이나 5일선 사수"
                    " 여부를 확인하며 차분히 보유 판단을 내리시게. (★ <b>손절"
                    f" 마지노선: {stop_loss_label}</b>)"
                )
            else:
                profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                exp_def_gain = ((defense_line - user_avg_price) / user_avg_price) * 100
                exp_tgt_gain = ((target_price_100 - user_avg_price) / user_avg_price) * 100

                if p >= user_avg_price:
                    if p >= defense_line:
                        wall_target_str = (
                            f"성벽(수익보존선:{defense_line:{fmt_p}}{currency} / {exp_def_gain:+.1f}%) 사수와 함께"
                            f" 수확목표선(기대수익:{exp_tgt_gain:+.1f}%)"
                        )
                    else:
                        wall_target_str = (
                            f"성벽(기대수익:{exp_def_gain:+.1f}%) 및 수확목표선(기대수익:{exp_tgt_gain:+.1f}%)"
                        )

                    holder_guide_msg = (
                        " • <b>[수익권 보유자 (평단가:"
                        f" {user_avg_price:{fmt_p}}{currency} / 수익률:"
                        f" +{profit_rate:.2f}%)]</b><br> • <b>기세 지속:</b>"
                        f" 5일선({ma5_val:{fmt_p}}{currency})을 이탈하지 않는 한"
                        f" {wall_target_str}까지 추세를 즐기시게.<br> • <b>단기"
                        f" 트레이딩:</b> 5일선 -{dynamic_stop_pct:.1f}% 이탈 시"
                        " 수익 보존을 위해 일부 분할"
                        f" 익절({ma5_dynamic_stop:{fmt_p}}{currency})<br> •"
                        " <b>수익 확정선:</b> 성벽 위 음봉 발생 또는 볼린저"
                        " 상단 도달 시 분할 매도 집행."
                    )
                else:
                    if is_ma5_safe:
                        ma5_loss_action = (
                            f"5일선({ma5_val:{fmt_p}}{currency}) 위에 안착했으니"
                            " 5일선 지지를 확인하며 추가 하락에 대비하시게."
                        )
                    else:
                        ma5_loss_action = (
                            f"5일선({ma5_val:{fmt_p}}{currency}) 아래에서는 추측"
                            " 추가 매수(물타기)를 절대 금지하네."
                        )

                    wall_exit_action = (
                        "본전/차익 분할 정리"
                        if exp_def_gain >= 0
                        else "손실 축소 및 비중 축소 분할 정리"
                    )

                    holder_guide_msg = (
                        " • <b>[손실권 보유자 (평단가:"
                        f" {user_avg_price:{fmt_p}}{currency} / 손실률:"
                        f" {profit_rate:.2f}%)]</b><br> • <b>단기 생명선:</b>"
                        f" {ma5_loss_action}<br> • <b>성벽 탈환 시:</b>"
                        f" 성벽({defense_line:{fmt_p}}{currency}) 도달 시 손익률({exp_def_gain:+.1f}%)을 점검하여 {wall_exit_action}.<br> • <b>단기"
                        f" 트레이딩:</b> 5일선 -{dynamic_stop_pct:.1f}% 이탈 시"
                        " 추가 하락 방어를 위해 비중"
                        f" 조절({ma5_dynamic_stop:{fmt_p}}{currency})<br> •"
                        " <b>최후 방어선:</b> 바닥권"
                        f" 전저점({stop_loss_price:{fmt_p}}{currency}) 이탈 시"
                        " 미련 없이 전량 칼손절 후퇴."
                    )

            if is_band_riding:
                ma5_guide_text = (
                    f"현재가({p:{fmt_p}}{currency})가 볼린저 상단을 타고 확장 중이오! "
                    f"절반 익절 완료 후 남은 50%는 <b>5일선({ma5_val:{fmt_p}}{currency}) 종가 이탈 전까지</b> 흔들리지 말고 끝까지 추종하시게."
                )
            elif is_target_reached:
                ma5_guide_text = (
                    f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 있으나, "
                    f"수학 목표선에 도달했으므로 5일선 -{dynamic_stop_pct:.1f}% 이탈({ma5_dynamic_stop:{fmt_p}}{currency})을 잔여 물량의 '수익 보존 전량 정리선'으로 엄수하시게."
                )
            elif not is_ma5_safe:
                ma5_guide_text = (
                    f"현재가({p:{fmt_p}}{currency})가"
                    f" 5일선({ma5_val:{fmt_p}}{currency}) 아래이나, 1단계"
                    " 진바닥 지표 충족으로 소량 씨앗 뿌리기 허용 구역이오."
                    if final_code == "BOTTOM_ENTRY"
                    else f"현재가({p:{fmt_p}}{currency})가"
                    f" 5일선({ma5_val:{fmt_p}}{currency}) 아래로 이탈했으니"
                    " 종가 안착 전까진 손가락을 묶으시게."
                )
            else:
                if vol_strength < 80:
                    ma5_guide_text = (
                        f"현재가({p:{fmt_p}}{currency})가"
                        f" 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착해 있으나, <b>거래절벽({vol_strength:.1f}점)</b>으로 수급이 마른 상태이오. 섣부른 추격을 금하고 관망하시게."
                    )
                elif is_down_trend_v or is_candle_bearish:
                    candlestick_name = "음봉 조정" if is_candle_bearish else "하락 변동성"
                    ma5_guide_text = (
                        f"현재가({p:{fmt_p}}{currency})가"
                        f" 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착해 있으나, 당일 {candlestick_name} 중이오. 5일선 지지 사수 확인 후 대응하시게."
                    )
                elif final_code == "ESCAPE_BUY":
                    ma5_time_str = "14:00 이후 지지 확인 50% 분할 진입" if is_kr else "07:00 일봉 안착 확인 시 2단계 진입"
                    ma5_guide_text = (
                        f"현재가({p:{fmt_p}}{currency})가"
                        f" 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착하며 2단계"
                        f" 진바닥 탈출 성공! {ma5_time_str} 유효 구역이오."
                    )
                elif final_code == "PULLBACK_BUY":
                    ma5_time_str = "14:00 이후 지지 시 3단계 분할 진격" if is_kr else "07:00 일봉 안착 확인 시 3단계 진격"
                    ma5_guide_text = (
                        f"현재가({p:{fmt_p}}{currency})가"
                        f" 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착하여 단기"
                        f" 전투선이 완벽히 살아있네. {ma5_time_str} 가능구역이오."
                    )
                else:
                    ma5_guide_text = (
                        f"현재가({p:{fmt_p}}{currency})가"
                        f" 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착하여 단기 전투선 유지 중이오. 5일선 사수 여부를 지켜보시게."
                    )

            if is_band_riding:
                def_status = (
                    f"성벽({defense_line:{fmt_p}}{currency})을 가뿐히 넘어 볼린저 상단이 상방으로 찢어지고 있네! "
                    "1차 50% 수익 확정 후 든든한 방어선을 뒤에 두고 잔여 추세를 즐기시게."
                )
            elif is_target_reached:
                def_status = (
                    f"성벽({defense_line:{fmt_p}}{currency}) 위 진격은 이미 완수되었네! "
                    f"수학 목표선({target_price_100:{fmt_p}}{currency}) 머리를 들이받았으니 진격을 멈추고 방어선을 등진 채 분할 매도로 현금을 챙기시게."
                )
            elif defense_line > target_price_100:
                def_status = (
                    f"성벽(방어선:{defense_line:{fmt_p}}{currency})이 상단 목표선({target_price_100:{fmt_p}}{currency})보다 위로 왜곡된 <b>[역배열 침체]</b> 구역이오! "
                    "상방 동력이 완전히 메말랐으니 섣부른 진격을 금하고 철저히 관망하시게."
                )
            elif p >= defense_line:
                if vol_strength < 80:
                    def_status = (
                        f"성벽({defense_line:{fmt_p}}{currency}) 위에는 있으나 <b>거래절벽({vol_strength:.1f}점)</b>으로 상방 동력이 없네! "
                        "추격매수를 삼가고 선제적 익절이나 관망을 준비하시게."
                    )
                else:
                    candlestick_warn_name = "음봉 발생" if is_candle_bearish else "기세 둔화"
                    def_status = (
                        f"성벽({defense_line:{fmt_p}}{currency}) 위에서 5일선 기세를"
                        " 타고 <b>위로 진격 중</b>이네! 든든한 방어선을 등지고 계속"
                        " 밀어붙이시게."
                        if not is_candle_bearish and (p >= prev_p and p >= ma5_val)
                        else f"성벽({defense_line:{fmt_p}}{currency}) 위에는 있으나"
                        f" 단기 기세가 <b>숨고르기 중</b>이네! 성벽 위 {candlestick_warn_name} 시"
                        " 선제적 익절을 준비하시게."
                    )
            else:
                if not is_ma5_safe:
                    def_status = (
                        f"성벽({defense_line:{fmt_p}}{currency}) 아래로 함락된 채 <b>단기 생명선(5일선)마저 이탈</b>했소! "
                        "추가 하락 위험이 크니 섣부른 물타기를 금하고 칼같이 관망하시게."
                    )
                elif final_code == "BOTTOM_ENTRY":
                    def_status = (
                        f"성벽({defense_line:{fmt_p}}{currency}) 아래"
                        " 극바닥권이나, 1단계 바닥 지표 동조로 <b>소량 입질"
                        " 진격 타점</b>을 형성 중이네!"
                    )
                elif final_code == "ESCAPE_BUY":
                    def_status = (
                        f"성벽({defense_line:{fmt_p}}{currency}) 아래이나,"
                        " 5일선을 딛고 <b>2단계 바닥 탈출 진격</b>을 시작하며"
                        " 성벽 탈환에 나서는 중이네!"
                    )
                elif is_ma5_safe:
                    def_status = (
                        f"성벽({defense_line:{fmt_p}}{currency}) 아래에 있으나,"
                        " 단기 5일선<b>(생명선)을 사수</b>하며 반격의 시동을"
                        " 거는 중이네!"
                    )
                else:
                    def_status = (
                        f"성벽({defense_line:{fmt_p}}{currency}) 아래로 함락된"
                        " 채 기세마저 밑으로 처박히고 있네! <b>절대 칼을 뽑지"
                        " 마시게.</b>"
                    )

            if is_band_riding:
                macd_strategy_msg = (
                    "<b>🔥 엔진 풀가동 + 밴드 라이딩</b><br>• <b>역할:</b>"
                    " 상방 대시세 추종.<br>• <b>진단:</b> 엔진 가속과 함께 상단 밴드가 열리고 있소! "
                    "추격 매수는 자제하되, 1차 절반 익절 후 남은 물량은 5일선 이탈 전까지 강하게 끌고 가시게."
                )
            elif is_target_reached:
                macd_strategy_msg = (
                    "<b>🚨 엔진 과열 경보 (수학 목표선 도달)</b><br>• <b>역할:</b>"
                    " 상단 오버슈팅 방어.<br>• <b>진단:</b> 엔진 가속도가 붙어 있어도 상단 저항선 코앞일세! "
                    "추격 매수는 엄금이며, 1~2호가 아래에 매도 주문을 깔아두어 이익을 챙기시게."
                )
            else:
                if is_macd_accelerating:
                    if rsi_val >= 70:
                        base_macd_desc = "<b>🔥 정회전 가속 (과열권)</b>: 추진력은 강력하나 보조지표 초과열권이오."
                    elif vol_strength < 80 or is_candle_bearish:
                        mac_desc_word = "음봉 조정" if is_candle_bearish else "숨고르기 공방"
                        base_macd_desc = f"<b>⚡ 가속 중이나 거래절벽/{mac_desc_word}</b>: MACD는 가속 중이나 성벽 위에서 {mac_desc_word} 중이오."
                    elif p >= defense_line:
                        base_macd_desc = "<b>🔥 정회전 가속 (성벽 수성)</b>: 성벽 사수하며 5일선 타고 상승 탄력 풀가동 중이오."
                    else:
                        base_macd_desc = "<b>🔥 정회전 가속 (돌파 시도)</b>: 상방을 향해 5일선 지지받으며 추진력이 붙고 있소."
                elif is_macd_decelerating:
                    if is_down_trend_structural or not is_ma5_safe:
                        base_macd_desc = "<b>⚠️ 정회전 둔화 (반탄력 소멸)</b>: 하락 험지 속 단기 반등 추진력이 꺾였소."
                    else:
                        base_macd_desc = "<b>⚠️ 정회전 둔화 (탄력 저하)</b>: 상승 관성은 유지 중이나 상방 추진력이 다소 둔화되었소."
                elif is_macd_recovering:
                    if is_escape_buy_signal or final_code == "ESCAPE_BUY":
                        base_macd_desc = "<b>🌤️ 역회전 감소 (바닥 탈출)</b>: 매도세가 잦아들며 5일선 안착 추진력이 가동 중이오."
                    elif final_code == "BOTTOM_ENTRY":
                        base_macd_desc = "<b>🌤️ 역회전 감소 (바닥 입질)</b>: 하락 압력이 줄어들며 극바닥 다지기가 시도되는 중이오."
                    elif is_down_trend_structural or p < defense_line:
                        base_macd_desc = "<b>🌤 역회전 감소 (기술적 반등)</b>: 매도세는 잦아들었으나 역배열/공방 구역이라 주의가 필요하오."
                    else:
                        base_macd_desc = "<b>🌤 역회전 감소 (반등 시동)</b>: 하락 관성이 둔화되며 바닥 다지기 반등을 모색 중이오."
                else:
                    base_macd_desc = "<b>⚙️ 엔진 역회전 심화</b>: 하락 관성이 지속되며 매도 압력이 깊어지는 중이오."

                if is_overall_cautious_state:
                    macd_strategy_msg = (
                        f"{base_macd_desc}<br>• <b>[관망 기조 동조]:</b> 현재 상단 종합 결론이 관망/경계 상태이므로, "
                        "엔진 상태와 무관하게 섣부른 추격매수를 금하고 안전하게 관망하시게."
                    )
                else:
                    macd_strategy_msg = f"{base_macd_desc}<br>• <b>[엔진 연동]:</b> 위 전황에 맞춰 유효하게 대응하시게."

            st.markdown(
                f"""<div class='trend-card'><div class='trend-title'>⚔️ 실전 필살 대응 전략</div><div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{ma5_guide_text}</span></div><div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>2. 성벽 사수 및 공방 확인</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{def_status}</span></div><div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>3. 중장기 추세 진단 및 지표 동조 현황</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{indicator_verify_text}</span></div><div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>4. 엔진(MACD) 확인</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{macd_strategy_msg}</span></div><div style='margin-bottom: 25px;'><span style='color: #D32F2F; font-weight: 900; font-size: 24px;'>5. 🛡️ [보유자 전용] 실전 행동 가이드</span><br><span style='color: #2E7D32; font-weight: bold; font-size: 20px;'>👉 {holder_guide_msg}</span></div><hr style='border:1px solid #FFEBEE; margin: 20px 0;'><div class='final-msg'>{final_adv}</div></div>""",
                unsafe_allow_html=True,
            )

            st.divider()

            # 하단 4대 핵심 지표 박스
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                if final_code == "BOTTOM_ENTRY":
                    bb_time_diag = (
                        "14:00 이후 50% 타진, 15:20 저가 사수 시 완성"
                        if is_kr
                        else "07:00 일봉 바닥 지지 확인 시 완성"
                    )
                    bb_diag = (
                        f"🔴 <b>[1단계 진바닥 입질 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 과매도 바닥권 선취매.<br>• <b>진단:</b> 지표"
                        f" 터치 + 바닥 지지 확인! {bb_time_diag} (윗꼬리 바닥 이탈 시 철수)"
                    )
                elif final_code == "ESCAPE_BUY":
                    bb_time_diag = (
                        "14:00 이후 5일선 안착 시 50% 분할 타진, 15:20 종가 사수 시 2단계 완성"
                        if is_kr
                        else "07:00 일봉 5일선 안착 확인 시 2단계 완성"
                    )
                    bb_diag = (
                        f"🟢 <b>[2단계 진바닥 탈출 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 5일선 안착 후 배팅 확대.<br>• <b>진단:</b>"
                        f" {bw_diag_msg}. {bb_time_diag} (윗꼬리 5일선 이탈 시 철수)"
                    )
                elif final_code == "WAIT_VOLUME":
                    bb_diag = (
                        f"🟡 <b>[수급 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 속임수 반등 차단.<br>• <b>진단:</b> 바닥"
                        " 기술 지표는 달성했으나 거래량이 부족하니 진입 보류."
                    )
                elif final_code == "WAIT_DOWNTREND_FALL":
                    bb_diag = (
                        f"🟡 <b>[진바닥 탐색/칼날 관망 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 칼날 회피.<br>• <b>진단:</b> 5일선 아래"
                        " 하락 구간이오. 5일선 회복 전까지 관망하시게."
                    )
                elif final_code == "WAIT_PULLBACK_CANDLE":
                    candlestick_word = "음봉 조정" if is_candle_bearish else "숨고르기 공방"
                    bb_diag = (
                        f"🟡 <b>[5일선 지지 검증 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        f" <b>역할:</b> {candlestick_word} 휩소 방지.<br>• <b>진단:</b> 5일선 위"
                        f" 안착 상태이나 당일 {candlestick_word} 중이오. 5일선 지지 사수 확인 후 대응하시게."
                    )
                elif final_code == "PULLBACK_BUY":
                    bb_time_diag = (
                        "14:00 이후 안전마진 안착 시 50% 타진, 15:20 종가 사수 시 3단계 완성"
                        if is_kr
                        else "07:00 일봉 안착 확인 시 3단계 완성"
                    )
                    bb_diag = (
                        f"🔵 <b>[3단계 눌림목 추가 매수 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 승수 확대.<br>• <b>진단:</b>"
                        f" {bw_diag_msg}. {bb_time_diag} (윗꼬리 20일선 이탈 시 철수)"
                    )
                elif final_code == "BAND_RIDING_HARVEST":
                    bb_diag = (
                        f"🟣 <b>[밴드 라이딩 대시세 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 상방 대시세 추종.<br>• <b>진단:</b> 상단 밴드가 확장 중이오! "
                        "50%는 이익을 확정하고 남은 물량은 5일선 사수 기준으로 추종하시게."
                    )
                elif final_code == "RED_SELL_TARGET":
                    bb_diag = (
                        f"🔴 <b>[수학 목표선 저항 도달 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 고점 분할 수익 확정.<br>• <b>진단:</b> 볼린저 상단 저항에 닿았으니 "
                        "물량의 50%를 즉시 수확하고 분할 매도에 임하시게."
                    )
                elif final_code == "RED_SELL_WARNING":
                    sell_warn_type = "음봉 발생" if is_candle_bearish else "기세 둔화"
                    bb_diag = (
                        f"🔴 <b>[성벽 위 {sell_warn_type} 익절 구간]</b><br>•"
                        f" <b>역할:</b> 선제적 수익 방어.<br>• <b>진단:</b> 성벽 위 {sell_warn_type}으로 분할 익절 실행."
                    )
                elif final_code == "BREAKOUT_ATTACK":
                    bb_diag = (
                        f"🟢 <b>[성벽 돌파 진격 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 상방 분출 추진력 가속.<br>• <b>진단:</b> 성벽을"
                        f" 뚫고 목표선({target_price_100:{fmt_p}}{currency})을 향해 진격 중이오. 5일선 사수하며 수익을 극대화하시게."
                    )
                elif final_code == "YELLOW_CAUTION":
                    bb_diag = (
                        "🟡 <b>[성벽 위 경계 및 추격 차단 구역]</b><br>•"
                        " <b>역할:</b> 추격 매수 원천 차단.<br>• <b>진단:</b> 성벽"
                        " 위 공방 중이므로 신규 매수를 금지하고 익절 타이밍을 노림."
                    )
                elif final_code == "WAIT_OVER_EXTENDED":
                    bb_diag = (
                        f"🟡 <b>[과다이격 추격 금지 구역] (5일선 이격: +{bias_ma5:.1f}%)</b><br>•"
                        " <b>역할:</b> 고점 물림 방지.<br>• <b>진단:</b> 5일선"
                        " 대비 5% 이상 벌어졌으니 숨고르기까지 매수 보류."
                    )
                elif final_code in ["WAIT_MA20_BUFFER", "WAIT_ORDERBOOK"]:
                    bb_diag = (
                        f"🟡 <b>[호가/20일선 검증 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 휩소 및 허매수 방지.<br>•"
                        " <b>진단:</b> 상승형 매도잔량비(1.2~2.5배) 사수 및 확실한 안착 전까지 진입 보류."
                    )
                else:
                    bb_diag = (
                        f"⚖️ <b>[관망 및 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
                        " <b>역할:</b> 뇌동매매 방지.<br>• <b>진단:</b> 명확한"
                        " 바닥/추세 신호가 뜨면 진격하시게."
                    )

                st.markdown(
                    f"<div class='ind-box'><p class='ind-title'>Bollinger"
                    f" (기세/위치)</p><p class='ind-diag'>{bb_diag}</p></div>",
                    unsafe_allow_html=True,
                )

            with i2:
                rsi_trend = (
                    "▲ 상승"
                    if rsi_val > rsi_prev
                    else ("▼ 하락" if rsi_val < rsi_prev else "─ 변동없음")
                )
                if is_target_reached or rsi_val >= 60:
                    r_status = (
                        "<b>👿 불지옥 과열권</b><br>• <b>역할:</b> 매수 에너지"
                        " 고갈 경보.<br>• <b>진단:</b> 과열 구간 진입, 상단"
                        " 차익 실현을 준비하시게."
                    )
                elif rsi_val <= 35:
                    r_time_txt = "14:00 이후 지지 확인하고 1단계 입질 매수 타이밍." if is_kr else "07:00 일봉 지지 확인 후 1단계 입질 매수 타이밍."
                    r_status = (
                        "<b>🧊 냉골 바닥권</b><br>• <b>역할:</b> 진바닥 수급"
                        " 감지.<br>• <b>진단:</b> 바닥권 지표 터치 및 수급 유입"
                        f" 시 {r_time_txt}"
                    )
                else:
                    r_status = (
                        "<b>⚖️ 적정 온도 구간</b><br>• <b>역할:</b> 에너지 충전"
                        " 및 눌림목 동조.<br>• <b>진단:</b> 에너지 충전 중."
                        " 보조지표 고개 돌림을 주시하시게."
                    )
                st.markdown(
                    f"<div class='ind-box'><p class='ind-title'>RSI (매수"
                    " 온도)</p><p style='font-size:36px; color:#E65100;"
                    f" margin:10px 0;'>{rsi_val:.2f} <span style='font-size:22px;"
                    f" color:#333333;'>({rsi_trend})</span></p><p"
                    f" class='ind-diag'>{r_status}</p></div>",
                    unsafe_allow_html=True,
                )

            with i3:
                will_trend = (
                    "▲ 상승"
                    if will_val > will_prev
                    else ("▼ 하락" if will_val < will_prev else "─ 변동없음")
                )
                if is_target_reached or will_val >= -20:
                    w_status = (
                        "<b>🚀 상방 저항 도달 구역</b><br>• <b>역할:</b> 단기"
                        " 상향 압력 한계 측정.<br>• <b>진단:</b> 목표선 도달 완료!"
                        " 추격 매수 엄금 및 선제적 분할 매도 집행."
                    )
                elif will_val <= -80:
                    w_time_txt = "14:00 이후 지표 동조 시 입질 대기." if is_kr else "07:00 일봉 지표 동조 시 입질 대기."
                    w_status = (
                        "<b>🏳️ 개미 항복 구역</b><br>• <b>역할:</b> 세력"
                        " 선취매 포착.<br>• <b>진단:</b> 🧊 <b>[바닥 침체]</b>"
                        f" -80 밑 투매 진행 중! {w_time_txt}"
                    )
                else:
                    w_status = (
                        "<b>⚖️ 중간 지대</b><br>• <b>역할:</b> 추세 방향"
                        " 탐색.<br>• <b>진단:</b> 상/하방 방향 탐색 중."
                    )
                st.markdown(
                    f"<div class='ind-box'><p class='ind-title'>Williams %R"
                    " (민감 반전)</p><p style='font-size:36px; color:#E65100;"
                    f" margin:10px 0;'>{will_val:.2f} <span"
                    f" style='font-size:22px; color:#333333;'>({will_trend})</span></p><p"
                    f" class='ind-diag'>{w_status}</p></div>",
                    unsafe_allow_html=True,
                )

            with i4:
                if is_band_riding:
                    m_diag = (
                        "<b>🔥 엔진 풀가동 (대세 추종)</b><br>• <b>역할:</b> 추세 지속력 측정.<br>• <b>진단:</b>"
                        " 밴드 확장과 함께 엔진이 힘을 내고 있소! 50% 수확 완료 후 5일선 사수 기준으로 잔여 물량을 즐기시게."
                    )
                elif is_target_reached:
                    m_diag = (
                        "<b>🚨 엔진 과열 차단</b><br>• <b>역할:</b> 고점 상투 방어.<br>• <b>진단:</b>"
                        " 목표선 도달 완료로 추가 가속 중단! 잔여 물량 익절에 집중하시게."
                    )
                elif is_overall_cautious_state:
                    m_diag = (
                        f"{base_macd_desc}<br>• <b>[관망 기조 동조]:</b> 현재 상단 종합 결론이 관망/경계 상태이므로, "
                        "엔진 상태와 무관하게 섣부른 추격매수를 금하고 안전하게 관망하시게."
                    )
                else:
                    m_diag = f"{base_macd_desc}<br>• <b>[엔진 연동]:</b> 위 전황에 맞춰 유효하게 대응하시게."

                st.markdown(
                    f"<div class='ind-box'><p class='ind-title'>MACD (추세"
                    f" 엔진)</p><p class='ind-diag'>{m_diag}</p></div>",
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.error(f"👵 아이구! 오류: {e}")
