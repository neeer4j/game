# Python Eggs

A Python Tkinter Snake game.

## Run

```powershell
python main.py
```

No third-party packages are required.

The source is separated into:

- `main.py` for the Tkinter interface
- `logic.py` for the game class and processing
- `data/avatars.json` for avatar data
- `data/high_score.json` for saved high scores

## Controls

- Arrow keys or WASD: move
- Space or Escape: pause
- Enter: start or restart
- Click/tap an avatar card: choose that avatar
- 1, 2, or 3: choose a snake avatar

## Features

- Snake grows after eating an egg
- Wall and self-collision game over
- Five eggs per level
- Speed increases every level
- Rocks appear in later levels
- High score saved in `high_score.txt`
- Choose from Naseef, Nasrin, or Neeraj snake avatars
- Avatar selection appears before the first game and after game over
- The selected avatar continues through level changes
- Each new level starts the snake in a safe center position
