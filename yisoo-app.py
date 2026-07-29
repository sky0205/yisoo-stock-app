import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

# --- [보급로 최적화 캐싱 장치: 반응속도 극대화 조율] ---
@st.cache_data(ttl=3600)
def load_krx_listing():
    try: return fdr.StockListing('KRX')
    except: return pd.DataFrame()

@st.cache_data(ttl=10) # 10초 단위로 신선도 유지
def fetch_global_market():
    nasdaq = yf.Ticker("^IXIC").fast_info
    sp500 = yf.Ticker("^GSPC").fast_info
    dow = yf.Ticker("^DJI").fast_info
    tnx = yf.Ticker("^TNX").fast_info
    usdkrw = yf.Ticker("USDKRW=X").fast_info
    return {
        "n_last": nasdaq.last_price, "n_prev": nasdaq.previous_close,
        "s_last": sp500.last_price, "s_prev": sp500.previous_close,
        "d_last": dow.last_price, "d_prev": dow.previous_close,
        "t_last": tnx.last_price, "t_prev": tnx.previous_close,
        "u_last": usdkrw.last_price, "u_prev": usdkrw.previous_close
    }

# --- ⚔️ 켈리 공식(Kelly Criterion) 정밀 자금관리 연산 장치 ---
def calculate_kelly_size(win_rate, win_loss_ratio, fraction=0.5):
    b = win_loss_ratio
    p = win_rate
    q = 1.0 - p
    f_star = (p * b - q) / b
    
    if f_star <= 0:
        return 0.0 # 기대값이 음수이면 매수 금지 (0%)
    
    safe_kelly = min(30.0, f_star * fraction * 100)
    return round(safe_kelly, 1)

# 1. 스타일 및 화면 구성
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36058", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-box * { color: #FFFFFF !important; }
    .signal-text { font-size: 48px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .signal-subtext { font-size: 22px !important; color: #FFFFFF !important; line-height: 1.6; margin-top: 10px; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
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
        background: linear-gradient(90deg, #283593 0%, #3F51B5 100%) !important;
        color: #FFEB3B !important;
        border-color: #FFFFFF !important;
    }
    div.stButton > button * {
        color: #FFFFFF !important;
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
        
        macro_alerts = []
        if tnx_val >= 4.5: 
            macro_alerts.append(f"🚨 [금리 발작] 국채 금리 {tnx_val:.3f}% 돌파!")
        
        if u_val >= 1500:
            macro_alerts.append(f"☠️ [환율 대공황 비상] 원/달러 {u_val:,.2f}원! 1,500원선 완전 붕괴! 과거 1,550원 악몽 재현, 국가 경제 및 증시 전면 초토화 경보!")
        elif u_val >= 1480:
            macro_alerts.append(f"☠️ [환율 초비상] 원/달러 {u_val:,.2f}원! 1,480원 임계점 폭풍 돌파, 외인 자금 대이탈 경보!")
        elif u_val >= 1450:
            macro_alerts.append(f"🚨 [환율 격랑] 원/달러 {u_val:,.2f}원! 1,480원 고지를 목전에 둔 마지노선 위협!")
        elif u_val >= 1400:
            macro_alerts.append(f"⚠️ [환율 경계] 원/달러 {u_val:,.2f}원! 1,400원대 고착화 주의!")
        
        if u_chg > 0.3:
            macro_alerts.append(f"📈 [환율 급등] 오늘 환율 {u_chg:+.2f}% 치솟는 중!")
        elif u_chg < -0.3:
            macro_alerts.append(f"📉 [환율 안정] 환율 {u_chg:+.2f}% 진정세.")
        
        if macro_alerts:
            adv = " ".join(macro_alerts)
        elif n_chg > 0.5 and tnx_chg < 0:
            adv = "🔥 [골디락스 진입] 지수 상승과 금리 하락, 기세 타시게."
        else:
            adv = "🧐 [눈치싸움 중] 세력들이 간 보고 있구먼."
        st.info(f"🧐 이수 할배의 글로벌 판독: {adv}")
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36058")
display_global_risk(); st.divider()

col_input, col_btn = st.columns([3, 2])
with col_input:
    symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "IONQ").strip()
with col_btn:
    st.write("") 
    if st.button("🔄 실시간 시세 재조회 및 정밀 분석 실행"):
        st.rerun()

if symbol:
    try:
        try:
            start_date = datetime.now() - timedelta(days=500)
        except Exception:
            start_date = datetime.now(ZoneInfo('UTC')) - timedelta(days=500)
            
        is_kr = symbol.isdigit()
        
        try:
            now_tz = ZoneInfo('Asia/Seoul') if is_kr else ZoneInfo('America/New_York')
            now_local = datetime.now(now_tz)
        except Exception:
            utc_now = datetime.now(ZoneInfo('UTC'))
            now_local = utc_now.astimezone(ZoneInfo('Asia/Seoul') if is_kr else ZoneInfo('America/New_York'))

        df = pd.DataFrame()
        p, v_curr = 0.0, 0.0
        us_prev_p = None

        if is_kr:
            currency, fmt_p = "원", ",.0f"
            try:
                df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            except:
                pass
            
            if df.empty:
                try:
                    df = yf.Ticker(f"{symbol}.KS").history(start=start_date)
                    if df.empty:
                        df = yf.Ticker(f"{symbol}.KQ").history(start=start_date)
                except:
                    pass

            try:
                url = f"https://finance.naver.com/item/main.naver?code={symbol}"
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=1)
                soup = BeautifulSoup(res.text, 'html.parser')
                p = float(soup.select_one(".no_today .blind").text.replace(",", ""))
                v_curr = float(soup.select(".no_info .blind")[3].text.replace(",", ""))
            except:
                if not df.empty:
                    p = float(df['Close'].iloc[-1])
                    v_curr = float(df['Volume'].iloc[-1])
        else:
            currency, fmt_p = "$", ",.2f"
            ticker = yf.Ticker(symbol.upper())
            
            try:
                df = ticker.history(start=start_date)
            except Exception:
                df = ticker.history(period="1y")
                
            try:
                info = ticker.fast_info
                p = getattr(info, 'last_price', float(df['Close'].iloc[-1]))
                v_curr = getattr(info, 'last_volume', float(df['Volume'].iloc[-1]))
                us_prev_p = info.previous_close
            except:
                pass
            
            if p == 0.0 and not df.empty:
                p = float(df['Close'].iloc[-1])
                v_curr = float(df['Volume'].iloc[-1])

        if df.empty:
            st.warning(f"⚠️ [{symbol}] 종목의 데이터를 불러오지 못했구먼. 종목번호를 다시 확인하거나 잠시 후 다시 시도해 주시게.")
        else:
            df = df.ffill().dropna()
            df.index = pd.to_datetime(df.index).date
            today_date = now_local.date()

            if not is_kr and us_prev_p and us_prev_p > 0:
                prev_p = us_prev_p
            else:
                if today_date in df.index:
                    temp_df = df.loc[df.index < today_date]
                    prev_p = float(temp_df['Close'].iloc[-1]) if not temp_df.empty else float(df['Close'].iloc[0])
                else:
                    prev_p = float(df['Close'].iloc[-1]) if len(df) > 0 else p

            if today_date in df.index:
                df.loc[today_date, 'Close'] = p
                df.loc[today_date, 'Volume'] = v_curr
                if p > df.loc[today_date, 'High']: df.loc[today_date, 'High'] = p
                if p < df.loc[today_date, 'Low']: df.loc[today_date, 'Low'] = p
            else:
                new_row = pd.DataFrame({
                    'Open': [p], 'High': [p], 'Low': [p], 'Close': [p], 'Volume': [v_curr]
                }, index=[today_date])
                df = pd.concat([df, new_row])

            v_avg5 = float(df['Volume'].iloc[-6:-1].mean()) if len(df) >= 6 else float(df['Volume'].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            
            p_diff = p - prev_p
            p_chg = (p_diff / prev_p) * 100 if prev_p > 0 else 0
            
            # 시간보정 거래량
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
                vol_strength = min(1000, v_ratio / (elapsed / total_minutes))
            else:
                vol_strength = v_ratio 

            # 보조지표 연산
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_series = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            rsi_val, rsi_prev = rsi_series.iloc[-1], rsi_series.iloc[-2]
            
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            will_series = (h14 - df['Close']) / (h14 - l14 + 1e-10) * -100
            will_val, will_prev = will_series.iloc[-1], will_series.iloc[-2]
            
            macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
            sig_line = macd.ewm(span=9).mean()
            m_l, s_l, m_p, s_p = macd.iloc[-1], sig_line.iloc[-1], macd.iloc[-2], sig_line.iloc[-2]
            
            df['MA5'] = df['Close'].rolling(5).mean()
            df['MA20'] = df['Close'].rolling(20).mean()
            df['MA60'] = df['Close'].rolling(60).mean()
            df['MA120'] = df['Close'].rolling(120).mean()
            df['Std'] = df['Close'].rolling(20).std()
            
            mid_line = df['MA20'].iloc[-1]; up_b = mid_line + (df['Std'].iloc[-1] * 2); low_b = mid_line - (df['Std'].iloc[-1] * 2)
            ma5_val = df['MA5'].iloc[-1] if len(df) >= 5 else mid_line
            ma60_val = df['MA60'].iloc[-1] if len(df) >= 60 else mid_line
            ma120_val = df['MA120'].iloc[-1] if len(df) >= 120 else mid_line
            
            prev_low_20 = float(df['Low'].iloc[-21:-1].min()) if len(df) > 20 else float(df['Low'].min())
            is_above_ma20 = (p >= mid_line)
            
            if is_above_ma20:
                stop_loss_price = mid_line
                stop_loss_label = f"20일선({mid_line:{fmt_p}})"
            else:
                stop_loss_price = prev_low_20
                stop_loss_label = f"전저점({prev_low_20:{fmt_p}})"

            defense_link_idx = min(21, len(df))
            defense_line = float(df['High'].iloc[-defense_link_idx:-1].max()) * 0.93 if len(df) > 1 else p * 0.93

            high_52w = float(df['High'].rolling(window=250, min_periods=1).max().iloc[-1])
            low_52w = float(df['Low'].rolling(window=250, min_periods=1).min().iloc[-1])
            is_new_high = (p >= high_52w * 0.99)
            is_new_low = (p <= low_52w * 1.01)

            is_bullish = (ma5_val > mid_line and mid_line > ma60_val and ma60_val > ma120_val)
            is_bearish = (ma5_val < mid_line and mid_line < ma60_val and ma60_val < ma120_val)
            is_ma5_safe = (p >= ma5_val)

            if is_bullish: trend_status = "🔥 <b>[대세 정배열]</b> 완벽한 우상향 성벽 구축 완료"
            elif is_bearish: trend_status = "⚠️ <b>[대세 역배열]</b> 지하실 향하는 하락 추세"
            elif ma5_val > mid_line: trend_status = "🌱 <b>[단기 반등 초입]</b> 5일선이 20일선 돌파! 상방 반전 시도 중"
            elif ma5_val < mid_line: trend_status = "📉 <b>[단기 조정 국면]</b> 5일선이 20일선 밑으로 밀려 숨고르기 중"
            else: trend_status = "⚖️ <b>[추세 혼조]</b> 방향 탐색 중"

            if is_kr:
                core_vault = {"005930": "삼성전자", "000660": "SK하이닉스", "033100": "제룡전기", "257720": "실리콘투", "058610": "에스피지"}
                final_display_name = core_vault.get(symbol, f"국내종목 ({symbol})")
                if symbol not in core_vault:
                    try:
                        url = f"https://finance.naver.com/item/main.naver?code={symbol}"
                        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=1)
                        soup = BeautifulSoup(res.text, 'html.parser')
                        final_display_name = soup.select_one(".wrap_company h2 a").text.strip()
                    except:
                        try:
                            df_krx_backup = load_krx_listing()
                            final_display_name = df_krx_backup[df_krx_backup['Code'] == symbol]['Name'].values[0]
                        except: pass
            else:
                us_vault = {
                    "TSLA": "테슬라", "NVDA": "엔비디아", "AAPL": "애플", 
                    "MSFT": "마이크로소프트", "AMZN": "아마존", "GOOGL": "알파벳A", 
                    "META": "메타", "IONQ": "아이온큐", "CPNG": "쿠팡", "NFLX": "넷플릭스"
                }
                tk = symbol.upper()
                kor_name = us_vault.get(tk, None)
                if not kor_name:
                    try:
                        info_dict = ticker.info
                        kor_name = info_dict.get('longName', info_dict.get('shortName', tk))
                    except: kor_name = tk
                final_display_name = f"{kor_name} ({tk})"

            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'><p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{final_display_name}</p><p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>", unsafe_allow_html=True)

            if is_bearish and vol_strength >= 100: v_status, v_adv = "역배열과열", f"⚠️ <b>[역배열 과열]</b> 시간보정 강도 {vol_strength:.1f}점! 하락 추세 속 속임수 거래량 주의."
            elif vol_strength >= 150: v_status, v_adv = "과열폭발", f"🔥 <b>[화력폭발]</b> 시간보정 강도 {vol_strength:.1f}점! 본진 진격 중이오."
            elif vol_strength >= 100: v_status, v_adv = "매집시작", f"🚀 <b>[매집시작]</b> 시간보정 강도 {vol_strength:.1f}점! 화력이 차오르네."
            elif vol_strength >= 80: v_status, v_adv = "정상화력", f"⚔️ <b>[정상화력]</b> 시간보정 강도 {vol_strength:.1f}점! 기세가 빳빳하구먼."
            else: v_status, v_adv = "거래절벽", f"🧊 <b>[거래절벽]</b> 시간보정 강도 {vol_strength:.1f}점! 수급이 마르고 동력이 없으니 속지 마시게."
            
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량 전황: {v_status} (실시간 {v_ratio:.1f}% / 5일평균대비)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            # 점수 연산
            bb_bottom = 1 if p <= (low_b * 1.005) else 0
            rsi_bottom = 1 if rsi_val <= 35 else 0
            williams_bottom = 1 if will_val <= -80 else 0
            bottom_score = bb_bottom + rsi_bottom + williams_bottom

            bb_top = 1 if p >= (up_b * 0.995) else 0
            rsi_top = 1 if rsi_val >= 60 else 0
            williams_top = 1 if will_val >= -20 else 0 
            top_score = bb_top + rsi_top + williams_top

            m_diff_curr, m_diff_prev = m_l - s_l, m_p - s_p
            is_engine_reverse = (m_l < s_l)
            is_reverse_shrinking = is_engine_reverse and (abs(m_diff_curr) < abs(m_diff_prev))
            is_macd_turning = (m_l < s_l and m_diff_curr > m_diff_prev)

            is_william_turn = (will_val > will_prev) or (will_val > -80)
            is_rsi_turn = (rsi_val > rsi_prev)
            is_macd_hist_up = (m_diff_curr > m_diff_prev) or (m_l >= s_l)
            is_indicator_turned_up = is_william_turn and is_rsi_turn

            pullback_rebound_score = (1 if is_rsi_turn else 0) + (1 if is_william_turn else 0) + (1 if is_macd_hist_up else 0)
            margin_to_target = (up_b - p) / p if p > 0 else 0
            is_too_close_to_top = margin_to_target < 0.02

            is_trend_buy_raw = (p >= mid_line) and (ma5_val >= mid_line) and is_ma5_safe and not is_too_close_to_top and (pullback_rebound_score >= 2)
            is_bottom_buy_raw = (bottom_score >= 2) and is_ma5_safe and (is_reverse_shrinking or is_macd_turning or m_l >= s_l) and is_indicator_turned_up

            # =========================================================================
            # ★ [최종 결론 연산]
            # =========================================================================
            holder_guide_msg = ""

            if is_new_high:
                final_code = "NEW_HIGH"
                final_adv = f"🚀 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[52주 신고가(무주공산)]</b> 영역 진격 중! 5일선 사수 기준 트레일링 스탑(분할 익절)으로 대응하시게!"
                holder_guide_msg = f"보유 물량은 5일선({ma5_val:{fmt_p}}) 사수 시 계속 홀딩하되, 이탈 시 50% 분할 익절하시게."

            elif is_new_low:
                final_code = "NEW_LOW"
                final_adv = f"🚨 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). <b>[52주 신저가(칼날 하락)]</b> 구역 전개! 5일선 안착 전까지 절대 무조건 관망하시게!"
                holder_guide_msg = f"함부로 물타지 마시고, 단기 반등 시 손절가({stop_loss_label}) 준수 후 비중 축소를 고려하시게."

            elif is_too_close_to_top or top_score >= 2 or p >= up_b:
                final_code = "SELL_ZONE"  # 🟢 매도 구간 (초록색)
                final_adv = f"🟢 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 주가가 수확 목표선(볼린저상단 {up_b:{fmt_p}}) 및 과열권 진입! 신규 진입은 금지하고 <b>[보유자]는 즉시 분할 매도로 수익 확정에 들어가시게!</b>"
                holder_guide_msg = f"🚨 <b>[수확 목표 달성!]</b> 수확목표선({up_b:{fmt_p}})에 다다랐으니 <b>보유 물량의 30~50%는 즉시 분할 매도(수익 확정)</b>하시게."

            elif is_trend_buy_raw:
                if vol_strength < 80:
                    final_code = "WAIT_GENERAL"
                    final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 20일선 지지는 확인되었으나 <b>[거래량 부족]</b>으로 동력이 없네! 수급 폭발 시까지 관망하시게!"
                    holder_guide_msg = f"성벽({defense_line:{fmt_p}})을 깨지 않는 한 느긋하게 홀딩하시게."
                else:
                    final_code = "PULLBACK_BUY"  # 🔵 눌림목 매수 구간 (파란색)
                    k_size = calculate_kelly_size(win_rate=0.65, win_loss_ratio=1.5, fraction=0.5)
                    final_adv = f"🔵 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 거래량 실린 20일선 지지 안착! <b>[추세 눌림목 매수 타점]</b>이시네. <b>[켈리 최적 비중: 자산의 {k_size}%]</b> 진격하되, <b>{stop_loss_label} 이탈 시 후퇴</b> 기준을 엄수하시게!"
                    holder_guide_msg = f"추세 정배열 파동이 살아있으니 수확 목표선({up_b:{fmt_p}})까지 자신감 있게 홀딩하시게."

            elif is_bottom_buy_raw:
                if vol_strength < 80:
                    final_code = "WAIT_GENERAL"
                    final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 바닥 지표는 안착했으나 <b>[거래량 부족]</b>으로 동력이 없네! 수급 폭발 시까지 관망하시게!"
                    holder_guide_msg = f"바닥 탈출 시도 중이나 추가 매수는 자제하고 5일선 사수 여부를 지켜보시게."
                else:
                    final_code = "BOTTOM_BUY"  # 🔴 바닥/선취매 매수 구간 (빨간색)
                    k_size = calculate_kelly_size(win_rate=0.45, win_loss_ratio=2.5, fraction=0.5)
                    final_adv = f"🔴 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 다중 바닥 및 거래량 유입 포착! <b>[진바닥 선취매 타점]</b>이시네. <b>[켈리 최적 비중: 자산의 {k_size}%]</b> 진격하되, <b>{stop_loss_label} 이탈 시 후퇴</b> 기준을 지키시게!"
                    holder_guide_msg = f"바닥 잡고 돌아서는 중이니 손절선({stop_loss_label})을 짧게 잡고 수확목표선까지 들고 가시게."

            else:
                final_code = "WAIT_GENERAL"  # 🟡 관망 구간 (노란색)
                holder_guide_msg = f"현재 추세 탐색 구간이니 성벽({defense_line:{fmt_p}})이나 5일선 사수 여부를 확인하며 차분히 보유 판단을 내리시게."
                if not is_above_ma20 and bottom_score >= 2:
                    final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 바닥 지표는 들어왔으나 20일선({mid_line:{fmt_p}}) 아래 역배열 상태이므로 관망하시게!"
                elif is_above_ma20 and pullback_rebound_score < 2:
                    final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 20일선 위에 있으나 보조지표 동조가 부족하네. 관망하시게!"
                elif not is_ma5_safe and bottom_score >= 2:
                    final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 바닥 지표는 들어왔으나 5일선 이탈 중일세. 관망하시게!"
                else:
                    final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 엔진 정회전이나 추세 탐색 중일세. 관망하시게!"

            # =========================================================================
            # ★ [신호등 메인 색상 4색 통일 연동 규칙]
            # 🟢 매도 / 🔴 매수(바닥) / 🔵 눌림목 / 🟡 관망
            # =========================================================================
            if final_code == "SELL_ZONE":
                sig = "🟢 [매도] 푸른 수확 / 이익실현 타점!"
                col = "#388E3C"  # 초록색
                s_adv = f"• <b>[보유자] 🚨 수확 목표 달성! 보유 물량 30~50% 즉시 현금화(매도)</b><br>• <b>[미보유자]</b> ✋ 추격매수 금지 (수확목표선 {up_b:{fmt_p}} 고점 저항대)"

            elif final_code == "BOTTOM_BUY":
                sig = "🔴 [매수] 불꽃 진격 / 진바닥 선취매!"
                col = "#D32F2F"  # 빨간색
                s_adv = f"• <b>[미보유자] 🎯 [진바닥 포착] 켈리 적정 비중으로 1차 매수 진격!</b><br>• <b>[보유자]</b> 🚀 손절가({stop_loss_label}) 사수하며 목표선까지 홀딩"

            elif final_code == "PULLBACK_BUY":
                sig = "🔵 [눌림목 매수] 냉철한 보급 / 추세 안착!"
                col = "#1976D2"  # 파란색
                s_adv = f"• <b>[미보유자] 🎯 [20일선 지지 반등] 거래량 실린 눌림목 매수 진격!</b><br>• <b>[보유자]</b> 🚀 수확목표선({up_b:{fmt_p}})까지 편안하게 추세 홀딩"

            else:  # WAIT_GENERAL, NEW_HIGH, NEW_LOW 등
                sig = "🟡 [관망] 방향 탐색 / 손가락 묶고 대기"
                col = "#FBC02D"  # 노란색
                if is_bearish: s_adv = "• ⚠️ 대세 역배열 하락 추세 중이니 보유/미보유 모두 관망하시게."
                elif not is_above_ma20: s_adv = f"• ⚠️ 주가가 20일선({mid_line:{fmt_p}}) 하단 저항을 받는 구간이네."
                elif not is_ma5_safe: s_adv = "• ⚠️ 단기 전투선인 5일선 아래에서 기세 허덕이는 중일세."
                else: s_adv = f"• 눈치싸움 중일세. (바닥동조: {bottom_score}/3 | 눌림동조: {pullback_rebound_score}/3)"

            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><div class='signal-subtext'>{s_adv}</div></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선 (볼린저하단)</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선 (볼린저상단)</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            if defense_line > up_b:
                def_status = f"성벽({defense_line:{fmt_p}})이 수확목표선({up_b:{fmt_p}})보다 높은 <b>[고점 매물대]</b> 구역이오! 1차 수확선에서 짧게 익절하고 관망하시게."
            elif p >= defense_line:
                if p >= prev_p and p >= ma5_val:
                    def_status = f"성벽({defense_line:{fmt_p}}) 위에서 5일선 기세를 타고 <b>위로 진격 중</b>이네! 든든한 방어선을 등지고 계속 밀어붙이시게."
                else:
                    def_status = f"성벽({defense_line:{fmt_p}}) 위에는 있으나 단기 기세가 <b>숨고르기 중</b>이네! 5일선 안착 여부를 관망하시게."
            else:
                if is_ma5_safe:
                    def_status = f"성벽({defense_line:{fmt_p}}) 아래에 있으나, 단기 5일선<b>(생명선)을 사수</b>하며 성벽 탈환을 위한 반격의 시동을 거는 중이네!"
                else:
                    if p > prev_p and m_l >= s_l:
                        def_status = f"성벽({defense_line:{fmt_p}}) 아래(지하실)이나, 엔진 시동을 걸며 <b>지하실 탈출 시도 중</b>이네!"
                    else:
                        def_status = f"성벽({defense_line:{fmt_p}}) 아래로 함락된 채 기세마저 밑으로 처박히고 있네! <b>절대 칼을 뽑지 마시게.</b>"

            if m_l > s_l:
                macd_strategy_msg = "엔진 정회전이나 성벽 아래(지하실)이므로 헛바퀴 주의! 성벽 회복 전까진 추격 금지." if p < defense_line else "엔진 정회전 완료! 성벽을 등지고 본대 진격 신호탄이 터졌네."
            else:
                macd_strategy_msg = "엔진 역회전폭 급감 중이네! 시동 걸 채비 중이니 회복을 관망하시게." if is_macd_turning else "엔진 역회전 심화 중이네! 거꾸로 도는 차니 절대 칼을 뽑지 마시게."

            st.markdown(f"""<div class='trend-card'>
<div class='trend-title'>⚔️ 실전 필살 대응 전략</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>1. 단기 생명선(5일선) 사수</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>현재가({p:{fmt_p}})가 5일선({ma5_val:{fmt_p}}) {'아래로 이탈했으니 기세가 꺾였구먼.' if not is_ma5_safe else '위에 안착하여 단기 전투선이 살아있네.'}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>2. 성벽 사수 확인</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{def_status}</span>
</div>
<div style='margin-bottom: 20px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>3. 중장기 추세 진단</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{trend_status} (5일선: {ma5_val:{fmt_p}} | 20일선: {mid_line:{fmt_p}} | 60일선: {ma60_val:{fmt_p}} | 120일선: {ma120_val:{fmt_p}})</span>
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
</div>""", unsafe_allow_html=True)

            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            
            with i1:
                if p >= up_b: bb_diag = "👺 <b>[천장 돌파]</b> 울타리 밖으로 기세 폭발! 탐욕의 끝단이니 익절하시게."
                elif p <= low_b: bb_diag = "🧊 <b>[바닥 돌파]</b> 지하실까지 밀렸구먼. 엔진 시동을 기다리시게."
                elif p >= mid_line: bb_diag = "🔥 <b>[중앙선 안착]</b> 중앙선 위이자 5일선 사수 중! 기세가 살아있네." if is_ma5_safe else "⚠️ <b>[과열 경계]</b> 중앙선 위이나 5일선 아래로 이탈했으니 주의하시게."
                else: bb_diag = "🏹 <b>[중앙선 아래 반격]</b> 중앙선 밑이나 5일선 사수하며 반격 시도 중!" if is_ma5_safe else "🏠 <b>[기세 둔화]</b> 중앙선 및 5일선 모두 이탈. 관망 및 대기가 상책이오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2:
                rsi_trend = "▲ 상승" if rsi_val > rsi_prev else ("▼ 하락" if rsi_val < rsi_prev else "─ 변동없음")
                is_div = p > prev_p and rsi_val < rsi_prev
                if rsi_val >= 60: r_status = f"<b>👿 불지옥</b> 문턱! {'🚨 가짜 상승이니 대피하시게.' if is_div else '수익 챙길 채비 하시게.'}"
                elif rsi_val <= 35: r_status = "<b>🧊 냉골 바닥</b>이나, 온도가 올라오며 <b>[지수 개선]</b> 중일세." if rsi_val > rsi_prev else "<b>🧊 냉골 바닥</b>일세. 지속 하락 중."
                else: r_status = f"중립일세. {'🚨 가짜 기세니 눈 부라리고 보시게.' if is_div else '끝단을 기다리시게.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f} <span style='font-size:25px; color:#333333;'>({rsi_trend})</span></p><p class='ind-diag'>● {r_status}</p></div>", unsafe_allow_html=True)
            
            with i3:
                will_trend = "▲ 상승" if will_val > will_prev else ("▼ 하락" if will_val < will_prev else "─ 변동없음")
                if will_val >= -20: w_status = "<b>🚩 천장 광기</b>! 비수 꽂히기 전에 수확하시게."
                elif will_val >= -35: w_status = "<b>⚠️ 천장 근접</b>! 고점 징후니 주시하시게."
                elif will_val <= -80: w_status = "<b>🏳️ 개미 항복 구역</b>이나, 기운이 고개를 들며 <b>[지수 개선]</b> 중." if will_val > will_prev else "<b>🏳️ 개미 항복 구역</b>일세. 지속 하락 중."
                elif will_val <= -65: w_status = "<b>📉 낙폭 과대</b> 구역이나, 하락 브레이크 잡히는 중." if will_val > will_prev else "<b>📉 하락 가속</b>! 절대 칼 뽑지 마시게."
                else: w_status = "중간 지대일세. 기세를 냉정하게 지켜보시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f} <span style='font-size:25px; color:#333333;'>({will_trend})</span></p><p class='ind-diag'>● {w_status}</p></div>", unsafe_allow_html=True)
            
            with i4:
                m_diag = "● 엔진 <b>정회전(헛바퀴)</b>! 성벽 아래이므로 속지 마시게." if (m_l > s_l and p < defense_line) else ("● 엔진 <b>정회전</b>! 성벽 사수하며 자신 있게 진격하시게." if m_l > s_l else ("● 엔진 <b>역회전폭 급감</b>! 시동 걸 채비 중." if is_macd_turning else "● 엔진 <b>역회전 심화</b>! 자숙하시게."))
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
