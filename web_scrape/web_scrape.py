import platform
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import constants as c
import utils as u

import scrapedDataBase as db

schema_path = os.path.join(os.path.dirname(__file__), "sql", "schema.sql")
db.init_db("scraped_data.db", schema_path)


def set_up():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
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
    return img_url
    
    

def click_statistics_button():
    try:
        statistics_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='STATISTICS']")))
        statistics_button.click()
        u.log("Successfully clicked 'STATISTICS' button.")
    except Exception as e:
        u.log(f"Error clicking 'STATISTICS' button: {e}", "error")

def original_get_world_rankings():
    try:
        world_rankings_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='World rankings']"))
        )
        world_rankings_button.click()
        u.log("Successfully clicked 'World rankings' button.")

        stats_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "athletesStatisticsTable_athletesStatisticsContent__dDNOs"))
        )
        event_sections = stats_section.find_elements(By.XPATH, 
            "//div[contains(@class, 'athletesCardContainer')]"
            " | //div[contains(text(), 'Race Walking')]"
            " | //div[contains(text(), 'Ranking')]"
        )

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


def get_world_rankings(athlete_id):
    try:
        # Click the "World rankings" button
        world_rankings_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='World rankings']"))
        )
        world_rankings_button.click()
        u.log("Successfully clicked 'World rankings' button.")

        # Wait for the statistics section to load
        stats_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "athletesStatisticsTable_athletesStatisticsContent__dDNOs"))
        )
        event_sections = stats_section.find_elements(By.XPATH, 
            "//div[contains(@class, 'athletesCardContainer')]"
        )

        # Iterate over each event section
        for event_index, event in enumerate(event_sections, start=1):
            try:
                event_title = event.find_element(By.CLASS_NAME, "profileStatistics_rankingCardTitle__2OeiW").text

                # Extract labels and values for each event
                labels = event.find_elements(By.CLASS_NAME, "athletesEventsDetails_athletesEventsDetailsLabel__6KN98")
                values = event.find_elements(By.CLASS_NAME, "athletesEventsDetails_athletesEventsDetailsValue__FrHFZ")

                ranking_position = None
                ranking_score = None
                weeks_at_position = None

                # Match labels to extract specific data
                for label, value in zip(labels, values):
                    if label.text == "Place":
                        ranking_position = int(value.text)
                    elif label.text == "Score":
                        ranking_score = int(value.text)
                    elif label.text == "Weeks":
                        weeks_at_position = int(value.text)

                # Log extracted data
                u.log(f"Extracted ranking data for event #{event_index}:")
                u.log(f"  Event Title: {event_title}")
                u.log(f"  Ranking Position: {ranking_position}")
                u.log(f"  Ranking Score: {ranking_score}")
                u.log(f"  Weeks at Position: {weeks_at_position}")

                # Insert ranking into the database
                db.insert_ranking("scraped_data.db", athlete_id, event_title, ranking_position, ranking_score, weeks_at_position)
            except Exception as inner_e:
                u.log(f"Error processing event #{event_index}: {inner_e}", "error")

        u.log("Successfully stored all world rankings.")
    except Exception as e:
        u.log(f"Error getting world rankings: {e}", "error")



#athletesTitle_athletesTitle__388RT this has the card's race title
#profileStatistics_personnalBestCardWrapper__-09Nt -- this is the wrapper holding all the data
#profileStatistics_personnalBestCardContent__1GplY -- this has the race title, the date and flag name

#TODO: click the dropdown list to iterate through all the years, no idea how
def get_season_bests():
    try:
        # Click the "Season Bests" button
        season_bests_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Season')]"))
        )
        season_bests_button.click()
        u.log("Successfully clicked 'Season bests' button.")

        # Wait for the card wrappers to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "profileStatistics_personnalBestCardWrapper__-09Nt"))
        )

        # Retrieve all season best card wrappers
        season_bests_wrappers = driver.find_elements(By.CLASS_NAME, "profileStatistics_personnalBestCardWrapper__-09Nt")

        # Iterate through each card wrapper
        for index, wrapper in enumerate(season_bests_wrappers, start=1):
            u.log(f"Processing Season Bests Card #{index}")

            # Extract the race title
            race_titles = wrapper.find_elements(By.CLASS_NAME, "athletesTitle_athletesTitle__388RT")
            for race_title in race_titles:
                u.log(f"Race Title: {race_title.text}")

            # Extract race details (assumed to contain race name, date, and flag)
            race_details = wrapper.find_elements(By.CLASS_NAME, "profileStatistics_personnalBestCardContent__1GplY")
            for detail in race_details:
                # Split details text by line and label each part
                detail_lines = detail.text.splitlines()
                
                if len(detail_lines) > 0:
                    u.log(f"Race Name: {detail_lines[0]}")
                if len(detail_lines) > 1:
                    u.log(f"Date: {detail_lines[1]}")
                if len(detail_lines) > 2:
                    u.log(f"Flag/Country: {detail_lines[2]}")

    except Exception as e:
        u.log(f"Error getting season bests: {e}", "error")

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

#TODO: For some reason Row 9 of Table 1 always has missing data???
def get_progression():
    try:
        progression_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Progression']"))
        )
        progression_button.click()
        u.log("Successfully clicked 'Progression' button.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profileStatistics_table__1o71p"))
        )
        
        labels = ["YEAR", "TIME", "RACE", "DATE"]

        # Get all global titles, skipping the first as it's not useful for individual tables
        global_titles = driver.find_elements(By.CLASS_NAME, "athletesTitle_athletesTitle__388RT")
        global_title_texts = [title.text for title in global_titles][1:]  # Skip the first title
        u.log(f"Global titles found on page (skipping first): {global_title_texts}")

        tables = driver.find_elements(By.CLASS_NAME, "profileStatistics_table__1o71p")[:-1]  # Skip the last table, it's out of scope for this func.

        for table_index, table in enumerate(tables):
            table_title = global_title_texts[table_index] if table_index < len(global_title_texts) else "Unknown Title"
            u.log(f"Extracting data from table '{table_title}'...")

            table_body = table.find_element(By.CLASS_NAME, "profileStatistics_tableBody__1w5O9")
            rows = table_body.find_elements(By.TAG_NAME, "tr")

            for row_index, row in enumerate(rows):
                td_elements = row.find_elements(By.TAG_NAME, "td")
            
                row_data = {label: td.text for label, td in zip(labels, td_elements)}
                u.log(f"Row {row_index + 1} Data for '{table_title}': {row_data}")

    except Exception as e:
        u.log(f"Error getting progression data: {e}", "error")


#def get_results() #TODO: implement

#Event title: athletesTitle_athletesTitle__388RT
# Table body: profileStatistics_tableBody__1w5O9. It has the data in this order: placement, race title, date
# Click this dropdown button to get more data: athletesDropdownButton_athletesDropdownButton__3k-Ds
# Data in this dropdown class: profileStatistics_trDropdownContent__21lVN, has Mark, Venue, Competition.

#TODO: need to somehow click the dropdown carrot to get mark, venue and competition data.
def get_honours():
    try:
        honours_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Honours']"))
        )
        honours_button.click()
        u.log("Successfully clicked 'Honours' button.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "profileStatistics_tableBody__1w5O9"))
        )

        event_titles = driver.find_elements(By.CLASS_NAME, "athletesTitle_athletesTitle__388RT")[1:-1]
        table_bodies = driver.find_elements(By.CLASS_NAME, "profileStatistics_tableBody__1w5O9")[:-1]

        # Loop through each title-table pair, excluding the last table
        for index, (event_title, table_body) in enumerate(zip(event_titles, table_bodies), start=1):
            u.log(f"Processing Table #{index} with Event Title: {event_title.text}")

            rows = table_body.find_elements(By.TAG_NAME, "tr")

            labels = ["Placement", "Race Title", "Date"]

            for row_index, row in enumerate(rows):
                td_elements = row.find_elements(By.TAG_NAME, "td")
                row_data = {label: td.text for label, td in zip(labels, td_elements)}
                u.log(f"Row {row_index + 1} Data for '{event_title.text}': {row_data}")

    except Exception as e:
        u.log(f"Error getting honours data: {e}", "error")

def get_athlete_name(driver):
    try:
        # Wait for the element to be present
        name_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "athletesBio_athletesBioTitle__3pPRL"))
        )
        spans = name_div.find_elements(By.TAG_NAME, "span")
        athlete_first_name = spans[0].text
        athlete_last_name = spans[1].text
        full_name = f"{athlete_first_name} {athlete_last_name}"
        u.log(f"Athlete Name: {full_name}")
        return full_name
    except Exception as e:
        u.log(f"Error finding Athlete Name: {e}", "error")
        return None
    

def scrape_athlete_data(driver): #--------------- This currently scrapes the athlethe basic info and the rankings (separate linked tables)
    # Step 1: Get athlete name and profile image
    full_name = get_athlete_name(driver)
    profile_image_url = get_profile_image()

    if full_name:
        # Step 2: Insert athlete and get athlete_id
        athlete_id = db.insert_athlete("scraped_data.db", full_name, profile_image_url)

        # Step 3: Collect and store data
        click_statistics_button()
        get_world_rankings(athlete_id)
        # Add calls to get_season_bests, get_personal_bests, etc.

        u.log(f"Successfully scraped and stored data for {full_name}.")
    else:
        u.log("Failed to retrieve athlete name. Skipping data scraping.", "error")



#Testing
driver = set_up()
close_cookie_banner()
scrape_athlete_data(driver)
db.display_table("scraped_data.db", "athletes")
db.display_table("scraped_data.db", "rankings")
driver.quit()

