import instagrapi
from pathlib import Path
import os


class Instagram:

    def __init__(self, user, passw, proxy):
        proxy = f"http://{proxy}"
        self.sdir = os.path.dirname(__file__)
        self.user = user
        self.cl = instagrapi.Client()
        self.cl.set_proxy(proxy)
        if os.path.exists(f"{user}.json"):
            self.cl.load_settings(Path(f"{user}.json"))
            self.cl.login(user, passw)
        else:
            self.cl.login(user, passw)
            self.cl.dump_settings(Path(f"{user}.json"))


us = input("Enter your username: ")
pa = input("Enter your password: ")
pr = input("Enter your proxy: ")

i = Instagram(us, pa, pr)
