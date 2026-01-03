import time
from manager.baseManager import BaseQLearningManager

class PriceManager(BaseQLearningManager):
    """Manages price adjustments using Q-Learning"""

    def __init__(self, button_manager, info_collector, **kwargs):
        self.possible_actions = [
            "btnRaisePrice",
            "btnLowerPrice",
            "wait"
        ]
        self.action_to_index = {action: idx for idx, action in enumerate(self.possible_actions)}
        super().__init__(button_manager, info_collector, save_file="../data/q_table_prices.json", **kwargs)
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