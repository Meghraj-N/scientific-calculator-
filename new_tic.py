# app.py
import streamlit as st

st.set_page_config(page_title="Tic-Tac-Toe (Simple 3x3)", page_icon="❎", layout="centered")

# --- CSS: colours and subtle light reflection background ---
st.markdown(
    """
    <style>
    /* page background with soft light reflections */
    .stApp {
      background: radial-gradient(circle at 10% 20%, rgba(255,255,255,0.40), transparent 8%),
                  radial-gradient(circle at 80% 80%, rgba(255,255,255,0.18), transparent 16%),
                  linear-gradient(180deg, #eaf2ff 0%, #d8e9ff 100%);
      min-height: 100vh;
      background-attachment: fixed;
    }

    /* make the container narrower */
    .block-container {
      padding-top: 1rem;
      padding-bottom: 2rem;
      max-width: 520px;
    }

    /* style Streamlit buttons as white square cells */
    .stButton>button {
      background-color: white;
      border: 2px solid #cfd8e3;
      height: 90px;
      width: 90px;
      font-size: 42px;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(18, 35, 85, 0.06);
    }

    /* colour X blue and O red by aria-label (the button label) */
    button[aria-label="X"] {
      color: #0b66ff;   /* blue for X */
      font-weight: 700;
    }
    button[aria-label="O"] {
      color: #ff2b2b;   /* red for O */
      font-weight: 700;
    }

    /* slightly larger on hover */
    .stButton>button:hover {
      transform: translateY(-2px);
    }

    /* small responsive tweak */
    @media (max-width: 480px) {
      .stButton>button {
        height: 72px;
        width: 72px;
        font-size: 34px;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Tic-Tac-Toe — Simple 3×3")
st.caption("No extras — just a plain 3×3 board. X is blue, O is red. Background has a subtle light reflection.")

# --- Game logic helpers ---
def init_board():
    return [[None for _ in range(3)] for _ in range(3)]

def check_winner(board):
    # rows
    for r in range(3):
        if board[r][0] and board[r][0] == board[r][1] == board[r][2]:
            return board[r][0]
    # cols
    for c in range(3):
        if board[0][c] and board[0][c] == board[1][c] == board[2][c]:
            return board[0][c]
    # diagonals
    if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    # draw?
    if all(board[r][c] is not None for r in range(3) for c in range(3)):
        return "Draw"
    return None

# --- Session state init ---
if "board" not in st.session_state:
    st.session_state.board = init_board()
if "turn" not in st.session_state:
    st.session_state.turn = "X"   # X starts
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "message" not in st.session_state:
    st.session_state.message = ""

# --- Controls ---
cols = st.columns([1,1,1])
with cols[0]:
    if st.button("Reset"):
        st.session_state.board = init_board()
        st.session_state.turn = "X"
        st.session_state.game_over = False
        st.session_state.message = ""

st.caption("Click a white cell to place the current symbol.")

# --- Board UI (3x3 grid) ---
grid_cols = [st.columns(3) for _ in range(3)]  # rows of columns

for r in range(3):
    for c in range(3):
        label = st.session_state.board[r][c] or " "  # empty label is a single space so aria-label isn't empty
        key = f"cell_{r}_{c}_{sum(1 for row in st.session_state.board for _ in row if _ is not None)}"
        if grid_cols[r][c].button(label, key=key):
            # do not allow moves after game over or on occupied cell
            if st.session_state.game_over:
                pass
            elif st.session_state.board[r][c] is not None:
                pass
            else:
                st.session_state.board[r][c] = st.session_state.turn
                winner = check_winner(st.session_state.board)
                if winner:
                    st.session_state.game_over = True
                    if winner == "Draw":
                        st.session_state.message = "It's a draw!"
                    else:
                        st.session_state.message = f"Winner: {winner}"
                else:
                    st.session_state.turn = "O" if st.session_state.turn == "X" else "X"

# --- Status message ---
st.write("")
if st.session_state.message:
    if st.session_state.message.startswith("Winner"):
        st.success(st.session_state.message)
    else:
        st.info(st.session_state.message)
else:
    st.info(f"Turn: {st.session_state.turn}")

# --- Simple board text (for accessibility) ---
st.write("")
st.markdown("**Board (rows top→bottom):**")
for r in range(3):
    row_display = [st.session_state.board[r][c] or "." for c in range(3)]
    st.write(" | ".join(row_display))
