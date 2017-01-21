Robot for getting images in batches from Google Images

Requirements:
- Python 2.7+
- Selenium for Python - https://pypi.python.org/pypi/selenium
- Geckodriver - https://github.com/mozilla/geckodriver/releases

How to use:
# Create the object and pass what you wanna search as a parameter
bot = Bot("car")
bot.fetchAllImages()
# Save thumbnails only
bot.saveThumbImages()
# Save the image from the host, it means the image may have better resolution
bot.saveBigImages()
