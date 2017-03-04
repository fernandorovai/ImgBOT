######### THIS ROBOT IS FOR EDUCATIONAL PURPOSES #########

from selenium import webdriver
import time
import urllib2
import os
import os.path

class Bot:
    def __init__(self, toSearch):
        self.imgFolder = '/home/junior/Documents/NN/datasets/FoodDevKit/Images/' + toSearch
        self.driver = webdriver.Firefox()
        url = "https://www.google.com.br/search?hl=pt-PT&site=imghp&tbm=isch&q=" + toSearch
        self.driver.get(url)
        self.imgList = []

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
        if rawData is None:
            return

        if not os.path.exists(self.imgFolder):
            os.makedirs(self.imgFolder)

        if not os.path.exists(self.imgFolder + "/" + type):
            os.makedirs(self.imgFolder + "/" + type)

        imgName = self.imgFolder + "/" + type + "/" + str(imgCount).zfill(7) + ".jpg"

        #decoded in base64
        if 'base64' in rawData:
            dataArray = rawData.split(",")
            data = dataArray[1].decode('base64')
        else:
            try:
                data = urllib2.urlopen(rawData, timeout=10).read()
            except urllib2.URLError, e:
                print("Something wrong happened trying to download the image")
                print(e)
                return

        fd = open(imgName, 'wb')
        fd.write(data)
        fd.close()
        self.imgList.append(rawData)
        print("Img Saved " + rawData)

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
        self.imgList = []

        for element in elements:
            # Click on the image to open the panel
            element.click()
            wrapperElements = self.driver.find_elements_by_class_name("irc_mi")
            for item in wrapperElements:
                srcFullImg = item.get_attribute("src")
                if srcFullImg is None:
                    continue
                # Hack to avoid saving the same image
                if srcFullImg not in self.imgList:
                    self.createFile(srcFullImg, len(self.imgList), 'fullImg')

        self.driver.close()
        self.saveImgList(self.imgList)

    def saveImgList(self, imgList):
        imgListFile = self.imgFolder + "list.txt"
        fd = open(imgListFile, 'a+')

        for idx, img in enumerate(imgList):
            fd.write(str(idx) + " " + str(img) + "\n")
        fd.close()

# Create the object and pass what you wanna search as a parameter
bot = Bot("prato arroz e feijao")
bot.fetchAllImages()
# Save thumbnails only
#bot.saveThumbImages()
# Save the image from the host, it means the image may have better resolution
bot.saveBigImages()
