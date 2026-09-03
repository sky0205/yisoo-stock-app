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
      del st.session_state["password"]  # 비밀번호 기억 삭제
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


@st.cache_data(ttl=10)  # 10초 단위로 신선도 유지
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


# 1. 스타일 및 화면 구성
st.set_page_config(
    page_title="이수할아버지의 냉정 진단기 v36064", layout="wide"
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
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
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
      if avg_us_chg >= 1.0:
        market_mood = "미 3대 지수 동반 훈풍 속 안도 랠리!"
      else:
        market_mood = "미 3대 지수 일제히 상승 마감!"
    elif neg_cnt == 3:
      if avg_us_chg <= -1.0:
        market_mood = "미 3대 지수 동반 급락으로 투심 냉각!"
      else:
        market_mood = "미 3대 지수 일제히 하락 (전면 약세 국면)!"
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
          f"⚡ [환율 분기점] 원/달러 {u_val:,.2f}원! 1,400원 하회했으나 안심은"
          " 금물(외인 눈치보기)"
      )
    elif u_val <= 1330:
      macro_alerts.append(f"💵 [환율 우호] 원/달러 {u_val:,.2f}원 하향 안정세")

    if u_chg > 0.3:
      macro_alerts.append(f"📈 오늘 환율 {u_chg:+.2f}% 치솟는 중!")
    elif u_chg < -0.3:
      macro_alerts.append(f"📉 오늘 환율 {u_chg:+.2f}% 진정세")

    if tnx_val >= 4.5 or u_val >= 1380:
      strategy = (
          "외인 수급 이탈 우려로 상단 저항이 강하니 추격매수 금지, 5일선 및"
          " 방어선 위주로 보수적 대응하시게."
      )
    elif avg_us_chg > 0.5 and tnx_val < 4.2 and u_val < 1350:
      strategy = (
          "매크로 환경이 우호적이니 거래량 실린 정석 눌림목 주도주 위주로 적극"
          " 공략하시게."
      )
    else:
      strategy = (
          "장 초반 뇌동매매를 삼가고 지표 동조와 5일선 안착 여부를 끝까지 확인"
          " 후 진입하시게."
      )

    macro_text = (
        " | ".join(macro_alerts) if macro_alerts else "매크로 특이 동향 없음"
    )

    st.info(
        f"🧐 **이수 할배의 글로벌 판독:** {market_mood}!\n\n- {macro_text}\n- 💡"
        f" **[대응 전략]** {strategy}"
    )
  except:
    st.error("⚠️ 글로벌 데이터 호출 불가")


st.title("🧐 이수할아버지의 냉정 진단기 v36064 (미장 07:00 매수원칙 완성판)")
display_global_risk()
st.divider()

# ==============================================================================
# ★ [상단: 종목 / 수동입력 / 평단가 통합 입력창]
# ==============================================================================
col_symbol, col_manual, col_avg, col_btn = st.columns([1.8, 1.8, 1.8, 1.2])

with col_symbol:
  symbol = st.text_input("📊 종목번호 또는 티커", "005930").strip()

with col_manual:
  manual_price_str = st.text_input(
      "⚡ 프리장/수동 실시간가 (선택)",
      value="",
      help=(
          "프리장이나 주간거래 가격을 직접 적으시면 정규장 시세 대신 우선"
          " 적용합니다. (지우고 빈칸으로 만드시면 자동 시세 복귀)"
      ),
  ).strip()

with col_avg:
  user_avg_price = st.number_input(
      "💡 보유 평단가 (미보유 시 0)",
      min_value=0.0,
      value=0.0,
      step=100.0,
      help="평단가를 입력하시면 수익권/손실권 맞춤형 실전 대응 가이드를 제공합니다.",
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

    # 한국 시각(KST) 및 현지 시각 정밀 동기화
    kst_now = datetime.now(ZoneInfo("Asia/Seoul"))
    try:
      now_tz = (
          ZoneInfo("Asia/Seoul") if is_kr else ZoneInfo("America/New_York")
      )
      now_local = datetime.now(now_tz)
    except Exception:
      utc_now = datetime.now(ZoneInfo("UTC"))
      now_local = utc_now.astimezone(
          ZoneInfo("Asia/Seoul") if is_kr else ZoneInfo("America/New_York")
      )

    df = pd.DataFrame()
    auto_p, v_curr = 0.0, 0.0
    us_prev_p = None

    if is_kr:
      currency, fmt_p = "원", ",.0f"
      try:
        df = fdr.DataReader(symbol, start=start_date.strftime("%Y-%m-%d"))
      except:
        pass

      if df.empty:
        try:
          df = yf.Ticker(f"{symbol}.KS").history(start=start_date)
          if df.empty:
            df = yf.Ticker(f"{symbol}.KQ").history(start=start_date)
        except:
          pass

      kr_fetched = False
      try:
        api_url = f"https://m.stock.naver.com/api/stock/{symbol}/basic"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"
            )
        }
        res = requests.get(api_url, headers=headers, timeout=3)
        if res.status_code == 200:
          data = res.json()
          auto_p = float(data["closePrice"].replace(",", ""))
          v_curr = float(data["accumulatedTradingVolume"].replace(",", ""))
          kr_fetched = True
      except:
        pass

      if not kr_fetched:
        try:
          url = f"https://finance.naver.com/item/main.naver?code={symbol}"
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
        except:
          if not df.empty:
            auto_p = float(df["Close"].iloc[-1])
            v_curr = float(df["Volume"].iloc[-1])
    else:
      currency, fmt_p = "$", ",.2f"
      ticker = yf.Ticker(symbol.upper())

      try:
        df = ticker.history(start=start_date)
      except Exception:
        df = ticker.history(period="1y")

      try:
        info = ticker.fast_info
        auto_p = getattr(info, "last_price", float(df["Close"].iloc[-1]))
        v_curr = getattr(info, "last_volume", float(df["Volume"].iloc[-1]))
        us_prev_p = info.previous_close
      except:
        pass

      if auto_p == 0.0 and not df.empty:
        auto_p = float(df["Close"].iloc[-1])
        v_curr = float(df["Volume"].iloc[-1])

    # 수동 입력 시세 우선 채택
    is_manual_mode = False
    if manual_price_str:
      try:
        parsed_val = float(manual_price_str.replace(",", "").replace("$", ""))
        if parsed_val > 0:
          p = parsed_val
          is_manual_mode = True
          st.info(
              f"💡 **[수동 입력 모드]** 현재가를 **{p:{fmt_p}}{currency}** 기준으로"
              " 정밀 연산합니다."
          )
        else:
          p = auto_p
      except ValueError:
        st.warning(
            "⚠️ 올바른 숫자 형식으로 입력해 주십시오. (자동 시세로"
            " 연산합니다)"
        )
        p = auto_p
    else:
      p = auto_p

    if df.empty:
      st.warning(
          f"⚠️ [{symbol}] 종목의 데이터를 불러오지 못했구먼. 종목번호를 다시"
          " 확인하거나 잠시 후 다시 시도해 주시게."
      )
    else:
      df = df.ffill().dropna()
      df.index = pd.to_datetime(df.index).date
      today_date = now_local.date()

      if not is_kr and us_prev_p and us_prev_p > 0:
        prev_p = us_prev_p
      else:
        if today_date in df.index:
          prev_p = float(df["Close"].iloc[-2]) if len(df) >= 2 else p
        else:
          prev_p = float(df["Close"].iloc[-1]) if len(df) >= 1 else p

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

      p_diff = p - prev_p
      p_chg = (p_diff / prev_p) * 100 if prev_p > 0 else 0

      if is_kr:
        m_start = now_local.replace(hour=9, minute=0, second=0, microsecond=0)
        m_end = now_local.replace(hour=15, minute=30, second=0, microsecond=0)
        total_minutes = 390
      else:
        m_start = now_local.replace(hour=9, minute=30, second=0, microsecond=0)
        m_end = now_local.replace(hour=16, minute=0, second=0, microsecond=0)
        total_minutes = 390

      if m_start <= now_local <= m_end and now_local.weekday() < 5:
        elapsed = max(10, (now_local - m_start).seconds / 60)
        vol_strength_auto = min(1000, v_ratio / (elapsed / total_minutes))
      else:
        vol_strength_auto = v_ratio

      if is_manual_mode:
        vol_strength = 100.0
      else:
        vol_strength = vol_strength_auto

      # 보조지표 연산 (RSI 14/9, Williams %R 14/6, MACD 12/26/9, BB 20/2)
      delta = df["Close"].diff()
      gain = (delta.where(delta > 0, 0)).rolling(14).mean()
      loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
      rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
      rsi_val, rsi_prev = rsi_series.iloc[-1], rsi_series.iloc[-2]

      h14, l14 = df["High"].rolling(14).max(), df["Low"].rolling(14).min()
      will_series = (h14 - df["Close"]) / (h14 - l14 + 1e-10) * -100
      will_val, will_prev = will_series.iloc[-1], will_series.iloc[-2]

      macd = (
          df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
      )
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

      if is_macd_accelerating:
        macd_status_name = "🔥 엔진 정회전 가속"
        macd_strategy_msg = (
            "<b>🔥 엔진 정회전 가속 (엑셀 풀가동)</b><br>• <b>역할:</b> 상승 추진력"
            " 폭발.<br>• <b>진단:</b> 상승 가속도가 날마다 붙고 있네! 성벽을"
            " 향해 든든하게 추세를 즐기시게."
        )
      elif is_macd_decelerating:
        macd_status_name = "⚠️ 엔진 정회전 둔화"
        macd_strategy_msg = (
            "<b>⚠️ 엔진 정회전 둔화 (탄력 저하 경보)</b><br>• <b>역할:</b> 상승"
            " 탄력 둔화 감지.<br>• <b>진단:</b> 상승세는 유지 중이나 추진력이"
            " 꺾였으니, 신규 매수를 자제하고 성벽 위 분할 익절을 준비하시게."
        )
      elif is_macd_recovering:
        macd_status_name = "🌤️ 역회전 감소"
        macd_strategy_msg = (
            "<b>🌤️ 엔진 역회전 감소 (반등 시동)</b><br>• <b>역할:</b> 하락 둔화 및"
            " 바닥 다지기.<br>• <b>진단:</b> 매도세가 잦아들며 반등 채비 중이오."
            " 5일선 안착 여부를 확인하시게."
        )
      else:
        macd_status_name = "⚙️ 엔진 역회전 심화"
        macd_strategy_msg = (
            "<b>⚙️ 엔진 역회전 심화 (하락 가속)</b><br>• <b>역할:</b> 하락 조정"
            " 가속.<br>• <b>진단:</b> 하락 관성 지속. 섣부른 매수 및 물타기를"
            " 절대 금지하고 관망하시게."
        )

      df["MA5"] = df["Close"].rolling(5).mean()
      df["MA20"] = df["Close"].rolling(20).mean()
      df["MA60"] = df["Close"].rolling(60).mean()
      df["MA120"] = df["Close"].rolling(120).mean()
      df["Std"] = df["Close"].rolling(20).std()

      mid_line = df["MA20"].iloc[-1]
      up_b = mid_line + (df["Std"].iloc[-1] * 2)
      low_b = mid_line - (df["Std"].iloc[-1] * 2)

      bandwidth = ((up_b - low_b) / mid_line) * 100 if mid_line > 0 else 0

      ma5_val = df["MA5"].iloc[-1] if len(df) >= 5 else mid_line
      ma60_val = df["MA60"].iloc[-1] if len(df) >= 60 else mid_line
      ma120_val = df["MA120"].iloc[-1] if len(df) >= 120 else mid_line

      bias_ma5 = ((p - ma5_val) / ma5_val) * 100 if ma5_val > 0 else 0
      bias_ma20 = ((p - mid_line) / mid_line) * 100 if mid_line > 0 else 0
      is_over_extended_5 = bias_ma5 >= 5.0

      # 밴드폭 판정
      if bandwidth < 12.0:
        is_bandwidth_ok = False
        bw_status_category = "EXTREME_SQUEEZE"
        bw_diag_msg = (
            f"밴드폭 극소({bandwidth:.1f}%)로 에너지 극단 응축 중 / 돌파 방향"
            " 확인 전까지 승수 확대 금지"
        )
        squeeze_info_str = (
            f"<br>• ⚡ <b>[밴드폭 극소({bandwidth:.1f}%)]</b> 에너지가 바짝"
            " 응축 중이오! 상/하방 돌파 방향이 잡힐 때까지 승수 확대를 금지하네."
        )
      elif 12.0 <= bandwidth < 20.0:
        if p >= ma5_val:
          is_bandwidth_ok = True
          bw_status_category = "SQUEEZE_BREAKOUT"
          bw_diag_msg = (
              f"밴드폭 응축돌파({bandwidth:.1f}%) 5일선 안착 확인! 에너지 분출"
              " 초입 진입 허용"
          )
          squeeze_info_str = (
              f"<br>• 🟢 <b>[밴드폭 응축돌파({bandwidth:.1f}%)]</b> 에너지를 잔뜩"
              " 모은 뒤 5일선을 뚫고 올라섰네! 상방 분출 초입으로 유효하오."
          )
        else:
          is_bandwidth_ok = False
          bw_status_category = "NARROW_WATCH"
          bw_diag_msg = (
              f"밴드폭 협소({bandwidth:.1f}%) 및 5일선 하회로 하방 확장 위험"
              " 관망"
          )
          squeeze_info_str = (
              f"<br>• 🟡 <b>[밴드폭 협소({bandwidth:.1f}%)]</b> 밴드폭이 좁은데"
              " 주가가 5일선 밑에 머물러 있소! 아래로 터지는 칼날을 주의하시게."
          )
      else:
        is_bandwidth_ok = True
        bw_status_category = "WIDE_OK"
        bw_diag_msg = (
            f"밴드폭 양호({bandwidth:.1f}%) 목표 변동폭 충분 (정상 공략 구역)"
        )
        squeeze_info_str = (
            f"<br>• 🌊 <b>[밴드폭 넉넉함({bandwidth:.1f}%)]</b> 상하 진폭 활주로가"
            " 넉넉히 트였네! 정상 승수 확대 가능 구역이오."
        )

      today_open = float(df["Open"].iloc[-1])
      today_high = float(df["High"].iloc[-1])
      today_low = float(df["Low"].iloc[-1])

      candle_range = max(0.01, today_high - today_low)
      lower_tail = min(today_open, p) - today_low
      body_len = abs(today_open - p)

      # 캔들 정밀 판독: 음봉 투매 시 매수 차단
      is_down_trend_v = (p < prev_p) and (p_chg < 0)

      is_pure_bullish_candle = p >= today_open
      is_bottom_lower_tail = (
          (lower_tail >= candle_range * 0.45) or (lower_tail >= body_len * 1.3)
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
      defense_line = (
          float(df["High"].iloc[-defense_link_idx:-1].max()) * 0.93
          if len(df) > 1
          else p * 0.93
      )

      # 추세 정밀 판독
      is_bullish = (
          ma5_val > mid_line and mid_line > ma60_val and ma60_val > ma120_val
      )
      is_bearish = (
          ma5_val < mid_line and mid_line < ma60_val and ma60_val < ma120_val
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
            "🌱 <b>[단기 반등 초입]</b> 5일선이 20일선 돌파! 상방 반전 시도 중"
        )
      elif ma5_val < mid_line:
        trend_status = (
            "📉 <b>[단기 조정 국면]</b> 5일선이 20일선 밑으로 밀려 숨고르기 중"
        )
      else:
        trend_status = "⚖️ <b>[추세 혼조]</b> 방향 탐색 중"

      ma_price_summary = (
          "<br>• 📌 <b>[주요 이동평균선 현황]</b><br>&nbsp;&nbsp;<span"
          f" style='color:#D32F2F; font-weight:bold;'>🔴 5일선: {ma5_str} (이격:"
          f" {bias_ma5:+.1f}%)</span> | <span style='color:#1976D2;"
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
        }
        final_display_name = core_vault.get(symbol, f"국내종목 ({symbol})")
        if symbol not in core_vault:
          try:
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(
                url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3
            )
            soup = BeautifulSoup(res.text, "html.parser")
            final_display_name = soup.select_one(
                ".wrap_company h2 a"
            ).text.strip()
          except:
            try:
              df_krx_backup = load_krx_listing()
              final_display_name = df_krx_backup[
                  df_krx_backup["Code"] == symbol
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

      st.markdown("### 📊 현재주가현황")
      display_price = (
          f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
      )
      st.markdown(
          "<div style='background-color:#f8f9fa; padding:20px;"
          " border-radius:10px; border-left:10px solid #1565C0;'><p"
          " style='font-size:35px; color:#1565C0; font-weight:bold;"
          f" margin:0;'>{safe_display_name}</p><p style='font-size:30px;"
          " color:#FF4B4B; font-weight:bold; margin:10px 0 0"
          f" 0;'>{display_price}</p></div>",
          unsafe_allow_html=True,
      )

      # 거래량 전황 판정
      if is_manual_mode:
        v_status, v_adv = (
            "수동검증",
            "⚡ <b>[프리장/수동 연산]</b> 수동 입력 시세를 기준으로 정밀 검증"
            " 중이외다.",
        )
      elif vol_strength >= 150:
        if not is_down_trend_v:
          v_status, v_adv = (
              "과열폭발",
              f"🔥 <b>[화력폭발]</b> 시간보정 강도 {vol_strength:.1f}점! 바닥"
              " 거래량 폭발 또는 본진 진격 중이오.",
          )
        else:
          v_status, v_adv = (
              "역배열투매",
              f"🚨 <b>[역배열/하방 투매과열]</b> 시간보정 강도 {vol_strength:.1f}점!"
              " 하방 압력 속 투매 물량 폭발 중이니 절대 칼날을 잡지 마시게.",
          )
      elif vol_strength >= 100:
        if not is_down_trend_v:
          v_status, v_adv = (
              "매집시작",
              f"🚀 <b>[매집시작]</b> 시간보정 강도 {vol_strength:.1f}점! 화력이"
              " 차오르네.",
          )
        else:
          v_status, v_adv = (
              "역배열과열",
              f"⚠️ <b>[역배열과열]</b> 시간보정 강도 {vol_strength:.1f}점! 하락"
              " 추세 속 속임수 음봉 거래량 주의.",
          )
      elif vol_strength >= 80:
        if not is_down_trend_v:
          v_status, v_adv = (
              "정상화력",
              f"⚔️ <b>[정상화력]</b> 시간보정 강도 {vol_strength:.1f}점! 기세가"
              " 뻣뻣하구먼.",
          )
        else:
          v_status, v_adv = (
              "역배열과열",
              f"⚠️ <b>[역배열과열]</b> 시간보정 강도 {vol_strength:.1f}점! 하락"
              " 추세 속 속임수 음봉 거래량 주의.",
          )
      else:
        v_status, v_adv = (
            "거래절벽",
            f"🧊 <b>[거래절벽]</b> 시간보정 강도 {vol_strength:.1f}점! 수급이 마르고"
            " 동력이 없으니 속지 마시게.",
        )

      st.markdown(
          f"<div class='vol-box'><div style='font-size:32px; font-weight:bold;"
          f" color:#0D47A1; margin-bottom:10px;'>📊 거래량 전황: {v_status}"
          f" ({'수동 연산 모드' if is_manual_mode else f'실시간 {v_ratio:.1f}% / 5일평균대비'})</div><div"
          f" class='vol-sub-text'>{v_adv}</div></div>",
          unsafe_allow_html=True,
      )

      # 지표 정밀 연산 및 바닥 기억
      bb_bot_series = (df["Close"] <= (low_b * 1.02)).astype(int)
      rsi_bot_series = (rsi_series <= 35).astype(int)
      will_bot_series = (will_series <= -80).astype(int)
      bottom_score_series = bb_bot_series + rsi_bot_series + will_bot_series

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
        stop_reason = f"보유 평단가 대비 손절 마지노선 이탈"
      elif (recent_bottom_memory or bottom_score >= 2) and p < prev_low:
        is_stop_loss_triggered = True
        stop_reason = f"바닥권 전저점 이탈 마지노선"

      # 성벽 & 수확목표선
      target_price_100 = up_b
      is_target_reached = p >= (target_price_100 * 0.97)
      is_on_the_wall = (p >= defense_line) and (p < target_price_100)

      # ==============================================================================
      # ★ [1·2·3단계 매수 판정: 음봉 투매 차단 및 5일선 기준 분격]
      # ==============================================================================
      is_bottom_indicator_ok = bottom_score >= 2 or recent_bottom_memory
      is_macd_not_deepening = not is_macd_reverse_deepening

      # 1단계: 5일선 아래 + 음봉투매 차단
      is_bottom_entry_signal = (
          (not is_ma5_safe)
          and (bottom_score >= 2)
          and (vol_strength >= 80)
          and (not is_down_trend_v)
          and is_macd_not_deepening
          and is_valid_bottom_candle
      )

      # 2단계: 5일선 위 안착
      is_escape_buy_signal = (
          is_ma5_safe
          and is_bottom_indicator_ok
          and (vol_strength >= 80)
          and is_macd_not_deepening
          and is_valid_buy_candle
          and is_bandwidth_ok
      )

      # 3단계: 눌림목 추가 매수
      is_pullback_buy_signal = (
          (not is_down_trend_structural)
          and (p >= mid_line)
          and is_ma5_safe
          and (pullback_rebound_score >= 2)
          and (vol_strength >= 80)
          and is_bandwidth_ok
          and is_macd_not_deepening
          and is_valid_buy_candle
      )

      # ==============================================================================
      # ★ [국장 14:00 vs 미장 07:00 정규장 실시간 매수 차단 족쇄]
      # ==============================================================================
      if is_kr and not is_manual_mode:
        # 국장: 14:00 이후에만 매수 허용
        is_afternoon_safe_time = (now_local.hour > 14) or (
            now_local.hour == 14 and now_local.minute >= 0
        )
        time_tag_wait = "★ 14:00 매수 대기"
        time_tag_ok = "14:00 이후 안착 완료"
        time_rule_desc = (
            "오전장 휩소를 피하기 위해 14:00까지 손가락을 묶고 지지 여부를"
            " 관찰 후 진입"
        )
        time_rule_pass = "14:00 이후 바닥 지지 확인 완료!"
      elif not is_kr and not is_manual_mode:
        # 미장: 실시간 정규장(밤~새벽) 중에는 매수 원천 차단! 익일 오전 07:00 이후에만 매수 허용!
        # 한국시간 07:00부터 22:30(본장 시작 전) 사이에만 확정 일봉 매수 허용
        is_afternoon_safe_time = (kst_now.hour >= 7) and (kst_now.hour < 22)
        time_tag_wait = "★ 07:00 마감 일봉 대기"
        time_tag_ok = "07:00 일봉 안착 확인"
        time_rule_desc = (
            "정규장 중에는 매도만 유효! 밤새 휩소를 피하고 07:00 마감 일봉을"
            " 확인 후 진입"
        )
        time_rule_pass = "정규장 캔들 마감! 07:00 일봉 안착 확인 완료!"
      else:
        is_afternoon_safe_time = True
        time_tag_wait = "★ 수동 검증"
        time_tag_ok = "수동 시세 확인"
        time_rule_desc = "수동 입력 시세 지지 확인 후 진입"
        time_rule_pass = "수동 시세 지지 확인 완료!"

      # ==============================================================================
      # ★ [신호등 분기: 매도는 실시간 즉시 발동, 매수는 07시/14시 족쇄 엄격 적용]
      # ==============================================================================
      if is_stop_loss_triggered:
        final_code = "STOP_LOSS_ALERT"
        sig = "🚨 [비상 손절] 바닥권 전저점 붕괴! 전량 칼손절 후퇴!"
        col = "#D32F2F"
        final_adv = (
            f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[바닥권"
            " 전저점 방어선 붕괴]</b> 미련을 버리고 즉시 전량 칼손절"
            " 후퇴하시게."
        )

      elif is_on_the_wall and is_bearish_candle:
        final_code = "RED_SELL_WARNING"
        sig = "🟡 [경계] 성벽 위 음봉 출현 / 분할 익절 준비"
        col = "#EF6C00"
        final_adv = (
            f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[성벽 위"
            " 음봉 출현]</b> 성벽(방어선) 위에서 음봉이 발생했으니, 5일선 사수"
            " 여부를 살피며 기세 둔화 시 분할 익절할 준비를 하시게."
        )

      elif is_target_reached:
        final_code = "RED_SELL_TARGET"
        sig = "🔴 [매도] 수확 목표선 도달! 이익실현 타점!"
        col = "#D32F2F"
        final_adv = (
            f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[수확"
            " 목표선 도달]</b> 성벽 위 목표선 도달 완료! 즉시 분할 익절 및 전량"
            " 매도로 수익을 확정하시게."
        )

      elif is_on_the_wall:
        final_code = "YELLOW_CAUTION"
        sig = "🟡 [경계] 성벽 위 공방 / 매도 준비!"
        col = "#EF6C00"
        final_adv = (
            f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[성벽 위"
            " 진입 및 공방]</b> 추격 매수는 절대 금하고, 매도 준비 및 경계"
            " 태세를 갖추시게!"
        )

      elif (
          is_escape_buy_signal or is_pullback_buy_signal
      ) and is_over_extended_5:
        final_code = "WAIT_OVER_EXTENDED"
        sig = (
            f"🟡 [관망/경계] 5일선 과다이격(+{bias_ma5:.1f}%) / 추격 매수 금지"
        )
        col = "#F57C00"
        final_adv = (
            f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[5일선"
            f" 과다이격(+{bias_ma5:.1f}%)]</b> 주가가 5일선에서 5% 이상 벌어져"
            " 단기 차익 매물(되돌림) 위험이 크니, 5일선 부근으로 숨고르기할"
            " 때까지 추격 매수를 엄금하시게."
        )

      # 🟢 [1단계 진바닥 입질 매수]
      elif is_bottom_entry_signal:
        final_code = "BOTTOM_ENTRY"
        col = "#388E3C"
        if not is_afternoon_safe_time:
          sig = f"🟢 [입질 포착] 1단계 진바닥 입질 ({time_tag_wait})"
          final_adv = (
              f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[진바닥"
              f" 포착 완료]</b> 3중 지표 터치 확인! 단, {time_rule_desc}하시게."
          )
        else:
          sig = f"🟢 [매입 진격] 1단계 진바닥 입질 매수 ({time_tag_ok})"
          final_adv = (
              f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[{time_tag_ok}]</b>"
              f" {time_rule_pass} 소량 씨앗 뿌리기 진격 (전저점 방어선"
              " 엄수)."
          )

      # 🟢 [2단계 진바닥 탈출 매수]
      elif is_escape_buy_signal:
        final_code = "ESCAPE_BUY"
        col = "#2E7D32"
        if not is_afternoon_safe_time:
          sig = f"🟢 [탈출 포착] 2단계 진바닥 탈출 ({time_tag_wait})"
          final_adv = (
              f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[5일선"
              f" 안착 포착]</b> {bw_diag_msg}. 기세는 살아있으나 {time_rule_desc}"
              " 비중 확대를 집행하시게."
          )
        else:
          sig = f"🟢 [추가 진격] 2단계 진바닥 탈출 매수 ({time_tag_ok})"
          final_adv = (
              f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[{time_tag_ok}]</b>"
              f" {bw_diag_msg}. 5일선 위 안착 완벽 사수! 배팅 비중을 늘려"
              " 밭을 다짐."
          )

      # 🔵 [3단계 눌림목 추가 매수] (동기화 보수 완료)
      elif is_pullback_buy_signal:
        final_code = "PULLBACK_BUY"
        col = "#1976D2"
        if not is_afternoon_safe_time:
          sig = f"🔵 [승수 포착] 3단계 눌림목 ({time_tag_wait})"
          final_adv = (
              f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[눌림목"
              f" 지지 포착]</b> {bw_diag_msg}. <b>{time_rule_desc}</b> 본진을"
              " 투입하시게."
          )
        else:
          sig = f"🔵 [본진 진격] 3단계 눌림목 추가 매수 ({time_tag_ok})"
          final_adv = (
              f" • <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[{time_tag_ok}]</b>"
              f" {bw_diag_msg}. {time_rule_pass} 5·20일선 위 안착 및 활주로"
              " 확보 완료! 알짜배기 추가 매수."
          )

      # 🟡 [음봉 투매 또는 하락 진행 관망 분기]
      elif (bottom_score >= 2 or recent_bottom_memory) and is_down_trend_v:
        final_code = "WAIT_DOWNTREND_FALL"
        sig = "🟡 [진바닥 탐색 중] 역배열 투매/음봉 진행 / 칼날 관망"
        col = "#F57C00"
        final_adv = (
            f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[역배열"
            " 투매 음봉 진행]</b> 바닥권 지표는 터치했으나 하방 투매와 음봉"
            " 압력이 거세니 절대 떨어지는 칼날을 잡지 마시고 5일선 회복 전까지"
            " 손가락을 묶으시게."
        )

      elif (
          is_ma5_safe
          and not is_bottom_indicator_ok
          and not is_down_trend_structural
      ):
        final_code = "WAIT_INDICATOR"
        sig = "🟡 [관망/보류] 5일선 안착했으나 보조지표 미흡 (외바닥 주의)"
        col = "#F57C00"
        final_adv = (
            f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[지표"
            " 미흡]</b> 5일선은 안착했으나 보조지표 동조 점수 부족으로 외바닥"
            " 속임수를 경계하고 관망하시게."
        )

      elif is_ma5_safe and is_macd_reverse_deepening:
        final_code = "WAIT_MACD"
        sig = "🟡 [관망/보류] 5일선 회복 중이나 엔진 역회전 심화 (진입 자제)"
        col = "#F57C00"
        final_adv = (
            f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[엔진"
            " 역회전 심화]</b> 5일선 위 안착 시도 중이나 MACD 하락 압력이"
            " 가속되므로 속임수 반등을 주의하고 관망하시게."
        )

      elif (
          bottom_score >= 2 or recent_bottom_memory
      ) and vol_strength < 80:
        final_code = "WAIT_VOLUME"
        sig = "🟡 [입질 대기] 지표 충족 / 거래량 수반 대기"
        col = "#E65100"
        final_adv = (
            f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[수급"
            " 부진]</b> 바닥 지표는 확인했으나 거래량이 실리지 않은 속임수"
            " 구간이니, 확실한 거래량 유입을 확인 후 진입하시게."
        )

      elif is_down_trend_structural and not is_ma5_safe:
        final_code = "WAIT_DOWNTREND_FALL"
        sig = "🟡 [진바닥 탐색 중] 역배열 하락 진행 / 칼날 관망"
        col = "#F57C00"
        final_adv = (
            f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[진바닥"
            " 탐색 중]</b> 대세 역배열 하락 추세 속에서 5일선 아래로 칼날이"
            " 떨어지는 중이니 섣부른 물타기를 금하고 손가락을 묶으시게."
        )

      elif (
          (p >= mid_line * 0.98 and p <= mid_line * 1.03)
          and (pullback_rebound_score >= 1)
          and (not is_down_trend_structural)
      ):
        final_code = "WAIT_PULLBACK"
        if not is_bandwidth_ok:
          sig = (
              "🟡 [관망/보류] 눌림목 영역이나 밴드폭 기준 미달 (돌파 확인 대기)"
          )
          final_adv = (
              f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[{bw_diag_msg}]</b>"
              " 확실한 5일선 안착 및 분출 확인 전까지 승수 확대 금지."
          )
        else:
          sig = "🟡 [관망/보류] 눌림목 영역 도달했으나 지표 동조 미흡"
          final_adv = (
              f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[눌림목"
              f" 지표 미흡]</b> 20일선 부근이나 지표 동조({pullback_rebound_score}점)"
              " 및 지지 캔들 확인 전까지 매수 보류."
          )
        col = "#F57C00"

      else:
        final_code = "WAIT_GENERAL"
        sig = "🟡 [관망] 조건 미충족 / 뇌동매매 금지"
        col = "#FBC02D"
        final_adv = (
            f"• <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 조건 미충족"
            " 상태이므로 뇌동매매를 금하고 관망 유지."
        )

      # ==============================================================================
      # ★ [지표 세부 텍스트]
      # ==============================================================================
      if bottom_score >= 2:
        bottom_status_str = f"<b>(당일 진바닥 지표 {bottom_score}개 터치 달성!)</b>"
        if is_stop_loss_triggered:
          bottom_action_str = (
              f"→ <b>[비상 후퇴]</b> 바닥권 전저점 이탈로 매수 금지"
          )
        elif is_on_the_wall or is_target_reached:
          bottom_action_str = (
              "→ <b>[바닥 탈출 완료]</b> 성벽 도달로 진바닥 임무 완수! (추가"
              " 매수 금지 / 익절 준비)"
          )
        elif is_down_trend_v:
          bottom_action_str = (
              "→ <b>[투매 칼날 경계]</b> 지표 터치했으나 하락 음봉 투매"
              " 진행으로 매수 금지 및 관망"
          )
        elif vol_strength < 80:
          bottom_action_str = (
              "→ <b>[입질 대기]</b> 지표 충족이나 거래량"
              f" 부족({vol_strength:.1f}점)으로 매수 보류"
          )
        elif is_macd_reverse_deepening:
          bottom_action_str = (
              "→ <b>[매수 보류]</b> MACD 엔진 역회전 심화 중이므로 진입 금지"
          )
        elif not is_valid_bottom_candle:
          bottom_action_str = (
              "→ <b>[캔들 대기]</b> 지표 충족했으나 음봉 매도세 지속으로 매수"
              " 보류"
          )
        elif is_escape_buy_signal:
          bottom_action_str = (
              "→ <b>[2단계 진바닥 탈출]</b> 바닥 다진 후 5일선 위 안착 성공! 추가"
              " 매수 유효."
          )
        else:
          bottom_action_str = (
              "→ <b>[1단계 진바닥 입질 매수]</b> 지표 충족 + 거래량 유입 + 바닥"
              " 지지! 소량 입질 매수 시작."
          )
      elif recent_bottom_memory:
        bottom_status_str = f"<b>(최근 2~3일 내 진바닥 확인 완료!)</b>"
        if is_stop_loss_triggered:
          bottom_action_str = (
              f"→ <b>[비상 후퇴]</b> 바닥권 전저점 이탈로 매수 금지"
          )
        elif is_on_the_wall or is_target_reached:
          bottom_action_str = (
              "→ <b>[바닥 탈출 완료]</b> 성벽 도달로 2단계 탈출 임무 완수! (추가"
              " 매수 금지 / 익절 준비)"
          )
        elif is_over_extended_5:
          bottom_action_str = (
              f"→ <b>[추격 매수 금지]</b> 5일선 대비 +{bias_ma5:.1f}% 과다이격"
              " 발생으로 관망 대기."
          )
        elif not is_valid_buy_candle:
          bottom_action_str = (
              "-> <b>[캔들 대기]</b> 5일선 안착했으나 유효 지지캔들 미충족으로"
              " 관망."
          )
        elif not is_bandwidth_ok:
          bottom_action_str = f"→ <b>[밴드폭 대기]</b> {bw_diag_msg} 관망."
        elif is_escape_buy_signal:
          bottom_action_str = (
              "→ <b>[2단계 진바닥 탈출]</b> 바닥 다진 후 5일선 위 안착 성공! 추가"
              " 매수 유효."
          )
        elif not is_ma5_safe:
          bottom_action_str = (
              "→ <b>[5일선 안착 대기]</b> 바닥은 확인되었으나 5일선 돌파 대기 중"
              " 관망."
          )
        elif vol_strength < 80:
          bottom_action_str = (
              "→ <b>[거래량 대기]</b> 5일선 위 안착했으나 거래량"
              f" 부족({vol_strength:.1f}점)으로 관망."
          )
        else:
          bottom_action_str = f"→ <b>[관망]</b> 추세 안착 대기 중."
      else:
        bottom_status_str = "<b>(조건 미흡)</b>"
        bottom_action_str = "➔ <b>[관망]</b> 진바닥 지표 조건 미충족"

      # 눌림목 판정
      if is_escape_buy_signal:
        pullback_status_str = f"<b>(밴드폭 {bandwidth:.1f}% / 진바닥 구간)</b>"
        pullback_action_str = (
            "-> <b>[진바닥 반등]</b> 바닥 탈출 국면이므로 5일선 사수 기준으로"
            " 대응"
        )
      elif is_down_trend_structural:
        pullback_status_str = f"<b>(대세 역배열 하락 추세 / 밴드폭 {bandwidth:.1f}%)</b>"
        if not is_ma5_safe:
          pullback_action_str = (
              "-> <b>[진바닥 탐색 중]</b> 역배열 지하실 하락 진행형 (5일선"
              " 미안착 / 칼날 관망)"
          )
        else:
          pullback_action_str = (
              "-> <b>[진바닥 안착 시도]</b> 5일선 회복 시도 중이나 역배열 저항"
              " 경계"
          )
      elif not is_bandwidth_ok:
        pullback_status_str = (
            f"<b>(밴드폭 {bandwidth:.1f}% / {bw_status_category})</b>"
        )
        pullback_action_str = f"-> <b>[매수 보류]</b> {bw_diag_msg}"
      else:
        pullback_status_str = (
            f"<b>(밴드폭 {bandwidth:.1f}% / {bw_status_category})</b>"
        )
        if pullback_rebound_score == 0:
          pullback_action_str = "-> <b>[관망]</b> 눌림목 지표 조건 미충족"
        elif pullback_rebound_score < 2:
          pullback_action_str = (
              "-> <b>[지표 미흡]</b> 눌림목 동조 점수"
              f" 부족({pullback_rebound_score}점)으로 돌파/안착 대기"
          )
        elif is_over_extended_5 and (p >= mid_line):
          pullback_action_str = (
              f"-> <b>[추격 매수 금지]</b> 5일선 대비 +{bias_ma5:.1f}% 과다이격"
              " 발생으로 눌림목 지지 대기"
          )
        elif not is_valid_buy_candle:
          pullback_action_str = (
              "-> <b>[캔들 확인 대기]</b> 눌림목 영역이나 캔들 지지(양봉/밑꼬리)"
              " 미흡으로 관망"
          )
        elif is_macd_reverse_deepening:
          pullback_action_str = (
              "-> <b>[엔진 역회전 심화]</b> MACD 하락 가속 중이므로 관망"
          )
        elif is_pullback_buy_signal:
          pullback_action_str = (
              "-> <b>[3단계 눌림목 추가 매수]</b> 5·20일선 위 안착 + 지표 동조"
              " 확인, 승수 확대 진격!"
          )
        else:
          pullback_action_str = (
              "-> <b>[돌파/안착 대기]</b> 상방 공방 및 이격 조율 중 관망"
          )

      if (
          is_escape_buy_signal
          or bottom_score >= 2
          or recent_bottom_memory
          or is_down_trend_structural
      ):
        if is_down_trend_structural and not (
            is_escape_buy_signal or bottom_score >= 2 or recent_bottom_memory
        ):
          sub_indicator_str = (
              f"   - <b>진바닥 탐색 현황:</b> {pullback_status_str}"
              f" {pullback_action_str}"
          )
        else:
          sub_indicator_str = (
              f"   - <b>진바닥 입질 동조:</b> {bottom_score}개 터치"
              f" {bottom_status_str} {bottom_action_str}"
          )
      else:
        sub_indicator_str = (
            f"   - <b>눌림목 동조:</b> {pullback_rebound_score}/3점"
            f" {pullback_status_str} {pullback_action_str}"
        )

      indicator_verify_text = (
          f"{ma_price_summary}<br>• <b>[추세 정밀 판독]:</b>"
          f" {trend_status}<br>• <b>[지표 검증"
          f" 연산]</b><br>{sub_indicator_str}{squeeze_info_str}"
      )

      # 보유 평단가 맞춤형 실전 대응 가이드
      ma5_dynamic_stop = dynamic_stop_price

      if user_avg_price <= 0:
        holder_guide_msg = (
            f"현재 추세 탐색 및 방향 정립 구간이니"
            f" 성벽({defense_line:{fmt_p}}{currency})이나 5일선 사수 여부를"
            " 확인하며 차분히 보유 판단을 내리시게. (★ <b>손절 마지노선:"
            f" {stop_loss_label}</b>)"
        )
      else:
        profit_rate = ((p - user_avg_price) / user_avg_price) * 100
        if p >= user_avg_price:
          holder_guide_msg = (
              f" • <b>[수익권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} /"
              f" 수익률: +{profit_rate:.2f}%)]</b><br> • <b>기세 지속:</b>"
              f" 5일선({ma5_val:{fmt_p}}{currency})을 이탈하지 않는 한 성벽 및"
              " 수확목표선까지 추세를 즐기시게.<br> • <b>단기 트레이딩:</b> 5일선"
              f" -{dynamic_stop_pct:.1f}% 이탈 시 수익 보존을 위해 일부 분할"
              f" 익절({ma5_dynamic_stop:{fmt_p}}{currency})<br> • <b>수익"
              " 확정선:</b> 성벽 위 음봉 발생 또는 볼린저 상단 도달 시 분할 매도"
              " 집행."
          )
        else:
          holder_guide_msg = (
              f" • <b>[손실권 보유자 (평단가: {user_avg_price:{fmt_p}}{currency} /"
              f" 손실률: {profit_rate:.2f}%)]</b><br> •"
              f" <b>5일선({ma5_val:{fmt_p}}{currency}) 아래에서는 추측 추가"
              " 매수(물타기)를 절대 금지하네.</b><br> • <b>단기 트레이딩:</b>"
              f" 5일선 -{dynamic_stop_pct:.1f}% 이탈 시 추가 하락 방어를 위해"
              f" 비중 조절({ma5_dynamic_stop:{fmt_p}}{currency})<br> • <b>최후"
              f" 방어선:</b> 바닥권"
              f" 전저점({stop_loss_price:{fmt_p}}{currency}) 이탈 시 미련 없이"
              " 전량 칼손절 후퇴."
          )

      # 신호등 박스 설명문 (s_adv) 완벽 동기화
      if final_code == "STOP_LOSS_ALERT":
        s_adv = (
            f" • <b>[긴급 집행] {stop_reason}!</b> 추가 손실을 막기 위해 미련 없이"
            " 즉시 전량 칼손절 후퇴하시게."
        )
      elif final_code == "RED_SELL_TARGET":
        s_adv = (
            " • <b>[수확 완료]</b> 수확 목표선에 거뜬히 도달했네! 물량"
            " 30~50%를 매도하며 수익을 확실하게 챙기시게.<br> • <b>[미보유자]</b>"
            " 고가 추격 매수 절대 금지!"
        )
      elif final_code == "RED_SELL_WARNING":
        s_adv = (
            " • <b>[경계 태세]</b> 성벽(방어선) 위에서 음봉이 발생했네! 5일선"
            " 지지 여부를 확인하며 기세가 꺾일 때를 대비해 분할 익절 준비를"
            " 하시게."
        )
      elif final_code == "YELLOW_CAUTION":
        s_adv = (
            " • <b>[경계 태세]</b> 성벽(방어선) 위 진입! 추격 매수는 철저히"
            " 차단하고, <b>수확</b> 목표선 도달 시 매도할 준비를 하시게."
        )
      elif final_code == "WAIT_OVER_EXTENDED":
        s_adv = (
            f" • <b>[과다이격 경계]</b> 5일선 대비 +{bias_ma5:.1f}% 벌어져 단기"
            " 과열 구간이오! 5일선 부근으로 이격을 좁힐 때까지 추격 매수 절대"
            " 금지."
        )
      elif final_code == "BOTTOM_ENTRY":
        if not is_afternoon_safe_time:
          s_adv = (
              f" • <b>[입질 포착]</b> 진바닥 터치 완료! <b>{time_rule_desc} 후"
              " 소량 진격</b>하시게."
          )
        else:
          s_adv = (
              f" • <b>[입질 진격]</b> {time_rule_pass} 소량 씨앗 뿌리기 진격"
              " (전저점 방어선 철저 준수)."
          )
      elif final_code == "ESCAPE_BUY":
        if not is_afternoon_safe_time:
          s_adv = (
              " • <b>[탈출 포착]</b> 5일선 위 안착 기세 확인!"
              f" <b>{time_rule_desc} 추가 매수</b>하시게."
          )
        else:
          s_adv = (
              f" • <b>[추가 진격]</b> {time_rule_pass} 5일선 위 안착 완벽 사수!"
              " 배팅 비중을 늘려 밭을 다짐."
          )
      elif final_code == "PULLBACK_BUY":
        if not is_afternoon_safe_time:
          s_adv = (
              " • <b>[승수 포착]</b> 5·20일선 위 활주로 확보!"
              f" <b>{time_rule_desc} 알짜배기 승수 확대</b>를 집행하시게."
          )
        else:
          s_adv = (
              f" • <b>[본진 진격]</b> {time_rule_pass} 5·20일선 위 안착 및"
              " 지지력 검증 완료! 알짜배기 승수 확대 집행."
          )
      elif final_code in ["WAIT_INDICATOR", "WAIT_MACD"]:
        s_adv = (
            " • <b>[지표 검증 대기]</b> 5일선 위에 있으나 바닥 지표 미충족 또는"
            " MACD 하락세 지속 중이오! 뇌동 진입을 엄격히 금함."
        )
      elif final_code == "WAIT_DOWNTREND_FALL":
        s_adv = (
            " • <b>[칼날 주의]</b> 대세 역배열 하락 관성과 투매 음봉이 주가를"
            " 누르고 있네! 바닥을 치고 5일선 위로 올라타기 전까지 절대 칼을"
            " 뽑지 마시게."
        )
      elif final_code == "WAIT_PULLBACK":
        s_adv = (
            " • <b>[눌림목 지지 대기]</b> 20일선 영역이나 지표 동조 미흡 또는"
            f" 밴드폭 기준 미달! ({bw_diag_msg})"
        )
      elif final_code == "WAIT_VOLUME":
        s_adv = (
            " • <b>[수급 대기]</b> 기술적 바닥 신호는 충족했으나 거래량이"
            " 부족하니, 확실한 거래량 폭발 전까지 진입을 보류하시게."
        )
      else:
        s_adv = (
            " • <b>[관망 유지]</b> 확실한 바닥 신호나 매수/매도 조건이 맞을"
            " 때까지 손가락을 묶고 대기하시게."
        )

      st.markdown(
          f"<div class='signal-box' style='background-color:{col};'><p"
          f" class='signal-text'>{sig}</p><div"
          f" class='signal-subtext'>{s_adv}</div></div>",
          unsafe_allow_html=True,
      )

      c1, c2, c3 = st.columns(3)
      with c1:
        st.markdown(
            "<div class='price-card'><p>⚖️ 공략 대기선 (볼린저하단)</p><p"
            f" style='color:#388E3C;"
            f" font-size:32px;'>{format(low_b, fmt_p)}</p></div>",
            unsafe_allow_html=True,
        )
      with c2:
        st.markdown(
            "<div class='price-card'><p>🎯 수확 목표선 (볼린저상단)</p><p"
            f" style='color:#D32F2F;"
            f" font-size:32px;'>{format(target_price_100, fmt_p)}</p></div>",
            unsafe_allow_html=True,
        )
      with c3:
        st.markdown(
            "<div class='price-card'><p>🛡️ 성벽(방어선)</p><p"
            f" style='color:#E65100;"
            f" font-size:32px;'>{format(defense_line, fmt_p)}</p></div>",
            unsafe_allow_html=True,
        )

      # 실전 전략 1, 2번 문구 동기화
      if not is_ma5_safe:
        if final_code == "BOTTOM_ENTRY":
          ma5_guide_text = (
              f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency})"
              " 아래이나, 1단계 진바닥 지표 충족으로 소량 씨앗 뿌리기(선취매) 허용"
              " 구역이오."
          )
        else:
          ma5_guide_text = (
              f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency})"
              " 아래로 이탈했으니 종가 안착 전까진 손가락을 묶으시게."
          )
      else:
        if final_code == "ESCAPE_BUY":
          ma5_guide_text = (
              f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에"
              " 안착하며 2단계 진바닥 탈출 성공! 추가 매수 및 비중 확대"
              " 유효 구역이오."
          )
        else:
          ma5_guide_text = (
              f"현재가({p:{fmt_p}}{currency})가 5일선({ma5_val:{fmt_p}}{currency}) 위에"
              " 안착하여 단기 전투선이 살아있네. 본진 진격 가능구역이오."
          )

      if defense_line > up_b:
        def_status = (
            f"성벽({defense_line:{fmt_p}}{currency})이"
            f" 수확목표선({up_b:{fmt_p}}{currency})보다 높은 <b>[고점"
            " 매물대]</b> 구역이오! 1차 수확선에서 짧게 익절하고 관망하시게."
        )
      elif p >= defense_line:
        if p >= prev_p and p >= ma5_val:
          def_status = (
              f"성벽({defense_line:{fmt_p}}{currency}) 위에서 5일선 기세를 타고"
              " <b>위로 진격 중</b>이네! 든든한 방어선을 등지고 계속"
              " 밀어붙이시게."
          )
        else:
          def_status = (
              f"성벽({defense_line:{fmt_p}}{currency}) 위에는 있으나 단기"
              " 기세가 <b>숨고르기 중</b>이네! 성벽 위 음봉 발생 시 선제적 익절을"
              " 준비하시게."
          )
      else:
        if final_code == "BOTTOM_ENTRY":
          def_status = (
              f"성벽({defense_line:{fmt_p}}{currency}) 아래 극바닥권이나, 1단계"
              " 바닥 지표 동조로 <b>소량 입질 진격 타점</b>을 형성 중이네!"
          )
        elif final_code == "ESCAPE_BUY":
          def_status = (
              f"성벽({defense_line:{fmt_p}}{currency}) 아래이나, 5일선을"
              " 딛고 <b>2단계 바닥 탈출 진격</b>을 시작하며 성벽 탈환에 나서는"
              " 중이네!"
          )
        elif is_ma5_safe:
          def_status = (
              f"성벽({defense_line:{fmt_p}}{currency}) 아래에 있으나, 단기"
              " 5일선<b>(생명선)을 사수</b>하며 반격의 시동을 거는 중이네!"
          )
        else:
          def_status = (
              f"성벽({defense_line:{fmt_p}}{currency}) 아래로 함락된 채"
              " 기세마저 밑으로 처박히고 있네! <b>절대 칼을 뽑지 마시게.</b>"
          )

      st.markdown(
          f"""<div class='trend-card'>
<div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{ma5_guide_text}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>2. 성벽 사수 및 공방 확인</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{def_status}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>3. 중장기 추세 진단 및 지표 동조 현황</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{indicator_verify_text}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>4. 엔진(MACD) 확인</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{macd_strategy_msg}</span>
</div>
<div style='margin-bottom: 25px;'>
<span style='color: #D32F2F; font-weight: 900; font-size: 24px;'>5. 🛡️ [보유자 전용] 실전 행동 가이드</span><br>
<span style='color: #2E7D32; font-weight: bold; font-size: 20px;'>👉 {holder_guide_msg}</span>
</div>
<hr style='border:1px solid #FFEBEE; margin: 20px 0;'>
<div class='final-msg'>
{final_adv}
</div>
</div>""",
          unsafe_allow_html=True,
      )

      st.divider()

      # 하단 4대 핵심 지표 박스
      i1, i2, i3, i4 = st.columns(4)

      with i1:
        if final_code == "BOTTOM_ENTRY":
          bb_diag = (
              f"🔴 <b>[1단계 진바닥 입질 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
              " <b>역할:</b> 과매도 바닥권 선취매.<br>• <b>진단:</b> 지표 터치 +"
              " 거래량 유입 + 바닥 지지! 소량 입질 매수 시작 (전저점 마지노선"
              " 준수)."
          )
        elif final_code == "ESCAPE_BUY":
          bb_diag = (
              f"🟢 <b>[2단계 진바닥 탈출 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
              " <b>역할:</b> 5일선 안착 후 배팅 확대.<br>• <b>진단:</b>"
              f" {bw_diag_msg}. 5일선 위 안착 성공! 추가 매수로 비중 확대."
          )
        elif final_code == "WAIT_VOLUME":
          bb_diag = (
              f"🟡 <b>[수급 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
              " <b>역할:</b> 속임수 반등 차단.<br>• <b>진단:</b> 바닥 기술"
              " 지표는 달성했으나 거래량이 부족하니, 확실한 수급 유입 전까지"
              " 진입 보류."
          )
        elif final_code == "WAIT_DOWNTREND_FALL":
          bb_diag = (
              "🟡 <b>[진바닥 탐색/칼날 관망 구역] (밴드폭:"
              f" {bandwidth:.1f}%)</b><br>• <b>역할:</b> 떨어지는 칼날"
              " 회피.<br>• <b>진단:</b> 대세 역배열 하락 구간이오. 5일선 안착"
              " 전까지 절대 매수하지 말고 관망하시게."
          )
        elif final_code == "PULLBACK_BUY":
          bb_diag = (
              f"🔵 <b>[3단계 눌림목 추가 매수 구역] (밴드폭:"
              f" {bandwidth:.1f}%)</b><br>• <b>역할:</b> 추세 속 승수 확대.<br>•"
              f" <b>진단:</b> {bw_diag_msg}. 5·20일선 위 안정적 안착 및 활주로"
              " 확보로 알짜배기 추가 매수 집행."
          )
        elif final_code in ["RED_SELL_TARGET", "RED_SELL_WARNING"]:
          bb_diag = (
              "🔴 <b>[성벽 위 수확 및 음봉 익절 구간]</b><br>• <b>역할:</b> 고점"
              " 수익 확정.<br>• <b>진단:</b> 목표선 도달 또는 성벽 위 음봉"
              " 발생으로 선제적 익절 실행."
          )
        elif final_code == "YELLOW_CAUTION":
          bb_diag = (
              "🟡 <b>[성벽 위 경계 및 추격 차단 구역]</b><br>• <b>역할:</b>"
              " 고가 추격 매수 원천 차단.<br>• <b>진단:</b> 성벽 위 공방"
              " 중이므로 신규 매수를 금지하고 익절 타이밍을 노림."
          )
        elif final_code == "WAIT_OVER_EXTENDED":
          bb_diag = (
              "🟡 <b>[과다이격 추격 금지 구역] (5일선 이격:"
              f" +{bias_ma5:.1f}%)</b><br>• <b>역할:</b> 고점 물림 방지.<br>•"
              " <b>진단:</b> 5일선 대비 5% 이상 벌어졌으니 5일선 부근 숨고르기까지"
              " 매수 보류."
          )
        elif final_code in ["WAIT_INDICATOR", "WAIT_MACD", "WAIT_PULLBACK"]:
          bb_diag = (
              f"🟡 <b>[지표/밴드폭 검증 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
              " <b>역할:</b> 속임수 휩소 방지.<br>• <b>진단:</b> 이평선에는"
              f" 닿았으나 세부 지표 및 밴드폭 기준 미달({bw_diag_msg})로 관망"
              " 유지."
          )
        else:
          bb_diag = (
              f"⚖️ <b>[관망 및 대기 구역] (밴드폭: {bandwidth:.1f}%)</b><br>•"
              " <b>역할:</b> 뇌동매매 방지.<br>• <b>진단:</b> 명확한 바닥/추세"
              " 신호가 뜰 때까지 손가락을 묶고 관망 유지."
          )

        st.markdown(
            "<div class='ind-box'><p class='ind-title'>Bollinger"
            f" (기세/위치)</p><p class='ind-diag'>{bb_diag}</p></div>",
            unsafe_allow_html=True,
        )

      with i2:
        rsi_trend = (
            "▲ 상승"
            if rsi_val > rsi_prev
            else ("▼ 하락" if rsi_val < rsi_prev else "─ 변동없음")
        )
        if rsi_val >= 60:
          r_status = (
              "<b>👿 불지옥 과열권</b><br>• <b>역할:</b> 매수 에너지 고갈"
              " 경보.<br>• <b>진단:</b> 과열 구간 진입, 성벽 위 익절 및 차익"
              " 실현을 준비하시게."
          )
        elif rsi_val <= 35:
          r_status = (
              "<b>🧊 냉골 바닥권</b><br>• <b>역할:</b> 진바닥 수급 에너지"
              " 감지.<br>• <b>진단:</b> 바닥권 지표 터치 및 거래량 유입 시 1단계"
              " 입질 매수 타이밍."
          )
        else:
          r_status = (
              "<b>⚖️ 적정 온도 구간</b><br>• <b>역할:</b> 에너지 충전 및"
              " 눌림목 동조.<br>• <b>진단:</b> 에너지 충전 중. 보조지표 고개"
              " 돌림을 주시하시게."
          )
        st.markdown(
            "<div class='ind-box'><p class='ind-title'>RSI (매수 온도)</p><p"
            " style='font-size:36px; color:#E65100; margin:10px"
            f" 0;'>{rsi_val:.2f} <span style='font-size:22px;"
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
        if will_val >= -20:
          w_status = (
              "<b>🚀 상방 돌파 도전 구역</b><br>• <b>역할:</b> 단기 상향 압력"
              " 측정.<br>• <b>진단:</b> 성벽 위 목표선 근접 구역이오. 음봉"
              " 발생 시 선제적 매도 대비."
          )
        elif will_val <= -80:
          w_status = (
              "<b>🏳️ 개미 항복 구역</b><br>• <b>역할:</b> 세력 선취매 및 반전"
              " 포착.<br>• <b>진단:</b> 🧊 <b>[바닥 침체]</b> -80 밑 투매 진행"
              " 중! 지표 동조 및 거래량 유입 시 입질 대기."
          )
        else:
          w_status = (
              "<b>⚖️ 중간 지대</b><br>• <b>역할:</b> 추세 방향 탐색.<br>•"
              " <b>진단:</b> 상/하방 방향 탐색 중."
          )
        st.markdown(
            "<div class='ind-box'><p class='ind-title'>Williams %R (민감"
            " 반전)</p><p style='font-size:36px; color:#E65100; margin:10px"
            f" 0;'>{will_val:.2f} <span style='font-size:22px;"
            f" color:#333333;'>({will_trend})</span></p><p"
            f" class='ind-diag'>{w_status}</p></div>",
            unsafe_allow_html=True,
        )

      with i4:
        if is_macd_accelerating:
          m_diag = (
              "<b>🔥 엔진 정회전 가속</b><br>• <b>역할:</b> 상승 추진력 폭발.<br>•"
              " <b>진단:</b> 성벽 사수하며 5일선 타고 목표선까지 거침없이"
              " 진격하시게."
          )
        elif is_macd_decelerating:
          m_diag = (
              "<b>⚠️ 엔진 정회전 둔화</b><br>• <b>역할:</b> 상승 탄력 저하"
              " 감지.<br>• <b>진단:</b> 상승세는 유지 중이나 추진력이 꺾였으니,"
              " 성벽 위 분할 익절을 준비하시게."
          )
        elif is_macd_recovering:
          m_diag = (
              "<b>🌤️ 역회전 감소</b><br>• <b>역할:</b> 하락 둔화 / 반등"
              " 시동.<br>• <b>진단:</b> 매도세 소멸 중! 5일선 안착(2단계) 및"
              " 거래량 확인 시 추매 준비하시게."
          )
        else:
          m_diag = (
              "<b>⚙️ 엔진 역회전 심화</b><br>• <b>역할:</b> 하락 조정 가속.<br>•"
              " <b>진단:</b> 하락 관성 지속. 신규 매수 및 물타기 금지,"
              " 관망하시게."
          )

        st.markdown(
            "<div class='ind-box'><p class='ind-title'>MACD (추세 엔진)</p><p"
            f" class='ind-diag'>{m_diag}</p></div>",
            unsafe_allow_html=True,
        )
  except Exception as e:
    st.error(f"👵 아이구! 오류: {e}")
