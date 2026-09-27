# -*- coding: utf-8 -*-
"""
Free Fire Generator OB55 - TẠO 100 ACC LIÊN TIẾP
Multi-thread + Auto Save + Full Pipeline
"""
import hmac, hashlib, requests, string, random, json, time, base64, codecs, uuid
import urllib3
import os
import threading
import gc
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════
REGION = "BD"               # VN TH ID IND ME BR CIS SAC BD PK TW
TARGET = 100                # Số acc cần tạo
THREADS = 10                # Số luồng song song
DELAY_MIN = 0.1
DELAY_MAX = 0.3
SAVE_EVERY = 5              # Save file mỗi N acc

REGION_HOST = "loginbp.ppmainecoonghj.com"
CLIENT_HOST = "clientbp.ppmainecoonghj.com"

SAVE_DIR = "TEST_ACCOUNTS"
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_FILE = os.path.join(SAVE_DIR, f"accounts-{REGION}.json")

API_V1_REGISTER = "https://connect.garena.com/oauth/guest/register"
API_V1_TOKEN = "https://connect.garena.com/oauth/guest/token/grant"
API_DEVICE_ID = "https://100067.msdk.garena.com/device/api/v1/android/device-id:generate"

CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
API_KEY = CLIENT_SECRET.encode()
HMAC_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")
AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

PHIENBAN = "OB55"
LITE_PHIENBAN = "2018.4.12f1"
TIMEOUT = 15

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


# ═══════════════════════════════════════════════════════
#  IP ROTATOR
# ═══════════════════════════════════════════════════════
import ipaddress


class IPRotator:
    REGION_IP_CIDRS = {
        "TW": ["1.160.0.0/12", "36.224.0.0/12", "114.24.0.0/12", "118.160.0.0/12"],
        "VN": ["1.52.0.0/14", "14.160.0.0/11", "27.64.0.0/12"],
        "TH": ["1.46.0.0/15", "27.55.0.0/16", "49.228.0.0/15"],
        "BD": ["27.147.128.0/17", "37.111.192.0/19", "103.220.220.0/22"],
        "ID": ["36.64.0.0/11", "101.255.0.0/16", "103.10.60.0/22"],
        "IND": ["1.6.0.0/15", "1.38.0.0/15", "14.96.0.0/15"],
    }

    @classmethod
    def get_random_ip(cls, region):
        reg = region.upper()
        cidrs = cls.REGION_IP_CIDRS.get(reg, ["203.113.0.0/16"])
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
#  SAVE FILE (thread-safe)
# ═══════════════════════════════════════════════════════
_save_lock = threading.Lock()
_saved_uids = set()


def save_account(acc_data):
    """Lưu account vào file JSON (merge, thread-safe)"""
    global _saved_uids
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

            # Check trùng
            found = False
            for i, a in enumerate(existing):
                if str(a.get("uid")) == uid:
                    existing[i] = acc_data
                    found = True
                    break

            if not found:
                existing.append(acc_data)

            # Ghi file atomic
            tmp = SAVE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            os.replace(tmp, SAVE_FILE)
            return True
        except Exception as e:
            return False


# ═══════════════════════════════════════════════════════
#  STEPS
# ═══════════════════════════════════════════════════════
def step1_register():
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    data = f"password={password}&client_type=2&source=2&app_id=100067"
    signature = hmac.new(HMAC_KEY, data.encode(), hashlib.sha256).hexdigest()

    headers = {
        "User-Agent": random.choice(USER_AGENTS_WEB),
        "Authorization": "Signature " + signature,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
    }

    for attempt in range(3):
        try:
            r = requests.post(API_V1_REGISTER, headers=headers, data=data,
                              timeout=TIMEOUT, verify=False)
            if r.status_code == 200:
                j = r.json()
                if "uid" in j:
                    return {"uid": str(j["uid"]), "password": password}
            time.sleep(0.3)
        except Exception:
            time.sleep(0.3)
    return None


def step2_token(uid, password):
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

    for attempt in range(3):
        try:
            r = requests.post(API_V1_TOKEN, headers=headers, data=body,
                              timeout=TIMEOUT, verify=False)
            if r.status_code == 200:
                j = r.json()
                if "access_token" in j and "open_id" in j:
                    return {"access_token": j["access_token"], "open_id": str(j["open_id"])}
            time.sleep(0.3)
        except Exception:
            time.sleep(0.3)
    return None


def step2b_device_id(open_id):
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
        r = requests.post(API_DEVICE_ID, headers=headers, data=payload,
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
        r = requests.post(url, headers=headers, data=payload,
                          timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            return r.text.strip()
    except Exception:
        pass
    return ""


def step4_major_register(access_token, open_id):
    url = f"https://{REGION_HOST}/MajorRegister"
    lang = REGION_LANG.get(REGION.upper(), "en")

    encoded_open_id = encode_open_id(open_id)
    field14 = encoded_open_id.encode('latin1')

    field22 = bytes.fromhex('474752450101010067020000a6a42db7bc5516876af3d1ba4adc337bac558af092eb3757d59d65c9323bba42c6593a48b74f33b2b5b3dc45cbd7ac02040db58f394045be4835213e12c35e5566445a5224f39d205fcf91c0e6bec797e7b3968ac00e90d7500b5865828a9d6f2091c3070f5319a130748e407ed57e6638974670ac045631b3d08c310cf1256cebcf1aed2d97d177534603d1c95d9c5d698340e797e72aa7ecc67a33122e48b0dfda050a1649586aca5e979be1fd9d99f48cd8cf59630e0ff60f67d4ed2ec4e5e7475970449a6c06329009ee0ce2567892587675781a31e4bb2774403b2f78e9811df2cb397fa602572266747704c6258077910902eb7420bcb4ab743d1610cddba9019e7867aaad3aa7ba9b04968064a409b66733f9f78c566a25ff478cba37a2ffe23203d4b05bceef826f174b0be7912d19432cc759325251fa094d70693fb672d6f9e799284081b3adb541dd8f27ef80dcf1e7f0ff30f2fd976659457ce41e175a2d6301b777981ccc16b9a8247abaab8de0867836c27de0146fe4d0e1fd39b86ba51f0b58601cfcbd7f6f3451fe4184b26ed44ac2f6f7bb4ce5d9a80f88c2cbfe7553e5ab97c8b028ae16b4f70f037753b8c229a6e5e9038fcbb9b4c2abb954894f8f2faf177bfdaab3b0ed537156633621d16b62d58ba4ebe518997c33e2304976ba6af9df7e7e34302c7910ae559c7e3d20a30d71c14f85c0e86f26291bbf18c2d9dfe9a908592eea4523e6c1e5d9bb5abfbebfccd5c4e136f9be777723e932b06c029df5125191000c90fde62a8e5f8fceb28648f0c69ec3037d09302b2ade908a20dbd42761ca449b2743fc362649e16235769d9fbd7f87cd64972b58d69c0441abb5d22ddc6ed059f7ac1bdbfaef8c60e64631809c5e08c7cb4074c8ce6170d94b411604986be4ae163a')

    gen_nick = step3_generate_nickname(open_id)
    name = gen_nick if gen_nick else f"UoU_{random.randint(1000, 9999)}"

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
        r = requests.post(url, headers=headers, data=payload,
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


def step5_choose_newbie(account_id):
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
        r = requests.post(url, headers=headers, data=payload,
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


def step6_major_login(access_token, open_id, platform_type=4, tag="L1"):
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
        r = requests.post(url, headers=headers, data=payload,
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
        r = requests.post(url, headers=headers, data=body,
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


def step8_get_login_data(jwt_token, access_token, open_id, platform_type=4):
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
        r = requests.post(url, headers=headers, data=payload,
                          timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            return parse_proto(r.content.hex())
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════
#  CREATE ACCOUNT (FULL PIPELINE)
# ═══════════════════════════════════════════════════════
def create_account(worker_id):
    """Tạo 1 account hoàn chỉnh - return dict hoặc None"""
    try:
        # STEP 1
        r1 = step1_register()
        if not r1:
            return None
        uid, password = r1['uid'], r1['password']

        # STEP 2
        r2 = step2_token(uid, password)
        if not r2:
            return None
        access_token = r2['access_token']
        open_id = r2['open_id']

        # STEP 2b
        device_id = step2b_device_id(open_id)

        # STEP 3-4
        r3 = step4_major_register(access_token, open_id)
        if not r3:
            return None
        name = r3['name']
        account_id_1 = r3.get('account_id')

        # STEP 5
        if account_id_1:
            step5_choose_newbie(account_id_1)

        # STEP 6 - L1
        jwt1 = step6_major_login(access_token, open_id, tag="L1")
        if not jwt1:
            return None

        # STEP 7
        rc = step7_choose_region(jwt1)

        # STEP 6b - L2
        jwt2 = step6_major_login(access_token, open_id, tag="L2")
        jwt_final = jwt2 if jwt2 else jwt1

        # STEP 8
        ld = step8_get_login_data(jwt_final, access_token, open_id)

        # Lấy account_id
        account_id_final = account_id_1
        if ld and '1' in ld:
            field1 = ld['1']
            if field1.get("wire_type") == "varint":
                account_id_final = str(field1.get("data"))

        # Lấy nickname từ JWT
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

        # Tạo record
        account_obj = {
            "uid": str(uid),
            "password": str(password),
            "name": str(nickname),
            "account_id": str(account_id_final) if account_id_final else None,
            "region": REGION,
            "has_account_id": bool(account_id_final),
            "access_token": access_token,
            "open_id": open_id,
            "device_id": device_id,
            "token": jwt_final,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Save file
        save_account(account_obj)

        return account_obj

    except Exception as e:
        return None


# ═══════════════════════════════════════════════════════
#  MAIN - TẠO 100 ACC MULTI-THREAD
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 70)
    print(f"  FREE FIRE OB55 - TẠO {TARGET} ACC LIÊN TIẾP")
    print(f"  Region: {REGION} | Threads: {THREADS}")
    print(f"  Save file: {SAVE_FILE}")
    print("=" * 70)

    start_time = time.time()
    success = 0
    failed = 0
    counter_lock = threading.Lock()

    def worker(worker_id):
        global success, failed
        while True:
            with counter_lock:
                if success >= TARGET:
                    return
            try:
                acc = create_account(worker_id)
                if acc:
                    with counter_lock:
                        success += 1
                        cnt = success
                    elapsed = time.time() - start_time
                    speed = cnt / elapsed if elapsed > 0 else 0
                    print(f"[W{worker_id:02d}] ✅ [{cnt}/{TARGET}] UID={acc['uid']} | PASS={acc['password']} | NAME={acc['name']} | AID={acc['account_id']} | {speed:.2f}/s")
                else:
                    with counter_lock:
                        failed += 1
                        cnt = failed
                    print(f"[W{worker_id:02d}] ❌ [FAIL #{cnt}]")
                    time.sleep(0.5)
            except Exception:
                with counter_lock:
                    failed += 1
                time.sleep(0.5)
            # Delay nhẹ
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    # Start workers
    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=worker, args=(i+1,), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(0.02)

    # Chờ hoàn thành
    try:
        while success < TARGET:
            time.sleep(1)
            if all(not t.is_alive() for t in threads):
                break
    except KeyboardInterrupt:
        print("\n[!] Dừng bởi người dùng")

    # Chờ threads kết thúc
    for t in threads:
        t.join(timeout=2)

    # TỔNG KẾT
    elapsed = time.time() - start_time
    speed = success / elapsed if elapsed > 0 else 0

    print("\n" + "=" * 70)
    print(f"  KẾT QUẢ")
    print("=" * 70)
    print(f"  ✅ Thành công : {success}/{TARGET}")
    print(f"  ❌ Thất bại   : {failed}")
    print(f"  ⏱  Thời gian  : {elapsed:.1f}s ({elapsed/60:.1f} phút)")
    print(f"  ⚡ Tốc độ     : {speed:.2f} acc/s")
    print(f"  💾 File       : {os.path.abspath(SAVE_FILE)}")

    # Đếm lại từ file
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"  📁 Tổng acc trong file: {len(data)}")
    except Exception:
        pass

    print("=" * 70)