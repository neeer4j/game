import random
import tkinter as tk
from pathlib import Path


COLS = 28
ROWS = 20
CELL_SIZE = 30
EGGS_PER_LEVEL = 5
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE
HIGH_SCORE_FILE = Path(__file__).resolve().parent / "high_score.txt"

AVATARS = (
    {
        "name": "NASEEF SNAKE",
        "body": "#baf05b",
        "head": "#99be48",
        "outline": "#718e39",
        "image": "Gemini_Generated_Image_4a28o44a28o44a28 (1).png",
    },
    {
        "name": "NASRIN SNAKE",
        "body": "#ff9fc5",
        "head": "#e878a6",
        "outline": "#b44f7b",
        "image": "Gemini_Generated_Image_4a28o44a28o44a28 (2).png",
    },
    {
        "name": "NEERAJ SNAKE",
        "body": "#ffc857",
        "head": "#dc9c32",
        "outline": "#9d7024",
        "image": "Gemini_Generated_Image_4a28o44a28o44a28.png",
    },
)


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Eggs")
        self.root.resizable(False, False)

        self.score = 0
        self.level = 1
        self.eggs_collected = 0
        self.running = False
        self.paused = False
        self.direction = "Right"
        self.pending_direction = "Right"
        self.snake = []
        self.food = None
        self.obstacles = []
        self.avatar_index = 0
        self.selection_active = False
        self._game_over = False
        self.high_score = self.load_high_score()

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg="#202721",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.status_frame = tk.Frame(root, bg="#171b24")
        self.status_frame.pack(fill="x")
        self.status_label = tk.Label(
            self.status_frame,
            text="",
            fg="#f2f4ed",
            bg="#171b24",
            font=("Courier", 14, "bold"),
            pady=10,
        )
        self.status_label.pack()

        self.avatar_images = [
            tk.PhotoImage(file=str(HIGH_SCORE_FILE.parent / data["image"])).subsample(8)
            for data in AVATARS
        ]

        self.root.bind("<Up>", lambda event: self.set_direction("Up"))
        self.root.bind("<Down>", lambda event: self.set_direction("Down"))
        self.root.bind("<Left>", lambda event: self.set_direction("Left"))
        self.root.bind("<Right>", lambda event: self.set_direction("Right"))
        self.root.bind("<w>", lambda event: self.set_direction("Up"))
        self.root.bind("<s>", lambda event: self.set_direction("Down"))
        self.root.bind("<a>", lambda event: self.set_direction("Left"))
        self.root.bind("<d>", lambda event: self.set_direction("Right"))
        self.root.bind("1", lambda event: self.choose_avatar(0))
        self.root.bind("2", lambda event: self.choose_avatar(1))
        self.root.bind("3", lambda event: self.choose_avatar(2))
        self.root.bind("<space>", lambda event: self.toggle_pause())
        self.root.bind("<Escape>", lambda event: self.toggle_pause())
        self.root.bind("<Return>", lambda event: self.start_or_restart())

        self.reset_game()
        self.show_avatar_selector("CHOOSE YOUR SNAKE")

    def load_high_score(self):
        try:
            return int(HIGH_SCORE_FILE.read_text(encoding="utf-8").strip())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        HIGH_SCORE_FILE.write_text(str(self.high_score), encoding="utf-8")

    def reset_snake(self):
        center_y = ROWS // 2
        self.snake = [
            {"x": 8, "y": center_y},
            {"x": 7, "y": center_y},
            {"x": 6, "y": center_y},
        ]
        self.direction = "Right"
        self.pending_direction = "Right"

    def reset_game(self):
        self.score = 0
        self.level = 1
        self.eggs_collected = 0
        self.obstacles = []
        self.reset_snake()
        self.food = self.find_free_cell()
        self.update_status()

    def start_or_restart(self):
        if self.running:
            return
        if self.selection_active:
            if self._game_over:
                self.reset_game()
                self._game_over = False
            self.selection_active = False
            self.running = True
            self.paused = False
            self.canvas.focus_set()
            self.update_status()
            self.draw()
            self.schedule_move()

    def choose_avatar(self, index):
        if self.selection_active:
            self.avatar_index = index
            title = "GAME OVER" if self._game_over else "CHOOSE YOUR SNAKE"
            self.show_avatar_selector(title)

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        self.update_status()
        self.draw()

    def set_direction(self, new_direction):
        opposites = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left",
        }
        if new_direction != opposites.get(self.direction):
            self.pending_direction = new_direction

    def schedule_move(self):
        if self.running:
            delay = max(55, 150 - (self.level - 1) * 12)
            self.root.after(delay, self.game_step)

    def game_step(self):
        if not self.running:
            return
        if not self.paused:
            self.move()
        if self.running:
            self.draw()
            self.schedule_move()

    def move(self):
        self.direction = self.pending_direction
        head = self.snake[0]
        movement = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0),
        }
        dx, dy = movement[self.direction]
        new_head = {"x": head["x"] + dx, "y": head["y"] + dy}

        if (
            new_head["x"] < 0
            or new_head["x"] >= COLS
            or new_head["y"] < 0
            or new_head["y"] >= ROWS
        ):
            self.end_game("Hit the wall")
            return
        if new_head in self.snake:
            self.end_game("Hit yourself")
            return
        if new_head in self.obstacles:
            self.end_game("Hit an obstacle")
            return

        self.snake.insert(0, new_head)

        if new_head != self.food:
            self.snake.pop()
            return

        self.score += 10
        self.eggs_collected += 1

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

        if self.eggs_collected >= EGGS_PER_LEVEL:
            self.level += 1
            self.eggs_collected = 0
            self.reset_snake()
            self.add_obstacles()
            self.food = self.find_free_cell()

        else:
            self.food = self.find_free_cell()

        self.update_status()

    def add_obstacles(self):
        rock_count = min(self.level - 1, 10)
        self.obstacles = []
        head = self.snake[0]
        while len(self.obstacles) < rock_count:
            rock = self.find_free_cell()
            distance = abs(rock["x"] - head["x"]) + abs(rock["y"] - head["y"])
            if rock not in self.obstacles and distance >= 5:
                self.obstacles.append(rock)

    def find_free_cell(self):
        occupied = {
            (segment["x"], segment["y"])
            for segment in self.snake
        }
        occupied.update((rock["x"], rock["y"]) for rock in self.obstacles)
        if self.food is not None:
            occupied.add((self.food["x"], self.food["y"]))

        available = [
            {"x": x, "y": y}
            for y in range(ROWS)
            for x in range(COLS)
            if (x, y) not in occupied
        ]
        return random.choice(available)

    def end_game(self, reason):
        self.running = False
        self._game_over = True
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        self.update_status()
        self.show_avatar_selector("GAME OVER", reason)

    def show_avatar_selector(self, title, reason=""):
        self.selection_active = True
        self.running = False
        self.draw()

        avatar = AVATARS[self.avatar_index]
        self.canvas.create_rectangle(35, 30, WIDTH - 35, 78, fill="#171b24", outline="#171b24")
        self.canvas.create_text(
            WIDTH // 2,
            54,
            text=title,
            fill="#ff6b6b" if title == "GAME OVER" else "#ffc857",
            font=("Courier", 24, "bold"),
        )

        card_width = 238
        card_height = 260
        card_y1 = 150
        card_y2 = card_y1 + card_height
        centers = (
            WIDTH // 2 - card_width - 24,
            WIDTH // 2,
            WIDTH // 2 + card_width + 24,
        )

        for index, data in enumerate(AVATARS):
            x1 = centers[index] - card_width // 2
            x2 = x1 + card_width
            selected = index == self.avatar_index
            tag = f"avatar_{index}"

            self.canvas.create_rectangle(
                x1,
                card_y1,
                x2,
                card_y2,
                fill="#2c342d" if selected else "#252b26",
                outline="#ffc857" if selected else "#4d554f",
                width=4 if selected else 2,
                tags=(tag,),
            )
            cx = (x1 + x2) // 2
            self.canvas.create_image(
                cx,
                card_y1 + 108,
                image=self.avatar_images[index],
                tags=(tag,),
            )
            self.canvas.create_text(
                cx,
                card_y1 + 205,
                text=data["name"],
                fill="#f2f4ed",
                font=("Courier", 13, "bold"),
                tags=(tag,),
            )
            self.canvas.tag_bind(tag, "<Button-1>", lambda event, i=index: self.choose_avatar(i))

        self.canvas.create_text(
            WIDTH // 2,
            470,
            text="Choose with 1, 2, 3 or click a card",
            fill="#98a29a",
            font=("Courier", 14),
        )

        if reason:
            summary = f"{reason}  |  Score: {self.score}"
        else:
            summary = f"Selected: {avatar['name']}"
        self.canvas.create_text(
            WIDTH // 2,
            510,
            text=f"{summary}  |  Press Enter to start",
            fill="#baf05b",
            font=("Courier", 16, "bold"),
        )

    def update_status(self):
        progress = "●" * self.eggs_collected + "○" * (EGGS_PER_LEVEL - self.eggs_collected)
        pause_text = "  |  PAUSED" if self.paused else ""
        avatar_name = AVATARS[self.avatar_index]["name"]
        self.status_label.config(
            text=(
                f"Score: {self.score:04d}   "
                f"High: {self.high_score:04d}   "
                f"Level: {self.level}   "
                f"{progress}   {avatar_name}{pause_text}"
            )
        )

    def draw(self):
        self.canvas.delete("all")
        self.canvas.configure(bg="#202721")

        for x in range(COLS + 1):
            px = x * CELL_SIZE
            self.canvas.create_line(px, 0, px, HEIGHT, fill="#2a322b")
        for y in range(ROWS + 1):
            py = y * CELL_SIZE
            self.canvas.create_line(0, py, WIDTH, py, fill="#2a322b")

        if self.food is not None:
            cx = self.food["x"] * CELL_SIZE + CELL_SIZE // 2
            cy = self.food["y"] * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_oval(cx - 9, cy - 12, cx + 9, cy + 11, fill="#f7efe0", outline="#d7cfc1")
            self.canvas.create_oval(cx - 5, cy - 8, cx - 1, cy - 4, fill="#ffffff", outline="")

        for rock in self.obstacles:
            x1 = rock["x"] * CELL_SIZE + 4
            y1 = rock["y"] * CELL_SIZE + 4
            x2 = x1 + CELL_SIZE - 8
            y2 = y1 + CELL_SIZE - 8
            self.canvas.create_polygon(
                x1 + 8, y1,
                x2 - 2, y1 + 3,
                x2, y1 + 15,
                x2 - 7, y2,
                x1 + 3, y2,
                x1, y1 + 13,
                fill="#4d554f",
                outline="#697268",
            )

        avatar = AVATARS[self.avatar_index]
        for index, segment in enumerate(self.snake):
            x1 = segment["x"] * CELL_SIZE + 3
            y1 = segment["y"] * CELL_SIZE + 3
            x2 = x1 + CELL_SIZE - 6
            y2 = y1 + CELL_SIZE - 6
            color = avatar["head"] if index == 0 else avatar["body"]

            self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=color,
                outline=avatar["outline"],
                width=2,
            )

            if index == 0:
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                if self.direction in ("Left", "Right"):
                    eye_x = x2 - 7 if self.direction == "Right" else x1 + 7
                    self.canvas.create_oval(eye_x - 2, cy - 8, eye_x + 2, cy - 4, fill="#1a2218")
                    self.canvas.create_oval(eye_x - 2, cy + 4, eye_x + 2, cy + 8, fill="#1a2218")
                else:
                    eye_y = y1 + 7 if self.direction == "Up" else y2 - 7
                    self.canvas.create_oval(cx - 8, eye_y - 2, cx - 4, eye_y + 2, fill="#1a2218")
                    self.canvas.create_oval(cx + 4, eye_y - 2, cx + 8, eye_y + 2, fill="#1a2218")


def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
