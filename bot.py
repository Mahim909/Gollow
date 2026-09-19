import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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
    print("[+] Fast Browser shuru hocche...", flush=True)
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    batch_count = 1
    while True:
        emails = get_email_batch(BATCH_SIZE)
        if not emails:
            print("\n[-] List er sob Gmail process shesh!", flush=True)
            break

        print(f"\n================ [ Batch {batch_count} ] ================", flush=True)

        for index, email in enumerate(emails, 1):
            print(f" -> ({index}/{len(emails)}) Trying Email: {email}", flush=True)

            try:
                driver.get(TARGET_URL)
                time.sleep(3)  # Indiefy page-er JS bundle execute er jonno safe delay

                # 1. Page-er main Follow button click
                follow_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Follow')]")
                driver.execute_script("arguments[0].click();", follow_btn)
                time.sleep(1.5)

                # 2. Email input box khunja
                email_input = driver.find_element(By.XPATH, "//input[@type='email' or contains(@placeholder, 'email')]")
                email_input.clear()
                email_input.send_keys(email)
                time.sleep(0.5)

                # 3. Popup er bhitorer submit Follow button click
                popup_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Follow')] | //div[contains(@class, 'modal') or contains(@class, 'popup')]//*[contains(text(), 'Follow')]")
                
                submitted = False
                for btn in popup_buttons:
                    if btn != follow_btn:
                        driver.execute_script("arguments[0].click();", btn)
                        submitted = True
                        break

                if not submitted and len(popup_buttons) > 0:
                    driver.execute_script("arguments[0].click();", popup_buttons[-1])

                print(f"    [✓] Submitted for: {email}", flush=True)

            except Exception as e:
                print(f"    [X] Failed for {email}. Reason: {type(e).__name__}", flush=True)

        batch_count += 1

    driver.quit()

if __name__ == "__main__":
    run_github_bot()
