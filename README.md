# Sudoku Solver AI

An interactive **9×9 Sudoku desktop application** built with Python and Tkinter. Generate puzzles, play manually, request hints, solve the board, and watch recursive backtracking step by step.

This project demonstrates **classical AI search and constraint satisfaction**: each empty cell must receive a number that satisfies the row, column, and 3×3 box constraints. It uses algorithmic search without a trained machine-learning model or external AI service.

## Features

- **Puzzle generation:** create a new board in Easy, Medium, or Hard mode.
- **Automatic solver:** solve a valid, solvable board using recursive backtracking.
- **Hints:** fill a selected empty cell, or a random empty cell when no suitable cell is selected, using a solution of the current board.
- **Conflict highlighting:** highlight repeated numbers in a row, column, or 3×3 box; turn highlighting on or off.
- **Dead-end checks:** Solve and Hint check both immediate conflicts and whether the current board can still be solved.
- **Undo and reset:** restore recorded board states or clear entries while retaining the original clues.
- **Animated visualization:** watch candidate placements and backtracking with Start, Pause, and Resume.
- **Keyboard navigation:** move between cells with the arrow keys.
- **Input validation:** accept numbers from 1 to 9 and preserve the generated clues.

## Quick start

### Requirements

- Python 3 with **Tkinter/Tcl/Tk** support.
- A desktop graphical environment.

The application imports only `tkinter`, `random`, and `copy`. No third-party Python packages, dataset, API key, or model download are required.

### Download the project

Clone the repository:

```bash
git clone https://github.com/Asif78980/Sudoku-Solver-AI.git
cd Sudoku-Solver-AI
```

Alternatively, select **Code → Download ZIP** on GitHub, extract the ZIP, and open a terminal in the extracted folder.

### Run on Windows

```powershell
python AI_project.py
```

If your installation uses the Python launcher:

```powershell
py AI_project.py
```

### Run on macOS or Linux

```bash
python3 AI_project.py
```

An Easy puzzle opens automatically when the application starts.

To check whether Tkinter is available, run `python -m tkinter` (or `python3 -m tkinter`). A small demonstration window should open. If the module is missing, install or enable the Tcl/Tk support supplied by your Python installation or operating system.

## How to use

1. Choose **Easy**, **Medium**, or **Hard** to generate a new puzzle.
2. Click an editable cell and enter a number from **1–9**. Use Backspace or Delete to clear an entry.
3. Use the arrow keys to move around the grid.
4. Keep **Highlight Conflicts** enabled to see duplicate-number conflicts as you type.
5. Use **Hint** for help with one empty cell or **Solve** to fill the board.
6. To explore the algorithm, begin with a conflict-free board and select **Start** under Visualization. Use **Pause** and **Resume** to control the animation.

| Control | What it does |
|---|---|
| Easy / Medium / Hard | Generates a fresh puzzle and replaces the current game |
| Solve | Validates the board, checks solvability, and fills a solution |
| Undo | Returns to an earlier recorded board state |
| Reset | Clears non-clue cells while preserving the original puzzle |
| Hint | Fills one empty cell from a solution consistent with the current entries |
| Highlight Conflicts | Toggles duplicate-number highlighting |
| Start | Begins the backtracking animation from the current board |
| Pause / Resume | Pauses or continues the animation |

During visualization, let the animation finish before editing cells, starting another animation, or changing the puzzle. The current implementation does not lock these controls while it runs.

## Difficulty levels

The generator first creates a complete valid board using randomized backtracking, then removes a fixed number of cells.

| Mode | Empty cells | Remaining clues |
|---|---:|---:|
| Easy | 35 | 46 |
| Medium | 45 | 36 |
| Hard | 55 | 26 |

These labels are based on the number of removed cells. The generator does not measure logical solving difficulty or check that a puzzle has exactly one solution.

## How the solver works

Sudoku is treated as a **constraint satisfaction problem**:

- **Variables:** empty cells.
- **Domain:** numbers 1 through 9.
- **Constraints:** a number cannot repeat in its row, column, or 3×3 box.

The solver uses depth-first search with backtracking:

1. Find the next empty cell in row order.
2. Try the numbers 1–9.
3. Place a number only if it satisfies all three constraints.
4. Recursively solve the remaining cells.
5. If that choice reaches a dead end, clear it and try the next number.
6. Return success once there are no empty cells left.

The visualization uses a Python generator to yield placement and removal steps. Tkinter's `after()` schedules the next animation step at a nominal 50 ms interval.

## Code guide

The implementation is contained in [AI_project.py](AI_project.py).

| Function | Purpose |
|---|---|
| `is_valid()` | Checks whether a candidate satisfies row, column, and box constraints |
| `is_board_valid()` | Checks existing entries for immediate conflicts |
| `solve_board()` | Solves a board using recursive backtracking |
| `is_solvable()` | Tries solving a copy without changing the current board |
| `generate_full()` | Generates a complete board with randomized candidate order |
| `remove_cells()` | Removes cells according to the selected mode |
| `new_game()` | Creates a puzzle and records its original clues |
| `check_input()` | Handles user entries and records board history |
| `give_hint()` | Finds and fills one value from a solution |
| `highlight_conflicts()` | Marks duplicate values in the grid |
| `simulate_generator()` | Yields backtracking steps for visualization |
| `simulate_step()` | Updates the board during the animation |

Board values are stored in a 9×9 list, with `0` representing an empty cell. A separate `fixed` grid identifies the original clues, and copied board states support Undo.

## Current limitations

- Generated puzzles are solvable, but **unique solutions are not guaranteed**. Hints therefore follow one valid solution consistent with the current entries.
- The manual completion notification checks whether all cells are filled; it does not perform a final Sudoku-validity check. A full board with conflicts can incorrectly trigger the notification.
- Visualization does not run the same initial validity and solvability checks as Solve and Hint.
- Undo tracks recorded edits, hints, and resets; Solve and animation steps are not independently added to the history.
- Puzzle generation and the non-animated solver run on the GUI thread, so demanding searches can temporarily make the window unresponsive.
- Games are kept in memory; save/load, puzzle import, and progress persistence are not implemented.

## Possible improvements

- Guarantee a unique solution during puzzle generation.
- Validate all constraints before displaying the completion message.
- Add a Stop button and disable conflicting controls during visualization.
- Add the minimum remaining values (MRV) heuristic to improve search efficiency.
- Support saving games, importing custom puzzles, and adjustable animation speed.
