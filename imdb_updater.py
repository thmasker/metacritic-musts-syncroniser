import os
import time
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import metacritic_scraper


def update_imdb_list(list_id: str, movie_url: str):
    metacritic_list = metacritic_scraper.get_metacritic_titles(movie_url)
    print(f"Found {len(metacritic_list)} items matching your criteria:")
    imdb_ids = []
    for m in metacritic_list:
        print(f"- {m['title']} ({m['year']}, {m['score']} score, {m['imdb_id']})")
        imdb_ids.append(m['imdb_id'])

    clear_and_refill_imdb_list(list_id, imdb_ids)


def clear_and_refill_imdb_list(list_id: str, new_ids: list[str]):
    options = uc.ChromeOptions()
    options.add_argument('--headless')  # Run without window

    # Path to the folder we cached in the YAML file
    profile_path = os.path.join(os.getcwd(), "imdb_profile")
    options.add_argument(f'--user-data-dir={profile_path}')

    # Important for Linux/GitHub environments
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_description = f"Last updated on: {now} (UTC)"

    try:
        # 1. Access the Edit Page Directly
        print("Navigating to IMDb list edit page...")
        driver.get(f"https://www.imdb.com/list/{list_id}/edit")

        # 2. Clear the list (Bulk Delete)
        select_all = wait.until(ec.element_to_be_clickable((By.ID, "check_all")))
        select_all.click()
        driver.find_element(By.ID, "delete_items").click()
        wait.until(ec.element_to_be_clickable((By.XPATH, "//input[@value='DELETE']"))).click()
        print("List cleared successfully.")
        time.sleep(3)

        # 3. Refill the list
        driver.get(f"https://www.imdb.com/list/{list_id}/")
        for mid in new_ids:
            search_box = wait.until(ec.presence_of_element_located((By.ID, "add-to-list-search")))
            search_box.clear()
            search_box.send_keys(mid)
            time.sleep(2)  # Give IMDb time to process the ID
            search_box.send_keys(Keys.ENTER)
            print(f"Added: {mid}")

        desc_box = wait.until(ec.presence_of_element_located((By.ID, "description")))
        desc_box.clear()
        desc_box.send_keys(new_description)

        # 4. Click the 'Save' button (usually at the bottom)
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()
    except Exception as e:
        print(f"An error occurred: {e}")
        driver.save_screenshot("error_state.png")
    finally:
        driver.quit()
