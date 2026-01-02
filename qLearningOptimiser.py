import numpy as np
import random
import time
import json
import os
from collections import defaultdict

class QLearningPaperclipsOptimizer:
    def __init__(self, button_manager, info_collector, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, min_exploration_rate=0.01, exploration_decay=0.995, save_file="data/q_table_paperclips.json"):
        self.clips_history = [0, 0]
        self.clips_maker_rate_history = []
        self.wire_state_history = 1000
        self.max_history = 10
        self.last_clips = 0
        self.production_reward_history = 0
        self.button_manager = button_manager
        self.info_collector = info_collector
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.min_exploration_rate = min_exploration_rate
        self.exploration_decay = exploration_decay
        self.save_file = save_file
        self.possible_actions = [
            "btnMakePaperclip",
            "btnMakeClipper",
            "btnMakeMegaClipper",
            "btnLowerPrice",
            "btnRaisePrice",
            "btnExpandMarketing",
            "btnBuyWire",
            "wait"
            # Add other button IDs here if needed
        ]
        self.action_to_index = {action: idx for idx, action in enumerate(self.possible_actions)}
        self.q_table = defaultdict(lambda: np.zeros(len(self.possible_actions)))
        self.load_q_table()  # Load Q-table if it exists

    def get_state(self):
        """Returns a discretized state based on the game phase."""
        clips = self.info_collector.get_clips_count()
        funds = self.info_collector.get_funds()
        unsold_clips = funds = self.info_collector.get_unsold_clips()
        wire = self.info_collector.get_wire_count()
        clip_maker_rate = self.info_collector.get_clip_maker_rate()
        operations = self.info_collector.get_operations()
        creativity = self.info_collector.get_creativity()

        funds_state = min((funds + unsold_clips / (clip_maker_rate + 1)) // 100, 10)  # Max 10 categories
        wire_state = min(wire / (clip_maker_rate + 1) // 100, 10)  # Max 10 categories
        operations_state = min(operations // 100, 10)  # Max 10 categories
        creativity_state = min(creativity // 100, 10)  # Max 10 categories

        # Phase 1: Early game (few paperclips)
        if clips < 1000:
            return f"early_{clips // 100}_funds_{funds_state}_wire_{wire_state}"
        # Phase 2: Mid game (automatic production)
        elif clips < 1_000_000:
            return f"mid_{clips // 10_000}_funds_{funds_state}_wire_{wire_state}_operations_{operations_state}_creativity_{creativity_state}"
        # Phase 3: Late game (cosmic expansion)
        else:
            return f"late_{clips // 1_000_000}_funds_{funds_state}_wire_{wire_state}_operations_{operations_state}_creativity_{creativity_state}"

    def choose_action(self, state):
        if random.random() < self.exploration_rate:
            return random.choice(self.possible_actions)
        else:
            return self.possible_actions[np.argmax(self.q_table[state])]

    def execute_action(self, action):
        """Executes an action (including waiting)."""
        if action == "wait":
            return True
        else:
            return self.button_manager.click_button_by_id(action)

    def decay_exploration(self):
        self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)

    def save_q_table(self):
        # Converts the Q-table to a serializable format
        q_table_serializable = {k: v.tolist() for k, v in self.q_table.items()}
        with open(self.save_file, 'w') as f:
            json.dump(q_table_serializable, f)
        print(f"Q-table saved to {self.save_file}")

    def load_q_table(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                q_table_serializable = json.load(f)
                self.q_table = defaultdict(lambda: np.zeros(len(self.possible_actions)), {k: np.array(v) for k, v in q_table_serializable.items()})
            print(f"Q-table loaded from {self.save_file}")
        else:
            print("No saved Q-table found, initializing a new one.")

    def update_q_table(self, state, action, reward, new_state):
        """Updates the Q-table with a long-term vision."""
        action_idx = self.action_to_index[action]
        best_next_action = np.argmax(self.q_table[new_state])
        td_target = reward + self.discount_factor * self.q_table[new_state][best_next_action]
        td_error = td_target - self.q_table[state][action_idx]
        self.q_table[state][action_idx] += self.learning_rate * td_error

    def get_reward(self):
        """Balanced reward: production, resources, funds, and trend."""
        # Data retrieval
        clips = self.info_collector.get_clips_count()
        wire = self.info_collector.get_wire_count()
        autoclippers = self.info_collector.get_autoclippers_count()
        megalippers_count = self.info_collector.get_megalippers_count()
        funds = self.info_collector.get_funds()
        unsold_clips = self.info_collector.get_unsold_clips()
        clip_maker_rate = self.info_collector.get_clip_maker_rate()
        wire_cost = self.info_collector.get_wire_cost()

        # Initialize rewards
        immediate_reward = 0
        production_reward = 0
        resource_reward = 0
        penalty = 0

        # Update histories
        self.clips_history.append(clips)
        self.clips_maker_rate_history.append(clip_maker_rate)
        if len(self.clips_history) > self.max_history:
            self.clips_history.pop(0)
            self.clips_maker_rate_history.pop(0)

        # Immediate reward (increase in clips)
        if len(self.clips_history) >= 2:
            immediate_reward = max(clips - self.clips_history[-2] - clip_maker_rate, 0)

        # Production reward (AutoClippers and MegaClippers)
        current_production = autoclippers + 10 * megalippers_count
        production_reward = current_production - self.production_reward_history
        self.production_reward_history = current_production

        # Resource reward/penalty
        # Penalties if funds are insufficient to buy Wire or AutoClippers
        wire_cost = wire_cost
        autoclipper_cost = 6
        if funds < wire_cost:
            penalty -= 5  # Strong penalty if funds are insufficient for Wire
        if funds < autoclipper_cost:
            penalty -= 3  # Penalty if funds are insufficient for AutoClipper

        # Penalties if Wire is too low
        if wire < 100:
            penalty -= 30
        elif wire < 500:
            penalty -= 10
        elif wire < 800:
            penalty -= 3

        # Reward if funds are sufficient to prepare for purchases
        if funds > 10 * wire_cost:  # Arbitrary threshold for "comfortable"
            resource_reward += 20
        if funds > 5 * autoclipper_cost:
            resource_reward += 10

        # Reward based on production trend
        trend_reward = 0
        if len(self.clips_maker_rate_history) >= 2:
            trend_reward = (self.clips_maker_rate_history[-1] - self.clips_maker_rate_history[0]) / len(
                self.clips_maker_rate_history)

        # Return total reward
        return immediate_reward + production_reward + resource_reward + penalty + trend_reward

    def run(self, episodes=1000, save_every=100, waiting_time=0.1):
        for i in range(episodes):
            state = self.get_state()  # Returns a string, e.g., "early_0"
            action = self.choose_action(state)
            success = self.execute_action(action)
            time.sleep(waiting_time)
            new_state = self.get_state()  # Returns a string, e.g., "early_1"
            reward = self.get_reward()
            self.update_q_table(state, action, reward, new_state)
            self.decay_exploration()
            print(f"Iteration {i + 1}/{episodes} | State: {state} | Action: {action} | Reward: {reward}")
            if (i + 1) % save_every == 0:
                self.save_q_table()
        self.save_q_table()

    def visualize_strategies(self, top_n=10):
        """Displays the best actions for the most frequent states."""
        # Sort states by number of occurrences in the Q-table
        sorted_states = sorted(self.q_table.keys(), key=lambda x: -len(self.q_table[x]))
        print("\n--- Learned Strategies (Top {}) ---".format(min(top_n, len(sorted_states))))
        for i, state in enumerate(sorted_states[:top_n]):
            best_action_idx = np.argmax(self.q_table[state])
            best_action = self.possible_actions[best_action_idx]
            print(f"State {state} : Best action = {best_action} (Q={self.q_table[state][best_action_idx]:.2f})")

def main():
    from buttonManager import PaperclipsButtonManager
    from infoCollector import PaperclipsInfoCollector
    from selenium import webdriver

    # Initialization
    driver = webdriver.Chrome()
    driver.get("https://www.decisionproblem.com/paperclips/index2.html")

    button_manager = PaperclipsButtonManager(driver)
    info_collector = PaperclipsInfoCollector(driver)
    ql_optimizer = QLearningPaperclipsOptimizer(button_manager, info_collector)

    try:
        ql_optimizer.run(episodes=1000, save_every=50)
        # Visualize learned strategies
        ql_optimizer.visualize_strategies(top_n=5)
    except KeyboardInterrupt:
        print("Manual stop, saving Q-table...")
        ql_optimizer.save_q_table()
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
