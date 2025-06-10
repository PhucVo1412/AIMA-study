from dataclasses import dataclass
from typing import List, Optional
from abc import ABC, abstractmethod
import heapq
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time

# --------- Node Class -----------
@dataclass
class Node:
    state: List[List[int]]
    parent: Optional['Node']
    action: Optional[str]
    cost: int
    depth: int

    def __lt__(self, other):  # < operator
        return (self.cost + self.depth) < (other.cost + other.depth)


# --------- State Logic -----------
class State:
    def __init__(self, state: List[List[int]]):
        self.state = state
        self.size = 3  # For 8-puzzle

    def find_zero(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.state[i][j] == 0:
                    return i, j
        return None

    def move(self, direction: str):
        i, j = self.find_zero()
        new_state = [row[:] for row in self.state]
        if direction == "up" and i > 0:
            new_state[i][j], new_state[i-1][j] = new_state[i-1][j], new_state[i][j]
        elif direction == "down" and i < self.size - 1:
            new_state[i][j], new_state[i+1][j] = new_state[i+1][j], new_state[i][j]
        elif direction == "left" and j > 0:
            new_state[i][j], new_state[i][j-1] = new_state[i][j-1], new_state[i][j]
        elif direction == "right" and j < self.size - 1:
            new_state[i][j], new_state[i][j+1] = new_state[i][j+1], new_state[i][j]
        else:
            return None
        return new_state

    def successors(self):
        directions = ['up', 'down', 'left', 'right']
        result = []
        for d in directions:
            new_state = self.move(d)
            if new_state:
                result.append((d, new_state))
        return result


# --------- Abstract Search Base Class -----------
class SearchingStrategy(ABC):
    @abstractmethod
    def search(self, init_state: List[List[int]], goal_state: List[List[int]]) -> Optional[Node]:
        pass


# --------- Breadth-First Search -----------
class BFSearch(SearchingStrategy):
    def search(self, init_state, goal_state):
        root = Node(init_state, None, None, 0, 0)
        queue = [root]
        visited = set()

        while queue:
            node = queue.pop(0)
            if node.state == goal_state:
                return node
            visited.add(str(node.state))

            for action, new_state in State(node.state).successors():
                if str(new_state) not in visited:
                    child = Node(new_state, node, action, 0, node.depth + 1)
                    queue.append(child)
        return None

#-----------DFS------------------------
class DFSearch(SearchingStrategy):
    def search(self, init_state, goal_state):
        root = Node(init_state, None, None, 0, 0)
        stack = [root]
        visited = set()

        while stack:
            node = stack.pop()
            if node.state == goal_state:
                return node
            visited.add(str(node.state))

            for action, new_state in reversed(State(node.state).successors()):
                if str(new_state) not in visited:
                    child = Node(new_state, node, action, 0, node.depth + 1)
                    stack.append(child)
        return None

#---------Iterative Deepening DFS------------
class IDDFSearch(SearchingStrategy):
    def search(self, init_state, goal_state):
        def dls(node, depth_limit):
            if node.state == goal_state:
                return node
            if depth_limit == 0:
                return None
            for action, new_state in State(node.state).successors():
                child = Node(new_state, node, action, 0, node.depth + 1)
                result = dls(child, depth_limit - 1)
                if result:
                    return result
            return None

        for depth in range(50):  # Max depth limit
            root = Node(init_state, None, None, 0, 0)
            result = dls(root, depth)
            if result:
                return result
        return None


# --------- A* Search -----------
class AstarSearch(SearchingStrategy):
    def __init__(self):
        pass

    def heuristic_Manhattan(self, state, goal):
        # Manhattan distance
        total = 0
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                if val != 0:
                    for x in range(3):
                        for y in range(3):
                            if goal[x][y] == val:
                                total += abs(x - i) + abs(y - j)
        return total
    
    def heuristic_Nilson(self, state, goal):
        def manhattan():
            return self.heuristic_Manhattan(state, goal)

        seq_score = 0
        spiral_order = [(0,0),(0,1),(0,2),(1,2),(2,2),(2,1),(2,0),(1,0)]
        spiral_vals = [state[i][j] for i, j in spiral_order]
        for idx in range(len(spiral_vals) - 1):
            if (spiral_vals[idx] + 1) % 8 != spiral_vals[idx + 1] % 8:
                seq_score += 2
        if state[1][1] != 0:
            seq_score += 1
        return manhattan() + seq_score

    def heuristic_LinearConflict(self, state, goal):
        def manhattan():
            return self.heuristic_Manhattan(state, goal)

        def find_conflicts(line, goal_line):
            conflict = 0
            for i in range(len(line)):
                for j in range(i + 1, len(line)):
                    if line[i] in goal_line and line[j] in goal_line:
                        if goal_line.index(line[i]) > goal_line.index(line[j]):
                            conflict += 1
            return conflict

        linear_conflict = 0
        for i in range(3):
            row = state[i]
            goal_row = [goal[i][j] for j in range(3)]
            linear_conflict += find_conflicts(row, goal_row)

            col = [state[j][i] for j in range(3)]
            goal_col = [goal[j][i] for j in range(3)]
            linear_conflict += find_conflicts(col, goal_col)
        return manhattan() + 2 * linear_conflict

    def heuristic_PatternDB(self, state, goal):
        # Simulate with Manhattan distance over two subsets
        subset1 = {1, 2, 3, 4}
        subset2 = {5, 6, 7, 8}
        dist1 = 0
        dist2 = 0
        goal_pos = {val: (i, j) for i in range(3) for j in range(3) if goal[i][j] != 0 for val in [goal[i][j]]}
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                if val in goal_pos:
                    goal_i, goal_j = goal_pos[val]
                    if val in subset1:
                        dist1 += abs(i - goal_i) + abs(j - goal_j)
                    elif val in subset2:
                        dist2 += abs(i - goal_i) + abs(j - goal_j)
        return dist1 + dist2
    
    def heuristic_PatternDB(self, state, goal):
        return 0

    def search(self, init_state, goal_state):
        root = Node(init_state, None, None, self.heuristic_Manhattan(init_state, goal_state), 0)
        frontier = []
        heapq.heappush(frontier, root)
        visited = set()

        while frontier:
            node = heapq.heappop(frontier)
            if node.state == goal_state:
                return node
            visited.add(str(node.state))

            for action, new_state in State(node.state).successors():
                if str(new_state) not in visited:
                    cost = self.heuristic_Manhattan(new_state, goal_state)
                    child = Node(new_state, node, action, cost, node.depth + 1)
                    heapq.heappush(frontier, child)
        return None


# --------- Game Manager -----------
class GameManager:
    def __init__(self, init_state, goal_state, searcher: SearchingStrategy):
        self.init_state = init_state
        self.goal_state = goal_state
        self.searcher = searcher

    def solve(self):
        return self.searcher.search(self.init_state, self.goal_state)

    def print_solution(self, node):
        path = []
        while node:
            path.append((node.action, node.state))
            node = node.parent
        for step in reversed(path):
            print("Action:", step[0])
            for row in step[1]:
                print(row)
            print()


class PuzzleGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("8-Puzzle Solver")
        self.master.geometry("400x500")  # Optional initial size

        # Make grid expandable
        for i in range(6):  # 3 rows puzzle + dropdown + button + output
            self.master.rowconfigure(i, weight=1)
        for j in range(3):  # 3 columns
            self.master.columnconfigure(j, weight=1)

        self.entries = [[None]*3 for _ in range(3)]
        self.create_grid()

        self.algorithm_var = tk.StringVar(value="A*")
        self.algo_dropdown = ttk.Combobox(master, textvariable=self.algorithm_var, values=["A*", "BFS", "DFS", "IDDFS", "Greedy"])
        self.algo_dropdown.grid(row=3, column=0, columnspan=3, pady=5, sticky="nsew")

        self.solve_button = tk.Button(master, text="Solve", command=self.solve_puzzle)
        self.solve_button.grid(row=4, column=0, columnspan=3, pady=10, sticky="nsew")

        self.output_label = tk.Label(master, text="", font=("Arial", 12), wraplength=300, anchor="center", justify="center")
        self.output_label.grid(row=5, column=0, columnspan=3, sticky="nsew")

    def create_grid(self):
        for i in range(3):
            for j in range(3):
                entry = tk.Entry(self.master, width=3, justify='center', font=("Arial", 24))
                entry.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                self.entries[i][j] = entry


    def get_initial_state(self):
        try:
            state = []
            used = set()
            for i in range(3):
                row = []
                for j in range(3):
                    val = int(self.entries[i][j].get())
                    if val < 0 or val > 8 or val in used:
                        raise ValueError
                    used.add(val)
                    row.append(val)
                state.append(row)
            return state
        except:
            messagebox.showerror("Invalid Input", "Enter digits 0-8 with no duplicates.")
            return None

    def solve_puzzle(self):
        init_state = self.get_initial_state()
        if init_state is None:
            return
        goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        
        # Select the algorithm
        selected_algo = self.algorithm_var.get()

        if selected_algo == "A*":
            searcher = AstarSearch()
        elif selected_algo == "BFS":
            searcher = BFSearch()
        elif selected_algo == "DFS":
            searcher = DFSearch()
        elif selected_algo == "IDDFS":
            searcher = IDDFSearch()
        else:
            messagebox.showerror("Error", "Unknown algorithm selected.")
            return


        manager = GameManager(init_state, goal, searcher)
        start = time.time()
        result = manager.solve()
        end = time.time()

        if not result:
            self.output_label.config(text="No solution found.")
            return

		# Get path
        path = []
        while result and result.action is not None:
            path.append(result.action.upper()[0])
            result = result.parent

        self.output_label.config(
		    text=f"Solution: {' '.join(reversed(path))}\nMoves: {len(path)}\nTime: {end-start:.4f}s"
		)


# --------- Example Run with UI -----------
if __name__ == "__main__":
    root = tk.Tk()
    gui = PuzzleGUI(root)
    root.mainloop()

#-------------No UI run example----------------
# if __name__ == "__main__":
#     init_state = [[0, 6, 3], [2, 1, 8], [7, 5, 4]]
#     goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

#     # Choose the search strategy
#     searcher = AstarSearch()  # or BFSearch(), DFSearch(), IDDFSearch()

#     manager = GameManager(init_state, goal_state, searcher)
#     result = manager.solve()

#     if result:
#         manager.print_solution(result)
#     else:
#         print("No solution found.")