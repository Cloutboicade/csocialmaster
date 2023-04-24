import os
from os.path import exists
from selenium_stealth import stealth
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import csv
import unicodedata
import re
import datetime


import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import undetected_chromedriver as uc
    from selenium import webdriver as firefox_driver


def get_chrome_session(proxy=None, headless=True):
    chrome_options = uc.ChromeOptions()
    if headless:
        chrome_options.add_argument("--headless=new")
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    driver = uc.Chrome(options=chrome_options)
    driver.set_page_load_timeout(90)
    return driver


def get_chrome_session_with_profile(profile_path, proxy=None, headless=True):
    profile_name = os.path.basename(os.path.normpath(profile_path))
    profiles_dir = os.path.dirname(os.path.normpath(profile_path))
    chrome_options = webdriver.ChromeOptions()
    if headless:
        chrome_options.add_argument("--headless=new")
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(f"--user-data-dir={profiles_dir}")
    chrome_options.add_argument(f'--profile-directory={profile_name}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chrome_options)
    driver.set_page_load_timeout(90)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver


def get_firefox_session(profile_path, headless=True, proxy=None):
    options = firefox_driver.FirefoxOptions()
    profile = firefox_driver.FirefoxProfile(profile_path)
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    if proxy:
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", proxy.split(":")[0])
        profile.set_preference("network.proxy.http_port", int(proxy.split(":")[1]))
        profile.set_preference("network.proxy.ssl", proxy.split(":")[0])
        profile.set_preference("network.proxy.ssl_port", int(proxy.split(":")[1]))
    profile.update_preferences()
    if headless:
        options.headless = True
    driver = firefox_driver.Firefox(firefox_profile=profile, options=options, executable_path="geckodriver")
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.set_page_load_timeout(90)
    driver.fullscreen_window()
    return driver


def delete(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        print(f"Tried to delete {path} but it does not exist.")


def get_used(platform, credentials):
    cwd = os.getcwd()
    used_dir = os.path.join(cwd, "used")

    if "ubuntu" in credentials:
        credentials = credentials.split("/")[-1]
    if "AppData" in credentials:
        credentials = credentials.split("\\")[-1]

    print("DEBUG", credentials)

    file_name = f"used_{platform}_{credentials}.csv"
    file_path = os.path.join(used_dir, file_name)

    if exists(file_path):
        with open(file_path, "r") as file:
            reader = csv.reader(file)
            rows = [row[0] for row in reader]
            file.close()
    else:
        rows = []
    return rows


def add_used(platform, credentials, url):
    cwd = os.getcwd()
    used_dir = os.path.join(cwd, "used")

    if "ubuntu" in credentials:
        credentials = credentials.split("/")[-1]
    if "AppData" in credentials:
        credentials = credentials.split("\\")[-1]

    print("DEBUG", credentials)

    file_name = f"used_{platform}_{credentials}.csv"
    file_path = os.path.join(used_dir, file_name)

    with open(file_path, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([url])
        file.close()


def write_cookies(credentials, cookies):
    cwd = os.getcwd()
    cookies_dir = os.path.join(cwd, "cookies")

    if "ubuntu" in credentials:
        credentials = credentials.split("/")[-1]
    if "AppData" in credentials:
        credentials = credentials.split("\\")[-1]

    file_name = f"{credentials}.txt"
    file_path = os.path.join(cookies_dir, file_name)

    with open(file_path, "w") as file:
        for cookie in cookies:
            try:
                expiry = str(cookie["expiry"])
            except KeyError:
                expiry = "0"
            file.write(cookie["name"] + "\t" +
                       cookie["value"] + "\t" +
                       cookie["path"] + "\t" +
                       cookie["domain"] + "\t" +
                       str(cookie["secure"]) + "\t" +
                       expiry + "\n")
        file.close()


def get_spreadsheet_key():
    cwd = os.getcwd()
    used_dir = os.path.join(cwd, "setup")
    file_name = "spreadsheet_key.txt"
    file_path = os.path.join(used_dir, file_name)
    if exists(file_path):
        with open(file_path, "r") as file:
            key = file.read()
            file.close()
            if key == "key":
                return None
            else:
                return key
    else:
        with open(file_path, "w") as file:
            file.write("delete_me_and_put_key")
            file.close()
            return None


def setup():
    cwd = os.getcwd()
    used_dir = os.path.join(cwd)
    file_name = "dont_delete.txt"
    file_path = os.path.join(used_dir, file_name)
    if exists(file_path):
        return True
    else:
        return False


def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def title_platform_fix(title, to_platform):
    if to_platform == "youtube":
        w = "#shorts"
    elif to_platform == "tiktok":
        w = "#fyp"
    elif to_platform == "instagram":
        w = "#reels"
    else:
        w = ""
    for ht in ["#fyp", "#reels", "#shorts", "#foryoupage", "#fy", "#foryou"]:
        if ht in title:
            return title.replace(ht, w)
    return title


def log_record(values):
    with open('logs/record.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values.insert(0, timestamp)
        writer.writerow(values)
        csvfile.close()
