from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

def text_to_number(text):
    """
    Converts a text representing a number (e.g., "1,000", "1 000", "1.000") to an integer.
    Also handles decimal numbers if needed (e.g., "1,000.5" → 1000.5).
    """
    # Replace thousand separators with nothing
    text = text.replace(',', '').replace(' ', '').replace('.',
                                                          text.count('.') - 1) if '.' in text else text.replace(',',
                                                                                                                '').replace(
        ' ', '')
    try:
        # Try to convert to float first (to handle decimals)
        number = float(text)
        # Return an integer if the number is an integer
        return int(number) if number.is_integer() else number
    except ValueError:
        raise ValueError(f"Unable to convert '{text}' to a number.")

class PaperclipsInfoCollector:
    def __init__(self, driver):
        self.driver = driver

    def get_clips_count(self):
        try:
            clips_element = self.driver.find_element(By.ID, "clips")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Unable to retrieve the number of paperclips: {e}")
            return "0"

    def get_wire_cost(self):
        try:
            clips_element = self.driver.find_element(By.ID, "wireCost")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Unable to retrieve the wire cost: {e}")
            return 0

    def get_wire_count(self):
        try:
            clips_element = self.driver.find_element(By.ID, "wire")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Unable to retrieve the wire count: {e}")
            return 0

    def get_funds(self):
        try:
            clips_element = self.driver.find_element(By.ID, "funds")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Unable to retrieve available funds: {e}")
            return 0

    def get_operations(self):
        try:
            clips_elements = self.driver.find_elements(By.ID, "operations")
            if len(clips_elements) > 0 and len(clips_elements[0].text) == 0:
                return 0
            else:
                clips_element = clips_elements[0]  # Takes the first element
                return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Unable to retrieve available operations: {e}")
            return 0

    def get_creativity(self):
        try:
            clips_elements = self.driver.find_elements(By.ID, "creativity")
            if len(clips_elements) > 0 and len(clips_elements[0].text) == 0:
                return 0
            else:
                clips_element = clips_elements[0]  # Takes the first element
                return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Unable to retrieve available creativity: {e}")
            return 0

    def get_unsold_clips(self):
        try:
            clips_element = self.driver.find_element(By.ID, "unsoldClips")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Unable to retrieve unsold clips: {e}")
            return 0

    def get_ad_costs(self):
        try:
            clips_element = self.driver.find_element(By.ID, "adCost")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Unable to retrieve ad costs: {e}")
            return 0

    def get_clip_maker_rate(self):
        try:
            clips_element = self.driver.find_element(By.ID, "clipmakerRate")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Unable to retrieve the paperclip production rate: {e}")
            return 0

    def get_autoclippers_count(self):
        try:
            clips_elements = self.driver.find_elements(By.ID, "clipmakerLevel2")
            if len(clips_elements) == 0:
                return 0  # No element found
            else:
                clips_element = clips_elements[0]  # Takes the first element
                text = clips_element.text.strip()  # Cleans the text
                return text_to_number(text) if text else 0  # Converts or returns 0 if empty
        except Exception as e:
            print(f"Unable to retrieve the number of auto clippers: {e}")
            return 0

    def get_megalippers_count(self):
        try:
            clips_elements = self.driver.find_elements(By.ID, "megaClipperLevel")
            if len(clips_elements) == 0:
                return 0  # No element found
            else:
                clips_element = clips_elements[0]  # Takes the first element
                text = clips_element.text.strip()  # Cleans the text
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

    time.sleep(1)
if __name__ == "__main__":
    main()
