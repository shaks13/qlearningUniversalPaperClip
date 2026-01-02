import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import queue
import time

class PaperclipsGUI:
    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.root = tk.Tk()
        self.root.title("Universal Paperclips Q-Learning Optimizer")
        self.root.geometry("1000x800")

        # Data storage for plotting
        self.production_history = []
        self.resource_history = []
        self.price_history = []
        self.reward_history = {"production": [], "resource": [], "price": []}
        self.action_history = {"production": [], "resource": [], "price": []}

        # Queue for thread-safe communication
        self.data_queue = queue.Queue()

        # Create GUI elements
        self.create_widgets()

        # Start the update loop
        self.update_gui()

        # Start a thread to run the optimizer
        self.running = True
        self.optimizer_thread = threading.Thread(target=self.run_optimizer)
        self.optimizer_thread.daemon = True
        self.optimizer_thread.start()

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Stats tab
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Stats")

        # Production frame
        prod_frame = ttk.LabelFrame(self.stats_tab, text="Production")
        prod_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.prod_clips_label = ttk.Label(prod_frame, text="Clips: 0")
        self.prod_clips_label.pack(anchor="w")
        self.prod_clippers_label = ttk.Label(prod_frame, text="Clippers: 0")
        self.prod_clippers_label.pack(anchor="w")
        self.prod_megaclippers_label = ttk.Label(prod_frame, text="MegaClippers: 0")
        self.prod_megaclippers_label.pack(anchor="w")
        self.prod_rate_label = ttk.Label(prod_frame, text="Rate: 0")
        self.prod_rate_label.pack(anchor="w")
        self.prod_action_label = ttk.Label(prod_frame, text="Last Action: None")
        self.prod_action_label.pack(anchor="w")
        self.prod_reward_label = ttk.Label(prod_frame, text="Reward: 0")
        self.prod_reward_label.pack(anchor="w")

        # Resources frame
        res_frame = ttk.LabelFrame(self.stats_tab, text="Resources")
        res_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.res_wire_label = ttk.Label(res_frame, text="Wire: 0")
        self.res_wire_label.pack(anchor="w")
        self.res_funds_label = ttk.Label(res_frame, text="Funds: 0")
        self.res_funds_label.pack(anchor="w")
        self.res_wire_cost_label = ttk.Label(res_frame, text="Wire Cost: 0")
        self.res_wire_cost_label.pack(anchor="w")
        self.res_action_label = ttk.Label(res_frame, text="Last Action: None")
        self.res_action_label.pack(anchor="w")
        self.res_reward_label = ttk.Label(res_frame, text="Reward: 0")
        self.res_reward_label.pack(anchor="w")

        # Price frame
        price_frame = ttk.LabelFrame(self.stats_tab, text="Price Management")
        price_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        self.price_price_label = ttk.Label(price_frame, text="Price: 0")
        self.price_price_label.pack(anchor="w")
        self.price_demand_label = ttk.Label(price_frame, text="Demand: 0")
        self.price_demand_label.pack(anchor="w")
        self.price_unsold_label = ttk.Label(price_frame, text="Unsold: 0")
        self.price_unsold_label.pack(anchor="w")
        self.price_action_label = ttk.Label(price_frame, text="Last Action: None")
        self.price_action_label.pack(anchor="w")
        self.price_reward_label = ttk.Label(price_frame, text="Reward: 0")
        self.price_reward_label.pack(anchor="w")

        # Plots tab
        self.plots_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plots_tab, text="Plots")

        # Create matplotlib figures
        self.create_plots()

        # Control buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_optimizer)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_optimizer)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(control_frame, text="Save Q-Tables", command=self.save_all_q_tables)
        self.save_button.pack(side=tk.LEFT, padx=5)

    def create_plots(self):
        """Create matplotlib plots for visualization"""
        # Production plot
        self.prod_fig, self.prod_ax = plt.subplots(figsize=(4, 3))
        self.prod_ax.set_title("Production Over Time")
        self.prod_ax.set_xlabel("Time")
        self.prod_ax.set_ylabel("Count")
        self.prod_canvas = FigureCanvasTkAgg(self.prod_fig, master=self.plots_tab)
        self.prod_canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

        # Resources plot
        self.res_fig, self.res_ax = plt.subplots(figsize=(4, 3))
        self.res_ax.set_title("Resources Over Time")
        self.res_ax.set_xlabel("Time")
        self.res_ax.set_ylabel("Count")
        self.res_canvas = FigureCanvasTkAgg(self.res_fig, master=self.plots_tab)
        self.res_canvas.get_tk_widget().grid(row=0, column=1, padx=5, pady=5)

        # Rewards plot
        self.reward_fig, self.reward_ax = plt.subplots(figsize=(4, 3))
        self.reward_ax.set_title("Rewards Over Time")
        self.reward_ax.set_xlabel("Time")
        self.reward_ax.set_ylabel("Reward")
        self.reward_canvas = FigureCanvasTkAgg(self.reward_fig, master=self.plots_tab)
        self.reward_canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def update_plots(self):
        """Update the matplotlib plots with new data"""
        # Production plot
        self.prod_ax.clear()
        if self.production_history:
            clips = [p['clips'] for p in self.production_history]
            clippers = [p['clippers'] for p in self.production_history]
            mega_clippers = [p['mega_clippers'] for p in self.production_history]
            self.prod_ax.plot(clips, label="Clips")
            self.prod_ax.plot(clippers, label="Clippers")
            self.prod_ax.plot(mega_clippers, label="MegaClippers")
            self.prod_ax.legend()
        self.prod_canvas.draw()

        # Resources plot
        self.res_ax.clear()
        if self.resource_history:
            wire = [r['wire'] for r in self.resource_history]
            funds = [r['funds'] for r in self.resource_history]
            self.res_ax.plot(wire, label="Wire")
            self.res_ax.plot(funds, label="Funds")
            self.res_ax.legend()
        self.res_canvas.draw()

        # Rewards plot
        self.reward_ax.clear()
        if self.reward_history['production']:
            self.reward_ax.plot(self.reward_history['production'], label="Production")
            self.reward_ax.plot(self.reward_history['resource'], label="Resource")
            self.reward_ax.plot(self.reward_history['price'], label="Price")
            self.reward_ax.legend()
        self.reward_canvas.draw()

    def update_gui(self):
        """Update the GUI with new data from the queue"""
        try:
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()

                # Update production stats
                if 'production' in data:
                    prod_data = data['production']
                    self.prod_clips_label.config(text=f"Clips: {prod_data['clips']}")
                    self.prod_clippers_label.config(text=f"Clippers: {prod_data['clippers']}")
                    self.prod_megaclippers_label.config(text=f"MegaClippers: {prod_data['mega_clippers']}")
                    self.prod_rate_label.config(text=f"Rate: {prod_data['production_rate']}")
                    self.prod_action_label.config(text=f"Last Action: {data.get('production_action', 'None')}")
                    self.prod_reward_label.config(text=f"Reward: {data.get('production_reward', 0)}")

                    self.production_history.append(prod_data)

                # Update resource stats
                if 'resource' in data:
                    res_data = data['resource']
                    self.res_wire_label.config(text=f"Wire: {res_data['wire']}")
                    self.res_funds_label.config(text=f"Funds: {res_data['funds']}")
                    self.res_wire_cost_label.config(text=f"Wire Cost: {res_data['wire_cost']}")
                    self.res_action_label.config(text=f"Last Action: {data.get('resource_action', 'None')}")
                    self.res_reward_label.config(text=f"Reward: {data.get('resource_reward', 0)}")

                    self.resource_history.append(res_data)

                # Update price stats
                if 'price' in data:
                    price_data = data['price']
                    self.price_price_label.config(text=f"Price: {price_data['price']}")
                    self.price_demand_label.config(text=f"Demand: {price_data['demand']}")
                    self.price_unsold_label.config(text=f"Unsold: {price_data['unsold']}")
                    self.price_action_label.config(text=f"Last Action: {data.get('price_action', 'None')}")
                    self.price_reward_label.config(text=f"Reward: {data.get('price_reward', 0)}")

                # Update rewards history
                if 'production_reward' in data:
                    self.reward_history['production'].append(data['production_reward'])
                if 'resource_reward' in data:
                    self.reward_history['resource'].append(data['resource_reward'])
                if 'price_reward' in data:
                    self.reward_history['price'].append(data['price_reward'])

            # Update plots
            self.update_plots()

        except queue.Empty:
            pass

        # Schedule the next update
        self.root.after(100, self.update_gui)

    def run_optimizer(self):
        """Run the optimizer in a separate thread"""
        episode = 0
        while self.running:
            episode += 1

            # Collect data from each manager
            data = {}

            # Production manager
            prod_stats = self.optimizer.production_manager.get_production_stats()
            if prod_stats:
                data['production'] = prod_stats
                action = self.optimizer.production_manager.choose_action(
                    self.optimizer.production_manager.get_state())
                data['production_action'] = action
                self.optimizer.production_manager.execute_action(action)
                reward = self.optimizer.production_manager.get_reward()
                data['production_reward'] = reward

            # Resource manager
            res_stats = self.optimizer.resource_manager.get_resource_stats()
            if res_stats:
                data['resource'] = res_stats
                action = self.optimizer.resource_manager.choose_action(
                    self.optimizer.resource_manager.get_state())
                data['resource_action'] = action
                self.optimizer.resource_manager.execute_action(action)
                reward = self.optimizer.resource_manager.get_reward()
                data['resource_reward'] = reward

            # Price manager
            price_stats = self.optimizer.price_manager.get_price_stats()
            if price_stats:
                data['price'] = price_stats
                action = self.optimizer.price_manager.choose_action(
                    self.optimizer.price_manager.get_state())
                data['price_action'] = action
                self.optimizer.price_manager.execute_action(action)
                reward = self.optimizer.price_manager.get_reward()
                data['price_reward'] = reward

            # Send data to GUI
            self.data_queue.put(data)

            # Save Q-tables periodically
            if episode % 100 == 0:
                self.optimizer.production_manager.save_q_table()
                self.optimizer.resource_manager.save_q_table()
                self.optimizer.price_manager.save_q_table()

            # Small delay to prevent overwhelming the browser
            time.sleep(0.5)

    def start_optimizer(self):
        """Start the optimizer thread"""
        self.running = True
        if not self.optimizer_thread.is_alive():
            self.optimizer_thread = threading.Thread(target=self.run_optimizer)
            self.optimizer_thread.daemon = True
            self.optimizer_thread.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_optimizer(self):
        """Stop the optimizer thread"""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def save_all_q_tables(self):
        """Save all Q-tables to disk"""
        self.optimizer.production_manager.save_q_table()
        self.optimizer.resource_manager.save_q_table()
        self.optimizer.price_manager.save_q_table()
        print("All Q-tables saved!")

    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()
