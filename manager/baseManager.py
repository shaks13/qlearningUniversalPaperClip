import random
import json
import os
from collections import defaultdict
import numpy as np

class BaseQLearningManager:
    """Base class for Q-Learning managers with common functionality"""

    def __init__(self, button_manager, info_collector, learning_rate=0.1, discount_factor=0.9,
                 exploration_rate=1.0, min_exploration_rate=0.01, exploration_decay=0.995,
                 save_file='../data/q_table.json'):
        self.button_manager = button_manager
        self.info_collector = info_collector
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.min_exploration_rate = min_exploration_rate
        self.exploration_decay = exploration_decay
        self.save_file = save_file
        self.q_table = defaultdict(lambda: np.zeros(len(self.possible_actions)))
        self.load_q_table()

    def save_q_table(self):
        q_table_serializable = {k: v.tolist() for k, v in self.q_table.items()}
        with open(self.save_file, 'w') as f:
            json.dump(q_table_serializable, f)
        # print(f"Q-table saved to {self.save_file}")

    def load_q_table(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                q_table_serializable = json.load(f)
                self.q_table = defaultdict(lambda: np.zeros(len(self.possible_actions)),
                                           {k: np.array(v) for k, v in q_table_serializable.items()})
            print(f"Q-table loaded from {self.save_file}")
        else:
            print("No saved Q-table found, initializing a new one.")

    def decay_exploration(self):
        self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)

    def choose_action(self, state):
        if random.random() < self.exploration_rate:
            return random.choice(self.possible_actions)
        else:
            return self.possible_actions[np.argmax(self.q_table[state])]

    def update_q_table(self, state, action, reward, new_state):
        action_idx = self.action_to_index[action]
        best_next_action = np.argmax(self.q_table[new_state])
        td_target = reward + self.discount_factor * self.q_table[new_state][best_next_action]
        td_error = td_target - self.q_table[state][action_idx]
        self.q_table[state][action_idx] += self.learning_rate * td_error

    def visualize_strategies(self, top_n=10):
        sorted_states = sorted(self.q_table.keys(), key=lambda x: -len(self.q_table[x]))
        print(f"\n--- Learned Strategies (Top {min(top_n, len(sorted_states))}) ---")
        for i, state in enumerate(sorted_states[:top_n]):
            best_action_idx = np.argmax(self.q_table[state])
            best_action = self.possible_actions[best_action_idx]
            print(f"State {state} : Best action = {best_action} (Q={self.q_table[state][best_action_idx]:.2f})")
