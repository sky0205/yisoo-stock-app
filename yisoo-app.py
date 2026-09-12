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
    page_title="이수할아버지의 냉정 진단기 v36077", layout="wide"
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


# --- [보급로 최적화 캐싱 장치] ---
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


def fetch_kr_orderbook(symbol):
    return {
        "ask": 0.0,
        "bid": 0.0,
        "ratio": None,
        "ok": False,
        "msg": "실시간 호가 API 미연결 (수동 입력 필요)",
    }


# 스타일 정의
st.markdown(
    """
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
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
        tnx_val, tnx_chg = data["t_last"], (data["t_last"] / data["t_prev"] - 1) * 100
        u_val, u_chg = data["u_last"], (data["u_last"] / data["u_prev"] - 1) * 100

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("나스닥 (NASDAQ)", f"{data['n_last']:,.2f}", f"{n_chg:+.2f}%")
        c2.metric("S&P 500 (SPX)", f"{data['s_last']:,.2f}", f"{s_chg:+.2f}%")
        c3.metric("다우존스 (DJI)", f"{data['d_last']:,.2f}", f"{d_chg:+.2f}%")
        c4.metric("미 국채 10년 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
        c5.metric("원/달러 환율", f"{u_val:,.2f}원", f"{u_chg:+.2f}%")
        st.info("🧐 **이수 할배의 글로벌 전황 판독 완료**")
    except Exception:
        st.error("⚠️ 글로벌 데이터 호출 불가")


st.title("🧐 이수할아버지의 냉정 진단기 v36077 (종목명 및 전일비 복원 완벽판)")
display_global_risk()
st.divider()

col_symbol, col_manual, col_avg, col_ask, col_bid, col_btn = st.columns(
    [1.5, 1.4, 1.4, 1.4, 1.4, 1.0]
)

with col_symbol:
    raw_symbol_input = st.text_input("📊 종목번호", "005930")
    symbol = raw_symbol_input.strip()

with col_manual:
    manual_price_str = st.text_input("⚡ 수동 실시간가 (선택)", value="", help="직접 가격 적으시면 자동 시세 우선 적용").strip()

with col_avg:
    user_avg_price = st.number_input("💡 보유 평단가", min_value=0.0, value=0.0, step=100.0)

with col_ask:
    manual_ask = st.number_input("🔴 HTS 총매도잔량", min_value=0.0, value=0.0, step=1.0, format="%.2f", help="천주 단위 입력")

with col_bid:
    manual_bid = st.number_input("🔵 HTS 총매수잔량", min_value=0.0, value=0.0, step=1.0, format="%.2f", help="천주 단위 입력")

with col_btn:
    st.write("")
    st.write("")
    if st.button("🔄 정밀 분석"):
        st.rerun()

first_entry_done = st.checkbox(
    "☑ 1차 진입 완료",
    value=st.session_state.get("first_entry_done", False),
    key="first_entry_done",
    help="1차 진입 후 숨고르기 판정 활성화 체크",
)

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=500)
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
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(api_url, headers=headers, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    auto_p = float(str(data["closePrice"]).replace(",", ""))
                    v_curr = float(str(data["accumulatedTradingVolume"]).replace(",", ""))
                    kr_fetched = True
            except Exception:
                pass

            if not kr_fetched and not df.empty:
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
                us_prev_p = getattr(info, "previous_close", None)
            except Exception:
                pass

            if auto_p == 0.0 and not df.empty:
                auto_p = float(df["Close"].iloc[-1])
                v_curr = float(df["Volume"].iloc[-1])

        # 호가창 데이터 처리
        ob_data = fetch_kr_orderbook(symbol) if is_kr else {"ok": False, "ratio": 0.0}
        if manual_ask > 0 and manual_bid > 0:
            calc_ratio = round(manual_ask / manual_bid, 2)
            ob_data = {
                "ask": manual_ask * 1000.0,
                "bid": manual_bid * 1000.0,
                "ratio": calc_ratio,
                "ok": True,
                "msg": "HTS 직접입력",
            }

        # 수동 시세 반영
        is_manual_mode = False
        if manual_price_str:
            try:
                parsed_val = float(manual_price_str.replace(",", "").replace("$", ""))
                if parsed_val > 0:
                    p = parsed_val
                    is_manual_mode = True
                else:
                    p = auto_p
            except ValueError:
                p = auto_p
        else:
            p = auto_p

        if df.empty:
            st.warning(f"⚠️ [{symbol}] 종목 데이터를 불러오지 못했구먼. 종목번호를 확인하시게.")
        else:
            df = df.ffill().dropna()
            df.index = pd.to_datetime(df.index).date
            today_date = now_local.date()

            # 장부 기반 전일 종가 정밀 산출
            if not is_kr and us_prev_p and us_prev_p > 0:
                prev_p = us_prev_p
            else:
                try:
                    df_sorted = df.sort_index()
                    if today_date in df_sorted.index:
                        df_past = df_sorted.drop(today_date, errors="ignore")
                    else:
                        df_past = df_sorted
                    prev_p = float(df_past["Close"].iloc[-1]) if len(df_past) >= 1 else p
                except Exception:
                    prev_p = float(df["Close"].iloc[-2]) if len(df) >= 2 else p

            if today_date in df.index:
                df.loc[today_date, "Close"] = p
                df.loc[today_date, "Volume"] = v_curr
            else:
                new_row = pd.DataFrame({"Open": [p], "High": [p], "Low": [p], "Close": [p], "Volume": [v_curr]}, index=[today_date])
                df = pd.concat([df, new_row])

            v_avg5 = float(df["Volume"].iloc[-6:-1].mean()) if len(df) >= 6 else float(df["Volume"].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0

            p_diff = p - prev_p
            p_chg = (p_diff / prev_p) * 100 if prev_p > 0 else 0

            vol_strength = 100.0 if is_manual_mode else v_ratio

            today_open = float(df["Open"].iloc[-1])
            today_high = float(df["High"].iloc[-1])
            today_low = float(df["Low"].iloc[-1])
            is_down_trend_v = (p < prev_p) and (p_chg < 0)
            is_candle_bearish = p < today_open

            # 보조지표 연산 (20/2, 14/6, 14/9)
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

            bandwidth = ((up_b - low_b) / mid_line) * 100 if mid_line > 0 else 0

            has_enough_ma120 = len(df) >= 120 and pd.notna(df["MA120"].iloc[-1])
            ma5_val = float(df["MA5"].iloc[-1]) if (len(df) >= 5 and pd.notna(df["MA5"].iloc[-1])) else p
            ma60_val = float(df["MA60"].iloc[-1]) if (len(df) >= 60 and pd.notna(df["MA60"].iloc[-1])) else mid_line
            ma120_val = float(df["MA120"].iloc[-1]) if has_enough_ma120 else 0.0

            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            is_ma5_safe = p >= ma5_val

            # 호가 안정성 판정
            ob_ratio_val = ob_data.get("ratio")
            ob_ratio_available = ob_ratio_val is not None and float(ob_ratio_val) >= 0
            if ob_ratio_available:
                is_orderbook_safe = float(ob_ratio_val) <= 1.5
            else:
                is_orderbook_safe = False

            is_bandwidth_ok = bandwidth >= 12.0
            bw_diag_msg = f"밴드폭 {bandwidth:.1f}%"

            # 캔들 구조
            candle_range = max(0.01, today_high - today_low)
            lower_tail = min(today_open, p) - today_low
            body_len = abs(today_open - p)
            is_pure_bullish_candle = p >= today_open
            is_bottom_lower_tail = (lower_tail >= candle_range * 0.45 or lower_tail >= body_len * 1.3) and (p_chg >= 0.0)
            is_valid_bottom_candle = (is_pure_bullish_candle or is_bottom_lower_tail) and (not is_down_trend_v)
            is_valid_buy_candle = is_pure_bullish_candle or ((lower_tail >= candle_range * 0.45) and (p >= ma5_val))

            # 방어선 및 목표선
            defense_line = max(float(df["High"].iloc[-min(21, len(df)):-1].max()) * 0.93 if len(df) > 1 else p * 0.93, mid_line)
            target_price_100 = up_b
            is_target_reached = p >= (target_price_100 * 0.995)
            is_on_the_wall = (p >= defense_line) and (p < target_price_100)
            is_band_riding = is_target_reached and bandwidth >= 15.0 and is_ma5_safe and (p >= today_open)

            bottom_score = int(df["Close"].iloc[-1] <= low_b * 1.02) + int(rsi_val <= 35) + int(will_val <= -80)
            recent_bottom_memory = bottom_score >= 2

            is_bottom_entry_signal = (not is_ma5_safe) and (bottom_score >= 2) and (vol_strength >= 80) and (not is_down_trend_v) and (not is_macd_reverse_deepening) and is_valid_bottom_candle and (not is_target_reached)
            is_escape_buy_signal = is_ma5_safe and (bottom_score >= 2 or recent_bottom_memory) and (vol_strength >= 80) and (not is_macd_reverse_deepening) and is_valid_buy_candle and is_bandwidth_ok and is_orderbook_safe and (not is_target_reached)

            # ★ [종목명 복원 볼트 장치]
            if is_kr:
                core_vault = {
                    "005930": "삼성전자", "000660": "SK하이닉스", "033100": "제룡전기",
                    "257720": "실리콘투", "058610": "에스피지", "010140": "삼성중공업",
                    "068270": "셀트리온", "272210": "한화시스템", "101490": "에스앤에스텍", "051600": "한전KPS"
                }
                final_display_name = core_vault.get(clean_symbol, f"국내종목 ({symbol})")
                if clean_symbol not in core_vault:
                    try:
                        url = f"https://finance.naver.com/item/main.naver?code={clean_symbol}"
                        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
                        soup = BeautifulSoup(res.text, "html.parser")
                        final_display_name = soup.select_one(".wrap_company h2 a").text.strip()
                    except Exception:
                        try:
                            df_krx_backup = load_krx_listing()
                            final_display_name = df_krx_backup[df_krx_backup["Code"] == clean_symbol]["Name"].values[0]
                        except Exception:
                            final_display_name = f"국내종목 ({symbol})"
            else:
                us_vault = {"TSLA": "테슬라", "NVDA": "엔비디아", "AAPL": "애플", "MSFT": "마이크로소프트", "IONQ": "아이온큐", "CPNG": "쿠팡"}
                tk = symbol.upper()
                kor_name = us_vault.get(tk, tk)
                final_display_name = f"{kor_name} ({tk})"

            safe_display_name = html.escape(final_display_name)

            # ==================================================================
            # ★ [신호등 우선순위 분기 논리]
            # ==================================================================
            is_stop_loss_triggered = (user_avg_price > 0 and p < ma5_val * 0.95) or (recent_bottom_memory and p < prev_low)

            if is_stop_loss_triggered:
                final_code = "STOP_LOSS_ALERT"
                sig = "🚨 [비상 손절] 바닥권 전저점 또는 생명선 이탈!"
                col = "#D32F2F"
                final_adv = "• <b>[최종 결론]</b> 미련을 버리고 즉시 전량 칼손절 후퇴하시게."
            elif is_band_riding:
                final_code = "BAND_RIDING_HARVEST"
                sig = "🟣 [밴드 라이딩 대시세] 목표선 상방 확장 중!"
                col = "#6A1B9A"
                final_adv = "• <b>[최종 결론]</b> 볼린저 상단 확장 중! 50% 익절 후 5일선 기준으로 잔여 추종하시게."
            elif is_target_reached:
                final_code = "RED_SELL_TARGET"
                sig = "🔴 [목표 도달] 수학 목표선 저항! 1차 50% 수확!"
                col = "#D32F2F"
                final_adv = "• <b>[최종 결론]</b> 상단 저항 도달 완료! 신규 진입을 금하고 분할 현금화를 집행하시게."
            elif not is_orderbook_safe:
                final_code = "WAIT_ORDERBOOK"
                sig = "🟡 [관망/보류] 실시간 호가 미연결 또는 매도벽 우세"
                col = "#F57C00"
                final_adv = "• <b>[최종 결론]</b> 호가 검증 데이터가 부족하거나 매도벽이 두터우니 손가락을 묶고 관망하시게."
            elif is_on_the_wall and (vol_strength >= 150) and (not is_down_trend_v):
                final_code = "BREAKOUT_ATTACK"
                sig = "🟢 [돌격] 성벽 강력 돌파 / 수확선 진격!"
                col = "#2E7D32"
                final_adv = "• <b>[최종 결론]</b> 성벽을 돌파했소! 5일선을 타고 목표선까지 거침없이 달리시게."
            elif is_bottom_entry_signal or is_escape_buy_signal:
                final_code = "ESCAPE_BUY"
                sig = "🟢 [진바닥 탈출/안착] 매수 진격 유효 구역"
                col = "#2E7D32"
                final_adv = "• <b>[최종 결론]</b> 바닥 지지 및 5일선 안착 확인! 분할 매수 타진 가능 구역이오."
            elif vol_strength < 80 and not (first_entry_done or p_chg >= 0):
                final_code = "WAIT_VOLUME"
                sig = "🟡 [거래절벽 관망] 수급 마름 / 섣부른 진입 금지"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> 보정강도 {vol_strength:.1f}점으로 수급이 부족하니 속지 말고 관망하시게."
            else:
                final_code = "WAIT_GENERAL"
                sig = "🟡 [관망] 조건 미충족 / 뇌동매매 금지"
                col = "#FBC02D"
                final_adv = "• <b>[최종 결론]</b> 명확한 주도 신호가 충족되지 않았으므로 차분히 관망을 유지하시게."

            # 신호등 박스 표출
            st.markdown(
                f"<div class='signal-box' style='background-color: {col};'>"
                f"<div class='signal-text'>{sig}</div>"
                f"<div class='signal-subtext'>{final_adv}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # 전광판 현황 출력 (종목명과 전일비 정상 출력)
            st.markdown(f"### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(
                f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>"
                f"<p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{safe_display_name}</p>"
                f"<p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>",
                unsafe_allow_html=True,
            )

            st.success("👵 종목명과 전일비 계산 장부가 완벽하게 복원되었사옵니다, 할배!")

    except Exception as e:
        st.error(f"👵 아이구! 오류가 발생했사옵니다: {e}")
