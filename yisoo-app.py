import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

import streamlit as st

# [재료 1] 글로벌 리스크 지표 함수
# 10번 줄부터 싹 지우시고 붙여넣으십시오!
def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 종합 전황 (90% 승률 필터)")
    
    # [급소 1] 소금 통을 먼저 준비합니다.
    us_advice = "🧐 [안개 장세] 데이터 판독 중일세..." 
    
    try:
        # 실시간 지수 획득
        nasdaq = yf.Ticker("^IXIC").fast_info
        sp500 = yf.Ticker("^GSPC").fast_info
        tnx = yf.Ticker("^TNX").fast_info
        
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        
        # [급소 2] 화면에 지수를 다시 그려줍니다.
        st.write(f"📈 **나스닥:** {nasdaq.last_price:.2f} ({n_chg:.2f}%)")
        # (SP500, TNX 등 다른 지수도 여기에 st.write로 그리십시오!)
        
        # 할배의 매서운 미장 판독 로직
        if n_chg < -0.5:
            us_advice = f"🚨 [미장 소나기] 나스닥 {n_chg:.2f}% 폭락 중! 홍수 속에 핀 꽃은 금방 시드네. 진격 금지!"
        elif n_chg > 0.5:
            us_advice = f"✅ [미장 쾌청] 나스닥 {n_chg:.2f}% 상승 중! 하늘이 맑으니 성벽 확인 후 진격 가능!"
        else:
            us_advice = "🧐 [안개 장세] 미장이 혼조세구먼. 무리하지 말고 낚싯대만 던져두시게."
            
        # [출구 1] 판독 완료 후 밖으로 던져주기
        return us_advice

    except Exception as e:
        # 에러가 나도 장부가 멈추지 않게 방어막을 칩니다.
        return "⚠️ [데이터 오류] 미장 전황을 읽을 수 없으니 일단 정박하십시오!"

# (hoka_check 등 다른 함수들이 지나갑니다...)

# [급소 3] 144번 줄: 검은 바탕 제거 및 할배 호통 출력
# 어르신 장부의 144번 줄(`st.markdown(f"...`) 부분을 아래 내용으로 갈아끼우십시오!
<div class='trend-item'>
    ● <b>필살 조언:</b><br>
    # <span style='color:#FF0000; font-weight:bold; font-size:1.2em; display:inline-block; margin:5px 0;'>{us_advice}</span><br>
    # <span class='advice-highlight'>{'⚠️ 신고가 추격 시: ' + format(p*0.95, fmt) + ' ' + currency + ' 이탈 시 손절!'}</span>
</div>
            # 5. 가격 전략 카드 (중앙선 추가)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선(하단)</p><p class='val-main' style='color:#388E3C;'>{format(low_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선(상단)</p><p class='val-main' style='color:#D32F2F;'>{format(up_b, fmt)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽 (방어선)</p><p class='val-main' style='color:#E65100;'>{format(defense_line, fmt)}</p></div>", unsafe_allow_html=True)

            # 6. 네 기둥 지수란 (볼린저 밴드 중앙선 기준 보완)
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                if p >= up_b: bb_pos, bb_color = "🔥 폭주", "#D32F2F"
                elif p <= low_b: bb_pos, bb_color = "📉 추락", "#1976D2"
                elif p > mid_line: bb_pos, bb_color = "⚖️ 눈치보기(상)", "#388E3C"
                else: bb_pos, bb_color = "⚖️ 눈치보기(하)", "#E65100"
                
                bb_diag = f"● 현재 **중앙선({format(mid_line, fmt)}) 위**에서 기세를 타는 중입니다. 상단 성벽 돌파 시도는 긍정적이나, 실패 시 중앙선까지 밀릴 수 있으니 주의하십시오." if bb_pos=="⚖️ 눈치보기(상)" else \
                          f"● 현재 **중앙선({format(mid_line, fmt)}) 아래**에서 빌빌대고 있습니다. 기운이 빠져 하단 성벽까지 밀릴 위험이 크니 섣부른 진격은 금물입니다." if bb_pos=="⚖️ 눈치보기(하)" else \
                          f"● 성벽 밖 **과열 권역**입니다. 평균 회귀 본능에 의해 조만간 차익 실현 소나기가 올 수 있으니 보따리 쌀 준비를 하십시오." if bb_pos=="🔥 폭주" else \
                          f"● 하단 성벽이 무너진 **공포 구간**입니다. 투매 비명소리가 잦아들 때까지 절대 칼날을 잡지 마십시오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-status' style='color:{bb_color};'>{bb_pos}</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2: # RSI
                r_stat = "👺 불지옥" if rsi_val > 65 else "🧊 냉골" if rsi_val < 35 else "미지근"
                r_diag = f"● 온도 {rsi_val:.2f}로 **탐욕의 불지옥** 직전입니다. 남들이 환호할 때 냉정하게 분할 매도로 수익을 확정 지으십시오." if r_stat=="👺 불지옥" else \
                         f"● 온도 {rsi_val:.2f}의 **냉골 상태**입니다. 지수가 30 근처까지 완전히 식어버릴 때까지 낚싯대만 던져두고 기다리십시오." if r_stat=="🧊 냉골" else \
                         f"● 매수와 매도가 팽팽한 **줄다리기** 중입니다. 방향성 없는 싸움에 끼어들어 수수료만 버리지 마십시오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams %R
                w_status = "🧨 광기폭발" if will_val > -35 else "🏳️ 개미항복" if will_val < -65 else "중간지대"
                w_diag = f"● **불나방 광기(-20↑)** 직전입니다! 지수 {will_val:.2f}는 천장 근처이니 추격하지 말고 후퇴를 준비하십시오." if will_val > -35 else \
                         f"● **항복 지점(-75↓)** 근처입니다. 지수 {will_val:.2f}로 바닥권이니 이제 분할 매수 보따리를 푸십시오." if will_val < -65 else \
                         f"● 현재 지수 {will_val:.2f}로 **안개 속**입니다. 방향이 정해질 때까지 자중하며 째려만 보십시오."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                macd_status = "▲ 상승엔진" if m_l > s_l else "▼ 하강엔진"
                macd_diag = f"● **상승 엔진**이 힘차게 돌고 있으나, 상단 성벽 저항을 이겨내는지 확인하며 진격 수위를 조절하십시오." if m_l > s_l else \
                           f"● **하강 엔진**으로 역회전 중입니다. 섣부른 진격보다는 포구에 정박하여 폭풍우가 지나가길 기다리는 게 상책입니다."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{macd_status}</p><p class='ind-diag'>{macd_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"오류: {e}")
