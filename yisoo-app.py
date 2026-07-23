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

# 1. 스타일 및 화면 구성
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36056", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-box * { color: #FFFFFF !important; }
    .signal-text { font-size: 65px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .final-msg { color: #D32F2F !important; font-size: 24px !important; font-weight: 900 !important; line-height: 1.5 !important; }
    .market-tag { background-color: #0D47A1; color: #FFFFFF !important; padding: 4px 12px; border-radius: 6px; font-size: 18px; margin-left: 10px; display: inline-block; }
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

st.title("🧐 이수할아버지의 냉정 진단기 v36056")
display_global_risk(); st.divider()

col_input, col_btn = st.columns([4, 1])
with col_input:
    symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "257720").strip()
with col_btn:
    st.write("") # 위치 맞춤용
    if st.button("🔄 실시간 시세 재조회"):
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

        curr_hour = now_local.hour
        curr_min = now_local.minute
        curr_time_val = curr_hour * 100 + curr_min

        if is_kr:
            if curr_time_val < 800:
                m_tag = "🌙 장개장 전"
            elif 800 <= curr_time_val < 900:
                m_tag = "🌅 장전 시간외 (프리장)"
            elif 900 <= curr_time_val <= 1530:
                m_tag = "☀️ 정규장 실시간"
            elif 1530 < curr_time_val <= 2000:
                m_tag = "🌆 장후 시간외 / 대체거래소"
            else:
                m_tag = "🌙 장마감 완료"
        else:
            if curr_time_val < 400:
                m_tag = "🌙 장개장 전"
            elif 400 <= curr_time_val < 930:
                m_tag = "🌅 미장 프리장 (Pre-Market)"
            elif 930 <= curr_time_val <= 1600:
                m_tag = "☀️ 미장 정규장 (Regular)"
            elif 1600 < curr_time_val <= 2000:
                m_tag = "🌆 미장 애프터마켓 (Post-Market)"
            else:
                m_tag = "🌙 장마감 완료"

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

           # ★ [네이버 실시간 시세 API 직통 연동: 장전/정규장/장후 시간외 단가 100% 정밀 파싱]
            try:
                # 네이버 모바일 실시간 기본 API (가장 빠르고 정확함)
                api_url = f"https://m.stock.naver.com/api/stock/{symbol}/basic"
                res = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=2).json()
                
                # 1. 정규장 및 기본 현재가 추출
                raw_now_p = str(res.get('nowPrice', '0')).replace(",", "")
                p = float(raw_now_p) if raw_now_p != '0' else float(df['Close'].iloc[-1])
                
                # 2. 장후 시간외 / 대체거래소 단가 존재 여부 정밀 확인
                over_time = res.get('overTimePriceDetails', None)
                if over_time and isinstance(over_time, dict):
                    ot_price = over_time.get('nowPrice', None)
                    if ot_price:
                        p = float(str(ot_price).replace(",", ""))
                elif over_time and isinstance(over_time, list) and len(over_time) > 0:
                    ot_price = over_time[0].get('nowPrice', None)
                    if ot_price:
                        p = float(str(ot_price).replace(",", ""))

                # 3. 실시간 거래량
                v_curr = float(str(res.get('accumulatedTradingVolume', 0)).replace(",", ""))
                
                # 4. 전일 대비 변동폭 및 변동률 기반 전일 종가 정밀 산출
                diff_price = float(str(res.get('compareToPreviousPrice', 0)).replace(",", ""))
                ratio_str = str(res.get('fluctuationsRatio', '0'))
                
                if '-' in ratio_str or float(ratio_str) < 0:
                    prev_p = p + diff_price
                else:
                    prev_p = p - diff_price
                    
            except:
                if not df.empty:
                    p = float(df['Close'].iloc[-1])
                    v_curr = float(df['Volume'].iloc[-1])
                    prev_p = float(df['Close'].iloc[-2]) if len(df) >= 2 else p
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
            
            if is_kr:
                s_h, s_m = 8, 0
                total_minutes = 720
            else:
                s_h, s_m = 4, 0
                total_minutes = 960

            m_start = now_local.replace(hour=s_h, minute=s_m, second=0, microsecond=0)
            
            if now_local < m_start: 
                vol_strength = v_ratio 
            else:
                elapsed = min(total_minutes, max(10, (now_local - m_start).seconds / 60))
                if now_local.weekday() >= 5: elapsed = total_minutes
                vol_strength = min(1000, v_ratio / (elapsed / total_minutes))
            
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
            
            defense_link_idx = min(21, len(df))
            defense_line = float(df['High'].iloc[-defense_link_idx:-1].max()) * 0.93 if len(df) > 1 else p * 0.93

            is_bullish = (ma5_val > mid_line and mid_line > ma60_val and ma60_val > ma120_val)
            is_bearish = (ma5_val < mid_line and mid_line < ma60_val and ma60_val < ma120_val)
            is_ma5_safe = (p >= ma5_val)

            if is_bullish: trend_status = "🔥 <b>[대세 정배열]</b> 우상향 성벽 구축 중"
            elif is_bearish: trend_status = "⚠️ <b>[대세 역배열]</b> 지하실 향하는 하락 추세"
            else: trend_status = "⚖️ <b>[추세 혼조/횡보]</b> 방향 탐색 중"

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
                    except:
                        kor_name = tk
                final_display_name = f"{kor_name} ({tk})"

            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'><p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{final_display_name} <span class='market-tag'>{m_tag}</span></p><p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>", unsafe_allow_html=True)

            if vol_strength >= 150: v_status, v_adv = "과열폭발", f"🔥 <b>[화력폭발]</b> 시간보정 강도 {vol_strength:.1f}점! 본진 진격 중이오."
            elif vol_strength >= 100: v_status, v_adv = "매집시작", f"🚀 <b>[매집시작]</b> 시간보정 강도 {vol_strength:.1f}점! 화력이 차오르네."
            elif vol_strength >= 80: v_status, v_adv = "정상화력", f"⚔️ <b>[정상화력]</b> 시간보정 강도 {vol_strength:.1f}점! 기세가 빳빳하구먼."
            else: v_status, v_adv = "기세부족", f"🧊 <b>[거래절벽]</b> 시간보정 강도 {vol_strength:.1f}점! 속지 마시게."
            
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1; margin-bottom:10px;'>📊 거래량 전황: {v_status} (실시간 {v_ratio:.1f}% / 5일평균대비)</div><div class='vol-sub-text'>{v_adv}</div></div>", unsafe_allow_html=True)

            bb_bottom       = 1 if p <= (low_b * 1.005) else 0
            rsi_bottom      = 1 if rsi_val <= 35 else 0
            williams_bottom = 1 if will_val <= -80 else 0
            bottom_score    = bb_bottom + rsi_bottom + williams_bottom

            bb_top       = 1 if p >= (up_b * 0.995) else 0
            rsi_top      = 1 if rsi_val >= 60 else 0
            williams_top = 1 if will_val >= -20 else 0 
            top_score    = bb_top + rsi_top + williams_top

            m_diff_curr, m_diff_prev = m_l - s_l, m_p - s_p
            is_engine_reverse = (m_l < s_l)
            is_reverse_shrinking = is_engine_reverse and (abs(m_diff_curr) < abs(m_diff_prev))
            is_macd_turning = (m_l < s_l and m_diff_curr > m_diff_prev)

            if top_score >= 2:
                sig, col, s_adv = "🟢 매도권 진입", "#388E3C", f"• {'👿 불지옥 문턱일세! 탐욕 버리고 익절하시게.' if rsi_val >= 70 else '• 다중 과열 지표 포착! 기세가 완연한 수확기일세.'} (매도 지표 일치도: {top_score}/3)"
            elif bottom_score >= 2:
                if is_bearish: sig, col, s_adv = "🟡 관망 및 대기 (역배열 주의)", "#FBC02D", f"• ⚠️ 다중 바닥({bottom_score}/3)이나 <b>[대세 역배열]</b> 구간이오!"
                elif not is_ma5_safe: sig, col, s_adv = "🟡 관망 및 대기 (5일선 이탈)", "#FBC02D", f"• ⚠️ 다중 바닥({bottom_score}/3)이나 단기 생명선 <b>[5일선 이탈]</b> 상태이오!"
                elif is_reverse_shrinking or is_macd_turning: 
                    sig, col, s_adv = "🎯 [명장의 선취매 타점]", "#E65100", f"• 🔥 <b>[필살 변곡점 포착]</b> 다중 바닥({bottom_score}/3) + 5일선 사수 완벽 일치!"
                elif is_engine_reverse: sig, col, s_adv = "🟡 관망 및 대기 (역회전 심화)", "#FBC02D", f"• ⚠️ 다중 바닥 지표({bottom_score}/3)이나 엔진 역회전 심화 중."
                else: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", f"• 🧊 다중 바닥, 5일선 사수 및 엔진 정회전 확정!"
            else:
                if is_bearish: sig, col, s_adv = "🟡 관망 및 대기 (역배열 하락중)", "#FBC02D", f"• ⚠️ 대세 역배열 하락 추세 중이네."
                elif not is_ma5_safe: sig, col, s_adv = "🟡 관망 및 대기 (5일선 아래)", "#FBC02D", f"• ⚠️ 단기 전투선인 5일선 아래에서 기세 허덕이는 중."
                else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", f"• 눈치싸움 중일세. (바닥동조: {bottom_score}/3 | 과열동조: {top_score}/3)"
            
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선 (볼린저하단)</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선 (볼린저상단)</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            if p >= defense_line:
                if p >= prev_p and p >= ma5_val:
                    def_status = f"성벽({format(defense_line, fmt_p)}) 위에서 5일선 기세를 타고 <b>위로 진격 중</b>이네! 든든한 방어선을 등지고 계속 밀어붙이시게."
                else:
                    def_status = f"성벽({format(defense_line, fmt_p)}) 위에는 있으나 단기 기세가 <b>아래로 꺾이는 중</b>일세. 방어선을 예의주시하시게."
            else:
                if is_ma5_safe:
                    def_status = f"성벽({format(defense_line, fmt_p)}) 아래에 있으나, 단기 5일선<b>(생명선)을 사수하며 성벽 탈환을 위한 반격의 시동</b>을 거는 중이네!"
                else:
                    if p > prev_p and m_l >= s_l:
                        def_status = f"성벽({format(defense_line, fmt_p)}) 아래(지하실)이나, 엔진 시동을 걸며 <b>반격 중</b>이네! 반전의 불씨를 지켜보시게."
                    else:
                        def_status = f"성벽({format(defense_line, fmt_p)}) 아래로 함락된 채 기세마저 <b>밑으로 처박히고 있네</b>! 절대 칼을 뽑지 마시게."

            if top_score >= 2 or p >= up_b * 0.99 or rsi_val >= 60:
                if vol_strength >= 150 and p > defense_line:
                    final_adv = f"🚀 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 화력 폭발하며 수확 목표선 도달! <b>비중 유지 및 홀딩!</b>"
                else:
                    final_adv = f"💰 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 다중 과열권 및 수확기 진입! <b>욕심 버리고 야금야금 분할 익절 시작!</b>"
            elif bottom_score >= 2 and is_ma5_safe and (is_reverse_shrinking or is_macd_turning or m_l >= s_l):
                final_adv = f"🏹 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 다중 바닥 및 <b>5일선({ma5_val:{fmt_p}}) 안착 완료</b>! 소량 <b>[분할 매수]</b> 타이밍이오!"
            else:
                if not is_ma5_safe and bottom_score >= 2:
                    final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 바닥 지표는 좋으나 단기 5일선 아래라 <b>가짜 반등 우려! 무조건 5일선 회복 때까지 대기!</b>"
                elif m_l < s_l:
                    if is_macd_turning:
                        final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 중간 지대에서 엔진 역회전폭 급감 중이네. <b>무조건 관망 및 대기!</b>"
                    else:
                        final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 중간 지대에서 엔진 역회전 심화 중이네. <b>무조건 관망 및 대기!</b>"
                else:
                    if p <= (low_b * 1.02):
                        final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 엔진은 정회전이나 성벽 아래일세. <b>추가 진격 금지 및 관망!</b>" if p < defense_line else f"🔮 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 바닥권에서 엔진 정회전 및 5일선 사수 중이네! <b>강력 매수 검토!</b>"
                    else:
                        final_adv = f"🧐 <b>[최종 결론]</b> 보정강도({vol_strength:.1f}점). 엔진 정회전이나 추세 탐색 중일세. <b>무조건 관망 및 대기!</b>"

            if is_bearish:
                final_adv = f"🚨 <b>[냉정 경고]</b> 현재 <b>[대세 역배열(하락 추세)]</b> 구간이네! 단기 바닥 신호에 속아 진격하면 지하실로 끌려가니 <b>무조건 관망 및 반등 시 탈출!</b>"

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
<div style='margin-bottom: 25px;'>
<span style='color: #1565C0; font-weight: 900; font-size: 24px;'>4. 엔진(MACD) 확인</span><br>
<span style='color: #333333; font-weight: bold; font-size: 20px;'>{'다중 바닥 권역 + 5일선 사수 상태에서 엔진 시동 중이네! 소량 분할 매수 기회.' if (bottom_score >= 2 and is_ma5_safe and (is_reverse_shrinking or is_macd_turning or m_l >= s_l)) else ('바닥 지표는 들어왔으나 5일선 아래에 처박혀 있소. 회복 대기!' if (not is_ma5_safe and bottom_score >= 2) else (('엔진 역회전폭 급감 중이네! 시동 걸 채비 중이니 대기하시게.' if is_macd_turning else '엔진 역회전 심화 중이네! 거꾸로 도는 차니 절대 속지 마시게.') if m_l < s_l else '엔진 정회전 완료! 본대 진격 신호탄이 터졌네.'))}</span>
</div>
<hr style='border:1px solid #FFEBEE; margin: 20px 0;'>
<div class='final-msg'>
{final_adv.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')}
</div>
</div>""", unsafe_allow_html=True)

            st.divider()
            i1, i2, i3, i4 = st.columns(4)
            
            with i1:
                if p >= up_b: 
                    bb_diag = "👺 <b>[천장 돌파]</b> 울타리 밖으로 기세 폭발! 탐욕의 끝단이니 익절하시게."
                elif p <= low_b: 
                    bb_diag = "🧊 <b>[바닥 돌파]</b> 지하실까지 밀렸구먼. 엔진 시동을 기다리시게."
                elif p >= mid_line: 
                    if is_ma5_safe:
                        bb_diag = "🔥 <b>[중앙선 안착]</b> 중앙선 위이자 5일선 사수 중! 기세가 살아있네."
                    else:
                        bb_diag = "⚠️ <b>[과열 진입]</b> 중앙선 위이나 5일선 아래로 이탈했으니 주의하시게."
                else:
                    if is_ma5_safe:
                        bb_diag = "🏹 <b>[중앙선 아래 반격]</b> 중앙선 밑이나 5일선 사수하며 고개 드는 중! 반전 주시."
                    else:
                        if m_l < s_l:
                            if abs(m_l - s_l) >= abs(m_diff_prev): 
                                bb_diag = "🏠 <b>[기세 둔화]</b> 중앙선 밑 + 5일선 이탈. 엔진 역회전 심화 중이니 대기하시게."
                            else: 
                                bb_diag = "🏠 <b>[기세 둔화]</b> 중앙선 밑 + 5일선 이탈. 엔진 역회전폭 급감 중이니 회복을 기다리시게."
                        else: 
                            bb_diag = "🏠 <b>[기세 둔화]</b> 중앙선 밑이나 엔진 정회전 중. 기세를 냉정하게 보시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2:
                rsi_trend = "▲ 상승" if rsi_val > rsi_prev else ("▼ 하락" if rsi_val < rsi_prev else "─ 변동없음")
                is_div = p > prev_p and rsi_val < rsi_prev
                
                if rsi_val >= 60: r_status = f"<b>👿 불지옥</b> 문턱! {'🚨 가짜 상승이니 대피하시게.' if is_div else '수익 챙길 채비 하시게.'}"
                elif rsi_val <= 35: 
                    if rsi_val > rsi_prev: r_status = "<b>🧊 냉골 바닥</b>이나, 온도가 올라오며 <b>[지수 개선]</b> 중일세."
                    else: r_status = "<b>🧊 냉골 바닥</b>일세. 온도가 계속 떨어지며 <b>[지속 하락]</b> 중."
                else: r_status = f"중립일세. {'🚨 가짜 기세니 눈 부라리고 보시게.' if is_div else '끝단을 기다리시게.'}"
                
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f} <span style='font-size:25px; color:#333333;'>({rsi_trend})</span></p><p class='ind-diag'>● {r_status}</p></div>", unsafe_allow_html=True)
            
            with i3:
                will_trend = "▲ 상승" if will_val > will_prev else ("▼ 하락" if will_val < will_prev else "─ 변동없음")
                if will_val >= -20: w_status = "<b>🚩 천장 광기</b>! 비수 꽂히기 전에 수확하시게."
                elif will_val >= -35: w_status = "<b>⚠️ 천장 근접</b>! 고점 징후니 주시하시게."
                elif will_val <= -80: 
                    if will_val > will_prev: w_status = "<b>🏳️ 개미 항복 구역</b>이나, 기운이 고개를 들며 <b>[지수 개선]</b> 중."
                    else: w_status = "<b>🏳️ 개미 항복 구역</b>일세. 지속 하락 중."
                elif will_val <= -65: 
                    if will_val > will_prev: w_status = "<b>📉 낙폭 과대</b> 구역이나, 하락 브레이크 잡히는 중."
                    else: w_status = "<b>📉 하락 가속</b>! 절대 칼 뽑지 마시게."
                else: w_status = "중간 지대일세. 기세를 냉정하게 지켜보시게."
                
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f} <span style='font-size:25px; color:#333333;'>({will_trend})</span></p><p class='ind-diag'>● {w_status}</p></div>", unsafe_allow_html=True)
            
            with i4:
                if m_l > s_l: m_diag = "● 엔진 <b>정회전(헛바퀴)</b>! 성벽 무너졌으니 속지 마시게." if p < defense_line else "● 엔진 <b>정회전</b>! 성벽 사수하며 자신 있게 진격하시게."
                else: m_diag = "● 엔진 <b>역회전폭 급감</b>! 시동 걸 채비 중." if m_diff_curr > m_diff_prev else "● 엔진 <b>역회전 심화</b>! 자숙하시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
