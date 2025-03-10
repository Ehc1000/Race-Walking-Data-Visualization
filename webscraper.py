from flask import Blueprint, render_template
from web_scrape.scrapedDataBase import display_table  # Import the display_table function
import pandas as pd

webscraper_bp = Blueprint('webscraper', __name__)

# I figure here will most crucially just be a button to kick off the webscraping, which well then in the background
# do stuff in the database, and maybe then be like, okay! I'm done! Different buttons for different scrapes, or whatever you want to do
# but really could just have all your webscraping logic in another file and just have one button to call it from here,
# and then forget you're even using flask, if you want.


@webscraper_bp.route('/')
def web_scraper():
    # Query the database for all data
    athletes = display_table("scraped_data.db", "athletes")  # Returns a DataFrame
    rankings = display_table("scraped_data.db", "rankings")
    personal_bests = display_table("scraped_data.db", "personal_bests")
    progressions = display_table("scraped_data.db", "progressions")
    honors = display_table("scraped_data.db", "honors")

    # Convert DataFrames to lists of dictionaries for easier rendering in Jinja2
    athletes_data = athletes.to_dict(orient="records")
    rankings_data = rankings.to_dict(orient="records")
    personal_bests_data = personal_bests.to_dict(orient="records")
    progressions_data = progressions.to_dict(orient="records")
    honors_data = honors.to_dict(orient="records")

    athlete_name = athletes_data[0]['name'] if athletes_data else "Unknown Athlete"
    profile_image_url = athletes_data[0]["profile_image_url"] if athletes_data else None

    def time_to_seconds(time_str):
        """
        Convert time strings (e.g., '1:30:45' or '45:30') to seconds.
        Handles missing or invalid data gracefully by returning None.
        """
        try:
            parts = list(map(int, time_str.split(':')))
            if len(parts) == 3:  # Format: HH:MM:SS
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2:  # Format: MM:SS
                return parts[0] * 60 + parts[1]
        except Exception:
            return None
    

    if 'time' in progressions.columns:
        progressions['TimeInSeconds'] = progressions['time'].apply(time_to_seconds)
        average_times = (
            progressions.groupby('event_title')['TimeInSeconds']
            .mean()
            .reset_index()
            .rename(columns={'TimeInSeconds': 'AverageTimeInSeconds'})
        )
        # Convert seconds back to HH:MM:SS format
        def seconds_to_time(seconds):
            if seconds is None or pd.isna(seconds):
                return 'N/A'
            h, m = divmod(seconds, 3600)
            m, s = divmod(m, 60)
            return f"{int(h):02}:{int(m):02}:{int(s):02}"
        average_times['AverageTime'] = average_times['AverageTimeInSeconds'].apply(seconds_to_time)
        average_times_data = average_times[['event_title', 'AverageTime']].to_dict(orient="records")
    else:
        average_times_data = []

    # Pass the data to the template
    return render_template(
        'web_scraper.html',
        athlete_name=athlete_name,
        profile_image_url=profile_image_url,
        athletes=athletes_data,
        rankings=rankings_data,
        personal_bests=personal_bests_data,
        progressions=progressions_data,
        honors=honors_data,
        average_times=average_times_data
    )

# Command line functionality
def runs_only_when_ran_from_command_line():
    print("This function runs when the script is executed directly!")

if __name__ == '__main__':
    runs_only_when_ran_from_command_line()


