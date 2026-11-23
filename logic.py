"""Game logic module for Python Eggs."""

import json
import random
from pathlib import Path


COLS = 28
ROWS = 20
EGGS_PER_LEVEL = 5


class SnakeLogic:
    """Store and process all snake game data without Tkinter."""

    def __init__(self):
        """FR2: Initialise the game and load saved data."""
        self.data_dir = Path(__file__).resolve().parent / "data"
        self.score_file = self.data_dir / "high_score.json"
        self.avatar_file = self.data_dir / "avatars.json"
        self.score = 0
        self.level = 1
        self.eggs = 0
        self.direction = "Right"
        self.pending = "Right"
        self.snake = []
        self.food = None
        self.obstacles = []
        self.avatar_index = 0
        self.avatars = self.load_avatars()
        self.high_score = self.load_score()
        self.reset()

    # FR7
    def load_avatars(self):
        """FR7: Read avatar choices from JSON; use safe defaults if missing."""
        try:
            with self.avatar_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list) and data:
                return data
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        return [
            {"name": "NASEEF SNAKE", "body": "#baf05b", "head": "#99be48"},
            {"name": "NASRIN SNAKE", "body": "#ff9fc5", "head": "#e878a6"},
            {"name": "NEERAJ SNAKE", "body": "#ffc857", "head": "#dc9c32"},
        ]

    # FR8
    def load_score(self):
        """FR8: Read a high score and handle missing or invalid files."""
        try:
            with self.score_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            value = data.get("high_score", 0)
            return int(value) if isinstance(value, int) else 0
        except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError, AttributeError):
            return 0

    # FR8
    def save_score(self):
        """FR8: Save the high score, without crashing if writing fails."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with self.score_file.open("w", encoding="utf-8") as file:
                json.dump({"high_score": self.high_score}, file)
        except OSError:
            pass

    # FR2
    def reset(self):
        """FR2: Reset one game with the snake in a safe centre position."""
        self.score = 0
        self.level = 1
        self.eggs = 0
        self.direction = "Right"
        self.pending = "Right"
        self.obstacles = []
        self.reset_snake()
        self.food = self.free_cell()

    def reset_snake(self):
        """FR6: Place three connected segments in the centre facing right."""
        y = ROWS // 2
        self.snake = [{"x": 8, "y": y}, {"x": 7, "y": y}, {"x": 6, "y": y}]
        self.direction = "Right"
        self.pending = "Right"

    # FR3
    def set_direction(self, text):
        """FR3: Reject reverse turns and validate the direction text."""
        allowed = {"Up", "Down", "Left", "Right"}
        opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if text in allowed and text != opposite.get(self.direction):
            self.pending = text
            return True
        return False

    # FR4
    def move(self):
        """FR4: Move, detect collisions, collect eggs, and level up."""
        self.direction = self.pending
        moves = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
        dx, dy = moves[self.direction]
        head = self.snake[0]
        new = {"x": head["x"] + dx, "y": head["y"] + dy}

        if not (0 <= new["x"] < COLS and 0 <= new["y"] < ROWS):
            return "Hit the wall"
        if new in self.snake:
            return "Hit yourself"
        if new in self.obstacles:
            return "Hit an obstacle"

        self.snake.insert(0, new)
        if new != self.food:
            self.snake.pop()
            return None

        self.score += 10
        self.eggs += 1
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_score()

        if self.eggs >= EGGS_PER_LEVEL:
            self.level += 1
            self.eggs = 0
            self.reset_snake()
            self.add_obstacles()
        self.food = self.free_cell()
        return None

    # FR5
    def add_obstacles(self):
        """FR5: Add rocks while keeping the safe starting area clear."""
        count = min(self.level - 1, 10)
        self.obstacles = []
        head = self.snake[0]
        while len(self.obstacles) < count:
            rock = self.free_cell()
            distance = abs(rock["x"] - head["x"]) + abs(rock["y"] - head["y"])
            if rock not in self.obstacles and distance >= 5:
                self.obstacles.append(rock)

    # FR2
    def free_cell(self):
        """FR2: Find a random square that is not occupied."""
        occupied = {(part["x"], part["y"]) for part in self.snake}
        occupied.update((rock["x"], rock["y"]) for rock in self.obstacles)
        if self.food is not None:
            occupied.add((self.food["x"], self.food["y"]))
        choices = [
            {"x": x, "y": y}
            for y in range(ROWS)
            for x in range(COLS)
            if (x, y) not in occupied
        ]
        return random.choice(choices) if choices else None
