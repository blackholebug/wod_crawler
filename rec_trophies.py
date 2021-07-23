from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
import time
import json

def delay(sec=5):
    time.sleep(sec)

def start_browser(headless=False):
    # headless mode
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    # login
    driver = webdriver.Firefox(firefox_options=options) if headless else webdriver.Firefox()
    driver.get("http://delta.world-of-dungeons.org/")
    Select(driver.find_element_by_id("world")).select_by_value("CD")
    driver.find_element_by_xpath('//*[@id="USERNAME"]').send_keys('blackstick')
    driver.find_element_by_xpath('//*[@id="PASSWORT"]').send_keys('mD8kMbRyF7giAJK', Keys.ENTER)
    delay(5)
    return driver

def record_trophies(driver, cur_char, battle_count=0):
    """record the trophies from last battle

    Args:
        driver (webdriver): a Firefox session
        cur_char (int): the id of the character to request trophies
        battle_count (int, optional): the number of battle to check. Defaults to 0 to check the latest battle.

    Returns:
        list(str): a list of trophies acquired
    """
    driver.get(f"http://delta.world-of-dungeons.org/wod/spiel/dungeon/report.php?session_hero_id={cur_char}")
    # TODO: add database for recording
    driver.find_element_by_xpath(f"//input[@name='items[{battle_count}]']").click()
    soup = BeautifulSoup(driver.page_source, "lxml")
    # find unique items
    findings = []
    for char in soup.find_all('h3', text='战利品'):
        for i in char.parent.find_all('a', class_="report rep_uni item_unique"):
            findings.append(i.string)
    # TODO: find items in wishlist
    # TODO: find completion of each character
    return {battle_count:findings}


avatars = {'Johnny':102198, 'Blackstick':100555, 'Phaziben':103225, 'Jan':102415, 'Baggins':103900, 'Frint':101489}
driver = start_browser(True)
trophies = record_trophies(driver, avatars['Jan'], 0)
driver.quit()

with open('./trophies.log', 'w', encoding='utf-8') as f:
    json.dump(trophies, f, indent=2)
with open('./trophies.log', 'r', encoding='utf-8') as f:
    raw_text = json.load(f)

print(raw_text)