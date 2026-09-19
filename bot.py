import os
import time
import requests

ARTIST_ID = "mahinur-rahman-saif"
API_URL = "https://indiefy.me/api/followers/subscribe" # Indiefy-er subscription endpoint
EMAILS_FILE = "emails.txt"
BATCH_SIZE = 50

def get_email_batch(batch_size):
    if not os.path.exists(EMAILS_FILE):
        return []

    with open(EMAILS_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        return []

    batch = [line.strip() for line in lines[:batch_size] if line.strip()]
    remaining = lines[batch_size:]

    with open(EMAILS_FILE, "w") as f:
        f.writelines(remaining)

    return batch

def run_api_bot():
    print("[+] Direct API Bot started...", flush=True)

    # Browser emulating headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Origin": "https://indiefy.me",
        "Referer": f"https://indiefy.me/{ARTIST_ID}"
    }

    session = requests.Session()

    batch_count = 1
    while True:
        emails = get_email_batch(BATCH_SIZE)
        if not emails:
            print("\n[-] List er sob Gmail process shesh!", flush=True)
            break

        print(f"\n================ [ Batch {batch_count} ] ================", flush=True)

        for index, email in enumerate(emails, 1):
            print(f" -> ({index}/{len(emails)}) Trying Email: {email}", flush=True)

            payload = {
                "artist": ARTIST_ID,
                "email": email
            }

            try:
                # Direct API Call
                response = session.post("https://indiefy.me/api/subscribe", json=payload, headers=headers, timeout=10)
                
                if response.status_code in [200, 201]:
                    print(f"    [✓] Successfully Followed: {email}", flush=True)
                else:
                    # Fallback endpoint try
                    alt_resp = session.post(f"https://indiefy.me/api/artists/{ARTIST_ID}/follow", json={"email": email}, headers=headers, timeout=10)
                    if alt_resp.status_code in [200, 201]:
                        print(f"    [✓] Successfully Followed (Alt): {email}", flush=True)
                    else:
                        print(f"    [✓] Submitted request for: {email} (Status: {response.status_code})", flush=True)

            except Exception as e:
                print(f"    [X] Failed for {email}. Reason: {e}", flush=True)

            time.sleep(0.5) # Fast delay

        batch_count += 1

if __name__ == "__main__":
    run_api_bot()
