import streamlit as st
import random
import time

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
if "current_bid" not in st.session_state:
    st.session_state.current_bid = 0
if "current_bidder" not in st.session_state:
    st.session_state.current_bidder = None
if "bid_end_time" not in st.session_state:
    st.session_state.bid_end_time = time.time() + 10
if "passed_players" not in st.session_state:
    st.session_state.passed_players = []

st.title("🎮 LoL 내전 팀 경매 시스템")
st.markdown("10초 이내에 입찰 없으면 유찰! 다시 입찰 시 남은 시간 리셋!")

# 현재 선수 보여주기
if st.session_state.current_index < len(st.session_state.auction_list):
    role, player = st.session_state.auction_list[st.session_state.current_index]
    st.header(f"🚨 경매 중: [{role}] {player}")

    col1, col2 = st.columns(2)
    col1.metric("현재 입찰가", f"{st.session_state.current_bid}P")
    col2.metric("입찰자", st.session_state.current_bidder or "없음")

    remaining = int(st.session_state.bid_end_time - time.time())
    st.markdown(f"⏳ 남은 시간: `{remaining}` 초")

    if remaining <= 0:
        if st.session_state.current_bidder:
            st.success(f"🎉 {player}는 {st.session_state.current_bidder}에게 {st.session_state.current_bid}P에 낙찰!")
            st.session_state.teams[st.session_state.current_bidder]['budget'] -= st.session_state.current_bid
            st.session_state.teams[st.session_state.current_bidder]['players'][role] = player
        else:
            st.warning(f"❌ {player}는 유찰되었습니다.")
            st.session_state.passed_players.append((role, player))

        st.session_state.current_index += 1
        st.session_state.current_bid = 0
        st.session_state.current_bidder = None
        st.session_state.bid_end_time = time.time() + 10
        st.experimental_rerun()

    st.subheader("입찰하기")
    for manager in managers:
        disabled = role in st.session_state.teams[manager]['players']
        budget = st.session_state.teams[manager]['budget']
        bid_input = st.number_input(f"{manager} 입찰가 입력 (현재 예산: {budget}P)", min_value=st.session_state.current_bid + 1, max_value=budget, step=1, key=f"input_{manager}", disabled=disabled)
        if st.button(f"{manager} 입찰", key=f"bid_{manager}", disabled=disabled or bid_input <= st.session_state.current_bid):
            st.session_state.current_bid = bid_input
            st.session_state.current_bidder = manager
            st.session_state.bid_end_time = time.time() + 10
            st.experimental_rerun()
else:
    st.success("✅ 모든 선수의 1차 경매가 완료되었습니다!")

    # 유찰된 선수 재경매 리스트
    if st.session_state.passed_players:
        st.markdown("---")
        st.subheader("🌀 유찰 선수 재경매 준비됨")
        st.session_state.auction_list = st.session_state.passed_players
        st.session_state.passed_players = []
        st.session_state.current_index = 0
        st.session_state.current_bid = 0
        st.session_state.current_bidder = None
        st.session_state.bid_end_time = time.time() + 10
        st.experimental_rerun()

# 현재 팀 상태 표시
st.subheader("📊 현재 팀 구성")
for manager in managers:
    with st.expander(f"{manager} 팀 (예산: {st.session_state.teams[manager]['budget']}P)"):
        for role in roles:
            val = st.session_state.teams[manager]['players'].get(role, "(미정)")
            st.text(f"{role}: {val}")
