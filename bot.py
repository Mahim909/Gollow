import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://indiefy.me/mahinur-rahman-saif"
EMAILS_FILE = "emails.txt"

BATCH_SIZE = 1500
WAIT_TIME = 60

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

def run_github_bot():
    print("[+] Browser শুরু হচ্ছে...", flush=True)
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    batch_count = 1
    while True:
        emails = get_email_batch(BATCH_SIZE)
        if not emails:
            print("\n[-] লিস্টের সব জিমেইলের প্রসেস শেষ!", flush=True)
            break

        print(f"\n================ [ Batch {batch_count} ] ================", flush=True)

        for index, email in enumerate(emails, 1):
            print(f" -> ({index}/{len(emails)}) Trying Email: {email}", flush=True)

            try:
                driver.get(TARGET_URL)
                time.sleep(5)

                # ১. JavaScript দিয়ে সকল Follow বাটন খুঁজে ক্লিক করা
                buttons = driver.find_elements(By.TAG_NAME, "button")
                follow_btn = None
                for btn in buttons:
                    if "follow" in btn.text.lower():
                        follow_btn = btn
                        break

                if follow_btn:
                    driver.execute_script("arguments[0].click();", follow_btn)
                    time.sleep(3)
                else:
                    print("    [!] Follow বাটন খুঁজে পাওয়া যায়নি (Cloudflare Block হতে পারে)।", flush=True)
                    continue

                # ২. ইমেইল ইনপুট বক্স খোঁজা
                email_inputs = driver.find_elements(By.XPATH, "//input")
                target_input = None
                for inp in email_inputs:
                    inp_type = inp.get_attribute("type")
                    inp_ph = inp.get_attribute("placeholder") or ""
                    if inp_type == "email" or "email" in inp_ph.lower():
                        target_input = inp
                        break

                if target_input:
                    target_input.clear()
                    target_input.send_keys(email)
                    time.sleep(1)

                    # ৩. পপ-আপের ভেতরে থাকা সাবমিট/ফলো বাটন খুঁজে ক্লিক করা
                    sub_buttons = driver.find_elements(By.TAG_NAME, "button")
                    for s_btn in sub_buttons:
                        if "follow" in s_btn.text.lower() and s_btn != follow_btn:
                            driver.execute_script("arguments[0].click();", s_btn)
                            print(f"    [✓] Submitted for: {email}", flush=True)
                            break
                else:
                    print(f"    [!] ইমেইল ইনপুট বক্স পপ-আপে পাওয়া যায়নি।", flush=True)

            except Exception as e:
                print(f"    [X] Failed for {email}. Exception: {type(e).__name__}", flush=True)

            time.sleep(2)

        print(f"[⏳] ব্যাচ শেষ। {WAIT_TIME} সেকেন্ড বিরতি...", flush=True)
        time.sleep(WAIT_TIME)
        batch_count += 1

    driver.quit()

if __name__ == "__main__":
    run_github_bot()
