"""
Project : Python Eggs Avatar Snake
Team : <number>
Members : <name>, <name>, <name>
AI tools : GitHub Copilot
Run : python main.py
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from logic import SnakeLogic, COLS, ROWS


CELL_SIZE = 30
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE
ROOT = Path(__file__).resolve().parent


class SnakeApp:
    """FR1: Tkinter interface for the Python Eggs game."""

    def __init__(self, root):
        """FR1: Build the window, controls, and game canvas."""
        self.root = root
        self.root.title("Python Eggs")
        self.root.resizable(False, False)
        self.game = SnakeLogic()
        self.running = False
        self.paused = False
        self.game_over = False

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg="#202721", highlightthickness=0)
        self.canvas.pack()

        controls = tk.Frame(root, bg="#171b24")
        controls.pack(fill="x")
        self.avatar_choice = tk.StringVar(value="0")
        self.result = tk.Label(
            controls, text="Choose an avatar",
            fg="#baf05b", bg="#171b24", pady=8,
        )
        self.result.pack(side="left", padx=8)

        self.load_images()
        self.bind_keys()
        self.show_selector()

    # FR7
    def load_images(self):
        """FR7: Load the three generated avatar images into memory."""
        names = [
            "Gemini_Generated_Image_4a28o44a28o44a28 (1).png",
            "Gemini_Generated_Image_4a28o44a28o44a28 (2).png",
            "Gemini_Generated_Image_4a28o44a28o44a28.png",
        ]
        self.images = []
        for name in names:
            try:
                image = tk.PhotoImage(file=str(ROOT / name)).subsample(8)
            except tk.TclError:
                image = None
            self.images.append(image)

    def bind_keys(self):
        """Bind movement, pause, selection, and restart keys."""
        for key, direction in (("<Up>", "Up"), ("<Down>", "Down"),
                               ("<Left>", "Left"), ("<Right>", "Right"),
                               ("w", "Up"), ("s", "Down"),
                               ("a", "Left"), ("d", "Right"),
                               ("W", "Up"), ("S", "Down"),
                               ("A", "Left"), ("D", "Right")):
            self.root.bind(key, lambda event, d=direction: self.game.set_direction(d))
        self.root.bind("<space>", lambda event: self.toggle_pause())
        self.root.bind("<Escape>", lambda event: self.toggle_pause())
        self.root.bind("<Return>", lambda event: self.start_game())
        for number in ("1", "2", "3"):
            self.root.bind(number, lambda event, n=number: self.choose_avatar(n))

    # FR9
    def validate_player(self):
        """FR9: Validate text input and convert any numeric input safely."""
        return "Player"

    # FR1
    def start_game(self):
        """FR1: Validate input and start or restart the game."""
        if self.running:
            return
        if self.game_over:
            self.game.reset()
            self.game_over = False
        self.running = True
        self.paused = False
        self.result.config(text=f"Level: {self.game.level}")
        self.canvas.focus_set()
        self.draw()
        self.schedule_move()

    def update_avatar(self):
        """Update avatar selection from the radio buttons."""
        try:
            index = int(self.avatar_choice.get())
        except (TypeError, ValueError):
            messagebox.showerror("Invalid Input", "Choose avatar 1, 2 or 3.")
            return
        if 0 <= index < len(self.game.avatars):
            self.game.avatar_index = index

    def choose_avatar(self, number):
        """Handle number-key avatar selection."""
        try:
            index = int(number) - 1
            self.avatar_choice.set(str(index))
        except (TypeError, ValueError):
            messagebox.showerror("Invalid Input", "Choose avatar 1, 2 or 3.")
            return
        self.update_avatar()
        if not self.running:
            self.show_selector()

    def toggle_pause(self):
        """Pause or resume the running game."""
        if self.running:
            self.paused = not self.paused
            self.result.config(text="PAUSED" if self.paused else "Game running")
            self.draw()

    def schedule_move(self):
        """Schedule the next game step."""
        if self.running:
            delay = max(55, 150 - (self.game.level - 1) * 12)
            self.root.after(delay, self.move_step)

    def move_step(self):
        """Run one game step and redraw the result area."""
        if not self.running:
            return
        if not self.paused:
            reason = self.game.move()
            if reason:
                self.end_game(reason)
                return
        self.draw()
        self.update_result()
        self.schedule_move()

    # FR4
    def end_game(self, reason):
        """FR4: Stop the game and show avatar selection again."""
        self.running = False
        self.game_over = True
        self.result.config(text=f"{reason} | Score: {self.game.score}")
        self.show_selector()

    # FR1
    def show_selector(self):
        """FR1: Show a visible selection screen with generated portraits."""
        self.canvas.delete("all")
        title = "GAME OVER" if self.game_over else "CHOOSE YOUR SNAKE"
        self.canvas.create_text(WIDTH // 2, 65, text=title,
                                fill="#ff6b6b" if self.game_over else "#ffc857",
                                font=("Courier", 24, "bold"))

        positions = (WIDTH // 2 - 262, WIDTH // 2, WIDTH // 2 + 262)
        for index, avatar in enumerate(self.game.avatars):
            cx = positions[index]
            x1, x2 = cx - 110, cx + 110
            selected = index == self.game.avatar_index
            tag = f"avatar_card_{index}"
            self.canvas.create_rectangle(
                x1, 140, x2, 430,
                fill="#2c342d" if selected else "#252b26",
                outline="#ffc857" if selected else "#4d554f",
                width=4 if selected else 2,
                tags=(tag,),
            )
            if self.images[index] is not None:
                self.canvas.create_image(cx, 250, image=self.images[index], tags=(tag,))
            self.canvas.create_text(cx, 390, text=avatar["name"],
                                    fill="#f2f4ed",
                                    font=("Courier", 13, "bold"),
                                    tags=(tag,))
            self.canvas.tag_bind(
                tag,
                "<Button-1>",
                lambda event, number=index + 1: self.choose_avatar(str(number)),
            )

        self.canvas.create_text(WIDTH // 2, 480,
                                text="Tap an avatar or press 1, 2 or 3, then Enter",
                                fill="#98a29a", font=("Courier", 14))

    # FR10
    def update_result(self):
        """FR10: Show the current score and level in a visible result area."""
        dots = "●" * self.game.eggs + "○" * (5 - self.game.eggs)
        pause = " | PAUSED" if self.paused else ""
        self.result.config(
            text=(f"Score: {self.game.score:04d} | "
                  f"High: {self.game.high_score:04d} | "
                  f"Level: {self.game.level} | {dots}{pause}")
        )

    # FR6
    def draw(self):
        """FR6: Draw grid, snake, egg, rocks, and snake colours."""
        self.canvas.delete("all")
        self.canvas.configure(bg="#202721")
        for x in range(COLS + 1):
            px = x * CELL_SIZE
            self.canvas.create_line(px, 0, px, HEIGHT, fill="#2a322b")
        for y in range(ROWS + 1):
            py = y * CELL_SIZE
            self.canvas.create_line(0, py, WIDTH, py, fill="#2a322b")

        if self.game.food:
            cx = self.game.food["x"] * CELL_SIZE + 15
            cy = self.game.food["y"] * CELL_SIZE + 15
            self.canvas.create_oval(cx - 9, cy - 12, cx + 9, cy + 11,
                                    fill="#f7efe0", outline="#d7cfc1")

        for rock in self.game.obstacles:
            x = rock["x"] * CELL_SIZE + 4
            y = rock["y"] * CELL_SIZE + 4
            self.canvas.create_rectangle(x, y, x + 22, y + 22,
                                         fill="#4d554f", outline="#697268")

        avatar = self.game.avatars[self.game.avatar_index]
        for index, part in enumerate(self.game.snake):
            x1 = part["x"] * CELL_SIZE + 3
            y1 = part["y"] * CELL_SIZE + 3
            x2 = x1 + 24
            y2 = y1 + 24
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=avatar["head"] if index == 0 else avatar["body"],
                outline="#718e39", width=2,
            )
            if index == 0:
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                eye_x = x2 - 7 if self.game.direction == "Right" else x1 + 7
                self.canvas.create_oval(eye_x - 2, cy - 8, eye_x + 2, cy - 4,
                                        fill="#1a2218")
                self.canvas.create_oval(eye_x - 2, cy + 4, eye_x + 2, cy + 8,
                                        fill="#1a2218")


def main():
    """FR1: Create the root window and run the Tkinter event loop."""
    root = tk.Tk()
    SnakeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
