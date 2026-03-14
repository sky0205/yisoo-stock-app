# (앞부분 생략 - 어르신이 주신 v36056 전체 코드 중 6번 지수란 부분만 교체하십시오)

            # 6. 네 기둥 지수란 (심화 진단 적용)
            i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_pos = "🔥 폭주" if p>=up_b else "📉 추락" if p<=low_b else "⚖️ 눈치보기"
                bb_diag = f"""● 현재 성벽 중간에서 **방향성 탐색 중**입니다. 상단({format(up_b, fmt)}) 돌파 실패 시 실망 매물이 쏟아질 수 있으니, 무리한 진격보다는 지지선을 지키는지 정밀 관측하십시오.""" if bb_pos=="⚖️ 눈치보기" else \
                          f"""● 성벽 밖 **과열 권역**입니다. 평균 회귀 본능에 의해 조만간 차익 실현 소나기가 내릴 가능성이 농후하니, 보따리 쌀 준비를 서두르시는 게 상책입니다.""" if bb_pos=="🔥 폭주" else \
                          f"""● 하단 성벽이 무너진 **공포 구간**입니다. 바닥 아래 지하실이 있을 수 있으니, 투매 비명소리가 잦아들고 안정을 찾을 때까지 절대 칼날을 잡지 마십시오."""
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-status'>{bb_pos}</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)

            with i2: # RSI (냉정 진단 65↑ 기준 적용)
                r_stat = "👺 불지옥" if rsi_val > 65 else "🧊 냉골" if rsi_val < 35 else "미지근"
                r_diag = f"""● 현재 온도 {rsi_val:.2f}로 **탐욕의 불지옥** 진입 전야입니다. 남들이 환호할 때가 가장 위험한 법이니, 냉정하게 분할 매도로 수익을 확정 지을 준비를 하십시오.""" if r_stat=="👺 불지옥" else \
                         f"""● 현재 온도 {rsi_val:.2f}의 **냉골 상태**입니다. 아직 개미들의 곡소리가 부족하니, 지수가 30 근처까지 완전히 식어버릴 때까지 낚싯대만 던져두고 기다리십시오.""" if r_stat=="🧊 냉골" else \
                         f"""● 매수와 매도가 팽팽한 **줄다리기 구간**입니다. 방향성 없는 싸움에 끼어들어 수수료만 버리지 마시고, 기세가 어느 한쪽으로 쏠릴 때까지 자중하십시오."""
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)

            with i3: # Williams %R (냉정 진단 -75↓ 기준 적용)
                w_status = "🧨 광기폭발" if will_val > -20 else "🏳️ 개미항복" if will_val < -75 else "추락중"
                w_diag = f"""● 윌리엄 지수 {will_val:.2f}로 **불나방 광기**가 절정입니다! 세력들이 물량을 떠넘기고 떠날 채비를 하고 있으니, 뒤도 돌아보지 말고 후퇴하여 내 자산을 사수하십시오.""" if w_status=="🧨 광기폭발" else \
                         f"""● 드디어 **진짜 개미들이 항복**을 선언한 바닥권입니다. 공포가 극에 달했을 때가 기회이니, 욕심내지 말고 빳빳한 보따리를 풀어 분할 매수를 시작할 때입니다.""" if w_status=="🏳️ 개미항복" else \
                         f"""● 지표가 바닥을 향해 **자유낙하 중**입니다. 어설픈 낙주 매매는 자살행위이니, 개미들의 비명소리가 시장에 가득 찰 때까지 느긋하게 째려만 보십시오."""
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)

            with i4: # MACD
                macd_status = "▲ 상승엔진" if m_l > s_l else "▼ 하강엔진"
                macd_diag = f"""● **상승 엔진**이 힘차게 돌고 있습니다. 다만, 상단 성벽({format(up_b, fmt)})의 저항력을 이겨내는지 확인하며 진격의 수위를 조절하는 혜안이 필요합니다.""" if m_l > s_l else \
                           f"""● **하강 엔진**으로 역회전 중입니다. 엔진이 꺼진 배는 조류에 휩쓸리기 마련이니, 섣부른 진격보다는 포구에 정박하여 폭풍우가 지나가길 기다리는 게 상책입니다."""
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-status'>{macd_status}</p><p class='ind-diag'>{macd_diag}</p></div>", unsafe_allow_html=True)
