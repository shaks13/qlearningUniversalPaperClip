from manager.baseManager import BaseQLearningManager
import time

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

def main ():
    prod_mgmt = ProductionManager

if __name__ == "__main__":
    main()

