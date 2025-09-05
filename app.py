import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Teen Patti Tracker", layout="wide")

# --- Dark Styling ---
st.markdown("""
<style>
body {
    background-color: black;
    color: white;
}
h1, h2, h3 {
    color: gold;
}
.player-card {
    background-color: #1a1a1a;
    padding: 16px;
    border-radius: 8px;
    border: 2px solid #444;
    text-align: center;
    box-shadow: 0 0 10px #222;
}
.folded {
    background-color: #333 !important;
    opacity: 0.6;
}
button {
    margin: 2px 4px;
}
</style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
if 'players' not in st.session_state:
    st.session_state.players = [
        {
            "name": f"Player {i+1}",
            "status": "waiting",
            "history": [],
            "total_wins": 0,
            "total_earned": 0,
            "total_lost": 0,
            "contribution": 0
        } for i in range(4)  # only 4 players
    ]
if 'pot' not in st.session_state:
    st.session_state.pot = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'boot_done' not in st.session_state:
    st.session_state.boot_done = False
if 'hand_history' not in st.session_state:
    st.session_state.hand_history = []

# --- Helper functions ---
def snapshot():
    st.session_state.history.append([
        {
            "name": p["name"],
            "status": p["status"],
            "history": p["history"][:],
            "total_wins": p["total_wins"],
            "total_earned": p["total_earned"],
            "total_lost": p["total_lost"],
            "contribution": p["contribution"]
        } for p in st.session_state.players
    ])

def update_player(idx, amount):
    snapshot()
    if amount % 5 != 0:
        st.warning("Amount must be multiple of 5")
        return
    p = st.session_state.players[idx]
    if p["status"] == "folded":
        st.warning(f"{p['name']} has folded and cannot add.")
        return
    p["contribution"] += amount
    st.session_state.pot = sum(player["contribution"] for player in st.session_state.players)
    p["status"] = "active"
    action = f"+{amount}"
    p["history"].append(action)

def fold_player(idx):
    snapshot()
    p = st.session_state.players[idx]
    p["status"] = "folded"
    p["history"].append("Fold")

def remove_player(idx):
    snapshot()
    if 0 <= idx < len(st.session_state.players):
        del st.session_state.players[idx]

def undo():
    if st.session_state.history:
        st.session_state.players = st.session_state.history.pop()
        st.session_state.pot = sum(player["contribution"] for player in st.session_state.players)

def reset_round():
    snapshot()
    st.session_state.pot = 0
    for p in st.session_state.players:
        p["status"] = "waiting"
        p["history"] = []
        p["contribution"] = 0
    for p in st.session_state.players:
        p["contribution"] += 5
        p["history"].append("Boot 5")
    st.session_state.pot = sum(player["contribution"] for player in st.session_state.players)
    st.success("♻️ New round started with ₹5 boot for each player. Leaderboard retained.")

def fresh_leaderboard():
    for p in st.session_state.players:
        p["total_wins"] = 0
        p["total_earned"] = 0
        p["total_lost"] = 0
    st.success("🆕 Leaderboard has been reset!")

def declare_winner(idx):
    snapshot()
    pot = st.session_state.pot
    winner = st.session_state.players[idx]

    winnings = pot - winner["contribution"]
    winner["total_wins"] += 1
    winner["total_earned"] += winnings
    winner["history"].append(f"Won ₹{winnings}")

    st.session_state.hand_history.append(f"{winner['name']} won ₹{winnings}")

    for i, p in enumerate(st.session_state.players):
        if i != idx:
            p["total_lost"] += p["contribution"]

    st.success(f"🏆 {winner['name']} wins ₹{winnings}")
    st.info("Click 'New Round' to start the next game.")

# --- Auto Boot on First Load ---
if not st.session_state.boot_done:
    for p in st.session_state.players:
        p["contribution"] += 5
        p["history"].append("Boot 5")
    st.session_state.pot = sum(player["contribution"] for player in st.session_state.players)
    st.session_state.boot_done = True
    st.info("🎉 Game started with ₹5 boot from each player.")

# --- Title & Pot Display ---
st.title("🎴 Teen Patti Tracker")

_, pot_col, _ = st.columns([1, 2, 1])
with pot_col:
    st.markdown(f"""
    <div style="
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid gold;
        text-align: center;
        box-shadow: 0 0 15px #444;">
        <h2 style="color: gold; margin: 0;">🪙 Pot</h2>
        <h3 style="color:white; margin: 10px 0;">₹{st.session_state.pot}</h3>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("♻️ New Round", key="new_round_pot"):
            reset_round()
            st.rerun()
    with col_b:
        if st.button("🔄 Undo"):
            undo()
            st.rerun()

# --- Player Panels ---
player_cols = st.columns(4, gap="large")
for i in range(len(st.session_state.players)):
    p = st.session_state.players[i]
    folded_class = " folded" if p["status"] == "folded" else ""
    with player_cols[i]:
        st.markdown(f"""
        <div class="player-card{folded_class}">
            <h3>🧑 {p['name']}</h3>
            <p>🪙 <b>Contributed:</b> ₹{p['contribution']}</p>
            <p>📌 <b>Status:</b> {p['status'].capitalize()}</p>
        </div>
        """, unsafe_allow_html=True)

        # ✅ instant name update
        st.text_input(
            f"Name {i}",
            p["name"],
            key=f"name_{i}",
            on_change=lambda idx=i: st.session_state.players.__setitem__(
                idx,
                {**st.session_state.players[idx], "name": st.session_state[f"name_{idx}"]}
            )
        )

        if p["status"] == "folded":
            st.markdown("**<span style='color:red; font-size:20px;'>FOLDED</span>**", unsafe_allow_html=True)
        else:
            amt_cols = st.columns([1,1,1,1,1])
            for j, amt in enumerate([5, 10, 15, 20, 30]):
                with amt_cols[j]:
                    if st.button(f"➕ ₹{amt}", key=f"add_{i}_{amt}"):
                        update_player(i, amt)
                        st.rerun()

            action_cols = st.columns(2)
            with action_cols[0]:
                if st.button("🪙 Fold", key=f"fold_{i}"):
                    fold_player(i)
                    st.rerun()
            with action_cols[1]:
                # --- Confirmation before removing ---
                if f"confirm_remove_{i}" not in st.session_state:
                    st.session_state[f"confirm_remove_{i}"] = False

                if not st.session_state[f"confirm_remove_{i}"]:
                    if st.button("❌ Remove", key=f"remove_{i}"):
                        st.session_state[f"confirm_remove_{i}"] = True
                        st.rerun()
                else:
                    st.warning(f"Are you sure you want to remove {p['name']}?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Yes", key=f"yes_remove_{i}"):
                            remove_player(i)
                            st.session_state[f"confirm_remove_{i}"] = False
                            st.rerun()
                    with c2:
                        if st.button("❌ No", key=f"no_remove_{i}"):
                            st.session_state[f"confirm_remove_{i}"] = False
                            st.rerun()

        st.markdown("#### 📜 Actions")
        st.markdown(", ".join(map(str, p["history"])) if p["history"] else "_No actions yet_")

# --- Winner Section ---
st.markdown("---")
st.subheader("🏆 Declare Winner")
if st.session_state.players:
    active_players = [p for p in st.session_state.players if p["status"] != "folded"]

    if len(active_players) == 1:
        st.success(f"🏆 {active_players[0]['name']} wins automatically as others folded!")
        winner_idx = st.session_state.players.index(active_players[0])
        declare_winner(winner_idx)
    elif len(active_players) > 1:
        options = [f"{p['name']} (₹{p['contribution']})" for p in active_players]
        idx_map = [st.session_state.players.index(p) for p in active_players]
        choice = st.selectbox("Select Winner", options)
        idx = idx_map[options.index(choice)]
        if st.button("✅ Confirm Winner"):
            declare_winner(idx)
    else:
        st.info("No active players left to declare a winner.")

# --- Controls ---
st.markdown("---")
if st.button("🆕 Fresh Leaderboard"):
    fresh_leaderboard()
    st.rerun()

# --- Leaderboard ---
st.markdown("---")
st.header("📊 Leaderboard")
leaderboard = []
for p in st.session_state.players:
    lost = p["total_lost"]
    overall = p["total_earned"] - lost
    leaderboard.append({
        "Player": p["name"],
        "Wins": p["total_wins"],
        "Amount Won (₹)": p["total_earned"],
        "Amount Lost (₹)": lost,
        "Overall (₹)": overall
    })
leaderboard = sorted(leaderboard, key=lambda x: x["Overall (₹)"], reverse=True)
st.table(leaderboard)

# --- Hand History ---
st.markdown("---")
st.header("🕑 Hand History")
if st.session_state.hand_history:
    for i, h in enumerate(st.session_state.hand_history[::-1], 1):
        st.write(f"Hand {len(st.session_state.hand_history) - i + 1}: {h}")
else:
    st.write("No hands played yet.")

