import random
import traceback
import gspread
import schedule
import time

import SocialMaster_tiktok as SM_tiktok
import SocialMaster_yt as SM_yt
import SocialMaster_fb as SM_fb
import SocialMaster_ig as SM_ig
import SocialMaster_reddit as SM_reddit
import SocialMaster_utility as SM_util

from autopylogger import init_logging

logger = init_logging(log_name='log', log_directory='logs')

masters = {"insta_master_login": "", "insta_master_pass": "", "insta_master_proxy": "", "tiktok_master": "", "reddit_client_id": "", "reddit_client_secret": "", "reddit_pass": "", "reddit_user": ""}
youtube_api_key = ""


# Main Posting Function


def post(to_platform, from_platform, credentials, custom_caption, take_from_overwrite, proxy, comment=None, tags=[]):

    video_path = None
    new_post = None

    try:

        from_platform_list = from_platform.split(",")
        from_platform_split = random.choice(from_platform_list).split("$")
        from_platform = from_platform_split[0]
        from_user = from_platform_split[1]
        print(f"Posting to: {to_platform} from {from_platform} from {from_user}")

    except Exception as e:

        logger.error(f"Error: parsing platform/user: {e}\n\n{traceback.format_exc()}\n\n")
        SM_util.log_record(["FAILED (INVALID PLATFORM)", to_platform, from_platform, proxy])
        print("Error: parsing platform/user")
        return

    try:

        for i in range(5):

            try:

                if not take_from_overwrite:

                    if from_platform == "facebook":
                        fb = SM_fb.Facebook(credentials)
                        video = fb.get_random_video_from_page(from_user)
                        video_path = fb.download_post(video["url"], video["title_safe"])

                    elif from_platform == "youtube":
                        yt = SM_yt.Youtube(youtube_api_key, credentials)
                        video = yt.get_random_video_from_user(from_user)
                        video_path = yt.download_post(video["url"], video["title_safe"])

                    elif from_platform == "tiktok":
                        tiktok = SM_tiktok.TikTok(masters, credentials, proxy)
                        if from_user[0] == "%":
                            from_user = from_user[1:]
                            video = tiktok.get_random_post_from_search(from_user)
                        else:
                            video = tiktok.get_random_post_from_user(from_user)
                        video_path = tiktok.download_post(video["url"], video["title_safe"])

                    elif from_platform == "instagram":
                        if "ubuntu" in credentials or "AppData" in credentials:
                            user_for = credentials
                        else:
                            user_for = credentials.split("$")[0]
                        video = ig_master.get_random_post_from_user(from_user, user_for)
                        video_path = ig_master.download_post(video["url"], video["title_safe"])

                    elif from_platform == "reddit":
                        reddit = SM_reddit.Reddit(masters=masters, credentials=credentials)
                        video = reddit.get_random_post_from_subreddit(from_user)
                        video_path = reddit.download_post(video["url"], video["title_safe"])

                    else:
                        logger.error(f"Error: posting or getting video: {from_platform} is not valid")
                        SM_util.log_record(["FAILED (INVALID FROM)", to_platform, from_platform, from_user, proxy])
                        print(f"Error: posting or getting video: {from_platform} is not valid")
                        return

                else:

                    print(f"using overwrite video {take_from_overwrite}")

                    video = {"title": custom_caption["caption"], "url": take_from_overwrite, "title_safe": SM_util.slugify(custom_caption["caption"])}

                    if "fb.watch" in take_from_overwrite:
                        fb = SM_fb.Facebook(credentials)
                        video_path = fb.download_post(video["url"], video["title_safe"])

                    elif "youtube" in take_from_overwrite:
                        yt = SM_yt.Youtube(youtube_api_key, credentials)
                        video_path = yt.download_post(video["url"], video["title_safe"])

                    elif "tiktok" in take_from_overwrite:
                        tiktok = SM_tiktok.TikTok(masters, credentials)
                        video_path = tiktok.download_post(video["url"], video["title_safe"])

                    elif "instagram" in take_from_overwrite:
                        video_path = ig_master.download_post(video["url"], video["title_safe"])

                if custom_caption["caption_type"] == "ow":
                    video["title"] = custom_caption["caption"]
                else:
                    if video["title"] is None:
                        video["title"] = custom_caption["caption"]
                video["title"] = SM_util.title_platform_fix(video["title"], to_platform)

                if video_path:
                    break
                else:
                    print(f"Error: getting video from {from_platform} trying again...")

            except Exception as e:
                continue

        if not video_path:
            logger.error(f"Error: getting video from: {from_platform}")
            SM_util.log_record(["FAILED (GETTING VIDEO)", to_platform, from_platform, from_user, proxy])
            print(f"Error: getting video: {from_platform}")
            return

        for i in range(3):

            try:

                if to_platform == "youtube":
                    yt = SM_yt.Youtube(youtube_api_key, credentials)
                    new_post = yt.upload_post(video_path, video["title"][:98]+" ", video["title"]+" ", tags=tags)
                    if comment:
                        yt.comment(new_post, comment)

                if to_platform == "tiktok":
                    tiktok = SM_tiktok.TikTok(masters, credentials, proxy)
                    new_post = tiktok.upload(video_path, video["title"])
                    if comment:
                        tiktok.comment_on_last_post(comment)

                if to_platform == "instagram":
                    login, passw = credentials.split("$")
                    ig = SM_ig.Instagram(login, passw, proxy)
                    new_post = ig.upload(video_path, video["title"])
                    if comment:
                        ig.comment(new_post, comment)

                if new_post:
                    break
                else:
                    print(f"Error: posting video to {to_platform} trying again...")

            except Exception as e:
                continue

        if not new_post:
            logger.error(f"Error: posting video to: {to_platform}")
            SM_util.log_record(["FAILED (POSTING VIDEO)", to_platform, from_platform, from_user, proxy])
            print(f"Error: posting video: {from_platform}")
            return

        SM_util.delete(video_path)

        print(f"Successfully posted to: {to_platform} from {from_platform} from {from_user}")
        SM_util.log_record(["SUCCESS", to_platform, from_platform, from_user, proxy])

    except Exception as e:

        logger.error(f"Error: posting or getting video: {e}\n\n{traceback.format_exc()}\n\n")
        SM_util.log_record(["FAILED", to_platform, from_platform, from_user, proxy])
        print("Error: posting or getting video")

        try:
            SM_util.delete(video_path)
        except Exception as e:
            pass

    if comment:
        try:
            if to_platform == "youtube":
                yt.comment(new_post, comment)

            if to_platform == "tiktok":
                tiktok.comment_on_last_post(comment)

            if to_platform == "instagram":
                ig.comment(new_post, comment)
        except Exception as e:
            logger.error(f"Error: failed comment: {e}\n\n{traceback.format_exc()}\n\n")
            SM_util.log_record(["FAILED Comment", to_platform, from_platform, from_user, proxy])
            print("Error: commenting on video")
        else:
            SM_util.log_record(["SUCCESS Comment", to_platform, from_platform, from_user, proxy])


# Sheet handling


def get_from_sheet():
    gc = gspread.service_account(filename='service.json')
    sh = gc.open_by_key(spreadsheet_key)

    ws = sh.worksheet("TikTok")
    tiktok_accounts = ws.get("A2:G25")

    ws = sh.worksheet("YouTube")
    youtube_accounts = ws.get("A2:H25")

    ws = sh.worksheet("Instagram")
    instagram_accounts = ws.get("A2:G25")

    return tiktok_accounts, youtube_accounts, instagram_accounts


def set_masters():
    gc = gspread.service_account(filename='service.json')
    sh = gc.open_by_key(spreadsheet_key)

    ws = sh.worksheet("Master Accounts")
    master_accounts = ws.get("A2:G2")

    insta_master_login, insta_master_pass = master_accounts[0][0].split("$")
    tiktok_master = master_accounts[0][1]
    masters["insta_master_login"] = insta_master_login
    masters["insta_master_pass"] = insta_master_pass
    masters["insta_master_proxy"] = master_accounts[0][6]
    masters["tiktok_master"] = tiktok_master
    masters["reddit_client_id"] = master_accounts[0][2]
    masters["reddit_client_secret"] = master_accounts[0][3]
    masters["reddit_user"] = master_accounts[0][4]
    masters["reddit_pass"] = master_accounts[0][5]

    ig = SM_ig.Instagram(masters["insta_master_login"], masters["insta_master_pass"], masters["insta_master_proxy"])

    return ig


# Scheduling


def schedule_posts():
    schedule.clear()
    schedule.every(10).minutes.do(schedule_posts)

    try:

        tiktok_accounts, youtube_accounts, instagram_accounts = get_from_sheet()

        for account in tiktok_accounts:
            if not account:
                continue
            for c in account:
                if c is None:
                    continue
                if c == "":
                    continue
            row_credentials = account[0]
            row_take_from = account[1]
            row_post_times = account[2]
            row_custom_caption = account[3]
            row_comments = account[4]
            row_proxy = account[5]
            if len(account) == 7:
                row_take_from_overwrite = account[6]
            else:
                row_take_from_overwrite = None
            post_times = ''.join(row_post_times.split()).split(",")
            for post_time in post_times:

                custom_caption = {"caption_type": row_custom_caption.split("$")[0], "caption": random.choice(row_custom_caption.split("$")[1].split(","))}
                credentials = row_credentials
                take_from = random.choice(row_take_from.split(","))

                if row_take_from_overwrite:
                    take_from_overwrite = random.choice(account[5].split(","))
                else:
                    take_from_overwrite = False

                if row_comments != "none":
                    comments = row_comments.split(",")
                    comment = random.choice(comments)
                else:
                    comment = None

                if row_proxy != "none":
                    proxy = row_proxy
                else:
                    proxy = None
                print(f"Scheduling TIKTOK post for {post_time} on {credentials} from {take_from} with caption {custom_caption} and comment {comment} and proxy {proxy} and take_from_overwrite {take_from_overwrite}\n")
                schedule.every().day.at(post_time).do(post, "tiktok", take_from, credentials, custom_caption, take_from_overwrite, proxy, comment)
        for account in youtube_accounts:
            if not account:
                continue
            for c in account:
                if c is None:
                    continue
                if c == "":
                    continue
            row_credentials = account[0]
            row_take_from = account[1]
            row_post_times = account[2]
            row_custom_caption = account[3]
            row_tags = account[4]
            row_comments = account[5]
            row_proxy = account[6]
            if len(account) == 8:
                row_take_from_overwrite = account[7]
            else:
                row_take_from_overwrite = None
            post_times = ''.join(row_post_times.split()).split(",")
            for post_time in post_times:
                custom_caption = {"caption_type": row_custom_caption.split("$")[0], "caption": random.choice(row_custom_caption.split("$")[1].split(","))}
                credentials = row_credentials
                take_from = random.choice(row_take_from.split(","))

                if row_take_from_overwrite:
                    take_from_overwrite = random.choice(row_take_from_overwrite.split(","))
                else:
                    take_from_overwrite = False

                if row_proxy != "none":
                    proxy = row_proxy
                else:
                    proxy = None

                if row_tags != "none":
                    tags = row_tags.split(",")
                else:
                    tags = []

                if row_comments != "none":
                    comments = row_comments.split(",")
                    comment = random.choice(comments)
                else:
                    comment = None
                print(f"Scheduling YOUTUBE post for {post_time} on {credentials} from {take_from} with caption {custom_caption} and comment {comment} and proxy {proxy} and take_from_overwrite {take_from_overwrite}\n")
                schedule.every().day.at(post_time).do(post, "youtube", take_from, credentials, custom_caption, take_from_overwrite, proxy, comment, tags=tags)
        for account in instagram_accounts:
            if not account:
                continue
            for c in account:
                if c is None:
                    continue
                if c == "":
                    continue
            row_credentials = account[0]
            row_take_from = account[1]
            row_post_times = account[2]
            row_custom_caption = account[3]
            row_comments = account[4]
            row_proxy = account[5]
            if len(account) == 7:
                row_take_from_overwrite = account[6]
            else:
                row_take_from_overwrite = None
            post_times = ''.join(row_post_times.split()).split(",")
            for post_time in post_times:
                custom_caption = {"caption_type": row_custom_caption.split("$")[0], "caption": random.choice(row_custom_caption.split("$")[1].split(","))}
                credentials = row_credentials
                take_from = random.choice(row_take_from.split(","))

                if row_take_from_overwrite:
                    take_from_overwrite = random.choice(account[5].split(","))
                else:
                    take_from_overwrite = False

                if row_comments != "none":
                    comments = row_comments.split(",")
                    comment = random.choice(comments)
                else:
                    comment = None

                if row_proxy != "none":
                    proxy = row_proxy
                else:
                    proxy = None
                print(f"Scheduling INSTAGRAM post for {post_time} on {credentials} from {take_from} with caption {custom_caption} and comment {comment} and proxy {proxy} and take_from_overwrite {take_from_overwrite}\n")
                schedule.every().day.at(post_time).do(post, "instagram", take_from, credentials, custom_caption, take_from_overwrite, proxy, comment)

    except Exception as e:
        logger.error(f"Error: Something went wrong while scheduling posts, most likely an error on the spreadsheet / user error / incorrect input: {e}\n\n{traceback.format_exc()}\n\n")
        print(f"Error: Something went wrong while scheduling posts, most likely an error on the spreadsheet / user error / incorrect input: {e}\n\n{traceback.format_exc()}\n\n")
        print("Quitting in 500 seconds...")
        time.sleep(500)
        quit()


if __name__ == '__main__':

    if SM_util.setup() is False:
        print("ERROR: Please run first_time.py before running the bot.")
        logger.error(f"ERROR: Please run first_time.py before running the bot.")
        quit()
    spreadsheet_key = SM_util.get_spreadsheet_key()
    if spreadsheet_key is None:
        print("ERROR: No spreadsheet key...")
        logger.error(f"ERROR: No spreadsheet key...")
        quit()

    ig_master = set_masters()
    schedule_posts()
    schedule.every(10).minutes.do(schedule_posts)
    while True:
        schedule.run_pending()
        time.sleep(1)
