######### THIS ROBOT IS FOR EDUCATIONAL PURPOSES #########

import webdriver
import time
import urllib
import os

class Bot:
    def __init__(self, toSearch):
        self.imgFolder = '/home/junior/Documents/NN/datasets/FoodDevKit/Images/' + toSearch
        self.driver = webdriver.Firefox()
        url = "https://www.google.com.br/search?hl=pt-PT&site=imghp&tbm=isch&q=" + toSearch
        self.driver.get(url)

    # Let's browse the entire page first to load all the images and avoid getting stuck on "more results" button
    # When the document.body.scrollHeight stop changing is because we reached all the results
    def fetchAllImages(self):
        moreButton = self.driver.find_element_by_id("smc")
        style = moreButton.get_attribute("style")
        lastHeight = 0
        currentHeight = self.driver.execute_script("return document.body.scrollHeight")
        while lastHeight < currentHeight:
            lastHeight = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            currentHeight = self.driver.execute_script("return document.body.scrollHeight")
            style = moreButton.get_attribute("style")
            # We found the "more results" button, let's be polite and click on it =)
            if "none" not in style:
                self.driver.find_element_by_id("smb").click()
        print("All images are available now")
        return

    def createFile(self, rawData, imgCount, type):
        if not os.path.exists(self.imgFolder):
            os.makedirs(self.imgFolder)

        if not os.path.exists(self.imgFolder + "/" + type):
            os.makedirs(self.imgFolder + "/" + type)

        if rawData is None:
            print("Stopped")
        if rawData is not None:
            if 'base64' in rawData:
                dataArray = rawData.split(",")
                data = dataArray[1].decode('base64')
            else:
                data = urllib.urlopen(rawData).read()

        imgName = self.imgFolder + "/" + type + "/" + str(imgCount).zfill(7) + ".jpg"
        fd = open(imgName, 'wb')
        fd.write(data)
        fd.close()

    def saveThumbImages(self):
        elements = self.driver.find_elements_by_class_name("ivg-i")
        imgCount = 0

        for element in elements:
            img = element.find_element_by_tag_name("img")
            rawData = img.get_attribute("src")
            print(rawData)
            self.createFile(rawData, imgCount, 'thumb')
            imgCount += 1
        self.driver.close()

    def saveBigImages(self):
        elements = self.driver.find_elements_by_class_name("ivg-i")
        imgCount = 0
        prevImg = None
        srcFullImg = None

        for element in elements:
            # Click on the image to open the panel
            element.click()
            wrapperElements = self.driver.find_element_by_class_name("irc_mi")
            srcFullImg = wrapperElements.get_attribute("src")
            # Hack to avoid saving the same image
            if srcFullImg is not None and srcFullImg != prevImg:
                self.createFile(srcFullImg, imgCount, 'fullImg')
                imgCount += 1
                prevImg = srcFullImg
        self.driver.close()

# Create the object and pass what you wanna search as a parameter
bot = Bot("car")
bot.fetchAllImages()
# Save thumbnails only
bot.saveThumbImages()
# Save the image from the host, it means the image may have better resolution
bot.saveBigImages()
