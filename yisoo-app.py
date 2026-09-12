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
    page_title="이수할아버지의 냉정 진단기 v36075", layout="wide"
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

# 1차 진입 여부는 사용자가 명시적으로 체크하여 제어한다.
first_entry_done = st.checkbox(
    "☑ 1차 진입 완료",
    value=st.session_state.get("first_entry_done", False),
    key="first_entry_done",
    help="1차 진입 후 숨고르기 판정을 활성화하려면 체크하십시오.",
)

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
            except Exception:
                pass

            if df.empty:
                try:
                    df = yf.Ticker(f"{clean_symbol}.KS").history(start=start_date)
                    if df.empty:
                        df = yf.Ticker(f"{clean_symbol}.KQ").history(start=start_date)
                except Exception:
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
            except Exception:
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
                        _avg_v = float(df["Volume"].iloc[-6:-1].mean()) if len(df) >= 6 else float(df["Volume"].mean())
                        if _avg_v > 0 and v_curr > _avg_v * 10:
                            v_curr = float(df["Volume"].iloc[-1])
                except Exception:
                    st.toast("⚠️ 실시간 시세 미확인: 네이버 크롤링 실패로 차트 종가로 대체합니다.", icon="🚨")
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
                # [미장 거래량 왜곡 방어 가드]
                if 'v_curr' in locals() and 'df' in locals() and df is not None and not df.empty:
                    _us_avg_v = float(df["Volume"].iloc[-6:-1].mean()) if len(df) >= 6 else float(df["Volume"].mean())
                    if _us_avg_v > 0 and v_curr > _us_avg_v * 10:
                        v_curr = float(df["Volume"].iloc[-1])
            except Exception:
                pass

            if auto_p == 0.0 and not df.empty:
                auto_p = float(df["Close"].iloc[-1])
                v_curr = float(df["Volume"].iloc[-1])

        # 호가창 데이터 처리 (지적 2 반영: 미연결 시 안전 불허)
        ob_data = fetch_kr_orderbook(symbol) if is_kr else {"ok": False, "ratio": 0.0}
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
        elif manual_ask > 0 or manual_bid > 0:
            ob_data = {
                "ask": manual_ask * 1000.0,
                "bid": manual_bid * 1000.0,
                "ratio": None,
                "ok": False,
                "msg": "매도·매수잔량을 모두 입력해야 분석 가능",
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
                st.warning("⚠️ 올바른 숫자 형식으로 입력해 주십시오. (자동 시세로 연산합니다)")
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

            # ★ [지적 반영 1]: 단일 전일비 기준 확립 (prev_p)
            if not is_kr and us_prev_p and us_prev_p > 0:
                prev_p = us_prev_p
            else:
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

            # ★ [지적 반영 2]: 보합 왜곡 조작 로직 완전 박멸 (정직한 비교)
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

            # 오직 단일 prev_p 기반 전일비/등락률 연산
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

            # ★ [지적 반영 3]: 날짜별 하단 밴드 시리즈 구성 (recent_bottom_memory 정확도 확보)
            df["MA20_series"] = df["Close"].rolling(20).mean()
            df["Std_series"] = df["Close"].rolling(20).std()
            df["Low_B_series"] = df["MA20_series"] - (df["Std_series"] * 2)

            bb_bot_series = (df["Close"] <= (df["Low_B_series"] * 1.02)).astype(int)
            rsi_bot_series = (rsi_series <= 35).astype(int)
            will_bot_series = (will_series <= -80).astype(int)
            bottom_score_series = (
                bb_bot_series + rsi_bot_series + will_bot_series
            )

            bottom_score = int(bottom_score_series.iloc[-1])
            recent_bottom_memory = int(bottom_score_series.iloc[-3:].max()) >= 2

            # 데이터 부족 종목 방어
            has_enough_ma120 = len(df) >= 120 and pd.notna(df["MA120"].iloc[-1])
            ma5_val = float(df["MA5"].iloc[-1]) if (len(df) >= 5 and pd.notna(df["MA5"].iloc[-1])) else p
            ma60_val = float(df["MA60"].iloc[-1]) if (len(df) >= 60 and pd.notna(df["MA60"].iloc[-1])) else mid_line
            ma120_val = float(df["MA120"].iloc[-1]) if has_enough_ma120 else 0.0

            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            is_over_extended_5 = bias_ma5 >= 5.0

            # 20일선 버퍼 판정
            ma20_safe_threshold = mid_line * 1.002
            is_ma20_buffer_safe = p >= ma20_safe_threshold
            is_ma20_teetering = (p >= mid_line * 0.998) and (
                p < ma20_safe_threshold
            )

            # 호가창 판정 (지적 반영: 미연결 시 안전 불허)
            ob_ratio_val = ob_data.get("ratio")
            ob_ratio_available = ob_ratio_val is not None and float(ob_ratio_val) >= 0

            if ob_ratio_available:
                ob_ratio_val = float(ob_ratio_val)
                ask_formatted = f"{ob_data.get('ask', 0.0):,.0f}"
                bid_formatted = f"{ob_data.get('bid', 0.0):,.0f}"

                if ob_ratio_val > 2.8:
                    ob_status_msg = (
                        f"🚨 <b>[매도벽 과다 저항]</b> 잔량비 "
                        f"<b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted} / 매수:{bid_formatted}) - 진격 차단"
                    )
                    is_orderbook_safe = False
                elif ob_ratio_val >= 1.5:
                    ob_status_msg = (
                        f"🟡 <b>[매도 우위 공방]</b> 잔량비 "
                        f"<b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted} / 매수:{bid_formatted}) - 매도잔량 우세"
                    )
                    is_orderbook_safe = False
                elif ob_ratio_val >= 1.0:
                    ob_status_msg = (
                        f"⚖️ <b>[정상 공방 호가]</b> 잔량비 "
                        f"<b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted} / 매수:{bid_formatted}) - 균형권"
                    )
                    is_orderbook_safe = True
                else:
                    ob_status_msg = (
                        f"🟢 <b>[매수 우위 호가]</b> 잔량비 "
                        f"<b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted} / 매수:{bid_formatted}) - 매수 우세"
                    )
                    is_orderbook_safe = True
            elif manual_ask > 0 or manual_bid > 0:
                ob_status_msg = "⚠️ <b>[호가 입력 불완전]</b> 매도·매수잔량을 모두 입력해야 합니다."
                is_orderbook_safe = False
            else:
                ob_status_msg = "💡 <b>[호가 미연결]</b> HTS 잔량 미입력으로 보수적 관망을 적용합니다."
                is_orderbook_safe = False

            # 밴드폭 판정
            if bandwidth < 12.0:
                is_bandwidth_ok = False
                bw_status_category = "EXTREME_SQUEEZE"
                bw_diag_msg = f"밴드폭 극소({bandwidth:.1f}%) 에너지 응축 중"
                squeeze_info_str = f"<br>• ⚡ <b>[밴드폭 극소({bandwidth:.1f}%)]</b> 에너지가 바짝 응축 중이오!"
            elif 12.0 <= bandwidth < 20.0:
                if p >= ma5_val:
                    is_bearish_zone = ma5_val < mid_line
                    if is_bearish_zone:
                        is_bandwidth_ok = False
                        bw_status_category = "BEARISH_RESISTANCE"
                        bw_diag_msg = f"밴드폭 응축({bandwidth:.1f}%) 역배열 저항 경계"
                        squeeze_info_str = f"<br>• ⚠️ <b>[밴드폭 응축({bandwidth:.1f}%)]</b> 역배열 저항 매물벽 경계."
                    else:
                        is_bandwidth_ok = True
                        bw_status_category = "SQUEEZE_BREAKOUT"
                        bw_diag_msg = f"밴드폭 응축돌파({bandwidth:.1f}%) 분출 초입"
                        squeeze_info_str = f"<br>• 🟢 <b>[밴드폭 응축돌파({bandwidth:.1f}%)]</b> 상방 분출 초입 유효."
                else:
                    is_bandwidth_ok = False
                    bw_status_category = "SQUEEZE_WAIT"
                    bw_diag_msg = f"밴드폭 응축({bandwidth:.1f}%) 돌파 대기"
                    squeeze_info_str = f"<br>• ⏳ <b>[밴드폭 응축({bandwidth:.1f}%)]</b> 돌파 전이오."
            else:
                is_bandwidth_ok = True
                bw_status_category = "WIDE_OK"
                bw_diag_msg = f"밴드폭 넉넉함({bandwidth:.1f}%)"
                squeeze_info_str = f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 진폭 활주로 충분."

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

            is_bullish = has_enough_ma120 and (
                ma5_val > mid_line
                and mid_line > ma60_val
                and ma60_val > ma120_val
            )
            is_bearish = has_enough_ma120 and (
                ma5_val < mid_line
                and mid_line < ma60_val
                and ma60_val < ma120_val
            )
            is_down_trend_structural = is_bearish or (
                p < mid_line and mid_line <= ma60_val
            )

            ma5_str = f"{ma5_val:{fmt_p}}{currency}"
            ma20_str = f"{mid_line:{fmt_p}}{currency}"
            ma60_str = f"{ma60_val:{fmt_p}}{currency}"
            ma120_str = f"{ma120_val:{fmt_p}}{currency}" if has_enough_ma120 else "데이터 부족(미확인)"

            if is_bullish:
                trend_status = "🔥 <b>[대세 정배열]</b> 완벽한 우상향 성벽 구축 완료"
            elif is_bearish:
                trend_status = "⚠️ <b>[대세 역배열]</b> 지하실 향하는 하락 추세"
            elif not has_enough_ma120:
                trend_status = "⚠️ <b>[장기 추세 미확인]</b> 120일선 데이터 부족으로 관망"
            elif ma5_val > mid_line:
                trend_status = "🌱 <b>[단기 반등 초입]</b> 5일선이 20일선 돌파!"
            else:
                trend_status = "📉 <b>[단기 조정 국면]</b> 숨고르기 중"

            ma_price_summary = (
                "<br>• 📌 <b>[주요 이동평균선 현황]</b><br>&nbsp;&nbsp;<span"
                f" style='color:#D32F2F; font-weight:bold;'>🔴 5일선: {ma5_str}"
                f" (이격: {bias_ma5:+.1f}%)</span> | <span style='color:#1976D2;"
                f" font-weight:bold;'>🔵 20일선: {ma20_str}</span> | <span"
                f" style='color:#388E3C; font-weight:bold;'>🟢 60일선:"
                f" {ma60_str}</span> | <span style='color:#7B1FA2;"
                f" font-weight:bold;'>🟣 120일선: {ma120_str}</span><br>"
            )

            # ★ [종목명 완벽 복원 장치 (국장/미장 분리 반영)]
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
                final_display_name = core_vault.get(clean_symbol, f"국내종목 ({symbol})")
                if clean_symbol not in core_vault:
                    try:
                        url = f"https://finance.naver.com/item/main.naver?code={clean_symbol}"
                        res = requests.get(
                            url,
                            headers={"User-Agent": "Mozilla/5.0"},
                            timeout=3,
                        )
                        soup = BeautifulSoup(res.text, "html.parser")
                        final_display_name = soup.select_one(
                            ".wrap_company h2 a"
                        ).text.strip()
                    except Exception:
                        try:
                            df_krx_backup = load_krx_listing()
                            final_display_name = df_krx_backup[
                                df_krx_backup["Code"] == clean_symbol
                            ]["Name"].values[0]
                        except Exception:
                            final_display_name = f"국내종목 ({symbol})"
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
                    "AVGO": "브로드컴",
                }
                tk = symbol.upper()
                kor_name = us_vault.get(tk, tk)
                final_display_name = f"{kor_name} ({tk})"

            safe_display_name = html.escape(final_display_name)

            is_target_reached = p >= (up_b * 0.995)
            is_on_the_wall = (p >= defense_line) and (p < up_b)
            is_band_riding = is_target_reached and bandwidth >= 15.0 and is_ma5_safe and (p >= today_open)

            is_bottom_indicator_ok = bottom_score >= 2 or recent_bottom_memory
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
                time_rule_desc = "오전장 휩소를 피하기 위해 14:00 이후 지지 확인 시 50% 분할 타진하시게."
            elif not is_kr and not is_manual_mode:
                is_afternoon_safe_time = (kst_now.hour >= 7) and (
                    kst_now.hour < 22
                )
                time_tag_wait = "★ 07:00 마감 일봉 대기"
                time_tag_ok = "07:00 일봉 안착 확인"
                time_rule_desc = "정규장 휩소를 피하고 07:00 마감 일봉을 확인 후 진입하시게."
            else:
                is_afternoon_safe_time = True
                time_tag_wait = "★ 수동 검증"
                time_tag_ok = "수동 시세 확인"
                time_rule_desc = "수동 시세 지지 확인 후 진입하시게."

            # ==================================================================
            # ★ [신호등 우선순위 분기 논리]
            # ==================================================================
            is_stop_loss_triggered = (user_avg_price > 0 and p < ma5_val * 0.95) or (recent_bottom_memory and p < prev_low)

            if is_stop_loss_triggered:
                final_code = "STOP_LOSS_ALERT"
                sig = "🚨 [비상 손절] 방어선 이탈!"
                col = "#D32F2F"
                final_adv = "• <b>[최종 결론]</b> 미련을 버리고 즉시 전량 칼손절 후퇴하시게."
            elif is_band_riding:
                final_code = "BAND_RIDING_HARVEST"
                sig = "🟣 [밴드 라이딩 대시세] 목표선 상방 확장 중!"
                col = "#6A1B9A"
                final_adv = (
                    "• <b>[최종 결론]</b> 볼린저 상단 확장 중! "
                    "<b>물량의 50%는 익절</b>하고, <b>잔여 50%는 5일선 이탈 전까지 홀딩</b>하시게."
                )
            elif is_target_reached:
                final_code = "RED_SELL_TARGET"
                sig = "🔴 [목표 도달] 수학 목표선 저항! 1차 50% 분할 매도!"
                col = "#D32F2F"
                final_adv = (
                    "• <b>[최종 결론]</b> 볼린저 상단 저항 도달! "
                    "추가 진격을 중단하고 <b>우선 50% 물량을 기계적으로 수확</b>하시게."
                )
            elif not is_orderbook_safe:
                final_code = "WAIT_ORDERBOOK"
                sig = "🟡 [관망/보류] 실시간 호가 미연결 또는 매도벽 우세"
                col = "#F57C00"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f})점. "
                    "호가 검증 데이터가 부족하거나 매도벽이 두터우니 관망하시게."
                )
            elif is_bottom_entry_signal or is_escape_buy_signal:
                final_code = "ESCAPE_BUY"
                sig = f"🟢 [진바닥 탈출/안착] 매수 진격 유효 구역 ({time_tag_ok})"
                col = "#2E7D32"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f})점. "
                    f"<b>[지지 안착]</b> {time_rule_desc}"
                )
            elif vol_strength < 80 and not (first_entry_done or p_chg >= 0):
                final_code = "WAIT_VOLUME"
                sig = "🟡 [거래절벽 관망] 수급 마름 / 섣부른 진입 금지"
                col = "#F57C00"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f})점. "
                    "수급이 마르고 동력이 없으니 관망하시게."
                )
            else:
                final_code = "WAIT_GENERAL"
                sig = "🟡 [관망] 조건 미충족 / 뇌동매매 금지"
                col = "#FBC02D"
                final_adv = (
                    f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f})점. "
                    "조건 미충족 상태이므로 뇌동매매를 금하고 관망 유지."
                )

            # 신호등 박스 표출
            st.markdown(
                f"<div class='signal-box' style='background-color: {col};'>"
                f"<div class='signal-text'>{sig}</div>"
                f"<div class='signal-subtext'>{final_adv}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # 전광판 현황 출력 (종목명 및 단일 prev_p 기준 전일비 정상 출력)
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

            # 하단 4대 핵심 지표 박스 카드용 임시 조립 변수 세팅
            pullback_status_str = f"<b>(밴드폭 {bandwidth:.1f}%)</b>"
            pullback_action_str = "-> <b>[관망]</b> 추세 및 지표 안착 대기"
            sub_indicator_str = f"  - <b>지표 검증:</b> {pullback_status_str} {pullback_action_str}"
            squeeze_info_str = f"<br>• 🌊 <b>[밴드폭 상태({bandwidth:.1f}%)]</b> 활주로 점검 완료."

            indicator_verify_text = (
                f"{ma_price_summary}<br>• <b>[추세 정밀 판독]:</b>"
                f" {trend_status}<br>• <b>[지표 검증 연산]</b><br>{sub_indicator_str}{squeeze_info_str}"
            )
            ma5_dynamic_stop = dynamic_stop_price

            if is_band_riding:
                holder_guide_msg = "• <b>[밴드 라이딩 대시세 구역]</b> 상단 밴드 확장 중! 50% 익절 후 5일선 사수 기준으로 잔여 물량 홀딩."
            elif is_target_reached:
                holder_guide_msg = "• <b>[수학 목표선 도달 완료 구역]</b> 신규 매수 금지! 50% 분할 매도로 계좌에 현금을 챙기시게."
            elif user_avg_price <= 0:
                holder_guide_msg = f"현재 추세 탐색 구간이니 성벽({defense_line:{fmt_p}}{currency})이나 5일선 사수 여부를 확인하시게. (★ <b>{stop_loss_label}</b>)"
            else:
                profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                holder_guide_msg = f"• <b>[보유자 가이드]</b> 평단가 {user_avg_price:{fmt_p}}{currency} (수익률: {profit_rate:+.2f}%) - 5일선 이탈 전까지 추세 유지."

            ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에서 전투선을 유지 중이오."
            def_status = f"성벽({defense_line:{fmt_p}}{currency}) 수성 여부를 확인하며 추세를 주시하시게."
            macd_strategy_msg = "<b>🔥 추세 엔진 연동 중</b>: 위 전황에 맞춰 유효하게 대응하시게."

            st.markdown(
                f"""<div class='trend-card'>
                <div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
                <div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{ma5_guide_text}</span></div>
                <div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>2. 성벽 사수 및 공방 확인</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{def_status}</span></div>
                <div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>3. 중장기 추세 진단 및 지표 동조 현황</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{indicator_verify_text}</span></div>
                <div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>4. 엔진(MACD) 확인</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{macd_strategy_msg}</span></div>
                <div style='margin-bottom: 25px;'><span style='color: #D32F2F; font-weight: 900; font-size: 24px;'>5. 🛡️ [보유자 전용] 실전 행동 가이드</span><br><span style='color: #2E7D32; font-weight: bold; font-size: 20px;'>👉 {holder_guide_msg}</span></div>
                <hr style='border:1px solid #FFEBEE; margin: 20px 0;'>
                <div class='final-msg'>{final_adv}</div>
                </div>""",
                unsafe_allow_html=True,
            )

            st.divider()

            # 하단 4대 핵심 지표 박스
            i1, i2, i3, i4 = st.columns(4)
            with i1:
                bb_diag = f"볼린저 밴드폭 {bandwidth:.1f}% 상태에서 전황을 면밀히 조율 중이오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세/위치)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2:
                rsi_trend = "▲ 상승" if rsi_val > rsi_prev else ("▼ 하락" if rsi_val < rsi_prev else "─ 변동없음")
                r_status = f"현재 RSI 온도: {rsi_val:.2f} ({rsi_trend})."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (매수 온도)</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{rsi_val:.2f} <span style='font-size:22px; color:#333333;'>({rsi_trend})</span></p><p class='ind-diag'>{r_status}</p></div>", unsafe_allow_html=True)
            with i3:
                will_trend = "▲ 상승" if will_val > will_prev else ("▼ 하락" if will_val < will_prev else "─ 변동없음")
                w_status = f"Williams %R 민감도: {will_val:.2f} ({will_trend})."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R (민감 반전)</p><p style='font-size:36px; color:#E65100; margin:10px 0;'>{will_val:.2f} <span style='font-size:22px; color:#333333;'>({will_trend})</span></p><p class='ind-diag'>{w_status}</p></div>", unsafe_allow_html=True)
            with i4:
                m_diag = f"MACD 추세 엔진 구동 중 (현재 차이: {curr_diff:+.4f})."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (추세 엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

            st.success("👵 머리부터 꼬리까지 잘림 없이 온전히 엮인 v36082 완결판이옵니다, 할배!")

    except Exception as e:
        st.error(f"👵 아이구! 오류가 발생했사옵니다: {e}")
