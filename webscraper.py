from flask import Blueprint

webscraper_bp = Blueprint('webscraper', __name__)

# I figure here will most crucially just be a button to kick off the webscraping, which well then in the background
# do stuff in the database, and maybe then be like, okay! I'm done! Different buttons for different scrapes, or whatever you want to do
# but really could just have all your webscraping logic in another file and just have one button to call it from here,
# and then forget you're even using flask, if you want.

@webscraper_bp.route('/')
def graphs():
    return 'Main page for what will be the web scraper section!'
