import numpy as np
import random
import time
import json
import os
from collections import defaultdict
from gui import PaperclipsGUI
from infoCollector import text_to_number

class BaseQLearningManager:
    """Base class for Q-Learning managers with common functionality"""

    def __init__(self, button_manager, info_collector, learning_rate=0.1, discount_factor=0.9,
                 exploration_rate=1.0, min_exploration_rate=0.01, exploration_decay=0.995,
                 save_file="data/q_table.json"):
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


class ProductionManager(BaseQLearningManager):
    """Manages paperclip and clipper production using Q-Learning"""

    def __init__(self, button_manager, info_collector, **kwargs):
        self.possible_actions = [
            "btnMakePaperclip",
            "btnMakeClipper",
            "btnMakeMegaClipper",
            "wait"
        ]
        self.action_to_index = {action: idx for idx, action in enumerate(self.possible_actions)}
        super().__init__(button_manager, info_collector, save_file="data/q_table_production.json", **kwargs)
        self.clips_history = [0, 0]
        self.production_reward_history = 0
        self.max_history = 10
        self.last_action = "wait"

    def get_state(self):
        """Returns a discretized state for production management"""
        clips = self.info_collector.get_clips_count()
        autoclippers = self.info_collector.get_autoclippers_count()
        megalippers = self.info_collector.get_megalippers_count()
        clip_maker_rate = self.info_collector.get_clip_maker_rate()

        # Discretize state components
        clips_state = min(clips // 100, 50)
        autoclippers_state = min(autoclippers // 10, 20)
        megalippers_state = min(megalippers // 5, 10)
        rate_state = min(clip_maker_rate // 10, 20)

        return f"prod_clips_{clips_state}_auto_{autoclippers_state}_mega_{megalippers_state}_rate_{rate_state}"

    def can_buy_clipper(self):
        """return true when the IA can afford to buy a clipper without risking wire shortage"""
        funds = self.info_collector.get_funds()
        wire_cost = self.info_collector.get_wire_cost()
        clippers_cost = self.info_collector.get_autoclippers_cost()
        if funds - clippers_cost < wire_cost:
            return False
        return True

    def get_reward(self):
        """Calculates reward based on production metrics"""
        clips = self.info_collector.get_clips_count()
        autoclippers = self.info_collector.get_autoclippers_count()
        megalippers = self.info_collector.get_megalippers_count()
        clip_maker_rate = self.info_collector.get_clip_maker_rate()

        penalities = 0

        # Update histories
        self.clips_history.append(clips)
        if len(self.clips_history) > self.max_history:
            self.clips_history.pop(0)

        # Immediate reward (increase in clips)
        immediate_reward = 0
        if len(self.clips_history) >= 2:
            immediate_reward = max(clips - self.clips_history[-2] - clip_maker_rate, 0)

        # Production reward (AutoClippers and MegaClippers)
        current_production = autoclippers + 10 * megalippers
        production_reward = current_production - self.production_reward_history
        self.production_reward_history = current_production

        # Trend reward
        trend_reward = 0
        if len(self.clips_history) >= 2:
            trend = (self.clips_history[-1] - self.clips_history[0]) / len(self.clips_history)
            trend_reward = trend * 0.1

        # Pénality when the last action was to buy a clipper but the funds is not enough
        if (
                self.last_action == "btnMakeClipper" or self.last_action == "btnMakeMegaClipper") and not self.can_buy_clipper():
            penalities -= 10

        return immediate_reward + production_reward + trend_reward + penalities

    def execute_action(self, action):
        """Executes a production-related action"""
        self.last_action = action
        if action == "wait":
            return True
        return self.button_manager.click_button_by_id(action)

    def get_production_stats(self):
        """Returns current production statistics for GUI display."""
        try:
            stats = {
                'clips': self.info_collector.get_clips_count(),
                'clippers': self.info_collector.get_autoclippers_count(),
                'mega_clippers': self.info_collector.get_megalippers_count(),
                'production_rate': self.info_collector.get_clip_maker_rate()
            }
            # Convert all values to integers for cleaner display
            return {k: int(v) if isinstance(v, (int, float)) else 0 for k, v in stats.items()}
        except Exception as e:
            print(f"Error getting production stats: {e}")
            return {
                'clips': 0,
                'clippers': 0,
                'mega_clippers': 0,
                'production_rate': 0
            }

    def run(self, episodes=1000, save_every=100, waiting_time=0.1):
        for i in range(episodes):
            state = self.get_state()
            action = self.choose_action(state)
            success = self.execute_action(action)
            time.sleep(waiting_time)
            new_state = self.get_state()
            reward = self.get_reward()
            self.update_q_table(state, action, reward, new_state)
            self.decay_exploration()
            print(f"Iteration {i + 1}/{episodes} | State: {state} | Action: {action} | Reward: {reward}")
            if (i + 1) % save_every == 0:
                self.save_q_table()
        self.save_q_table()


class ResourceManager(BaseQLearningManager):
    """Manages resource purchases (Wire) using Q-Learning"""

    def __init__(self, button_manager, info_collector, **kwargs):
        self.possible_actions = [
            "btnBuyWire",
            "wait"
        ]
        self.action_to_index = {action: idx for idx, action in enumerate(self.possible_actions)}
        super().__init__(button_manager, info_collector, save_file="data/q_table_resources.json", **kwargs)
        self.wire_history = [0]
        self.funds_history = [0]
        self.max_history = 10

    def get_state(self):
        """Returns a discretized state for resource management"""
        wire = self.info_collector.get_wire_count()
        funds = self.info_collector.get_funds()
        wire_cost = self.info_collector.get_wire_cost()

        # Discretize state components
        wire_state = min(wire // 100, 20)
        funds_state = min(funds // 100, 20)
        cost_ratio = min(funds // (wire_cost + 1), 10) if wire_cost > 0 else 0

        return f"res_wire_{wire_state}_funds_{funds_state}_ratio_{cost_ratio}"

    def get_reward(self):
        """Calculates reward based on resource management"""
        wire = self.info_collector.get_wire_count()
        funds = self.info_collector.get_funds()
        wire_cost = self.info_collector.get_wire_cost()

        # Update histories
        self.wire_history.append(wire)
        self.funds_history.append(funds)
        if len(self.wire_history) > self.max_history:
            self.wire_history.pop(0)
            self.funds_history.pop(0)

        # Reward for maintaining good resource levels
        reward = 0

        # Penalty for low and high wire
        if wire < 100 or wire > 100000:
            reward -= 30
        elif wire < 500 or wire > 10000:
            reward -= 10

        # Reward for having sufficient funds relative to wire cost
        if wire_cost > 0:
            fund_ratio = funds / wire_cost
            if fund_ratio > 5:
                reward += 10
            elif fund_ratio > 2:
                reward += 5

        # Reward for increasing wire stock
        if len(self.wire_history) >= 2:
            wire_increase = self.wire_history[-1] - self.wire_history[-2]
            if wire_increase > 0:
                reward += wire_increase * 0.1

        return reward

    def execute_action(self, action):
        """Executes a resource-related action"""
        if action == "wait":
            return True
        return self.button_manager.click_button_by_id(action)

    def get_resource_stats(self):
        """Returns current resource statistics for GUI display."""
        try:
            wire = self.info_collector.get_wire_count()
            funds = self.info_collector.get_funds()
            wire_cost = self.info_collector.get_wire_cost()

            return {
                'wire': int(wire) if wire else 0,
                'funds': int(funds) if funds else 0,
                'wire_cost': int(wire_cost) if wire_cost else 0,
                'funds_to_wire_ratio': int(funds // (wire_cost + 0.1)) if wire_cost and funds else 0
            }
        except Exception as e:
            print(f"Error getting resource stats: {e}")
            return {
                'wire': 0,
                'funds': 0,
                'wire_cost': 0,
                'funds_to_wire_ratio': 0
            }


    def run(self, episodes=1, save_every=100, waiting_time=0.1):
        """Runs the resource management optimization loop."""
        for i in range(episodes):
            state = self.get_state()
            action = self.choose_action(state)
            success = self.execute_action(action)
            time.sleep(waiting_time)
            new_state = self.get_state()
            reward = self.get_reward()
            self.update_q_table(state, action, reward, new_state)
            self.decay_exploration()
            print(f"Iteration {i + 1}/{episodes} | State: {state} | Action: {action} | Reward: {reward}")
            if (i + 1) % save_every == 0:
                self.save_q_table()
        return True


class PriceManager(BaseQLearningManager):
    """Manages price adjustments using Q-Learning"""

    def __init__(self, button_manager, info_collector, **kwargs):
        self.possible_actions = [
            "btnRaisePrice",
            "btnLowerPrice",
            "wait"
        ]
        self.action_to_index = {action: idx for idx, action in enumerate(self.possible_actions)}
        super().__init__(button_manager, info_collector, save_file="data/q_table_prices.json", **kwargs)
        self.price_history = []
        self.demand_history = []
        self.funds_history = [0]
        self.max_history = 10

    def get_state(self):
        """Returns a discretized state for price management"""
        price = self.info_collector.get_paperclip_price()
        demand = self.info_collector.get_paperclip_demand()
        unsold_clips = self.info_collector.get_unsold_clips()

        # Discretize state components
        price_state = min(price // 0.01, 50)  # Assuming price is in dollars
        demand_state = min(demand, 10) if isinstance(demand, (int, float)) else 0
        unsold_state = min(unsold_clips // 100, 20)

        return f"price_{price_state}_demand_{demand_state}_unsold_{unsold_state}"

    def get_reward(self):
        """Calculates reward based on price management"""
        price = self.info_collector.get_paperclip_price()
        demand = self.info_collector.get_paperclip_demand()
        unsold_clips = self.info_collector.get_unsold_clips()
        funds = self.info_collector.get_funds()

        # Update histories
        self.price_history.append(price)
        self.demand_history.append(demand)
        if len(self.price_history) > self.max_history:
            self.price_history.pop(0)
            self.demand_history.pop(0)

        # Reward for good price management
        reward = 0

        # Penalty for too many unsold clips
        if unsold_clips > 1000:
            reward -= unsold_clips * 0.01
        elif unsold_clips > 500:
            reward -= unsold_clips * 0.005

        # Reward for high demand
        if isinstance(demand, (int, float)):
            reward = (demand - 50) / 10

        # Reward for increasing funds
        if len(self.price_history) >= 2:
            if funds > self.funds_history[-1] if len(self.funds_history) > 0 else 0:
                reward += 0.1 * (funds - (self.funds_history[-1] if len(self.funds_history) > 0 else 0))

        return reward

    def execute_action(self, action):
        """Executes a price-related action"""
        if action == "wait":
            return True
        return self.button_manager.click_button_by_id(action)

    def get_price_stats(self):
        """Returns current price management statistics for GUI display."""
        try:
            # Get price (may need to adapt based on actual game element IDs)
            price= self.info_collector.get_paperclip_price()

            # Get demand (adapt based on actual game)
            demand = self.info_collector.get_paperclip_demand()

            # Get unsold clips
            unsold_clips = self.info_collector.get_unsold_clips()

            return {
                'price': float(price) if price else 0.0,
                'demand': float(demand) if demand else 0.0,
                'unsold': int(unsold_clips) if unsold_clips else 0,
                'demand_level': "High" if demand > 0.7 else "Medium" if demand > 0.4 else "Low"
            }
        except Exception as e:
            print(f"Error getting price stats: {e}")
            return {
                'price': 0.0,
                'demand': 0.0,
                'unsold': 0,
                'demand_level': "Unknown"
            }

    def run(self, episodes=1, save_every=100, waiting_time=0.1):
        """Runs the price management optimization loop."""
        for i in range(episodes):
            state = self.get_state()
            action = self.choose_action(state)
            success = self.execute_action(action)
            time.sleep(waiting_time)
            new_state = self.get_state()
            reward = self.get_reward()
            self.update_q_table(state, action, reward, new_state)
            self.decay_exploration()
            print(f"Iteration {i + 1}/{episodes} | State: {state} | Action: {action} | Reward: {reward}")
            if (i + 1) % save_every == 0:
                self.save_q_table()
        return True


class PaperclipsOptimizer:
    """Main class to coordinate the three managers"""

    def __init__(self, button_manager, info_collector):
        self.production_manager = ProductionManager(button_manager, info_collector)
        self.resource_manager = ResourceManager(button_manager, info_collector)
        self.price_manager = PriceManager(button_manager, info_collector)

    def run_with_gui(self):
        """Run the optimizer with GUI visualization"""
        gui = PaperclipsGUI(self)
        gui.run()

    def run(self, episodes=1000):
        """Runs the optimization loop for all managers"""
        for i in range(episodes):
            # Run each manager
            self.production_manager.run(episodes=i, save_every=episodes)
            self.resource_manager.run(episodes=i, save_every=episodes)
            self.price_manager.run(episodes=i, save_every=episodes)

            # Print progress
            if (i + 1) % 100 == 0:
                print(f"Episode {i + 1}/{episodes} completed")


def main():
    from buttonManager import PaperclipsButtonManager
    from infoCollector import PaperclipsInfoCollector
    from selenium import webdriver

    # Initialization
    driver = webdriver.Chrome()
    driver.get("https://www.decisionproblem.com/paperclips/index2.html")

    button_manager = PaperclipsButtonManager(driver)
    info_collector = PaperclipsInfoCollector(driver)
    optimizer = PaperclipsOptimizer(button_manager, info_collector)

    try:
        optimizer.run(episodes=1000)
    except KeyboardInterrupt:
        print("Manual stop, saving Q-tables...")
        optimizer.production_manager.save_q_table()
        optimizer.resource_manager.save_q_table()
        optimizer.price_manager.save_q_table()
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
