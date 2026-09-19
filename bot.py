import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://indiefy.me/mahinur-rahman-saif"
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

def run_github_bot():
    print("[+] Browser শুরু হচ্ছে...", flush=True)
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # CSS এবং JS ঠিকমতো লোড হতে দিতে হবে
    prefs = {
        "profile.managed_default_content_settings.images": 2  # শুধু ইমেজ বন্ধ রাখা হলো স্পিডের জন্য
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

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

                # ১. প্রথম 'Follow' বাটন খুঁজে ক্লিক করা (১ম স্ক্রিনশট)
                follow_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(text(), 'FOLLOW', 'follow'), 'follow')]"))
                )
                driver.execute_script("arguments[0].click();", follow_btn)

                # ২. পপ-আপের ইমেইল ইনপুট বক্স আসা পর্যন্ত অপেক্ষা করা (২য় স্ক্রিনশট)
                email_input = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='email' or contains(@placeholder, 'email')]"))
                )
                email_input.clear()
                email_input.send_keys(email)

                # ৩. পপ-আপের ভেতরের ফাইনাল 'Follow' বাটন খুঁজে ক্লিক করা
                # পপ-আপ মোডালের ভেতরের সাবমিট বাটন নির্ধারণ
                submit_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'FOLLOW', 'follow'), 'follow')] | //div[contains(@class, 'modal') or contains(@class, 'popup')]//*[contains(text(), 'Follow')]"))
                )
                driver.execute_script("arguments[0].click();", submit_btn)

                print(f"    [✓] Successfully Followed & Submitted for: {email}", flush=True)

            except Exception as e:
                print(f"    [X] Failed for {email}. Reason: {type(e).__name__}", flush=True)

        batch_count += 1

    driver.quit()

if __name__ == "__main__":
    run_github_bot()
