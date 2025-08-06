import streamlit as st
import numpy as np
import time
import random
import json
import os

# 🎨 Set page config
st.set_page_config(page_title="🎯 Sudoku Master Pro", layout="wide")

# ✅ Initialize session state
def init_state():
    if "original_board" not in st.session_state:
        st.session_state.original_board = np.zeros((9, 9), dtype=int)
    if "board" not in st.session_state:
        st.session_state.board = np.copy(st.session_state.original_board)
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    if "hints_used" not in st.session_state:
        st.session_state.hints_used = 0
    if "moves" not in st.session_state:
        st.session_state.moves = []
    if "score" not in st.session_state:
        st.session_state.score = 1000
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Easy"

init_state()

# 📁 Constants
DIFFICULTY_LEVELS = {
    "Easy": 35,
    "Medium": 30,
    "Hard": 25
}

LEADERBOARD_FILE = "leaderboard.json"

# 🧠 Sudoku Generator
def generate_sudoku(difficulty="Easy"):
    board = np.zeros((9, 9), dtype=int)
    fill_diagonal_blocks(board)
    solve(board)
    solution = np.copy(board)
    remove_cells(board, DIFFICULTY_LEVELS[difficulty])
    return board, solution

def fill_diagonal_blocks(board):
    for i in range(0, 9, 3):
        nums = random.sample(range(1, 10), 9)
        for row in range(3):
            for col in range(3):
                board[i+row][i+col] = nums.pop()

def solve(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                for n in range(1, 10):
                    if is_valid(board, i, j, n):
                        board[i][j] = n
                        if solve(board):
                            return True
                        board[i][j] = 0
                return False
    return True

def is_valid(board, row, col, num):
    block_row, block_col = row // 3 * 3, col // 3 * 3
    return all([
        num not in board[row, :],
        num not in board[:, col],
        num not in board[block_row:block_row+3, block_col:block_col+3]
    ])

def remove_cells(board, count):
    removed = 0
    while removed < 81 - count:
        i, j = random.randint(0, 8), random.randint(0, 8)
        if board[i][j] != 0:
            board[i][j] = 0
            removed += 1

# 💾 Leaderboard
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r") as file:
        return json.load(file)

def save_score(name, score, time_taken, difficulty):
    leaderboard = load_leaderboard()
    leaderboard.append({
        "name": name,
        "score": score,
        "time": round(time_taken, 2),
        "difficulty": difficulty
    })
    leaderboard.sort(key=lambda x: (-x["score"], x["time"]))
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file, indent=2)

# 🎵 Music Toggle (Basic Sound)
def audio_tag():
    audio_html = """
    <audio autoplay loop>
        <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# 🔢 Sudoku Grid UI
def draw_board():
    for i in range(9):
        cols = st.columns(9)
        for j in range(9):
            key = f"cell-{i}-{j}"
            default_val = (
                int(st.session_state.board[i][j])
                if st.session_state.board[i][j] != 0
                else ""
            )
            disabled = st.session_state.original_board[i][j] != 0
            val = cols[j].text_input("", value=str(default_val), max_chars=1, key=key, disabled=disabled)
            if val.isdigit():
                val_int = int(val)
                if 1 <= val_int <= 9:
                    if not disabled:
                        st.session_state.moves.append((i, j, st.session_state.board[i][j]))
                        st.session_state.board[i][j] = val_int

# 💡 Hint Generator
def give_hint():
    for i in range(9):
        for j in range(9):
            if st.session_state.board[i][j] == 0:
                st.session_state.board[i][j] = st.session_state.solution[i][j]
                st.session_state.hints_used += 1
                st.success(f"Hint placed at ({i+1}, {j+1})")
                return

# 🔍 Validator
def validate_board():
    board = st.session_state.board
    for i in range(9):
        for j in range(9):
            if board[i][j] != 0 and not is_valid(board, i, j, board[i][j]):
                st.error(f"Invalid number at row {i+1}, column {j+1}")
                return
    st.success("Board looks valid so far!")

# 🔄 Undo
def undo_move():
    if st.session_state.moves:
        i, j, prev = st.session_state.moves.pop()
        st.session_state.board[i][j] = prev

# ⏱ Timer
def show_timer():
    elapsed = int(time.time() - st.session_state.start_time)
    mins, secs = divmod(elapsed, 60)
    st.sidebar.markdown(f"⏱ **Time:** {mins:02d}:{secs:02d}")
    return elapsed

# 🧠 Game Logic
st.sidebar.header("🧩 Sudoku Controls")
difficulty = st.sidebar.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
if st.sidebar.button("🆕 Generate Puzzle"):
    board, solution = generate_sudoku(difficulty)
    st.session_state.original_board = np.copy(board)
    st.session_state.board = np.copy(board)
    st.session_state.solution = solution
    st.session_state.difficulty = difficulty
    st.session_state.start_time = time.time()
    st.session_state.hints_used = 0
    st.session_state.moves = []

if st.sidebar.checkbox("🎵 Play Background Music"):
    audio_tag()

draw_board()

# Footer controls
col1, col2, col3, col4, col5 = st.columns(5)
if col1.button("💡 Hint"):
    give_hint()

if col2.button("🔍 Validate"):
    validate_board()

if col3.button("🔄 Undo"):
    undo_move()

if col4.button("✅ Submit"):
    if np.array_equal(st.session_state.board, st.session_state.solution):
        elapsed = show_timer()
        hints = st.session_state.hints_used
        score = max(1000 - elapsed - (hints * 50), 0)
        st.success(f"🎉 Solved! Time: {elapsed}s | Hints used: {hints} | Score: {score}")
        name = st.text_input("Enter your name for leaderboard:")
        if name:
            save_score(name, score, elapsed, st.session_state.difficulty)
    else:
        st.error("❌ Incorrect solution. Try again!")

if col5.button("🔁 Reset"):
    st.session_state.board = np.copy(st.session_state.original_board)

# Timer
elapsed_time = show_timer()

# 📈 Leaderboard Display
st.sidebar.header("🏆 Leaderboard")
leaderboard = load_leaderboard()
for entry in leaderboard[:5]:
    st.sidebar.markdown(
        f"{entry['name']} – {entry['score']} pts – {entry['time']}s ({entry['difficulty']})"
    )
