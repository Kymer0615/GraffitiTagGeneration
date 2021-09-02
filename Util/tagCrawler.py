import pandas as pd
import requests
from selenium import webdriver
from urllib.request import urlretrieve
from os import getcwd
import time
import uuid


class TagCrawler():
    def __init__(self, account, password, targetAccount):
        self.browser = webdriver.Chrome()
        self.urls = []
        self.contents = []
        self.rowCounter = 1
        self.colCounter = 1
        self.index = 0
        try:
            self.browser.get("https://www.instagram.com/")
            self.login(account, password)
            self.jump_to(targetAccount)
            self.getImg()
            # self.saveImgInfo()
            self.saveImg()
            time.sleep(1)

        finally:
            self.browser.close()

    def saveImgInfo(self):
        tempSet = set(zip(self.urls, self.contents))
        # print(self.urls)
        # print(self.contents)
        # print(tempSet)
        df = pd.read_csv(getcwd() + '/tagInfo.csv')
        for i in tempSet:
            # df2 = pd.DataFrame([[uuid.uuid4().time_mid, i[0], i[1]]], columns=['FileName', 'URL', 'Content'])
            df2 = pd.DataFrame([[self.index, i[0], i[1]]], columns=['FileName', 'URL', 'Content'])
            self.index += 1
            df = df.append(df2, ignore_index=True)
        df.to_csv(
            getcwd() + "/tagInfo.csv",
            mode='a', header=False, index=False)

    def saveImg(self):
        self.urls = set(self.urls)
        for url in self.urls:
            uuid_str = uuid.uuid4().hex
            urlretrieve(url, getcwd() + 'rawdata/%s.png' % uuid_str)

    def getImg(self):
        # todo probly to short in some case so some detection is needed
        SCROLL_PAUSE_TIME = 3

        # Get scroll height
        last_height = self.browser.execute_script("return document.body.scrollHeight")

        while True:
            self.openNestedImg()
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def openNestedImg(self):
        while True:
            if self.rowCounter != 14:
                if self.rowCounter != 15:
                    self.rowCounter = self.rowCounter % 14
                else:
                    self.rowCounter = 1
                    break
            if self.colCounter != 3:
                if self.colCounter != 4:
                    self.colCounter = self.colCounter % 3
                else:
                    self.colCounter = 1
                    self.rowCounter += 1
            print((self.rowCounter, self.colCounter))
            img = """//article/div[1]/div//div[%s]/div[%s]/a/div[1]/div[2]""" % (self.rowCounter, self.colCounter)
            try:
                time.sleep(0.4)
                self.clickByXpath(img)
                time.sleep(0.7)
            except:
                break
            self.appendCurImg()
            time.sleep(0.5)
            nextButton = """//button[@tabindex="-1" and not(@aria-hidden="true")]"""
            while True:
                try:
                    self.clickByXpath(nextButton)
                    time.sleep(0.5)
                    self.appendCurImg()
                    time.sleep(0.5)
                except:
                    break
                nextButton = """//button[@tabindex="-1" and not(@aria-hidden="true")][2]"""
            closeButton = """/html/body/div[6]/div[3]/button"""
            self.colCounter += 1

            self.clickByXpath(closeButton)

    def appendCurImg(self):
        try:
            imgSrc = self.browser.find_element_by_xpath("""//div[@role='button']/div/div/img""")
            # print(imgSrc.get_attribute("src").split(',')[-1].split(" ")[0])
            print(imgSrc.get_attribute("src"))
            self.urls.append(imgSrc.get_attribute("src"))
        except:
            return
        try:
            contentSrc = self.browser.find_element_by_xpath("""//article/div[3]/div[1]/ul/div/li/div/div/div[2]/span""")
            content = contentSrc.text.strip()
            print(content)
            self.contents.append(content)
        except:
            self.contents.append("")

    def clickByXpath(self, xpath):
        self.browser.execute_script(
            """document.evaluate('%s', document,null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();""" % xpath)

    def login(self, account, password):
        while True:
            try:
                account_input = self.browser.find_element_by_xpath(
                    """//*[@id="loginForm"]//div[@class="-MzZI"][1]//input""")
                account_input.send_keys(account)
                password_input = self.browser.find_element_by_xpath(
                    """//*[@id="loginForm"]//div[@class="-MzZI"][2]//input""")
                password_input.send_keys(password)
            except:
                time.sleep(0.01)
            else:
                break

        while True:
            try:
                submit_button = self.browser.find_element_by_xpath("""//*[@id="loginForm"]//button[@type="submit"]""")
                submit_button.click()
            except:
                time.sleep(0.01)
            else:
                break

        while True:
            try:
                saveData_button = self.browser.find_element_by_xpath(
                    """//*[@id="react-root"]/section/main/div/div/div/section/div/button""")
                saveData_button.click()
            except:
                time.sleep(0.01)
            else:
                break
        for i in range(3):
            try:
                saveData_button = self.browser.find_element_by_xpath(
                    """/html/body/div[6]/div/div/div/div[3]/button[1]""")
                saveData_button.click()
            except:
                time.sleep(0.1)
            # else:
            #     break

    def jump_to(self, username):
        for i in range(3):
            try:
                self.browser.get("https://www.instagram.com/%s/" % username)
            except:
                time.sleep(0.02)
            # else:
            #     break


def main():
    t = TagCrawler()


if __name__ == "__main__":
    main()
