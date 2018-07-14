######### THIS ROBOT IS FOR EDUCATIONAL PURPOSES #########
import urllib

from selenium import webdriver
import time
from urllib.request import urlopen
from urllib import error
from urllib.parse import urlparse
import os.path
import socket
import ssl
import  os
import json
from datetime import datetime
from multiprocessing import Pool
import argparse

class Bot:
    def __init__(self, toSearch, searchEngine):
        self.searchEngine = int(searchEngine)
        self.appPath = os.path.dirname(os.path.realpath(__file__))
        self.toSearch = toSearch
        self.imgFolder = os.path.join(self.appPath, toSearch)
        self.driver = webdriver.Firefox()
        url = None
        if self.searchEngine == 1:
            url = "https://www.google.com.br/search?hl=pt-PT&site=imghp&tbm=isch&q=" + toSearch
        elif self.searchEngine == 2:
            url = "http://www.bing.com/images/search?q=" + toSearch

        self.driver.get(url)
        self.imgList = []
        #Create directory
        if not os.path.exists(self.imgFolder):
            os.makedirs(self.imgFolder)

        if not os.path.exists(self.appPath + "/list.txt"):
            try:
                open(self.appPath + "/list.txt", 'a').close()
            except Exception as e:
                print(e)

        self.appendTxtTofile("#" + toSearch + ";" + str(datetime.now()) + "#")


    # Let's browse the entire page first to load all the images and avoid getting stuck on "more results" button
    # When the document.body.scrollHeight stop changing is because we reached all the results
    def fetchAllImages(self):
        moreButton = None
        # Google Only
        if self.searchEngine == 1:
            moreButton = self.driver.find_element_by_id("smc")
            style = moreButton.get_attribute("style")

        lastHeight = 0
        currentHeight = self.driver.execute_script("return document.body.scrollHeight")
        while lastHeight < currentHeight:
            lastHeight = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            currentHeight = self.driver.execute_script("return document.body.scrollHeight")
            # Google Only
            if self.searchEngine == 1:
                style = moreButton.get_attribute("style")
                # We found the "more results" button, let's be polite and click on it =)
                if "none" not in style:
                    self.driver.find_element_by_id("smb").click()

        print("All images of %s are available now" % str(self.toSearch))
        return

    def createFile(self, imgUrl):
        if imgUrl is None:
            return

        imgURL = urlparse(imgUrl)
        imgName = os.path.basename(imgURL.path)

        imgName = self.imgFolder + "/" + imgName

        #decoded in base64
        if 'base64' in imgUrl:
            dataArray = imgUrl.split(",")
            data = dataArray[1].decode('base64')
        else:
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                data = urlopen(imgUrl, timeout=10, context=ctx).read()
            except urllib.error.URLError as e:
                print(e)
                return
            except socket.timeout:
                print("The socket has reached timeout, skipping this file")
                return
            except ssl.SSLError as e:
                print(e)
                return
            except socket.error as e:
                print(e)
                return
            except Exception as e:
                print(e)
                return
        try:
            fd = open(imgName, 'wb')
            fd.write(data)
            fd.close()
            self.imgList.append(imgUrl)
            # print("Img Saved " + imgUrl)
        except Exception as e:
            print(e)

    def saveThumbImages(self):
        elements = self.driver.find_elements_by_class_name("ivg-i")
        imgCount = 0

        for element in elements:
            img = element.find_element_by_tag_name("img")
            rawData = img.get_attribute("src")
            print(rawData)
            self.createFile(rawData, imgCount)
            imgCount += 1
        self.driver.close()

    def saveBigImages(self):
        elements = None

        # Google
        if self.searchEngine == 1:
            elements = self.driver.find_elements_by_class_name("rg_meta")
        # BING
        elif self.searchEngine == 2:
            elements = self.driver.find_elements_by_class_name("iusc")

        if elements != None:
            numElements = len(elements)
            print(str(numElements) + " elements found")
            self.imgList = []
            count = 0
            jsonText = None
            for element in elements:
                count += 1
                print("[%s] Saving Image %s/%s" % (str(self.toSearch), str(count), numElements))
                # Google
                if self.searchEngine == 1:
                    jsonText = element.get_attribute('innerHTML')
                # BING
                elif self.searchEngine == 2:
                    jsonText = element.get_attribute('m')

                if jsonText is None:
                    print("error")
                    continue

                jsonOutput = json.loads(jsonText)
                # GOOGLE
                if self.searchEngine == 1:
                    srcFullImg = jsonOutput['ou']
                # BING
                elif self.searchEngine ==2:
                    srcFullImg = jsonOutput['murl']

                # Hack to avoid saving the same image, also checks if the image was downloaded before
                if not self.isURLonTextFile(srcFullImg):
                    self.appendTxtTofile(srcFullImg)
                    self.createFile(srcFullImg)
                else:
                    print("Skipping file %s in %s, you already have it!" % (str(count), self.toSearch))
        self.driver.close()


    def isURLonTextFile(self, url):
        imgListFile = self.appPath + "/list.txt"

        if url in open(imgListFile).read():
            return True
        return False

    # Append Url to a text file
    def appendTxtTofile(self, text):
        imgListFile = self.appPath + "/list.txt"
        fd = open(imgListFile, 'a+')
        fd.write(str(text) + "\n")
        fd.close()

    # Save the whole image list on a text file
    def saveImgList(self, imgList):
        imgListFile = self.imgFolder + "list.txt"
        fd = open(imgListFile, 'a+')

        for idx, img in enumerate(imgList):
            fd.write(str(idx) + " " + str(img) + "\n")
        fd.close()


def start(keyword):
    bot = Bot(keyword, searcher)
    bot.fetchAllImages()
    bot.saveBigImages()

def parse_args():
    parser = argparse.ArgumentParser(description="Robot for getting images in batches from Google Images.")
    parser.add_argument('-f', '--file', help="Read a txt file with keywords to be downloaded", type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    keywords=[]
    keywordFile = args.file

    searcher = input("What searcher to use GOOGLE(1) ou BING(2) ? ")
    if keywordFile == None:
        n=int(input('How many things are you looking for? '))
        for i in range(n):
            keywords.append((input('Look for: ')))
    else:
        with open(keywordFile) as file:
            keywords = file.read().splitlines()

    pool = Pool()
    pool.map(start, keywords)
