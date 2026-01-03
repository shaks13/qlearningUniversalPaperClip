
from manager.baseManager import BaseQLearningManager
import time

class ResourceManager(BaseQLearningManager):
    """Manages resource purchases (Wire) using Q-Learning"""

    def __init__(self, button_manager, info_collector, **kwargs):
        self.possible_actions = [
            "btnBuyWire",
            "wait"
        ]
        self.action_to_index = {action: idx for idx, action in enumerate(self.possible_actions)}
        super().__init__(button_manager, info_collector, save_file="../data/q_table_resources.json", **kwargs)
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
