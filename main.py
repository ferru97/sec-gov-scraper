import os
from bs4 import BeautifulSoup
import logging
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By

OUTPUT_DIR = "output/"
INPUT_FILE = "input_list.txt"

def saveData(data, id):
    f = open(OUTPUT_DIR + str(id) + ".txt", "w+")
    f.write(str(data.encode('ascii', errors='ignore')).replace('\\n', ''))
    f.close()

def getSeleniumInstanceFirefox():
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"
    firefoxService = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=firefoxService)
    return driver

def getData(link, driver):
    driver.get(link)
    time.sleep(3)
    try:
        driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))
        html = driver.page_source.lower()
        driver.switch_to.default_content()
    except:
        html = driver.page_source.lower()
    soup = BeautifulSoup(html, "html.parser")
    firstSectionId = soup.find("a", text="risk factors")["href"]
    secondSectionId = soup.find("a", text="unresolved staff comments")["href"]
    start = html.find(f'id="{firstSectionId.replace("#", "")}"')
    stop = html.find(f'id="{secondSectionId.replace("#", "")}"')
    if start == -1 and stop == -1:
        start = html.find(f'name="{firstSectionId.replace("#", "")}"')
        stop = html.find(f'name="{secondSectionId.replace("#", "")}"')
    htmlData = html[start:stop-5]
    toRemove = htmlData.find("risk factors")
    finalHtml = htmlData[toRemove:]
    soup = BeautifulSoup(finalHtml, "html.parser")
    return soup.text

def run():
    df = pd.read_csv(INPUT_FILE)
    driver = getSeleniumInstanceFirefox()
    for index, row in df.iterrows():
        logging.info(f"Fetch document {index}")
        try:
            data = getData(row["link"], driver)
            saveData(data, row["id"])
        except:
            logging.info(f"Error for document with id {index}")


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    logging.info("Start!")
    run()
