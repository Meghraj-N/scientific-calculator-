# app.py
import streamlit as st
import copy
import random
from typing import List, Optional, Tuple

st.set_page_config(page_title="Unique Tic-Tac-Toe", page_icon="🎯", layout="centered")
st.title("🎯 Unique Tic-Tac-Toe (Power Cells + Swap Rule)")
st.markdown("""
Unique twists:
- Board sizes: 3×3, 4×4, or 5×5.
- Adjustable win-length (3,4,5 depending on board).
- **Power Cells**: special cells give the mover an extra immediate move.
- **Swap Rule**: after each player placed one or two initial moves (configurable), the second player can swap symbols.
- Human vs Human (local) or Human vs AI (minimax, depth-limited).
- Undo, Reset, and move history. Winning line highlight.
""")

# -------------------------
# Utilities
# -------------------------
def new_board(n:int) -> List[List[Optional[str]]]:
    return [[None for _ in range(n)] for _ in range(n)]

def avail_moves(board):
    moves = []
    for r in range(len(board)):
        for c in range(len(board)):
            if board[r][c] is None:
                moves.append((r,c))
    return moves

def board_full(board):
    return all(cell is not None for row in board for cell in row)

def generate_power_cells(n:int, count:int) -> List[Tuple[int,int]]:
    # deterministic-ish: shuffle all cells then pick first count
    cells = [(r,c) for r in range(n) for c in range(n)]
    random.seed(42 + n)  # reproducible per size
    random.shuffle(cells)
    return cells[:count]

def win_lines(n:int, win_len:int):
    lines = []
    # rows
    for r in range(n):
        for c in range(n - win_len + 1):
            lines.append([(r,c+i) for i in range(win_len)])
    # cols
    for c in range(n):
        for r in range(n - win_len + 1):
            lines.append([(r+i,c) for i in range(win_len)])
    # diag down-right
    for r in range(n - win_len + 1):
        for c in range(n - win_len + 1):
            lines.append([(r+i,c+i) for i in range(win_len)])
    # diag up-right
    for r in range(win_len-1, n):
        for c in range(n - win_len + 1):
            lines.append([(r-i,c+i) for i in range(win_len)])
    return lines

def check_winner(board, win_len):
    lines = win_lines(len(board), win_len)
    for line in lines:
        vals = [board[r][c] for r,c in line]
        if vals[0] is not None and all(v == vals[0] for v in vals):
            return vals[0], line
    return None, None

# -------------------------
# Minimax (depth-limited)
# -------------------------
def minimax(board, win_len, depth, max_depth, is_max, ai_p, human_p):
    winner, _ = check_winner(board, win_len)
    if winner == ai_p:
        return 1000 - depth, None
    if winner == human_p:
        return -1000 + depth, None
    if board_full(board):
        return 0, None
    if depth >= max_depth:
        return heuristic(board, win_len, ai_p, human_p), None

    if is_max:
        best = -10**9
        best_move = None
        for (r,c) in avail_moves(board):
            board[r][c] = ai_p
            sc, _ = minimax(board, win_len, depth+1, max_depth, False, ai_p, human_p)
            board[r][c] = None
            if sc > best:
                best = sc
                best_move = (r,c)
        return best, best_move
    else:
        best = 10**9
        best_move = None
        for (r,c) in avail_moves(board):
            board[r][c] = human_p
            sc, _ = minimax(board, win_len, depth+1, max_depth, True, ai_p, human_p)
            board[r][c] = None
            if sc < best:
                best = sc
                best_move = (r,c)
        return best, best_move

def heuristic(board, win_len, ai_p, human_p):
    # simple potential-line heuristic
    def count_p(player):
        cnt = 0
        for line in win_lines(len(board), win_len):
            vals = [board[r][c] for r,c in line]
            if all(v is None or v == player for v in vals):
                cnt += sum(1 for v in vals if v == player) + 1
        return cnt
    return count_p(ai_p) - count_p(human_p)

# -------------------------
# Session initialization
# -------------------------
if "settings" not in st.session_state:
    st.session_state.settings = {
        "size": 3,
        "win_len": 3,
        "mode": "Human vs AI",
        "ai_depth": 3,
        "first": "Human",
        "ai_symbol": "O",
        "power_cells_enabled": True,
        "power_cells_count": 1,
        "swap_rule_enabled": True,
        "swap_after_moves_each": 1,  # after each placed this many moves, swap allowed
        "symbols": {"X":"❌", "O":"⭕"}
    }

if "board" not in st.session_state:
    n = st.session_state.settings["size"]
    st.session_state.board = new_board(n)
if "turn" not in st.session_state:
    st.session_state.turn = "X" if st.session_state.settings["first"] == "Human" else st.session_state.settings["ai_symbol"]
if "history" not in st.session_state:
    st.session_state.history = []  # list of (player,r,c)
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "winning_line" not in st.session_state:
    st.session_state.winning_line = None
if "power_cells" not in st.session_state:
    s = st.session_state.settings
    st.session_state.power_cells = generate_power_cells(s["size"], s["power_cells_count"]) if s["power_cells_enabled"] else []
if "swap_available" not in st.session_state:
    st.session_state.swap_available = False
if "has_swapped" not in st.session_state:
    st.session_state.has_swapped = False

# -------------------------
# Settings UI
# -------------------------
with st.expander("Settings (expand to customize)"):
    s = st.session_state.settings
    size = st.selectbox("Board size", [3,4,5], index=[3,4,5].index(s["size"]))
    possible_win = [3]
    if size >=4: possible_win.append(4)
    if size >=5: possible_win.append(5)
    win_len = st.selectbox("Win length", possible_win, index=possible_win.index(s["win_len"]) if s["win_len"] in possible_win else 0)
    mode = st.selectbox("Mode", ["Human vs AI", "Human vs Human (Local)"], index=0 if s["mode"]=="Human vs AI" else 1)
    ai_depth = st.slider("AI depth (difficulty)", 1, 6, s["ai_depth"])
    first = st.radio("Who goes first?", ["Human", "AI"], index=0 if s["first"]=="Human" else 1)
    ai_symbol = st.selectbox("AI symbol (if playing AI)", ["O","X"], index=0 if s["ai_symbol"]=="O" else 1)
    power_cells_enabled = st.checkbox("Enable Power Cells (play again when you land on one)", value=s["power_cells_enabled"])
    power_cells_count = st.slider("Power Cells count", 0, min(4, size*size//3), s["power_cells_count"])
    swap_enabled = st.checkbox("Enable Swap Rule (second player may swap after initial moves)", value=s["swap_rule_enabled"])
    swap_after = st.selectbox("Swap available after each player placed", [1,2], index=0 if s["swap_after_moves_each"]==1 else 1)
    sym_x = st.text_input("Symbol for X (single char or emoji)", value=s["symbols"]["X"])
    sym_o = st.text_input("Symbol for O (single char or emoji)", value=s["symbols"]["O"])
    apply = st.button("Apply & Reset")

# apply changes when requested
if apply or any([
    size != st.session_state.settings["size"],
    win_len != st.session_state.settings["win_len"],
    mode != st.session_state.settings["mode"],
    ai_depth != st.session_state.settings["ai_depth"],
    first != st.session_state.settings["first"],
    ai_symbol != st.session_state.settings["ai_symbol"],
    power_cells_enabled != st.session_state.settings["power_cells_enabled"],
    power_cells_count != st.session_state.settings["power_cells_count"],
    swap_enabled != st.session_state.settings["swap_rule_enabled"],
    swap_after != st.session_state.settings["swap_after_moves_each"],
    sym_x != st.session_state.settings["symbols"]["X"],
    sym_o != st.session_state.settings["symbols"]["O"],
]):
    st.session_state.settings.update({
        "size": size,
        "win_len": win_len,
        "mode": mode,
        "ai_depth": ai_depth,
        "first": first,
        "ai_symbol": ai_symbol,
        "power_cells_enabled": power_cells_enabled,
        "power_cells_count": power_cells_count,
        "swap_rule_enabled": swap_enabled,
        "swap_after_moves_each": swap_after,
        "symbols": {"X": sym_x or "X", "O": sym_o or "O"}
    })
    # reset game
    st.session_state.board = new_board(size)
    st.session_state.history = []
    st.session_state.game_over = False
    st.session_state.winning_line = None
    st.session_state.turn = "X" if first == "Human" else ai_symbol
    st.session_state.power_cells = generate_power_cells(size, power_cells_count) if power_cells_enabled else []
    st.session_state.swap_available = False
    st.session_state.has_swapped = False

# -------------------------
# Game actions
# -------------------------
def make_move(r,c,player):
    if st.session_state.game_over:
        return
    if st.session_state.board[r][c] is not None:
        return
    st.session_state.board[r][c] = player
    st.session_state.history.append((player,r,c))
    winner, line = check_winner(st.session_state.board, st.session_state.settings["win_len"])
    if winner:
        st.session_state.game_over = True
        st.session_state.winning_line = line
    elif board_full(st.session_state.board):
        st.session_state.game_over = True
        st.session_state.winning_line = None
    else:
        # check swap availability: if swap enabled and both players have each placed swap_after_moves_each moves
        counts = {"X":0,"O":0}
        for p,_,_ in st.session_state.history:
            counts[p]+=1
        if st.session_state.settings["swap_rule_enabled"] and not st.session_state.has_swapped:
            if counts["X"] >= st.session_state.settings["swap_after_moves_each"] and counts["O"] >= st.session_state.settings["swap_after_moves_each"]:
                st.session_state.swap_available = True
        # check power cell: same player moves again if cell is in power_cells
        if (r,c) in st.session_state.power_cells:
            # remove power cell so it's used once
            st.session_state.power_cells.remove((r,c))
            # same player's turn again
            st.experimental_rerun()
        else:
            st.session_state.turn = "O" if st.session_state.turn == "X" else "X"

def ai_move():
    if st.session_state.game_over:
        return
    board_copy = copy.deepcopy(st.session_state.board)
    ai_p = st.session_state.settings["ai_symbol"]
    human_p = "O" if ai_p == "X" else "X"
    depth = st.session_state.settings["ai_depth"]
    _, mv = minimax(board_copy, st.session_state.settings["win_len"], 0, depth, True, ai_p, human_p)
    if mv is None:
        moves = avail_moves(st.session_state.board)
        if not moves:
            return
        mv = random.choice(moves)
    r,c = mv
    make_move(r,c, ai_p)

# make AI first move if required (safe when nothing played)
if st.session_state.settings["mode"] == "Human vs AI" and st.session_state.settings["first"] == "AI" and not st.session_state.history:
    ai_move()

# -------------------------
# Controls (left column)
# -------------------------
left, right = st.columns([1,2])

with left:
    st.write("**Game controls**")
    st.write(f"Mode: {st.session_state.settings['mode']}")
    st.write(f"Board: {st.session_state.settings['size']}×{st.session_state.settings['size']}, Win: {st.session_state.settings['win_len']}")
    st.write(f"Turn: {st.session_state.turn}  ({st.session_state.settings['symbols'][st.session_state.turn]})")
    if st.session_state.game_over:
        w, _ = check_winner(st.session_state.board, st.session_state.settings["win_len"])
        if w:
            st.success(f"Winner: {w} ({st.session_state.settings['symbols'][w]})")
        else:
            st.info("Draw!")
    st.write(f"Power cells left: {len(st.session_state.power_cells)}")
    if st.button("Undo last move"):
        if st.session_state.history:
            last = st.session_state.history.pop()
            _, r, c = last
            st.session_state.board[r][c] = None
            st.session_state.game_over = False
            st.session_state.winning_line = None
            st.session_state.swap_available = False
            st.session_state.has_swapped = False
            # swap turn back
            st.session_state.turn = "O" if st.session_state.turn == "X" else "X"
    if st.button("Reset game"):
        s = st.session_state.settings
        st.session_state.board = new_board(s["size"])
        st.session_state.history = []
        st.session_state.game_over = False
        st.session_state.winning_line = None
        st.session_state.turn = "X" if s["first"] == "Human" else s["ai_symbol"]
        st.session_state.power_cells = generate_power_cells(s["size"], s["power_cells_count"]) if s["power_cells_enabled"] else []
        st.session_state.swap_available = False
        st.session_state.has_swapped = False
    if st.session_state.swap_available and not st.session_state.has_swapped:
        st.write("Swap is available!")
        if st.button("Swap symbols (second player)"):
            # only allow swap by the player who is second to move (rough check: if last move made by X and X started, second is O)
            # permit swap action for either to keep simple UI (game fairness trusts player)
            s = st.session_state.settings
            # swap mapping of symbols only
            s["symbols"]["X"], s["symbols"]["O"] = s["symbols"]["O"], s["symbols"]["X"]
            st.session_state.has_swapped = True
            st.session_state.swap_available = False

with right:
    # draw grid of buttons (UI)
    n = st.session_state.settings["size"]
    sym = st.session_state.settings["symbols"]
    grid_cols = [st.columns(n) for _ in range(n)]
    for r in range(n):
        for c in range(n):
            val = st.session_state.board[r][c]
            label = sym[val] if val is not None else ""
            # visually mark power cells
            is_power = (r,c) in st.session_state.power_cells
            key = f"cell_{r}_{c}_{len(st.session_state.history)}"
            style_label = label or ("💠" if is_power else " ")
            if grid_cols[r][c].button(style_label, key=key):
                # clicking behavior: enforce turn rules
                if st.session_state.game_over:
                    pass
                else:
                    # If Human vs AI: only allow human to place when it's human's turn
                    if st.session_state.settings["mode"] == "Human vs AI":
                        ai_p = st.session_state.settings["ai_symbol"]
                        human_p = "O" if ai_p == "X" else "X"
                        if st.session_state.turn != human_p:
                            # not human turn
                            pass
                        else:
                            make_move(r,c, human_p)
                            if not st.session_state.game_over:
                                ai_move()
                    else:
                        # Human vs Human: accept move of current turn
                        make_move(r,c, st.session_state.turn)

    st.write("---")
    st.markdown("**Legend:**")
    st.markdown(f"- {st.session_state.settings['symbols']['X']}: X")
    st.markdown(f"- {st.session_state.settings['symbols']['O']}: O")
    st.markdown("- 💠 : Power Cell (play here and get an extra immediate move).")

# -------------------------
# Board textual & history
# -------------------------
st.write("---")
st.subheader("Board (text view)")
for r in range(len(st.session_state.board)):
    row = [st.session_state.settings["symbols"][v] if v is not None else "." for v in st.session_state.board[r]]
    st.write(" ".join(row))

st.subheader("Move history (latest first)")
for i, entry in enumerate(reversed(st.session_state.history[-50:]), 1):
    p,r,c = entry
    st.write(f"{i}. {p} ({st.session_state.settings['symbols'][p]}) → row {r+1}, col {c+1}")

# highlight winning line visually (small extra)
if st.session_state.winning_line:
    st.write("---")
    st.markdown("**Winning line:**")
    for (r,c) in st.session_state.winning_line:
        st.write(f"- row {r+1}, col {c+1}")

st.caption("Tip: Use Power Cells for combo plays. Try 5×5 with 4-in-a-row and a few power cells for creative puzzles.")
