from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

# TODO: import argparse
# TODO: check if the current configration is correct or not

import re
import time

def delay(sec=5):
    """sleep to wait the loading

    Args:
        sec (int, optional): seconds to wait. Defaults to 5.
    """
    time.sleep(sec)

def sleep_time(next_time):
    """calculate the interval between battles for mini characters

    Args:
        next_time (str): gt time in string: 'xx:xx'

    Returns:
        int: time difference in seconds
    """
    cur_time = time.strftime("%H:%M", time.gmtime())
    diff = ((int(next_time[:2]) - int(cur_time[:2])) % 24 * 60 + int(next_time[-2:]) - int(cur_time[-2:])) * 60
    return diff

def wrap_time(next_time):
    """translate localtime to GM time

    Args:
        next_time (str): local time in string: 'xx:xx'

    Returns:
        str: next time in gmtime
    """
    if next_time == "99:99":
        return next_time
    else: 
        # Convert to GM time
        (hour, minu) = ((int(next_time[:2])-2)%24, next_time[-2:])
        return f"{hour:02d}:{minu}"

def find_latest(time1, time2):
    """to find the latest time to start next battle when having multiple teams to rotate

    Args:
        time1 (str): next time for team 1
        time2 (str): next time for team 2

    Returns:
        str: next time to start battle
    """
    if time1[:2] == time2[:2] :
        return time1 if int(time1[-2:]) > int(time2[-2:]) else time2
    else:
        if time1[:2] in ('00','23') and time2[:2] in ('00','23'):
            return time1 if int(time1[:2]) < int(time2[:2]) else time2
        else:
            return time1 if int(time1[:2]) > int(time2[:2]) else time2

def start_browser(headless=False):
    """start the webdriver of Firefox browser

    Args:
        headless (bool, optional): to enable headless mode. Defaults to False.

    Returns:
        webdriver: a new local session of Firefox
    """
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
    delay()
    return driver


# TODO: empty the bag and check repository
def start_dungeon(driver, cur_main_char, rot_main_char, *rotation):
    """automatically start dungeon

    Args:
        driver (webdriver): a session of firefox
        cur_main_char (int): id of the former activated character
        rot_main_char (int): id of the leader of mini team to activate

    Returns:
        str: local time to start next battle
    """
    driver.get("http://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php")
    delay()
    ## change activated avatars
    if rotation:
        for id in rotation: 
            driver.find_element_by_xpath(f'//input[@name="aktiv[{id}]"]').click()
        # change the main character
        driver.find_element_by_xpath(f'//td/input[@value="{rot_main_char}"]').click()
        driver.find_element_by_xpath('//p/input[@name="ok"]').click()

        # empty the temporary bag for each character 
        for id in rotation[len(rotation)//2:]:
            try:
                driver.get(f"http://delta.world-of-dungeons.org/wod/spiel/hero/items.php?session_hero_id={id}")
                delay()
            except Exception:
                print(f"Cannot have access to the repository of character {id}")
        # request the dungeon
        try:
            driver.get(f"http://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php?session_hero_id={rot_main_char}")
            start_battle = driver.find_element_by_xpath('//input[@name="reduce_dungeon_time"]')
            start_battle.click()
            delay(30)
        except NoSuchElementException:
            print(f"No dungeon is avaliable to start for main character {rot_main_char}")
            # TODO: deal with nothing runing
            next_time = driver.find_element_by_xpath('//span[@id="gadgetNextdungeonTime"]').get_attribute("innerHTML")[-5:]
        # wait untill the battle finished
        try:
            driver.get(f"http://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php?session_hero_id={rot_main_char}")
            speed_up = driver.find_element_by_xpath('//input[@name="reduce_dungeon_time"]')
            next_time = speed_up.get_attribute('value')[-5:]
            speed_up.click()    
        # except WebDriverException:
        #     print("Something went wrong with the website...")
        #     delay(30)
        except NoSuchElementException:
            # TODO: While finishing a time-limited dungeon, there could be no regular dungeon to start...
            print(f"No dungeon is avaliable to speed up for main character {rot_main_char}")
            try: 
                next_time = driver.find_element_by_xpath('//span[@id="gadgetNextdungeonTime"]').get_attribute("innerHTML")[-5:]
            except NoSuchElementException:
                print("I guess no dungeon is running now...")
                next_time = "99:99"
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

def record_trophies(driver, cur_char, battle_count=0):
    """record the trophies from last battle

    Args:
        driver (webdriver): a Firefox session
        cur_char (int): the id of the character to request trophies
        battle_count (int, optional): the number of battle to check. Defaults to 0 to check the latest battle.

    Returns:
        dict{int:list(str)}: a dict of trophies acquired for battles
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

def auto_rotation():
    """start the battle regularly for mini teams. IDs of rotated characters need to be assigned in this function. 
    Also, the character to record trophies is also indentified here. 
    
    Returns:
        str: GMtime to start next battle
    """

    print("****************START ROTATION****************")
    # avatar ids
    avatars = {'Shiqian':102198, 'Volo':104539, 'Jan':102415, 
                'Phaziben':103225, 'Baggins':103900, 'Frint':101489,
                'Bubu':106107, 'Artanis':106402, 'Russ':106407}

    # enable the headless browser
    driver = start_browser(True)
    # delay()

    # time1 = start_dungeon(driver, avatars['Volo'], avatars['Bubu'], avatars['Volo'], avatars['Bubu'])
    # time2 = start_dungeon(driver, avatars['Volo'], avatars['Artanis'], avatars['Volo'], avatars['Artanis'])
    # time1 = find_latest(time1, time2)
    time1 = start_dungeon(driver, avatars['Volo'], avatars['Russ'], 
                                avatars['Jan'], avatars['Shiqian'], avatars['Volo'],
                                avatars['Bubu'], avatars['Artanis'], avatars['Russ'])
    time2 = start_dungeon(driver, avatars['Volo'], avatars['Frint'], 
                                avatars['Jan'], avatars['Shiqian'], avatars['Volo'], 
                                avatars['Phaziben'], avatars['Frint'], avatars['Baggins'])
    next_time = find_latest(time1, time2)
    delay()
    # TODO: need to change activation or record the result when finishing the battle
    # print(record_trophies(driver, avatars['Frint']))
    driver.quit()
    print("****************END ROTATION****************")
    return wrap_time(next_time)  # wrapped as GM time

while True:
    print(f"Current time: {time.strftime('%m-%d %H:%M', time.gmtime())}")
    next_time = auto_rotation()
    print(f"Next dungeon will start on : {next_time}")
    delay(sleep_time(next_time) + 60)