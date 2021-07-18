from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import time

def delay(sec=5):
    time.sleep(sec)

def start_dungeon(driver, cur_main_char, rot_main_char, *rotation):
    ## change activated avatars
    if rotation:
        for id in rotation: 
            driver.find_element_by_xpath(f'//input[@name="aktiv[{id}]"]').click()
        
        # change the main character
        driver.find_element_by_xpath(f'//td/input[@value="{rot_main_char}"]').click()
        driver.find_element_by_xpath('//p/input[@name="ok"]').click()

        # request the dungeon
        # selenium.common.exceptions.NoSuchElementException: Message: Unable to locate element: //input[@name="reduce_dungeon_time"]
        driver.get(f"http://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php?session_hero_id={rot_main_char}")
        start_battle = driver.find_element_by_xpath('//input[@name="reduce_dungeon_time"]')
        start_battle.click()

        delay(60)

        driver.get(f"http://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php?session_hero_id={rot_main_char}")
        speed_up = driver.find_element_by_xpath('//input[@name="reduce_dungeon_time"]')
        next_time = speed_up.get_attribute('value')
        speed_up.click()


        ## resume to previous avatars
        for id in rotation: 
            driver.find_element_by_xpath(f'//input[@name="aktiv[{id}]"]').click()
        
        # change the main character
        driver.find_element_by_xpath(f'//td/input[@value="{cur_main_char}"]').click()
        driver.find_element_by_xpath('//p/input[@name="ok"]').click()

        return next_time[-5:]
    else: 
        print("No hero ids for rotation!!!")

# headless mode
options = webdriver.FirefoxOptions()
options.add_argument("--headless")

# Login
driver = webdriver.Firefox()
driver.get("http://delta.world-of-dungeons.org/")
Select(driver.find_element_by_id("world")).select_by_value("CD")
driver.find_element_by_xpath('//*[@id="USERNAME"]').send_keys('blackstick')
driver.find_element_by_xpath('//*[@id="PASSWORT"]').send_keys('mD8kMbRyF7giAJK', Keys.ENTER)

delay()

# Change activation
driver.get("http://delta.world-of-dungeons.org/wod/spiel/settings/heroes.php")

avatars = {'Johnny':102198, 'Blackstick':100555, 'Phaziben':103225, 'Jan':102415, 'Lios':102324, 'Frint':101489}


next_time = start_dungeon(driver, avatars['Blackstick'], avatars['Frint'], avatars['Johnny'], avatars['Blackstick'], avatars['Phaziben'], avatars['Frint'])

next_time = start_dungeon(driver, avatars['Jan'], avatars['Lios'], avatars['Blackstick'], avatars['Lios'])

# driver.quit()