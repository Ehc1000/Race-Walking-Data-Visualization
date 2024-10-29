import platform

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import constants as c
import utils as u


def set_up():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    
    os_name = platform.system()
    if os_name not in c.DRIVER_PATHS:
        u.log("Unsupported OS. Only Windows and macOS are supported.", "error")
        raise EnvironmentError("Unsupported OS. Only Windows and macOS are supported.")

    webdriver_service = Service(c.DRIVER_PATHS[os_name])
    url = "https://worldathletics.org/athletes/spain/alvaro-martin-14410246" #TODO: Hardcoded URL for now
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.maximize_window()
    driver.get(url)

    return driver

def close_cookie_banner():
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        cookie_button.click()
        u.log("Successfully clicked the 'Allow all cookies' button.")
    except Exception as e:
        u.log(f"Error closing cookie banner: {e}", "error")

def get_profile_image():
    try:
        img_element = driver.find_element(By.XPATH, "//img[@alt='Athlete']")
        img_url = img_element.get_attribute("src")
        u.log(f"Image URL: {img_url}")
    except Exception as e:
        u.log(f"Error finding image: {e}", "error")

def click_statistics_button():
    try:
        statistics_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='STATISTICS']")))
        statistics_button.click()
        u.log("Successfully clicked 'STATISTICS' button.")
    except Exception as e:
        u.log(f"Error clicking 'STATISTICS' button: {e}", "error")

def get_world_rankings():
    try:
        world_rankings_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='World rankings']"))
        )
        world_rankings_button.click()
        u.log("Successfully clicked 'World rankings' button.")

        stats_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "athletesStatisticsTable_athletesStatisticsContent__dDNOs"))
        )
        # event_sections = stats_section.find_elements(By.CLASS_NAME, "athletesCardContainer_athletesCardContainer__39h-0")
        # event_sections = stats_section.find_elements(By.XPATH, "//div[contains(@class, 'athletesCardContainer')]")
        event_sections = stats_section.find_elements(By.XPATH, 
            "//div[contains(@class, 'athletesCardContainer')]"
            " | //div[contains(text(), 'Race Walking')]"
            " | //div[contains(text(), 'Ranking')]"
        )

        u.log(f"Length: {len(event_sections)}")

        for event in event_sections:
            event_titles = event.find_elements(By.CLASS_NAME, "profileStatistics_rankingCardTitle__2OeiW")
            labels = event.find_elements(By.CLASS_NAME, "athletesEventsDetails_athletesEventsDetailsLabel__6KN98")
            values = event.find_elements(By.CLASS_NAME, "athletesEventsDetails_athletesEventsDetailsValue__FrHFZ")

            for event_title in event_titles:
                u.log(f"Event Title: {event_title.text}")

            for label, value in zip(labels, values):
                u.log(f"{label.text}: {value.text}")

    except Exception as e:
        u.log(f"Error getting world rankings: {e}", "error")
    
def get_personal_bests():
    try:
        personal_bests_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Personal bests']"))
        )
        personal_bests_button.click()
        u.log("Successfully clicked 'Personal Bests' button.")

        stats_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "athletesStatisticsTable_athletesStatisticsContent__dDNOs"))
        )
        event_sections = stats_section.find_elements(By.XPATH, 
            "//div[contains(@class, 'athletesCardContainer')]"
            " | //div[contains(text(), 'Race Walk')]"
            " | //div[contains(text(), 'Ranking')]"
        )

        u.log(f"Length: {len(event_sections)}")

        for event in event_sections:
            event_titles = event.find_elements(By.CLASS_NAME, "athletesTitle_athletesTitle__388RT")
            labels = event.find_elements(By.CLASS_NAME, "athletesEventsDetails_athletesEventsDetailsLabel__6KN98")
            values = event.find_elements(By.CLASS_NAME, "athletesEventsDetails_athletesEventsDetailsValue__FrHFZ")

            for event_title in event_titles:
                u.log(f"Event Title: {event_title.text}")

            for label, value in zip(labels, values):
                u.log(f"{label.text}: {value.text}")

    except Exception as e:
        u.log(f"Error getting Personal Bests: {e}", "error")

if __name__ == "__main__":
    driver = set_up()
    close_cookie_banner()
    get_profile_image()
    click_statistics_button()  
    get_world_rankings()
    get_personal_bests()
    driver.quit()
