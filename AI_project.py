import tkinter as tk
from tkinter import messagebox
import random
import copy

# -------------------- Board and Fixed Cells --------------------
board = [[0]*9 for _ in range(9)]
fixed = [[False]*9 for _ in range(9)]
cells = [[None]*9 for _ in range(9)]
history = []

# -------------------- Simulation Variables --------------------
simulation_running = False
simulation_paused = False
simulation_gen = None

# Current game mode
current_mode = "Easy"

# -------------------- Sudoku Logic --------------------
def is_valid(bd, r, c, n):
    for i in range(9):
        if bd[r][i] == n or bd[i][c] == n:
            return False
    br, bc = (r//3)*3, (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if bd[i][j] == n:
                return False
    return True

def is_board_valid(bd):
    # Make a copy so we don't modify the original
    board_copy = copy.deepcopy(bd)
    for r in range(9):
        for c in range(9):
            val = board_copy[r][c]
            if val == 0:
                continue
            board_copy[r][c] = 0  # temporarily remove
            if not is_valid(board_copy, r, c, val):
                return False
            board_copy[r][c] = val
    return True

def solve_board(bd):
    for r in range(9):
        for c in range(9):
            if bd[r][c] == 0:
                for n in range(1, 10):
                    if is_valid(bd, r, c, n):
                        bd[r][c] = n
                        if solve_board(bd):
                            return True
                        bd[r][c] = 0
                return False
    return True

def is_solvable(bd):
    """Check if the board is solvable without modifying it"""
    temp = copy.deepcopy(bd)
    return solve_board(temp)

def generate_full(bd):
    for r in range(9):
        for c in range(9):
            if bd[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for n in nums:
                    if is_valid(bd, r, c, n):
                        bd[r][c] = n
                        if generate_full(bd):
                            return True
                        bd[r][c] = 0
                return False
    return True

def remove_cells(bd, diff):
    remove = {"Easy":35, "Medium":45, "Hard":55}[diff]
    while remove:
        r, c = random.randint(0,8), random.randint(0,8)
        if bd[r][c] != 0:
            bd[r][c] = 0
            remove -= 1

# -------------------- MAIN UI --------------------
root = tk.Tk()
root.title("Sudoku Solver AI - Final Presentation")
root.configure(bg="#f5f5f5")

# Color scheme
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#34495e"
ACCENT_COLOR = "#3498db"
SUCCESS_COLOR = "#27ae60"
WARNING_COLOR = "#f39c12"
DANGER_COLOR = "#e74c3c"
LIGHT_BG = "#ffffff"
DARK_BG = "#f8f9fa"
GRID_BG = "#ecf0f1"
GRID_LINE_COLOR = "#bdc3c7"
GRID_BLOCK_COLOR = "#2c3e50"

# Set window size and center it
window_width = 650
window_height = 750
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

highlight_enabled = tk.BooleanVar(root)
highlight_enabled.set(True)

# -------------------- UI Update --------------------
def update_ui():
    for r in range(9):
        for c in range(9):
            e = cells[r][c]
            e.config(state="normal")
            e.delete(0, tk.END)
            if board[r][c] != 0:
                e.insert(0, board[r][c])
                if fixed[r][c]:
                    e.config(bg="#ecf0f1", font=("Arial", 14, "bold"), 
                            fg=PRIMARY_COLOR, disabledbackground="#ecf0f1", 
                            disabledforeground=PRIMARY_COLOR)
                else:
                    e.config(bg="white", font=("Arial", 14), fg=PRIMARY_COLOR)
            else:
                e.config(bg="white", font=("Arial", 14), fg=PRIMARY_COLOR)
    highlight_conflicts()
    highlight_selected_cell()

def new_game(diff):
    global board, fixed, history, current_mode
    current_mode = diff
    mode_label.config(text=f"Current Mode: {current_mode}", 
                     bg=mode_colors[diff], fg="white")
    board = [[0]*9 for _ in range(9)]
    generate_full(board)
    remove_cells(board, diff)
    fixed = [[board[r][c] != 0 for c in range(9)] for r in range(9)]
    history = [copy.deepcopy(board)]
    update_ui()

# -------------------- Input Handling --------------------
def check_input(event, r, c):
    e = cells[r][c]
    val = e.get()
    if event.keysym in ("Up","Down","Left","Right"):
        return
    if fixed[r][c]:
        e.delete(0, tk.END)
        e.insert(0, board[r][c])
        return
    if val == "":
        board[r][c] = 0
        highlight_conflicts()
        history.append(copy.deepcopy(board))
        check_completion()
        return
    if not val.isdigit() or not (1 <= int(val) <= 9):
        e.delete(0, tk.END)
        board[r][c] = 0
        messagebox.showinfo("Invalid Input","Please enter a number 1-9")
        highlight_conflicts()
        return
    n = int(val)
    board[r][c] = n
    highlight_conflicts()
    history.append(copy.deepcopy(board))
    check_completion()

# -------------------- Navigation --------------------
def move(event, r, c):
    dr, dc = 0,0
    if event.keysym=="Up": dr=-1
    elif event.keysym=="Down": dr=1
    elif event.keysym=="Left": dc=-1
    elif event.keysym=="Right": dc=1
    new_r, new_c = r, c
    while True:
        new_r += dr
        new_c += dc
        if not (0<=new_r<9 and 0<=new_c<9):
            return
        break
    cells[new_r][new_c].focus()
    highlight_selected_cell()

# -------------------- Solve / Undo / Reset / Hint --------------------
def solve_click():
    # First check if current board is valid (no immediate conflicts)
    if not is_board_valid(board):
        messagebox.showerror(
            "Invalid Sudoku",
            "The current board has conflicts.\nPlease fix them before solving."
        )
        return

    # Check if the board is solvable
    if not is_solvable(board):
        messagebox.showwarning(
            "Dead End",
            "This puzzle has reached a dead end!\n\n" +
            "There are no immediate conflicts, but the puzzle cannot be solved " +
            "from this state.\n\n" +
            "Please use Undo or Reset to go back and try different numbers."
        )
        return

    # Create a copy to solve
    temp = copy.deepcopy(board)
    if solve_board(temp):
        # If solution found, update the main board
        for r in range(9):
            for c in range(9):
                board[r][c] = temp[r][c]
        update_ui()
        messagebox.showinfo("Solved!", "Sudoku puzzle solved successfully!")
    else:
        messagebox.showinfo("Sudoku", "No solution exists")

def undo():
    global board, history
    if len(history) > 1:
        history.pop()
        board[:] = copy.deepcopy(history[-1])
        update_ui()

def reset_board():
    global board, history
    for r in range(9):
        for c in range(9):
            if not fixed[r][c]:
                board[r][c] = 0
    history.append(copy.deepcopy(board))
    update_ui()

def give_hint():
    # First check if current board is valid
    if not is_board_valid(board):
        messagebox.showerror("Invalid Board", 
                           "The current board has conflicts. Please fix them before asking for a hint.")
        return
    
    # Check if the board is solvable
    if not is_solvable(board):
        messagebox.showwarning(
            "Dead End",
            "This puzzle has reached a dead end!\n\n" +
            "There are no immediate conflicts, but the puzzle cannot be solved " +
            "from this state.\n\n" +
            "Please use Undo or Reset to go back and try different numbers."
        )
        return
    
    # Find target cell (focused or random empty)
    focused = root.focus_get()
    target = None
    for r in range(9):
        for c in range(9):
            if cells[r][c] == focused:
                if not fixed[r][c] and board[r][c] == 0:
                    target = (r, c)
                break
        if target:
            break
    if not target:
        empty_cells = [(r,c) for r in range(9) for c in range(9) 
                      if board[r][c]==0 and not fixed[r][c]]
        if not empty_cells:
            messagebox.showinfo("No Hint", "The puzzle is already complete!")
            return
        target = random.choice(empty_cells)
    
    r, c = target
    
    # Make a copy of the board and solve it to find the correct number
    board_copy = copy.deepcopy(board)
    
    # First check if the puzzle is solvable
    if not solve_board(board_copy):
        messagebox.showerror("No Solution", 
                           "This puzzle has no solution. Please check your entries.")
        return
    
    # Now we have the solved board in board_copy
    correct_number = board_copy[r][c]
    
    # Place the correct number on the actual board
    board[r][c] = correct_number
    cells[r][c].delete(0, tk.END)
    cells[r][c].insert(0, correct_number)
    cells[r][c].config(bg="#d4edda", fg="#155724")
    
    # Add to history
    history.append(copy.deepcopy(board))
    
    # Check if puzzle is complete
    check_completion()

def check_completion():
    if all(board[r][c] != 0 for r in range(9) for c in range(9)):
        messagebox.showinfo("Sudoku","Congratulations! You solved the puzzle.")

# -------------------- Highlight Selected Cell --------------------
def highlight_selected_cell():
    focused = root.focus_get()
    for r in range(9):
        for c in range(9):
            e = cells[r][c]
            if fixed[r][c]:
                e.config(bg="#ecf0f1", fg=PRIMARY_COLOR)
            else:
                e.config(bg="white", fg=PRIMARY_COLOR)
            if cells[r][c] == focused:
                e.config(bg="#e3f2fd", fg=PRIMARY_COLOR, relief="sunken")

# -------------------- Conflict Highlight --------------------
def highlight_conflicts():
    for r in range(9):
        for c in range(9):
            e = cells[r][c]
            if fixed[r][c]:
                e.config(bg="#ecf0f1", fg=PRIMARY_COLOR, relief="flat")
            else:
                e.config(bg="white", fg=PRIMARY_COLOR, relief="flat")
    if not highlight_enabled.get():
        return
    for r in range(9):
        for c in range(9):
            val = board[r][c]
            if val == 0:
                continue
            # Row conflicts
            for i in range(9):
                if i != c and board[r][i] == val:
                    cells[r][i].config(bg="#f8d7da", fg="#721c24")
                    cells[r][c].config(bg="#f8d7da", fg="#721c24")
            # Column conflicts
            for i in range(9):
                if i != r and board[i][c] == val:
                    cells[i][c].config(bg="#f8d7da", fg="#721c24")
                    cells[r][c].config(bg="#f8d7da", fg="#721c24")
            # Block conflicts
            br, bc = (r//3)*3, (c//3)*3
            for i in range(br, br+3):
                for j in range(bc, bc+3):
                    if (i!=r or j!=c) and board[i][j]==val:
                        cells[i][j].config(bg="#f8d7da", fg="#721c24")
                        cells[r][c].config(bg="#f8d7da", fg="#721c24")

# -------------------- Simulation --------------------
def simulate_generator(bd):
    for r in range(9):
        for c in range(9):
            if bd[r][c] == 0:
                for n in range(1,10):
                    if is_valid(bd,r,c,n):
                        bd[r][c] = n
                        yield (r,c,n,"place")
                        yield from simulate_generator(bd)
                        bd[r][c] = 0
                        yield (r,c,n,"remove")
                return
    yield "done"

def start_simulation():
    global simulation_running, simulation_paused, simulation_gen
    simulation_running = True
    simulation_paused = False
    sim_board = copy.deepcopy(board)
    simulation_gen = simulate_generator(sim_board)
    simulate_step()

def simulate_step():
    global simulation_running, simulation_paused, simulation_gen, board
    if not simulation_running:
        return
    if simulation_paused:
        root.after(100, simulate_step)
        return
    try:
        step = next(simulation_gen)
    except StopIteration:
        simulation_running = False
        messagebox.showinfo("Sudoku","Simulation finished!")
        return
    if step == "done":
        simulation_running = False
        messagebox.showinfo("Sudoku","Simulation finished!")
        return
    r,c,n,action = step
    if action=="place":
        board[r][c] = n
        cells[r][c].delete(0, tk.END)
        cells[r][c].insert(0, n)
        cells[r][c].config(bg="#d4edda", fg="#155724")
    elif action=="remove":
        board[r][c] = 0
        cells[r][c].delete(0, tk.END)
        cells[r][c].config(bg="white", fg=PRIMARY_COLOR)
    highlight_conflicts()
    root.after(50, simulate_step)

def pause_simulation():
    global simulation_paused
    simulation_paused = True

def resume_simulation():
    global simulation_paused
    simulation_paused = False

# -------------------- Create Frames for Organization --------------------
main_frame = tk.Frame(root, bg="#f5f5f5")
main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

# -------------------- Title --------------------
title_frame = tk.Frame(main_frame, bg="#f5f5f5")
title_frame.pack(pady=(0, 5))

title_label = tk.Label(title_frame, text="Sudoku Solver AI", 
                       font=("Arial", 24, "bold"),
                       bg="#f5f5f5", fg=PRIMARY_COLOR)
title_label.pack()

subtitle_label = tk.Label(title_frame, text="Final Presentation - Intelligent Puzzle Solver", 
                         font=("Arial", 10),
                         bg="#f5f5f5", fg=SECONDARY_COLOR)
subtitle_label.pack()

# -------------------- Mode Display --------------------
mode_frame = tk.Frame(main_frame, bg="#f5f5f5")
mode_frame.pack(pady=(5, 15))

mode_colors = {
    "Easy": SUCCESS_COLOR,
    "Medium": WARNING_COLOR,
    "Hard": DANGER_COLOR
}

mode_label = tk.Label(mode_frame, text=f"Current Mode: {current_mode}", 
                     font=("Arial", 14, "bold"),
                     bg=mode_colors[current_mode], fg="white",
                     padx=20, pady=8, relief="raised", bd=2)
mode_label.pack()

# -------------------- Features Display --------------------
features_frame = tk.Frame(main_frame, bg="#f5f5f5")
features_frame.pack(pady=(0, 15))

features_label = tk.Label(features_frame, 
                         text="• Real-time Conflict Detection • Backtracking Solver • Intelligent Hints •",
                         font=("Arial", 9, "italic"),
                         bg="#f5f5f5", fg=SECONDARY_COLOR)
features_label.pack()

# -------------------- Sudoku Grid --------------------
grid_container = tk.Frame(main_frame, bg=GRID_BLOCK_COLOR, bd=2, relief="solid")
grid_container.pack(pady=(0, 15))

# Create the main grid
for r in range(9):
    for c in range(9):
        # Determine border thickness
        border_left = 2 if c % 3 == 0 else 1
        border_top = 2 if r % 3 == 0 else 1
        
        # Create cell frame
        cell_frame = tk.Frame(grid_container, 
                             highlightbackground=GRID_LINE_COLOR,
                             highlightthickness=1,
                             bg="white")
        cell_frame.grid(row=r, column=c, sticky="nsew", 
                       padx=(border_left, 0), 
                       pady=(border_top, 0))
        
        # Add thicker borders for block boundaries
        if border_left == 2:
            left_border = tk.Frame(cell_frame, bg=GRID_BLOCK_COLOR, width=2)
            left_border.pack(side="left", fill="y")
        
        if border_top == 2:
            top_border = tk.Frame(cell_frame, bg=GRID_BLOCK_COLOR, height=2)
            top_border.pack(side="top", fill="x")
        
        # Create the entry widget
        e = tk.Entry(cell_frame, width=1, font=("Arial", 12),
                    justify="center", relief="flat", bd=0, 
                    bg="white", fg=PRIMARY_COLOR, 
                    highlightthickness=0, insertbackground=PRIMARY_COLOR)
        e.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Bind events
        e.bind("<KeyRelease>", lambda ev, r=r, c=c: check_input(ev, r, c))
        e.bind("<Up>", lambda ev, r=r, c=c: move(ev, r, c))
        e.bind("<Down>", lambda ev, r=r, c=c: move(ev, r, c))
        e.bind("<Left>", lambda ev, r=r, c=c: move(ev, r, c))
        e.bind("<Right>", lambda ev, r=r, c=c: move(ev, r, c))
        e.bind("<Button-1>", lambda ev, r=r, c=c: highlight_selected_cell())
        e.bind("<FocusIn>", lambda ev, r=r, c=c: highlight_selected_cell())
        cells[r][c] = e

# Configure grid weights for even distribution
for i in range(9):
    grid_container.grid_rowconfigure(i, weight=1, minsize=32)
    grid_container.grid_columnconfigure(i, weight=1, minsize=32)

# -------------------- Control Panels --------------------
# Create a consistent styling for all buttons
def create_styled_button(parent, text, command, color=ACCENT_COLOR, width=8):
    btn = tk.Button(parent, text=text, font=("Arial", 9, "bold"),
                   bg=color, fg="white", activebackground=color,
                   activeforeground="white", relief="raised", 
                   padx=8, pady=4, cursor="hand2", bd=2,
                   command=command, width=width)
    return btn

# Use a different layout: Combine difficulty and game controls in one row
top_controls_frame = tk.Frame(main_frame, bg="#f5f5f5")
top_controls_frame.pack(fill=tk.X, pady=(0, 10))

# Left side: Difficulty
difficulty_frame = tk.Frame(top_controls_frame, bg="#f5f5f5")
difficulty_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

difficulty_label = tk.Label(difficulty_frame, text="DIFFICULTY:", 
                           font=("Arial", 10, "bold", "underline"),
                           bg="#f5f5f5", fg=PRIMARY_COLOR)
difficulty_label.pack(anchor=tk.W, padx=(0, 5))

diff_btn_frame = tk.Frame(difficulty_frame, bg="#f5f5f5")
diff_btn_frame.pack(pady=3)

create_styled_button(diff_btn_frame, "Easy", lambda: new_game("Easy"), SUCCESS_COLOR, 8).pack(side=tk.LEFT, padx=2)
create_styled_button(diff_btn_frame, "Medium", lambda: new_game("Medium"), WARNING_COLOR, 8).pack(side=tk.LEFT, padx=2)
create_styled_button(diff_btn_frame, "Hard", lambda: new_game("Hard"), DANGER_COLOR, 8).pack(side=tk.LEFT, padx=2)

# Right side: Game Controls
game_controls_frame = tk.Frame(top_controls_frame, bg="#f5f5f5")
game_controls_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

game_label = tk.Label(game_controls_frame, text="GAME CONTROLS:", 
                     font=("Arial", 10, "bold", "underline"),
                     bg="#f5f5f5", fg=PRIMARY_COLOR)
game_label.pack(anchor=tk.W, padx=(0, 5))

game_btn_frame = tk.Frame(game_controls_frame, bg="#f5f5f5")
game_btn_frame.pack(pady=3)

create_styled_button(game_btn_frame, "Solve", solve_click, ACCENT_COLOR, 8).pack(side=tk.LEFT, padx=2)
create_styled_button(game_btn_frame, "Undo", undo, "#9b59b6", 8).pack(side=tk.LEFT, padx=2)
create_styled_button(game_btn_frame, "Reset", reset_board, "#e67e22", 8).pack(side=tk.LEFT, padx=2)
create_styled_button(game_btn_frame, "Hint", give_hint, "#2ecc71", 8).pack(side=tk.LEFT, padx=2)

# Options and Simulation in one row
bottom_controls_frame = tk.Frame(main_frame, bg="#f5f5f5")
bottom_controls_frame.pack(fill=tk.X, pady=(10, 0))

# Left: Options
options_frame = tk.Frame(bottom_controls_frame, bg="#f5f5f5")
options_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

options_label = tk.Label(options_frame, text="OPTIONS:", 
                        font=("Arial", 10, "bold", "underline"),
                        bg="#f5f5f5", fg=PRIMARY_COLOR)
options_label.pack(anchor=tk.W, padx=(0, 5))

options_content = tk.Frame(options_frame, bg="#f5f5f5")
options_content.pack(pady=3)

# Highlight checkbox
check = tk.Checkbutton(options_content, text="Highlight Conflicts", 
                       variable=highlight_enabled, command=highlight_conflicts,
                       font=("Arial", 9, "bold"), bg="#f5f5f5", fg=PRIMARY_COLOR,
                       activebackground="#f5f5f5", activeforeground=PRIMARY_COLOR,
                       selectcolor="#f5f0f0")
check.pack(side=tk.LEFT)

# Right: Simulation
simulation_frame = tk.Frame(bottom_controls_frame, bg="#f5f5f5")
simulation_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

sim_label = tk.Label(simulation_frame, text="VISUALIZATION:", 
                    font=("Arial", 10, "bold", "underline"),
                    bg="#f5f5f5", fg=PRIMARY_COLOR)
sim_label.pack(anchor=tk.W, padx=(0, 5))

sim_btn_frame = tk.Frame(simulation_frame, bg="#f5f5f5")
sim_btn_frame.pack(pady=3)

create_styled_button(sim_btn_frame, "Start", start_simulation, SECONDARY_COLOR, 8).pack(side=tk.LEFT, padx=2)
create_styled_button(sim_btn_frame, "Pause", pause_simulation, "#e74c3c", 8).pack(side=tk.LEFT, padx=2)
create_styled_button(sim_btn_frame, "Resume", resume_simulation, "#2ecc71", 8).pack(side=tk.LEFT, padx=2)

# -------------------- Footer --------------------
footer_frame = tk.Frame(main_frame, bg="#f5f5f5")
footer_frame.pack(fill=tk.X, pady=(15, 0))

footer_label = tk.Label(footer_frame, 
                       text="Sudoku Solver AI Project | Backtracking Algorithm | Python Tkinter GUI",
                       font=("Arial", 8),
                       bg="#f5f5f5", fg=SECONDARY_COLOR)
footer_label.pack()

# Start the game
new_game("Easy")
root.mainloop()