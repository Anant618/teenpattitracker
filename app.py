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
    margin: 2px 0;
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
            "contribution": 0
        } for i in range(5)
    ]
if 'pot' not in st.session_state:
    st.session_state.pot = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'boot_done' not in st.session_state:
    st.session_state.boot_done = False  # Track if boot has been applied

# --- Helper functions ---
def snapshot():
    st.session_state.history.append([
        {
            "name": p["name"],
            "status": p["status"],
            "history": p["history"][:],
            "total_wins": p["total_wins"],
            "total_earned": p["total_earned"],
            "contribution": p["contribution"]
        } for p in st.session_state.players
    ])

def update_player(idx, amount):
    snapshot()
    if amount % 5 != 0:  # enforce multiple of 5
        st.warning("Amount must be multiple of 5")
        return
    p = st.session_state.players[idx]
    if p["status"] == "folded":  # cannot add if folded
        st.warning(f"{p['name']} has folded and cannot add/subtract.")
        return
    p["contribution"] += amount
    st.session_state.pot = sum(player["contribution"] for player in st.session_state.players)
    p["status"] = "active"
    action = f"{'+' if amount > 0 else ''}{amount}"
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
    # --- Boot amount of ₹5 for each player ---
    for p in st.session_state.players:
        p["contribution"] += 5
        p["history"].append("Boot 5")
    st.session_state.pot = sum(player["contribution"] for player in st.session_state.players)
    st.success("♻️ New round started with ₹5 boot for each player. Leaderboard retained.")

def fresh_leaderboard():
    """Clear only leaderboard stats (wins & total earnings)."""
    for p in st.session_state.players:
        p["total_wins"] = 0
        p["total_earned"] = 0
    st.success("🆕 Leaderboard has been reset!")

def declare_winner(idx):
    snapshot()
    pot = st.session_state.pot
    winner = st.session_state.players[idx]
    winnings = pot - winner["contribution"]
    winner["total_wins"] += 1
    winner["total_earned"] += winnings
    winner["history"].append(f"Won ₹{winnings}")
    st.session_state.pot = 0
    for p in st.session_state.players:
        p["status"] = "waiting"
        p["contribution"] = 0
    st.success(f"🏆 {winner['name']} wins ₹{winnings}")

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

    if st.button("♻️ New Round", key="new_round_pot"):
        reset_round()
        st.rerun()

# --- Player Panels ---
player_cols = st.columns(5, gap="large")
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

        # Allow renaming
        new_name = st.text_input(f"Name {i}", p["name"], key=f"name_{i}")
        p["name"] = new_name

        if p["status"] == "folded":
            st.markdown("**<span style='color:red; font-size:20px;'>FOLDED</span>**", unsafe_allow_html=True)
        else:
            amt = st.number_input("Amount (×5)", min_value=5, step=5, key=f"amt_{i}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Add", key=f"add_{i}"):
                    update_player(i, amt)
                    st.rerun()
            with col2:
                if st.button("➖ Subtract", key=f"sub_{i}"):
                    update_player(i, -amt)
                    st.rerun()

            if st.button("🪙 Fold", key=f"fold_{i}"):
                fold_player(i)
                st.rerun()

        if st.button("❌ Remove Player", key=f"remove_{i}"):
            remove_player(i)
            st.rerun()

        st.markdown("#### 📜 Actions")
        st.markdown(", ".join(map(str, p["history"])) if p["history"] else "_No actions yet_")

# --- Winner Declaration ---
st.markdown("---")
st.subheader("🏆 Declare Winner")
if st.session_state.players:
    winner_options = [f"{p['name']} (₹{p['contribution']})" for p in st.session_state.players]
    selected = st.selectbox("Select Winner", winner_options)
    winner_idx = winner_options.index(selected)
    if st.button("✅ Confirm Winner"):
        declare_winner(winner_idx)
        st.rerun()

# --- Controls ---
st.markdown("---")
cc1, cc2 = st.columns(2)
with cc1:
    if st.button("🔄 Undo"):
        undo()
        st.rerun()
with cc2:
    if st.button("🆕 Fresh Leaderboard"):
        fresh_leaderboard()
        st.rerun()

# --- Leaderboard ---
st.markdown("---")
st.header("📊 Leaderboard")
leaderboard = sorted(
    [
        {"Player": p["name"], "Wins": p["total_wins"], "Total Winnings (₹)": p["total_earned"]}
        for p in st.session_state.players
    ],
    key=lambda x: x["Wins"],
    reverse=True
)
st.table(leaderboard)

