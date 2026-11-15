import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

def check_proxy(proxy):
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=5)
        if r.status_code == 200:
            return proxy
    except:
        pass
    return None

def main():
    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[!] File proxies.txt not found.")
        sys.exit(1)

    print(f"[*] Loaded {len(proxies)} proxies. Checking ALL of them...")
    working = []
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(check_proxy, p): p for p in proxies}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result:
                print(f"[+] OK: {result} (Found: {len(working)})")
                working.append(result)
            if i % 100 == 0:
                print(f"[*] Checked {i}/{len(proxies)}...")

    with open("working_proxies.txt", "w") as f:
        for p in working:
            f.write(f"{p}\n")
            
    print(f"\n[*] Done. Found {len(working)} working proxies.")
    print("[*] Saved to working_proxies.txt")

if __name__ == "__main__":
    main()
