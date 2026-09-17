import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://indiefy.me/mahinur-rahman-saif"
EMAILS_FILE = "emails.txt"

# গতি নিয়ন্ত্রণের কনফিগারেশন
BATCH_SIZE = 5      # প্রতিবারে ৫টি করে ইমেইল প্রসেস হবে
WAIT_TIME = 60      # প্রতিটি ব্যাচ শেষে ৬০ সেকেন্ড (১ মিনিট) বিরতি

def get_email_batch(batch_size):
    """emails.txt থেকে একটি নির্দিষ্ট সংখ্যক ইমেইল নিয়ে আসে এবং ফাইল থেকে সেগুলো মুছে দেয়"""
    if not os.path.exists(EMAILS_FILE):
        print(f"Error: {EMAILS_FILE} ফাইলটি পাওয়া যায়নি!")
        return []

    with open(EMAILS_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        return []

    # ব্যাচের ইমেইলগুলো আলাদা করা
    batch = [line.strip() for line in lines[:batch_size] if line.strip()]
    remaining = lines[batch_size:]

    # ফাইল আপডেট করা
    with open(EMAILS_FILE, "w") as f:
        f.writelines(remaining)

    return batch

def run_github_bot():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    batch_count = 1
    while True:
        emails = get_email_batch(BATCH_SIZE)
        if not emails:
            print("\n[-] লিস্টের সব জিমেইলের প্রসেস সম্পন্ন হয়েছে!")
            break

        print(f"\n================ [ Batch {batch_count} ] ================")
        print(f"[+] Processing {len(emails)} emails...")

        for index, email in enumerate(emails, 1):
            print(f" -> ({index}/{len(emails)}) Trying Email: {email}")

            try:
                driver.get(TARGET_URL)
                time.sleep(3)

                # Follow Button
                follow_button = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'FOLLOW', 'follow'), 'follow')]"))
                )
                follow_button.click()
                time.sleep(2)

                # Email Box Search
                email_inputs = driver.find_elements(By.XPATH, "//input[@type='email']")
                if email_inputs:
                    email_inputs[0].clear()
                    email_inputs[0].send_keys(email)
                    time.sleep(1)

                    submit_btn = driver.find_elements(By.XPATH, "//button[@type='submit']")
                    if submit_btn:
                        submit_btn[0].click()
                        print(f"    [✓] Submitted: {email}")
                else:
                    print(f"    [i] Follow-এ ক্লিক হয়েছে (লগইন রিডাইরেক্ট)।")

            except Exception as e:
                print(f"    [X] Failed for {email}: {e}")

            time.sleep(2)  # প্রতি ইমেইলের মাঝে ২ সেকেন্ডের ছোট গ্যাপ

        print(f"[⏳] ব্যাচ সমাপ্ত। পরবর্তী ব্যাচের জন্য {WAIT_TIME} সেকেন্ড (১ মিনিট) বিরতি নেওয়া হচ্ছে...")
        time.sleep(WAIT_TIME)
        batch_count += 1

    driver.quit()

if __name__ == "__main__":
    run_github_bot()
