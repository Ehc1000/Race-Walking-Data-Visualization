import platform
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # Auto ChromeDriver

import constants as c
import utils as u
import scrapedDataBase as db

schema_path = os.path.join(os.path.dirname(__file__), "sql", "schema.sql")
db.init_db("scraped_data.db", schema_path)


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

def close_cookie_banner():
    """
    Handles the cookie banner on the webpage by clicking the 'Allow all cookies' button.

    Raises:
        Exception: Logs and handles any errors encountered while interacting with the cookie banner.

    Notes:
        - The cookie button is identified by its ID: "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll."
        - This function assumes that the WebDriver instance (`driver`) is already initialized and
          pointing to the appropriate webpage.
    """
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        cookie_button.click()
        u.log("Successfully clicked the 'Allow all cookies' button.")
    except Exception as e:
        u.log(f"Error closing cookie banner: {e}", "error")

def get_profile_image():
    """
    Extracts the profile image URL of the athlete from the webpage.

    Returns:
        str: The URL of the athlete's profile image if found.
        None: If the image could not be located or an error occurs.

    Raises:
        Exception: Logs and handles any exceptions encountered during the process.

    Notes:
        - The WebDriver instance (`driver`) is assumed to be initialized and pointed to
          the appropriate webpage.
        - The image is identified using an XPath query targeting the `alt` attribute.
    """
    try:
        img_element = driver.find_element(By.XPATH, "//img[@alt='Athlete']")
        img_url = img_element.get_attribute("src")
        u.log(f"Image URL: {img_url}")
    except Exception as e:
        u.log(f"Error finding image: {e}", "error")
    return img_url

def get_athlete_name():
    """
    Retrieves the athlete's full name from the webpage.

    Returns:
        str: The full name of the athlete if successfully retrieved.
        None: If the name element is not found or an error occurs.

    Raises:
        Exception: Logs and handles any exceptions encountered while locating or processing the name element.

    Notes:
        - The WebDriver instance (`driver`) must be initialized and pointed to the appropriate webpage.
        - The athlete's name is located using the `CLASS_NAME` selector "athletesBio_athletesBioTitle__3pPRL."
    """
    try:
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

def click_statistics_button():
    """
    Clicks the 'STATISTICS' button on the webpage to access the statistics section.

    Raises:
        Exception: Logs and handles any exceptions encountered while interacting with the 'STATISTICS' button.

    Notes:
        - The WebDriver instance (`driver`) is assumed to be initialized and pointed to
          the appropriate webpage.
        - The button is located using an XPath query with the text 'STATISTICS.'
    """
    try:
        statistics_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='STATISTICS']")))
        statistics_button.click()
        u.log("Successfully clicked 'STATISTICS' button.")
    except Exception as e:
        u.log(f"Error clicking 'STATISTICS' button: {e}", "error")

def get_world_rankings(athlete_id):
    """
    Scrapes and stores the athlete's world rankings for various events from the webpage.

    This function clicks the 'World rankings' button, extracts ranking data for each event,
    and stores the data in the database. It includes ranking position, ranking score, and
    the number of weeks the athlete has held the ranking.

    Parameters:
        athlete_id (int): The unique ID of the athlete in the database to associate the rankings with.

    Raises:
        Exception: Logs and handles errors that occur while interacting with the rankings section or processing data.

    Notes:
        - The WebDriver instance (`driver`) must be initialized and pointed to the appropriate webpage.
        - The function assumes that the database has a `db.insert_ranking` function to store the data.
        - Data is extracted from elements with specific class names, such as 
          "profileStatistics_rankingCardTitle__2OeiW" for titles and "athletesEventsDetails_athletesEventsDetailsLabel__6KN98"
          for labels.
    """
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

def get_personal_bests(athlete_id):
    """
    Scrapes and stores the athlete's personal bests for various events from the webpage.

    This function clicks the 'Personal bests' button, extracts data for each event,
    including performance time and score, and stores the data in the database.

    Parameters:
        athlete_id (int): The unique ID of the athlete in the database to associate the personal bests with.

    Raises:
        Exception: Logs and handles any errors encountered while interacting with the personal bests section or processing data.

    Notes:
        - The WebDriver instance (`driver`) must be initialized and pointed to the appropriate webpage.
        - The function assumes the database has a `db.insert_personal_best` function to store the data.
        - Data is extracted from elements with specific class names, such as
          "athletesTitle_athletesTitle__388RT" for event titles and "athletesEventsDetails_athletesEventsDetailsLabel__6KN98"
          for labels.
    """
    try:
        # Click the "Personal bests" button
        personal_bests_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Personal bests']"))
        )
        personal_bests_button.click()
        u.log("Successfully clicked 'Personal Bests' button.")

        # Wait for the statistics section to load
        stats_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "athletesStatisticsTable_athletesStatisticsContent__dDNOs"))
        )

        # Find event sections
        event_sections = stats_section.find_elements(By.XPATH, 
            "//div[contains(@class, 'athletesCardContainer')]"
        )

        # Iterate through each event section
        for event in event_sections:
            try:
                # Extract event title
                event_title_element = event.find_element(By.CLASS_NAME, "athletesTitle_athletesTitle__388RT")
                event_title = event_title_element.text

                # Extract labels and values
                labels = event.find_elements(By.CLASS_NAME, "athletesEventsDetails_athletesEventsDetailsLabel__6KN98")
                values = event.find_elements(By.CLASS_NAME, "athletesEventsDetails_athletesEventsDetailsValue__FrHFZ")

                performance_time = None
                performance_score = None

                # Match labels to extract specific data
                for label, value in zip(labels, values):
                    if label.text == "Performance":
                        performance_time = value.text
                    elif label.text == "Score":
                        performance_score = int(value.text)

                # Log extracted data
                u.log(f"Extracted personal best data:")
                u.log(f"  Event Title: {event_title}")
                u.log(f"  Performance Time: {performance_time}")
                u.log(f"  Performance Score: {performance_score}")

                # Insert personal bests into the database
                db.insert_personal_best("scraped_data.db", athlete_id, event_title, performance_time, performance_score)
            except Exception as inner_e:
                u.log(f"Error processing personal best for event: {inner_e}", "error")

        u.log("Successfully stored all personal bests.")
    except Exception as e:
        u.log(f"Error getting personal bests: {e}", "error")

def get_progression(athlete_id): #BUG: For some reason Row 9 of Table 1 always has missing data
    """
    Scrapes and stores the athlete's progression data from the webpage.

    This function clicks the 'Progression' button, extracts progression data for various events,
    and stores it in the database. The data includes year, time, race name, and date for each event.

    Parameters:
        athlete_id (int): The unique ID of the athlete in the database to associate the progression data with.

    Raises:
        Exception: Logs and handles any errors encountered while interacting with the progression section
                   or processing data.

    Notes:
        - The WebDriver instance (`driver`) must be initialized and pointed to the appropriate webpage.
        - The function assumes the database has a `db.insert_progression` function to store the data.
        - Data is extracted from elements with specific class names, such as
          "profileStatistics_tableBody__1w5O9" for table rows and "athletesTitle_athletesTitle__388RT"
          for table titles.
    """
    try:
        # Click the "Progression" button
        progression_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Progression']"))
        )
        progression_button.click()
        u.log("Successfully clicked 'Progression' button.")

        # Wait for the table elements to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profileStatistics_table__1o71p"))
        )

        # Labels for progression data
        labels = ["YEAR", "TIME", "RACE", "DATE"]

        # Get all global titles, skipping the first one
        global_titles = driver.find_elements(By.CLASS_NAME, "athletesTitle_athletesTitle__388RT")
        global_title_texts = [title.text for title in global_titles][1:]  # Skip the first title
        u.log(f"Global titles found on page (skipping first): {global_title_texts}")

        # Find all progression tables (excluding the last one, which is unrelated)
        tables = driver.find_elements(By.CLASS_NAME, "profileStatistics_table__1o71p")[:-1]

        # Process each table
        for table_index, table in enumerate(tables):
            table_title = global_title_texts[table_index] if table_index < len(global_title_texts) else "Unknown Title"
            u.log(f"Extracting data from table '{table_title}'...")

            table_body = table.find_element(By.CLASS_NAME, "profileStatistics_tableBody__1w5O9")
            rows = table_body.find_elements(By.TAG_NAME, "tr")

            for row_index, row in enumerate(rows):
                try:
                    # Extract data from table cells
                    td_elements = row.find_elements(By.TAG_NAME, "td")
                    row_data = {label: td.text for label, td in zip(labels, td_elements)}

                    # Parse year as an integer
                    year = int(row_data["YEAR"]) if row_data["YEAR"].isdigit() else None
                    time = row_data["TIME"]
                    race_name = row_data["RACE"]
                    date = row_data["DATE"]

                    # Log extracted data
                    u.log(f"Row {row_index + 1} Data for '{table_title}':")
                    u.log(f"  Year: {year}, Time: {time}, Race Name: {race_name}, Date: {date}")

                    # Insert progression data into the database
                    db.insert_progression(
                        "scraped_data.db", athlete_id, table_title, year, time, race_name, date
                    )
                except Exception as row_error:
                    u.log(f"Error processing row {row_index + 1} in table '{table_title}': {row_error}", "error")
    except Exception as e:
        u.log(f"Error getting progression data: {e}", "error")

def get_honours(athlete_id):
    """
    Scrapes and stores the athlete's honours data from the webpage.

    This function clicks the 'Honours' button, extracts honours data for various events,
    including placement, race title, and date, and stores the data in the database.

    Parameters:
        athlete_id (int): The unique ID of the athlete in the database to associate the honours data with.

    Raises:
        Exception: Logs and handles any errors encountered while interacting with the honours section
                   or processing data.

    Notes:
        - The WebDriver instance (`driver`) must be initialized and pointed to the appropriate webpage.
        - The function assumes the database has a `db.insert_honor` function to store the data.
        - Data is extracted from elements with specific class names, such as
          "profileStatistics_tableBody__1w5O9" for table rows and "athletesTitle_athletesTitle__388RT"
          for event titles.
        - The function skips the first and last event titles and honours table body, which are assumed to be unrelated.
    """
    try:
        # Click the "Honours" button
        honours_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Honours']"))
        )
        honours_button.click()
        u.log("Successfully clicked 'Honours' button.")

        # Wait for the honours table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "profileStatistics_tableBody__1w5O9"))
        )

        # Get event titles and table bodies
        event_titles = driver.find_elements(By.CLASS_NAME, "athletesTitle_athletesTitle__388RT")[1:-1]
        table_bodies = driver.find_elements(By.CLASS_NAME, "profileStatistics_tableBody__1w5O9")[:-1]

        # Loop through each title-table pair
        for index, (event_title, table_body) in enumerate(zip(event_titles, table_bodies), start=1):
            u.log(f"Processing Table #{index} with Event Title: {event_title.text}")

            rows = table_body.find_elements(By.TAG_NAME, "tr")

            # Process each row in the table
            for row_index, row in enumerate(rows):
                try:
                    # Extract row data
                    td_elements = row.find_elements(By.TAG_NAME, "td")
                    placement = int(td_elements[0].text) if td_elements[0].text.isdigit() else None
                    race_title = td_elements[1].text
                    date = td_elements[2].text

                    # Insert the data into the database
                    db.insert_honor(
                        "scraped_data.db",
                        athlete_id,
                        event_title.text,
                        placement,
                        race_title,
                        date
                    )

                    u.log(f"Inserted honour data for '{event_title.text}', row {row_index + 1}.")
                except Exception as row_error:
                    u.log(f"Error processing row {row_index + 1} in table '{event_title.text}': {row_error}", "error")
    except Exception as e:
        u.log(f"Error getting honours data: {e}", "error")

def scrape_athlete_data():
    """
    Scrapes and stores comprehensive athlete data from the webpage.

    This function collects basic athlete information (name and profile image) and additional
    detailed statistics, including world rankings, personal bests, progression data, and honours.
    The scraped data is stored in a database, with each category linked to the athlete's unique ID.

    Workflow:
        1. Extract athlete name and profile image.
        2. Insert the athlete into the database to retrieve a unique `athlete_id`.
        3. Scrape and store:
            - World rankings
            - Personal bests
            - Progression data
            - Honours
        4. Log progress and handle errors gracefully.

    Raises:
        Exception: Logs and handles errors that may occur during any stage of the scraping process.

    Notes:
        - The WebDriver instance (`driver`) must be initialized and pointed to the athlete's webpage.
        - The function assumes the existence of database functions to store the data, such as
          `db.insert_athlete`, `db.insert_ranking`, and similar functions for other data categories.
    """
    # Step 1: Get athlete name and profile image
    full_name = get_athlete_name()
    profile_image_url = get_profile_image()

    if full_name:
        # Step 2: Insert athlete and get athlete_id
        athlete_id = db.insert_athlete("scraped_data.db", full_name, profile_image_url)

        # Step 3: Collect and store data
        click_statistics_button()
        get_world_rankings(athlete_id)
        # get_season_bests() ??
        get_personal_bests(athlete_id)
        get_progression(athlete_id)
        #get_results() ??
        get_honours(athlete_id)

        #TODO: Implement commented functions

        u.log(f"Successfully scraped and stored data for {full_name}.")
    else:
        u.log("Failed to retrieve athlete name. Skipping data scraping.", "error")


#Testing
if __name__ == "__main__":
    driver = set_up()
    close_cookie_banner()
    scrape_athlete_data()
    db.display_table("scraped_data.db", "athletes")
    db.display_table("scraped_data.db", "rankings")
    db.display_table("scraped_data.db", "personal_bests")
    db.display_table("scraped_data.db", "progressions")
    db.display_table("scraped_data.db", "honors")
    driver.quit()