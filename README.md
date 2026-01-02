# 📎 Q-Learning Optimizer for Universal Paperclips

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Description

This project is a proof of concept (POC) of a reinforcement learning agent based on the **Q-Learning algorithm** to automatically play the web game [Universal Paperclips](https://www.decisionproblem.com/paperclips/index2.html).

The agent uses Selenium to interact with the game via a Chrome browser and progressively learns the best strategies to maximize paperclip production, manage resources, and optimize prices.

## 🎯 Features

### Three Intelligent Managers

1. **ProductionManager** 🏭
   - Decides when to manually make paperclips
   - Manages AutoClipper purchases
   - Manages MegaClipper purchases
   - Optimizes production rate

2. **ResourceManager** 📦
   - Manages wire purchases
   - Maintains optimal balance between available funds and wire stock
   - Avoids resource shortages

3. **PriceManager** 💰
   - Dynamically adjusts paperclip prices
   - Balances demand and unsold inventory
   - Maximizes revenue

### Reinforcement Learning

- **Q-Learning algorithm** with exploration/exploitation
- **Save and load** Q-tables in JSON format
- **Exploration decay** to converge towards an optimal strategy
- **Custom rewards** for each manager

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- Chrome or Chromium installed
- ChromeDriver compatible with your Chrome version

### Dependencies

Install the required Python packages:

```bash
pip install selenium numpy
```

Or create a `requirements.txt` file:

```txt
selenium>=4.0.0
numpy>=1.21.0
```

Then install with:

```bash
pip install -r requirements.txt
```

### ChromeDriver Configuration

Ensure ChromeDriver is in your PATH or specify its path in the code.

## 📖 Usage

### Quick Start

Run the main script to start optimization:

```bash
python qLearningOptimiser.py
```

### Testing Individual Components

#### Test the button manager

```bash
python buttonManager.py
```

#### Test the information collector

```bash
python infoCollector.py
```

### Learning Parameters

You can adjust Q-Learning hyperparameters during initialization:

```python
production_manager = ProductionManager(
    button_manager, 
    info_collector,
    learning_rate=0.1,          # Learning rate
    discount_factor=0.9,         # Discount factor
    exploration_rate=1.0,        # Initial exploration rate
    min_exploration_rate=0.01,   # Minimum exploration rate
    exploration_decay=0.995      # Exploration decay
)
```

## 📁 Project Structure

```
.
├── buttonManager.py              # Manages button clicks in the game
├── infoCollector.py              # Collects game information
├── qLearningOptimiser.py         # Main Q-Learning agent
├── data/
│   ├── q_table_production.json   # Q-table for production
│   ├── q_table_resources.json    # Q-table for resources
│   └── q_table_prices.json       # Q-table for prices
└── README.md                     # Documentation
```

## 🧠 How It Works

### 1. Information Collection

The `PaperclipsInfoCollector` extracts game data via Selenium:
- Number of paperclips produced
- Available funds
- Wire stock
- Price and demand
- Number of AutoClippers and MegaClippers
- etc.

### 2. State Discretization

Each manager transforms continuous values into discrete states:

```python
# Example for ProductionManager
clips_state = min(clips // 100, 50)
autoclippers_state = min(autoclippers // 10, 20)
```

### 3. Action Selection

The agent chooses an action using an ε-greedy strategy:
- **Exploration**: random action (probability ε)
- **Exploitation**: best action according to Q-table (probability 1-ε)

### 4. Reward Calculation

Each manager defines its own reward function:

**ProductionManager**:
- Reward for increased production
- Penalty for lack of funds when making a purchase

**ResourceManager**:
- Reward for maintaining good stock levels
- Penalty for wire shortage or excess

**PriceManager**:
- Reward for increased revenue
- Penalty for high unsold inventory

### 5. Q-Table Update

Q-Learning formula:

```
Q(s,a) ← Q(s,a) + α[r + γ·max(Q(s',a')) - Q(s,a)]
```

Where:
- `α` = learning rate
- `γ` = discount factor
- `r` = reward
- `s` = current state
- `s'` = new state
- `a` = chosen action

## 📊 Results

Q-tables are automatically saved in the `data/` folder:
- `q_table_production.json`: learned production strategies
- `q_table_resources.json`: learned resource management strategies
- `q_table_prices.json`: learned pricing strategies

The agent progressively improves its performance over episodes.

## 🛠️ Possible Improvements

- [ ] Implement more advanced algorithms (DQN, A3C)
- [ ] Add a graphical interface to visualize learning
- [ ] Handle advanced game phases (projects, quantum computing)
- [ ] Implement a multi-agent system
- [ ] Optimize hyperparameters with grid search
- [ ] Add performance metrics (graphs, logs)

## ⚠️ Limitations

- The agent currently only handles the early phases of the game
- Requires an internet connection to access the web game
- Performance heavily depends on chosen hyperparameters
- Learning time can be lengthy

## 📚 Resources

- [Universal Paperclips](https://www.decisionproblem.com/paperclips/index2.html)
- [Q-Learning Tutorial](https://en.wikipedia.org/wiki/Q-learning)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book.html)

---

