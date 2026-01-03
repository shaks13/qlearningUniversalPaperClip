from manager.priceManager import PriceManager
from manager.ressourceManager import ResourceManager
from manager.productionManager import ProductionManager


class PaperclipsOptimizer:
    """Main class to coordinate the three managers"""

    def __init__(self, button_manager, info_collector):
        self.production_manager = ProductionManager(button_manager, info_collector)
        self.resource_manager = ResourceManager(button_manager, info_collector)
        self.price_manager = PriceManager(button_manager, info_collector)

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
