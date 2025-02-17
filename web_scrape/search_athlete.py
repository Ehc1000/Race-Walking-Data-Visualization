import platform
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager 
import utils as u
import constants as c


def set_up():
    """
    Sets up a headless Chrome WebDriver for web scraping.

    Uses webdriver-manager to automatically download the correct ChromeDriver version.
    Configures the Chrome WebDriver with headless mode and initializes it for scraping.

    Returns:
        WebDriver: An instance of the configured Chrome WebDriver.

    Raises:
        Exception: If there's an issue with setting up the WebDriver.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use newer headless mode
    chrome_options.add_argument("--no-sandbox")  # Helps avoid crashes
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoids memory issues
    chrome_options.add_argument("--remote-debugging-port=9222")  # Helps debug

    try:
        # Automatically install and use the correct ChromeDriver version
        driver_path = ChromeDriverManager().install()
        webdriver_service = Service(driver_path)
        
        url = "https://worldathletics.org/athletes/spain/alvaro-martin-14410246"  # TODO: Hardcoded URL for now
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        driver.maximize_window()
        driver.get(url)

        return driver
    except Exception as e:
        u.log(f"Error setting up WebDriver: {e}", "error")
        raise

def extract_athlete_url(driver):
    """
    Extracts the athlete URL from the search results on the page.

    Returns:
        str: Full URL of the first athlete's profile if found.
        None: If no search results or URL is found.
    """
    try:
        # Locate the first search result cell -> we can add more results if needed. As of right now assume validiity of the first result
        result_cell = driver.find_element(By.CLASS_NAME, "AthleteSearch_name__2z8I1")
        u.log("Search result cell found.")

        # Locate the <a> tag inside the cell and extract the href attribute (houses second half of URL)
        link_element = result_cell.find_element(By.TAG_NAME, "a")
        relative_url = link_element.get_attribute("href")
        full_url = f"https://worldathletics.org{relative_url}" if relative_url.startswith("/") else relative_url

        u.log(f"Extracted URL: {full_url}")
        return full_url
    except Exception as e:
        u.log(f"Error extracting athlete URL: {e}", "error")
        return None


def search_athlete(athlete_name):
    driver = set_up()
    try:
        # Navigate to the base website
        url = "https://worldathletics.org/athletes"
        driver.get(url)
        u.log(f"Navigated to {url}")

        # Locate and change input value in search bar
        search_bar = driver.find_element(By.CLASS_NAME, "AthleteSearch_searchInput__37_Nk")
        search_bar.send_keys(athlete_name)
        u.log(f"Entered '{athlete_name}' in the search bar.")

        # Locate and click search button 
        search_button = driver.find_element(By.CLASS_NAME, "AthleteSearch_searchBtn__2CjV_")
        search_button.click()
        u.log("Search button clicked.")

        # wait for the search results before calling the URL extractor -> adjust this timer as needed
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "AthleteSearch_name__2z8I1"))
            )
            u.log("Search results loaded.")
        except Exception as e:
            u.log(f"Error waiting for search results: {e}", "error")
            return None

        # URL extractor call 
        profile_url = extract_athlete_url(driver)
        if profile_url:
            return profile_url
        else:
            u.log(f"No profile found for {athlete_name}.")
            return None
    except Exception as e:
        u.log(f"Unexpected error during the search process: {e}", "error")
        return None
    finally:
        driver.quit()
        u.log("WebDriver closed.")


if __name__ == "__main__":
    athlete_name = input("Enter the athlete's name: ").strip()
    profile_link = search_athlete(athlete_name)
    if profile_link:
        print(f"Profile link: {profile_link}")
    else:
        print("Athlete not found.")
