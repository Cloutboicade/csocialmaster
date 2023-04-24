import SocialMaster_utility as SM_util
import os
from selenium.webdriver.common.by import By


class Facebook:

    def __init__(self, credentials):
        self.sdir = os.path.dirname(__file__)
        if "\\Mozilla\\Firefox\\Profiles\\" not in credentials:
            self.credentials = credentials.split("$")[0]
        else:
            self.credentials = credentials

    def get_random_video_from_page(self, page_name):
        used = SM_util.get_used("fb", self.credentials)

        driver = SM_util.get_chrome_session()
        driver.get(f"https://www.facebook.com/{page_name}/videos/")

        videos = [v.get_attribute("href") for v in driver.find_elements(By.XPATH, f"//a[contains(@href, '{page_name}/videos')]") if "?ref=page_internal" not in v.get_attribute("href")]
        videos = [v for v in videos if v not in used]
        video_url = videos[0]

        video_title = video_url.split("/")[5]
        video_title_safe = SM_util.slugify(video_title)
        video_title = video_title.replace("-", " ")

        driver.close()

        SM_util.add_used("fb", self.credentials, video_url)

        return {"title": video_title, "url": video_url, "title_safe": video_title_safe}

    def download_post(self, video_url, video_name):
        file_name = f"{video_name[:100]}.mp4"
        file_path = os.path.join(self.sdir, file_name)
        sh = f'''yt-dlp -f b[ext=mp4] -o {file_name} {video_url}'''
        os.system(sh)
        return file_path
