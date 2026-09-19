import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://indiefy.me/mahinur-rahman-saif"
EMAILS_FILE = "emails.txt"

BATCH_SIZE = 5      # প্রতিবারে ৫টি ইমেইল প্রসেস হবে
WAIT_TIME = 60      # প্রতিটি ব্যাচ শেষে ১ মিনিট বিরতি

def get_email_batch(batch_size):
    if not os.path.exists(EMAILS_FILE):
        print(f"Error: {EMAILS_FILE} ফাইলটি পাওয়া যায়নি!", flush=True)
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
                time.sleep(4)

                # ১. মূল পেজের Follow বাটন ক্লিক
                main_follow_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'FOLLOW', 'follow'), 'follow')]"))
                )
                main_follow_btn.click()
                time.sleep(2)

                # ২. পপ-আপের ভেতরে ইমেইল ইনপুট বক্স খোঁজা
                email_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your email address' or @type='email']"))
                )
                email_box.clear()
                email_box.send_keys(email)
                time.sleep(1)

                # ৩. পপ-আপের ভেতরের ফলো বাটন ক্লিক
                popup_follow_btn = driver.find_element(By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'popup') or contains(@class, 'dialog')]//button[contains(translate(text(), 'FOLLOW', 'follow'), 'follow')]")
                popup_follow_btn.click()
                print(f"    [✓] Submitted for: {email}", flush=True)

            except Exception as e:
                print(f"    [X] Failed for {email}. Error: {e}", flush=True)

            time.sleep(2)

        print(f"[⏳] ব্যাচ শেষ। {WAIT_TIME} সেকেন্ড বিরতি...", flush=True)
        time.sleep(WAIT_TIME)
        batch_count += 1

    driver.quit()

if __name__ == "__main__":
    run_github_bot()
