import os
import json
import time
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from . import database
from . import config

songAlias = database.songAlias
songData = database.songData

def timestamp_to_str(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d-%H-%M-%S")

def calculate_level(xp):
    xp_ups = [100, 120, 140, 160, 180, 200, 220, 240, 300, 210]
    xp_ups += [220, 230, 240, 250, 260, 270, 280, 290, 300, 250]
    xp_ups += [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]
    xp_ups += [360, 370, 380, 390, 400, 410, 420, 430, 440, 450]
    xp_ups += [460, 470, 480, 490, 500]
    level = 0
    for xp_up in xp_ups:
        xp -= xp_up
        if xp < 0:
            break
        level += 1
    if xp > 0:
        level += xp / 500
    return level

def getCanUsePlayerAvatar(avatarID):
    return str(avatarID) if os.path.exists(f"./img/avatar/{str(avatarID)}.png") else "player"
def getCanUsePlayerBackground(BackgroundID):
    return str(BackgroundID).replace("background_", "")

def getCanUsePlayerCharacter(characterID):
    return str(characterID).replace("character_", "")

def calculate_song_rating(song_score, rating_real, song_is_cleared):
    next_rating_point = 0.001

    if song_score >= 1010000:
        song_rating = rating_real + 3.7
        next_point_score = 1010000
    elif 1008000 <= song_score < 1010000:
        song_rating = rating_real + 3.4 + (song_score - 1008000) / 10000
        next_point_score = (song_rating + next_rating_point - rating_real - 3.4) * 10000 + 1008000
    elif 1004000 <= song_score < 1008000:
        song_rating = rating_real + 2.4 + (song_score - 1004000) / 4000
        next_point_score = (song_rating + next_rating_point - rating_real - 2.4) * 4000 + 1004000
    elif 1000000 <= song_score < 1004000:
        song_rating = rating_real + 2.0 + (song_score - 1000000) / 10000
        next_point_score = (song_rating + next_rating_point - rating_real - 2.0) * 10000 + 1000000
    elif 980000 <= song_score < 1000000:
        song_rating = rating_real + 1.0 + (song_score - 980000) / 20000
        next_point_score = (song_rating + next_rating_point - rating_real - 1.0) * 20000 + 980000
    elif 950000 <= song_score < 980000:
        song_rating = rating_real + 0.0 + (song_score - 950000) / 30000
        next_point_score = (song_rating + next_rating_point - rating_real - 0.0) * 30000 + 950000
    elif 900000 <= song_score < 950000:
        song_rating = rating_real - 1.0 + (song_score - 900000) / 50000
        next_point_score = (song_rating + next_rating_point - rating_real + 1.0) * 50000 + 900000
    elif 500000 <= song_score < 900000:
        song_rating = rating_real - 5.0 + (song_score - 500000) / 100000
        next_point_score = (song_rating + next_rating_point - rating_real + 5.0) * 100000 + 500000
    else:
        song_rating = 0
        next_point_score = 500000
        
    if song_rating < 0: song_rating = 0
        
    if not song_is_cleared:
        song_rating = min(6, song_rating)
        
    next_point_score -= song_score
    if next_point_score + song_score > 1010000: next_point_score = 1010000 - song_score
    
    return song_rating, next_point_score

def shortIDToUserProfile(shortID):
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)
    for objectID in os.listdir(config.savesDir):
        for filename in os.listdir(f"{config.savesDir}/{objectID}/userdata"):
            if shortID in filename:
                for userID in users:
                    if users[userID]["objectId"] == objectID: return users[userID]
    return {"server": "", "objectId": "", "sign": "", "session": ""}

def userProfileToShortID(userProfile):
    userProfile["objectId"]
    
    if os.path.exists(f"{config.savesDir}/{userProfile['objectId']}"):
        for filename in os.listdir(f"{config.savesDir}/{userProfile['objectId']}/userdata"):
            return filename.split("-")[1].split(".")[0]
    return ""

def compress_image(image_path, max_size_mb=9.5, quality=95):
    max_size_bytes = max_size_mb * 1024 * 1024
    if os.path.getsize(image_path) > max_size_bytes:
        with Image.open(image_path) as img:
            img.thumbnail((img.width * 0.9, img.height * 0.9), Image.LANCZOS)
            img_format = img.format
            if img_format not in ["JPEG", "JPG", "PNG"]:
                return image_path
            if img.mode in ["RGBA", "P"]:
                img = img.convert("RGB")
            output_path = image_path.rsplit(".", 1)[0] + f".{time.time()}.webp"
            try:
                img.save(output_path, format="WEBP", quality=quality, method=6)
                if os.path.getsize(output_path) <= max_size_bytes:
                    return output_path
            except:
                ...
            output_path = image_path.rsplit(".", 1)[0] + f".{time.time()}.jpg"
            img.save(output_path, format="JPEG", quality=quality, optimize=True)
    else:
        return image_path
    if os.path.getsize(output_path) > max_size_bytes:
        return compress_image(output_path, max_size_mb=max_size_mb, quality=quality-20)
    else:
        return output_path

def render_html_to_jpg(window_size, sleep_time, html_path=None, isHTML=False, html_data=None):    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--allow-file-access-from-files")
    options.add_argument("--enable-local-file-accesses")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(window_size[0], window_size[1])
    
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    
    if isHTML:
        html_path = f"{config.tmpDir}/{time.time()}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_data)
        
    abs_html_path = os.path.abspath(html_path)
    file_url = f"file://{abs_html_path}"

    driver.get(file_url)
    time.sleep(sleep_time)
    
    total_height = driver.execute_script("return document.body.scrollHeight") + 200
    driver.set_window_size(window_size[0], total_height)
    driver.execute_script("document.body.style.overflow = 'hidden';")

    screenshot_path = f"{config.tmpDir}/{time.time()}.png"
    driver.save_screenshot(screenshot_path)
    driver.quit()
    
    return compress_image(screenshot_path, 9.5)

def draw_bar_chart(data, labels, save_path, title):
    plt.figure(figsize=(12, 6))
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    x = np.arange(len(labels))
    plt.bar(x, data, color='cornflowerblue', alpha=0.8, label="Rating")
    p = np.polyfit(x, data, 1)
    line_fit = np.polyval(p, x)
    plt.plot(x, line_fit, color='green', linestyle='--', linewidth=2, label="趋势")
    line_data = [v / 2 for v in data]
    plt.plot(x, line_data, marker='o', color='red', linestyle='-', linewidth=2, markersize=5, label="折线")
    for i, v in enumerate(data):
        plt.text(i, v + 0.2, f"{v:.3f}", ha='center', fontsize=8, rotation=90)
    for i, v in enumerate(line_data):
        plt.text(i, v, f" {v * 2:.3f}", ha='center', fontsize=8, color='red', verticalalignment='bottom', rotation=90)
    plt.xticks(x, labels, rotation=45, ha='right', fontsize=8)
    plt.ylabel("Rating")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path

def draw_line_datatime(data, save_path, title, y_title):
    dates = [datetime.fromtimestamp(ts) for ts, _ in data]
    ys = [y for _, y in data]
    plt.figure(figsize=(15, 5))
    plt.plot(dates, ys, marker='o', linestyle='-', color='b')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()
    plt.title(title)
    plt.xlabel('Date and Time')
    plt.ylabel(y_title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path


def sorted_json_files(folder_path, reverse=True, needTimestamp=False):
    # reverse=True 新的文件在前
    # reverse=False 旧的文件在前
    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    sorted_files = sorted(files, key=lambda f: float(f.split("-")[0] if "-" in f else f.split(".")[0]), reverse=reverse)
    if not needTimestamp:
        return [f"{folder_path}/{file}" for file in sorted_files]
    k = []
    for file in sorted_files:
        k.append([float(file.split(".")[0]), f"{folder_path}/{file}"])
    return k

def safe_open(file_path, mode="r", *args, **kwargs):
    folder = os.path.dirname(file_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    return open(file_path, mode, *args, **kwargs)
