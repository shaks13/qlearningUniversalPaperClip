from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

def text_to_number(text):
    """
    Convertit un texte représentant un nombre (ex: "1,000", "1 000", "1.000") en entier.
    Gère aussi les nombres décimaux si besoin (ex: "1,000.5" → 1000.5).
    """
    # Remplace les séparateurs de milliers par rien
    text = text.replace(',', '').replace(' ', '').replace('.', '',
                                                          text.count('.') - 1) if '.' in text else text.replace(',',
                                                                                                                '').replace(
        ' ', '')
    try:
        # Essaie de convertir en float d'abord (pour gérer les décimaux)
        number = float(text)
        # Retourne un entier si le nombre est entier
        return int(number) if number.is_integer() else number
    except ValueError:
        raise ValueError(f"Impossible de convertir '{text}' en nombre.")

class PaperclipsInfoCollector:
    def __init__(self, driver):
        self.driver = driver

    def get_clips_count(self):
        try:
            clips_element = self.driver.find_element(By.ID, "clips")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Impossible de récupérer le nombre de paperclips: {e}")
            return "0"

    def get_wire_cost(self):
        try:
            clips_element = self.driver.find_element(By.ID, "wireCost")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Impossible de récupérer le cout du fil: {e}")
            return 0

    def get_wire_count(self):
        try:
            clips_element = self.driver.find_element(By.ID, "wire")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Impossible de récupérer le compte de fil: {e}")
            return 0

    def get_funds(self):
        try:
            clips_element = self.driver.find_element(By.ID, "funds")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Impossible de récupérer les fonds disponible: {e}")
            return 0

    def get_operations(self):
        try:
            clips_elements = self.driver.find_elements(By.ID, "operations")
            if len(clips_elements[0].text) == 0:
                return 0
            else:
                clips_element = clips_elements[0]  # Prend le premier élément
                return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Impossible de récupérer les operations disponible: {e}")
            return 0

    def get_creativity(self):
        try:
            clips_elements = self.driver.find_elements(By.ID, "creativity")
            if len(clips_elements[0].text) == 0:
                return 0
            else:
                clips_element = clips_elements[0]  # Prend le premier élément
                return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Impossible de récupérer les creativités disponible: {e}")
            return 0

    def get_unsold_clips(self):
        try:
            clips_element = self.driver.find_element(By.ID, "unsoldClips")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Impossible de récupérer les fonds disponible: {e}")
            return 0

    def get_ad_costs(self):
        try:
            clips_element = self.driver.find_element(By.ID, "adCost")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Impossible de récupérer les fonds disponible: {e}")
            return 0

    def get_clip_maker_rate(self):
        try:
            clips_element = self.driver.find_element(By.ID, "clipmakerRate")
            return text_to_number(clips_element.text)
        except Exception as e:
            print(f"Impossible de récupérer le taux de création des trombonnes : {e}")
            return 0

    def get_autoclippers_count(self):
        try:
            clips_elements = self.driver.find_elements(By.ID, "clipmakerLevel2")
            if len(clips_elements) == 0:
                return 0  # Aucun élément trouvé
            else:
                clips_element = clips_elements[0]  # Prend le premier élément
                text = clips_element.text.strip()  # Nettoie le texte
                return text_to_number(text) if text else 0  # Convertit ou retourne 0 si vide
        except Exception as e:
            print(f"Impossible de récupérer le nombre d'auto clipper: {e}")
            return 0

    def get_megalippers_count(self):
        try:
            clips_elements = self.driver.find_elements(By.ID, "megaClipperLevel")
            if len(clips_elements) == 0:
                return 0  # Aucun élément trouvé
            else:
                clips_element = clips_elements[0]  # Prend le premier élément
                text = clips_element.text.strip()  # Nettoie le texte
                return text_to_number(text) if text else 0  # Convertit ou retourne 0 si vide
        except Exception as e:
            print(f"Impossible de récupérer le nombre d'auto clipper: {e}")
            return 0

    def get_message_box_content(self):
        try:
            message_box = self.driver.find_element(By.CSS_SELECTOR, ".messageBox, #messageBox, .log")
            return message_box.text
        except Exception as e:
            print(f"Impossible de récupérer le contenu du cadre noir: {e}")
            return ""

def main():
    from selenium import webdriver
    import time

    # Initialisation du navigateur
    driver = webdriver.Chrome()
    driver.get("https://www.decisionproblem.com/paperclips/index2.html")

    info_collector = PaperclipsInfoCollector(driver)
    clip_count = info_collector.get_clips_count()
    wire_cost = info_collector.get_wire_cost()
    wire_count = info_collector.get_wire_count()
    auto_clipper = info_collector.get_autoclippers_count()
    mega_clipper = info_collector.get_megalippers_count()
    print ("clip_count :", clip_count)
    print("wire_cost :", wire_cost)
    print("wire_count :", wire_count)
    print("auto_clipper :", auto_clipper)
    print("mega_clipper :", mega_clipper)
    clip_maker_rate = info_collector.get_clip_maker_rate()
    ad_costs = info_collector.get_ad_costs()
    unsold_clips = info_collector.get_unsold_clips()
    funds = info_collector.get_funds()
    print("clip_maker_rate :", clip_maker_rate)
    print("ad_costs :", ad_costs)
    print("unsold_clips :", unsold_clips)
    print("funds :", funds)
    creativity = info_collector.get_creativity()
    operations = info_collector.get_operations()
    print("creativity :", creativity)
    print("operations :", operations)

    time.sleep (1)
if __name__ == "__main__":
    main()