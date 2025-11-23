# app.py
import streamlit as st

st.set_page_config(page_title="Tic-Tac-Toe (Interactive)", page_icon="🕹️", layout="centered")

# -----------------------
# Styling: colors, highlight, background reflection
# -----------------------
st.markdown(
    """
    <style>
    .stApp {
      background: radial-gradient(circle at 12% 18%, rgba(255,255,255,0.45), transparent 8%),
                  radial-gradient(circle at 82% 78%, rgba(255,255,255,0.20), transparent 12%),
                  linear-gradient(180deg, #f6f9ff 0%, #eaf2ff 100%);
      min-height: 100vh;
      background-attachment: fixed;
    }
    .block-container { max-width: 680px; }

    /* Button cells: white table look */
    .stButton>button {
      background-color: white;
      border: 2px solid #d6dee9;
      height: 110px;
      width: 110px;
      font-size: 48px;
      border-radius: 10px;
      box-shadow: 0 8px 20px rgba(14,30,80,0.06);
      transition: transform .08s ease, box-shadow .08s ease;
    }
    .stButton>button:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(14,30,80,0.08); }

    /* X and O core colors */
    button[aria-label="X"] { color: #0b66ff; font-weight:800; }     /* blue */
    button[aria-label="O"] { color: #ff2b2b; font-weight:800; }     /* red */

    /* Winning highlight */
    button[aria-label="X★"] { background: linear-gradient(180deg, #e6f0ff, #d9e8ff); border-color:#7fb1ff; color:#0b66ff; box-shadow: 0 10px 30px rgba(11,102,255,0.12); }
    button[aria-label="O★"] { background: linear-gradient(180deg, #ffecec, #ffdede); border-color:#ff9b9b; color:#ff2b2b; box-shadow: 0 10px 30px rgba(255,43,43,0.08); }

    /* Small responsive sizes */
    @media (max-width: 520px) {
      .stButton>button { height: 82px; width: 82px; font-size: 36px; }
    }

    /* Control buttons (Reset/Undo) */
    .control-button .stButton>button { height: 40px; width: auto; font-size: 14px; border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🕹️ Tic-Tac-Toe — Interactive")
st.write("Play locally. Click a cell to place X or O. Buttons: Undo, New Game, Reset. Winning line highlights.")

# -----------------------
# Game helpers
# -----------------------
def init_board():
    return [[None]*3 for _ in range(3)]

def check_winner(board):
    # rows
    for r in range(3):
        if board[r][0] and board[r][0] == board[r][1] == board[r][2]:
            return board[r][0], [(r,0),(r,1),(r,2)]
    # cols
    for c in range(3):
        if board[0][c] and board[0][c] == board[1][c] == board[2][c]:
            return board[0][c], [(0,c),(1,c),(2,c)]
    # diags
    if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0], [(0,0),(1,1),(2,2)]
    if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2], [(0,2),(1,1),(2,0)]
    # draw
    if all(board[r][c] is not None for r in range(3) for c in range(3)):
        return "Draw", []
    return None, []

# -----------------------
# Session state init
# -----------------------
if "board" not in st.session_state:
    st.session_state.board = init_board()
if "turn" not in st.session_state:
    st.session_state.turn = "X"
if "history" not in st.session_state:
    st.session_state.history = []  # list of (player, r, c)
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "winner" not in st.session_state:
    st.session_state.winner = None
if "winning_cells" not in st.session_state:
    st.session_state.winning_cells = []

# -----------------------
# Controls (top)
# -----------------------
col1, col2, col3 = st.columns([1,1,2])
with col1:
    if st.button("Undo", key="undo"):
        if st.session_state.history and not st.session_state.game_over:
            last = st.session_state.history.pop()
            _, r, c = last
            st.session_state.board[r][c] = None
            st.session_state.turn = "O" if st.session_state.turn == "X" else "X"
with col2:
    if st.button("New Game", key="new"):
        st.session_state.board = init_board()
        st.session_state.turn = "X"
        st.session_state.history = []
        st.session_state.game_over = False
        st.session_state.winner = None
        st.session_state.winning_cells = []
with col3:
    if st.button("Reset All (clear state)", key="reset"):
        for k in ["board","turn","history","game_over","winner","winning_cells"]:
            if k in st.session_state:
                del st.session_state[k]
        st.experimental_rerun()

st.write("")  # spacing
st.markdown(f"**Turn:** {'❌ X' if st.session_state.turn=='X' else '⭕ O'}")

# -----------------------
# Board UI (3x3 grid)
# -----------------------
rows = [st.columns([1,1,1]) for _ in range(3)]
# compute filled count to keep unique keys
filled_count = sum(1 for r in range(3) for c in range(3) if st.session_state.board[r][c] is not None)

for r in range(3):
    for c in range(3):
        val = st.session_state.board[r][c]
        # if this cell is in winning cells, append a star to the aria-label so CSS can style it
        aria_label = ""
        label = " "  # single space so aria-label not empty when None
        if val is None:
            label = " "
            aria_label = f"cell_{r}_{c}"
        else:
            # winner highlight uses "X★" or "O★" aria-label
            if (r,c) in st.session_state.winning_cells:
                label = f"{val}★"
                aria_label = label
            else:
                label = val
                aria_label = val  # "X" or "O"
        key = f"btn_{r}_{c}_{filled_count}"
        # Use button and inspect clicks
        if rows[r][c].button(label, key=key):
            # If game over or occupied, ignore except allow clicking winning cells (no effect)
            if st.session_state.game_over:
                pass
            elif st.session_state.board[r][c] is not None:
                pass
            else:
                # place piece
                st.session_state.board[r][c] = st.session_state.turn
                st.session_state.history.append((st.session_state.turn, r, c))
                winner, win_cells = check_winner(st.session_state.board)
                if winner is not None:
                    st.session_state.game_over = True
                    st.session_state.winner = winner
                    st.session_state.winning_cells = win_cells
                else:
                    st.session_state.turn = "O" if st.session_state.turn == "X" else "X"
                # immediate re-run to update UI & apply highlight
                st.experimental_rerun()

# -----------------------
# Status + History
# -----------------------
st.write("")  # spacing
if st.session_state.game_over:
    if st.session_state.winner == "Draw":
        st.info("Result: Draw!")
    else:
        st.success(f"Winner: {st.session_state.winner}  {'❌' if st.session_state.winner=='X' else '⭕'}")
else:
    st.info("Game in progress")

st.write("---")
st.subheader("Move history (latest first)")
for i, m in enumerate(reversed(st.session_state.history[-9:]), 1):
    p, r, c = m
    st.write(f"{i}. Player **{p}** → row {r+1}, col {c+1}")

# accessibility: text board
st.write("---")
st.markdown("**Board (rows top → bottom):**")
for r in range(3):
    row_display = [st.session_state.board[r][c] if st.session_state.board[r][c] is not None else "." for c in range(3)]
    st.write(" | ".join(row_display))
