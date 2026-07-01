"""
CodeAlpha Python Internship - Task 1 (Advanced): Hangman Game (GUI Edition)
-------------------------------------------------------------------------------
A proper desktop Hangman game built with Tkinter.

Features:
- Visual hangman drawing on a canvas (builds stage by stage as you get wrong guesses)
- Word categories (Programming, Animals, Countries, Movies)
- Difficulty levels (Easy / Medium / Hard) that control word length & guess count
- On-screen clickable keyboard (plus real keyboard typing works too)
- Score tracking across rounds (wins/losses) shown in the window
- "New Game" and "Change Category/Difficulty" options
- Win/lose messages with the correct word revealed

Concepts used: OOP (classes), Tkinter GUI, Canvas drawing, event handling,
               dictionaries, random, functions, state management
"""

import tkinter as tk
from tkinter import messagebox
import random

# ----------------------------------------------------------------------------
# 1. GAME DATA: words organized by category and difficulty
# ----------------------------------------------------------------------------
WORD_BANK = {
    "Programming": {
        "Easy": ["python", "code", "loop", "array", "class"],
        "Medium": ["function", "variable", "algorithm", "compiler", "debugging"],
        "Hard": ["polymorphism", "encapsulation", "recursion", "asynchronous", "inheritance"],
    },
    "Animals": {
        "Easy": ["cat", "dog", "lion", "bird", "fish"],
        "Medium": ["elephant", "kangaroo", "dolphin", "penguin", "giraffe"],
        "Hard": ["rhinoceros", "chimpanzee", "hippopotamus", "salamander", "porcupine"],
    },
    "Countries": {
        "Easy": ["india", "chile", "japan", "spain", "egypt"],
        "Medium": ["pakistan", "germany", "portugal", "thailand", "argentina"],
        "Hard": ["kazakhstan", "mozambique", "liechtenstein", "azerbaijan", "kyrgyzstan"],
    },
    "Movies": {
        "Easy": ["up", "cars", "coco", "jaws", "root"],
        "Medium": ["avatar", "titanic", "inception", "gladiator", "interstellar"],
        "Hard": ["schindlerslist", "casablanca", "thegodfather", "pulpfiction", "goodfellas"],
    },
}

# Max wrong guesses allowed per difficulty (harder = fewer chances)
MAX_GUESSES = {
    "Easy": 8,
    "Medium": 6,
    "Hard": 5,
}

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


class HangmanGame:
    """Handles the core game logic - separate from the GUI code."""

    def __init__(self, category, difficulty):
        self.category = category
        self.difficulty = difficulty
        self.max_wrong = MAX_GUESSES[difficulty]
        self.word = random.choice(WORD_BANK[category][difficulty]).lower()
        self.guessed_letters = set()
        self.wrong_guesses = 0

    def guess(self, letter):
        """Process a single letter guess. Returns True if correct, False if wrong."""
        letter = letter.lower()
        if letter in self.guessed_letters:
            return None  # already guessed, ignore
        self.guessed_letters.add(letter)
        if letter in self.word:
            return True
        else:
            self.wrong_guesses += 1
            return False

    def is_won(self):
        return all(letter in self.guessed_letters for letter in self.word)

    def is_lost(self):
        return self.wrong_guesses >= self.max_wrong

    def display_word(self):
        return " ".join(letter if letter in self.guessed_letters else "_" for letter in self.word)


class HangmanApp:
    """Handles all the GUI: drawing, buttons, layout, and connecting to HangmanGame."""

    def __init__(self, root):
        self.root = root
        self.root.title("Hangman Game")
        self.root.geometry("650x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#f4f1de")

        # Score tracking persists across rounds within a session
        self.wins = 0
        self.losses = 0

        self.category = "Programming"
        self.difficulty = "Medium"
        self.game = None

        self.letter_buttons = {}

        self._build_top_bar()
        self._build_canvas()
        self._build_word_display()
        self._build_keyboard()
        self._build_bottom_bar()

        self.new_game()

        # Allow physical keyboard input too
        self.root.bind("<Key>", self._on_key_press)

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------
    def _build_top_bar(self):
        top = tk.Frame(self.root, bg="#f4f1de")
        top.pack(pady=8)

        self.category_var = tk.StringVar(value=self.category)
        self.difficulty_var = tk.StringVar(value=self.difficulty)

        tk.Label(top, text="Category:", bg="#f4f1de", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        category_menu = tk.OptionMenu(top, self.category_var, *WORD_BANK.keys(), command=self._on_settings_change)
        category_menu.grid(row=0, column=1, padx=5)

        tk.Label(top, text="Difficulty:", bg="#f4f1de", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
        difficulty_menu = tk.OptionMenu(top, self.difficulty_var, *MAX_GUESSES.keys(), command=self._on_settings_change)
        difficulty_menu.grid(row=0, column=3, padx=5)

        self.score_label = tk.Label(top, text="Wins: 0   Losses: 0", bg="#f4f1de", font=("Arial", 10, "bold"))
        self.score_label.grid(row=0, column=4, padx=15)

    def _build_canvas(self):
        self.canvas = tk.Canvas(self.root, width=300, height=250, bg="white", highlightthickness=1,
                                 highlightbackground="#333")
        self.canvas.pack(pady=10)
        # Draw the static gallows once
        self.canvas.create_line(20, 230, 150, 230, width=4)   # base
        self.canvas.create_line(50, 230, 50, 20, width=4)     # pole
        self.canvas.create_line(50, 20, 180, 20, width=4)     # top beam
        self.canvas.create_line(180, 20, 180, 50, width=4)    # rope

    def _build_word_display(self):
        self.word_label = tk.Label(self.root, text="", font=("Courier New", 24, "bold"), bg="#f4f1de")
        self.word_label.pack(pady=5)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12), bg="#f4f1de", fg="#333")
        self.status_label.pack(pady=2)

    def _build_keyboard(self):
        keyboard_frame = tk.Frame(self.root, bg="#f4f1de")
        keyboard_frame.pack(pady=10)

        row, col = 0, 0
        for letter in ALPHABET:
            btn = tk.Button(
                keyboard_frame, text=letter.upper(), width=3, height=1,
                font=("Arial", 10, "bold"),
                command=lambda l=letter: self._handle_guess(l)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.letter_buttons[letter] = btn
            col += 1
            if col > 8:
                col = 0
                row += 1

    def _build_bottom_bar(self):
        bottom = tk.Frame(self.root, bg="#f4f1de")
        bottom.pack(pady=10)

        tk.Button(bottom, text="New Game", command=self.new_game,
                  bg="#81b29a", font=("Arial", 11, "bold"), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom, text="Quit", command=self.root.quit,
                  bg="#e07a5f", font=("Arial", 11, "bold"), width=12).pack(side=tk.LEFT, padx=5)

    # ------------------------------------------------------------------
    # GAME FLOW
    # ------------------------------------------------------------------
    def _on_settings_change(self, _=None):
        self.category = self.category_var.get()
        self.difficulty = self.difficulty_var.get()
        self.new_game()

    def new_game(self):
        self.category = self.category_var.get() if hasattr(self, "category_var") else self.category
        self.difficulty = self.difficulty_var.get() if hasattr(self, "difficulty_var") else self.difficulty

        self.game = HangmanGame(self.category, self.difficulty)

        # Reset the drawing (clear hangman body parts, keep gallows)
        self.canvas.delete("body_part")

        # Reset keyboard buttons
        for letter, btn in self.letter_buttons.items():
            btn.config(state=tk.NORMAL, bg="SystemButtonFace")

        self.status_label.config(text=f"Category: {self.category} | Difficulty: {self.difficulty} | "
                                       f"Guesses left: {self.game.max_wrong}")
        self._update_word_display()

    def _handle_guess(self, letter):
        if self.game is None or self.game.is_won() or self.game.is_lost():
            return

        result = self.game.guess(letter)
        if result is None:
            return  # already guessed

        # Disable the clicked button and color it
        btn = self.letter_buttons.get(letter)
        if btn:
            btn.config(state=tk.DISABLED, bg="#a8dadc" if result else "#f28482")

        if not result:
            self._draw_next_body_part(self.game.wrong_guesses)

        self._update_word_display()

        if self.game.is_won():
            self.wins += 1
            self._update_score()
            messagebox.showinfo("You Won! 🎉", f"Great job! The word was '{self.game.word}'.")
        elif self.game.is_lost():
            self.losses += 1
            self._update_score()
            messagebox.showinfo("Game Over 💀", f"Out of guesses! The word was '{self.game.word}'.")

    def _on_key_press(self, event):
        letter = event.char.lower()
        if letter in ALPHABET:
            self._handle_guess(letter)

    def _update_word_display(self):
        self.word_label.config(text=self.game.display_word().upper())
        remaining = self.game.max_wrong - self.game.wrong_guesses
        self.status_label.config(
            text=f"Category: {self.category} | Difficulty: {self.difficulty} | Guesses left: {remaining}"
        )

    def _update_score(self):
        self.score_label.config(text=f"Wins: {self.wins}   Losses: {self.losses}")

    # ------------------------------------------------------------------
    # DRAWING THE HANGMAN (called once per wrong guess)
    # ------------------------------------------------------------------
    def _draw_next_body_part(self, wrong_count):
        """
        Draws one more part of the hangman figure based on how many
        wrong guesses have happened so far. Supports up to 8 stages
        so it works cleanly even on Easy mode (8 max guesses).
        """
        x, y = 180, 50  # rope end point, where the head will hang

        parts = {
            1: lambda: self.canvas.create_oval(x - 15, y, x + 15, y + 30, width=3, tags="body_part"),          # head
            2: lambda: self.canvas.create_line(x, y + 30, x, y + 80, width=3, tags="body_part"),                # torso
            3: lambda: self.canvas.create_line(x, y + 40, x - 25, y + 60, width=3, tags="body_part"),           # left arm
            4: lambda: self.canvas.create_line(x, y + 40, x + 25, y + 60, width=3, tags="body_part"),           # right arm
            5: lambda: self.canvas.create_line(x, y + 80, x - 20, y + 120, width=3, tags="body_part"),          # left leg
            6: lambda: self.canvas.create_line(x, y + 80, x + 20, y + 120, width=3, tags="body_part"),          # right leg
            7: lambda: self.canvas.create_line(x - 15, y + 10, x - 5, y + 10, width=2, tags="body_part"),       # left eye (X)
            8: lambda: self.canvas.create_line(x + 5, y + 10, x + 15, y + 10, width=2, tags="body_part"),       # right eye (X)
        }

        draw_fn = parts.get(wrong_count)
        if draw_fn:
            draw_fn()


def main():
    root = tk.Tk()
    app = HangmanApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()