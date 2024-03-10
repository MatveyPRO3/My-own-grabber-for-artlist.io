from os import path, makedirs
from time import sleep
import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "https://artlist.io"
library_url_postfix = "/library/songs"
tab_title = "Powerful Digital Assets & Tools for Video Creators | Artlist"

start_offset_track_title = input(
    "Enter part of title of song to start from (press enter to ignore; for example if song is named 'Dog' you can type 'og', but be careful to identify right song): "
).strip()
init_js = open("js\\init.js", "r").read()
start_recording_js = "window.mediaRecorder.start();"
stop_and_save_recording_js = open("js\\stop_and_get_recording.js", "r").read()
download_recording_js = open("js\\download_recording.js", "r").read()

makedirs("tracks", exist_ok=True)

chrome_options = webdriver.ChromeOptions()

chrome_options.page_load_strategy = "eager"
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--window-size=1200,1000")
chrome_options.add_argument("--enable-usermedia-screen-capturing")
chrome_options.add_argument("--allow-http-screen-capture")
chrome_options.add_argument(f"--auto-select-tab-capture-source-by-title={tab_title}")
chrome_options.add_experimental_option(
    "prefs",
    {
        "profile.default_content_settings.popups": 0,
        "download.default_directory": path.abspath("./tracks"),
        "profile.default_content_setting_values.automatic_downloads": 1,
    },
)


driver = webdriver.Chrome(options=chrome_options)


def load_cookies():
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.execute_cdp_cmd(
            "Network.setCookie", cookie
        )  # using chrome devtools protocol to load cookies before loading site and avoid invalid cookie domain error


def save_cookies():
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))


if not path.exists("cookies.pkl"):
    print("Please login first time")
    driver.get(base_url)
    input("Press enter when done")
    save_cookies()
    print("Session saved, exiting, now restart and you will be logged in")
    exit()

load_cookies()
print("Cookies loaded")

driver.get(base_url + library_url_postfix)
driver.execute_script("""window.open("https://example.com","_blank");""")
driver.switch_to.window(driver.window_handles[0])

try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "/html/body/div[1]/div[1]/div[2]/main/div[2]/div[3]/div/div/div[1]/div/div[1]/button",
            )
        )
    )
except:
    print("It seems you have no saved songs, exiting ...")
    exit()


track_list = driver.find_element(
    By.XPATH, "/html/body/div[1]/div[1]/div[2]/main/div[2]/div[3]/div/div"
)
tracks = track_list.find_elements(By.XPATH, "./*")
print(len(tracks), "- total found songs")
skip = True if start_offset_track_title else False
skipped_tracks = 0
buttons = track_list.find_elements(By.TAG_NAME, "button")

driver.switch_to.window(driver.window_handles[1])
driver.execute_script(init_js)
sleep(1)
driver.switch_to.window(driver.window_handles[0])

for i, t in enumerate(tracks):

    track_text = t.text.split("\n")
    if len(track_text) == 4:
        title = track_text[0].strip()
        author = track_text[2].strip()
        duration_string = track_text[3].strip()
    else:
        title = track_text[0].strip()
        author = track_text[1].strip()
        duration_string = track_text[2].strip()

    print("--- Found track --- ")
    print("Title:", title)
    print("Author:", author)
    print("Duration:", duration_string)

    if skip:
        if start_offset_track_title.lower() in title.lower():
            skip = False
            print("Found offset track")
            driver.execute_script(f"window.scrollBy(0, {100*skipped_tracks})")
            sleep(1)
        else:
            print("Offset track still not found")
            skipped_tracks += 1
            continue

    button = buttons[i * 4 + 1]
    minutes, seconds = map(int, duration_string.split(":"))
    duration_seconds = minutes * 60 + seconds

    driver.switch_to.window(driver.window_handles[1])
    driver.execute_script(start_recording_js)
    sleep(0.5)  # Waiting for recording to start

    driver.switch_to.window(driver.window_handles[0])
    button.click()
    driver.execute_script("window.scrollBy(0, 100)")
    sleep(duration_seconds - 0.3)
    button.click()
    driver.switch_to.window(driver.window_handles[1])
    driver.execute_script("window.mediaRecorder.stop();")
    sleep(1)
    driver.execute_script(
        stop_and_save_recording_js
        + download_recording_js.format(filename=title + ".wav")
    )
    sleep(1)
    driver.switch_to.window(driver.window_handles[0])

    sleep(2)

input("done")
