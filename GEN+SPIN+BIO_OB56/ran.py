# -*- coding: utf-8 -*-
"""
Free Fire Generator OB55 - Không Nghỉ + Auto Recovery + Auto Gacha Spin + Auto Bio
SPIN HEX fetch 100% từ Google Apps Script API (không fallback)
Format output: UID | Pass | AiD | ReGiOn | Speed
"""
import hmac, hashlib, requests, string, random, json, time, base64, codecs, uuid
import urllib3
import os
import threading
import gc
from datetime import datetime
from urllib.parse import quote
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════════════════════
#  COLOR
# ═══════════════════════════════════════════════════════
C_RESET = "\033[0m"
C_XANHLA = "\033[92m"
C_DO = "\033[91m"
C_VANG = "\033[93m"
C_XANHDUONG = "\033[96m"
C_TIM = "\033[95m"
C_TRANG = "\033[97m"

# ═══════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════
REGION = "ID"
TARGET = 2000
THREADS = 10
DELAY_MIN = 0.2
DELAY_MAX = 0.1

MAX_CONSECUTIVE_FAILS = 10
RATE_LIMIT_SLEEP = 0.5

SPIN_GACHA = True
SPIN_SLEEP_BETWEEN = 0.2
SPIN_TIMEOUT = 10
HEX_SPIN = False

REGION_HOST = "loginbp.ppmainecoonghj.com"
CLIENT_HOST = "clientbp.ppmainecoonghj.com"

SAVE_DIR = "TEST_ACCOUNTS"
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_FILE = os.path.join(SAVE_DIR, f"accounts-{REGION}.json")

API_V1_REGISTER = "https://connect.garena.com/oauth/guest/register"
API_V1_TOKEN = "https://connect.garena.com/oauth/guest/token/grant"
API_DEVICE_ID = "https://100067.msdk.garena.com/device/api/v1/android/device-id:generate"
SPIN_API_URL = "https://script.google.com/macros/s/AKfycbx-sZ_dt2wA0JjjRQ4lV7W76kone1SODCYjDAHavXWEGDArJxeReaQdtS5_ShZvD6snsg/exec"

CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
API_KEY = CLIENT_SECRET.encode()
HMAC_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")
AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

PHIENBAN = "OB55"
LITE_PHIENBAN = "2018.4.12f1"
TIMEOUT = 10

REGION_LANG = {"ME":"ar","IND":"hi","ID":"id","VN":"vi","TH":"th","BD":"bn","PK":"ur",
               "TW":"zh","EU":"en","CIS":"ru","NA":"en","SAC":"es","BR":"pt","US":"en"}

USER_AGENTS_WEB = [
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
]
USER_AGENTS_MOBILE = [
    "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
    "Dalvik/2.1.0 (Linux; U; Android 10; G011A Build/PI)",
    "Dalvik/2.1.0 (Linux; U; Android 11; SM-A515F Build/RP1A.200720.012)",
]
USER_AGENT_UNITY = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
PIXEL_UA = "GarenaMSDK/4.0.44(Pixel ;Android 10;en;US;app 1.132.1 2019121229;)"


# ═══════════════════════════════════════════════════════
#  BIO CONFIG
# ═══════════════════════════════════════════════════════
SKIP_BIO = False

LONG_BIO = {
    "ME": "I'm a new guest account from ME region!",
    "IND": "Welcome to my profile! IND server.",
    "ID": "ID Guest Account - Follow me!",
    "VN": """[B][C][88ff88]te_le: @henntaiiz
[B][C][ff0000]Nation: Vietnam's""",
    "TH": "TH Guest Account - Ready to play!",
    "BD": "BD New Player.",
    "PK": "PK Guest - Let's go!",
    "TW": """[B][C]你们在寻找什么？漂亮女孩和帅哥吗？
[b][c]FREE F[FF8800]I[FFFFFF]RE[FF8800]
[S]Te_lE:@henntaiiz""",
    "EU": "EU Guest - Playing Free Fire!",
    "CIS": "CIS Guest Account.",
    "NA": "NA Guest - Newcomer!",
    "SAC": "SAC Guest - Hola!",
    "BR": "BR Guest - Bora!",
    "US": "你好"
}


# ═══════════════════════════════════════════════════════
#  TEN REGION + KÝ TỰ REGION
# ═══════════════════════════════════════════════════════
TENREGION = {
    "ME": "FALCON", "IND": "RAJA", "ID": "GARUDA", "VN": "SPEED",
    "TH": "SING", "BD": "TIGER", "PK": "SHAHEEN", "TW": "UoU",
    "EU": "KNIGHT", "CIS": "BEAR", "NA": "EAGLE", "SAC": "TORO",
    "BR": "LOBO", "US": "WaW",
}

KYTUREGION = {
    "ME":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "⚔️🔥☠️", "Falcon", "Guest"],
    "IND": ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Raja", "Deva", "🛕🔥"],
    "ID":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Garuda", "⚡🔥"],
    "VN":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Rong", "PhuongHo", "🐉🔥"],
    "TH":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Sing", "⚔️👑"],
    "BD":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Tiger", "🔥"],
    "PK":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Shaheen", "🦅"],
    "TW":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ"],
    "EU":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Knight", "⚔️"],
    "CIS": ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Bear", "❄️"],
    "NA":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Eagle", "🦅"],
    "SAC": ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Toro", "🔥"],
    "BR":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "Lobo", "🐺"],
    "US":  ["ㅤᅟᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤ","ㅤᅟᅟㅤᅟㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ","ㅤᅟᅟㅤᅟㅤᅟᅟ","ㅤᅟ",
            "▲","ℳ","☆","°","ℛ","『","ツ","◇","༺","◆","웃","꧁","彡","★","ン",
            "•","乂","⍤","유","ヅ","Ø","♪","Ƹ","⌂","シ","⊹",
            "·","∞","♡","✦","✧","◈","▸","꧂","༻","࿐",
            "ʜ","ɪ","ᴋ","ᴍ","ɴ","ꪆ","ꪀ","』","「","」",
            "〖","〗","【","】","《","》","ッ","ジ","ヅ","亗",
            "ℳ","ℛ","Ɽ","Ƈ","Ƨ","Ƴ","Ʀ","Ƶ","⋆","⋈",
            "_-@$#", "Wolf", "Hello"],
}


# ═══════════════════════════════════════════════════════
#  BIO + NAME + PASSWORD
# ═══════════════════════════════════════════════════════
def set_bio_with_token(region: str, token: str, uid: str):
    region_key = region.upper().strip()
    bio = LONG_BIO.get(region_key, "Default Guest Bio")
    base_url = "https://improved-computing-machine-nine.vercel.app/encrypt"
    try:
        encoded_bio = quote(bio)
        full_url = f"{base_url}?token={token}&bio={encoded_bio}"
        print(f"{C_TIM}[BIO]{C_RESET} Đang đặt Bio cho UID {uid} ({region_key})...")
        response = requests.get(full_url, timeout=30)
        response.raise_for_status()
        if response.status_code == 200:
            print(f"{C_XANHLA}[BIO OK]{C_RESET} Đặt Bio thành công cho UID {uid}. Resp: {response.text[:30]}...")
        else:
            print(f"{C_DO}[BIO FAIL]{C_RESET} Lỗi khi đặt Bio (Mã: {response.status_code}).")
    except requests.RequestException as e:
        print(f"{C_DO}[BIO ERROR]{C_RESET} Lỗi kết nối API đặt Bio: {e}")
    except Exception as e:
        print(f"{C_DO}[BIO ERROR]{C_RESET} Lỗi không xác định khi đặt Bio: {e}")


def generate_random_name(region: str = None, length: int = None):
    reg = region if region else REGION
    reg = reg.upper().strip()
    prefix = TENREGION.get(reg, "User")
    groups = KYTUREGION.get(reg, ["ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"])
    if length is None:
        length = random.choice([3, 4])
    random_name_parts = []
    for _ in range(length):
        chosen_group = random.choice(groups)
        char = random.choice(chosen_group)
        random_name_parts.append(char)
    random_part = ''.join(random_name_parts).upper()
    return f"{prefix}_{random_part}"


def generate_custom_password(region, random_length=1):
    characters = string.ascii_letters + string.digits
    random_part = ''.join(random.choice(characters) for _ in range(random_length)).upper()
    return f"{random_part}"


# ═══════════════════════════════════════════════════════
#  SPIN GACHA CONFIG
# ═══════════════════════════════════════════════════════
SPIN_HOST_BY_REGION = {
    "BD":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "TW":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "VN":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "TH":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "ID":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "ME":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "IND": "https://client.ind.freefiremobile.com/PurchaseGacha",
    "PK":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "EU":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "CIS": f"https://{CLIENT_HOST}/PurchaseGacha",
    "NA":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "SAC": f"https://{CLIENT_HOST}/PurchaseGacha",
    "BR":  f"https://{CLIENT_HOST}/PurchaseGacha",
    "US":  f"https://{CLIENT_HOST}/PurchaseGacha",
}

SPIN_REWARD_DIR = "SPIN_REWARDS"

SPIN_HEX_BY_REGION = {}
SPIN_HEX_BY_REGION_EXPANDED = {}


# ═══════════════════════════════════════════════════════
#  HEX EXPANDER
# ═══════════════════════════════════════════════════════
def expand_hex_list(hex_list, region="", debug=False):
    result = []
    debug_lines = []

    for idx, item in enumerate(hex_list):
        if isinstance(item, dict):
            for k, v in item.items():
                if isinstance(k, str) and k.lower().startswith("x") and len(k) > 1:
                    try:
                        count = int(k[1:])
                    except ValueError:
                        debug_lines.append(f"    [!] '{k}' không phải cú pháp xN hợp lệ → bỏ qua")
                        continue
                    if not isinstance(v, str):
                        debug_lines.append(f"    [!] value của '{k}' không phải string → bỏ qua")
                        continue
                    debug_lines.append(f"    [{idx:02d}] {k:6s} → {v[:16]}... (lặp {count} lần)")
                    for _ in range(count):
                        result.append(v)
                else:
                    debug_lines.append(f"    [!] Dict key '{k}' không hợp lệ → bỏ qua")
        elif isinstance(item, str):
            result.append(item)
        else:
            debug_lines.append(f"    [!] Item không hợp lệ (type {type(item).__name__}) → bỏ qua")

    if debug and region:
        print(f"\n  {C_XANHDUONG}Region {region}{C_RESET}  "
              f"(config gốc: {len(hex_list)} | sau expand: {len(result)})")
        for line in debug_lines:
            print(line)
        for i, h in enumerate(result, 1):
            print(f"    {C_TRANG}[{i:02d}]{C_RESET} {h}")

    return result


# ═══════════════════════════════════════════════════════
#  FETCH HEX FROM API — RETRY 3 LẦN
# ═══════════════════════════════════════════════════════
def fetch_spin_hex_from_api(api_url=SPIN_API_URL, timeout=30, max_retries=3):
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            print(f"{C_XANHDUONG}[API]{C_RESET} Lần {attempt}/{max_retries} — Đang tải hex từ Apps Script...")
            r = requests.get(api_url, timeout=timeout, verify=False)
            r.raise_for_status()
            j = r.json()

            if j.get("status") != "success":
                last_error = f"API trả về status='{j.get('status')}' message='{j.get('message', '')}'"
                print(f"{C_DO}[API FAIL]{C_RESET} {last_error}")
                time.sleep(1)
                continue

            data = j.get("data")
            if not data:
                last_error = "API trả về data rỗng"
                print(f"{C_DO}[API FAIL]{C_RESET} {last_error}")
                time.sleep(1)
                continue

            if isinstance(data, list) and len(data) > 0:
                region_dict = data[0]
            elif isinstance(data, dict):
                region_dict = data
            else:
                last_error = "data không phải list/dict hợp lệ"
                print(f"{C_DO}[API FAIL]{C_RESET} {last_error}")
                time.sleep(1)
                continue

            if not isinstance(region_dict, dict):
                last_error = "region_dict không phải dict"
                print(f"{C_DO}[API FAIL]{C_RESET} {last_error}")
                time.sleep(1)
                continue

            cleaned = {}
            for region, hex_list in region_dict.items():
                if isinstance(hex_list, list) and len(hex_list) > 0:
                    cleaned[region.upper()] = hex_list

            if not cleaned:
                last_error = "Không có region nào có hex hợp lệ"
                print(f"{C_DO}[API FAIL]{C_RESET} {last_error}")
                time.sleep(1)
                continue

            print(f"{C_XANHLA}[API OK]{C_RESET} Đã tải {len(cleaned)} region: "
                  f"{', '.join(cleaned.keys())}")
            return cleaned

        except requests.RequestException as e:
            last_error = f"Lỗi kết nối API: {e}"
            print(f"{C_DO}[API ERROR]{C_RESET} {last_error}")
        except json.JSONDecodeError as e:
            last_error = f"API không trả về JSON hợp lệ: {e}"
            print(f"{C_DO}[API ERROR]{C_RESET} {last_error}")
        except Exception as e:
            last_error = f"Lỗi không xác định: {e}"
            print(f"{C_DO}[API ERROR]{C_RESET} {last_error}")

        if attempt < max_retries:
            print(f"{C_VANG}[RETRY]{C_RESET} Chờ 2s rồi thử lại...")
            time.sleep(1)

    raise RuntimeError(
        f"❌ KHÔNG THỂ TẢI HEX TỪ API sau {max_retries} lần thử!\n"
        f"   URL: {api_url}\n"
        f"   Lỗi cuối: {last_error}\n"
        f"   → Kiểm tra: Apps Script đã deploy public chưa? payload.js trên GitHub có đúng không?"
    )


# ═══════════════════════════════════════════════════════
#  CRYPTO
# ═══════════════════════════════════════════════════════
def encrypt_api(hex_str):
    data = bytes.fromhex(hex_str)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(data, AES.block_size)).hex()


def enc_varint(n):
    out = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)


def proto_varint(f, v):
    return enc_varint((f << 3) | 0) + enc_varint(v)


def proto_length(f, v):
    v = v.encode() if isinstance(v, str) else v
    return enc_varint((f << 3) | 2) + enc_varint(len(v)) + v


def build_proto(fields):
    pkt = bytearray()
    for f, v in fields.items():
        if isinstance(v, dict):
            pkt.extend(proto_length(f, build_proto(v)))
        elif isinstance(v, int):
            pkt.extend(proto_varint(f, v))
        elif isinstance(v, (str, bytes)):
            pkt.extend(proto_length(f, v))
    return bytes(pkt)


def parse_proto(hex_str, max_depth=5, current_depth=0):
    if current_depth > max_depth:
        return None
    try:
        data = bytes.fromhex(hex_str)
    except Exception:
        return None
    result = {}
    i = 0
    while i < len(data):
        try:
            tag = 0; shift = 0
            while i < len(data):
                b = data[i]; i += 1
                tag |= (b & 0x7F) << shift
                if not (b & 0x80): break
                shift += 7
            field = tag >> 3
            wire = tag & 7
            if field == 0: break
            if wire == 0:
                val = 0; shift = 0
                while i < len(data):
                    b = data[i]; i += 1
                    val |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
                result[field] = {"wire_type": "varint", "data": val}
            elif wire == 2:
                length = 0; shift = 0
                while i < len(data):
                    b = data[i]; i += 1
                    length |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
                if length > len(data) - i: break
                chunk = data[i:i + length]; i += length
                nested = None
                if current_depth < max_depth:
                    try: nested = parse_proto(chunk.hex(), max_depth, current_depth + 1)
                    except Exception: nested = None
                if nested and len(nested) > 0:
                    result[field] = {"wire_type": "length_delimited", "data": nested}
                else:
                    try: result[field] = {"wire_type": "string", "data": chunk.decode('utf-8')}
                    except Exception: result[field] = {"wire_type": "bytes", "data": chunk.hex()}
            elif wire == 5: i += 4
            elif wire == 1: i += 8
            else: break
        except Exception:
            break
    return result


def decode_jwt(jwt_token):
    try:
        parts = jwt_token.split('.')
        if len(parts) < 2: return None
        payload_b64 = parts[1] + '=' * ((4 - len(parts[1]) % 4) % 4)
        return json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
    except Exception:
        return None


def encode_open_id(original):
    ks = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,
          0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]
    return ''.join(chr(ord(c) ^ ks[i % len(ks)]) for i, c in enumerate(original))


def to_unicode_escaped(s):
    return ''.join(
        c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}'
        for c in s
    )


# ═══════════════════════════════════════════════════════
#  IP ROTATOR
# ═══════════════════════════════════════════════════════
import ipaddress


class IPRotator:
    REGION_IP_CIDRS = {
        "BD":  ["27.147.128.0/17", "37.111.192.0/19", "103.220.220.0/22", "172.27.237.138/22",
                "103.230.104.0/22", "119.30.32.0/19"],
        "TW":  ["1.160.0.0/12", "36.224.0.0/12", "114.24.0.0/12", "118.160.0.0/12",
                "39.8.0.0/13", "61.216.0.0/13"],
        "VN":  ["1.52.0.0/14", "14.160.0.0/11", "27.64.0.0/12",
                "42.112.0.0/13", "113.160.0.0/11"],
        "TH":  ["1.46.0.0/15", "27.55.0.0/16", "49.228.0.0/15",
                "58.8.0.0/13", "171.96.0.0/13"],
        "ID":  ["36.64.0.0/11", "101.255.0.0/16", "103.10.60.0/22",
                "111.94.0.0/15", "114.79.0.0/16"],
        "ME":  ["5.32.0.0/11", "31.9.0.0/16", "37.186.0.0/16",
                "46.19.0.0/16", "78.100.0.0/15"],
        "IND": ["1.6.0.0/13", "14.96.0.0/12", "49.32.0.0/13", "172.27.234.155/22",
                "106.192.0.0/12", "182.64.0.0/12"],
        "PK":  ["39.32.0.0/11", "111.88.0.0/13", "119.73.0.0/16",
                "175.107.0.0/16", "202.83.160.0/19"],
        "EU":  ["5.0.0.0/8", "31.0.0.0/8", "37.0.0.0/8", "46.0.0.0/8",
                "62.0.0.0/8", "77.0.0.0/8", "80.0.0.0/8"],
        "CIS": ["5.8.0.0/13", "31.128.0.0/11", "37.110.0.0/16",
                "46.0.0.0/12", "77.88.0.0/14"],
        "NA":  ["23.0.0.0/12", "24.0.0.0/12", "50.0.0.0/12",
                "64.0.0.0/12", "69.0.0.0/12"],
        "SAC": ["177.0.0.0/8", "179.0.0.0/8", "181.0.0.0/8",
                "186.0.0.0/8", "189.0.0.0/8", "200.0.0.0/8"],
        "BR":  ["177.0.0.0/8", "179.0.0.0/8", "187.0.0.0/8",
                "189.0.0.0/8", "200.0.0.0/8", "201.0.0.0/8"],
        "US":  ["3.0.0.0/8", "4.0.0.0/8", "8.0.0.0/8", "12.0.0.0/8",
                "16.0.0.0/8", "23.0.0.0/12", "24.0.0.0/12", "50.0.0.0/12"],
        "default": ["203.113.0.0/16"],
    }

    @classmethod
    def get_random_ip(cls, region):
        reg = region.upper()
        cidrs = cls.REGION_IP_CIDRS.get(reg, cls.REGION_IP_CIDRS["default"])
        cidr = random.choice(cidrs)
        try:
            net = ipaddress.IPv4Network(cidr, strict=False)
            offset = random.randint(1, net.num_addresses - 2)
            return str(ipaddress.IPv4Address(int(net.network_address) + offset))
        except Exception:
            return "203.113.1.1"

    @classmethod
    def get_ip_headers(cls, region):
        ip = cls.get_random_ip(region)
        return {
            "X-Forwarded-For": ip,
            "X-Real-IP": ip,
            "Client-IP": ip,
        }


# ═══════════════════════════════════════════════════════
#  SESSION POOL
# ═══════════════════════════════════════════════════════
_thread_local = threading.local()


def get_session():
    if not hasattr(_thread_local, 'session'):
        s = requests.Session()
        s.verify = False
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=5, pool_maxsize=5, max_retries=0
        )
        s.mount("https://", adapter)
        _thread_local.session = s
    return _thread_local.session


def reset_thread_session():
    if hasattr(_thread_local, 'session'):
        try:
            _thread_local.session.close()
        except Exception:
            pass
        delattr(_thread_local, 'session')


# ═══════════════════════════════════════════════════════
#  SAVE FILE
# ═══════════════════════════════════════════════════════
_save_lock = threading.Lock()
_saved_uids = set()


def save_account(acc_data):
    uid = str(acc_data.get("uid", ""))
    with _save_lock:
        if uid in _saved_uids:
            return False
        _saved_uids.add(uid)
        try:
            existing = []
            if os.path.exists(SAVE_FILE):
                try:
                    with open(SAVE_FILE, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                        if not isinstance(existing, list):
                            existing = []
                except Exception:
                    existing = []

            found = False
            for i, a in enumerate(existing):
                if str(a.get("uid")) == uid:
                    existing[i] = acc_data
                    found = True
                    break
            if not found:
                existing.append(acc_data)

            tmp = SAVE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            os.replace(tmp, SAVE_FILE)
            return True
        except Exception:
            return False


# ═══════════════════════════════════════════════════════
#  SPIN GACHA HELPERS
# ═══════════════════════════════════════════════════════
_spin_lock = threading.Lock()


def _spin_byte_converter(obj):
    if isinstance(obj, bytes):
        try:
            return obj.decode("utf-8")
        except Exception:
            return obj.hex()
    raise TypeError(f"Type {type(obj)} not serializable")


def _spin_extract_item_ids(reward_data):
    items = []

    if not isinstance(reward_data, dict):
        return items

    block = reward_data.get("1")

    if isinstance(block, list):
        blocks = block
    elif isinstance(block, dict):
        blocks = [block]
    else:
        blocks = []

    for b in blocks:
        if not isinstance(b, dict):
            continue
        raw_id = b.get("2")
        if raw_id is None:
            continue
        try:
            item_id = int(raw_id)
        except (TypeError, ValueError):
            continue

        quantity = None
        if "3" in b and isinstance(b["3"], int):
            quantity = b["3"]

        items.append({
            "item_id": item_id,
            "item_block": b,
            "quantity": quantity,
        })

    return items


def _spin_append_entry(file_path, entry):
    existing = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
                if not isinstance(existing, list):
                    existing = []
        except Exception:
            existing = []
    existing.append(entry)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4, ensure_ascii=False, default=_spin_byte_converter)
    except Exception:
        pass


def _spin_update_summary(summary_path, item_id, uid):
    summary = {}
    if os.path.exists(summary_path):
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
                if not isinstance(summary, dict):
                    summary = {}
        except Exception:
            summary = {}

    key = str(item_id)
    if key not in summary:
        summary[key] = {"item_id": item_id, "count": 0, "uids": []}
    summary[key]["count"] += 1
    if uid and uid not in summary[key]["uids"]:
        summary[key]["uids"].append(uid)

    try:
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4, ensure_ascii=False, default=_spin_byte_converter)
    except Exception:
        pass


def _spin_save_rewards(reward_dir, account_info, account_idx, spin_count,
                       decoded_data, raw_hex, payload_hex):
    items = _spin_extract_item_ids(decoded_data)
    uid = account_info.get("uid") if isinstance(account_info, dict) else None
    summary_path = os.path.join(reward_dir, "_summary.json")

    if not items:
        entry = dict(account_info) if isinstance(account_info, dict) else {}
        entry["account_index"] = account_idx
        entry["spin_number"] = spin_count
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        entry["payload_hex"] = payload_hex
        entry["raw_hex"] = raw_hex
        entry["reward_data"] = decoded_data
        _spin_append_entry(os.path.join(reward_dir, "_unknown.json"), entry)
        return []

    saved_ids = []
    for item in items:
        item_id = item["item_id"]
        item_block = item["item_block"]
        quantity = item.get("quantity")

        entry = dict(account_info) if isinstance(account_info, dict) else {}
        entry["account_index"] = account_idx
        entry["spin_number"] = spin_count
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        entry["item_id"] = item_id
        if quantity is not None:
            entry["quantity"] = quantity
        entry["payload_hex"] = payload_hex
        entry["raw_hex"] = raw_hex
        entry["reward_data"] = {"1": item_block}

        file_path = os.path.join(reward_dir, f"{item_id}.json")
        _spin_append_entry(file_path, entry)
        _spin_update_summary(summary_path, item_id, uid)
        saved_ids.append(item_id)

    return saved_ids


def _try_decode_proto(raw_bytes):
    try:
        import blackboxprotobuf
        decoded, _ = blackboxprotobuf.decode_message(raw_bytes)
        return decoded
    except ImportError:
        try:
            return parse_proto(raw_bytes.hex())
        except Exception:
            return {"raw_hex": raw_bytes.hex().upper()}
    except Exception as e:
        return {"decode_error": str(e), "raw_hex": raw_bytes.hex().upper()}


def spin_account(acc, account_idx):
    if not acc:
        return

    jwt_token = acc.get("token")
    if not jwt_token:
        return

    region = (acc.get("region") or REGION).upper()
    spin_url = SPIN_HOST_BY_REGION.get(region, SPIN_HOST_BY_REGION["BD"])
    hex_list = SPIN_HEX_BY_REGION_EXPANDED.get(region, SPIN_HEX_BY_REGION_EXPANDED.get("BD", []))

    if not hex_list:
        return

    reward_dir = os.path.join(SPIN_REWARD_DIR, region)
    os.makedirs(reward_dir, exist_ok=True)

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "X-GA": "v1 1",
        "ReleaseVersion": PHIENBAN,
        "Content-Type": "application/octet-stream",
        "User-Agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
    }

    uid = acc.get("uid")
    spin_count = 0

    for payload_hex in hex_list:
        spin_count += 1
        try:
            payload_bytes = bytes.fromhex(payload_hex)
        except Exception:
            continue

        try:
            resp = requests.post(spin_url, data=payload_bytes, headers=headers,
                                 verify=False, timeout=SPIN_TIMEOUT)

            if resp.status_code == 200:
                raw_response = resp.content
                raw_hex = raw_response.hex().upper()
                decoded_data = _try_decode_proto(raw_response)

                with _spin_lock:
                    saved_ids = _spin_save_rewards(reward_dir, acc, account_idx,
                                                   spin_count, decoded_data,
                                                   raw_hex, payload_hex)

                ids_str = ",".join(str(i) for i in saved_ids) if saved_ids else "?"
                print(
                    f"{C_TIM}🎰 [SPIN][{region}] UID={uid} "
                    f"payload #{spin_count}/{len(hex_list)} "
                    f"→ item_id=[{ids_str}] ✔ x{spin_count}{C_RESET}"
                )
        except Exception:
            pass

        if spin_count < len(hex_list):
            time.sleep(SPIN_SLEEP_BETWEEN)


# ═══════════════════════════════════════════════════════
#  STEPS
# ═══════════════════════════════════════════════════════
def GeT_ReGiStEr():
    password = generate_custom_password(REGION)
    data = f"password={password}&client_type=2&source=2&app_id=100067"
    signature = hmac.new(HMAC_KEY, data.encode(), hashlib.sha256).hexdigest()

    headers = {
        "User-Agent": random.choice(USER_AGENTS_WEB),
        "Authorization": "Signature " + signature,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
    }

    try:
        r = get_session().post(API_V1_REGISTER, headers=headers, data=data,
                               timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            j = r.json()
            if "uid" in j:
                return {"uid": str(j["uid"]), "password": password}
    except Exception:
        pass
    return None


def GeT_ToKeN(uid, password):
    body = {
        "uid": uid, "password": password,
        "response_type": "token", "client_type": "2", "source": "2",
        "expires_in": 1296000, "token_type": "Bearer",
        "client_secret": CLIENT_SECRET, "client_id": "100067",
        "grant_type": "guest",
    }
    headers = {
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": random.choice(USER_AGENTS_WEB),
    }

    try:
        r = get_session().post(API_V1_TOKEN, headers=headers, data=body,
                               timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            j = r.json()
            if "access_token" in j and "open_id" in j:
                return {"access_token": j["access_token"], "open_id": str(j["open_id"])}
    except Exception:
        pass
    return None


def DeViCe_Id(open_id):
    payload_json = {
        "app_id": 100067,
        "data": {
            "ad_aaid": "", "android_id": "01b05346c944b5e6",
            "android_version_release": "10", "android_version_sdk": "29",
            "brand": "Google", "build_date": "1697185398000",
            "build_display": "NHG47O release-keys", "build_id": "NHG47O",
            "cpu_abis": "arm64-v8a,armeabi-v7a,armeabi",
            "drm_id": "", "drm_vendor": "",
            "fingerprint": "Google/sailfish/sailfish:10/NHG47O/eng.build.20231013.013027:user/release-keys",
            "gcbooster_uuid": "", "hardware": "msm8996", "imei": "",
            "model": "Pixel", "key_mqs_uuid": "", "product_name": "sailfish",
            "random_uuid": str(uuid.uuid4()),
            "soc_manufacturer": "", "soc_model": ""
        }
    }
    payload = json.dumps(payload_json, separators=(',', ':'))
    signature = hmac.new(API_KEY, payload.encode(), hashlib.sha256).hexdigest()

    headers = {
        "User-Agent": PIXEL_UA,
        "Authorization": f"Signature {signature}",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Host": "100067.msdk.garena.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        **IPRotator.get_ip_headers(REGION)
    }

    try:
        r = get_session().post(API_DEVICE_ID, headers=headers, data=payload,
                               timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            j = r.json()
            if j.get("code") == 0:
                return j["data"].get("device_id", "")
    except Exception:
        pass
    return ""


def step3_generate_nickname(open_id):
    url = f"https://{REGION_HOST}/GenerateNickname"
    payload = bytes.fromhex(encrypt_api(build_proto({1: "en", 2: open_id}).hex()))

    x_ga_sv = str(int(time.time()))
    headers = {
        "Accept-Encoding": "gzip", "Authorization": "Bearer",
        "Connection": "Keep-Alive", "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue", "Host": REGION_HOST,
        "ReleaseVersion": PHIENBAN, "User-Agent": USER_AGENT_UNITY,
        "X-GA": "v1 1", "X-GA-SV": x_ga_sv, "X-Unity-Version": LITE_PHIENBAN,
        **IPRotator.get_ip_headers(REGION)
    }

    try:
        r = get_session().post(url, headers=headers, data=payload,
                               timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            return r.text.strip()
    except Exception:
        pass
    return ""


def GeT_MaJoR_ReGiStEr(access_token, open_id):
    url = f"https://{REGION_HOST}/MajorRegister"
    lang = REGION_LANG.get(REGION.upper(), "en")

    encoded_open_id = encode_open_id(open_id)
    field14 = encoded_open_id.encode('latin1')

    field22 = bytes.fromhex('474752450101010067020000a6a42db7bc5516876af3d1ba4adc337bac558af092eb3757d59d65c9323bba42c6593a48b74f33b2b5b3dc45cbd7ac02040db58f394045be4835213e12c35e5566445a5224f39d205fcf91c0e6bec797e7b3968ac00e90d7500b5865828a9d6f2091c3070f5319a130748e407ed57e6638974670ac045631b3d08c310cf1256cebcf1aed2d97d177534603d1c95d9c5d698340e797e72aa7ecc67a33122e48b0dfda050a1649586aca5e979be1fd9d99f48cd8cf59630e0ff60f67d4ed2ec4e5e7475970449a6c06329009ee0ce2567892587675781a31e4bb2774403b2f78e9811df2cb397fa602572266747704c6258077910902eb7420bcb4ab743d1610cddba9019e7867aaad3aa7ba9b04968064a409b66733f9f78c566a25ff478cba37a2ffe23203d4b05bceef826f174b0be7912d19432cc759325251fa094d70693fb672d6f9e799284081b3adb541dd8f27ef80dcf1e7f0ff30f2fd976659457ce41e175a2d6301b777981ccc16b9a8247abaab8de0867836c27de0146fe4d0e1fd39b86ba51f0b58601cfcbd7f6f3451fe4184b26ed44ac2f6f7bb4ce5d9a80f88c2cbfe7553e5ab97c8b028ae16b4f70f037753b8c229a6e5e9038fcbb9b4c2abb954894f8f2faf177bfdaab3b0ed537156633621d16b62d58ba4ebe518997c33e2304976ba6af9df7e7e34302c7910ae559c7e3d20a30d71c14f85c0e86f26291bbf18c2d9dfe9a908592eea4523e6c1e5d9bb5abfbebfccd5c4e136f9be777723e932b06c029df5125191000c90fde62a8e5f8fceb28648f0c69ec3037d09302b2ade908a20dbd42761ca449b2743fc362649e16235769d9fbd7f87cd64972b58d69c0441abb5d22ddc6ed059f7ac1bdbfaef8c60e64631809c5e08c7cb4074c8ce6170d94b411604986be4ae163a')

    gen_nick = step3_generate_nickname(open_id)
    name = generate_random_name()

    payload_fields = {
        1: name, 2: access_token, 3: open_id,
        5: 102000007, 6: 4, 7: 1, 13: 1, 14: field14,
        15: lang, 16: 1, 17: 1,
        20: "1.132.6", 21: 1, 22: field22
    }
    payload = bytes.fromhex(encrypt_api(build_proto(payload_fields).hex()))

    x_ga_sv = str(int(time.time()))
    headers = {
        "Accept-Encoding": "gzip", "Authorization": "Bearer",
        "Connection": "Keep-Alive", "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue", "Host": REGION_HOST,
        "ReleaseVersion": PHIENBAN, "User-Agent": USER_AGENT_UNITY,
        "X-GA": "v1 1", "X-GA-SV": x_ga_sv, "X-Unity-Version": LITE_PHIENBAN,
        **IPRotator.get_ip_headers(REGION)
    }

    try:
        r = get_session().post(url, headers=headers, data=payload,
                               timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            parsed = parse_proto(r.content.hex())
            account_id = None
            if parsed and 3 in parsed:
                account_id = parsed[3].get("data")
            return {"name": name, "account_id": account_id}
    except Exception:
        pass
    return None


def GeT_ChooSeNeWbie(account_id):
    if not account_id:
        return False
    url = f"https://{REGION_HOST}/ChooseNewbieChoice"
    payload = bytes.fromhex(encrypt_api(build_proto({1: int(account_id), 2: 1, 3: 3}).hex()))

    x_ga_sv = str(int(time.time()))
    headers = {
        "Accept-Encoding": "gzip", "Authorization": "Bearer",
        "Connection": "Keep-Alive", "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue", "Host": REGION_HOST,
        "ReleaseVersion": PHIENBAN, "User-Agent": USER_AGENT_UNITY,
        "X-GA": "v1 1", "X-GA-SV": x_ga_sv, "X-Unity-Version": LITE_PHIENBAN,
        **IPRotator.get_ip_headers(REGION)
    }

    try:
        r = get_session().post(url, headers=headers, data=payload,
                               timeout=TIMEOUT, verify=False)
        return r.status_code == 200
    except Exception:
        return False


def build_major_login_payload(access_token, open_id, platform_type=4):
    fields = {
        3: str(datetime.now())[:-7], 4: "free fire", 5: 1, 7: "1.132.6",
        8: "Android OS 10 / API-29 (NHG47O/eng.build.20231013.013027)",
        9: "Handheld", 10: "TelKila", 11: "WIFI",
        12: 1708, 13: 750, 14: "440", 15: "ARM64 FP ASIMD AES | 2850 | 8",
        16: 3968, 17: "Mali-G610 MC6",
        18: "OpenGL ES 3.2 v1.r32p1-01eac0.54329dee8f160f288c574caaf67bbe3f",
        19: "Google|0ecc7b3b-6c41-462e-9050-26d835e84c53",
        20: IPRotator.get_random_ip(REGION),
        21: REGION_LANG.get(REGION.upper(), "en"),
        22: open_id, 23: str(platform_type), 24: "Handheld",
        25: "Google Pixel", 26: REGION.upper(), 29: access_token, 30: 1,
        41: "TelKila", 42: "WIFI",
        57: "7428b253defc164018c604a1ebbfebdf",
        60: 109029, 61: 37616, 62: 2048, 63: 804,
        64: 37616, 65: 109029, 66: 37616, 67: 109029,
        73: 3,
        74: "/data/app/com.dts.freefireth-oiglMJkEoNJlsRci10280Q==/lib/arm64",
        76: 1,
        77: "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/com.dts.freefireth-oiglMJkEoNJlsRci10280Q==/base.apk",
        78: 3, 79: 2, 81: "64", 83: "2019121229",
        85: 3, 86: "OpenGLES2", 87: 511, 88: platform_type,
        92: 36711, 93: "android",
        94: "KqsHT8at0g7Na/G7iOeF1IpesHMf+HoePFMFFE8Tq/dSk4fIbJ1j8TdV8OAyWIVnSmD2rM6vfFMtCD8Ig7iROgDJmIMrdtcB6orwuNRpMr4MVu3D7FoTcuQdq/8EyOkRQiUrbg==",
        96: '{"cur_rate":null,"support_etc2":false}',
        97: 1, 99: str(platform_type), 100: str(platform_type),
        102: bytes.fromhex('4000434f07555f0637'),
        104: 1797, 105: 1,
        106: "https://dl.cdn.freefiremobile.com/live/ABHotUpdates/|https://dl-core.cdn.freefiremobile.com/live/ABHotUpdates/|4a0070ac356973792f002e0b25b96c3b",
        107: "c8e41b7a93f02d56e1a94c7b8203f5d1"
    }
    return bytes.fromhex(encrypt_api(build_proto(fields).hex()))


def _decode_varint(data, offset):
    result = 0; shift = 0
    while offset < len(data):
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        offset += 1
        shift += 7
        if not (byte & 0x80):
            return result, offset
    return None, offset


def _extract_field8_jwt(raw):
    o = 0
    while o < len(raw) - 1:
        idx = raw.find(b"\x42", o)
        if idx < 0: break
        length, after = _decode_varint(raw, idx + 1)
        if length is None:
            o = idx + 1; continue
        end = after + length
        if end <= len(raw) and raw[after:after + 3] == b"eyJ":
            return raw[after:end]
        o = idx + 1
    return None


def MaJoR_LoGiN(access_token, open_id, platform_type=4):
    url = f"https://{REGION_HOST}/MajorLogin"
    payload = build_major_login_payload(access_token, open_id, platform_type)

    x_ga_sv = str(int(time.time()))
    headers = {
        'X-Unity-Version': LITE_PHIENBAN, 'ReleaseVersion': PHIENBAN,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer', 'Accept': '*/*', 'Expect': '100-continue',
        'X-GA': 'v1 1', 'X-GA-SV': x_ga_sv,
        'User-Agent': USER_AGENT_UNITY, 'Host': REGION_HOST,
        'Connection': 'Keep-Alive', 'Accept-Encoding': 'deflate, gzip',
        **IPRotator.get_ip_headers(REGION)
    }

    try:
        r = get_session().post(url, headers=headers, data=payload,
                               timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            jwt_bytes = _extract_field8_jwt(r.content)
            if jwt_bytes is None:
                text = r.text
                jwt_start = text.find("eyJ")
                if jwt_start != -1:
                    jwt = text[jwt_start:]
                    dot2 = jwt.find(".", jwt.find(".") + 1)
                    if dot2 != -1:
                        jwt_bytes = jwt[:dot2 + 44].encode('utf-8', 'replace')
            if jwt_bytes:
                return jwt_bytes.decode('utf-8', 'replace')
    except Exception:
        pass
    return None


def step7_choose_region(jwt_token):
    url = f"https://{REGION_HOST}/ChooseRegion"
    try:
        body = bytes.fromhex(encrypt_api(build_proto({1: REGION.upper()}).hex()))
    except Exception:
        return 0

    headers = {
        "X-Unity-Version": LITE_PHIENBAN, "ReleaseVersion": PHIENBAN,
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Authorization": f"Bearer {jwt_token}",
        "Content-Length": "16",
        "User-Agent": random.choice(USER_AGENTS_MOBILE),
        "Host": REGION_HOST, "Connection": "Keep-Alive",
        "X-GA": "v1 1", "Accept-Encoding": "gzip",
    }

    try:
        r = get_session().post(url, headers=headers, data=body,
                               timeout=TIMEOUT, verify=False)
        return r.status_code
    except Exception:
        return 0


def build_get_login_data_payload(access_token, open_id, platform_type=4):
    fields = {
        3: str(datetime.now())[:-7], 4: "free fire", 5: 1, 7: "1.132.6",
        8: "Android OS 10 / API-29 (NHG47O/eng.build.20231013.013027)",
        9: "Handheld", 10: "TelKila", 11: "WIFI",
        12: 1708, 13: 750, 14: "440", 15: "ARM64 FP ASIMD AES | 2850 | 8",
        16: 3968, 17: "Mali-G610 MC6",
        18: "OpenGL ES 3.2 v1.r32p1-01eac0.54329dee8f160f288c574caaf67bbe3f",
        19: "Google|0ecc7b3b-6c41-462e-9050-26d835e84c53",
        20: IPRotator.get_random_ip(REGION),
        21: REGION_LANG.get(REGION.upper(), "en"),
        22: open_id, 23: str(platform_type), 24: "Handheld",
        25: "Google Pixel", 26: REGION.upper(), 29: access_token, 30: 1,
        41: "TelKila", 42: "WIFI",
        57: "7428b253defc164018c604a1ebbfebdf",
        73: 3,
        74: "/data/app/com.dts.freefireth-oiglMJkEoNJlsRci10280Q==/lib/arm64",
        76: 1,
        77: "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/com.dts.freefireth-oiglMJkEoNJlsRci10280Q==/base.apk",
        78: 3, 79: 2, 81: "64", 83: "2019121229",
        85: 3, 86: "OpenGLES2", 87: 511, 88: platform_type,
        90: bytes.fromhex('48e1baa3692044c6b0c6a16e67'), 91: "61",
        92: 36711, 93: "android",
        94: "KqsHT8at0g7Na/G7iOeF1IpesHMf+HoePFMFFE8Tq/dSk4fIbJ1j8TdV8OAyWIVnSmD2rM6vfFMtCD8Ig7iROgDJmIMrdtcB6orwuNRpMr4MVu3D7FoTcuQdq/8EyOkRQiUrbg==",
        96: '{"cur_rate":null,"support_etc2":false}', 97: 1,
        99: "0", 100: str(platform_type),
        102: bytes.fromhex('4000434f07555f0637'),
        103: 1, 104: 1797, 105: 1,
        106: "https://dl.cdn.freefiremobile.com/live/ABHotUpdates/|https://dl-core.cdn.freefiremobile.com/live/ABHotUpdates/|4a0070ac356973792f002e0b25b96c3b",
        107: "c8e41b7a93f02d56e1a94c7b8203f5d1"
    }
    return bytes.fromhex(encrypt_api(build_proto(fields).hex()))


def LoGiN_DaTa(jwt_token, access_token, open_id, platform_type=4):
    url = f"https://{CLIENT_HOST}/GetLoginData"
    payload = build_get_login_data_payload(access_token, open_id, platform_type)

    x_ga_sv = str(int(time.time()))
    headers = {
        'X-Unity-Version': LITE_PHIENBAN, 'ReleaseVersion': PHIENBAN,
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-GA': 'v1 1', 'X-GA-SV': x_ga_sv,
        'User-Agent': USER_AGENT_UNITY, 'Host': CLIENT_HOST,
        'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip',
        'Authorization': f'Bearer {jwt_token}',
        **IPRotator.get_ip_headers(REGION)
    }

    try:
        r = get_session().post(url, headers=headers, data=payload,
                               timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            return parse_proto(r.content.hex())
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════
#  CREATE ACCOUNT
# ═══════════════════════════════════════════════════════
def create_account(worker_id):
    try:
        r1 = GeT_ReGiStEr()
        if not r1: return None
        uid, password = r1['uid'], r1['password']

        r2 = GeT_ToKeN(uid, password)
        if not r2: return None
        access_token = r2['access_token']
        open_id = r2['open_id']

        device_id = DeViCe_Id(open_id)

        r3 = GeT_MaJoR_ReGiStEr(access_token, open_id)
        if not r3: return None
        name = r3['name']
        account_id_1 = r3.get('account_id')

        if account_id_1:
            GeT_ChooSeNeWbie(account_id_1)

        jwt1 = MaJoR_LoGiN(access_token, open_id)
        if not jwt1: return None

        step7_choose_region(jwt1)

        jwt2 = MaJoR_LoGiN(access_token, open_id)
        jwt_final = jwt2 if jwt2 else jwt1

        ld = LoGiN_DaTa(jwt_final, access_token, open_id)

        account_id_final = account_id_1
        if ld and '1' in ld:
            field1 = ld['1']
            if field1.get("wire_type") == "varint":
                account_id_final = str(field1.get("data"))

        nickname = name
        jp_final = decode_jwt(jwt_final)
        if jp_final and jp_final.get("nickname"):
            try:
                raw = jp_final["nickname"]
                decoded = base64.b64decode(raw)
                nk = b'1e5898ccb8dfdd921f9bdea848768b64a201'
                nickname = bytes([decoded[i] ^ nk[i % len(nk)] for i in range(len(decoded))]).decode('utf-8', errors='ignore')
            except Exception:
                pass

        if not SKIP_BIO and jwt_final:
            try:
                set_bio_with_token(REGION, jwt_final, uid)
            except Exception:
                pass

        account_obj = {
            "uid": str(uid), "password": str(password),
            "name": str(nickname),
            "account_id": str(account_id_final) if account_id_final else None,
            "region": REGION,
            "has_account_id": bool(account_id_final),
            "access_token": access_token, "open_id": open_id,
            "device_id": device_id, "token": jwt_final,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        save_account(account_obj)
        return account_obj
    except Exception:
        return None


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    # BƯỚC 1: KHỞI TẠO SPIN HEX TỪ API
    print(f"{C_XANHDUONG}{'═' * 70}{C_RESET}")
    print(f"{C_XANHDUONG}  KHỞI TẠO SPIN HEX TỪ GOOGLE APPS SCRIPT API{C_RESET}")
    print(f"{C_XANHDUONG}{'═' * 70}{C_RESET}")

    SPIN_HEX_BY_REGION = fetch_spin_hex_from_api()

    print(f"{C_XANHLA}[OK]{C_RESET} Đã nạp thành công hex cho: {list(SPIN_HEX_BY_REGION.keys())}")
    print(f"{C_XANHDUONG}{'═' * 70}{C_RESET}\n")

    SPIN_HEX_BY_REGION_EXPANDED = {
        region: expand_hex_list(hex_list, region=region if HEX_SPIN else "", debug=HEX_SPIN)
        for region, hex_list in SPIN_HEX_BY_REGION.items()
    }

    # BƯỚC 2: IN BANNER CHÍNH
    print("=" * 70)
    print("  FREE FIRE OB55 - KHÔNG NGHỈ + AUTO GACHA SPIN + AUTO BIO")
    print(f"  Region: {REGION} | Threads: {THREADS} | Target: {TARGET}")
    print(f"  Spin Gacha: {'BẬT' if SPIN_GACHA else 'TẮT'}")
    print(f"  Auto Bio  : {'BẬT' if not SKIP_BIO else 'TẮT'}")
    print(f"  Hex Spin Debug: {'BẬT' if HEX_SPIN else 'TẮT'}")
    print(f"  Hex Regions: {list(SPIN_HEX_BY_REGION.keys())}")
    print("=" * 70)

    # BƯỚC 3: CHẠY
    start_time = time.time()
    success = 0
    failed = 0

    counter_lock = threading.Lock()
    stop_flag = [False]

    def worker(worker_id):
        global success, failed

        consecutive_fails = 0

        while not stop_flag[0]:

            with counter_lock:
                if success >= TARGET:
                    return

            try:
                acc = create_account(worker_id)

                if acc:
                    consecutive_fails = 0

                    if SPIN_GACHA:
                        try:
                            spin_account(acc, worker_id)
                        except Exception:
                            pass

                    with counter_lock:
                        success += 1
                        cnt = success

                    elapsed = time.time() - start_time
                    speed = cnt / elapsed if elapsed > 0 else 0

                    uid = acc.get("uid", "None")
                    password = acc.get("password", "None")
                    aid = acc.get("account_id") or "None"

                    print(
                        f"{C_XANHLA}"
                        f"UiD = {uid} | "
                        f"Pass = {password} | "
                        f"AiD = {aid} | "
                        f"ReGiOn = {REGION} | "
                        f"{speed:.2f}/s"
                        f"{C_RESET} "
                        f"[Total: "
                        f"{C_XANHLA}{success}"
                        f"{C_RESET} "
                        f"{C_DO}{failed}"
                        f"{C_RESET}]"
                    )

                    if cnt % 20 == 0:
                        try:
                            reset_thread_session()
                        except Exception:
                            pass
                        gc.collect()

                else:
                    consecutive_fails += 1

                    with counter_lock:
                        failed += 1

                    if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                        try:
                            reset_thread_session()
                        except Exception:
                            pass
                        gc.collect()
                        time.sleep(RATE_LIMIT_SLEEP)
                        consecutive_fails = 0
                    else:
                        time.sleep(0.2)

            except Exception:
                with counter_lock:
                    failed += 1

                consecutive_fails += 1

                if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                    try:
                        reset_thread_session()
                    except Exception:
                        pass
                    gc.collect()
                    time.sleep(RATE_LIMIT_SLEEP)
                    consecutive_fails = 0
                else:
                    time.sleep(0.2)

            time.sleep(
                random.uniform(
                    DELAY_MIN,
                    DELAY_MAX
                )
            )

    threads = []

    for i in range(THREADS):
        t = threading.Thread(
            target=worker,
            args=(i + 1,),
            daemon=True
        )
        t.start()
        threads.append(t)
        time.sleep(0.05)

    try:
        while True:
            with counter_lock:
                current_success = success
            if current_success >= TARGET:
                break
            if all(
                not t.is_alive()
                for t in threads
            ):
                break
            time.sleep(0.2)

    except KeyboardInterrupt:
        print(
            f"\n{C_VANG}"
            f"[!] Dừng bởi người dùng"
            f"{C_RESET}"
        )
        stop_flag[0] = True

    stop_flag[0] = True

    for t in threads:
        t.join(timeout=2)

    elapsed = time.time() - start_time
    speed = (
        success / elapsed
        if elapsed > 0
        else 0
    )

    print()
    print("=" * 70)
    print("  KẾT QUẢ")
    print("=" * 70)

    print(f"  {C_XANHLA}✅ Thành công : {success}/{TARGET}{C_RESET}")
    print(f"  {C_DO}❌ Thất bại   : {failed}{C_RESET}")
    print(f"  ⏱  Thời gian  : {elapsed:.1f}s ({elapsed / 60:.1f} phút)")
    print(f"  ⚡ Tốc độ     : {speed:.2f} acc/s")
    print(f"  💾 File       : {os.path.abspath(SAVE_FILE)}")

    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                total_file = len(data)
            elif isinstance(data, dict):
                total_file = len(data)
            else:
                total_file = 0

            print(f"  📁 Tổng acc trong file: {total_file}")
    except Exception:
        pass

    print("=" * 70)