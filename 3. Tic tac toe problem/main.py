from dataclasses import dataclass
from typing import List
import tkinter as tk
from tkinter import messagebox

# --------- State Logic -----------
@dataclass
class State:
    board: List[List[str]]

    def __init__(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]

    def is_full(self):
        return all(cell != '' for row in self.board for cell in row)

    def winner(self):
        b = self.board
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] != '':
                return b[i][0]
            if b[0][i] == b[1][i] == b[2][i] != '':
                return b[0][i]
        if b[0][0] == b[1][1] == b[2][2] != '':
            return b[0][0]
        if b[0][2] == b[1][1] == b[2][0] != '':
            return b[0][2]
        return None

    def available_moves(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == '']

    def make_move(self, i, j, player):
        self.board[i][j] = player

    def undo_move(self, i, j):
        self.board[i][j] = ''


# --------- Alpha-Beta Pruning AI -----------
class AlphaBetaAI:
    def __init__(self, player):
        self.ai_player = player
        self.human_player = 'X' if player == 'O' else 'O'

    def best_move(self, state: State):
        best_score = float('-inf')
        move = None
        for i, j in state.available_moves():
            state.make_move(i, j, self.ai_player)
            score = self.minimax(state, 0, False, float('-inf'), float('inf'))
            state.undo_move(i, j)
            if score > best_score:
                best_score = score
                move = (i, j)
        return move

    def minimax(self, state, depth, is_max, alpha, beta):
        winner = state.winner()
        if winner == self.ai_player:
            return 10 - depth
        elif winner == self.human_player:
            return depth - 10
        elif state.is_full():
            return 0

        if is_max:
            max_eval = float('-inf')
            for i, j in state.available_moves():
                state.make_move(i, j, self.ai_player)
                eval = self.minimax(state, depth + 1, False, alpha, beta)
                state.undo_move(i, j)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for i, j in state.available_moves():
                state.make_move(i, j, self.human_player)
                eval = self.minimax(state, depth + 1, True, alpha, beta)
                state.undo_move(i, j)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval


# --------- Game Manager and GUI -----------
class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe with Alpha-Beta Bot")

        self.state = State()
        self.bot_first = False  # Default
        self.ai = AlphaBetaAI('O')  # AI is 'O', human is 'X'
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        # Ask user to choose who plays first
        self.ask_first_player()

        # Create board
        for i in range(3):
            for j in range(3):
                btn = tk.Button(root, text='', font=('Arial', 36), width=5, height=2,
                                command=lambda i=i, j=j: self.user_move(i, j))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn

        if self.bot_first:
            self.bot_move()

    def ask_first_player(self):
        answer = messagebox.askyesno("Who goes first?", "Should the bot play first?")
        self.bot_first = answer
        if self.bot_first:
            self.ai = AlphaBetaAI('X')  # Bot is 'X', human is 'O'
        else:
            self.ai = AlphaBetaAI('O')  # Bot is 'O', human is 'X'

    def user_move(self, i, j):
        current_player = self.ai.human_player
        if self.state.board[i][j] == '' and self.state.winner() is None:
            self.state.make_move(i, j, current_player)
            self.update_gui()
            if self.check_game_over():
                return
            self.bot_move()

    def bot_move(self):
        ai_move = self.ai.best_move(self.state)
        if ai_move:
            self.state.make_move(ai_move[0], ai_move[1], self.ai.ai_player)
            self.update_gui()
            self.check_game_over()

    def update_gui(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j]['text'] = self.state.board[i][j]

    def check_game_over(self):
        winner = self.state.winner()
        if winner:
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.reset()
            return True
        elif self.state.is_full():
            messagebox.showinfo("Game Over", "It's a draw!")
            self.reset()
            return True
        return False

    def reset(self):
        self.state = State()
        for i in range(3):
            for j in range(3):
                self.buttons[i][j]['text'] = ''
        self.ask_first_player()
        if self.bot_first:
            self.bot_move()


# --------- Run the Game -----------
if __name__ == '__main__':
    root = tk.Tk()
    game = TicTacToeGUI(root)
    root.mainloop()
