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
    chrome_options.add_argument("--headless")
    webdriver_service = Service(c.CHROME_DRIVER_PATH)  # TODO: Update with the path to your chromedriver TODO: install driver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    url = "https://worldathletics.org/athletes/spain/alvaro-martin-14410246" #TODO: url hardcoded
    driver.get(url)

    return driver

def get_profile_image():
    try:
        img_element = driver.find_element(By.XPATH, "//img[@alt='Athlete']")
        img_url = img_element.get_attribute("src")
        u.write(f"Image URL: {img_url}\n")
        u.log(f"Image URL: {img_url}\n", level="info")
    except Exception as e:
        u.log(f"Error finding image: {e}", level="error")

def close_cookie_banner():
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        cookie_button.click()
        u.log("Successfully clicked the 'Allow all cookies' button.", level="info")
    except Exception as e:
        u.log(f"Error closing cookie banner: {e}", level="error")

def click_statistics_button():
    try:
        statistics_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='STATISTICS']")))
        statistics_button.click()
        u.log("Successfully clicked 'STATISTICS' button.", level="info")
    except Exception as e:
        u.log(f"Error clicking 'STATISTICS' button: {e}", level="error")

def get_world_rankings():
    world_rankings_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='World rankings']")))
    world_rankings_button.click()

    # parent_div = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[2]/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div/div/div[1]/div[2]')
    # children = parent_div.find_elements(By.XPATH, "./*")

    # for index, child in enumerate(children):
    #         print(f"Child {index + 1}:")
    #         print(f"Tag Name: {child.tag_name}")
    #         print(f"Text Content: {child.text}")
    #         print(f"Attributes: {child.get_attribute('outerHTML')}")
    #         print("------------")






driver = set_up()
get_profile_image()
close_cookie_banner()
click_statistics_button()
get_world_rankings()

# WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='STATISTICS']")))
# WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@value='World rankings']")))



driver.quit()
