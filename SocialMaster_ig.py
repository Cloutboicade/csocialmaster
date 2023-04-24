import os
import SocialMaster_utility as SM_util
import requests
import instagrapi
from instagrapi import exceptions as instagrapi_exceptions
from pathlib import Path
import time


class Instagram:

    def __init__(self, user, passw, proxy):
        proxy = f"http://{proxy}"
        self.sdir = os.path.dirname(__file__)
        self.user = user
        self.passw = passw
        self.cl = instagrapi.Client()
        self.cl.set_proxy(proxy)
        if os.path.exists(f"{user}.json"):
            self.cl.load_settings(Path(f"{user}.json"))
            self.cl.login(user, passw)
        else:
            self.cl.login(user, passw)
            self.cl.dump_settings(Path(f"{user}.json"))
        self.total_posts = self.cl.user_info_by_username(self.user).media_count

    def download_post(self, video_url, video_name):
        file_name = f"{video_name[:100]}.mp4"
        file_path = os.path.join(self.sdir, file_name)

        r = requests.get(video_url)
        with open(file_name, "wb") as v:
            v.write(r.content)

        return file_path

    def get_random_post_from_user(self, username, user_for):
        used = SM_util.get_used("ig", user_for)

        user_id = int(self.cl.user_id_from_username(username))

        end_cursor = None
        for page in range(100):
            medias, end_cursor = self.cl.user_medias_paginated(user_id, 20, end_cursor=end_cursor)
            videos = [media for media in medias if media.media_type == 2]
            videos = [(v.video_url, v.caption_text, v.pk) for v in videos if v.pk not in used]
            if videos:
                v = videos[0]
                break

        SM_util.add_used("ig", user_for, v[2])

        return {"title": v[1], "url": v[0], "title_safe": SM_util.slugify(v[1])}

    def update_total_posts(self):
        self.total_posts = self.cl.user_info_by_username(self.user, use_cache=False).media_count

    def comment(self, post_id, comment):
        self.cl.media_comment(post_id, comment)

    def upload(self, file, caption):
        wait_time = 15
        relogged = False
        start_posts = self.total_posts
        for i in range(8):
            print("total_posts, start_posts", self.total_posts, start_posts)
            if self.total_posts > start_posts:
                user_id = int(self.cl.user_id_from_username(self.user))
                time.sleep(5)
                last_post = self.cl.user_medias(user_id, 1)[0]
                last_post_id = last_post.id
                return last_post_id
            try:
                new_post = self.cl.video_upload(path=file, caption=caption)
                return new_post.id
            except (requests.exceptions.ProxyError, requests.exceptions.SSLError, instagrapi_exceptions.ClientConnectionError):
                print(f"Proxy error occurred for instagram upload, trying again in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2  # Back off wait
            except instagrapi_exceptions.VideoNotUpload:
                if relogged:
                    print("Video not uploaded, relogged and still not working, giving up...")
                    break
                print(f"Login error occurred for instagram upload relogging, trying again in {wait_time} seconds...")
                self.cl.logout()
                self.cl.login(self.user, self.passw)
                time.sleep(wait_time)
                wait_time *= 2
            time.sleep(5)
            self.update_total_posts()
