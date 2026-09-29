# 🐍 AI-Powered Snake & Ladder

An intelligent Snake & Ladder game where the AI player uses a hybrid of **A\* Search**, **BFS**, **K-Means Clustering**, and **Logistic Regression** to make smart decisions — including when to use shields.

---

## 📁 Project Structure

```
AI Project/
├── main.py          # Entry point — initializes everything and launches the game
├── config.py        # All constants (board layout, AI weights, ML config, UI settings)
├── board.py         # Board represented as a directed graph
├── bfs.py           # BFS to find minimum rolls from any cell to cell 100
├── astar.py         # A* search for optimal path evaluation
├── ai_agent.py      # AI decision engine (A* + Logistic Regression hybrid)
├── ml_models.py     # K-Means clustering + Logistic Regression training
├── simulate.py      # Simulates random games to generate ML training data
├── game.py          # Core game logic (turns, dice, shields, win condition)
└── gui.py           # Pygame GUI (board rendering, heatmap, interaction)
```

---

## 🧠 How the AI Works

The AI combines multiple techniques in a pipeline:

### Step 1 — Board as a Graph (`board.py`)
The 10×10 board is modeled as a **directed graph**. Each cell has edges to up to 6 neighbors (dice values 1–6). Snake and ladder teleports are baked into the graph — so landing on a snake head automatically resolves to its tail.

### Step 2 — BFS for Shortest Path (`bfs.py`)
At startup, **Breadth-First Search** computes the minimum number of dice rolls to reach cell 100 from every cell (1–100). This lookup table is used by the AI agent for quick reference.

### Step 3 — Game Simulation (`simulate.py`)
**10,000 random games** are simulated between two players. Each cell visited in each game is recorded with board features and labeled as a win or loss. This data is used to train the ML models.

### Step 4 — ML Training (`ml_models.py`)
Two models are trained on the simulated data:

| Model | Purpose |
|---|---|
| **K-Means (3 clusters)** | Segments all 100 cells into `danger`, `neutral`, and `advantage` zones based on proximity to snakes/ladders |
| **Logistic Regression** | Predicts win probability (0–1) for each cell based on 5 board features |

Cell features used: position ratio, distance to nearest snake/ladder, number of snakes/ladders ahead.

### Step 5 — A\* Search (`astar.py`)
Given the AI's current position and a dice option, **A\*** evaluates the quality of the resulting move:
- **Heuristic:** `h(n) = (100 - n) / 6` (admissible — never overestimates)
- Penalizes landing near snakes, rewards landing near ladders
- Returns a cost score for each dice option

### Step 6 — AI Decision Making (`ai_agent.py`)
The AI is given **two dice options** each turn and picks the better one using:

```
Final Score = 0.6 × A* Score + 0.4 × Logistic Regression Win Probability
```

- **A\* Score** is normalized: `max(0, 1 - cost / 20)`
- **LR Score** is the predicted win probability for the destination cell
- If a move leads directly to cell 100, it's chosen immediately (score = 999)
- If a move exceeds cell 100, it's disqualified (score = -1)

### Shield Logic
The AI also decides **when to use a shield** (to block a snake) using K-Means zone info:
- Always use shield if snake drop > 30 cells
- Use shield if in a `danger` zone and drop > 15 cells

---

## 🎮 Game Rules

- **2 Players:** Human vs AI
- **Dice:** Each turn, 2 dice are rolled — the player chooses which value to use
- **Snakes (10):** Landing on a snake head sends you down to its tail
- **Ladders (9):** Landing on a ladder bottom sends you up to its top
- **Shields:** Each player starts with **2 shields** — use one to block a snake
- **Win:** First player to reach exactly **cell 100** wins (overshooting is blocked)

### Board Layout

**Snakes** (head → tail):

| 16→6 | 47→26 | 49→11 | 56→53 | 62→19 |
|------|-------|-------|-------|-------|
| 64→60 | 87→24 | 93→73 | 95→75 | 98→78 |

**Ladders** (bottom → top):

| 1→38 | 4→14 | 9→31 | 21→42 | 28→84 |
|------|------|------|-------|-------|
| 36→44 | 51→67 | 71→91 | 80→100 | |

---

## 🖥️ Controls

| Key | Action |
|---|---|
| `SPACE` | Roll dice |
| `1` | Choose dice option 1 |
| `2` | Choose dice option 2 |
| `Y` / `N` | Use / Skip shield (when snake is hit) |
| `H` | Toggle K-Means heatmap overlay |
| `R` | Restart (after game over) |

---

## 🗺️ GUI Features (`gui.py`)

- Pygame-rendered 10×10 board with snakes and ladders drawn
- **Heatmap overlay** showing K-Means risk zones:
  - 🔴 Red = Danger zone
  - 🟡 Yellow = Neutral zone
  - 🟢 Green = Advantage zone
- Stats panel showing current position, shields, and AI decision details
- AI turn plays automatically with a brief delay

---

## ⚙️ Configuration (`config.py`)

| Constant | Value | Description |
|---|---|---|
| `BOARD_SIZE` | 100 | Total cells |
| `SHIELDS_PER_PLAYER` | 2 | Shields each player starts with |
| `SIMULATION_COUNT` | 10,000 | Games simulated for ML training |
| `KMEANS_CLUSTERS` | 3 | Number of board zones |
| `WEIGHT_ASTAR` | 0.6 | A\* weight in scoring formula |
| `WEIGHT_LR` | 0.4 | Logistic Regression weight |

---

## 🚀 How to Run

### Requirements
```bash
pip install pygame numpy scikit-learn
```

### Run
```bash
python main.py
```

### Startup Sequence
```
[1/5] Building board graph...
[2/5] Running BFS (shortest paths)...
[3/5] Simulating 10,000 games...
[4/5] Training ML models (K-Means + Logistic Regression)...
[5/5] Launching game window...
```

---

## 👥 Team Contributions

| File | Contributor |
|---|---|
| `astar.py` , `game.py` | Samia |
| `gui.py`, `config.py` | Maruf |
| `ml_models.py`, `main.py`, `simulate.py` | Mahi |
| `ai_agent.py`, `bfs.py`, `board.py` | Rafi |

---

## 🏫 Project Info

**Course:** Artificial Intelligence Lab  
**Institution:** United International University (UIU)
