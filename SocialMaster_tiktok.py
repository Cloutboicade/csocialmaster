import time
import os
import requests
import random
import SocialMaster_utility as SM_util
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import json


def title_fix(title):
    if "Replying to @" in title:
        return " ".join(title.split("@")[1].split(" ")[1:])
    else:
        return title


class TikTok:

    def __init__(self, masters, credentials, proxy):
        self.masters = masters
        self.credentials = credentials
        self.sdir = os.path.dirname(__file__)
        self.proxy = proxy

    def download_post(self, post_url, video_name):
        file_name = f"{video_name[:100]}.mp4"
        file_path = os.path.join(self.sdir, file_name)
        sh = f'''yt-dlp -f b[ext=mp4] -o {file_name} "{post_url}"'''
        os.system(sh)

        return file_path

    def get_random_post_from_user(self, username):
        used = SM_util.get_used("tiktok", self.credentials)

        driver = SM_util.get_chrome_session()
        driver.get(f"https://www.tiktok.com/@{username}/")

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, "//div[contains(@data-e2e, 'user-post-item')]")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        while True:
            posts_all = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='user-post-item']")
            posts = [(post.find_element(By.TAG_NAME, "a").get_attribute("href"), post.find_element(By.TAG_NAME, "img").get_attribute("alt")) for post in posts_all if post.find_element(By.TAG_NAME, "a").get_attribute("href") not in used]
            if not posts:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            else:
                break

        post = posts[0]
        post_url = post[0]
        post_title = post[1]

        if post_title == "":
            post_title = post_url.split("/")[-1]
        else:
            post_title = title_fix(post_title)

        SM_util.add_used("tiktok", self.credentials, post_url)

        driver.quit()

        return {"title": post_title, "url": post_url, "title_safe": SM_util.slugify(post_title)}

    def get_random_post_from_search(self, search_term):
        used = SM_util.get_used("tiktok", self.credentials)

        driver = SM_util.get_chrome_session_with_profile(self.credentials, proxy=self.proxy)
        driver.get(f"https://www.tiktok.com/search/video?q={search_term}")

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, "//div[contains(@data-e2e, 'search_video-item')]")))

        posts = driver.find_elements(By.XPATH, "//div[contains(@data-e2e, 'search_video-item')]")
        posts = [(post.find_element(By.TAG_NAME, "a").get_attribute("href"), post.find_element(By.TAG_NAME, "img").get_attribute("alt")) for post in posts if post.find_element(By.TAG_NAME, "a").get_attribute("href") not in used]
        post = random.choice(posts)

        post_url = post[0]
        post_title = post[1]

        if post_title == "":
            post_title = None
            post_title_safe = SM_util.slugify(post_url.split("/")[-1])
        else:
            post_title = title_fix(post_title)
            post_title_safe = SM_util.slugify(post_title)

        SM_util.add_used("tiktok", self.credentials, post_url)

        driver.quit()

        return {"title": post_title, "url": post_url, "title_safe": post_title_safe}

    def comment_on_last_post(self, comment):
        driver = SM_util.get_chrome_session_with_profile(self.credentials, proxy=self.proxy)
        driver.get("https://www.tiktok.com/")
        sigi_state_element = driver.find_element(By.ID, "SIGI_STATE")
        sigi_state_json = sigi_state_element.get_attribute("innerHTML")
        info = json.loads(sigi_state_json)
        username = info["AppContext"]["appContext"]["user"]["uniqueId"]
        driver.get(f"https://www.tiktok.com/@{username}")

        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//div[contains(@data-e2e, 'user-post-item')]")))

        while True:
            posts_all = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='user-post-item']")
            posts = [(post.find_element(By.TAG_NAME, "a").get_attribute("href"),
                      post.find_element(By.TAG_NAME, "img").get_attribute("alt")) for post in posts_all if
                     post.find_element(By.TAG_NAME, "a").get_attribute("href") not in []]
            if not posts:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            else:
                break

        latest_post_url = posts[0][0]
        driver.get(latest_post_url)

        comment_box = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, "//div[@class='notranslate public-DraftEditor-content' and @contenteditable='true']")))

        time.sleep(5)

        for i in range(150):
            comment_box.send_keys(Keys.BACK_SPACE)
            time.sleep(random.randint(1, 3) / 10)

        time.sleep(6)

        for letter in comment:
            comment_box.send_keys(letter)
            time.sleep(random.randint(1, 3) / 10)

        time.sleep(random.randint(6, 9))

        comment_box.send_keys(Keys.ENTER)

        time.sleep(10)

        driver.quit()

    def upload(self, file, caption):
        driver = SM_util.get_chrome_session_with_profile(self.credentials, proxy=self.proxy)
        driver.get("https://www.tiktok.com/upload?lang=en")

        iframe = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)

        time.sleep(2)

        select_file = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"][accept="video/*"]')))

        time.sleep(5)

        select_file.send_keys(file)

        time.sleep(5)

        caption_box = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"]')))

        time.sleep(5)

        for i in range(150):
            caption_box.send_keys(Keys.BACK_SPACE)
            time.sleep(random.randint(1, 3) / 10)

        time.sleep(6)

        for letter in caption[:151]:
            caption_box.send_keys(letter)
            time.sleep(random.randint(1, 3) / 10)

        time.sleep(random.randint(6, 9))

        post_button_div = WebDriverWait(driver, 120).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "div.btn-post")))
        post_button = post_button_div.find_element(By.TAG_NAME, "button")

        time.sleep(5)

        post_button.click()

        time.sleep(60)

        driver.quit()

        return True
