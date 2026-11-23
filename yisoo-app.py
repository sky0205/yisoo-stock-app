import html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
import os

st.set_page_config(page_title="이수할아버지의 냉정 진단기 최종본", layout="wide")

# --- 🔒 자물쇠(비밀번호) 보안 장치 ---
def check_password():
    correct_pw = str(st.secrets.get("APP_PASSWORD", "1111"))

    def password_entered():
        if st.session_state["password"] == correct_pw:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.subheader("🔒 이수할아버지의 냉정 진단기 - 보안 접속")
        st.text_input("비밀번호를 입력하시구먼요:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.subheader("🔒 이수할아버지의 냉정 진단기 - 보안 접속")
        st.text_input("비밀번호를 입력하시구먼요:", type="password", on_change=password_entered, key="password")
        st.error("😕 비밀번호가 틀렸사옵니다. 다시 확인하시구먼요!")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- [보급로 최적화 캐싱 장치] ---
@st.cache_data(ttl=300)
def fetch_global_market():
    tickers = {"n": "^IXIC", "s": "^GSPC", "d": "^DJI", "t": "^TNX", "u": "USDKRW=X"}
    results = {}
    for k, tk in tickers.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}?interval=1d&range=1d"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
            meta = res.json()["chart"]["result"][0]["meta"]
            results[f"{k}_last"] = float(meta["regularMarketPrice"])
            results[f"{k}_prev"] = float(meta["chartPreviousClose"])
        except Exception:
            results[f"{k}_last"], results[f"{k}_prev"] = 0.0, 0.0
    return results

# --- [종목명 해독 통합 함수] ---
def get_stock_name(symbol, is_kr):
    if is_kr:
        clean_sym = str(symbol).strip().zfill(6)
        core_vault = {
            "005930": "삼성전자", "000660": "SK하이닉스", "033100": "제룡전기",
            "257720": "실리콘투", "058610": "에스피지", "010140": "삼성중공업",
            "068270": "셀트리온", "272210": "한화시스템", "101490": "에스앤에스텍",
            "051600": "한전KPS", "064350": "현대로템", "032300": "솔리드", "050890": "솔리드"
        }
        if clean_sym in core_vault:
            return core_vault[clean_sym]
        
        if not os.path.exists("krx_list.csv"):
            return f"국내종목 ({clean_sym})"
            
        try:
            try:
                with open("krx_list.csv", "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open("krx_list.csv", "r", encoding="cp949", errors="ignore") as f:
                    lines = f.readlines()
            
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    c1 = parts[0].strip().replace('"', '')
                    c2 = parts[1].strip().replace('"', '')
                    if c1.zfill(6) == clean_sym: return c2
                    elif c2.zfill(6) == clean_sym: return c1
        except Exception:
            pass
        return f"국내종목 ({clean_sym})"
    else:
        us_vault = {
            "TSLA": "테슬라", "NVDA": "엔비디아", "AAPL": "애플", "MSFT": "마이크로소프트",
            "AMZN": "아마존", "GOOGL": "알파벳A", "META": "메타", "IONQ": "아이온큐",
            "CPNG": "쿠팡", "NFLX": "넷플릭스", "SKHY": "SK하이닉스", "INTC": "인텔",
            "BE": "블룸에너지", "RKLB": "로켓랩", "AVGO": "브로드컴", "LRCX": "램리서치",
        }
        tk = symbol.upper()
        if tk in us_vault: 
            return f"{us_vault[tk]} ({tk})"
        try:
            info_dict = yf.Ticker(tk).info
            kor_name = info_dict.get("longName", info_dict.get("shortName", tk))
            return f"{kor_name} ({tk})"
        except Exception:
            return tk

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
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 12px; border: 2.5px solid #CFD8DC; text-align: center; box-shadow: 1px 1px 6px rgba(0,0,0,0.05); min-height: 175px; display: flex; flex-direction: column; justify-content: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 300px; margin-bottom: 18px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 24px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 19px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 12px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .final-msg { color: #D32F2F !important; font-size: 24px !important; font-weight: 900 !important; line-height: 1.5 !important; }
    /* 글로벌 지수 증감 비율칸(먹박스) 뿌리까지 완벽 투명화 */
    div[data-testid="stMetricDelta"],
    div[data-testid="stMetricDelta"] > div,
    div[data-testid="stMetricDelta"] * {
        background-color: transparent !important;
    }
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

    /* 🎯 종목번호 입력칸 완벽 관통 붉은색 테마 (먹물 방어벽 파괴판) */
    div[data-testid="stTextInput"]:has(input[aria-label*="종목번호"]) > div,
    div[data-testid="stTextInput"]:has(input[aria-label*="종목번호"]) [data-baseweb="input"],
    input[aria-label*="종목번호"] {
        background-color: #D32F2F !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 26px !important;
        font-weight: 900 !important;
        border-radius: 8px !important;
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

        avg_us_chg = (n_chg + s_chg + d_chg) / 3
        pos_cnt = sum([n_chg > 0, s_chg > 0, d_chg > 0])
        neg_cnt = sum([n_chg < 0, s_chg < 0, d_chg < 0])

        if pos_cnt == 3: market_mood = "미 3대 지수 동반 훈풍 속 안도 랠리!" if avg_us_chg >= 1.0 else "미 3대 지수 일제히 상승 마감!"
        elif neg_cnt == 3: market_mood = "미 3대 지수 동반 급락으로 투심 냉각!" if avg_us_chg <= -1.0 else "미 3대 지수 일제히 하락 (전면 약세 국면)!"
        else: market_mood = "미 3대 지수 혼조세 속 숨고르기 진행!"

        macro_alerts = []
        if tnx_val >= 5.0: 
            macro_alerts.append(f"🚨 [초고금리 발작] 국채 금리 {tnx_val:.3f}%! 5% 재돌파 초위험 구간!")
        elif tnx_val >= 4.5:
            if tnx_chg < 0:
                macro_alerts.append(f"⛅ [고금리 진정] 국채 금리 {tnx_val:.3f}%. 4.5% 이상 고금리나 전일 대비 하락하며 한숨 돌림")
            else:
                macro_alerts.append(f"⚠️ [고금리 경계] 국채 금리 {tnx_val:.3f}%. 4.5% 이상 유지되며 상방 압력 지속!")
        elif tnx_val <= 3.8: 
            macro_alerts.append(f"🌱 [금리 안정] 국채 금리 {tnx_val:.3f}% 안정권 진입")

        if u_val >= 1450: macro_alerts.append(f"🚨 [환율 격랑] 원/달러 {u_val:,.2f}원! 초위험 고환율 비상!")
        elif u_val >= 1400: macro_alerts.append(f"⚠️ [환율 경계] 원/달러 {u_val:,.2f}원 1,400원대 고착화 압박!")
        elif u_val >= 1380: macro_alerts.append(f"⚡ [환율 분기점] 원/달러 {u_val:,.2f}원! 외인 눈치보기")
        elif u_val <= 1330: macro_alerts.append(f"💵 [환율 우호] 원/달러 {u_val:,.2f}원 하향 안정세")

        if u_chg > 0.3: macro_alerts.append(f"📈 오늘 환율 {u_chg:+.2f}% 치솟는 중!")
        elif u_chg < -0.3: macro_alerts.append(f"📉 오늘 환율 {u_chg:+.2f}% 진정세")

        if tnx_val >= 5.0 and u_val >= 1400: 
            strategy = "초고금리와 고환율 동반 발작으로 외인 수급 이탈 우려가 큽니다. 추격매수를 멈추고 철저히 관망하시게."
        elif tnx_val >= 5.0:
            strategy = f"환율({u_val:,.2f}원)은 안정권이나 미 국채 금리({tnx_val:.3f}%) 초고금리 발작으로 기술주 하방 압력이 큽니다. 추격매수를 멈추고 철저히 관망하시게."
        elif u_val >= 1400:
            strategy = f"고환율({u_val:,.2f}원) 압박으로 외인 수급 이탈 우려가 큽니다. 추격매수를 멈추고 보수적으로 관망하시게."
        elif tnx_val >= 4.5 or u_val >= 1380: 
            if tnx_chg < 0:
                strategy = "매크로 고점(금리 4.5%↑)이나 단기 하락 진정세가 나타나고 있소. 5일선 지지 확인 후 선별적으로 타진하시게."
            else:
                strategy = "매크로 상단 저항(고금리 4.5%↑)이 여전히 강하니 방어선 위주로 보수적 대응하시게."
        elif avg_us_chg > 0.5 and tnx_val < 4.2 and u_val < 1350: 
            strategy = "매크로 환경이 우호적이니 거래량 실린 정석 눌림목 주도주 위주로 적극 공략하시게."
        else: 
            strategy = "장 초반 뇌동매매를 삼가고 지표 동조와 5일선 안착 여부를 확인하며 기민하게 대응하시게."

        macro_text = " | ".join(macro_alerts) if macro_alerts else "매크로 특이 동향 없음"
        st.markdown(
            f"<div style='background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 2.5px solid #CFD8DC; color: #263238; margin-bottom: 20px;'>"
            f"<div style='font-size: 20px; margin-bottom: 10px;'><b>🧐 이수 할배의 글로벌 판독:</b> <span style='color: #D32F2F; font-weight: bold;'>{market_mood}</span></div>"
            f"<div style='font-size: 18px; line-height: 1.8;'>• {macro_text}<br>• 💡 <b>[대응 전략]</b> {strategy}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    except Exception:
        st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기")
display_global_risk()
st.divider()

# ==============================================================================
# ★ [1단계: 종목별 수동 입력값 무한 기억 및 🎛️ 실전 타점 통제소 UI 개편]
# ==============================================================================
if 'price_memory' not in st.session_state:
    st.session_state.price_memory = {}

st.markdown("### 🎛️ 실전 정밀 타점 통제소")

col_sym, _ = st.columns([1, 3])
with col_sym:
    raw_symbol_input = st.text_input("📊 종목번호", value="272210")
    symbol = raw_symbol_input.strip()

mem_data = st.session_state.price_memory.get(symbol, {})
saved_open = float(mem_data.get('open', 0.0))
saved_prev = str(mem_data.get('prev', ""))
saved_pre = str(mem_data.get('pre', ""))
saved_avg = float(mem_data.get('avg', 0.0))
saved_1st = float(mem_data.get('1st', 0.0))
saved_ask = float(mem_data.get('ask', 0.0))
saved_bid = float(mem_data.get('bid', 0.0))

st.markdown("<hr style='margin: 5px 0 15px 0; border: 1px solid #CFD8DC;'>", unsafe_allow_html=True)

with st.expander("⚙️ [시장 기준 가격 및 수동 통제소] (필요 시 클릭하여 열기)", expanded=False):
    st.markdown("<span style='color:#1565C0; font-size:18px;'><b>[시장 기준 가격 통제]</b></span>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        manual_open = st.number_input("📌 HTS 호가창 시가 (0=자동)", value=saved_open, step=10.0, key=f"open_{symbol}")
    with c2:
        manual_prev_price_str = st.text_input("🎯 HTS 전일종가", value=saved_prev, help="전일 기준가", key=f"prev_{symbol}")
    with c3:
        manual_pre_price_str = st.text_input("us 미장 프리(Pre) 시세", value=saved_pre, help="미장 프리마켓 시세", key=f"pre_{symbol}")

    st.write("")

    st.markdown("<span style='color:#D32F2F; font-size:18px;'><b>[보유 계좌 및 호가창 수급 동향]</b></span>", unsafe_allow_html=True)
    c4, c5, c6, c7 = st.columns(4)
    with c4:
        user_avg_price = st.number_input("💡 보유 평단가", min_value=0.0, value=saved_avg, step=100.0, key=f"avg_{symbol}")
    with c5:
        user_last_1st_price = st.number_input("📉 직전 1차 매수가", min_value=0.0, value=saved_1st, step=100.0, key=f"1st_{symbol}")
    with c6:
        manual_ask = st.number_input("🔴 총매도잔량", min_value=0.0, value=saved_ask, step=1.0, format="%.2f", key=f"ask_{symbol}")
    with c7:
        manual_bid = st.number_input("🔵 총매수잔량", min_value=0.0, value=saved_bid, step=1.0, format="%.2f", key=f"bid_{symbol}")

st.session_state.price_memory[symbol] = {
    'open': manual_open,
    'prev': manual_prev_price_str,
    'pre': manual_pre_price_str,
    'avg': user_avg_price,
    '1st': user_last_1st_price,
    'ask': manual_ask,
    'bid': manual_bid
}

st.markdown("<hr style='margin: 15px 0 20px 0; border: 1px solid #CFD8DC;'>", unsafe_allow_html=True)

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    if st.button("🔄 정밀 분석 가동"):
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
        now_local = datetime.now(kst_tz) if is_kr else datetime.now(ny_tz)

        df = pd.DataFrame()
        auto_p, v_curr = 0.0, 0.0
        us_prev_p = None
        start_dt_str = start_date.strftime("%Y-%m-%d") 

        real_kr_open, real_kr_high, real_kr_low = 0.0, 0.0, 0.0

        if is_kr:
            currency, fmt_p = "원", ",.0f"
            clean_symbol = symbol.zfill(6)
            try:
                df = fdr.DataReader(clean_symbol, start=start_dt_str)
            except Exception:
                pass

            if df.empty:
                try:
                    df = yf.Ticker(f"{clean_symbol}.KS").history(start=start_dt_str)
                    if df.empty:
                        df = yf.Ticker(f"{clean_symbol}.KQ").history(start=start_dt_str)
                except Exception:
                    pass

            kr_fetched = False
            _code = clean_symbol

            def _to_price(value):
                if value is None:
                    return 0.0
                text_value = str(value).strip().replace(",", "").replace("원", "")
                if text_value in ("", "-", "--", "None", "null"):
                    return 0.0
                try:
                    number = float(text_value)
                    return number if pd.notna(number) and number > 0 else 0.0
                except (TypeError, ValueError):
                    return 0.0

            _naver_quote_values = {
                "auto_p": auto_p, "v_curr": v_curr,
                "open": real_kr_open, "high": real_kr_high, "low": real_kr_low,
                "prev_p": 0.0
            }

            def _apply_naver_quote(quote):
                _krx_close = _to_price(quote.get("closePrice", quote.get("nv")))
                _krx_open = _to_price(quote.get("openPrice", quote.get("ov")))
                _krx_high = _to_price(quote.get("highPrice", quote.get("hv")))
                _krx_low = _to_price(quote.get("lowPrice", quote.get("lv")))
                _volume = _to_price(quote.get("accumulatedTradingVolume", quote.get("aq")))

                # 🎯 [핵심 교정] 마이너스(-) 부호 때문에 등락폭이 0으로 증발하던 버그 완벽 제거!
                _prev_close = _to_price(quote.get("previousClosePrice", quote.get("basePrice", quote.get("sv"))))
                if _prev_close <= 0 and _krx_close > 0:
                    _raw_cmp = str(quote.get("compareToPreviousClosePrice", quote.get("cv", ""))).replace(",", "").replace("원", "").strip()
                    _risefall = quote.get("compareToPreviousPrice", {})
                    if not isinstance(_risefall, dict):
                        _risefall = {}
                    _rf_code = str(_risefall.get("code", quote.get("rf", ""))).strip()
                    _rf_name = str(_risefall.get("name", "")).upper()

                    try:
                        _cmp_signed = float(_raw_cmp) if _raw_cmp not in ("", "-", "None", "null") else 0.0
                    except ValueError:
                        _cmp_signed = 0.0

                    _cmp_abs = abs(_cmp_signed)
                    if _cmp_abs > 0:
                        if _cmp_signed < 0 or _rf_code in ["4", "5"] or "DOWN" in _rf_name or "FALL" in _rf_name or "하락" in _rf_name or "하한" in _rf_name:
                            _prev_close = _krx_close + _cmp_abs
                        elif _rf_code in ["1", "2"] or "UP" in _rf_name or "RISE" in _rf_name or "상승" in _rf_name or "상한" in _rf_name or _cmp_signed > 0:
                            _prev_close = _krx_close - _cmp_abs
                    elif _rf_code == "3" or "FLAT" in _rf_name or "보합" in _rf_name:
                        _prev_close = _krx_close

                _price = _krx_close
                _open = _krx_open
                _high = _krx_high
                _low = _krx_low

                # 🔥 아침 8시 프리마켓 시가 & 15시 30분 이후 애프터마켓 현재가 정밀 추적!
                _over_info = quote.get("overMarketPriceInfo")
                if isinstance(_over_info, dict):
                    _over_status = str(_over_info.get("overMarketStatus", "")).upper()
                    _over_p = _to_price(_over_info.get("overPrice", _over_info.get("closePrice")))
                    _over_open = _to_price(_over_info.get("openPrice"))
                    _over_high = _to_price(_over_info.get("highPrice"))
                    _over_low = _to_price(_over_info.get("lowPrice"))
                    _over_vol = _to_price(_over_info.get("accumulatedTradingVolume"))

                    if _prev_close <= 0 and _over_p > 0:
                        _over_cmp_raw = str(_over_info.get("compareToPreviousClosePrice", "")).replace(",", "").strip()
                        _over_rf = _over_info.get("compareToPreviousPrice", {})
                        _over_rf_code = str(_over_rf.get("code", "")).strip() if isinstance(_over_rf, dict) else ""
                        try:
                            _over_cmp_val = abs(float(_over_cmp_raw))
                        except ValueError:
                            _over_cmp_val = 0.0
                        if _over_cmp_val > 0:
                            if "-" in _over_cmp_raw or _over_rf_code in ["4", "5"]:
                                _prev_close = _over_p + _over_cmp_val
                            else:
                                _prev_close = _over_p - _over_cmp_val

                    if _over_open > 0:
                        _open = _over_open

                    is_after_kr_regular = (now_local.hour > 15) or (now_local.hour == 15 and now_local.minute >= 30)
                    if _over_p > 0 and (_krx_open <= 0 or is_after_kr_regular):
                        _price = _over_p

                    if _over_high > 0:
                        _high = max(_high, _over_high) if _high > 0 else _over_high
                    if _over_low > 0:
                        _low = min(_low, _over_low) if _low > 0 else _over_low
                    if _over_vol > 0:
                        _volume = _over_vol if _krx_open <= 0 else (_volume + _over_vol)

                if _price <= 0:
                    return False
                if _open <= 0:
                    _open = _price

                _high = max(_high, _open, _price) if _high > 0 else max(_open, _price)
                _low = min(_low, _open, _price) if _low > 0 else min(_open, _price)

                _naver_quote_values["auto_p"] = _price
                _naver_quote_values["open"] = _open
                _naver_quote_values["high"] = _high
                _naver_quote_values["low"] = _low
                if _prev_close > 0:
                    _naver_quote_values["prev_p"] = _prev_close
                if _volume > 0:
                    _naver_quote_values["v_curr"] = _volume
                return True

            try:
                api_url = f"https://polling.finance.naver.com/api/realtime/domestic/stock/{_code}"
                headers = {
                    "User-Agent": "Mozilla/5.0",
                    "Referer": "https://finance.naver.com/",
                    "Accept": "application/json, text/plain, */*",
                }
                res = requests.get(api_url, headers=headers, timeout=5)
                res.raise_for_status()
                payload = res.json()
                quotes = payload.get("datas", []) if isinstance(payload, dict) else []
                if quotes and isinstance(quotes[0], dict):
                    kr_fetched = _apply_naver_quote(quotes[0])
            except (requests.RequestException, ValueError, TypeError, KeyError):
                pass

            if not kr_fetched:
                try:
                    api_url = f"https://m.stock.naver.com/api/stock/{_code}/basic"
                    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.stock.naver.com/"}
                    res = requests.get(api_url, headers=headers, timeout=5)
                    res.raise_for_status()
                    data = res.json()
                    if isinstance(data, dict):
                        kr_fetched = _apply_naver_quote(data)
                except (requests.RequestException, ValueError, TypeError, KeyError):
                    pass

            if not kr_fetched:
                try:
                    api_url = f"https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{_code}"
                    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.naver.com/"}
                    res = requests.get(api_url, headers=headers, timeout=5)
                    res.raise_for_status()
                    payload = res.json()
                    quote = payload["result"]["areas"][0]["datas"][0]
                    kr_fetched = _apply_naver_quote(quote)
                except (requests.RequestException, ValueError, TypeError, KeyError, IndexError):
                    pass

            auto_p = _naver_quote_values["auto_p"]
            v_curr = _naver_quote_values["v_curr"]
            real_kr_open = _naver_quote_values["open"]
            real_kr_high = _naver_quote_values["high"]
            real_kr_low = _naver_quote_values["low"]

            if not kr_fetched and not df.empty:
                auto_p = _to_price(df["Close"].iloc[-1])
                v_curr = _to_price(df["Volume"].iloc[-1])

            if not df.empty and kr_fetched:
                _avg_v = float(df["Volume"].iloc[-6:-1].mean()) if len(df) >= 6 else float(df["Volume"].mean())
                if _avg_v > 0 and v_curr > _avg_v * 50:
                    v_curr = float(df["Volume"].iloc[-1])
                    
            if auto_p > 0:
                p = auto_p
        else:
            currency, fmt_p = "$", ",.2f"
            tk_upper = symbol.upper()
            ticker = yf.Ticker(tk_upper)

            try:
                df = ticker.history(start=start_dt_str)
            except Exception:
                df = ticker.history(period="1y")

            try:
                fast_inf = ticker.fast_info
                auto_p = getattr(fast_inf, "last_price", 0.0)
                v_curr = getattr(fast_inf, "last_volume", 0.0)
                us_prev_p = getattr(fast_inf, "previous_close", None)
            except Exception:
                auto_p, v_curr, us_prev_p = 0.0, 0.0, None

            if auto_p == 0.0 or pd.isna(auto_p):
                try:
                    inf_dict = ticker.info
                    auto_p = inf_dict.get("regularMarketPrice", inf_dict.get("currentPrice", 0.0))
                    if auto_p == 0.0 or pd.isna(auto_p):
                        auto_p = float(df["Close"].iloc[-1])
                except Exception:
                    if not df.empty:
                        auto_p = float(df["Close"].iloc[-1])

            if v_curr == 0.0 or pd.isna(v_curr):
                if not df.empty: v_curr = float(df["Volume"].iloc[-1])

            if not df.empty:
                _us_avg_v = float(df["Volume"].iloc[-6:-1].mean()) if len(df) >= 6 else float(df["Volume"].mean())
                if _us_avg_v > 0 and v_curr > _us_avg_v * 50:
                    v_curr = float(df["Volume"].iloc[-1])

        multiplier = 1000.0 if is_kr else 1.0

        is_ob_stage2_safe = True
        is_ob_stage3_safe = True

        if manual_ask > 0 and manual_bid > 0:
            calc_ratio = round(manual_ask / manual_bid, 2)
            display_ask = manual_ask * multiplier
            display_bid = manual_bid * multiplier
            ob_data = {"ask": display_ask, "bid": display_bid, "ratio": calc_ratio, "ok": True, "msg": "HTS 직접입력"}
        elif manual_ask > 0 or manual_bid > 0:
            ob_data = {"ask": manual_ask * multiplier, "bid": manual_bid * multiplier, "ratio": None, "ok": False, "msg": "HTS 매도·매수잔량을 모두 입력해야 분석 가능"}
        else:
            ob_data = {"ask": 0.0, "bid": 0.0, "ratio": None, "ok": False, "msg": "실시간 호가 API 미연결"}

        override_pre_p = 0.0
        auto_us_open = 0.0
        auto_us_high = 0.0
        auto_us_low = 0.0
        is_pre_market_mode = False

        if not is_kr:
            # 1순위: 수동 통제소에 직접 입력하신 프리장 시세가 있으면 최우선 적용
            if manual_pre_price_str:
                try:
                    override_pre_p = float(manual_pre_price_str.replace(",", "").replace("$", ""))
                    if override_pre_p > 0: is_pre_market_mode = True
                except ValueError:
                    pass

            # 2순위: 야후 1분봉(prepost=True)에서 미장 당일(프리장 포함) 실시간 현재가·시가·고가·저가 자동 추출!
            try:
                import yfinance as yf
                _tk = yf.Ticker(symbol)
                _yf_df = _tk.history(period="1d", interval="1m", prepost=True)
                if not _yf_df.empty:
                    # 뉴욕 현지 시간 정규장(09:30 ~ 16:00)일 때는 프리마켓 모드를 자동 해제하여 거래량 로직을 복구!
                    is_us_regular = (now_local.hour > 9 or (now_local.hour == 9 and now_local.minute >= 30)) and (now_local.hour < 16) and (now_local.weekday() < 5)
                    if not is_pre_market_mode and not is_us_regular:
                        _auto_pre_p = float(_yf_df["Close"].iloc[-1])
                        if _auto_pre_p > 0:
                            override_pre_p = _auto_pre_p
                            is_pre_market_mode = True
                    _reg_open = float(_tk.fast_info.get("open", 0.0) or 0.0)
                    auto_us_open = _reg_open if _reg_open > 0 else float(_yf_df["Open"].iloc[0])
                    auto_us_high = float(_yf_df["High"].max())
                    auto_us_low = float(_yf_df["Low"].min())
            except Exception:
                pass

        p = override_pre_p if is_pre_market_mode else auto_p

        if df.empty:
            st.warning(f"⚠️ [{symbol}] 종목의 데이터를 불러오지 못했구먼. 종목번호를 다시 확인해 주시게.")
        else:
            df = df.ffill().dropna()
            if len(df) < 20:
                _close_val = float(df["Close"].iloc[-1]) if (not df.empty and "Close" in df.columns and pd.notna(df["Close"].iloc[-1])) else None
                _live_val = None
                try:
                    _tk = yf.Ticker(symbol)
                    _fi = getattr(_tk, "fast_info", None)
                    if _fi is not None:
                        _live_val = _fi.get("lastPrice") or _fi.get("regularMarketPrice")
                    if _live_val is None:
                        _info = _tk.info or {}
                        _live_val = _info.get("currentPrice") or _info.get("regularMarketPrice")
                    if _live_val is not None:
                        _live_val = float(_live_val)
                except Exception:
                    _live_val = None

                _price_parts = []
                if _live_val is not None and _live_val > 0:
                    _live_str = f"{_live_val:,.0f}원" if is_kr else f"${_live_val:,.2f}"
                    _price_parts.append(f"실시간가: <span style='color:#D32F2F;'>{_live_str}</span>")
                if _close_val is not None:
                    _close_str = f"{_close_val:,.0f}원" if is_kr else f"${_close_val:,.2f}"
                    _price_parts.append(f"최근종가: <span style='color:#0D47A1;'>{_close_str}</span>")

                _cur_p_txt = (" | " + " / ".join(_price_parts)) if _price_parts else ""
                st.markdown(f"<div style='background-color:#FFF8E1; border:2px solid #FFB300; border-left:8px solid #FF6F00; padding:16px 20px; border-radius:8px; color:#3E2723; font-size:17px; font-weight:700; line-height:1.5;'>🚨 [{symbol}] 신규 상장 / 데이터 부족 분석 불가 — 현재 누적 거래일이 <span style='color:#D32F2F;'>{len(df)}일</span>뿐이라 20일선 및 보조지표 산출이 불가능하오! 최소 20거래일 이상 데이터가 쌓인 뒤 분석하시게.{_cur_p_txt}</div>", unsafe_allow_html=True)
                st.stop()
            if is_kr:
                df.index = pd.to_datetime(df.index).date
                today_date = now_local.date()
            else:
                # 🇺🇸 미장은 utc=True를 빼서 뉴욕 현지 거래일 날짜를 그대로 보존하고, 뉴욕 기준 오늘 날짜를 사용!
                df.index = pd.to_datetime(df.index).tz_localize(None).date if getattr(pd.to_datetime(df.index), 'tz', None) is not None else pd.to_datetime(df.index).date
                today_date = pd.Timestamp.now(tz="America/New_York").date()
            override_prev_p = 0.0
            if manual_prev_price_str:
                try:
                    override_prev_p = float(manual_prev_price_str.replace(",", "").replace("원", "").replace("$", ""))
                except ValueError:
                    pass

            # ==================================================================
            # 🚨 [결정적 버그 수정] 주말(토·일) 또는 휴장일에 가짜 날짜 행이 생성되어
            # 금요일의 진짜 고가(윗꼬리)와 저가(아래꼬리)가 증발하던 현상을 원천 차단!
            # ==================================================================
            df_sorted = df.sort_index()
            last_df_date = df_sorted.index[-1]
            is_active_weekday = (now_local.weekday() < 5) and (now_local.hour >= 8)

            if today_date in df_sorted.index:
                target_candle_date = today_date
                df_past = df_sorted.drop(today_date, errors="ignore")
            elif not is_active_weekday and not is_pre_market_mode:
                # 주말이거나 장 시작 전이면 마지막 거래일(금요일 등) 캔들을 오늘 기준 캔들로 고정!
                target_candle_date = last_df_date
                df_past = df_sorted.iloc[:-1]
            else:
                target_candle_date = today_date
                df_past = df_sorted

            naver_prev_p = _naver_quote_values.get("prev_p", 0.0) if is_kr else 0.0
            # 🎯 미장 전일종가는 일봉 장부(df_past)의 직전 정규장 마감 종가를 1순위로 사용하여 오차 원천 차단!
            calc_prev_p = naver_prev_p if naver_prev_p > 0 else (float(df_past["Close"].iloc[-1]) if len(df_past) >= 1 else (float(us_prev_p) if (not is_kr and us_prev_p and us_prev_p > 0) else p))
            prev_p = override_prev_p if override_prev_p > 0 else calc_prev_p

            existing_open = float(df.loc[target_candle_date, "Open"]) if (target_candle_date in df.index and pd.notna(df.loc[target_candle_date, "Open"])) else 0.0
            us_auto_open_val = existing_open if existing_open > 0 else auto_us_open
            
            # 프리마켓 중 수동 시가 미입력 시, 전일 종가(prev_p)를 시가로 원천 고정하여 양의 음봉 왜곡 차단!
            if not is_kr and is_pre_market_mode and manual_open <= 0:
                actual_open = prev_p
            else:
                actual_open = manual_open if manual_open > 0 else (real_kr_open if (is_kr and real_kr_open > 0) else (us_auto_open_val if (not is_kr and us_auto_open_val > 0) else (existing_open if existing_open > 0 else prev_p)))
            
            rt_high = real_kr_high if is_kr else auto_us_high
            rt_low = real_kr_low if is_kr else auto_us_low

            if target_candle_date in df.index:
                df.loc[target_candle_date, "Close"] = p
                df.loc[target_candle_date, "Volume"] = v_curr if v_curr > 0 else df.loc[target_candle_date, "Volume"]
                df.loc[target_candle_date, "Open"] = actual_open
                
                c_high = df.loc[target_candle_date, "High"]
                c_low = df.loc[target_candle_date, "Low"]
                df.loc[target_candle_date, "High"] = max(c_high if pd.notna(c_high) else p, actual_open, p, rt_high)
                
                safe_lows = [val for val in [c_low, rt_low] if pd.notna(val) and val > 0]
                df.loc[target_candle_date, "Low"] = min(min(safe_lows), actual_open, p) if safe_lows else min(actual_open, p)
            else:
                df_high = max(rt_high, actual_open, p)
                safe_lows = [val for val in [rt_low] if pd.notna(val) and val > 0]
                df_low = min(min(safe_lows), actual_open, p) if safe_lows else min(actual_open, p)
                
                new_row = pd.DataFrame({"Open": [actual_open], "High": [df_high], "Low": [df_low], "Close": [p], "Volume": [v_curr]}, index=[target_candle_date])
                df = pd.concat([df, new_row])

            v_avg5 = float(df["Volume"].iloc[-6:-1].mean()) if len(df) >= 6 else float(df["Volume"].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0

            p_diff = p - prev_p
            p_chg = (p_diff / prev_p) * 100 if prev_p > 0 else 0

            if is_kr:
                m_start = now_local.replace(hour=8, minute=0, second=0, microsecond=0)
                m_end = now_local.replace(hour=20, minute=0, second=0, microsecond=0)
                total_minutes = 720 
            else:
                m_start = now_local.replace(hour=9, minute=30, second=0, microsecond=0)
                m_end = now_local.replace(hour=16, minute=0, second=0, microsecond=0)
                total_minutes = 390

            if m_start <= now_local <= m_end and now_local.weekday() < 5:
                elapsed = max(10, (now_local - m_start).seconds / 60)
                vol_strength = min(1000, v_ratio / (elapsed / total_minutes))
            else:
                vol_strength = v_ratio

            # ==================================================================
            # ★ [수동 시가 및 당일 고가·저가 확정]
            # ==================================================================
            today_open = float(str(df["Open"].iloc[-1]).replace(',', ''))
            today_high = float(str(df["High"].iloc[-1]).replace(',', ''))
            today_low = float(str(df["Low"].iloc[-1]).replace(',', ''))
            p = float(str(df["Close"].iloc[-1]).replace(',', ''))
            
            if manual_open > 0:
                debug_msg = f"🟢 [수동 룰 작동] 명장님의 하명({manual_open:{fmt_p}}{currency}) 데이터에 완벽 각인!"
            else:
                debug_msg = f"🟡 [자동 시가 모드] 실시간/장부 시가 ({today_open:{fmt_p}}{currency}) 적용 중"

            _final_str = f"{today_open:{fmt_p}}"
            st.markdown(f"🚨 **[시가 수동 통제]** {debug_msg} | 📌 **확정 시가:** {_final_str}{currency} (당일 고가: {today_high:{fmt_p}}{currency} / 저가: {today_low:{fmt_p}}{currency})")

            is_down_trend_v = (p < prev_p) and (p_chg < 0)
            day_candle_range = max(0.01, today_high - today_low)
            is_api_delayed = (p > today_high * 1.005) or (p < today_low * 0.995) or (today_high == today_low)

            upper_tail_len = max(0.0, today_high - max(today_open, p))
            lower_tail_len = max(0.0, min(today_open, p) - today_low)
            body_len = abs(p - today_open)
            upper_tail_pct_of_range = (upper_tail_len / day_candle_range) * 100.0 if day_candle_range > 0 else 0.0

            if is_pre_market_mode and manual_open <= 0:
                cur_open_price = prev_p
            else:
                cur_open_price = today_open
            
            if p > cur_open_price:
                candle_color_txt = "빨간색 양봉"
                is_candle_bullish = True
                is_candle_bearish = False
            elif p < cur_open_price:
                candle_color_txt = "파란색 음봉"
                is_candle_bullish = False
                is_candle_bearish = True
            else:
                candle_color_txt = "빨간색 양봉" if p_chg >= 0 else "파란색 음봉"
                is_candle_bullish = (p_chg >= 0)
                is_candle_bearish = (p_chg < 0)

            if day_candle_range > 0:
                is_doji_candle = (body_len <= day_candle_range * 0.05) or (body_len <= cur_open_price * 0.002)
            else:
                is_doji_candle = (body_len == 0)
                
            strict_doji_check = is_doji_candle
            
            if strict_doji_check:
                is_candle_bullish = False
                is_candle_bearish = False
                candle_color_txt = "십자형 도지(Doji)"
            
            if is_pre_market_mode or is_api_delayed:
                is_long_upper_tail = False
                has_upper_tail_resist = False
                is_defended = is_candle_bullish      
                is_candle_unknown = True
                is_strong_bull_body = False
            else:
                if strict_doji_check:
                    is_long_upper_tail = False
                    has_upper_tail_resist = False
                else:
                    # 1) 치명적 장대 윗꼬리: 윗꼬리가 몸통보다 길거나 전체 진폭의 35% 이상이면서 몸통의 70% 이상일 때
                    is_long_upper_tail = (upper_tail_len > lower_tail_len) and ((upper_tail_len > body_len) or (upper_tail_len >= day_candle_range * 0.35 and upper_tail_len >= body_len * 0.7))
                    # 2) 일반 윗꼬리 저항: 양봉 몸통이 더 길더라도 고점 대비 전체 진폭의 15% 이상(또는 몸통의 25% 이상, 또는 0.8% 이상 하락) 윗꼬리가 달렸을 때!
                    has_upper_tail_resist = (upper_tail_len >= day_candle_range * 0.15) or (body_len > 0 and upper_tail_len >= body_len * 0.25) or (today_high > 0 and ((today_high - max(today_open, p)) / today_high) >= 0.008)
                
                is_tail_defended = (lower_tail_len > upper_tail_len) and (lower_tail_len >= day_candle_range * 0.25) and (not (is_candle_bearish and p_chg < 0 and lower_tail_len < body_len))
                is_strong_bull_body = is_candle_bullish and ((p_chg >= 1.0) or (body_len >= upper_tail_len))
                
                is_defended = ((p_chg > 0 or is_candle_bullish) and not is_long_upper_tail) or is_tail_defended or is_strong_bull_body
                is_candle_unknown = False

            is_pure_bullish_candle = p >= today_open
            is_bottom_lower_tail = ((lower_tail_len >= day_candle_range * 0.35) or (lower_tail_len >= body_len * 1.0)) and (p_chg >= -1.5)
            is_extreme_lower_tail = (day_candle_range > 0) and (lower_tail_len >= day_candle_range * 0.65) and ((day_candle_range - body_len - lower_tail_len) <= day_candle_range * 0.10) and (lower_tail_len >= body_len * 2.5) and (p_chg >= -1.5)
            is_valid_bottom_candle = (is_pure_bullish_candle or is_bottom_lower_tail) and (not is_down_trend_v)
            is_massive_dump = (vol_strength >= 150 and p_chg <= -2.5) or (vol_strength >= 80 and p_chg <= -4.5)

            # ==================================================================
            # ★ [지표 수술 파트] RSI (14,9) & Williams %R (14,6) 시그널 선 연산 
            # ==================================================================
            delta = df["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_sig_series = rsi_series.rolling(9).mean()
            
            rsi_val, rsi_prev = rsi_series.iloc[-1], rsi_series.iloc[-2]
            rsi_sig_val, rsi_sig_prev = rsi_sig_series.iloc[-1], rsi_sig_series.iloc[-2]

            h14, l14 = df["High"].rolling(14).max(), df["Low"].rolling(14).min()
            will_series = (h14 - df["Close"]) / (h14 - l14 + 1e-10) * -100
            will_sig_series = will_series.rolling(6).mean()
            
            will_val, will_prev = will_series.iloc[-1], will_series.iloc[-2]
            will_sig_val, will_sig_prev = will_sig_series.iloc[-1], will_sig_series.iloc[-2]

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

            bandwidth = (((up_b - low_b) / mid_line) * 100 if mid_line > 0 else 0)
            is_band_expanding = (up_b > prev_up_b) and (bandwidth >= prev_bandwidth)

            # ==================================================================
            # 🎯 [볼린저 위치(%B) × 캔들(양봉/음봉/윗꼬리) 결합 정밀 판독기]
            # ==================================================================
            bb_range = up_b - low_b
            bb_pct_b = ((p - low_b) / bb_range) * 100.0 if bb_range > 0 else 50.0
            if strict_doji_check:
                _c_short = "도지"
            elif is_candle_bullish:
                _c_short = "윗꼬리양봉" if has_upper_tail_resist else "양봉"
            else:
                _c_short = "극한아래꼬리음봉" if is_extreme_lower_tail else ("윗꼬리음봉" if has_upper_tail_resist else "음봉")

            _tail_note = f" (단, 고점 {today_high:{fmt_p}}{currency} 대비 윗꼬리 매물 저항 동반)" if has_upper_tail_resist else ""

            if p < low_b:
                if is_candle_bullish or is_bottom_lower_tail:
                    bb_pos_tag = f"🌱 지하실 이탈 후 {_c_short} 반발 ({bb_pct_b:.1f}%)"
                    bb_pos_short = f"지하실 {_c_short}"
                    bb_pos_col = "#E65100"
                    bb_pos_desc = f"볼린저 바닥선({low_b:{fmt_p}}{currency}) 아래({bb_pct_b:.1f}%)로 이탈했으나, <b>{candle_color_txt} 방어세</b>가 유입되며 바닥선 재진입을 노리고 있소{_tail_note}."
                else:
                    bb_pos_tag = f"🚨 하단선 지하실 음봉 추락 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "지하실 음봉추락"
                    bb_pos_col = "#D32F2F"
                    bb_pos_desc = f"현재가가 볼린저 바닥선({low_b:{fmt_p}}{currency})마저 깨고 <b>{candle_color_txt}으로 언더슈팅 추락({bb_pct_b:.1f}%)</b> 중인 위험 구역이오!"
            elif bb_pct_b <= 15.0 or p <= (low_b * 1.02):
                if is_candle_bullish or is_bottom_lower_tail:
                    if p_chg < 0 and bb_pct_b <= 15.0:
                        bb_pos_tag = f"📉 하단 바닥선 {_c_short} 반발 타진 ({bb_pct_b:.1f}%)"
                        bb_pos_short = f"하단 {_c_short}반발타진"
                        bb_pos_col = "#F57C00"
                        bb_pos_desc = f"볼린저 하단 바닥선({low_b:{fmt_p}}{currency}) 부근({bb_pct_b:.1f}% 지점)에서 <b>{candle_color_txt}</b>으로 저가 반발을 시도 중이나, 전일 대비 하락({p_chg:.2f}%) 추세가 이어지고 있으니 경계하며 확인하시게."
                    else:
                        bb_pos_tag = f"🎯 하단 바닥선 {_c_short} 지지 ({bb_pct_b:.1f}%)"
                        bb_pos_short = f"하단 {_c_short}지지"
                        bb_pos_col = "#2E7D32"
                        bb_pos_desc = f"볼린저 하단 바닥선({low_b:{fmt_p}}{currency}) 코앞({bb_pct_b:.1f}% 지점)에서 <b>{candle_color_txt}</b>으로 하락을 멈춰 세우며 진바닥 반등 시동을 걸고 있소!"
                elif strict_doji_check:
                    bb_pos_tag = f"⚖️ 하단 바닥선 도지 방어 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "하단 도지방어"
                    bb_pos_col = "#F57C00"
                    bb_pos_desc = f"볼린저 하단 바닥선({low_b:{fmt_p}}{currency}) 부근({bb_pct_b:.1f}% 지점)에서 십자 도지를 만들며 투매를 멈춰 세웠소. 내일 양봉 전환을 주시하시게."
                else:
                    bb_pos_tag = f"⚠️ 하단 바닥선 음봉 압박 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "하단 음봉압박"
                    bb_pos_col = "#D32F2F"
                    bb_pos_desc = f"볼린저 하단 바닥선({low_b:{fmt_p}}{currency}) 코앞({bb_pct_b:.1f}% 지점)에 도달했으나, <b>{candle_color_txt} 매도 압력에 밀려 바닥 붕괴를 위협</b>받고 있으니 양봉 확인 전까지 입질을 금하오!"
            elif bb_pct_b < 45.0:
                if is_candle_bullish:
                    _ma5_chk = float(df["MA5"].iloc[-1]) if (len(df) >= 5 and pd.notna(df["MA5"].iloc[-1])) else p
                    if p_chg < 0 and p < _ma5_chk:
                        bb_pos_tag = f"📉 갭하락 양봉 방어 시도 ({bb_pct_b:.1f}%)"
                        bb_pos_short = f"하단부 {_c_short} 방어시도"
                        bb_pos_col = "#F57C00"
                        bb_pos_desc = f"볼린저 하단부({bb_pct_b:.1f}% 지점)에서 <b>{candle_color_txt}</b>으로 저가 방어를 시도 중이나, 전일 대비 하락({p_chg:.2f}%) 및 대세 역배열 압력이 남아 있어 섣부른 진입은 보류하시게."
                    elif p < _ma5_chk:
                        bb_pos_tag = f"🌱 5일선 아래 {_c_short} 반등 시도 ({bb_pct_b:.1f}%)"
                        bb_pos_short = f"하단부 {_c_short}"
                        bb_pos_col = "#E65100"
                        bb_pos_desc = f"볼린저 하단권({bb_pct_b:.1f}% 지점)에서 <b>{candle_color_txt}</b>으로 반등을 시도 중이나, 아직 5일선({_ma5_chk:{fmt_p}}{currency}) 저항이 남아 있으니 안착 여부를 확인하시게."
                    else:
                        bb_pos_tag = f"🌱 중심선 아래 {_c_short} 반격 ({bb_pct_b:.1f}%)"
                        bb_pos_short = f"하단부 {_c_short}"
                        bb_pos_col = "#1565C0"
                        bb_pos_desc = f"바닥을 찍고 <b>{candle_color_txt}</b>을 세우며 20일 중심선({mid_line:{fmt_p}}{currency})을 향해 치고 올라가는 반등 구간({bb_pct_b:.1f}% 지점)이오."
                elif strict_doji_check:
                    bb_pos_tag = f"⚖️ 중심선 아래 도지 탐색 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "하단부 도지탐색"
                    bb_pos_col = "#F57C00"
                    bb_pos_desc = f"20일 중심선({mid_line:{fmt_p}}{currency}) 아래({bb_pct_b:.1f}% 지점)에서 십자 도지로 숨을 고르며 반등 여부를 탐색 중이오."
                else:
                    bb_pos_tag = f"📉 중심선 아래 음봉 조정 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "하단부 음봉밀림"
                    bb_pos_col = "#D32F2F"
                    bb_pos_desc = f"20일 중심선({mid_line:{fmt_p}}{currency}) 아래({bb_pct_b:.1f}% 지점)에 갇힌 채 <b>{candle_color_txt}으로 밀리며 하단 바닥선을 향해 뒷걸음질</b>치는 약세 구역이오."
            elif bb_pct_b <= 55.0:
                state_word = "지지 사수" if p >= mid_line else "돌파 시도"
                if is_candle_bullish:
                    bb_pos_tag = f"🔵 20일 중심선 {_c_short} {state_word} ({bb_pct_b:.1f}%)"
                    bb_pos_short = f"중심선 {_c_short}"
                    bb_pos_col = "#2E7D32"
                    bb_pos_desc = f"볼린저 정중앙인 20일 중심선({mid_line:{fmt_p}}{currency}) 허리({bb_pct_b:.1f}% 지점)에서 <b>{candle_color_txt}을 띄우며 {state_word}에 나서고 있는</b> 핵심 맥점이오{_tail_note}!"
                elif strict_doji_check:
                    bb_pos_tag = f"⚖️ 20일 중심선 도지 공방 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "중심선 도지공방"
                    bb_pos_col = "#F57C00"
                    bb_pos_desc = f"20일 중심선({mid_line:{fmt_p}}{currency}) 부근({bb_pct_b:.1f}% 지점)에서 매수·매도가 팽팽히 맞서며 십자 공방을 벌이는 허리 구역이오."
                else:
                    bb_pos_tag = f"⚠️ 20일 중심선 음봉 밀림 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "중심선 음봉저항"
                    bb_pos_col = "#D32F2F"
                    bb_pos_desc = f"20일 중심선({mid_line:{fmt_p}}{currency}) 부근({bb_pct_b:.1f}% 지점)에서 <b>{candle_color_txt} 매물을 맞고 밀려나며 중심선 안착에 애를 먹는</b> 저항 구역이오!"
            elif bb_pct_b < 85.0:
                if is_candle_bullish:
                    bb_pos_tag = f"📈 중심선 위 {_c_short} 순항 ({bb_pct_b:.1f}%)"
                    bb_pos_short = f"상단부 {_c_short}"
                    bb_pos_col = "#2E7D32"
                    bb_pos_desc = f"20일 중심선({mid_line:{fmt_p}}{currency})을 밟고 올라서서 <b>{candle_color_txt} 기세를 유지하며</b> 상단 목표선({up_b:{fmt_p}}{currency}) 쪽으로 나아가는 구역({bb_pct_b:.1f}% 지점)이오{_tail_note}."
                elif strict_doji_check:
                    bb_pos_tag = f"⚖️ 중심선 위 도지 숨고르기 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "상단부 도지대기"
                    bb_pos_col = "#F57C00"
                    bb_pos_desc = f"20일 중심선 위({bb_pct_b:.1f}% 지점) 상방 구역에서 십자 도지를 띄우며 단기 숨고르기를 진행 중이오."
                else:
                    bb_pos_tag = f"🟡 중심선 위 음봉 숨고르기 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "상단부 음봉조정"
                    bb_pos_col = "#F57C00"
                    bb_pos_desc = f"20일 중심선({mid_line:{fmt_p}}{currency}) 위 상방 구역({bb_pct_b:.1f}% 지점)에 있으나, 당일 <b>{candle_color_txt} 차익 매물로 눌림 조정을 받는 중</b>이니 5일선·20일선 지지를 확인하시게."
            elif bb_pct_b <= 100.0:
                if is_candle_bullish and not is_long_upper_tail:
                    bb_pos_tag = f"🔥 상단 수확선 {_c_short} 도달 ({bb_pct_b:.1f}%)"
                    bb_pos_short = f"상단선 {_c_short}"
                    bb_pos_col = "#E65100"
                    bb_pos_desc = f"볼린저 상단 목표선({up_b:{fmt_p}}{currency}) 턱밑({bb_pct_b:.1f}% 지점)까지 <b>{candle_color_txt}으로 치솟은</b> 수확/돌파 임박 구역이오{_tail_note}!"
                else:
                    bb_pos_tag = f"🔴 상단 수확선 음봉·윗꼬리 저항 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "상단선 음봉저항"
                    bb_pos_col = "#D32F2F"
                    bb_pos_desc = f"볼린저 상단 목표선({up_b:{fmt_p}}{currency}) 부근({bb_pct_b:.1f}% 지점)에서 <b>{candle_color_txt}(또는 윗꼬리) 차익 매물 폭탄을 맞고 꺾이는</b> 위험 고점이오!"
            else:
                if is_candle_bullish and not is_long_upper_tail:
                    bb_pos_tag = f"🟣 상단선 돌파 {_c_short} 폭발 ({bb_pct_b:.1f}%)"
                    bb_pos_short = f"상단돌파 {_c_short}"
                    bb_pos_col = "#6A1B9A"
                    bb_pos_desc = f"볼린저 상단선({up_b:{fmt_p}}{currency})을 <b>강력한 {candle_color_txt}으로 뚫고 밴드 밖({bb_pct_b:.1f}% 지점)으로 날아오르는</b> 대시세 밴드 라이딩 구역이오{_tail_note}!"
                else:
                    bb_pos_tag = f"🚨 상단선 밖 음봉 차익투매 ({bb_pct_b:.1f}%)"
                    bb_pos_short = "상단돌파 음봉꺾임"
                    bb_pos_col = "#D32F2F"
                    bb_pos_desc = f"볼린저 상단선({up_b:{fmt_p}}{currency}) 밖({bb_pct_b:.1f}% 지점) 과열권에서 <b>{candle_color_txt} 매물이 쏟아지며 밴드 안으로 밀려 들어오는</b> 상투 경보 구역이오!"

            ma5_val = float(df["MA5"].iloc[-1]) if (len(df) >= 5 and pd.notna(df["MA5"].iloc[-1])) else p
            ma60_val = float(df["MA60"].iloc[-1]) if (len(df) >= 60 and pd.notna(df["MA60"].iloc[-1])) else mid_line
            ma120_val = float(df["MA120"].iloc[-1]) if (len(df) >= 120 and pd.notna(df["MA120"].iloc[-1])) else ma60_val
            # --- [신규] 이평선 기울기(↗/→/↘) 및 20일선 연속 미돌파 일수 계산 ---
            def get_ma_slope_arrow(series, lookback=5, flat_pct=0.003):
                if len(series) <= lookback or pd.isna(series.iloc[-1]) or pd.isna(series.iloc[-1 - lookback]):
                    return "→"
                prev_val = series.iloc[-1 - lookback]
                curr_val = series.iloc[-1]
                if prev_val == 0:
                    return "→"
                diff_pct = (curr_val - prev_val) / prev_val
                if diff_pct >= flat_pct:
                    return "↗"
                elif diff_pct <= -flat_pct:
                    return "↘"
                return "→"
    
            _ma20_s = df["Close"].rolling(20).mean()
            arrow_5   = get_ma_slope_arrow(df["MA5"], lookback=3, flat_pct=0.005)
            arrow_20  = get_ma_slope_arrow(_ma20_s, lookback=5, flat_pct=0.003)
            arrow_60  = get_ma_slope_arrow(df["MA60"], lookback=5, flat_pct=0.002)
            arrow_120 = get_ma_slope_arrow(df["MA120"], lookback=5, flat_pct=0.002)
    
            # 어제까지 20일선 연속 미돌파 일수 역산
            ma20_fail_days = 0
            for idx in range(len(df) - 2, -1, -1):
                c_val = df["Close"].iloc[idx]
                m_val = _ma20_s.iloc[idx]
                if pd.isna(m_val):
                    break
                if c_val < m_val * 1.01:
                    ma20_fail_days += 1
                else:
                    break
    
            ma20_fail_days_now = (ma20_fail_days + 1) if (p < mid_line) else 0
    
            # [판정 플래그] 지속 저항 vs 장기 저항 첫 돌파
            is_ma20_chronic_resist = (ma20_fail_days_now >= 10) and (arrow_20 == "↘")
            _is_bull_today = (p >= float(df["Open"].iloc[-1])) if "Open" in df.columns else True
            _vol_5avg = df["Volume"].iloc[-6:-1].mean() if len(df) >= 6 else 0
            _is_vol_ok = (df["Volume"].iloc[-1] >= _vol_5avg) if _vol_5avg > 0 else True
            is_ma20_breakout_real = (ma20_fail_days >= 10) and (p >= mid_line) and _is_bull_today and _is_vol_ok
            is_ma20_breakout_try  = (ma20_fail_days >= 10) and (p >= mid_line) and (not is_ma20_breakout_real)

            # [보완 1] 돌파 시도 사유 구체화 (누적 거래량 % 명시)
            _try_reasons = []
            if not _is_vol_ok:
                _try_reasons.append(f"실제 누적 거래량 미달(현재 {v_ratio:.1f}%)")
            if not _is_bull_today:
                _try_reasons.append("음봉(시가 아래)")
            _try_reason_txt = " · ".join(_try_reasons) if _try_reasons else "거래량·양봉 안착 미달"

            # [보완 4] 장중 실시간 vs 종가 확정 구분
            if is_kr:
                is_market_closed = (now_local.weekday() >= 5) or (now_local.hour > 15) or (now_local.hour == 15 and now_local.minute >= 30) or (now_local.hour < 9)
            else:
                is_market_closed = (not is_pre_market_mode) and ((now_local.weekday() >= 5) or (now_local.hour >= 16) or (now_local.hour < 9) or (now_local.hour == 9 and now_local.minute < 30))
            session_badge = "🔒 [종가 확정]" if is_market_closed else "⏱️ [장중 실시간]"
            is_ma5_safe = p >= ma5_val
            bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
            bias_ma20 = ((p - mid_line) / mid_line) * 100 if mid_line > 0 else 0
            is_over_extended_5 = bias_ma5 >= 8.0

            is_trend_lower_tail = (((lower_tail_len >= day_candle_range * 0.35) or (lower_tail_len >= body_len * 1.0)) and (p >= ma5_val * 0.99) and (p_chg >= -2.5))
            is_valid_buy_candle = is_pure_bullish_candle or is_trend_lower_tail
            is_bearish_candle = (p < today_open) and (not is_trend_lower_tail)

            lookback_days = min(250, len(df) - 1) if len(df) > 1 else 1
            high_250 = float(df["High"].iloc[-lookback_days:-1].max()) if lookback_days > 1 else today_high
            is_new_high_breakout = (p > high_250) and (p_chg >= 2.0) and (bias_ma5 >= 3.0)
            
            recent_high_10 = float(df["High"].iloc[-min(10, len(df)):-1].max()) if len(df) > 1 else today_high
            has_recent_new_high = (recent_high_10 >= high_250) and (high_250 > 0)
            is_new_high_pullback = has_recent_new_high and is_ma5_safe and (-1.0 <= bias_ma5 <= 2.5) and not is_candle_bearish and not (ma5_val < mid_line and mid_line < ma60_val)

            low_b_val = low_b 

            bb_bot_check = (p <= (low_b_val * 1.02)) or (bb_pct_b <= 15.0)
            rsi_cold_check = rsi_val <= 38
            will_cold_check = will_val <= -75
            temp_bottom_score = int(bb_bot_check) + int(rsi_cold_check) + int(will_cold_check)

            is_ma_tangled = False
            if not (ma5_val > mid_line > ma60_val > ma120_val or ma5_val < mid_line < ma60_val < ma120_val):
                is_ma_tangled = True

            if is_ma_tangled and is_ma5_safe and vol_strength >= 65.0 and bandwidth >= 10.0 and (rsi_val <= 40 or temp_bottom_score >= 1 or (p_chg >= 0.0 and p >= mid_line)):
                is_ma_tangled = False

            ma20_safe_threshold = mid_line * 1.002
            is_ma20_teetering = (p >= mid_line * 0.998) and (p < ma20_safe_threshold)
            is_ma20_battling = (p >= mid_line * 0.97) and (p <= mid_line * 1.04) and (p >= ma5_val)
            is_ma20_buffer_safe = p >= ma20_safe_threshold

            bottom_score = min(3, temp_bottom_score)
            
            rsi_pullback_val = 1 if (38.0 <= rsi_val <= 62.0) else 0
            will_pullback_val = 1 if (-65.0 <= will_val <= -35.0) else 0
            bb_center_val = 1 if ((p >= mid_line) and (45.0 <= bb_pct_b <= 70.0 or p <= mid_line * 1.03) and (not is_bearish_candle)) else 0
            
            pullback_rebound_score = min(3, int(rsi_pullback_val + will_pullback_val + bb_center_val))

            is_bullish = (ma5_val > mid_line and mid_line > ma60_val and ma60_val > ma120_val)
            is_bearish = (ma5_val < mid_line and mid_line < ma60_val and ma60_val < ma120_val)
            is_down_trend_structural = is_bearish or (p < mid_line and mid_line <= ma60_val)

            # ==================================================================
            # ★ [신규] 3대 시장 국면 자동 분류 (정배열 / 혼조세 / 역배열)
            # ==================================================================
            if is_bullish or (p >= mid_line and ma5_val >= mid_line and mid_line >= ma60_val and arrow_20 != "↘"):
                market_regime = "정배열"
                regime_badge = "🟢 [정배열 · 추세 추종 모드]"
                stage1_alloc = "10%"
                stage2_alloc = "20~30%"
                stage3_alloc = "50%"
            elif is_down_trend_structural:
                market_regime = "역배열"
                regime_badge = "🔴 [역배열 · 방어 최우선 모드]"
                stage1_alloc = "5~10%(초소액 정찰)"
                stage2_alloc = "15~20%(20일선 돌파 조건부)"
                stage3_alloc = "20일선 안착 후 눌림목 대기"
            else:
                market_regime = "혼조세"
                regime_badge = "🟡 [혼조세 · 선별 짧은 호흡 모드]"
                stage1_alloc = "10%"
                stage2_alloc = "20%"
                stage3_alloc = "40~50%"
            rolling_low_b = df["MA20"] - (df["Std"] * 2)
            rolling_up_b = df["MA20"] + (df["Std"] * 2)
            rolling_pct_b = ((df["Close"] - rolling_low_b) / (rolling_up_b - rolling_low_b + 1e-10)) * 100.0
            bb_bot_series = ((df["Close"] <= (rolling_low_b * 1.02)) | (rolling_pct_b <= 15.0)).astype(int)
            rsi_bot_series = (rsi_series <= 38).astype(int)
            will_bot_series = (will_series <= -75).astype(int)
            bottom_score_series = bb_bot_series + rsi_bot_series + will_bot_series
            
            recent_bottom_entry_flag = (bottom_score_series.iloc[-4:-1].max() >= 1) if len(bottom_score_series) >= 4 else False
            recent_bottom_memory = bottom_score_series.iloc[-3:].max() >= 1  
            is_memory_ignored = False
            if user_last_1st_price == 0 and recent_bottom_entry_flag:
                recent_bottom_entry_flag = False
                is_memory_ignored = True

            is_deep_discount_buy = False
            drop_ratio = 0.0
            if user_last_1st_price > 0:
                drop_ratio = ((user_last_1st_price - p) / user_last_1st_price) * 100
                if drop_ratio >= 5.0 and (bottom_score >= 1 or will_val <= -75):
                    is_deep_discount_buy = True

            tr1 = df["High"] - df["Low"]
            tr2 = (df["High"] - df["Close"].shift(1)).abs()
            tr3 = (df["Low"] - df["Close"].shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr_14 = float(tr.rolling(14).mean().iloc[-1]) if len(df) >= 14 else float(tr.mean())

            atr_ratio = (atr_14 / ma5_val) if ma5_val > 0 else 0.03
            dynamic_stop_rate = max(0.02, min(0.05, atr_ratio))
            dynamic_stop_pct = dynamic_stop_rate * 100
            dynamic_stop_price = ma5_val * (1 - dynamic_stop_rate)

            lookback_window = min(20, len(df) - 1) if len(df) > 1 else 1
            raw_prev_low = float(df["Low"].iloc[-lookback_window-1:-1].min()) if lookback_window > 1 else float(df["Low"].min())
            prev_low = raw_prev_low * 0.97  

            if not (p < ma5_val):
                stop_loss_price = dynamic_stop_price
                stop_loss_label = f"🛡 단기 추세 체크포인트: 5일선 -{dynamic_stop_pct:.1f}% 이탈 시 비중 조절 및 관망({stop_loss_price:{fmt_p}}{currency})"
            else:
                stop_loss_price = prev_low
                stop_loss_label = f"🚨 칼손절 경보: 최근 20일 저점 -3% 마지노선({stop_loss_price:{fmt_p}}{currency})"

            defense_link_idx = min(21, len(df))
            raw_defense = float(df["High"].iloc[-defense_link_idx:-1].max()) * 0.93 if len(df) > 1 else p * 0.93
            defense_line = max(raw_defense, mid_line)
            wait_line = low_b_val * 1.02

            target_price_100 = up_b
            is_target_reached = p >= target_price_100
            is_on_the_wall = (p >= defense_line) and (p < target_price_100)
            is_band_riding = is_target_reached and is_band_expanding and is_ma5_safe and (not is_bearish_candle)
            
            is_peak_dumping = is_long_upper_tail and (is_band_riding or is_target_reached or p >= (target_price_100 * 0.98) or bb_pct_b >= 75.0)

            is_ob_stage2_safe = True
            is_ob_stage3_safe = True
            ob_ratio_val = ob_data.get("ratio")
            has_manual_ob = manual_ask > 0 and manual_bid > 0
            ob_ratio_available = ob_ratio_val is not None and float(ob_ratio_val) > 0 and has_manual_ob
    
            if not is_kr and not has_manual_ob:
                ob_status_msg = "💡 <b>미장 자동 호가 미제공</b> (수동 입력 시에만 HTS 잔량비 연산 가동)"
            elif ob_ratio_available:
                ob_ratio_val = float(ob_ratio_val)
                ask_formatted = f"{ob_data.get('ask', 0.0):,.0f}"
                bid_formatted = f"{ob_data.get('bid', 0.0):,.0f}"
    
                if ob_ratio_val >= 1.5:
                    ob_status_msg = f"🔥 <b>[본진 투입 합격]</b> 매도/매수 잔량비 <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted} / 매수:{bid_formatted}) - 매도벽을 걷어차는 강력 매수세 확정 (3단계 합격)"
                elif ob_ratio_val >= 1.0:
                    ob_status_msg = f"⚖️ <b>[탈출 공방 호가]</b> 매도/매수 잔량비 <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted} / 매수:{bid_formatted}) - 5일선 돌파 의지 확인 (2단계 합격 / 3단계 보류)"
                    is_ob_stage3_safe = False
                elif ob_ratio_val >= 0.5:
                    ob_status_msg = f"⚠️ <b>[속임수/윗꼬리 경계]</b> 매도/매수 잔량비 <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted} / 매수:{bid_formatted}) - 1.0배 미만! 세력이 위로 살 의지가 없는 속임수 경계"
                    is_ob_stage2_safe = False
                    is_ob_stage3_safe = False
                else:
                    ob_status_msg = f"🚨 <b>[허매수 폭락 경고]</b> 매도/매수 잔량비 <b>{ob_ratio_val:.2f}배</b> (매도:{ask_formatted} / 매수:{bid_formatted}) - 매수잔량이 2배 이상 많아 바닥을 가장한 허매수 투매 위험!"
                    is_ob_stage2_safe = False
                    is_ob_stage3_safe = False
            elif manual_ask > 0 or manual_bid > 0:
                ob_status_msg = "⚠️ <b>[호가 입력 불완전]</b> HTS 총매도잔량과 총매수잔량을 둘 다 입력해야 잔량비를 계산할 수 있습니다."
                is_ob_stage2_safe = False
                is_ob_stage3_safe = False
            else:
                ob_status_msg = "💡 <b>HTS 총매도·매수잔량을 입력하면 입력값 기준 호가 분석을 가동합니다.</b> (미입력 시 조건 패스)"

            if bandwidth < 10.0:
                is_bandwidth_ok = False
                bw_status_category = "EXTREME_SQUEEZE"
                bw_diag_msg = f"밴드폭 극소({bandwidth:.1f}%) 에너지 응축 중 / 돌파 방향 확인 대기"
                squeeze_info_str = f"<br>• ⚡ <b>[밴드폭 극소({bandwidth:.1f}%)]</b> 에너지가 바짝 응축 중이오! 돌파 방향 확인 전까지 진입 금지."
            elif 10.0 <= bandwidth < 20.0:
                if p >= ma5_val:
                    is_bearish_zone = ma5_val < mid_line
                    if is_bearish_zone:
                        is_bandwidth_ok = False
                        bw_status_category = "BEARISH_RESISTANCE"
                        bw_diag_msg = f"밴드폭 응축({bandwidth:.1f}%) 5일선 위 안착 / 역배열 저항 경계"
                        squeeze_info_str = f"<br>• ⚠️ <b>[밴드폭 응축({bandwidth:.1f}%)]</b> 5일선 위 안착 중이나, 머리 위 역배열 저항 매물벽(중심선 아래 위치 {bb_pct_b:.1f}%)을 경계하시오."
                    else:
                        is_bandwidth_ok = True
                        bw_status_category = "SQUEEZE_BREAKOUT"
                        bw_diag_msg = f"밴드폭 응축돌파({bandwidth:.1f}%) 5일선 안착 / 에너지 분출 초입"
                        if vol_strength < 65 or is_candle_bearish:
                            adjust_type_str = "음봉 조정" if is_candle_bearish else "숨고르기 공방"
                            squeeze_info_str = f"<br>• ⚠ <b>[성벽 위 {adjust_type_str}/차익매물출회({bandwidth:.1f}%)]</b> 5일선 위 안착 상태이나 당일 고점 차익 매물이 출회 중이오."
                        else:
                            if is_long_upper_tail:
                                squeeze_info_str = f"<br>• ⚠️ <b>[5일선 안착 속 상단 위꼬리 저항({bandwidth:.1f}%)]</b> 5일선({ma5_val:{fmt_p}}{currency}) 위는 뚫고 올라섰으나, 장중 고점({today_high:{fmt_p}}{currency})에서 위꼬리 매물 폭탄을 맞고 밀려 내려왔소! 상단 저항이 거세니 돌파를 맹신하지 마시게."
                            else:
                                squeeze_info_str = f"<br>• 🟢 <b>[밴드폭 응축돌파({bandwidth:.1f}%)]</b> 5일선을 뚫고 올라섰네! 상방 분출 초입으로 유효하오."
                else:
                    is_bandwidth_ok = False
                    if is_candle_bearish or p_chg < 0:
                        bw_status_category = "SQUEEZE_BREAKDOWN"
                        bw_diag_msg = f"밴드폭 응축({bandwidth:.1f}%) 5일선 이탈/하방 압력"
                        squeeze_info_str = f"<br>• 📉 <b>[밴드폭 응축({bandwidth:.1f}%)]</b> 5일선을 깨고 하락 중이오! 섣부른 매수를 멈추고 지지를 확인하시게."
                    else:
                        bw_status_category = "SQUEEZE_WAIT"
                        bw_diag_msg = f"밴드폭 응축({bandwidth:.1f}%) 5일선 상향 돌파 대기"
                        squeeze_info_str = f"<br>• ⏳ <b>[밴드폭 응축({bandwidth:.1f}%)]</b> 5일선 돌파 전이오. 안착 신호를 기다리시게."
            else:
                is_bandwidth_ok = True
                bw_status_category = "WIDE_OK"
                bw_diag_msg = f"밴드폭 넉넉함({bandwidth:.1f}%) 상하 변동 진폭 확보"
                if p < ma5_val and (is_candle_bearish or p_chg < 0):
                    squeeze_info_str = f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 진폭은 트였으나 5일선 아래로 추락 중이오. 칼날을 피하시게."
                elif p < ma5_val:
                    squeeze_info_str = f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 진폭은 트였으나 5일선 돌파 전이오. 안착을 기다리시게."
                else:
                    squeeze_info_str = f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 상하 진폭 활주로는 충분히 트였으나, 위 지표 조건 충족 시에만 진격하시게."

            bb_pos_summary_line = f"<br>• 📍 <b>[볼린저 위치×캔들 판독]:</b> <span style='color:{bb_pos_col}; font-weight:bold;'>{bb_pos_tag}</span> — {bb_pos_desc}"
            squeeze_info_str = bb_pos_summary_line + squeeze_info_str

            ma5_str = f"{ma5_val:{fmt_p}}{currency}({arrow_5})"
            ma20_str = f"{mid_line:{fmt_p}}{currency}({arrow_20})"
            ma60_str = f"{ma60_val:{fmt_p}}{currency}({arrow_60})"
            ma120_str = f"{ma120_val:{fmt_p}}{currency}({arrow_120})"
    
            if is_ma5_safe and is_ma20_chronic_resist:
                ma20_resist_msg = f"<br>⚠️ <b>[20일선 천장 저항]</b> 최근 <b>{ma20_fail_days_now}거래일 연속</b> 20일선 돌파 실패 중 (우하향 압박)<br>"
            elif is_ma20_breakout_real:
                if bias_ma5 >= 7.0:
                    ma20_resist_msg = f"<br>⚠️ <b>[장기 저항 돌파·이격 과열]</b> {ma20_fail_days}일간의 20일선 천장 돌파! (단, 5일선 이격 +{bias_ma5:.1f}% 과열로 추격 금지)<br>"
                else:
                    ma20_resist_msg = f"<br>🚀 <b>[장기 저항 첫 돌파!]</b> {ma20_fail_days}일간의 20일선 천장을 거래량 실린 양봉으로 돌파!<br>"
            elif is_ma20_breakout_try:
                ma20_resist_msg = f"<br>⏳ <b>[20일선 돌파 시도]</b> {ma20_fail_days}일 만에 20일선 상향 시도 중 ({_try_reason_txt})<br>"
            else:
                ma20_resist_msg = ""

            if is_bullish:
                if p < mid_line: trend_status = "⚠️ <b>[정배열 붕괴 경계]</b> 완벽한 우상향이나 현재가가 20일선 성벽을 깨고 추락 중"
                elif p < ma5_val: trend_status = "⚠️ <b>[정배열 단기 조정]</b> 우상향 성벽 속 5일선 이탈 숨고르기"
                else: trend_status = "🔥 <b>[대세 정배열]</b> 완벽한 우상향 성벽 구축 완료"
            elif is_bearish:
                if p > mid_line: trend_status = "🌱 <b>[역배열 탈출 시도]</b> 지하실에서 20일선을 뚫고 강력 반등 모색 중"
                else: trend_status = "⚠️ <b>[대세 역배열]</b> 지하실 향하는 하락 추세"
            elif ma5_val > mid_line:
                if p < ma5_val and p < mid_line: trend_status = "📉 <b>[추세 이탈/하락 반전]</b> 5일선·20일선 연쇄 붕괴! 하방 압력 심화 중"
                elif p < ma5_val: trend_status = "📉 <b>[단기 지지 이탈]</b> 5일선이 20일선 위에 있으나 현재가가 5일선을 깨고 밀리는 중"
                else: trend_status = "🌱 <b>[단기 반등 초입]</b> 5일선이 20일선 돌파! 상방 반전 시도 중"
            elif ma5_val <= mid_line:
                if p > ma5_val and p > mid_line: trend_status = "🔥 <b>[강력 반등 국면]</b> 5일선 역배열이나 현재가가 20일선을 강하게 돌파 중"
                elif p > ma5_val: trend_status = "🌱 <b>[단기 바닥 반등]</b> 5일선 밑에서 현재가가 5일선을 뚫고 고개를 드는 중"
                else: trend_status = "📉 <b>[하락 추세 심화]</b> 20일선 아래에서 단기 생명선(5일선)마저 붕괴! 하방 위험 증가"
            else: 
                trend_status = "⚖️ <b>[추세 혼조]</b> 방향 탐색 중"

            def generate_ma_hierarchy(df, current_price):
                ma_dict = {
                    "120일": ma120_val,
                    "60일": ma60_val,
                    "20일": mid_line,
                    "5일": ma5_val,
                    "현재가": current_price
                }
                sorted_items = sorted(ma_dict.items(), key=lambda x: x[1], reverse=True)
                
                hierarchy_parts = []
                for name, price in sorted_items:
                    if name == "현재가": 
                        hierarchy_parts.append(f'<span style="color:#ff6600; font-weight:bold;">현재가({current_price:{fmt_p}}{currency})</span>')
                    else: 
                        hierarchy_parts.append(f"{name}")
                
                hierarchy_str = " > ".join(hierarchy_parts)
                
                if ma5_val < mid_line < ma60_val < ma120_val: comment = "*(대세 역배열 저항 압박)*"
                elif ma5_val > mid_line > ma60_val > ma120_val: comment = "*(완벽 정배열 상승 랠리)*"
                else: comment = "*(이평선 혼조세 횡보 구간)*"
                
                return f"&nbsp;&nbsp;&nbsp;&nbsp;<b>[이평선 층위]</b> {hierarchy_str} {comment}"
              
            ma_price_summary = (
                "<br>• 📌 <b>[주요 이동평균선 현황]</b><br>&nbsp;&nbsp;&nbsp;<span"
                f" style='color:#D32F2F; font-weight:bold;'>🔴 5일선: {ma5_str} (이격:"
                f" {bias_ma5:+.1f}%)</span> | <span style='color:#1976D2;'"
                f" font-weight:bold;'>🔵 20일선: {ma20_str}</span> | <span"
                f" style='color:#388E3C; font-weight:bold;'>🟢 60일선: {ma60_str}</span> |"
                f" <span style='color:#7B1FA2; font-weight:bold;'>🟣 120일선: {ma120_str}</span><br>{ma20_resist_msg}"
            )
            ma_price_summary += generate_ma_hierarchy(df, p)
              
            final_display_name = get_stock_name(symbol, is_kr)
            safe_display_name = html.escape(final_display_name)

            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(
                f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>"
                f"<p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{safe_display_name}</p>"
                f"<p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>",
                unsafe_allow_html=True
            )

            c_wait, c_def, c_tgt = st.columns(3)
            with c_wait:
                wait_diff = ((p - wait_line) / wait_line) * 100 if wait_line > 0 else 0
                wait_tag = f"🎯 바닥 사정권 ({_c_short})" if (p <= wait_line * 1.03 or bb_pct_b <= 15.0) else f"바닥 상회 (위치 {bb_pct_b:.0f}%·{_c_short})"
                wait_color = "#E65100" if (p <= wait_line * 1.03 or bb_pct_b <= 15.0) else "#1565C0"
                st.markdown(
                    f"""<div class='price-card' style='border-top: 5px solid {wait_color}; margin-top: 10px;'>
                    <div style='font-size: 20px; color: #37474F;'>🎯 공략대기선 (볼린저 바닥선)</div>
                    <div style='font-size: 30px; color: {wait_color}; margin: 8px 0;'>{wait_line:{fmt_p}}{currency}</div>
                    <div style='font-size: 17px; color: {wait_color};'>{wait_tag} ({wait_diff:+.1f}%)</div>
                    </div>""", unsafe_allow_html=True
                )

            with c_def:
                def_diff = ((p - defense_line) / defense_line) * 100 if defense_line > 0 else 0
                def_status_tag = f"🏰 성벽 돌파/수성 ({_c_short})" if p >= defense_line else f"⚠️ 성벽 아래 함락 ({_c_short})"
                def_color = "#2E7D32" if p >= defense_line else "#D32F2F"
                st.markdown(
                    f"""<div class='price-card' style='border-top: 5px solid {def_color}; margin-top: 10px;'>
                    <div style='font-size: 20px; color: #37474F;'>🛡️ 성벽 (최후 방어선 / 돌파선)</div>
                    <div style='font-size: 30px; color: {def_color}; margin: 8px 0;'>{defense_line:{fmt_p}}{currency}</div>
                    <div style='font-size: 17px; color: {def_color};'>{def_status_tag} ({def_diff:+.1f}%)</div>
                    </div>""", unsafe_allow_html=True
                )

            with c_tgt:
                _real_candidates = [x for x in [defense_line, ma60_val] if x > p and x < target_price_100]
                if is_down_trend_structural and _real_candidates:
                    _disp_tgt = min(_real_candidates)
                    _disp_tgt_name = "성벽" if _disp_tgt == defense_line else "60일선"
                    _disp_diff = ((_disp_tgt - p) / p) * 100 if p > 0 else 0
                    tgt_title = f"🏆 1차 현실 목표선 (역배열 {_disp_tgt_name})"
                    tgt_val_show = _disp_tgt
                    tgt_status_tag = f"현실 여력 {_disp_diff:+.1f}% (볼린저상단 {target_price_100:{fmt_p}}{currency})"
                    tgt_color = "#E65100"
                else:
                    tgt_title = "🏆 수확 목표선 (볼린저 상단)"
                    tgt_val_show = target_price_100
                    tgt_diff = ((target_price_100 - p) / p) * 100 if p > 0 else 0
                    if is_band_riding: tgt_status_tag = "🌊 목표선 상방 확장 중 (밴드 라이딩)"; tgt_color = "#6A1B9A"
                    elif p >= (target_price_100 * 0.98) or bb_pct_b >= 90.0: tgt_status_tag = f"🎯 목표 임박/도달 ({_c_short} 수확 구역)"; tgt_color = "#E65100"
                    else: tgt_status_tag = f"상승 여력 {tgt_diff:+.1f}%"; tgt_color = "#1565C0"

                st.markdown(
                    f"""<div class='price-card' style='border-top: 5px solid {tgt_color}; margin-top: 10px;'>
                    <div style='font-size: 20px; color: #37474F;'>{tgt_title}</div>
                    <div style='font-size: 30px; color: {tgt_color}; margin: 8px 0;'>{tgt_val_show:{fmt_p}}{currency}</div>
                    <div style='font-size: 17px; color: {tgt_color};'>{tgt_status_tag}</div>
                    </div>""", unsafe_allow_html=True
                )

            st.write("")
            is_positive_day = p >= prev_p if prev_p > 0 else False
        
            if is_pre_market_mode:
                v_status, v_adv = ("프리장 대기", "🇺🇸 <b>[프리마켓 모드]</b> 수동 가격 반영 중이오. 장전 거래량이 희박하니 실시간 수급 차단 로직을 우회하여 타점을 판독하오.")
            elif is_positive_day:
                if vol_strength >= 300:
                    v_status, v_adv = ("광기 폭발(오버슈팅)", f"🔥 <b>[화력 폭발/광기]</b> 시간보정 강도 {vol_strength:.1f}점! 매수세가 미친 듯이 폭발 중이오. 윗꼬리(상투) 조심하시게.")
                elif vol_strength >= 100:
                    v_status, v_adv = ("매집 시작(강세)", f"🚀 <b>[매집시작]</b> 시간보정 강도 {vol_strength:.1f}점! 화력이 강하게 차오르며 하락 수압을 밀어 올리고 있소.")
                elif vol_strength >= 65:
                    v_status, v_adv = ("정상 화력(유입)", f"⚔️ <b>[정상화력]</b> 시간보정 강도 {vol_strength:.1f}점! 상승 기세가 든든하게 유지되고 있소.")
                else:
                    v_status, v_adv = ("거래 숨고르기", f"🧊 <b>[거래 숨고르기]</b> 시간보정 강도 {vol_strength:.1f}점! 1단계 진바닥 입질 및 양봉 지지력 확인 구역이오.")
                    
            else: 
                is_basement = (rsi_val <= 38 or will_val <= -75 or bb_pct_b <= 15.0)
        
                if is_massive_dump:
                    v_status, v_adv = ("대량 투매 경계", f"🚨 <b>[대량 투매 폭발/칼날 주의]</b> 시간보정 강도 {vol_strength:.1f}점! 지표는 바닥권이나 매도 물량이 쏟아지는 칼날 구간이오. 섣부른 입질을 금하고 투매 진정을 확인하시게.")
                elif vol_strength >= 300:
                    if is_basement:
                        v_status, v_adv = ("투매 절정 / 패닉셀", f"🚨 <b>[투매 절정/바닥 징후]</b> 시간보정 강도 {vol_strength:.1f}점! 지하실에서 개미들의 패닉셀이 폭발했소! 세력의 손바뀜을 노려보시게.")
                    else:
                        v_status, v_adv = ("대량 차익투매", f"🔥 <b>[대량 차익투매 경계]</b> 시간보정 강도 {vol_strength:.1f}점! 쏟아지는 음봉 폭포수이오. 섣부른 줍줍을 금하고 칼질 관망하시게.")
                elif vol_strength >= 100:
                    if is_basement:
                        v_status, v_adv = ("바닥 물량 매집", f"🟢 <b>[바닥권 매집/손바뀜]</b> 시간보정 강도 {vol_strength:.1f}점! 투매 물량을 세력이 조용히 쓸어 담고 있는 방어선이오.")
                    elif is_down_trend_structural:
                        v_status, v_adv = ("역배열 과열", f"⚠️ <b>[역배열과열]</b> 시간보정 강도 {vol_strength:.1f}점! 하락 추세 속 속임수 음봉 거래량이니 속지 마시게.")
                    else:
                        v_status, v_adv = ("차익 매물 출회", f"⚠️ <b>[차익매물출회]</b> 시간보정 강도 {vol_strength:.1f}점! 고점 및 성벽 저항대에서 차익 매물이 쏟아지고 있소.")
                elif vol_strength >= 65:
                    if is_basement:
                        v_status, v_adv = ("바닥 지지 테스트", f"🛡️ <b>[바닥 지지 공방]</b> 시간보정 강도 {vol_strength:.1f}점! 냉골 구역에서 하락을 멈추려는 방어전이 치열하오.")
                    elif not is_down_trend_v:
                        v_status, v_adv = ("정상 눌림목 조정", f"🛡️ <b>[숨고르기조정]</b> 시간보정 강도 {vol_strength:.1f}점! 정배열 속 정상적인 눌림목 음봉 조정 중이오.")
                    else:
                        v_status, v_adv = ("추세 하락 진행", f"⚠️ <b>[하락 압력]</b> 시간보정 강도 {vol_strength:.1f}점! 음봉 압력이 지속되며 매물대가 무거워지고 있소.")
                else:
                    v_status, v_adv = ("거래량 미달 / 절벽", f"🟡 <b>[거래량 미달 / 관망]</b> 시간보정 강도 {vol_strength:.1f}점! 수급이 마르고 동력이 없으니 섣부른 뇌동매매를 엄금하네.")
            st.markdown(
                f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량 전환: {v_status} (실시간 {v_ratio:.1f}% / 5일평균대비)</div>"
                f"<div style='font-size:18px; color:#37474F; background:#FFFFFF; padding:10px; border-radius:8px; border-left:6px solid #1976D2; margin-bottom:10px;'>{v_adv}</div>"
                f"<div style='font-size: 18px; color: #37474F; background: #FFFFFF; padding: 10px; border-radius: 8px; border-left: 6px solid #FF9800;'>🎯 <b>[호가창 잔량 공방]</b> {ob_status_msg}</div></div>",
                unsafe_allow_html=True,
            )

            is_stop_loss_triggered = False
            stop_reason = ""
            if user_avg_price > 0 and p < stop_loss_price:
                is_stop_loss_triggered = True
                stop_reason = "보유 평단가 대비 손절 마지노선 이탈"
            elif (recent_bottom_memory or bottom_score >= 1) and p < prev_low:
                is_stop_loss_triggered = True
                stop_reason = "바닥권 전저점 이탈 마지노선"

            is_bottom_indicator_ok = (bottom_score >= 1 or recent_bottom_memory)
            is_macd_not_deepening = not is_macd_reverse_deepening
            is_volume_ok_for_bottom = is_pre_market_mode or ((vol_strength >= 65.0) if (p_chg >= 0.0 and p >= today_open) else (vol_strength >= 70.0))
            
            # ==================================================================
            # ★ [신규] 국면별(역배열 / 혼조세 / 정배열) 1차·2차·눌림목 진입 조건 분기
            # ==================================================================
            is_near_ma5_bottom = (not is_ma5_safe) and (bias_ma5 >= -1.5) and (not is_candle_bearish)
            is_near_ma5_bull = (bias_ma5 >= -2.0) and (bias_ma5 <= 3.0) and (not is_candle_bearish)

            if market_regime == "역배열":
                # [역배열] 기존 보수 방어 로직 유지 (20일선 돌파 전 2차·눌림목 진입 엄격 차단)
                is_bottom_entry_signal = (
                    is_near_ma5_bottom and (bottom_score >= 1 or will_val <= -75)
                    and is_volume_ok_for_bottom and (not is_down_trend_v)
                    and is_macd_not_deepening and is_valid_bottom_candle and (not is_target_reached)
                    and (bb_pct_b <= 40.0)
                    and (not has_manual_ob or ob_ratio_val is None or ob_ratio_val >= 0.5)
                )
                is_escape_buy_signal = (
                    is_ma5_safe and (p >= mid_line) and is_bottom_indicator_ok
                    and (bias_ma5 <= 4.0)
                    and (vol_strength >= 65 or is_pre_market_mode)
                    and is_macd_not_deepening and is_valid_buy_candle
                    and is_bandwidth_ok and is_ob_stage2_safe and (not is_target_reached)
                    and (bb_pct_b < 80.0)
                )
                is_pullback_buy_signal = False

            elif market_regime == "혼조세":
                # [혼조세] 1차(5일선 직전·안착 + 진바닥), 2차(5일선 안착 + 20일선 돌파/근접), 눌림목(20일선 지지)
                is_bottom_entry_signal = (
                    (is_near_ma5_bottom or (is_ma5_safe and bias_ma5 <= 2.5))
                    and (bottom_score >= 1 or will_val <= -70)
                    and (vol_strength >= 55.0 or is_pre_market_mode)
                    and (not is_down_trend_v)
                    and is_macd_not_deepening and is_valid_bottom_candle and (not is_target_reached)
                    and (bb_pct_b <= 50.0)
                    and (not has_manual_ob or ob_ratio_val is None or ob_ratio_val >= 0.5)
                )
                is_escape_buy_signal = (
                    is_ma5_safe and (p >= mid_line * 0.99)
                    and (is_bottom_indicator_ok or pullback_rebound_score >= 1)
                    and (bias_ma5 <= 4.5)
                    and (vol_strength >= 60.0 or is_pre_market_mode)
                    and is_macd_not_deepening and is_valid_buy_candle
                    and is_ob_stage2_safe and (not is_target_reached)
                    and (bb_pct_b < 80.0)
                )
                is_pullback_buy_signal = (
                    is_ma20_buffer_safe and is_ma5_safe
                    and (pullback_rebound_score >= 1)
                    and (vol_strength >= 60.0 or is_pre_market_mode)
                    and is_macd_not_deepening and is_valid_buy_candle
                    and is_bandwidth_ok and is_ob_stage3_safe and (not is_target_reached)
                    and (45.0 <= bb_pct_b < 82.0)
                )

            else:
                # [정배열] 1차(5일선 지지·재돌파 유연 허용), 2차(5일선 안착 + MACD 정회전/회복), 눌림목(20일선 첫 눌림목)
                is_bottom_entry_signal = (
                    is_near_ma5_bull and (not is_ma5_safe or bias_ma5 <= 2.0)
                    and (bottom_score >= 1 or pullback_rebound_score >= 1 or rsi_val <= 55)
                    and (vol_strength >= 50.0 or is_pre_market_mode)
                    and is_macd_not_deepening and is_valid_buy_candle and (not is_target_reached)
                    and (bb_pct_b <= 75.0)
                    and (not has_manual_ob or ob_ratio_val is None or ob_ratio_val >= 0.5)
                )
                is_escape_buy_signal = (
                    is_ma5_safe and (bias_ma5 <= 5.0)
                    and (is_macd_bullish or is_macd_recovering)
                    and (vol_strength >= 55.0 or is_pre_market_mode)
                    and is_valid_buy_candle and is_ob_stage2_safe and (not is_target_reached)
                    and (bb_pct_b < 82.0)
                )
                is_pullback_buy_signal = (
                    is_ma20_buffer_safe and is_ma5_safe
                    and (pullback_rebound_score >= 1 or (p <= mid_line * 1.04 and is_macd_bullish))
                    and (vol_strength >= 50.0 or is_pre_market_mode)
                    and is_macd_not_deepening and is_valid_buy_candle
                    and is_ob_stage3_safe and (not is_target_reached)
                    and (40.0 <= bb_pct_b < 85.0)
                )

            if is_kr:
                is_morning_breakout_fast = (now_local.hour >= 10) and (vol_strength >= 300) and is_ma5_safe
                time_tag_ok = "오전장 화력 및 5일선 안착 완료 (기민 타점 가동)" if is_morning_breakout_fast else "14:00 이후 / 안정적 안착 확인"
            else:
                is_morning_breakout_fast = False
                time_tag_ok = "세션 화력 안착 확인"

            current_chg = float(p_chg)
            margin_diff = ((target_price_100 - p) / p) * 100 if p > 0 else 0

            is_strong_rebound = (p_chg >= 2.0) and (vol_strength >= 100) and (p >= today_open)
            
            total_candle_len = today_high - today_low if today_high > today_low else 0.0
            tail_bottom_len = (min(today_open, p) - today_low) if today_low < min(today_open, p) else 0.0
            
            is_long_lower_tail = total_candle_len > 0 and (tail_bottom_len >= total_candle_len * 0.5)
            
            if is_long_upper_tail and p >= today_open and not is_strong_rebound:
                final_code = "WAIT_LONG_TAIL_DEFENSE"
                sig = "🟡 [관망/보류] 윗꼬 매물 폭탄 / 시가 턱걸이 방어전 (신규 진입 금지)"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> <b>[위꼬리 매물 저항]</b> 시가({today_open:{fmt_p}}{currency}) 위로 솟구쳤으나 상단 매물 폭탄을 맞고 밀려 내려와 현재가({p:{fmt_p}}{currency})가 겨우 시가 위를 방어 중이오! 바닥 지표가 떴다 해도 섣부른 1단계 입질을 엄금하고 방어 성공 여부를 냉정하게 관망하시게."
        
            elif is_stop_loss_triggered:
                final_code = "STOP_LOSS_ALERT"
                sig = "🚨 [비상 손절] 바닥권 전저점 붕괴! 전량 칼손절 후퇴!"
                col = "#D32F2F"
                final_adv = f"• <b>[최종 결론]</b> <b>[바닥권 전저점 방어선 붕괴]</b> 최후의 방어선이 무참히 뚫렸소! 미련을 버리고 즉시 전량 칼손절 후퇴하시게."
            elif is_peak_dumping:
                final_code = "RED_SELL_WARNING"
                sig = "🔴 [고점 윗꼬리 투매] 상단 차익 매물 폭발! 즉시 수확(매도)!"
                col = "#D32F2F"
                final_adv = f"• <b>[최종 결론]</b> <b>[고점 윗꼬리 폭탄 포착]</b> 볼린저 상단 과열 구역에서 윗꼬리를 길게 달고 밀려 내려오고 있소! 세력의 대량 차익 실현이 시작되었으니 보유자는 즉시 전량 익절하시게."
            elif strict_doji_check and (p >= target_price_100 * 0.98 or bb_pct_b >= 85.0):
                final_code = "DOJI_TOP_WARNING"
                sig = "🟠 [고점 십자성 경고] 상승 에너지 고갈! 상투 징후"
                col = "#E65100"
                final_adv = f"• <b>[최종 결론]</b> <b>[고점 십자 도지(Doji) 포착]</b> 볼린저 상단 부근에서 매수세와 매도세가 팽팽하게 비겼소! 상투 징후이니 추격 매수를 금하고 익절을 준비하시게."
            elif strict_doji_check and (p <= low_b * 1.05 or bb_pct_b <= 20.0):
                final_code = "DOJI_BOTTOM_WAIT"
                sig = "🟡 [바닥 십자성 포착] 하락 투매 방어 확인! (내일 돌파 대기)"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> <b>[바닥 십자 도지(Doji) 포착]</b> 볼린저 하단 지하실을 파고 내려가던 중 누군가 가격을 방어해내며 십자형을 만들었소. 내일 십자 고가 돌파 여부를 확인하시게."
            elif strict_doji_check and (upper_tail_len <= day_candle_range * 0.1):
                if p < mid_line:
                    final_code = "DOJI_MID_WAIT"
                    sig = "🟡 [역배열·잠자리 도지] 하방 방어 시그널이나 20일선 아래 관망"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 장중 매도세를 걷어 올린 <b>[잠자리형 도지]</b>가 떴사오나, 아직 20일선({mid_line:{fmt_p}}{currency}) 아래 역배열 저항 구간이옵니다. 성급한 진입을 보류하시고 내일 양봉 안착 및 방향성을 확인하시게."
                else:
                    final_code = "DOJI_DRAGONFLY"
                    sig = "🟢 [강력한 하방 경직] 잠자리형 도지 포착! (매수세 방어 완승)"
                    col = "#2E7D32"
                    final_adv = f"• <b>[최종 결론]</b> 윗꼬리가 전혀 없는 <b>[잠자리형 도지(Dragonfly)]</b>가 떴소! 장중 투매를 매수세가 바닥에서 싹쓸이하여 시가(최고가)로 마감시킨 '강력한 방어 성공' 신호이니, 내일 긍정적인 반등을 기대해 볼 만하오."
            elif strict_doji_check:
                final_code = "DOJI_MID_WAIT"
                sig = "🟡 [추세 변곡 탐색] 십자형 공방전! 내일 승패를 확인하라"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> <b>[중간 지대 십자 도지(Doji) 포착]</b> 현재 매수세와 매도세가 50:50으로 피 터지게 싸우며 십자형을 만들었소. 당일 승패를 예단하는 것은 위험하니 관망하시게."
            elif (rsi_val >= 70 and rsi_val < rsi_sig_val) or (will_val >= -20 and will_val < will_sig_val):
                final_code = "SELL_PROFIT_TAKE"
                sig = "🚨 [선제 익절/수확 경보] 지표 초과열권 꺾임 포착!"
                col = "#D32F2F"
                final_adv = f"• <b>[최종 결론]</b> <b>[선제적 1차 익절 구간]</b> 현재가가 비록 5일선 위에 있더라도, RSI나 윌리엄스 지표가 극한의 천장을 찍고 시그널선을 뚫고 <b>아래로 꺾이고(▼ 데드크로스)</b> 있소! 세력의 고점 차익 실현(매도)이 막 시작된 찰나이니, <b>이평선이 무너지기 전에 미련 없이 50% 이상 분할 수확</b>하시고 신규 진입은 뇌동매매니 절대 엄금하시게."
            elif is_long_upper_tail and (p >= defense_line or p >= mid_line):
                final_code = "LONG_TAIL_WARNING"
                sig = "🟡 [위꼬리 저항 경계] 고점 매물 출회 / 추격 매수 금지"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> <b>[긴 위꼬리 저항 포착]</b> 장중 고점({today_high:{fmt_p}}{currency}) 대비 위꼬리가 길게 밀려 내려왔소! 지표상 안착처럼 보여도 위쪽 매물벽 저항이 맵사오니 섣부른 추격매수를 금하고 냉정하게 관망하시게."
            
            elif is_new_high_breakout:
                final_code = "NEW_HIGH_BREAKOUT_WARNING"
                sig = "🚨 [신고가 돌파 첫날] 불기둥 추격 매수 엄금!"
                col = "#D32F2F"
                final_adv = f"• <b>[최종 결론]</b> <b>[역사적 신고가 돌파]</b> 1년 최고점({high_250:{fmt_p}}{currency})을 뚫는 강력한 불기둥이 솟구쳤소! 섣불리 불을 잡지 말고, 단기 5일선({ma5_val:{fmt_p}}{currency}) 눌림목 안착 때까지 방아쇠를 굳게 잠그시게."
            elif is_new_high_pullback:
                _c_range = max(today_high - today_low, 1e-9)
                _body_len = abs(p - today_open)
                _upper_wick = today_high - max(p, today_open)
                _is_top_doji_or_wick = (_body_len / _c_range <= 0.25) or (_upper_wick > _body_len) or ("윗꼬리" in _c_short) or ("도지" in _c_short)
                if bb_pct_b >= 75.0 or _is_top_doji_or_wick:
                    final_code = "NEW_HIGH_BREAKOUT_WARNING"
                    sig = "🟠 [신고가 상단 도지/저항] 힘 빠짐 경계 (신규 매수 금지 · 보유자만 대응)"
                    col = "#FB8C00"
                    final_adv = f"• <b>[최종 결론]</b> <b>[고점 도지·윗꼬리 저항]</b> 1년 최고점 및 5일선({ma5_val:{fmt_p}}{currency}) 부근이나, 상단 과열(볼린저 {bb_pct_b:.1f}%) 속에 윗꼬리·도지 캔들이 출현하여 상승 추진력이 둔화되었소! 가짜 눌림목(상투) 위험이 크니 <b>[신규 매수 및 추가 불타기]는 절대 금하시고</b>, <b>[기 보유자]</b>만 5일선 이탈 전까지 추세를 지켜보시게."
                else:
                    final_code = "NEW_HIGH_PULLBACK_BUY"
                    sig = "🔵 [신고가 첫 눌림목] 정석 타점 (비중 채운 보유자는 불타기 금지)"
                    col = "#1E88E5"
                    final_adv = f"• <b>[최종 결론]</b> <b>[신고가 5일선 눌림목]</b> 1년 최고점 돌파 후 단기 생명선인 5일선({ma5_val:{fmt_p}}{currency})에 알찬 실체 양봉으로 아주 예쁘게 안착했소! <b>[신규 및 1·2단계 소량 보유자]</b>는 총 비중 50%까지 과감하게 본진을 투입(증원)하시게. 단, <b>[이미 비중을 다 채운 기 보유자]</b>는 무리한 고점 불타기를 금하고 신고가 대시세를 끝까지 발라 먹으시게."
            
            elif p >= target_price_100:
                if bandwidth <= 12.0:
                    final_code = "SQUEEZE_BREAKOUT_ATTACK"
                    sig = "🔥 [스퀴즈 상단 돌파] 볼린저 상단 돌파 대시세! (비중 채운 보유자는 불타기 금지)"
                    col = "#D84315"
                    final_adv = f"• <b>[최종 결론]</b> <b>[압력밥솥 볼린저 상단 폭발]</b> 밴드폭이 {bandwidth:.1f}%로 극한 응축된 상태에서 수확 목표선({target_price_100:{fmt_p}}{currency})마저 시원하게 뚫어버렸소! 드디어 상방으로 밸브가 터지며 대시세가 열렸으니 <b>[신규 및 1·2단계 소량 보유자]</b>는 총 비중 50%까지 과감하게 본진을 투입(증원)하고, <b>[이미 비중을 다 채운 기 보유자]</b>는 평단가를 높이는 불타기를 멈추고 랠리를 편안히 즐기시게."
                else:
                    final_code = "BAND_RIDING_HARVEST"
                    sig = "🟣 [상방 확장 중] 목표선 상방 돌파 완료!"
                    col = "#6A1B9A"
                    final_adv = f"• <b>[최종 결론]</b> <b>[목표선 상방 돌파 완료]</b> 현재가({p:{fmt_p}}{currency})가 최종 수확 목표선({target_price_100:{fmt_p}}{currency})을 돌파하여 안착했소! 저항선을 완전히 짓밟았으니, 이제부터는 밴드가 위로 쫙 벌어지는 대세 상승 랠리를 마음껏 즐기며 잔여 물량을 홀딩하시게."
            elif p >= (target_price_100 * 0.98) or bb_pct_b >= 92.0:
                if bandwidth <= 12.0:
                    final_code = "SQUEEZE_BREAKOUT_ATTACK"
                    sig = "🔥 [스퀴즈 상단 임박] 밸브 폭발 1초 전! (비중 채운 보유자는 불타기 금지)"
                    col = "#D84315"
                    final_adv = f"• <b>[최종 결론]</b> <b>[압력밥솥 상단 돌파 임박]</b> 밴드폭이 {bandwidth:.1f}%로 극한 응축된 상태에서 상단 목표선({target_price_100:{fmt_p}}{currency}) 돌파를 눈앞에 두고 있소! 상방으로 밸브가 터지기 직전이니 <b>[신규 및 1·2단계 소량 보유자]</b>는 총 비중 50%까지 본진을 투입(증원)하고, <b>[이미 비중을 다 채운 기 보유자]</b>는 무리한 불타기 없이 랠리에 탑승하시게."
                else:
                    final_code = "RED_SELL_TARGET"
                    sig = "🔴 [1차 선제적 익절] 수확 목표선 코앞 도달! (준비 구간)"
                    col = "#D32F2F"
                    final_adv = f"• <b>[최종 결론]</b> <b>[수확 목표선 임박]</b> 볼린저 상단({target_price_100:{fmt_p}}{currency}) 고지가 눈앞(위치 {bb_pct_b:.1f}%)이오! 욕심을 조금 덜어내고 1차 선제적 익절(분할 수확)을 준비하며 수익 일부를 챙길 채비를 하시게."
            elif p >= defense_line:
                if is_candle_bearish:
                    final_code = "RED_SELL_WARNING"
                    sig = "🔴 [성벽 위 음봉] 가짜 돌파(페이크) 경계 및 리스크 관리"
                    col = "#D32F2F"
                    final_adv = f"• <b>[최종 결론]</b> <b>[가짜 돌파 경계]</b> 현재가({p:{fmt_p}}{currency})가 성벽({defense_line:{fmt_p}}{currency}) 위에서 음봉을 띄우며 차익 매물을 쏟아내고 있소! 섣부른 추격 매수를 삼가고 방어선 붕괴 여부를 확인하시게."
                    
                elif p >= ma5_val:
                    _upside_pct = ((target_price_100 - p) / p * 100.0) if (p and p > 0 and target_price_100) else 999.0
                    if _upside_pct < 5.0:
                        final_code = "BREAKOUT_NEAR_TARGET_WAIT"
                        sig = f"🟡 [상단 근접·여력 {_upside_pct:.1f}%] 신규 추격 금지 / 보유자 관망·추종"
                        col = "#F57C00"
                        final_adv = (
                            f"• <b>[최종 결론]</b> <b>[상단 근접·신규 추격 보류]</b> 현재가({p:{fmt_p}}{currency})가 성벽({defense_line:{fmt_p}}{currency})과 5일선({ma5_val:{fmt_p}}{currency}) 위에서 기세를 유지 중이나, "
                            f"수확 목표선({target_price_100:{fmt_p}}{currency})까지 남은 상승 여력이 <b>+{_upside_pct:.1f}%</b>(5% 미만)뿐이오. "
                            f"신규 진입자는 매수 버튼에서 손을 떼고 눌림목을 기다리시며, 보유자만 5일선 종가 이탈 전까지 잔여 물량 수익을 관리하시게."
                        )
                    else:
                        final_code = "BREAKOUT_ATTACK"
                        sig = f"🟢 [성벽 위 {candle_color_txt}] 기세 유지 랠리 추종"
                        col = "#2E7D32"
                        final_adv = f"• <b>[최종 결론]</b> <b>[기세 유지 랠리 추종]</b> 현재가({p:{fmt_p}}{currency})가 성벽({defense_line:{fmt_p}}{currency}) 위에서 {candle_color_txt} 기세를 유지하고 있소! 5일선({ma5_val:{fmt_p}}{currency}) 지지 여부를 확인하며 상방 목표선({target_price_100:{fmt_p}}{currency}) 흐름을 추종하시게."
            
                else:  
                    final_code = "BREAKOUT_WARNING"
                    sig = "⚠️ [성벽 위 턱걸이] 5일선 이탈 경계"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> <b>[랠리 꺾임 경계]</b> 현재가({p:{fmt_p}}{currency})가 성벽({defense_line:{fmt_p}}{currency}) 위이나 단기 생명선(5일선) 아래로 뚫렸소! 진입을 멈추고 5일선 재돌파 전까지 철저히 관망하시게."
            elif (bottom_score >= 1 or pullback_rebound_score >= 1) and has_manual_ob and ob_ratio_val is not None and ob_ratio_val < 0.5 and not is_ma5_safe:
                final_code = "WAIT_ORDERBOOK"
                sig = "🟡 [관망/보류] 허매수 징후 포착 (폭락 경계)"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> <b>[허매수 투매 경계]</b> 진바닥 지표는 포착되었으나, 매도/매수 잔량비({ob_ratio_val:.2f}배)가 0.5배 미만으로 매수잔량이 비정상적으로 많소! 세력이 바닥을 가장해 개미에게 물량을 떠넘길 위험이 크니 절대 칼날을 잡지 마시게."
            elif is_ma5_safe and is_ma20_chronic_resist:
                _dist_to_ma20 = ((mid_line - p) / mid_line * 100.0) if (mid_line and mid_line > 0 and p) else 999.0
                if _dist_to_ma20 <= 5.0:
                    final_code = "WAIT_MA20_RESIST"
                    sig = f"🟡 [저항 관망] 20일선 {ma20_fail_days_now}일 연속 미돌파 (20일선 근접 저항)"
                    col = "#F57C00"
                    final_adv = (
                        f"• <b>[최종 결론]</b> <b>[20일선 천장 저항]</b> 최근 <b>{ma20_fail_days_now}거래일 연속</b>으로 "
                        f"20일선({mid_line:{fmt_p}}{currency}, {arrow_20})을 돌파하지 못한 상태에서 20일선 코앞(-{_dist_to_ma20:.1f}%)까지 접근했사옵니다. "
                        f"신규 매수는 보류하시고, 보유자께서는 20일선 부근 반등 시 비중 축소·분할 익절을 우선 고려하시옵소서."
                    )
                else:
                    final_code = "WAIT_MA5_BOUNCE"
                    sig = f"🟡 [단기 반등] 5일선 안착 반격 중 (20일선까지 +{_dist_to_ma20:.1f}% 거리)"
                    col = "#F57C00"
                    final_adv = (
                        f"• <b>[최종 결론]</b> <b>[5일선 단기 반등]</b> 현재가({p:{fmt_p}}{currency})가 5일선 위에 안착하며 단기 반격을 시작했사오나, "
                        f"20일선({mid_line:{fmt_p}}{currency})까지는 아직 <b>{_dist_to_ma20:.1f}%</b> 거리가 남은 역배열 구간이옵니다. "
                        f"20일선 공방 단계가 아니므로 5일선 지지 여부를 보며 단기 기술적 반등으로만 가볍게 대응하시옵소서."
                    )
            elif is_ma20_breakout_real:
                if bias_ma5 >= 7.0:
                    final_code = "WAIT_MA20_BREAK_OVEREXT"
                    sig = f"🟡 [돌파 성공·이격 과열] {ma20_fail_days}일 만의 20일선 돌파 (5일선 이격 +{bias_ma5:.1f}%)"
                    col = "#F57C00"
                    final_adv = (
                        f"• <b>[최종 결론]</b> <b>[장기 저항 돌파·추격 매수 금지]</b> {ma20_fail_days}거래일간 짓누르던 "
                        f"20일선({mid_line:{fmt_p}}{currency}) 천장을 거래량 실린 양봉으로 뚫어냈으나, "
                        f"5일선 대비 이격이 <b>+{bias_ma5:.1f}%</b>로 단기 과열되었사옵니다. "
                        f"고점 추격 매수는 금하시고, 20일선 눌림목 지지 확인 후 진입하시옵소서."
                    )
                else:
                    final_code = "BUY_MA20_BREAKOUT"
                    sig = f"🟡 [돌파 확인] {ma20_fail_days}일 만의 20일선 첫 돌파 (안착 확인)"
                    col = "#F57C00"
                    final_adv = (
                        f"• <b>[최종 결론]</b> <b>[20일선 첫 돌파·안착 확인]</b> {ma20_fail_days}거래일간 짓누르던 "
                        f"20일선({mid_line:{fmt_p}}{currency})을 거래량 실린 양봉으로 뚫어냈사옵니다. "
                        f"다만 역배열 저항 및 윗꼬리 매물 압력이 남아 있을 수 있으니, 20일선 지지 안착 여부를 확인한 뒤 분할 진입 및 홀딩을 검토하시옵소서."
                    )
            elif is_ma20_breakout_try:
                final_code = "WAIT_MA20_BREAK_TRY"
                if is_market_closed:
                    sig = f"🟡 [돌파 시도·종가 확정] {ma20_fail_days}일 만의 20일선 돌파 ({_try_reason_txt})"
                    final_adv = (
                        f"• <b>[최종 결론]</b> <b>[20일선 돌파 시도·종가 확정]</b> {ma20_fail_days}일 만에 20일선 위에 올라섰으나 "
                        f"<b>{_try_reason_txt}</b>로 인해 완전한 추세 전환으로 보기엔 부족하옵니다. "
                        f"내일 20일선({mid_line:{fmt_p}}{currency}) 지지 안착 여부를 확인한 뒤 대응하시옵소서."
                    )
                else:
                    sig = f"🟡 [돌파 시도] {ma20_fail_days}일 만의 20일선 돌파 시도 (종가 안착 확인)"
                    final_adv = (
                        f"• <b>[최종 결론]</b> <b>[20일선 돌파 시도 중]</b> {ma20_fail_days}일 만에 20일선을 넘보고 있으나 "
                        f"<b>{_try_reason_txt}</b> 상태이옵니다. 윗꼬리 함정을 피하기 위해 종가 기준 안착을 확인한 뒤 움직이시옵소서."
                    )
                col = "#F57C00"
            elif is_ma5_safe and not is_down_trend_structural and (bottom_score >= 1 or pullback_rebound_score >= 1) and has_manual_ob and ((pullback_rebound_score >= 1 and not is_ob_stage3_safe) or (bottom_score >= 1 and not is_ob_stage2_safe)):
                final_code = "WAIT_ORDERBOOK"
                sig = "🟡 [관망/보류] 매도잔량비 실전 기준 미달 (속임수 윗꼬 경계)"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> <b>[호가창 기준 미달]</b> 타점 지표는 충족했으나, 매도/매수 잔량비({ob_ratio_val:.2f}배)가 실전 투입 기준에 미달하오. 세력이 윗꼬리로 밀어버릴 속임수일 확률이 높으니 방아쇠를 잠그고 관망하시게."
            elif is_ma20_battling:
                final_code = "WAIT_MA20_BATTLE"
                col = "#F57C00"
                if p >= mid_line:
                    sig = f"🟡 [관망/대기] 20일선 성벽 수성전 (안착 대기)"
                    _battle_txt = f"볼린저 중심선({mid_line:{fmt_p}}{currency}, 위치 {bb_pct_b:.1f}%·{_c_short}) 턱 위에 올라타서 피 터지게 수성(방어)전을 치르는 중이오!"
                else:
                    sig = f"🟡 [관망/대기] 20일선 성벽 공방전 (돌파 대기)"
                    _battle_txt = f"볼린저 중심선({mid_line:{fmt_p}}{currency}, 위치 {bb_pct_b:.1f}%·{_c_short}) 턱밑까지 진격하여 피 터지게 돌파 공방을 벌이는 중이오!"
                
                final_adv = f"• <b>[최종 결론]</b> <b>[20일선 탈환 공방전]</b> 단기 생명선(5일선) 위로 올라타 {_battle_txt} 지금 들이대는 것은 칼받이가 되는 꼴이니, 20일선을 완벽하게 밟고 안착하는 '눌림목' 신호가 뜰 때까지 방아쇠를 잠그고 철저히 관망하시게."

            elif is_over_extended_5 and (vol_strength >= 300) and (p >= today_open) and (not is_long_upper_tail):
                final_code = "HIGH_PASS_OVEREXTENDED"
                sig = f"🔥 [불기둥 하이패스] 대량 거래 폭발! 과다이격({bias_ma5:+.1f}%) 추격 경계"
                col = "#D84315"
                final_adv = f"• <b>[최종 결론]</b> <b>[과다이격 추격 경계]</b> 대량 거래가 터졌으나 5일선 이격이 +{bias_ma5:.1f}%로 과도하게 벌어졌으니 섣부른 고점 추격 매수는 깊이 참고 자제하시게! <b>단, 20일선이나 5일선 이탈 시 즉각 대응할 수 있도록 보유 비중은 30% 이하로 엄격히 조여두시게.</b>"

            elif is_over_extended_5:
                final_code = "WAIT_OVER_EXTENDED"
                sig = f"🟡 [관망/보류] 5일선 과다이격 (+{bias_ma5:.1f}%) / 추격 매수 금지"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> <b>[과다이격 진입 차단]</b> 타점 조건은 충족했으나, 현재가가 5일선 대비 <b>+{bias_ma5:.1f}%</b>나 높게 떠 있소! 고점 윗꼬리에 물릴 위험이 크니 뇌동매매를 엄금하고 5일선과의 이격이 좁혀질 때까지 철저히 관망하시게."
            elif (bottom_score >= 1 or pullback_rebound_score >= 1) and (rsi_val < rsi_prev) and (will_val < will_prev) and (p < ma5_val):
                final_code = "WAIT_INDICATOR_FALLING"
                sig = "🟡 [관망/대기] 지표 하락 진행 중 (떨어지는 칼날)"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> 타점 점수 구간에 진입했으나, RSI와 윌리엄스 지표가 계속 <b>아래로 처박히고(▼ 하락)</b> 있소! 바닥이 어디일지 모르니 섣불리 줍지 말고, <b>다음날 지표가 위로 고개를 드는(▲ 상승) 것을 확인한 뒤에</b> 진입 여부를 결정하시게."
            
            elif p >= ma20_safe_threshold and bandwidth <= 12.0 and p >= today_open and (vol_strength >= 65 or is_pre_market_mode):
                if margin_diff < 4.0: 
                    final_code = "WAIT_NARROW_MARGIN"
                    sig = "🟡 [관망/보류] 상승 여력 부족 (수지타산 불량)"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 돌파 조건은 충족했으나 수확 목표선까지의 상승 여력이 {margin_diff:.1f}%에 불과하오! 리스크 대비 먹을 게 없는 좁은 자리이니 뇌동매매를 금하고 관망하시게."
                else:
                    final_code = "SQUEEZE_BREAKOUT_ATTACK"
                    col = "#D84315"
                    sig = "🔥 [스퀴즈 돌파] 압력밥솥 폭발! (비중 채운 보유자는 불타기 금지)"
                    final_adv = f"• <b>[최종 결론]</b> <b>[스퀴즈 20일선 돌파]</b> 밴드폭이 {bandwidth:.1f}%로 극한 응축된 상태에서 볼린저 중심선({ma20_safe_threshold:{fmt_p}}{currency})을 강력하게 뚫어냈소! <b>[신규 및 1·2단계 소량 보유자]</b>는 망설임 없이 총 비중 50%까지 본진을 투입(증원)하고, <b>[이미 비중을 다 채운 기 보유자]</b>는 평단가를 망치는 불타기 없이 상방 밸브가 터진 랠리에 편안히 탑승하시게."

            elif is_deep_discount_buy:
                final_code = "DEEP_DISCOUNT_ENTRY"
                sig = f"🔵 [낙폭 과대 하이패스] 추가 1단계 유효 (직전 매수가 대비 -{drop_ratio:.1f}% 폭탄 세일)"
                col = "#0277BD"
                final_adv = f"• <b>[최종 결론]</b> <b>[가격 메리트 극대화]</b> 직전 1차 매수가({user_last_1st_price:{fmt_p}}{currency}) 대비 <b>-{drop_ratio:.1f}%</b> 하락하여 완벽한 볼린저 하단 할인 구간에 진입했소! 대세 하락장이 아님을 확인했으니 기존의 쿨타임과 추매 금지 제약을 해제하고 평단가를 낮추는 과감한 물타기(추가 진입)가 유효하오."

            elif (bottom_score >= 2 or rsi_val <= 30):
                if is_massive_dump:
                    final_code = "BEARISH_GUARD"
                    sig = f"🚨 [투매/칼날 추락 중] 지표 바닥이나 대량 투매 폭발!"
                    col = "#D32F2F"
                    final_adv = f"• <b>[최종 결론]</b> <b>[대량 투매 경보]</b> 볼린저 및 지표는 바닥권이나, 거래량이 터지며 지하실로 쏟아지는 강력한 투매(칼날)가 발생 중이오! 절대 입질하지 말고 무조건 관망하시게."
                elif margin_diff < 4.0:
                    final_code = "WAIT_NARROW_MARGIN"
                    sig = "🟡 [관망/보류] 상승 여력 부족 (수지타산 불량)"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 진바닥 타점이나 수확 목표선까지의 상승 여력이 {margin_diff:.1f}%에 불과하오! 뇌동매매를 금하고 관망하시게."
                elif not is_defended:
                    if p < (ma5_val * 0.97):
                        final_code = "WATERFALL_DROP_WARNING"
                        sig = f"🚨 [절대 관망령] 지하실 폭포수 추락 중! (5일선 {bias_ma5:.1f}% 붕괴)"
                        col = "#D32F2F"
                        final_adv = f"• <b>[최종 결론]</b> 바닥 지표({bottom_score}/3점)가 반응했으나, 반등은커녕 5일선과 까마득히 멀어진 채 <b>{candle_color_txt}으로 지하실을 파고드는 수직 폭포수 추락 구간</b>이오! 떨어지는 칼날에 손목이 날아갈 자리이니 <b style='color:#FFEB3B;'>단 1주의 정찰병 파병조차 전면 금지하오!</b> 양봉 방어선이 구축될 때까지 100% 현금을 사수하시게!"
                    else:
                        final_code = "BEARISH_GUARD"
                        sig = "🔴 [떨어지는 칼날 경고] 지표는 바닥이나 하방 압력 지속!"
                        col = "#D32F2F"
                        final_adv = f"• <b>[최종 결론]</b> <b>[떨어지는 칼날 경고]</b> 지표는 극한의 바닥이나, 하방 압력(음봉/윗꼬리)이 여전히 거세오! 섣부른 희망 회로를 접고 <b>양봉 방어선이 확인될 때까지</b> 즉각 관망 모드로 대기하시게."
                else:
                    if recent_bottom_entry_flag and not is_strong_rebound:
                        final_code = "WAIT_COOL_TIME"
                        col = "#F57C00"
                        sig = "🟡 [관망/보류] 1단계 진입 쿨타임 가동 중 (중복 노이즈 차단)"
                        final_adv = f"• <b>[최종 결론]</b> 극한 진바닥 지표가 떴으나, <b>최근 3일 내에 이미 1차 진입 신호가 나간 이력</b>이 있소! 잔노이즈일 확률이 높으니 섣부른 중복 입질을 엄금하고 관망하시게."
                    else:
                        if p < (ma5_val * 0.97):
                            if p_chg <= 0 or is_candle_bearish:
                                final_code = "WATERFALL_DROP_WARNING"
                                col = "#D32F2F"
                                sig = f"🚨 [절대 관망령] 지하실 폭포수 추락 중! (단 1주도 아깝소!)"
                                final_adv = f"• <b>[최종 결론]</b> 바닥 지표가 반응했으나, 5일선과 까마득히 멀어진 수직 폭포수 하락({p_chg:+.2f}%) 구간이오! 아직 하락이 멈추지 않은 위험천만한 칼날이니, <b style='color:#FFEB3B;'>단 1주의 정찰병 파병조차 전면 금지하오!</b> 100% 현금을 사수하시게!"
                            else:
                                final_code = "DEAD_CAT_WARNING"
                                col = "#D32F2F"  
                                sig = "🚨 [절대 관망령] 데드캣 바운스 경계 (단 1주도 아깝소!)"
                                final_adv = f"• <b>[최종 결론]</b> 바닥 지표가 반응하며 반등을 시도하나, 5일선과 까마득히 멀어진 수직 폭포수 구간이오! 뻔히 죽을 자리로 끌어들이는 가짜 기술적 반등(데드캣 바운스) 위험이 크니, <b style='color:#FFEB3B;'>단 1주의 정찰병 파병조차 전면 금지하오!</b> 100% 현금을 사수하시게!"
                        else:
                            _bot_txt = f"당일 진바닥 지표({bottom_score}점, 볼린저위치 {bb_pct_b:.1f}%·{_c_short})" if bottom_score >= 1 else f"최근 3일 내 진바닥 터치(볼린저위치 {bb_pct_b:.1f}%·{_c_short})"
                
                            if "윗꼬리" in str(_c_short):
                                final_code = "WAIT_BOTTOM_UPPER_TAIL"
                                col = "#F57C00"
                                sig = "🟡 [진바닥·윗꼬리 주의] 매물 저항 출회 (종가 확인 후 1단계)"
                                final_adv = (
                                    f"• <b>[최종 결론]</b> <b>[극한 진바닥·윗꼬리 매물 주의]</b> {_bot_txt}이(가) 포착되었사오나, "
                                    f"상단 매물 저항(윗꼬리)이 동반되어 성급히 진입할 자리가 아니옵니다. "
                                    f"<b>[신규 진입자]</b>는 장중 추격을 보류하시고 종가 방어 또는 5일선 안착 확인 후 1단계 진입을 검토하시게."
                                )
                            elif is_candle_bearish and not is_extreme_lower_tail:
                                final_code = "BEARISH_GUARD"
                                col = "#D32F2F"
                                sig = "🚨 [진바닥·음봉 압력 주의] 양봉 전환 및 지지 확인 전까지 관망"
                                final_adv = (
                                    f"• <b>[최종 결론]</b> <b>[진바닥 음봉 압박 경계]</b> {_bot_txt}이(가) 포착되었사오나, "
                                    f"파란색 음봉 매도 압력이 이어져 바닥 붕괴 위험이 남아 있사옵니다. "
                                    f"<b>[신규 진입자]</b>는 성급한 입질을 멈추고 양봉 전환 및 지지 확인 후 진입을 검토하시게."
                                )
                            else:
                                final_code = "EXTREME_BOTTOM_ENTRY"
                                col = "#388E3C"
                                sig = "🟢 [극한 진바닥 포착] 신규 1단계 유효 (기 1단계 매수자는 추매 금지)"
                
                                if is_candle_unknown:
                                    _def_txt = "하락 진정 및 반등 기세"
                                elif is_strong_bull_body and not is_tail_defended:
                                    _def_txt = "강력한 매수세(반등 몸통)"
                                else:
                                    _def_txt = "아래꼬리 지지력(투매 방어)"
                
                                final_adv = (
                                    f"• <b>[최종 결론]</b> <b>[진바닥 지표 및 강력 방어 확인]</b> {_bot_txt}과(와) <b>{_def_txt}</b>이(가) 동시 확인되었소! "
                                    f"<b>[신규 진입자]</b>는 비중 10% 수준의 가벼운 1단계 정찰병을 투입하시게. 단, <b>[기 1단계 매수자]</b>는 섣부른 물타기를 엄금하고 5일선 안착(2단계)을 기다리며 관망하시게."
                                )
                        
            elif is_bottom_entry_signal and (p >= today_open) and (p_chg >= -1.5):
                if margin_diff < 4.0: 
                    final_code = "WAIT_NARROW_MARGIN"
                    sig = "🟡 [관망/보류] 상승 여력 부족 (수지타산 불량)"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 타점 조건은 충족했으나 수확 목표선까지의 상승 여력이 {margin_diff:.1f}%에 불과하오! 리스크 대비 먹을 게 없는 좁은 자리이니 뇌동매매를 금하고 관망하시게."
                elif not is_defended:
                    final_code = "WAIT_GENERAL"
                    sig = "🟡 [관망/보류] 1단계 입질 구역이나 방어선 미확인"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 바닥권에 진입했으나 아직 확고한 방어선이 확인되지 않았소! 칼날이 멈출 때까지 대기하시게."
                else:
                    if recent_bottom_entry_flag and not is_strong_rebound:
                        final_code = "WAIT_COOL_TIME"
                        col = "#F57C00"
                        sig = "🟡 [관망/보류] 1단계 진입 쿨타임 가동 중 (중복 노이즈 차단)"
                        final_adv = f"• <b>[최종 결론]</b> 1단계 바닥 지표가 켜졌으나, <b>최근 3일 내에 이미 1차 진입 이력</b>이 있소! 잔노이즈일 확률이 높으니 섣부른 중복 입질을 멈추고 관망하시게."
                    elif is_long_upper_tail:
                        final_code = "TRAP_UPPER_TAIL_1"
                        col = "#D32F2F"
                        sig = f"🚨 [진입 보류] 치명적 윗꼬리 발생! 1단계 입질 백지화"
                        final_adv = f"• <b>[최종 결론]</b> 지표는 바닥권이나, 흉측한 윗꼬리(상투)가 달리며 물량 떠넘기기가 의심되오! 전형적인 함정이니 섣부른 1단계 정찰병 투입마저 전면 취소하고 철저히 관망하시게."
                    elif vol_strength >= 300:
                        final_code = "OVERHEATED_BLOCK_1"
                        col = "#D32F2F"
                        sig = f"🚨 [진입 보류] 거래량 광기(과열)! 1단계 입질 백지화"
                        final_adv = f"• <b>[최종 결론]</b> 진바닥 타점이긴 하나, 매수세가 비정상적으로 과열된 '오버슈팅' 상태이오! 언제 급락의 철퇴를 맞을지 모르니 1단계 입질도 멈추고 방아쇠를 꽉 잠그시게."
                    else:
                        final_code = "BOTTOM_ENTRY"
                        col = "#388E3C"
                        sig = f"🟢 [진바닥 입질] 신규 1단계 유효 (기 1단계 매수자는 2단계 대기) ({time_tag_ok})"
        
                        if is_candle_unknown:
                            _def_txt = "하락 진정 및 반등 기세"
                        elif is_strong_bull_body and not is_tail_defended:
                            _def_txt = "강력한 매수세(반등 몸통)"
                        else:
                            _def_txt = "아래꼬리 지지력(투매 방어)"
        
                        _bot_txt = f"당일 진바닥 지표({bottom_score}점, 볼린저위치 {bb_pct_b:.1f}%·{_c_short})" if bottom_score >= 1 else f"최근 3일 내 바닥 터치 후 반등(볼린저위치 {bb_pct_b:.1f}%·{_c_short})"

                        final_adv = f"• <b>[최종 결론]</b> <b>[1단계 정찰병 포착]</b> {_def_txt} 및 {_bot_txt}이(가) 확인되었소! <b>[신규 진입자]</b>라면 비중 10% 수준의 1단계 정찰병(입질) 투입이 유효하오. 단, <b>[기 1단계 매수자]</b>는 추가 매수를 멈추고 5일선 위로 올라타는 2단계 진격 신호 전까지 철저히 관망하시게."
            elif is_escape_buy_signal and (market_regime == "정배열" or bottom_score >= 1 or pullback_rebound_score >= 1):
                if margin_diff < 4.0: 
                    final_code = "WAIT_NARROW_MARGIN"
                    sig = "🟡 [관망/보류] 상승 여력 부족 (수지타산 불량)"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 타점 조건은 충족했으나 수확 목표선까지의 상승 여력이 {margin_diff:.1f}%에 불과하오! 관망하시게."
                elif (rsi_val >= 68) or (will_val >= -25) or (bb_pct_b >= 80.0):
                    final_code = "WAIT_OVER_HEATED_IND"
                    col = "#F57C00"
                    sig = f"🚨 [진입 보류] 지표/볼린저 단기 과열권 도달! 2단계 진격 보류"
                    final_adv = f"• <b>[최종 결론]</b> 5일선에 안착하여 바닥은 탈출했으나, 지표나 볼린저 위치가 이미 <b>단기 상단 과열권</b>에 도달했소! 지금 들이대면 고점에 물릴 확률이 몹시 크니, 섣부른 2단계 진입을 멈추고 온도가 식을 때까지 철저히 관망하시게."
                elif is_long_upper_tail:
                    final_code = "TRAP_UPPER_TAIL"
                    col = "#D32F2F"
                    sig = f"🚨 [진입 보류] 치명적 윗꼬리 발생! 2단계 진격 백지화"
                    final_adv = f"• <b>[최종 결론]</b> 5일선 위에는 간신히 턱걸이했으나, 고점에서 차익 매물이 쏟아지며 흉측한 윗꼬리(상투)가 달렸소! 전형적인 세력의 물량 떠넘기기 함정이니 섣부른 2단계 진입을 전면 취소하고 철저히 관망하시게."
                elif vol_strength >= 300:
                    final_code = "OVERHEATED_BLOCK"
                    col = "#D32F2F"
                    sig = f"🚨 [진입 보류] 거래량 광기(과열)! 2단계 진격 백지화"
                    final_adv = f"• <b>[최종 결론]</b> 5일선 안착에는 성공했으나, 매수세가 비정상적으로 과열된 '오버슈팅' 상태이오! 언제 날카로운 윗꼬리를 달고 곤두박질칠지 모르는 몹시 위태로운 전장이니, 불나방처럼 뛰어들지 말고 방아쇠를 잠그시게."
                else:
                    final_code = "ESCAPE_BUY"
                    col = "#2E7D32"
                    sig = f"🟢 [추가 진격] 2단계 바닥 탈출 (기 2단계 매수자는 추매 금지) ({time_tag_ok})"
                    final_adv = f"• <b>[최종 결론]</b> <b>[{time_tag_ok}]</b> 밴드 하단부를 벗어나 5일선 안착 성공! 단, 머리 위 성벽 저항이 남았으니 [신규 진입자 및 1단계 소량 매수자]는 총 비중 20~30%까지 정찰대 증원으로 대응하시게. [이미 2단계 비중을 채운 보유자]는 섣부른 불타기를 엄금하고 3단계 눌림목 신호 전까지 관망하시게."
            elif is_pullback_buy_signal:
                if margin_diff < 4.0:
                    final_code = "WAIT_NARROW_MARGIN"
                    sig = "🟡 [관망/보류] 상승 여력 부족 (수지타산 불량)"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 타점 조건은 충족했으나 수확 목표선까지의 상승 여력이 {margin_diff:.1f}%로 너무 비좁소! 굳이 푼돈 먹겠다고 호랑이 굴에 들어가지 말고 관망하시게."
    
                elif (not is_valid_buy_candle) or (p_chg < 0):
                    final_code = "WAIT_DUMP_WARNING"
                    sig = "🟡 [관망/보류] 떨어지는 칼날 (음봉 하락 경고)"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 20일선 위에 있으나 현재 전일 대비 하락({p_chg:.2f}%) 중인 퍼런 음봉이오! 대량 투매에 휘말릴 수 있으니 섣부른 진격을 금하고 지지가 확인될 때까지 철저히 관망하시게."
                
                else:
                    final_code = "PULLBACK_BUY"
                    sig = "🔵 [정석 눌림목 진격] 20일 중심선 완벽 돌파 (비중 채운 보유자는 불타기 금지)"
                    col = "#5482F0"
                    final_adv = f"• <b>[최종 결론]</b> [눌림목 돌파 완료] 볼린저 20일 중심선({mid_line:{fmt_p}}{currency})을 든든히 밟고 붉은 양봉으로 상방 순항 구역에 진입하였소! <b>[신규 및 1·2단계 소량 보유자]</b>는 총 비중 50%까지 화끈하게 본진을 투입(증원)하고, <b>[이미 비중을 다 채운 기 보유자]</b>는 무리한 불타기 없이 랠리를 즐기시게."
            elif is_ma_tangled:
                final_code = "MA_TANGLED_WARNING"
                sig = "🟡 [이평선 꼬임 혼조세] 방향성 상실로 인한 관망"
                col = "#F57C00"
                final_adv = f"• <b>[최종 결론]</b> <b>[이평선 꼬임 혼조세]</b> 단기·중기 이평선이 엉키며 방향성을 상실했으니 뇌동매매를 금하고 냉정하게 관망하시게."
            elif (current_chg < 0.0 or p < actual_open) and bias_ma5 < 0.0 and not strict_doji_check:
                final_code = "BEARISH_GUARD"
                if p < actual_open:
                    sig = f"🟡 [하락/조정] 음봉 압력 속 추세 이탈 경계"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 현재 시가({actual_open:{fmt_p}}{currency}) 아래로 밀리는 파란 음봉 하락 국면이오니, 헛된 기대를 버리고 성벽 및 5일선({ma5_val:{fmt_p}}{currency}) 회복 전까지 칼질 관망을 유지하시게."
                else:
                    sig = f"🟡 [하락/조정] 갭하락 반등 양봉이나 5일선 아래 경계"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> 장중 저점에서 반등하여 시가({actual_open:{fmt_p}}{currency}) 위로 빨간 양봉을 세웠으나, 아직 전일 대비 약세({current_chg:+.2f}%)이고 단기 생명선인 5일선({ma5_val:{fmt_p}}{currency}) 아래에 머물러 있소! 5일선 안착이 확인될 때까지 섣부른 진입을 금하고 관망을 유지하시게."
            elif is_ma5_safe and not is_bottom_indicator_ok and not is_down_trend_structural:
                if pullback_rebound_score >= 1:
                    final_code = "WAIT_INDICATOR"
                    sig = "🟡 [관망/보류] 지표 충족이나 볼린저 중심선/캔들 안전마진 부족"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> <b>[추세 불안정 관망]</b> 눌림목 점수({pullback_rebound_score}/3점)는 포착되었으나, 볼린저 20일 중심선 위 양봉 안전마진이 부족하거나 상단 과열권이라 추세적 진입 요건이 확보되지 않았소. 뇌동매매를 금하고 관망하시게."
                else:
                    final_code = "WAIT_INDICATOR"
                    sig = "🟡 [관망/보류] 5일선 안착했으나 지표/수급 미충족 (안착 대기)"
                    col = "#F57C00"
                    final_adv = f"• <b>[최종 결론]</b> <b>[매수 조건 미충족]</b> 5일선 위에 안착했으나 수급 불량 또는 눌림목 지지 동조 점수 부족({pullback_rebound_score}/3점)으로 안착 대기 중이므로 관망하시게."
            else:
                final_code = "WAIT_GENERAL"
                sig = "🟡 [관망] 조건 미충족 / 뇌동매매 금지"
                col = "#E68A00"
                if pullback_rebound_score >= 1 or bottom_score >= 1:
                    final_adv = f"• <b>[최종 결론]</b> 일부 바닥·눌림 지표({max(bottom_score, pullback_rebound_score)}/3점)는 반응했으나, 대세 역배열 저항 또는 추세 안전마진 미충족 상태이오! 섣부른 뇌동매매를 금하고 관망을 유지하시게."
                else:
                    final_adv = f"• <b>[최종 결론]</b> 추세·수급·지표의 핵심 타점 조건이 모두 미충족된 어정쩡한 자리이오! 총알을 아끼고 철저히 관망을 유지하시게."
            
            if is_memory_ignored and final_code in ["BOTTOM_ENTRY", "EXTREME_BOTTOM_ENTRY"]:
                final_adv += "<br><br>💡 <b style='color:#FFEB3B;'>[이수할아버지의 안내]</b> 기계의 기억상 최근 3일 내 바닥 신호가 있었소. 만약 당시 <b>이미 매수하셨다면</b> 상단 <b>[직전 1차 매수가]</b> 칸에 금액을 입력하시게! 그래야 중복 매수를 차단하거나 물타기 계산을 가동할 수 있소이다."
            
            if user_last_1st_price > 0 and final_code in ["BOTTOM_ENTRY", "EXTREME_BOTTOM_ENTRY"]:
                final_code = "WAIT_GENERAL"
                col = "#F57C00"
                sig = "🟡 [관망/보류] 기 매수자 추가 진입 금지 (대세 하락 방어 가동)"
                final_adv = "• <b>[최종 결론]</b> 당일 강력한 반등 기세가 보이나, 대세 하락장 역배열 방어 로직이 작동 중이오! 이미 물량을 보유한 [기 1단계 매수자]는 섣부른 물타기(추매)를 엄금하고, 5일선 완벽 안착 신호를 기다리며 얌전히 관망하시게."
            if "투매" in sig and (v_ratio < 15):
                final_code = "WAIT_GENERAL"
                col = "#F57C00"
                sig = "🟡 [관망/보류] 장 초반 시간보정 노이즈 (가짜 투매 방어)"
                final_adv = f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점)가 치솟았으나, 실시간 거래량이 {v_ratio:.1f}% 수준으로 씨가 마른 상태이오! 얇은 호가에 툭 던진 물량이 만든 '시간보정 착시 현상'일 뿐이니 붉은 경고에 쫄지 말고 차분히 관망하시게."

            # ==================================================================
            # ★ [신호등-행동강령 100% 동기화] 볼린저 위치에 양봉/음봉/윗꼬리(_c_short) 명시!
            # ==================================================================
            _arr_name = "대세 정배열" if is_bullish else ("대세 역배열" if is_bearish else "이평선 혼조세")
            _ma5_state = f"5일선 안착({bias_ma5:+.1f}%)" if is_ma5_safe else f"5일선 이탈({bias_ma5:+.1f}%)"
            _macd_short = "정회전 가속" if is_macd_accelerating else ("정회전 둔화" if is_macd_decelerating else ("역회전 감소" if is_macd_recovering else "역회전 심화"))
            _ob_short = f" · 호가잔량비 {ob_ratio_val:.2f}배" if ob_ratio_available else ""

            if bottom_score >= 1 and pullback_rebound_score == 0:
                _score_phrase = f"진바닥 지표({bottom_score}/3점 · RSI {rsi_val:.1f} · 볼린저위치 {bb_pct_b:.1f}%[{_c_short}])"
            elif pullback_rebound_score >= 1:
                _score_phrase = f"눌림목 지표({pullback_rebound_score}/3점 · RSI {rsi_val:.1f} · 볼린저위치 {bb_pct_b:.1f}%[{_c_short}])"
            else:
                _score_phrase = f"3대 지표(0/3점 · RSI {rsi_val:.1f} · 볼린저위치 {bb_pct_b:.1f}%[{_c_short}])"

            _holistic_prefix = (
                f"🔍 <b>[지표 판독 근거]</b> {regime_badge} | <b>{_arr_name}({_ma5_state})</b> 구도 속에 "
                f"거래량 화력(<b>{vol_strength:.1f}점·{v_status}</b>), {_score_phrase}, "
                f"엔진(<b>{_macd_short}</b>){_ob_short}"
            )
            _pure_body = final_adv.replace("• <b>[최종 결론]</b> ", "").replace("<b>[최종 결론]</b> ", "")
            signal_box_adv = (
                f"<div style='font-size: 1.08em; font-weight: bold; line-height: 1.5; margin-bottom: 10px;'>"
                f"💡 [핵심 지침] {_pure_body}</div>"
                f"<hr style='border: 0; border-top: 1px dashed rgba(255,255,255,0.45); margin: 8px 0;'>"
                f"<div style='font-size: 0.82em; opacity: 0.9; font-weight: normal; line-height: 1.4;'>"
                f"{_holistic_prefix}</div>"
            )

            if final_code in ["BOTTOM_ENTRY", "EXTREME_BOTTOM_ENTRY"]:
                action_command_msg = f"🎯 [최종 실전 행동 강령 · {market_regime}] 신규 진입자는 현재가 부근에서 비중 {stage1_alloc} 이내로 '1단계 정찰병'만 가볍게 투입하시게! (기 1단계 매수자는 중복 추매 금지 / 2단계 기준선 5일선 {ma5_val:{fmt_p}}{currency} 안착 확인 / 최후 손절선 {stop_loss_price:{fmt_p}}{currency} 엄수)"
            elif final_code == "DEEP_DISCOUNT_ENTRY":
                action_command_msg = f"🎯 [최종 실전 행동 강령 · {market_regime}] 직전 매수가 대비 -{drop_ratio:.1f}% 폭탄 세일 구간이오! 평단가를 낮추는 추가 1단계 물타기를 집행하되, 최후 방어선({stop_loss_price:{fmt_p}}{currency}) 이탈 시 칼손절 원칙을 지키시게."
            elif final_code == "ESCAPE_BUY":
                action_command_msg = f"🎯 [최종 실전 행동 강령 · {market_regime}] 단기 생명선인 5일선({ma5_val:{fmt_p}}{currency}) 양봉 안착이 확인되었소! 신규 및 1단계 소량 보유자는 총 비중 {stage2_alloc}까지 '2단계 증원 매수'를 집행하고, 이미 비중을 채운 보유자는 추매 없이 5일선 사수를 지켜보시게!"
            elif final_code == "BUY_MA20_BREAKOUT":
                action_command_msg = f"🎯 [최종 실전 행동 강령 · {market_regime}] {ma20_fail_days}일 만의 20일선({mid_line:{fmt_p}}{currency}) 첫 돌파가 확인되었소! 다만 역배열 저항 및 윗꼬리 매물 압력이 남아 있을 수 있으니, 신규 및 소량 보유자는 20일선 지지 안착 여부를 확인한 뒤 총 비중 {stage2_alloc} 한도 내에서 분할 진입을 검토하시고, 20일선 재이탈 시 즉시 보수 전환하시게!"
            elif final_code in ["PULLBACK_BUY", "BREAK_MA20_CONFIRMED", "NEW_HIGH_PULLBACK_BUY"]:
                action_command_msg = f"🎯 [최종 실전 행동 강령 · {market_regime}] 추세와 양봉 안전마진이 모두 검증된 핵심 승부처이오! 신규 및 1·2단계 소량 보유자는 총 비중 {stage3_alloc}까지 '3단계 본진'을 과감히 투입(증원)하고, 이미 목표 비중을 다 채운 기 보유자는 무리한 불타기 없이 수확 목표선({target_price_100:{fmt_p}}{currency})까지 5일선({ma5_val:{fmt_p}}{currency})을 타고 랠리를 즐기시게!"
            elif final_code == "SQUEEZE_BREAKOUT_ATTACK":
                action_command_msg = f"🎯 [최종 실전 행동 강령] 응축된 밴드가 양봉으로 폭발하는 대시세 초입이오! 신규 및 1·2단계 소량 보유자는 총 비중 50%까지 본진을 과감히 투입(증원)하고, 이미 비중을 다 채운 기 보유자는 평단가를 높이는 불타기 없이 5일선({ma5_val:{fmt_p}}{currency}) 이탈 전까지 랠리를 즐기시게!"
            elif final_code == "HIGH_PASS_OVEREXTENDED":
                action_command_msg = f"🎯 [최종 실전 행동 강령] 대량 거래가 폭발했으나 5일선 이격(+{bias_ma5:.1f}%)이 과도하게 벌어진 과열 불기둥이오! 신규 고점 추격 매수는 깊이 참고 자제하시고, 기 보유자 또한 급락에 대비해 보유 비중을 30% 이하로 조인 채 5일선({ma5_val:{fmt_p}}{currency}) 및 20일선({mid_line:{fmt_p}}{currency}) 사수 여부를 엄격히 감시하시게!"
            elif final_code == "BAND_RIDING_HARVEST":
                action_command_msg = f"🎯 [최종 실전 행동 강령] 목표선({target_price_100:{fmt_p}}{currency})을 뚫고 상방 밴드 라이딩 중이오! 고점 신규 추격 매수는 금하되, 기 보유자는 5일선({ma5_val:{fmt_p}}{currency}) 종가 이탈 전까지 수익을 끝까지 극대화하시게!"
            elif final_code == "BREAKOUT_ATTACK":
                action_command_msg = f"🎯 [최종 실전 행동 강령] 성벽({defense_line:{fmt_p}}{currency}) 위에서 양봉 기세를 유지하며 순항 중이오! 기 보유자는 5일선({ma5_val:{fmt_p}}{currency})을 생명선 삼아 상단 목표선({target_price_100:{fmt_p}}{currency})까지 추세를 끝까지 추종하시게! (신규 및 소량 보유자는 5일선 부근 눌림 시에만 분할 가담)"
            elif final_code == "DOJI_DRAGONFLY":
                action_command_msg = f"🎯 [최종 실전 행동 강령] 장중 투매를 싹쓸이한 잠자리형 도지로 강력한 하방 경직성이 확인되었소! 내일 시가 위 양봉 출발 및 5일선({ma5_val:{fmt_p}}{currency}) 돌파 확인 시 기민하게 분할 타진하시게!"
            elif final_code in ["RED_SELL_WARNING", "SELL_PROFIT_TAKE", "RED_SELL_TARGET", "DOJI_TOP_WARNING"]:
                action_command_msg = f"🎯 [최종 실전 행동 강령] 상단 과열 및 차익 매물 출회 경보가 켜졌소! 신규 매수는 절대 엄금하며, 보유자는 욕심을 버리고 즉시 보유 물량의 50% 이상을 선제 익절(수확)하여 현금을 챙기시게!"
            elif final_code == "STOP_LOSS_ALERT":
                action_command_msg = f"🎯 [최종 실전 행동 강령] 최후의 마지노선({stop_loss_price:{fmt_p}}{currency})이 무너진 비상사태이오! 희망 회로를 당장 멈추고 전량 시장가 칼손절로 계좌를 사수하시게!"
            else:
                if not is_ma5_safe:
                    _next_target_str = f"1차 관문인 단기 생명선 5일선({ma5_val:{fmt_p}}{currency}) 위로 붉은 양봉을 세우며 완전히 안착하는 날"
                elif is_over_extended_5:
                    _next_target_str = f"과도하게 벌어진 5일선({ma5_val:{fmt_p}}{currency})과의 이격(+{bias_ma5:.1f}%)이 좁혀지며 건전한 양봉 눌림목 지지가 확인되는 날"
                elif p < mid_line:
                    _next_target_str = f"볼린저 20일 중심선({mid_line:{fmt_p}}{currency})을 양봉으로 돌파하여 안전마진을 확보하는 날"
                elif p < defense_line:
                    _next_target_str = f"머리 위 역배열 저항 및 최후 성벽({defense_line:{fmt_p}}{currency})을 거래량 실린 양봉으로 돌파하거나 역배열이 해소되는 날"
                else:
                    _next_target_str = f"음봉·윗꼬리 매물 소화 및 양봉 지지·호가창 동조가 완벽히 확인되는 날"
                action_command_msg = f"🎯 [최종 실전 행동 강령] 신규 진입 및 무리한 추매 전면 금지! 성급한 입질을 멈추고 주가가 {_next_target_str}까지 현금을 100% 사수하며 대기하시게! (기 보유자는 손절 마지노선 {stop_loss_price:{fmt_p}}{currency} 이탈 여부만 철저히 감시할 것)"

            st.markdown(
                f"<div class='signal-box' style='background-color: {col};'>"
                f"<div class='signal-text'>{sig}</div>"
                f"<div class='signal-subtext'>{signal_box_adv}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            is_overall_cautious_state = final_code in [
                "WAIT_MA20_RESIST", "WAIT_MA20_BREAK_TRY", "WAIT_MA20_BREAK_OVEREXT",
                "WAIT_GENERAL", "WAIT_INDICATOR", "WAIT_MACD", "WAIT_VOLUME",
                "WAIT_DOWNTREND_FALL", "WAIT_PULLBACK_CANDLE", "WAIT_PULLBACK",
                "WAIT_ORDERBOOK", "WAIT_OVER_EXTENDED", "HIGH_PASS_OVEREXTENDED", "NEW_HIGH_BREAKOUT_WARNING",
                "YELLOW_CAUTION", "RED_SELL_WARNING", "MA_TANGLED_WARNING", "LONG_TAIL_WARNING", "BEARISH_GUARD", "WAIT_NARROW_MARGIN",
                "DOJI_TOP_WARNING", "DOJI_BOTTOM_WAIT", "DOJI_MID_WAIT", "WAIT_COOL_TIME"
            ]

            if final_code == "SQUEEZE_BREAKOUT_ATTACK": sub_indicator_str = f"   - <b>스퀴즈 돌파 성공:</b> 20일선({mid_line:{fmt_p}}{currency}) 상방 폭발 -> <b>[매수 유효]</b> 신규 및 소량 보유자 본진 타진 진행"
            elif final_code == "HIGH_PASS_OVEREXTENDED": sub_indicator_str = f"   - <b>대량거래 불기둥 과다이격:</b> 5일선 이격 과다(+{bias_ma5:.1f}%) -> <b>[추격 자제]</b> 고점 추격 매수 엄금 및 비중 30% 이하 관리"
            elif final_code == "NEW_HIGH_PULLBACK_BUY": sub_indicator_str = f"   - <b>신고가 지지 성공:</b> 5일선({ma5_val:{fmt_p}}{currency}) 안착 확인 완료 -> <b>[매수 유효]</b> 신규 및 소량 보유자 본진 타진 진행"
            elif final_code == "NEW_HIGH_BREAKOUT_WARNING": sub_indicator_str = f"   - <b>신고가 돌파 주의:</b> 5일선 이격 과다(과열) -> <b>[관망]</b> 5일선 눌림목까지 추격 매수 차단"
            elif final_code == "BREAK_MA20_CONFIRMED": sub_indicator_str = f"   - <b>돌파 타진 성공:</b> 20일선({mid_line:{fmt_p}}{currency}) 안착 확인 완료 -> <b>[매수 유효]</b> 기민한 분할 타진 진행"
            elif final_code == "ESCAPE_BUY": sub_indicator_str = f"   - <b>진바닥 탈출 성공:</b> 5일선({ma5_val:{fmt_p}}{currency}) 안착 유지 -> <b>[매수 유효]</b> 2단계 분할 진격 타점 가동"
            elif final_code in ["BOTTOM_ENTRY", "EXTREME_BOTTOM_ENTRY"]:
                if p < (ma5_val * 0.97):
                    sub_indicator_str = f"  - <b style='color:#D32F2F;'>🚨 [절대 관망령] 데드캣 바운스 경고:</b> 바닥 지표({bottom_score}점) 포착! 허나 5일선 아래 까마득..."
                elif is_candle_bearish and not is_extreme_lower_tail:
                    sub_indicator_str = f"  - <b style='color:#D32F2F;'>⏳ [진바닥 음봉 대기]:</b> 바닥 지표({bottom_score}점) 포착되었으나 파란색 음봉 압력 중! 양봉 전환 및 지지 확인 전까지 입질 대기"
                else:
                    _ma5_note = "5일선 근접 하회·바닥 방어" if p < ma5_val else "건전한 5일선 눌림목"
                    sub_indicator_str = f"  - <b style='color:#1976D2;'>✅ [정상 진바닥 동조]:</b> 바닥 지표({bottom_score}점) 포착 완료 ({_ma5_note}) -> <b>[매수 유효]</b> 계획된 1단계 선발대 투입 가동"
            elif final_code == "DEEP_DISCOUNT_ENTRY": 
                sub_indicator_str = f"   - <b>가격 메리트 동조:</b> 직전 매수가 대비 -{drop_ratio:.1f}% 하락 -> <b>[추가 진입 유효]</b> 하이패스 물타기 타점 가동"
            elif final_code == "PULLBACK_BUY": sub_indicator_str = f"   - <b>눌림목 지지 성공:</b> 볼린저 중심선 위 양봉 안전마진 확보 완료 -> <b>[매수 유효]</b> 3단계 본진 진격 타점 가동"
            else:
                if final_code == "BEARISH_GUARD" and is_massive_dump: _p_action = f"-> <b>[투매 관망]</b> 칼날이 떨어지고 있으니 절대 매수 금지"
                elif final_code == "BEARISH_GUARD": _p_action = f"-> <b>[하락 이탈 관망]</b> 지표 점수와 무관하게 음봉 추세가 꺾여 매수 보류"
                elif final_code == "WAIT_NARROW_MARGIN": _p_action = f"-> <b>[수익비 불량 관망]</b> 상승 여력이 좁아 차단됨"
                elif final_code == "WAIT_ORDERBOOK": _p_action = f"-> <b>[호가창 미달 관망]</b> 허매수/속임수 경계"
                elif final_code == "WAIT_COOL_TIME": _p_action = f"-> <b>[중복 노이즈 관망]</b> 쿨타임 가동으로 중복 매수 차단"
                elif final_code in ["DOJI_TOP_WARNING", "DOJI_BOTTOM_WAIT", "DOJI_MID_WAIT"]: _p_action = f"-> <b>[십자형 변곡 대기]</b> 내일 상하방 이탈 방향을 확인하라"
                elif p < ma5_val and p_chg > 0 and not is_candle_bearish:
                    if p < (ma5_val * 0.97):
                        _p_action = f"-> <b><span style='color:#D32F2F;'>[가짜 반등 주의]</span></b> 붉은 양봉이 출현하여 반등을 시도하나, 5일선 저항이 까마득하여 첩첩산중이오! (데드캣 경계)"
                    else:
                        _p_action = f"-> <b>[5일선 탈환 시도]</b> 지표는 포착되었으며 양봉으로 5일선 고지를 향해 맹렬히 진격 중! (돌파/안착 대기)"
                elif p < ma5_val and (p_chg <= 0 or is_candle_bearish):
                    _p_action = f"-> <b>[추세 꺾임 관망]</b> 지표는 포착되었으나 5일선 아래 음봉/저항 구역이므로 진입 금지"
                elif is_down_trend_structural and not is_ma20_breakout_real:
                    if p >= mid_line:
                        _p_action = f"-> <b>[역배열 저항 관망]</b> 20일선은 넘었으나 상위 이평선(60·120일) 역배열 저항 구역이므로 섣부른 진입 보류"
                    else:
                        _p_action = f"-> <b>[역배열 저항 관망]</b> 20일선({mid_line:{fmt_p}}{currency}) 아래 대세 역배열 저항 구역이므로 섣부른 진입 보류"
                elif pullback_rebound_score >= 2: _p_action = f"-> <b>[눌림목 공방 유효]</b> 중간지대 조건 충족!"
                elif pullback_rebound_score == 1: _p_action = f"-> <b>[입질 대기]</b> 눌림목 지표 1개 포착"
                elif bottom_score >= 1: _p_action = f"-> <b>[바닥 포착/대기]</b> 바닥 지표는 켜졌으나 제반 조건 미달"
                else: _p_action = f"-> <b>[관망]</b> 지표 동조 미충족으로 안착 대기"

                _display_score = pullback_rebound_score if pullback_rebound_score >= 1 else bottom_score
                _score_name = "눌림목" if pullback_rebound_score >= 1 else ("진바닥" if bottom_score >= 1 else "전환")
                sub_indicator_str = f" - <b>{_score_name} 동조:</b> {_display_score}/3점 (밴드폭 {bandwidth:.1f}% / 위치 {bb_pct_b:.1f}%[{_c_short}]) {_p_action}"

            bottom_score_display = f"<b>{bottom_score}점</b> <span style='color:#E65100;'>(최근 3일 바닥 터치 인정)</span>" if (bottom_score == 0 and recent_bottom_memory) else f"<b>{bottom_score}점</b> (기준 1점)"
            
            # ==================================================================
            # 🚨 [핵심 교정] 추세 정밀 판독: 윗꼬리가 달린 양봉 저항 판별
            # ==================================================================
            if is_candle_unknown:
                pass  
            elif strict_doji_check:
                trend_status = f"⚖️ <b style='color:#F57C00;'>[십자 도지(Doji)형 변곡점]</b> 매수세와 매도세가 팽팽하게 맞서며 시가와 종가가 거의 같은 십자형 캔들을 만들었소! 내일 방향(상승/하락)이 결정될 때까지 당일 진입은 철저히 관망하시게."
            elif is_defended:
                has_meaningful_lower_tail = (lower_tail_len >= body_len * 0.3) or (lower_tail_len >= day_candle_range * 0.2)
                
                if is_long_upper_tail:
                    if p >= today_open:
                        trend_status = f"⚠️ <b style='color:#F57C00;'>[장대 위꼬리 매물 폭탄 / 시가 턱걸이 버팀]</b> 시가({today_open:{fmt_p}}{currency}) 위로 고점({today_high:{fmt_p}}{currency})까지 솟구쳤으나 상단 매물 폭탄을 맞고 크게 밀려 내려와, 현재가({p:{fmt_p}}{currency})가 겨우 양봉 몸통을 유지 중이오! 방심 금지."
                    else:
                        trend_status = f"⚠️ <b style='color:#F57C00;'>[장대 위꼬리 매물 폭탄 / 시가 붕괴]</b> 장중 고점({today_high:{fmt_p}}{currency})까지 강하게 솟구쳤으나 상단 매물 폭탄을 맞고 밀려 내려와, 현재가({p:{fmt_p}}{currency})가 시가({today_open:{fmt_p}}{currency}) 아래로 처박혔소! 섣부른 진입 금지."
                elif has_upper_tail_resist and is_candle_bullish:
                    if has_meaningful_lower_tail:
                        trend_status = f"⚠️ <b style='color:#E65100;'>[위·아래꼬리 공방 속 양봉 안착]</b> 장중 저점({today_low:{fmt_p}}{currency})에서 반등하여 {candle_color_txt}을 세웠으나, 당일 고점({today_high:{fmt_p}}{currency}) 상단 매물 저항에 부딪혀 윗꼬리(진폭의 {upper_tail_pct_of_range:.0f}%)를 달고 일부 밀려 내려왔소! 상단 저항을 의식하며 대응하시게."
                    else:
                        trend_status = f"⚠️ <b style='color:#E65100;'>[양봉 상승 속 윗꼬리 매물 출회]</b> 시가({today_open:{fmt_p}}{currency})에서 밀리지 않고 고점({today_high:{fmt_p}}{currency})까지 치솟았으나, 상단 매물벽 저항을 맞고 <b>윗꼬리(진폭의 {upper_tail_pct_of_range:.0f}%)를 달며 현재가({p:{fmt_p}}{currency}, {p_chg:+.2f}%)로 일부 밀려 내려온 {candle_color_txt}</b>이오! 무조건적인 맹공이 아니니 상단 매물 소화를 확인하시게."
                elif is_strong_bull_body and not has_meaningful_lower_tail and p_chg > 0:
                    if today_open == today_low and upper_tail_len <= day_candle_range * 0.15:
                        trend_status = f"🔥 <b style='color:#D84315;'>[강한 매수세 맹공 (꽉 찬 양봉)]</b> 시가({today_open:{fmt_p}}{currency})부터 아래꼬리와 윗꼬리 저항을 거의 허용하지 않고 고점 부근({p:{fmt_p}}{currency}, {p_chg:+.2f}%)까지 꽉 채워 밀어 올린 강력한 {candle_color_txt} 출현!"
                    else:
                        trend_status = f"📈 <b style='color:#388E3C;'>[견고한 매수세 유입]</b> 상단 윗꼬리 저항을 이겨내고 든든한 몸통의 {candle_color_txt}을 기록 중이오."
                elif p_chg < 0:
                    if is_long_lower_tail:
                        trend_status = f"📉 <b style='color:#F57C00;'>[하락 속 밑꼬리 반발]</b> 전일 대비 하락(-{abs(p_chg):.2f}%) 중이나, 밑꼬리를 전체 길이의 50% 이상 길게 달며 반발 매수세가 들어왔소! 허나 아직 완벽한 양봉 전환이 아니니, 내일 확실한 지지를 눈으로 확인하기 전까지는 섣부른 줍줍을 금하시게."
                    elif not is_candle_bearish:
                        trend_status = f"📉 <b style='color:#F57C00;'>[갭하락 반발 매수 / 경계 유지]</b> 전일 대비 하락(-{abs(p_chg):.2f}%) 구간이나, 저가 반발 매수세가 유입되며 양봉으로 버티고 있소. 다만 대세 하락 압력이 남아 있으니 성급한 추격은 경계하시게."
                    else:
                        trend_status = f"📉 <b style='color:#D32F2F;'>[추세 맹폭 / 방어선 붕괴]</b> 전일 대비 하락(-{abs(p_chg):.2f}%) 중이며, 매수세의 저항 한 번 제대로 못 해보고 속절없이 쏟아지고 있소! 절대 칼날을 잡지 마시게."
                else:
                    if today_open == today_low and not has_upper_tail_resist:
                        trend_status = f"🔥 <b style='color:#D84315;'>[강한 매수세 맹공]</b> 장 시작부터 밀리지 않고 위로 뻗어가는 {candle_color_txt} 출현!"
                    elif has_meaningful_lower_tail and (lower_tail_len > upper_tail_len) and (today_open > today_low):
                        trend_status = f"🛡️ <b>[방어선 구축 / 아래꼬리 지지 확인]</b> 하락 수압을 이겨내고 아래꼬리가 달린 {candle_color_txt} 출현!"
                    elif (is_long_upper_tail or has_upper_tail_resist) and is_candle_bearish:
                        trend_status = f"🚨 <b>[상승 기세 꺾임 / 윗꼬리 음봉 압박]</b> 고점({today_high:{fmt_p}}{currency})에서 윗꼬리를 달고 시가 아래로 밀려 내려온 {candle_color_txt} 출현! 상단 저항이 거세오."
                    elif is_candle_bearish:
                        trend_status = f"📉 <b>[단기 하락 / 매도 우위]</b> 매물 압박을 받으며 밀려 내려온 {candle_color_txt} 출현!"
                    else:
                        trend_status = f"🌱 <b>[방어선 구축 / 상승 전개]</b> 매수세가 유입되며 견고한 {candle_color_txt} 출현!"
            elif is_long_upper_tail:
                if is_candle_bearish: 
                    if p >= ma5_val:
                        trend_status = f"⚠️ <b style='color:#F57C00;'>[장중 차익 매물 출회 / 5일선 사수]</b> 시가에서부터 파란 음봉으로 쫙 밀리며 매물이 쏟아지고 있으나, 단기 생명선(5일선)은 아직 지켜내고 있소. 섣부른 추격은 금하되 지지 여부를 끝까지 확인하시게."
                    else:
                        trend_status = f"🚨 <b style='color:#D32F2F;'>[상승 기세 꺾임 / 하방 투매 거셈]</b> 시가에서부터 파란 음봉으로 강하게 밀리며 단기 생명선인 5일선마저 무참히 붕괴되었소! 상승 시도마다 매물 폭탄을 맞고 있으니 즉각 관망 모드로 전환하시게."
                else: 
                    if p >= ma5_val:
                        trend_status = f"⚠️ <b style='color:#F57C00;'>[고점 매물 저항 / 5일선 사수]</b> 윗꼬리를 길게 달았으나 단기 생명선(5일선)은 아직 지켜내고 있소. 섣부른 추격은 금하되 보수적으로 대응하시게."
                    else:
                        trend_status = f"🚨 <b style='color:#D32F2F;'>[상승 기세 꺾임 / 하방 압력 거셈]</b> 윗꼬리를 길게 달고 하방 압력이 거세어 단기 생명선인 5일선마저 붕괴되었소! 즉각 관망 모드로 전환하시게."
            elif final_code in ["RED_SELL_WARNING", "SELL_PROFIT_TAKE", "LONG_TAIL_WARNING", "STOP_LOSS_ALERT"]:
                if p < ma5_val:
                    trend_status = (
                        "🚨 <b style='color:#D32F2F;'>[상승 기세 꺾임 / 5일선 붕괴]</b> 이평선 배열상으론 반등 초입처럼 보이나, "
                        "이미 매물 폭탄을 맞고 5일선 생명선 밑으로 완전히 처박혔네! 섣부른 희망 회로를 당장 찢어버리고 미련 없이 탈출하시게."
                    )
                else:
                    trend_status = (
                        "🚨 <b style='color:#D32F2F;'>[상승 기세 꺾임 / 5일선 위태]</b> 이평선 배열상으론 반등 초입처럼 보이나, "
                        "당일 하방 압력이 거세져 5일선 생명선이 붕괴될 위기요! 섣부른 희망 회로를 접고 즉각 관망 모드로 전환하시게."
                    )

            indicator_verify_text = (
                f"{ma_price_summary}<br>• <b>[추세 정밀 판독]:</b><br> {trend_status}<br>• <b>[지표 검증 연산]</b><br>"
                f"<div style='padding-left: 20px;'>"
                f"• <b>[진바닥 점수]:</b> {bottom_score_display} | • <b>[눌림목 점수]:</b> <b>{pullback_rebound_score}점</b> (기준 1점)<br>"
                f"{sub_indicator_str}{squeeze_info_str}"
                f"</div>"
            )
            if final_code == "EXTREME_BOTTOM_ENTRY": indicator_verify_text += "<br>⚠️ <span style='color:red;'><b>[이평선 꼬임/하락 속 극한 바닥 1단계 입질 예외 가동]</b></span>"
            if final_code == "DEEP_DISCOUNT_ENTRY": indicator_verify_text += "<br>⚠️ <span style='color:blue;'><b>[직전 매수가 대비 5% 이상 하락 속 물타기 예외 가동]</b></span>"

            ma5_dynamic_stop = dynamic_stop_price

            if p >= target_price_100:
                if user_avg_price > 0:
                    profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                    holder_guide_msg = f"• <b>[상방 확장 대시세 구역 (수익률: {profit_rate:+.2f}%)]</b><br>• <b>실전 행동:</b> 신규 매수 금지!<br>• <b>잔여 물량 홀딩 기준:</b> 5일선({ma5_val:{fmt_p}}{currency}) 종가 사수 시 잔여 물량 랠리 추종.<br>• <b>최종 청산선:</b> 5일선 -{dynamic_stop_pct:.1f}% 이탈({ma5_dynamic_stop:{fmt_p}}{currency}) 시 전량 청산."
                else: holder_guide_msg = "• <b>[상방 확장 대시세 구역]</b><br>• <b>실전 행동:</b> 목표선을 뚫고 상단 밴드가 열리고 있으나 신규 진입은 금물이오! 보유자는 5일선 기준으로 끝까지 랠리를 추종하시게."
            elif p >= (target_price_100 * 0.98) or bb_pct_b >= 92.0:
                if user_avg_price > 0:
                    profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                    holder_guide_msg = f"• <b>[수확 목표선 임박 (수익률: {profit_rate:+.2f}%)]</b><br>• <b>실전 행동:</b> 신규 진입 절대 금지! 욕심을 덜고 1차 분할 수확 준비.<br>• <b>잔여 물량:</b> 성벽({defense_line:{fmt_p}}{currency})이나 5일선 이탈 시 전량 정리."
                else: holder_guide_msg = "• <b>[수확 목표선 임박 구역]</b><br>• <b>실전 행동:</b> 볼린저 상단 고지가 코앞이니 매수 엄금, 보유자는 1차 선제적 익절(수확) 준비."
            elif is_stop_loss_triggered:
                holder_guide_msg = f"🚨 <b style='color:#D32F2F;'>[비상 대피령 (손절선 붕괴)]</b><br>• <b>실전 행동:</b> 바닥권 전저점 방어선({stop_loss_price:{fmt_p}}{currency})이 무참히 뚫렸소!<br>• <b>잔여 물량:</b> 희망 회로를 찢어버리고 즉시 전량 칼손절 후퇴하시게."
            elif user_avg_price <= 0:
                holder_guide_msg = f"현재 추세 탐색 및 방향 정립 구간이니 성벽({defense_line:{fmt_p}}{currency})이나 5일선 사수 여부를 확인하시게. (★ <b>손절 마지노선: {stop_loss_label}</b>)"
            else:
                profit_rate = ((p - user_avg_price) / user_avg_price) * 100
                if p >= user_avg_price:
                    holder_guide_msg = f" • <b>[수익권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} / 수익률: +{profit_rate:.2f}%)]</b><br> • <b>기세 지속:</b> 5일선({ma5_val:{fmt_p}}{currency})을 이탈하지 않는 한 추세를 즐기시게.<br> • <b>수익 확정선:</b> 성벽 위 음봉 발생 또는 볼린저 상단 도달 시 분할 매도 집행."
                else:
                    holder_guide_msg = f" • <b>[손실권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} / 손실률: {profit_rate:.2f}%)]</b><br> • <b>단기 생명선:</b> 5일선 지지 확인.<br> • <b>최후 방어선:</b> 바닥권 전저점({stop_loss_price:{fmt_p}}{currency}) 이탈 시 미련 없이 전량 칼손절 후퇴."

            if is_peak_dumping: 
                ma5_guide_text = f"🚨 <b>[비상 탈출] 고점 윗꼬리 투매 발생!</b> 상단에서 대량 차익 매물이 쏟아지고 있소. 5일선({ma5_val:{fmt_p}}{currency}) 믿고 버티다간 다 토해내니 <b>즉시 전량 익절</b>하시게!"
            elif final_code == "DEEP_DISCOUNT_ENTRY":
                ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선 아래에 있으나, 직전 매수가 대비 확실한 가격 할인 구간이라 과감한 추가 매수 타점이오!"
            elif final_code == "WAIT_COOL_TIME":
                ma5_guide_text = f"현재가({p:{fmt_p}}{currency}) 부근에서 최근 이미 1차 깃발이 꽂혔으므로 중복 노이즈를 막기 위해 5일선 안착 전까지 관망 중이오."
            elif final_code == "DOJI_TOP_WARNING":
                ma5_guide_text = f"⚠️ <b>[고점 상투 십자성]</b> 상승 에너지가 멈추고 십자성(Doji)이 떴소! 5일선 지지를 맹신하지 말고 언제든 던질 채비를 하시게."
            elif final_code == "LONG_TAIL_WARNING":
                if p >= ma5_val:
                    ma5_guide_text = f"⚠️ <b>[고점 매물 저항]</b> 현재가({p:{fmt_p}}{currency}) 위로 긴 꼬리가 생겼소! 5일선({ma5_val:{fmt_p}}{currency}) 위를 간신히 지키고 있으나 위꼬 매물이 무거우니 주의하시게."
                elif p >= today_open:
                    ma5_guide_text = f"⚠️ <b>[고점 매물 저항]</b> 현재가({p:{fmt_p}}{currency})가 5일선 아래에 있으나 시가 대비 양봉으로 버티고 있소. 5일선 탈환 여부를 주시하시게."
                else:
                    ma5_guide_text = f"🚨 <b>[생명선 이탈/매물 폭탄]</b> 현재가({p:{fmt_p}}{currency}) 위로 긴 꼬리가 생기며 5일선({ma5_val:{fmt_p}}{currency}) 아래로 완전히 미끄러졌소. 비중을 줄이고 리스크를 관리하시게."
            elif final_code == "NEW_HIGH_BREAKOUT_WARNING":
                ma5_guide_text = f"🚨 <b>[신고가 불기둥 뇌동매매 차단]</b> 현재가({p:{fmt_p}}{currency})가 1년 최고점을 뚫었으나 5일선과의 이격이 과도하오! 추격을 멈추고 관망하시게."
            elif final_code == "NEW_HIGH_PULLBACK_BUY":
                ma5_guide_text = f"🟢 <b>[신고가 눌림목 사수]</b> 현재가({p:{fmt_p}}{currency})가 신고가 달성 후 5일선에 완벽히 안착했소! 단기 생명선이 살아있네."
            elif final_code == "SQUEEZE_BREAKOUT_ATTACK":
                ma5_guide_text = f"🔥 <b>[스퀴즈 폭발]</b> 현재가({p:{fmt_p}}{currency})가 응축된 밴드를 찢고 20일선 위로 폭발했소! 5일선을 든든한 등대 삼아 진격하시게."
            elif final_code == "HIGH_PASS_OVEREXTENDED":
                ma5_guide_text = f"⚠️ <b>[과다이격 불기둥 경계]</b> 현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 대비 +{bias_ma5:.1f}%나 높게 솟구쳤소! 추격 매수를 자제하고 5일선과의 이격 축소를 확인하시게."
            elif p >= target_price_100: 
                ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 볼린저 상단을 뚫고 상방 확장 중이오! 남은 물량은 <b>5일선({ma5_val:{fmt_p}}{currency}) 종가 이탈 전까지</b> 끝까지 추종하시게."
            elif p >= (target_price_100 * 0.98) or bb_pct_b >= 92.0: 
                ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 있으나 수확 목표선 임박 구간이므로 5일선 -{dynamic_stop_pct:.1f}% 이탈({ma5_dynamic_stop:{fmt_p}}{currency})을 잔여 물량 방어선으로 엄수하시게."
            elif final_code in ["BOTTOM_ENTRY", "EXTREME_BOTTOM_ENTRY"]:
                if p >= ma5_val:
                    ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위로 올라서며 1단계 진바닥 입질 및 방어선을 확고하게 굳혔소!"
                else:
                    ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 아래에 있으나 바닥 방어 지표가 확고하여 1단계 입질 타점을 형성 중이오."
            elif is_massive_dump:
                if p >= ma5_val:
                    ma5_guide_text = f"🚨 <b>[대량 투매 발생]</b> 현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에서 아슬아슬하게 버티고 있으나 대량 매물이 쏟아지고 있소! 절대 칼날을 잡지 마시게."
                else:
                    ma5_guide_text = f"🚨 <b>[투매/칼날 발생]</b> 현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 아래로 이탈하며 대량 매물이 쏟아지고 있소! 절대 칼날을 잡지 마시게."
            elif not is_ma5_safe: 
                ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 아래로 이탈했으니, 돌파 안착 신호가 확인될 때까지 관망하시게."
            else:
                if is_pre_market_mode: ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 있소! 정규장 개장 후 지지 사수를 확인하시게."
                elif vol_strength < 65: ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착했으나 수급이 마른 상태이오. 추격을 금하고 관망하시게."
                elif final_code == "DOJI_MID_WAIT": ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착해 있으나, 십자 공방전 중이오. 내일 십자 고가 돌파(안착 확정)를 기다리시게."
                elif p < today_open and p_chg < 0: 
                    ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착해 있으나, 시가 대비 파란 음봉으로 밀리며 조정 중이오. 5일선 지지 사수 확인 후 대응하시게."
                elif p_chg < 0: ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착해 있으나, 전일 대비 하락 속 붉은 양봉 형태로 방어하고 있소. 5일선 지지 사수 확인 후 대응하시게."
                elif is_down_trend_v: ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착해 상승 중이나, 단기 추세가 하방 압력을 받으며 조정 중이오. 5일선 지지 사수 확인 후 대응하시게."
                elif final_code == "WAIT_NARROW_MARGIN": ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착했으나, 상승 여력이 너무 좁아 뇌동매매를 강제 차단 중이오."
                elif final_code == "WAIT_ORDERBOOK": ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착했으나, 호가창 매도잔량비가 미달하여 속임수 경계 중이오."
                elif final_code == "WAIT_INDICATOR":
                    if pullback_rebound_score >= 1: ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 있고 지표는 충족되었으나, 안전마진 확보 전까지 추격 매수를 차단 중이오."
                    else: ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착했으나 수급 및 지표 미달로 진입 대기 중이오."
                elif final_code == "ESCAPE_BUY": ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착하며 2단계 진바닥 탈출 성공! 타점 유효 구역이오."
                elif final_code == "PULLBACK_BUY": ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착하여 3단계 눌림목 전투선이 살아있네."
                elif final_code == "BREAK_MA20_CONFIRMED": ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 20일선 및 5일선 위 안착에 성공하며 기민한 돌파 매수 타점을 형성 중이오."
                else: ma5_guide_text = f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에 안착하여 단기 전투선 유지 중이오."

            if is_peak_dumping: 
                def_status = f"🚨 <b>[고점 폭탄 투하]</b> 성벽({defense_line:{fmt_p}}{currency})은 뚫었으나 대량 매도 폭탄이 떨어졌소! 상방 랠리가 취소되었으니 당장 도망치시게."
            elif final_code == "LONG_TAIL_WARNING":
                def_status = f"⚠️ <b>[성벽 위 가짜 돌파 경계]</b> 성벽({defense_line:{fmt_p}}{currency}) 위에서 긴 윗꼬리가 달렸소. 저항이 거세니 돌파를 맹신하지 마시게."
            elif final_code == "DOJI_TOP_WARNING":
                def_status = f"⚠️ <b>[성벽 위 상투 경계]</b> 성벽({defense_line:{fmt_p}}{currency})은 뚫었으나 십자 캔들이 뜨며 진격 에너지가 고갈되었소. 매수 금지!"
            elif final_code == "NEW_HIGH_BREAKOUT_WARNING":
                def_status = f"🚨 <b>[신고가 성벽 돌파]</b> 1년 최고점({high_250:{fmt_p}}{currency}) 성벽을 뚫어냈으나 과열 상태이오! 흥분하지 말고 차분히 관망하시게."
            elif final_code == "NEW_HIGH_PULLBACK_BUY":
                def_status = f"🔵 <b>[신고가 성벽 안착]</b> 이전 성벽들이 모두 발아래로 깔려 완벽한 활주로가 열렸소! 든든하게 진격하시게."
            elif final_code == "SQUEEZE_BREAKOUT_ATTACK":
                def_status = f"🔥 <b>[상방 밸브 폭발]</b> 20일선({ma20_safe_threshold:{fmt_p}}{currency})을 시원하게 뚫었으니, 머리 위 얇은 성벽은 거칠 것이 없소!"
            elif final_code == "HIGH_PASS_OVEREXTENDED":
                if p >= defense_line:
                    def_status = f"⚠️ <b>[성벽 돌파 및 과다이격]</b> 성벽({defense_line:{fmt_p}}{currency})을 뚫어냈으나 단기 급등으로 이격이 과도하오! 추격 매수를 멈추고 성벽 지지 여부를 확인하시게."
                else:
                    def_status = f"⚠️ <b>[성벽 아래 과다이격 급등]</b> 20일선은 넘었으나 아직 상단 성벽({defense_line:{fmt_p}}{currency}) 아래에서 단기 과열되었소! 추격 매수를 자제하시게."
            elif p >= target_price_100: 
                def_status = f"성벽({defense_line:{fmt_p}}{currency})을 가뿐히 넘고 볼린저 상단 목표선까지 뚫어냈네! 든든한 방어선을 뒤에 두고 상방 랠리를 끝까지 즐기시게."
            elif p >= (target_price_100 * 0.98) or bb_pct_b >= 92.0: 
                def_status = f"성벽({defense_line:{fmt_p}}{currency}) 위 진격은 완수되었네! 수확 목표선({target_price_100:{fmt_p}}{currency}) 고지가 코앞이니 현금을 챙길 준비를 하시게."
            elif defense_line > target_price_100: 
                if final_code in ["BREAK_MA20_CONFIRMED", "PULLBACK_BUY", "ESCAPE_BUY", "BOTTOM_ENTRY", "EXTREME_BOTTOM_ENTRY"]:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency})이 상단 목표선({target_price_100:{fmt_p}}{currency})보다 위로 왜곡된 <b>[역배열 매물 소화 구간]</b>이오! 풀매수는 절대 금하되, 5일선 방어를 전제로 가벼운 분할 입질(정찰병)로만 유연하게 대응하시게."
                else:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency})이 상단 목표선({target_price_100:{fmt_p}}{currency})보다 위로 왜곡된 <b>[역배열 침체]</b> 구역이오! 섣부른 진격을 금하고 철저히 관망하시게."
            elif p >= defense_line:
                if p < ma5_val:
                    def_status = f"🚨 성벽({defense_line:{fmt_p}}{currency}) 위에는 간신히 턱걸이하고 있으나, <b>5일선 생명선이 무너져 하방 폭격을 맞는 중</b>이네! 섣부른 희망 회로를 접고 성벽 붕괴 여부를 뼈저리게 감시하시게."
                elif is_candle_bearish:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 위 안착 중이나 당일 <b>음봉으로 밀려 가짜 돌파(페이크) 리스크</b>가 있소! 즉시 수성 태세로 전환하시게."
                elif final_code == "WAIT_NARROW_MARGIN":
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 위에서 진격 타점을 잡았으나, <b>상단 목표선까지 먹을 게 {margin_diff:.1f}%밖에 없어</b> 진입을 강제 차단했소."
                else:
                    def_status = f"성벽({defense_line:{fmt_p}}{currency}) 위에서 {candle_color_txt} 기세를 타고 <b>상방 랠리 진격 중</b>이네! 방어선을 등지고 추세를 즐기시게."
            else:
                if is_massive_dump: def_status = f"🚨 성벽({defense_line:{fmt_p}}{currency}) 아래로 <b>대량 투매 폭탄</b>이 떨어지며 붕괴 중이오! 미련을 버리고 대피하시게."
                elif final_code == "DOJI_BOTTOM_WAIT": def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래 지하실에서 <b>십자 도지 방어선</b>이 쳐졌소! 내일 고가 돌파 시 진격할 채비를 하시게."
                elif final_code == "WAIT_NARROW_MARGIN": def_status = f"성벽({defense_line:{fmt_p}}{currency}) 공방 중 타점이 나왔으나, <b>상단 목표선까지 먹을 게 {margin_diff:.1f}%뿐이라</b> 진입을 강제 차단했소."
                elif final_code == "WAIT_ORDERBOOK": def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래에서 호가창 기준 미달(허매수 의심)로 돌파 진입을 강제 보류 중이오."
                elif final_code == "BREAK_MA20_CONFIRMED": def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래이나 <b>20일선 돌파 안착</b>에 성공하여 기민한 타점을 형성 중이네!"
                elif final_code == "WAIT_INDICATOR" and pullback_rebound_score >= 1: def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래에서 지표는 충족했으나, 안전마진 미달로 기민하게 대기 중이오."
                elif final_code in ["BOTTOM_ENTRY", "EXTREME_BOTTOM_ENTRY", "DEEP_DISCOUNT_ENTRY", "WAIT_COOL_TIME"]: def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래이나 진바닥 공방 구역으로 <b>수급 유입/물타기 타점</b>을 형성 중이네!"
                elif not is_ma5_safe: def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래로 함락된 채 <b>단기 생명선(5일선) 이탈</b> 상태이오! 회복 전까지 섣부른 진격을 금하시게."
                elif final_code == "ESCAPE_BUY": def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래이나 5일선을 딛고 <b>2단계 바닥 탈출 진격</b>을 시작하는 중이네!"
                elif is_ma5_safe: def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래에 있으나 단기 5일선을 사수하며 반격 시동을 거는 중이오!"
                else: def_status = f"성벽({defense_line:{fmt_p}}{currency}) 아래로 함락된 채 기세가 꺾였네! 절대 칼을 뽑지 마시게."

            if is_peak_dumping: base_macd_desc = "<b>🚨 고점 투매 (위험)</b>: 목표선 부근에서 윗꼬리가 생기며 세력의 매도세가 쏟아지고 있소!"
            elif is_massive_dump: base_macd_desc = "<b>🚨 대량 투매 폭발</b>: 하락 험지 속에서 걷잡을 수 없는 매도 폭탄이 떨어지고 있소!"
            elif is_macd_accelerating:
                if rsi_val >= 70: base_macd_desc = "<b>🔥 정회전 가속 (과열권)</b>: 추진력은 강력하나 보조지표 초과열권이오."
                elif vol_strength < 65 or is_candle_bearish or final_code == "DOJI_MID_WAIT":
                    mac_desc_word = "십자성 공방" if final_code == "DOJI_MID_WAIT" else ("음봉 조정" if is_candle_bearish else "숨고르기 공방")
                    wall_pos = "성벽 위에서" if p >= defense_line else "성벽 아래에서"
                    base_macd_desc = f"<b>⚡ 가속 중이나 거래절벽/{mac_desc_word}</b>: MACD는 가속 중이나 {wall_pos} {mac_desc_word} 중이오."
                elif p >= defense_line or final_code == "NEW_HIGH_PULLBACK_BUY" or final_code == "SQUEEZE_BREAKOUT_ATTACK": base_macd_desc = "<b>🔥 정회전 가속 (상승 수성)</b>: 방어선을 사수하며 5일선 타고 상승 탄력 풀가동 중이오."
                else: base_macd_desc = "<b>🔥 정회전 가속 (돌파 시도)</b>: 상방을 향해 5일선 지지받으며 추진력이 붙고 있소."
            elif is_macd_decelerating:
                if is_down_trend_structural or not is_ma5_safe: base_macd_desc = "<b>⚠️ 정회전 둔화 (반탄력 소멸)</b>: 하락 험지 속 단기 반등 추진력이 꺾였소."
                else: base_macd_desc = "<b>⚠️ 정회전 둔화 (탄력 저하)</b>: 상승 관성은 유지 중이나 상방 추진력이 다소 둔화되었소."
            elif is_macd_recovering:
                if is_escape_buy_signal or final_code == "ESCAPE_BUY": base_macd_desc = "<b>🌤️ 역회전 감소 (바닥 탈출)</b>: 매도세는 잦아들며 5일선 안착 추진력이 가동 중이오."
                elif final_code in ["BOTTOM_ENTRY", "EXTREME_BOTTOM_ENTRY", "DEEP_DISCOUNT_ENTRY", "WAIT_COOL_TIME"]: base_macd_desc = "<b>🌤️ 역회전 감소 (바닥 입질)</b>: 하락 압력이 줄어들며 극바닥 다지기가 시도되는 중이오."
                elif final_code == "BREAK_MA20_CONFIRMED": base_macd_desc = "<b>🔥 정회전 가속 (20일선 돌파)</b>: 매도세를 압도하는 수급 화력으로 20일선 안착 추진력 가동 중이오."
                elif is_down_trend_structural or p < defense_line: base_macd_desc = "<b>🌤 역회전 감소 (기술적 반등)</b>: 매도세는 잦아들었으나 역배열/공방 구역이라 주의가 필요하오."
                else: base_macd_desc = "<b>🌤 역회전 감소 (반등 시동)</b>: 하락 관성이 둔화되며 바닥 다지기 반등을 모색 중이오."
            else: base_macd_desc = "<b>⚙️ 엔진 역회전 심화</b>: 하락 관성이 지속되며 매도 압력이 깊어지는 중이오."

            if final_code == "SQUEEZE_BREAKOUT_ATTACK": macd_strategy_msg = f"{base_macd_desc}<br>• <b>[스퀴즈 엔진 폭발]:</b> 압축된 에너지가 상방으로 터지며 강력한 랠리 엔진이 점화되었소!"
            elif final_code == "HIGH_PASS_OVEREXTENDED": macd_strategy_msg = f"{base_macd_desc}<br>• <b>[과다이격 주의]:</b> 엔진 추진력은 강하나 5일선 이격(+{bias_ma5:.1f}%)이 과도하오! 추격 매수를 멈추고 비중을 30% 이하로 관리하시게."
            elif final_code == "NEW_HIGH_BREAKOUT_WARNING": macd_strategy_msg = f"{base_macd_desc}<br>• <b>[엔진 과열 주의]:</b> 돌파 첫날 엔진 가속이 붙었으나 과열이 심하니 절대 추격 매수 금지!"
            elif final_code == "NEW_HIGH_PULLBACK_BUY": macd_strategy_msg = f"{base_macd_desc}<br>• <b>[신고가 엔진 재가동]:</b> 눌림목에서 다시 강력한 랠리 엔진이 점화되었소!"
            elif p >= target_price_100: macd_strategy_msg = "<b>🔥 엔진 풀가동 + 밴드 라이딩</b><br>• <b>역할:</b> 상방 대시세 추종.<br>• <b>진단:</b> 엔진 가속과 함께 상단 밴드가 열리고 있소! 추격 매수는 자제하되, 잔여 물량은 5일선 이탈 전까지 강하게 끌고 가시게."
            elif p >= (target_price_100 * 0.98) or bb_pct_b >= 92.0: macd_strategy_msg = "<b>🚨 엔진 과열 경보 (수확 목표선 임박)</b><br>• <b>역할:</b> 상단 오버슈팅 방어.<br>• <b>진단:</b> 엔진 가속도가 붙어 있어도 상단 저항선 코앞일세! 1차 선제적 익절(분할 수확)을 준비하시게."
            elif is_massive_dump: macd_strategy_msg = f"{base_macd_desc}<br>• <b>[엔진 파손 경계]:</b> 매도 폭탄으로 엔진이 부서지고 있으니 손을 묶고 무조건 도망치시게."
            elif is_overall_cautious_state and not (is_kr and is_morning_breakout_fast): macd_strategy_msg = f"{base_macd_desc}<br>• <b>[관망 기조 동조]:</b> 현재 상단 종합 결론이 관망/경계 상태이므로, 엔진 상태와 무관하게 섣부른 추격매수를 금하고 안전하게 관망하시게."
            else: macd_strategy_msg = f"{base_macd_desc}<br>• <b>[엔진 연동]:</b> 위 전황에 맞춰 유효하게 대응하시게."

            st.markdown(
                f"""<div class='trend-card'><div class='trend-title'>⚔️ 실전 필살 대응 전략</div><div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{ma5_guide_text}</span></div><div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>2. 성벽 사수 및 공방 확인</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{def_status}</span></div><div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>3. 중장기 추세 진단 및 지표 동조 현황</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{indicator_verify_text}</span></div><div style='margin-bottom: 20px;'><span style='color: #1565C0; font-weight: 900; font-size: 24px;'>4. 엔진(MACD) 확인</span><br><span style='color: #333333; font-weight: bold; font-size: 20px;'>{macd_strategy_msg}</span></div><div style='margin-bottom: 25px;'><span style='color: #D32F2F; font-weight: 900; font-size: 24px;'>5. 🛡️ [보유자 전용] 실전 행동 가이드</span><br><span style='color: #2E7D32; font-weight: bold; font-size: 20px;'>👉 {holder_guide_msg}</span></div><hr style='border:1px solid #FFEBEE; margin: 20px 0;'><div class='final-msg'>{action_command_msg}</div></div>""",
                unsafe_allow_html=True,
            )

            st.divider()

            i1, i2 = st.columns(2)
            with i1:
                if final_code == "STOP_LOSS_ALERT" or is_massive_dump:
                    bb_diag = f"🚨 <b>[방어선 붕괴 / 대투매 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 칼날 회피 및 계좌 방어.<br>• <b>진단:</b> 전저점 지하실이 뚫리며 매물이 쏟아지고 있소! 절대 입질조차 하지 말고 즉각 대피하시게."
                elif final_code == "SQUEEZE_BREAKOUT_ATTACK":
                    if is_kr and is_morning_breakout_fast: bb_time_diag = "오전장 화력 폭발 시 총 비중 50%까지 진격"
                    elif is_kr: bb_time_diag = "14:00 이후 돌파 지지 시 총 비중 50%까지 진격"
                    else: bb_time_diag = "정규장 화력 동반 돌파 시 총 비중 50%까지 진격"
                    bb_diag = f"🔥 <b>[스퀴즈 돌파 본진 진격 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 압력밥솥 폭발 대시세 초입 공략.<br>• <b>진단:</b> 에너지가 꽉 찬 상태에서 20일선 양봉 상방 돌파 성공! {bb_time_diag} (윗꼬리 이탈 시 철수)"
                elif final_code == "HIGH_PASS_OVEREXTENDED":
                    bb_diag = f"🔥 <b>[불기둥 과다이격 경계 구역] (5일선 이격: +{bias_ma5:.1f}%)</b><br>• <b>역할:</b> 고점 추격 차단 및 비중 관리.<br>• <b>진단:</b> 대량 거래가 터졌으나 5일선 대비 이격이 과도하오! 추격 매수를 자제하고 비중을 30% 이하로 관리하시게."
                elif final_code == "DOJI_TOP_WARNING":
                    bb_diag = f"🔴 <b>[고점 십자성 상투 경고 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 상투 방어 및 수익 보전.<br>• <b>진단:</b> 밴드 상단에서 힘이 다하고 십자형이 떴소! 절대 추격하지 말고 익절을 준비하시게."
                elif final_code == "NEW_HIGH_BREAKOUT_WARNING":
                    bb_diag = f"🔴 <b>[신고가 돌파 추격 금지 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 고점 상투 및 FOMO 뇌동매매 방어.<br>• <b>진단:</b> 신고가 갱신 불기둥이오! 총알의 10% 미만 극소량 정찰병만 허용하며 절대 추격 금지."
                elif final_code == "NEW_HIGH_PULLBACK_BUY":
                    if is_kr and is_morning_breakout_fast: bb_time_diag = "오전장 화력 폭발 시 총 비중 50%까지 진격"
                    elif is_kr: bb_time_diag = "14:00 이후 지지 확인 시 총 비중 50%까지 진격"
                    else: bb_time_diag = "정규장 화력 동반 시 총 비중 50%까지 진격"
                    bb_diag = f"🔵 <b>[신고가 5일선 첫 눌림목 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 승수 극대화 및 신고가 랠리 추종.<br>• <b>진단:</b> 신고가 달성 후 가장 안전한 5일선 양봉 타점이오! {bb_time_diag} (5일선 이탈 시 전량 칼손절)"
                elif final_code == "BAND_RIDING_HARVEST":
                    bb_diag = f"🟣 <b>[밴드 라이딩 상방 확장] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 대세 상승 랠리 홀딩.<br>• <b>진단:</b> 목표선을 완전히 뚫고 상단 밴드가 확장 중이오! 잔여 물량은 5일선 사수 기준으로 끝까지 추종하시게."
                elif final_code == "RED_SELL_TARGET":
                    bb_diag = f"🔴 <b>[수확 목표선 임박 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 1차 선제적 익절 준비.<br>• <b>진단:</b> 볼린저 상단 고지가 코앞이니 욕심을 덜어내고 분할 수확을 준비하시게."
                elif final_code == "RED_SELL_WARNING":
                    bb_diag = f"🔴 <b>[성벽 위 리스크 관리] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 가짜 돌파(페이크) 방어.<br>• <b>진단:</b> 성벽 위 음봉 또는 상단 윗꼬리로 밀리고 있으니 즉시 비중을 줄이고 수성 태세로 전환하시게."
                elif final_code == "BREAKOUT_ATTACK":
                    bb_diag = f"🟢 <b>[성벽 위 양봉 랠리 추종] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 기세 유지 및 수익 극대화.<br>• <b>진단:</b> 성벽을 뚫고 양봉 전진 중이오. 상방 목표선까지 추세를 즐기시게."
                elif final_code == "WAIT_NARROW_MARGIN":
                    bb_diag = f"🟡 <b>[상승 여력 부족 / 관망] (여력: +{margin_diff:.1f}%)</b><br>• <b>역할:</b> 수지타산 불량 타점 회피.<br>• <b>진단:</b> 타점 조건은 좋으나 상단 목표선까지 거리가 너무 좁소. 진입을 보류하시게."
                elif final_code == "WAIT_ORDERBOOK":
                    bb_diag = f"🟡 <b>[호가창/매도벽 미달 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 속임수/허매수 함정 회피.<br>• <b>진단:</b> 매도잔량비 기준 미달! 세력이 위로 살 의지가 약하거나 허매수로 의심되니 진입을 강제 보류."
                elif final_code == "DOJI_MID_WAIT":
                    bb_diag = f"🟡 <b>[십자형 휩소 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 십자성 방향성 탐색.<br>• <b>진단:</b> 매수와 매도가 완벽히 비긴 상태요. 내일 십자 고가를 돌파해야만 방아쇠를 당기시게."
                elif final_code == "WAIT_COOL_TIME":
                    bb_diag = f"🟡 <b>[1차 진입 쿨타임 가동] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 횡보장 노이즈 차단.<br>• <b>진단:</b> 최근 3일 내에 이미 1차 깃발이 꽂혔소! 중복 매수를 멈추고 관망하시게."
                elif final_code == "DEEP_DISCOUNT_ENTRY":
                    bb_diag = f"🔵 <b>[낙폭 과대 하이패스 매수] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 평단가 축소 (물타기).<br>• <b>진단:</b> 대세 하락이 아닌 할인 구간이오! 쿨타임을 뚫고 즉시 진격하시게."
                elif final_code == "WAIT_INDICATOR":
                    if pullback_rebound_score >= 1:
                        bb_diag = f"🟡 <b>[추세/안전마진 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>진단:</b> 점수({pullback_rebound_score}/3점)는 충족했으나 중심선 위 양봉 안전마진 부족으로 관망."
                    else:
                        bb_diag = f"🟡 <b>[지표/수급 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>진단:</b> 지표 동조 점수 부족({pullback_rebound_score}/3점)으로 안착 대기 중."
                elif final_code in ["BOTTOM_ENTRY", "EXTREME_BOTTOM_ENTRY"]:
                    if is_kr and is_morning_breakout_fast: bb_time_diag = "오전장 화력 속 10% 선제 타진 및 종가 사수"
                    elif is_kr: bb_time_diag = "14:00 이후 10% 타진, 저녁 8시 애프터마켓 마감 사수 시 완성"
                    else: bb_time_diag = "정규장(세션) 수급 유입 시 10% 타진, 마감 사수 시 완성"
                    bb_diag = f"🔴 <b>[1단계 진바닥 입질 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 과매도 바닥권 선취매.<br>• <b>진단:</b> 지표 터치 + 양봉/아래꼬리 방어력 확인! {bb_time_diag} (바닥 이탈 시 철수)"
                elif final_code == "DOJI_BOTTOM_WAIT":
                    bb_diag = f"🔴 <b>[바닥 십자성(Doji) 방어 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 하락 투매 진정 확인.<br>• <b>진단:</b> 지하실에서 십자 방어선이 쳐졌소! 오늘 입질은 참으시고, 내일 십자 고가를 돌파할 때 정찰병을 투입하시게."
                elif final_code == "ESCAPE_BUY":
                    if is_kr and is_morning_breakout_fast: bb_time_diag = "오전장 수급(300점 이상) 속 총 비중 20~30%까지 정찰대 증원"
                    elif is_kr: bb_time_diag = "14:00 이후 5일선 안착 시 총 비중 20~30%까지 정찰대 증원"
                    else: bb_time_diag = "정규장(세션) 수급 동반 5일선 안착 시 총 비중 20~30%까지 정찰대 증원"
                    bb_diag = f"🟢 <b>[2단계 진바닥 탈출 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 5일선 양봉 안착 후 배팅 확대.<br>• <b>진단:</b> {bw_diag_msg}. {bb_time_diag} (윗꼬리 5일선 이탈 시 철수)"
                elif final_code == "BUY_MA20_BREAKOUT":
                    bb_diag = f"🟡 <b>[20일선 첫 돌파 · 안착 확인 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 장기 저항 돌파 후 지지력 검증.<br>• <b>진단:</b> {ma20_fail_days}일 만에 20일선({mid_line:{fmt_p}}{currency})을 거래량 실린 양봉으로 돌파했사오나, 역배열 저항 및 윗꼬리 매물 압력이 남았으니 20일선 지지 안착 확인 후 분할 진입을 검토하시게."
                elif final_code == "BREAK_MA20_CONFIRMED":
                    if defense_line > target_price_100:
                        bb_diag = f"🔵 <b>[눌림목 공방 / 정찰병 타점] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 역배열 매물 소화 중 선제 타진.<br>• <b>진단:</b> 20일선 양봉 돌파 성공! 단, 상단 성벽 왜곡이 남았으니 10~20% 정찰병만 투입하시게. (윗꼬리 이탈 시 철수)"
                    else:
                        if is_kr and is_morning_breakout_fast: bb_time_diag = "오전장 화력 폭발 시 총 비중 50%까지 진격"
                        elif is_kr: bb_time_diag = "14:00 이후 지지 확인 시 총 비중 50%까지 진격"
                        else: bb_time_diag = "정규장 화력 동반 시 총 비중 50%까지 진격"
                        bb_diag = f"🔵 <b>[정석 눌림목 본진 진격 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 본격적인 승수 확대.<br>• <b>진단:</b> 20일선 양봉 안착 및 지표 완벽 동조! {bb_time_diag} (윗꼬리 이탈 시 철수)"
                elif final_code == "WAIT_VOLUME":
                    bb_diag = f"🟡 <b>[수급 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 속임수 반등 차단.<br>• <b>진단:</b> 바닥 기술 지표는 달성했으나 거래량이 부족하니 진입 보류."
                elif final_code == "WAIT_DOWNTREND_FALL":
                    bb_diag = f"🟡 <b>[진바닥 탐색/칼날 관망 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 칼날 회피.<br>• <b>진단:</b> 5일선 아래 하락 구간이오. 5일선 회복 전까지 관망하시게."
                elif final_code == "WAIT_PULLBACK_CANDLE":
                    candlestick_word = "음봉 조정" if is_candle_bearish else "숨고르기 공방"
                    bb_diag = f"🟡 <b>[5일선 지지 검증 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> {candlestick_word} 휩소 방지.<br>• <b>진단:</b> 5일선 위 안착 상태이나 당일 {candlestick_word} 중이오. 5일선 지지 사수 확인 후 대응하시게."
                elif final_code == "PULLBACK_BUY":
                    if is_kr and is_morning_breakout_fast: bb_time_diag = "오전장 화력(300점 이상) 속 안전마진 안착 시 총 비중 50%까지 타진"
                    elif is_kr: bb_time_diag = "14:00 이후 안전마진 안착 시 총 비중 50%까지 타진"
                    else: bb_time_diag = "정규장(세션) 화력 속 안전마진 안착 시 총 비중 50%까지 타진"
                    bb_diag = f"🔵 <b>[3단계 눌림목 추가 매수 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 승수 확대.<br>• <b>진단:</b> {bw_diag_msg}. {bb_time_diag} (윗꼬리 20일선 이탈 시 철수)"
                elif final_code == "YELLOW_CAUTION":
                    bb_diag = "🟡 <b>[성벽 위 경계 및 추격 차단 구역]</b><br>• <b>역할:</b> 추격 매수 원천 차단.<br>• <b>진단:</b> 성벽 위 공방 중이므로 신규 매수를 금지하고 익절 타이밍을 노림."
                elif final_code == "WAIT_OVER_EXTENDED":
                    bb_diag = f"🟡 <b>[과다이격 추격 금지 구역] (5일선 이격: +{bias_ma5:.1f}%)</b><br>• <b>역할:</b> 고점 물림 방지.<br>• <b>진단:</b> 5일선 대비 8% 이상 벌어졌으니 숨고르기까지 매수 보류."
                elif final_code == "BREAKOUT_WARNING":
                    bb_diag = f"🔴 <b>[성벽 위 생명선 이탈 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>역할:</b> 랠리 꺾임 방어.<br>• <b>진단:</b> 성벽 위에는 있으나 단기 생명선(5일선)이 무너졌소! 진격을 멈추고 5일선 재돌파 전까지 철저히 대피하시게."
                else:
                    if pullback_rebound_score >= 1:
                        bb_diag = f"⚖️ <b>[관망 및 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>진단:</b> 지표 동조({pullback_rebound_score}/3점)는 되었으나 역배열 또는 윗꼬리/음봉 저항 등 조건 미달로 관망."
                    elif bottom_score >= 1 or rsi_val <= 38:
                        bb_diag = f"⚖️ <b>[진바닥 지표 관망] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>진단:</b> 바닥 점수({bottom_score}점)가 켜졌으나 음봉 압박 혹은 5일선 이격·방어선 미확인으로 입질 보류 중."
                    else:
                        bb_diag = f"⚖️ <b>[관망 및 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>• <b>진단:</b> 지표 동조 점수 미흡(0/3점)으로 안착 대기 중."

                bb_full_diag = f"📍 <b>[볼린저 위치×캔들]: <span style='color:{bb_pos_col};'>{bb_pos_tag}</span></b><br>• <b>위치 해설:</b> {bb_pos_desc}<hr style='margin:8px 0; border:0.5px dashed #CFD8DC;'>{bb_diag}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세/위치)</p><p style='font-size:28px; color:{bb_pos_col}; margin:10px 0;'>위치 {bb_pct_b:.1f}% <span style='font-size:18px; color:{bb_pos_col};'>({bb_pos_short})</span></p><p class='ind-diag'>{bb_full_diag}</p></div>", unsafe_allow_html=True)

            with i2:
                rsi_cross_up = (rsi_prev <= rsi_sig_prev) and (rsi_val > rsi_sig_val)
                rsi_cross_down = (rsi_prev >= rsi_sig_prev) and (rsi_val < rsi_sig_val)
                
                if rsi_cross_up:
                    rsi_trend_tag = "🚀 골든크로스"
                    rsi_trend_col = "#D32F2F"
                elif rsi_cross_down:
                    rsi_trend_tag = "🩸 데드크로스"
                    rsi_trend_col = "#1976D2"
                elif rsi_val > rsi_sig_val:
                    rsi_trend_tag = "▲ 정배열(상승)"
                    rsi_trend_col = "#E65100"
                else:
                    rsi_trend_tag = "▼ 역배열(하락)"
                    rsi_trend_col = "#1565C0"

                if p >= target_price_100 or rsi_val >= 60:
                    if rsi_cross_down:
                        r_status = "<b>👿 불지옥 과열권 (시그널 데드크로스 📉)</b><br>• <b>진단:</b> 과열권에서 매수세가 시그널을 깨고 추락했소! 즉각 탈출을 준비하시게."
                    elif rsi_val > rsi_sig_val:
                        r_status = "<b>👿 불지옥 과열권 (시그널 상회 📈)</b><br>• <b>진단:</b> 매수세가 극에 달했소! 언제 시그널을 깰지 모르니 신규 추격은 독이오."
                    else:
                        r_status = "<b>👿 불지옥 과열권 (꺾임 📉)</b><br>• <b>진단:</b> 과열권에서 시그널 아래로 꺾였소! 세력의 차익 실현 임박."
                elif rsi_val <= 38:
                    if final_code == "STOP_LOSS_ALERT" or is_massive_dump:
                        r_status = "<b>🩸 투매/방어선 붕괴 추락 중</b><br>• <b>진단:</b> 바닥권이나 전저점이 붕괴되었소! 절대 줍지 마시게."
                    else:
                        if rsi_cross_up:
                            r_status = "<b>🧊 냉골 바닥권 (골든크로스 폭발! 🚀)</b><br>• <b>진단:</b> 바닥에서 본선이 시그널선을 뚫어냈소! 강력한 매수 타점이오."
                        elif rsi_val > rsi_sig_val:
                            r_status = f"<b>🧊 냉골 바닥권 (반등 시동 📈)</b><br>• <b>진단:</b> 바닥을 찍고 매수 온도가 시그널 위로 올라섰소! 타점을 주시하시게."
                        else:
                            r_status = "<b>🧊 냉골 바닥권 (추락 중 📉)</b><br>• <b>진단:</b> 바닥권이나 아직 시그널 아래에 갇혀있소. 골든크로스를 대기하시게."
                else:
                    if rsi_cross_up:
                        r_status = "<b>📈 적정 온도 (골든크로스 포착 🚀)</b><br>• <b>진단:</b> 매수 온도가 시그널을 강하게 돌파했소! 긍정적 방향 전환 확정."
                    elif rsi_cross_down:
                        r_status = "<b>📉 적정 온도 (데드크로스 포착 🩸)</b><br>• <b>진단:</b> 매수 온도가 시그널을 깨고 하락 전환했소. 진입을 삼가시게."
                    elif rsi_val > rsi_sig_val:
                        r_status = "<b>📈 적정 온도 (온기 유지)</b><br>• <b>진단:</b> 시그널 선 위에서 안정적인 상승 에너지를 유지 중이오."
                    else:
                        r_status = "<b>📉 적정 온도 (냉기 유지)</b><br>• <b>진단:</b> 시그널 선 아래에서 하방 압력을 받고 있소. 돌파를 대기하시게."
                        
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (14,9 시그널)</p><p style='font-size:32px; color:#E65100; margin:10px 0;'>{rsi_val:.2f} <span style='font-size:18px; color:{rsi_trend_col};'>({rsi_trend_tag})</span></p><p class='ind-diag'>{r_status}</p></div>", unsafe_allow_html=True)
            i3, i4 = st.columns(2)
            with i3:
                will_cross_up = (will_prev <= will_sig_prev) and (will_val > will_sig_val)
                will_cross_down = (will_prev >= will_sig_prev) and (will_val < will_sig_val)
                
                if will_cross_up:
                    will_trend_tag = "🚀 골든크로스"
                    will_trend_col = "#D32F2F"
                elif will_cross_down:
                    will_trend_tag = "🩸 데드크로스"
                    will_trend_col = "#1976D2"
                elif will_val > will_sig_val:
                    will_trend_tag = "▲ 정배열(상승)"
                    will_trend_col = "#E65100"
                else:
                    will_trend_tag = "▼ 역배열(하락)"
                    will_trend_col = "#1565C0"
                
                if p >= target_price_100 or will_val >= -20:
                    if will_cross_down:
                        w_status = "<b>🚀 상방 저항 (시그널 데드크로스 📉)</b><br>• <b>진단:</b> 천장에서 시그널을 깨고 폭포수가 시작되려 하오! 전량 수확 후 도망치시게."
                    elif will_val > will_sig_val:
                        w_status = "<b>🚀 상방 저항 (천장 돌파 시도 📈)</b><br>• <b>진단:</b> 천장에 붙어서 상방 압력을 계속 터뜨리고 있소! 기세가 살아있으나 신규진입은 금지오."
                    else:
                        w_status = "<b>🚀 상방 저항 (천장 맞고 꺾임 📉)</b><br>• <b>진단:</b> 천장을 맞고 세력이 힘을 빼고 있소! 추격 매수 엄금."
                elif will_val <= -75:
                    if final_code == "STOP_LOSS_ALERT" or is_massive_dump:
                        w_status = "<b>🩸 투매/방어선 붕괴 추락 중</b><br>• <b>진단:</b> 지표는 항복 구역이나 손절선이 뚫려 쏟아지는 칼날이 매섭소! 절대 줍지 마시게."
                    else:
                        if will_cross_up:
                            w_status = f"<b>🏳️ 개미 항복 (골든크로스 반격 🚀)</b><br>• <b>진단:</b> 🧊 극한 투매 후 세력이 시그널을 강하게 돌파했소! 타점 유효."
                        elif will_val > will_sig_val:
                            w_status = f"<b>🏳️ 개미 항복 (세력 반전 시동 📈)</b><br>• <b>진단:</b> 🧊 극한 투매 후 시그널 위로 올라탔소! 반등을 주시하시게."
                        else:
                            w_status = "<b>🏳️ 개미 항복 (지하실 굴착 중 📉)</b><br>• <b>진단:</b> 항복 구간이나 아직 시그널 아래에 갇혔소. 섣불리 바닥이라 예단 말고 관망하시게."
                else:
                    if will_cross_up:
                        w_status = "<b>📈 중간 지대 (골든크로스 🚀)</b><br>• <b>진단:</b> 세력이 방향을 위로 틀며 시그널 선을 돌파했소! 긍정적 흐름이오."
                    elif will_cross_down:
                        w_status = "<b>📉 중간 지대 (데드크로스 🩸)</b><br>• <b>진단:</b> 세력이 고개를 숙이며 시그널 선을 이탈했소. 단기 하방 압력 경계."
                    elif will_val > will_sig_val:
                        w_status = "<b>📈 중간 지대 (상방 기세 유지)</b><br>• <b>진단:</b> 시그널 위에서 세력의 상방 의지가 지속 중이오."
                    else:
                        w_status = "<b>📉 중간 지대 (하방 기세 유지)</b><br>• <b>진단:</b> 시그널 아래에서 상/하방 방향 탐색 중이오."
                        
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R (14,6 시그널)</p><p style='font-size:32px; color:#E65100; margin:10px 0;'>{will_val:.2f} <span style='font-size:18px; color:{will_trend_col};'>({will_trend_tag})</span></p><p class='ind-diag'>{w_status}</p></div>", unsafe_allow_html=True)

            with i4:
                if is_peak_dumping:
                    m_diag = "<b>🚨 엔진 급제동 (고점 투매)</b><br>• <b>역할:</b> 고점 상투 방어.<br>• <b>진단:</b> 목표선 부근에서 윗꼬리가 생기며 세력의 매도세가 쏟아지고 있소! 즉시 수익을 챙기고 철수하시게."
                elif final_code == "STOP_LOSS_ALERT" or is_massive_dump:
                    m_diag = "<b>🚨 엔진 붕괴 (방어선 이탈 / 대투매)</b><br>• <b>역할:</b> 하방 가속 경보.<br>• <b>진단:</b> 지지선이 무너지며 매물 폭탄이 떨어지고 있소! 미련을 버리고 즉시 대피하시게."
                elif p >= target_price_100:
                    m_diag = "<b>🔥 엔진 풀가동 (대세 추종)</b><br>• <b>역할:</b> 추세 지속력 측정.<br>• <b>진단:</b> 목표선 돌파와 함께 엔진이 힘을 내고 있소! 5일선 사수 기준으로 잔여 물량을 추종하시게."
                elif p >= (target_price_100 * 0.98) or bb_pct_b >= 92.0:
                    m_diag = "<b>🚨 엔진 과열 차단 (목표선 임박)</b><br>• <b>역할:</b> 고점 상투 방어.<br>• <b>진단:</b> 목표선 도달 임박으로 1차 선제적 익절(분할 수확)을 준비하시게."
                elif is_overall_cautious_state and not (is_kr and is_morning_breakout_fast):
                    m_diag = f"{base_macd_desc}<br>• <b>[관망 기조 동조]:</b> 현재 상단 종합 결론이 관망/경계 상태이므로, 엔진 상태와 무관하게 섣부른 추격매수를 금하고 안전하게 관망하시게."
                else:
                    m_diag = f"{base_macd_desc}<br>• <b>[엔진 연동]:</b> 위 전황에 맞춰 유효하게 대응하시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (추세 엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"👵 아이구! 오류: {e}")
