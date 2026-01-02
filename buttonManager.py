from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

class PaperclipsButtonManager:
    def __init__(self, driver):
        self.driver = driver

    def is_button_clickable(self, button_id):
        """Checks if a button exists, is displayed, and is clickable."""
        try:
            button = self.driver.find_element(By.ID, button_id)
            return button.is_displayed() and button.is_enabled()
        except NoSuchElementException:
            return False

    def click_button_by_id(self, button_id):
        """Clicks on a button if it is clickable, otherwise returns False."""
        if self.is_button_clickable(button_id):
            try:
                button = self.driver.find_element(By.ID, button_id)
                button.click()
                return True
            except ElementNotInteractableException:
                print(f"The button {button_id} is not clickable.")
                return False
        else:
            # print(f"The button {button_id} does not exist or is not clickable.")
            return False

def main():
    from selenium import webdriver
    # Browser initialization
    driver = webdriver.Chrome()
    driver.get("https://www.decisionproblem.com/paperclips/index2.html")

    btnmng = PaperclipsButtonManager(driver)
    btnmng.click_button_by_id("btnMakePaperclip")

if __name__ == "__main__":
    main()
