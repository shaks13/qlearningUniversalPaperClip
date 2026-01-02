from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

class PaperclipsButtonManager:
    def __init__(self, driver):
        self.driver = driver

    def is_button_clickable(self, button_id):
        """Vérifie si un bouton existe, est affiché et est cliquable."""
        try:
            button = self.driver.find_element(By.ID, button_id)
            return button.is_displayed() and button.is_enabled()
        except NoSuchElementException:
            return False

    def click_button_by_id(self, button_id):
        """Clique sur un bouton s'il est cliquable, sinon retourne False."""
        if self.is_button_clickable(button_id):
            try:
                button = self.driver.find_element(By.ID, button_id)
                button.click()
                return True
            except ElementNotInteractableException:
                print(f"Le bouton {button_id} n'est pas cliquable.")
                return False
        else:
            #print(f"Le bouton {button_id} n'existe pas ou n'est pas cliquable.")
            return False

def main():
    from selenium import webdriver
    # Initialisation du navigateur
    driver = webdriver.Chrome()
    driver.get("https://www.decisionproblem.com/paperclips/index2.html")

    btnmng = PaperclipsButtonManager(driver)
    btnmng.click_button_by_id("btnMakePaperclip")

if __name__ == "__main__":
    main()
