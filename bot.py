from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

imgFolder = '/home/junior/Documents/NN/datasets/FoodDevKit/Images'
driver = webdriver.Firefox()
toSearch = "feijao"
url = "https://www.google.com.br/search?hl=pt-PT&site=imghp&tbm=isch&q=" + toSearch
driver.get(url)
# assert "Python" in driver.title
elem = driver.find_elements_by_class_name("ivg-i")
imgCount = 0
driver.implicitly_wait(30)  # seconds

for element in elem:
    binary_data = element.screenshot_as_png
    imgName = imgFolder + "/" + str(imgCount).zfill(7) + ".png"
    print(imgName)
    imgCount += 1
    fd = open(imgName, 'wb')
    fd.write(binary_data)
    fd.close()
    time.sleep(1)
    #  elem.clear()
# elem.send_keys("danilo viado")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
driver.close()