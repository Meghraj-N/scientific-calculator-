# app.py
import streamlit as st

st.set_page_config(page_title="Tic-Tac-Toe", page_icon="❎", layout="centered")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #001133, #000820 70%);
    color: white;
    text-align: center;
}

/* Title styling */
h1 {
    font-family: 'Courier New', monospace;
    font-size: 38px !important;
    font-weight: bold;
    color: #ffffff !important;
    text-shadow: 0px 0px 12px rgba(255,255,255,0.6);
}

/* Board container */
.board-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}

/* Buttons styled as cells */
.stButton>button {
    background-color: rgba(255,255,255,0.05);
    border: 2px solid #ffffff;
    height: 110px;
    width: 110px;
    font-size: 60px;
    font-weight: 900;
    border-radius: 6px;
    transition: 0.15s ease-in-out;
}

/* Hover effect */
.stButton>button:hover {
    background-color: rgba(255,255,255,0.15);
    transform: scale(1.05);
}

/* X (red) */
button[aria-label="X"], button[aria-label="X★"] {
    color: #ff3b3b !important;
    text-shadow: 0px 0px 10px rgba(255,0,0,0.6);
}

/* O (neon cyan) */
button[aria-label="O"], button[aria-label="O★"] {
    color: #1affff !important;
    text-shadow: 0px 0px 10px rgba(0,255,255,0.6);
}

/* Highlight winning cells */
button[aria-label="X★"], button[aria-label="O★"] {
    background-color: rgba(255,255,255,0.2) !important;
}

/* Controls */
.controls button {
    background-color: rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 8px !important;
    height: 40px !important;
    width: 120px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------- GAME LOGIC ----------
def init_board():
    return [[None]*3 for _ in range(3)]

def check_winner(board):
    # rows
    for r in range(3):
        if board[r][0] and board[r][0] == board[r][1] == board[r][2]:
            return board[r][0], [(r,0),(r,1),(r,2)]
    # columns
    for c in range(3):
        if board[0][c] and board[0][c] == board[1][c] == board[2][c]:
            return board[0][c], [(0,c),(1,c),(2,c)]
    # diagonals
    if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0], [(0,0),(1,1),(2,2)]
    if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2], [(0,2),(1,1),(2,0)]

    # draw check
    if all(board[r][c] is not None for r in range(3) for c in range(3)):
        return "Draw", []

    return None, []

# ---------- SESSION STATE ----------
if "board" not in st.session_state:
    st.session_state.board = init_board()
if "turn" not in st.session_state:
    st.session_state.turn = "X"
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "winner" not in st.session_state:
    st.session_state.winner = None
if "winning_cells" not in st.session_state:
    st.session_state.winning_cells = []
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- TITLE ----------
st.markdown("<h1>Tic-Tac-Toe</h1>", unsafe_allow_html=True)

# ---------- CONTROLS ----------
colA, colB, colC = st.columns(3)
with colA:
    if st.button("Undo", key="undo"):
        if st.session_state.history and not st.session_state.game_over:
            last = st.session_state.history.pop()
            _, r, c = last
            st.session_state.board[r][c] = None
            st.session_state.turn = "O" if st.session_state.turn == "X" else "X"

with colB:
    if st.button("New Game", key="new"):
        st.session_state.board = init_board()
        st.session_state.turn = "X"
        st.session_state.history = []
        st.session_state.game_over = False
        st.session_state.winner = None
        st.session_state.winning_cells = []

with colC:
    if st.button("Reset"):
        for key in ["board","turn","history","game_over","winner","winning_cells"]:
            st.session_state.pop(key, None)
        st.experimental_rerun()

# ---------- TURN DISPLAY ----------
st.markdown(
    f"<h3 style='color:white;'>Turn: {'❌ X' if st.session_state.turn=='X' else '⭕ O'}</h3>",
    unsafe_allow_html=True
)

# ---------- BOARD UI ----------
filled = sum(1 for r in st.session_state.board for c in r if c is not None)
rows = [st.columns([1,1,1]) for _ in range(3)]

for r in range(3):
    for c in range(3):
        val = st.session_state.board[r][c]

        if val is None:
            label = " "
            aria = f"cell_{r}_{c}"
        else:
            if (r,c) in st.session_state.winning_cells:
                label = f"{val}★"
                aria = label
            else:
                label = val
                aria = val

        key = f"{r}{c}_{filled}"

        if rows[r][c].button(label, key=key):
            if not st.session_state.game_over and st.session_state.board[r][c] is None:
                st.session_state.board[r][c] = st.session_state.turn
                st.session_state.history.append((st.session_state.turn,r,c))

                winner, cells = check_winner(st.session_state.board)
                if winner:
                    st.session_state.game_over = True
                    st.session_state.winner = winner
                    st.session_state.winning_cells = cells
                else:
                    st.session_state.turn = "O" if st.session_state.turn=="X" else "X"

                st.experimental_rerun()

# ---------- STATUS ----------
st.write("")
if st.session_state.game_over:
    if st.session_state.winner == "Draw":
        st.info("It's a Draw!")
    else:
        st.success(f"Winner: {st.session_state.winner}")
else:
    st.info("Game in progress...")
