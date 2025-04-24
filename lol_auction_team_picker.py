import streamlit as st
import random

st.set_page_config(page_title="LoL 내전 팀 경매", layout="centered")

# 초기 설정
initial_budget = 200
managers = ["예인", "동혁", "규환"]
roles = {
    "탑": ["남순", "봉현", "성택"],
    "정글": ["예인", "낙기", "게이"],
    "미드": ["성빈", "동혁", "종훈"],
    "원딜": ["엘가", "규환", "일만"],
    "서폿": ["준혁", "권혁", "준모"]
}

# 세션 상태 저장
if "teams" not in st.session_state:
    st.session_state.teams = {name: {"budget": initial_budget, "players": {}} for name in managers}
if "auction_list" not in st.session_state:
    st.session_state.auction_list = [(role, p) for role, lst in roles.items() for p in lst]
    random.shuffle(st.session_state.auction_list)
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

st.title("🎮 LoL 내전 팀 경매 시스템")
st.markdown("감독이 포인트로 선수를 경매하여 팀을 구성합니다.")

# 현재 선수 보여주기
if st.session_state.current_index < len(st.session_state.auction_list):
    role, player = st.session_state.auction_list[st.session_state.current_index]
    st.header(f"🚨 경매 중: [{role}] {player}")

    with st.form(key=f"bid_form_{st.session_state.current_index}"):
        bids = {}
        for manager in managers:
            disabled = role in st.session_state.teams[manager]['players']
            budget = st.session_state.teams[manager]['budget']
            label = f"{manager} 입찰가 (예산: {budget}P){' - 이미 보유' if disabled else ''}"
            bid = st.number_input(label, min_value=0, max_value=budget, step=1, key=f"bid_{manager}", disabled=disabled)
            bids[manager] = bid if not disabled else 0
        submitted = st.form_submit_button("📣 입찰 제출")

        if submitted:
            valid_bids = {m: b for m, b in bids.items() if b > 0}
            if not valid_bids:
                st.warning(f"{player}는 낙찰되지 않았습니다. 다음 선수로 넘어갑니다.")
            else:
                winner = max(valid_bids, key=valid_bids.get)
                price = valid_bids[winner]
                st.session_state.teams[winner]['budget'] -= price
                st.session_state.teams[winner]['players'][role] = player
                st.success(f"🎉 {player}는 {winner} 감독에게 {price}P에 낙찰!")

            st.session_state.current_index += 1
            st.experimental_rerun()
else:
    st.success("✅ 모든 선수의 경매가 완료되었습니다!")

# 현재 팀 상태 표시
st.subheader("📊 현재 팀 구성")
for manager in managers:
    with st.expander(f"{manager} 팀 (예산: {st.session_state.teams[manager]['budget']}P)"):
        for role in roles:
            val = st.session_state.teams[manager]['players'].get(role, "(미정)")
            st.text(f"{role}: {val}")
