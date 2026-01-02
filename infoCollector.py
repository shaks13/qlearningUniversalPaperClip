from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

def text_to_number(text):
    """
    Converts a text representing a number (e.g., "1,000", "1 000", "1.000") to an integer or float.
    Handles decimal numbers if needed (e.g., "1,000.5" → 1000.5).
    Returns 0 if conversion fails.
    """
    if not text or not isinstance(text, str):
        return 0

    # Remove all thousand separators (comma, space, dot)
    cleaned_text = text.strip()
    # Handle cases like "$1,000" or "1,000 clips"
    cleaned_text = ''.join(c for c in cleaned_text if c.isdigit() or c == '.')
    try:
        # Try to convert to float first (to handle decimals)
        number = float(cleaned_text)
        # Return an integer if the number is an integer
        return int(number) if number.is_integer() else number
    except ValueError:
        print(f"Unable to convert '{text}' to a number. Returning 0.")
        return 0


class PaperclipsInfoCollector:
    def __init__(self, driver):
        self.driver = driver

    def get_clips_count(self):
        try:
            element = self.driver.find_element(By.ID, "clips")
            return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve the number of paperclips: {e}")
            return "0"

    def get_wire_cost(self):
        try:
            element = self.driver.find_element(By.ID, "wireCost")
            return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve the wire cost: {e}")
            return 0

    def get_wire_count(self):
        try:
            element = self.driver.find_element(By.ID, "wire")
            return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve the wire count: {e}")
            return 0

    def get_funds(self):
        try:
            element = self.driver.find_element(By.ID, "funds")
            return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve available funds: {e}")
            return 0

    def get_paperclip_price(self):
        try:
            element = self.driver.find_element(By.ID, "margin")
            return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve paper clips price: {e}")
            return 0

    def get_paperclip_demand(self):
        try:
            element = self.driver.find_element(By.ID, "demand")
            return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to paper clip demand: {e}")
            return 0

    def get_operations(self):
        try:
            elements = self.driver.find_elements(By.ID, "operations")
            if len(elements) > 0 and len(elements[0].text) == 0:
                return 0
            else:
                element = elements[0]  # Takes the first element
                return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve available operations: {e}")
            return 0

    def get_creativity(self):
        try:
            elements = self.driver.find_elements(By.ID, "creativity")
            if len(elements) > 0 and len(elements[0].text) == 0:
                return 0
            else:
                element = elements[0]  # Takes the first element
                return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve available creativity: {e}")
            return 0

    def get_unsold_clips(self):
        try:
            element = self.driver.find_element(By.ID, "unsoldClips")
            return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve unsold clips: {e}")
            return 0

    def get_ad_costs(self):
        try:
            element = self.driver.find_element(By.ID, "adCost")
            return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve ad costs: {e}")
            return 0

    def get_clip_maker_rate(self):
        try:
            element = self.driver.find_element(By.ID, "clipmakerRate")
            return text_to_number(element.text)
        except Exception as e:
            print(f"Unable to retrieve the paperclip production rate: {e}")
            return 0

    def get_autoclippers_count(self):
        try:
            elements = self.driver.find_elements(By.ID, "clipmakerLevel2")
            if len(elements) == 0:
                return 0  # No element found
            else:
                element = elements[0]  # Takes the first element
                text = element.text.strip()  # Cleans the text
                return text_to_number(text) if text else 0  # Converts or returns 0 if empty
        except Exception as e:
            print(f"Unable to retrieve the number of auto clippers: {e}")
            return 0

    def get_autoclippers_cost(self):
        try:
            elements = self.driver.find_elements(By.ID, "clipperCost")
            if len(elements) == 0:
                return 0  # No element found
            else:
                element = elements[0]  # Takes the first element
                text = element.text.strip()  # Cleans the text
                return text_to_number(text) if text else 0  # Converts or returns 0 if empty
        except Exception as e:
            print(f"Unable to retrieve the cost of a clipper: {e}")
            return 0

    def get_megalippers_count(self):
        try:
            elements = self.driver.find_elements(By.ID, "megaClipperLevel")
            if len(elements) == 0:
                return 0  # No element found
            else:
                element = elements[0]  # Takes the first element
                text = element.text.strip()  # Cleans the text
                return text_to_number(text) if text else 0  # Converts or returns 0 if empty
        except Exception as e:
            print(f"Unable to retrieve the number of mega clippers: {e}")
            return 0

    def get_message_box_content(self):
        try:
            message_box = self.driver.find_element(By.CSS_SELECTOR, ".messageBox, #messageBox, .log")
            return message_box.text
        except Exception as e:
            print(f"Unable to retrieve the content of the black box: {e}")
            return ""

def main():
    from selenium import webdriver
    import time

    # Browser initialization
    driver = webdriver.Chrome()
    driver.get("https://www.decisionproblem.com/paperclips/index2.html")

    info_collector = PaperclipsInfoCollector(driver)
    clip_count = info_collector.get_clips_count()
    wire_cost = info_collector.get_wire_cost()
    wire_count = info_collector.get_wire_count()
    auto_clipper = info_collector.get_autoclippers_count()
    mega_clipper = info_collector.get_megalippers_count()
    print("clip_count:", clip_count)
    print("wire_cost:", wire_cost)
    print("wire_count:", wire_count)
    print("auto_clipper:", auto_clipper)
    print("mega_clipper:", mega_clipper)
    clip_maker_rate = info_collector.get_clip_maker_rate()
    ad_costs = info_collector.get_ad_costs()
    unsold_clips = info_collector.get_unsold_clips()
    funds = info_collector.get_funds()
    print("clip_maker_rate:", clip_maker_rate)
    print("ad_costs:", ad_costs)
    print("unsold_clips:", unsold_clips)
    print("funds:", funds)
    creativity = info_collector.get_creativity()
    operations = info_collector.get_operations()
    print("creativity:", creativity)
    print("operations:", operations)
    funds = info_collector.get_funds()
    print("funds:", funds)
    paperclip_price = info_collector.get_paperclip_price()
    print("paperclip_price:", paperclip_price)
    demand = info_collector.get_paperclip_demand()
    print("paperclip_demand:", demand)
    time.sleep(1)
if __name__ == "__main__":
    main()
