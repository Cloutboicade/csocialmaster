import SocialMaster_utility as SM_util
import requests
import json
import os
import random
from SocialMaster_yt_post import Upload
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time


class Youtube:

    def __init__(self, api_key, credentials):
        self.credentials = credentials
        self.api_key = api_key
        self.sdir = os.path.dirname(__file__)

    def get_random_video_from_user(self, username):
        used = SM_util.get_used("yt", self.credentials)

        r = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={username}&key={self.api_key}")
        content_details = json.loads(r.text)
        playlist_id = content_details["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        r = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=50&playlistId={playlist_id}&key={self.api_key}")
        videos = json.loads(r.text)["items"]
        videos = [(v["contentDetails"]["videoId"], v["snippet"]["title"]) for v in videos if v["contentDetails"]["videoId"] not in used]
        video = random.choice(videos)

        video_id = video[0]
        video_title = video[1]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        SM_util.add_used("yt", self.credentials, video[0])
        return {"title": video_title, "url": video_url, "title_safe": SM_util.slugify(video_title)}

    def download_post(self, video_url, video_name):
        file_name = f"{video_name[:100]}.mp4"
        file_path = os.path.join(self.sdir, file_name)
        sh = f'''yt-dlp -f b[ext=mp4] -o {file_name} {video_url}'''
        os.system(sh)
        return file_path

    def upload_post(self, file, title, description, tags):
        upload = Upload(self.credentials)
        was_uploaded, video_id = upload.upload(
            file,
            title=title,
            description=description,
            tags=tags,
            only_upload=False
        )
        if was_uploaded:
            print(f"{video_id} has been uploaded to YouTube")
        upload.close()
        return video_id

    def comment(self, video_id, comment):
        driver = SM_util.get_firefox_session(self.credentials)
        driver.get(f"https://www.youtube.com/watch?v={video_id}")
        time.sleep(5)

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)

        comment_box = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "#placeholder-area.style-scope.ytd-comment-simplebox-renderer")))
        comment_box.click()
        comment_box = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, '#contenteditable-root[contenteditable="true"][aria-label="Add a comment..."]')))

        time.sleep(5)

        for i in range(150):
            comment_box.send_keys(Keys.BACK_SPACE)
            time.sleep(random.randint(1, 3) / 10)

        time.sleep(6)

        for letter in comment:
            comment_box.send_keys(letter)
            time.sleep(random.randint(1, 3) / 10)

        time.sleep(random.randint(6, 9))

        comment_button = driver.find_element(By.XPATH, "//button[@aria-label='Comment']")

        comment_button.click()

        time.sleep(5)

        driver.get(f"https://www.youtube.com/watch?v={video_id}")

        time.sleep(5)

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)

        comment_action_menu = WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#action-menu.style-scope.ytd-comment-renderer")))
        comment_menu_button = WebDriverWait(comment_action_menu, 30).until(ec.presence_of_element_located((By.XPATH, '//button[@aria-label="Action menu"]')))
        comment_menu_button.click()

        dropdown = driver.find_element(By.CSS_SELECTOR, "ytd-menu-popup-renderer")
        time.sleep(1)
        dropdown.find_element(By.XPATH, "//yt-formatted-string[text()='Pin']").click()

        time.sleep(3)

        pin_button = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, "//yt-button-renderer[@id='confirm-button']")))
        pin_button.click()

        time.sleep(5)

        driver.quit()
