import praw
import SocialMaster_utility as SM_util
import os


class Reddit:

    def __init__(self, masters, credentials=None):

        if credentials:
            self.credentials = credentials
        self.reddit = praw.Reddit(
            client_id=masters["reddit_client_id"],
            client_secret=masters["reddit_client_secret"],
            password=masters["reddit_pass"],
            user_agent="reddit browser",
            username=masters["reddit_user"],
        )
        self.sdir = os.path.dirname(__file__)

    def get_random_post_from_subreddit(self, subreddit):
        used = SM_util.get_used("reddit", self.credentials)
        for submission in self.reddit.subreddit(subreddit).hot(limit=100):
            if submission.id not in used:
                if hasattr(submission, 'post_hint'):
                    if submission.post_hint == "hosted:video":
                        if submission.over_18 is False:
                            print(submission.id)
                            video_title = submission.title
                            video_title_safe = SM_util.slugify(video_title)
                            video_url = submission.url
                            SM_util.add_used("reddit", self.credentials, submission.id)
                            return {"title": video_title, "url": video_url, "title_safe": video_title_safe}

    def download_post(self, video_url, video_name):
        file_name = f"{video_name[:100]}.mp4"
        file_path = os.path.join(self.sdir, file_name)
        sh = f'''yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best -o {file_name} {video_url}'''
        os.system(sh)
        return file_path
