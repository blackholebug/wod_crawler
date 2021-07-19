from enum import auto
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

# import argparse
import sys
import time

def delay(sec=5):
    time.sleep(sec)

def sleep_time(next_time):
    cur_time = time.strftime("%H:%M", time.gmtime())
    diff = ((int(next_time[:2]) - int(cur_time[:2])) % 24 * 60 + int(next_time[-2:]) - int(cur_time[-2:])) * 60
    return diff

def wrap_time(next_time):
    # Convert to GM time
    (hour, minu) = ((int(next_time[:2])-2)%24, next_time[-2:])
    return f"{hour:02d}:{minu}"

def start_browser(headless=False):
    # headless mode
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    # login
    driver = webdriver.Firefox(options) if headless else webdriver.Firefox()
    driver.get("http://delta.world-of-dungeons.org/")
    Select(driver.find_element_by_id("world")).select_by_value("CD")
    driver.find_element_by_xpath('//*[@id="USERNAME"]').send_keys('blackstick')
    driver.find_element_by_xpath('//*[@id="PASSWORT"]').send_keys('mD8kMbRyF7giAJK', Keys.ENTER)
    return driver

def start_dungeon(driver, cur_main_char, rot_main_char, *rotation):

    driver.get("http://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php")
    ## change activated avatars
    if rotation:
        for id in rotation: 
            driver.find_element_by_xpath(f'//input[@name="aktiv[{id}]"]').click()
        # change the main character
        driver.find_element_by_xpath(f'//td/input[@value="{rot_main_char}"]').click()
        driver.find_element_by_xpath('//p/input[@name="ok"]').click()

        # request the dungeon
        try:
            driver.get(f"http://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php?session_hero_id={rot_main_char}")
        except NoSuchElementException:
            print(f"No dungeon is avaliable to start for main character {rot_main_char}")
            next_time = driver.find_element_by_xpath('//span[@id="gadgetNextdungeonTime"]').get_attribute("innerHTML")
        else:    
            start_battle = driver.find_element_by_xpath('//input[@name="reduce_dungeon_time"]')
            start_battle.click()
            delay(60)
        try:
            driver.get(f"http://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php?session_hero_id={rot_main_char}")
        except NoSuchElementException:
            print(f"No dungeon is avaliable to speed up for main character {rot_main_char}")
            next_time = driver.find_element_by_xpath('//span[@id="gadgetNextdungeonTime"]').get_attribute("innerHTML")
        else:
            speed_up = driver.find_element_by_xpath('//input[@name="reduce_dungeon_time"]')
            next_time = speed_up.get_attribute('value')[-5:]
            speed_up.click()
        finally:
            # resume to previous avatars
            for id in rotation: 
                driver.find_element_by_xpath(f'//input[@name="aktiv[{id}]"]').click()
            # change the main character
            driver.find_element_by_xpath(f'//td/input[@value="{cur_main_char}"]').click()
            driver.find_element_by_xpath('//p/input[@name="ok"]').click()
        return next_time
    else: 
        print("No hero ids for rotation!!!")

def auto_rotation():

    # avatar ids
    avatars = {'Johnny':102198, 'Blackstick':100555, 'Phaziben':103225, 'Jan':102415, 'Lios':102324, 'Frint':101489}

    driver = start_browser()
    # delay()
    next_time = start_dungeon(driver, avatars['Blackstick'], avatars['Frint'], avatars['Johnny'], avatars['Blackstick'], avatars['Phaziben'], avatars['Frint'])
    delay()
    next_time = start_dungeon(driver, avatars['Jan'], avatars['Lios'], avatars['Blackstick'], avatars['Lios'])
    delay()
    # driver.quit()
    return wrap_time(next_time)  # wrapped as GM time

while True:
    next_time = auto_rotation()
    print(f"next dungeon will start on : {next_time}")
    delay(sleep_time(next_time) + 60)