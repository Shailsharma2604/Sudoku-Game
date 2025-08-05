import streamlit as st
from copy import deepcopy
import random
import time

# --- THEME DEFINITIONS ---
THEMES = {
    "Light": {
        "bg": "#f0f2f6", "grid_bg": "#95a5a6", "cell_bg": "#ffffff", "fixed_bg": "#ecf0f1",
        "text": "#2c3e50", "fixed_text": "#2c3e50", "user_text": "#3498db", "error_bg": "#ffcdd2",
        "highlight_bg": "#e0f7fa", "selected_bg": "#b3e5fc", "same_num_bg": "#d1c4e9",
        "border": "#7f8c8d", "button_bg": "#34495e", "button_hover": "#2c3e50"
    },
    "Dark": {
        "bg": "#2c3e50", "grid_bg": "#576574", "cell_bg": "#34495e", "fixed_bg": "#2c3e50",
        "text": "#ecf0f1", "fixed_text": "#ecf0f1", "user_text": "#5dade2", "error_bg": "#e57373",
        "highlight_bg": "#546e7a", "selected_bg": "#78909c", "same_num_bg": "#9575cd",
        "border": "#95a5a6", "button_bg": "#5dade2", "button_hover": "#3498db"
    },
    "Mint": {
        "bg": "#e0f2f1", "grid_bg": "#a7ffeb", "cell_bg": "#ffffff", "fixed_bg": "#e0f2f1",
        "text": "#004d40", "fixed_text": "#004d40", "user_text": "#00796b", "error_bg": "#ffab91",
        "highlight_bg": "#b2dfdb", "selected_bg": "#80cbc4", "same_num_bg": "#ce93d8",
        "border": "#4db6ac", "button_bg": "#00796b", "button_hover": "#004d40"
    }
}

# --- SUDOKU LOGIC CLASS ---
class Sudoku:
    """A class to encapsulate Sudoku game logic and state."""

    def __init__(self):
        """Initializes an empty Sudoku board."""
        self.board = [[0] * 9 for _ in range(9)]
        self.solution = None
        self.puzzle = None

    def find_empty(self):
        """Finds the first empty cell (0) in the board."""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return (i, j)
        return None

    def is_valid(self, row, col, num):
        """Checks if a number is a valid placement."""
        # Check row and column
        for x in range(9):
            if self.board[row][x] == num or self.board[x][col] == num:
                return False
        # Check 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.board[i + start_row][j + start_col] == num:
                    return False
        return True

    def solve(self):
        """Solves the board using backtracking."""
        find = self.find_empty()
        if not find:
            return True
        row, col = find
        for i in range(1, 10):
            if self.is_valid(row, col, i):
                self.board[row][col] = i
                if self.solve():
                    return True
                self.board[row][col] = 0
        return False

    def generate_puzzle(self, difficulty):
        """Generates a new puzzle."""
        self.board = [[0] * 9 for _ in range(9)]
        self.solve()  # Create a full, solved board
        self.solution = deepcopy(self.board)
        
        difficulty_map = {'Easy': 40, 'Medium': 52, 'Hard': 58, 'Expert': 62}
        squares_to_remove = difficulty_map.get(difficulty, 52)
        
        self.puzzle = deepcopy(self.solution)
        attempts = 0
        while squares_to_remove > 0 and attempts < 1000:
            row, col = random.randint(0, 8), random.randint(0, 8)
            if self.puzzle[row][col] != 0:
                self.puzzle[row][col] = 0
                squares_to_remove -= 1
            attempts += 1
        return self.puzzle, self.solution

# --- UI RENDERING FUNCTIONS ---

def get_theme_css(theme):
    """Generates the CSS string for the selected theme."""
    return f"""
    <style>
        .main {{ background-color: {theme['bg']}; }}
        h1 {{ color: {theme['text']}; text-align: center; font-family: 'Verdana', sans-serif; }}
        .stButton>button {{
            width: 100%; border-radius: 8px; border: 1px solid {theme['button_hover']};
            background-color: {theme['button_bg']}; color: white; transition: all 0.3s ease;
            padding: 10px 0; font-size: 16px;
        }}
        .stButton>button:hover {{ background-color: {theme['button_hover']}; }}
        .grid-container {{
            display: grid; grid-template-columns: repeat(9, 1fr); gap: 1px;
            background-color: {theme['grid_bg']}; border: 3px solid {theme['text']};
            border-radius: 8px; width: min(90vw, 500px); margin: 20px auto;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .grid-cell {{ background-color: {theme['cell_bg']}; aspect-ratio: 1 / 1; }}
        .grid-cell input {{
            width: 100%; height: 100%; text-align: center; border: none;
            font-size: clamp(1rem, 4vw, 1.8rem); font-weight: bold;
            color: {theme['user_text']}; background-color: transparent; padding: 0;
            caret-color: {theme['user_text']};
        }}
        .grid-cell.fixed input {{ color: {theme['fixed_text']}; background-color: {theme['fixed_bg']}; }}
        .grid-cell.highlighted {{ background-color: {theme['highlight_bg']}; }}
        .grid-cell.selected {{ background-color: {theme['selected_bg']}; }}
        .grid-cell.same-number {{ background-color: {theme['same_num_bg']}; }}
        .grid-cell.error {{ background-color: {theme['error_bg']}; }}
        .status-bar {{
            display: flex; justify-content: space-between; align-items: center;
            width: min(90vw, 500px); margin: 10px auto; font-size: 1.2rem; color: {theme['text']};
        }}
        .number-pad {{
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px;
            width: min(90vw, 500px); margin: 15px auto;
        }}
    </style>
    """

def render_grid(grid_data, fixed_cells, selected_cell):
    """Renders the Sudoku grid as HTML."""
    grid_html = '<div class="grid-container">'
    for i in range(9):
        for j in range(9):
            cell_val = grid_data[i][j]
            is_fixed = fixed_cells[i][j] != 0 if fixed_cells else False
            cell_class = "grid-cell"
            
            if is_fixed: cell_class += " fixed"
            if selected_cell:
                r, c = selected_cell
                selected_val = grid_data[r][c]
                if i == r or j == c or (i//3 == r//3 and j//3 == c//3): cell_class += " highlighted"
                if cell_val != 0 and cell_val == selected_val: cell_class += " same-number"
                if i == r and j == c: cell_class += " selected"

            # Error checking
            if not is_fixed and cell_val != 0:
                temp_grid = deepcopy(grid_data)
                temp_grid[i][j] = 0 # Check validity against the rest of the board
                s = Sudoku(); s.board = temp_grid
                if not s.is_valid(i, j, cell_val):
                    cell_class += " error"

            grid_html += f'<div class="{cell_class}"><input id="cell-{i}-{j}" value="{cell_val if cell_val != 0 else ""}" {"disabled" if is_fixed else ""} onfocus="handleFocus({i}, {j})"></div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

def render_number_pad(on_click_handler):
    """Renders the interactive number pad."""
    st.markdown('<div class="number-pad">', unsafe_allow_html=True)
    pad_cols = st.columns(10)
    for k in range(1, 10):
        with pad_cols[k-1]:
            st.button(str(k), on_click=on_click_handler, args=(k,), use_container_width=True)
    with pad_cols[9]:
        st.button("C", on_click=on_click_handler, args=(0,), help="Clear cell", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_javascript(start_time):
    """Renders the necessary JavaScript for interactivity."""
    st.components.v1.html(f"""
        <script>
            function handleFocus(row, col) {{
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: {{'type': 'select_cell', 'row': row, 'col': col}}}}, '*');
            }}
            document.querySelectorAll('.grid-cell input').forEach(input => {{
                input.addEventListener('focus', (e) => {{
                    const [row, col] = e.target.id.split('-').slice(1).map(Number);
                    handleFocus(row, col);
                }});
            }});
            const timerElement = window.parent.document.querySelector('.status-bar #timer');
            let startTime = {start_time if start_time else 0};
            if (startTime > 0 && timerElement) {{
                if (!window.sudokuTimer) {{
                    window.sudokuTimer = setInterval(() => {{
                        let elapsed = Math.floor(Date.now() / 1000 - startTime);
                        let minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
                        let seconds = (elapsed % 60).toString().padStart(2, '0');
                        timerElement.textContent = `Time: ${{minutes}}:${{seconds}}`;
                    }}, 1000);
                }}
            }} else if (timerElement) {{
                if(window.sudokuTimer) clearInterval(window.sudokuTimer); window.sudokuTimer = null;
                timerElement.textContent = 'Time: --:--';
            }}
        </script>
    """, height=0)
    component_value = st.components.v1.html("", height=0)
    # FIX: Check if the component_value is a dictionary before trying to access it
    if isinstance(component_value, dict) and component_value.get('type') == 'select_cell':
        st.session_state.selected_cell = (component_value['row'], component_value['col'])
        st.rerun()

# --- MAIN APP ---
def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Sudoku Fusion", layout="centered")

    # --- Initialize Session State ---
    if "mode" not in st.session_state:
        st.session_state.mode = 'Game'
        st.session_state.puzzle = None
        st.session_state.solution = None
        st.session_state.user_grid = None
        st.session_state.solver_grid = [[0]*9 for _ in range(9)]
        st.session_state.difficulty = 'Medium'
        st.session_state.start_time = None
        st.session_state.selected_cell = None
        st.session_state.theme = 'Light'

    # --- Render CSS and Title ---
    st.markdown(get_theme_css(THEMES[st.session_state.theme]), unsafe_allow_html=True)
    st.title("Sudoku Fusion �")

    # --- Sidebar ---
    with st.sidebar:
        st.header("Controls")
        st.session_state.mode = st.radio("Choose Mode", ['Game', 'Solver'], horizontal=True)
        st.session_state.theme = st.selectbox("Select Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme))

        if st.session_state.mode == 'Game':
            # --- Game Mode Controls ---
            st.header("Game Controls")
            difficulty = st.selectbox("Select Difficulty", ['Easy', 'Medium', 'Hard', 'Expert'], index=['Easy', 'Medium', 'Hard', 'Expert'].index(st.session_state.difficulty))
            if st.button("🚀 New Game"):
                game = Sudoku()
                st.session_state.puzzle, st.session_state.solution = game.generate_puzzle(difficulty)
                st.session_state.user_grid = deepcopy(st.session_state.puzzle)
                st.session_state.difficulty = difficulty
                st.session_state.start_time = time.time()
                st.session_state.selected_cell = None
                st.rerun()
            if st.session_state.puzzle is not None:
                if st.button("🔄 Reset Puzzle"):
                    st.session_state.user_grid = deepcopy(st.session_state.puzzle)
                    st.session_state.start_time = time.time()
                    st.rerun()
                if st.button("💡 Solve Puzzle"):
                    st.session_state.user_grid = deepcopy(st.session_state.solution)
                if st.button("✅ Check Solution"):
                    if all(all(c != 0 for c in r) for r in st.session_state.user_grid):
                        if st.session_state.user_grid == st.session_state.solution:
                            st.success("Congratulations! You solved it! 🎉"); st.balloons()
                            st.session_state.start_time = None
                        else: st.error("Something is not right. Keep trying!")
                    else: st.warning("Please fill all cells before checking.")
        
        else: # Solver Mode
            st.header("Solver Controls")
            if st.button("🧩 Solve My Puzzle"):
                solver = Sudoku(); solver.board = deepcopy(st.session_state.solver_grid)
                if solver.solve():
                    st.session_state.solver_grid = solver.board
                    st.success("Puzzle Solved!")
                else: st.error("This puzzle is unsolvable.")
            if st.button("🗑️ Clear Board"):
                st.session_state.solver_grid = [[0]*9 for _ in range(9)]
                st.session_state.selected_cell = None

    # --- Main Board Rendering ---
    if st.session_state.mode == 'Game':
        if st.session_state.puzzle is None:
            st.info("Select a difficulty and click 'New Game' to start!")
        else:
            st.markdown(f'<div class="status-bar"><div>Difficulty: <strong>{st.session_state.difficulty}</strong></div><div id="timer"></div></div>', unsafe_allow_html=True)
            render_grid(st.session_state.user_grid, st.session_state.puzzle, st.session_state.selected_cell)
            def set_game_number(num):
                if st.session_state.selected_cell:
                    r, c = st.session_state.selected_cell
                    if st.session_state.puzzle[r][c] == 0: st.session_state.user_grid[r][c] = num
            render_number_pad(set_game_number)
    else: # Solver Mode
        st.info("Enter your puzzle, then click 'Solve My Puzzle'.")
        render_grid(st.session_state.solver_grid, None, st.session_state.selected_cell)
        def set_solver_number(num):
            if st.session_state.selected_cell:
                r, c = st.session_state.selected_cell
                st.session_state.solver_grid[r][c] = num
        render_number_pad(set_solver_number)

    # --- Render JS for interactivity ---
    render_javascript(st.session_state.start_time)

if __name__ == "__main__":
    main()
