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
    print("[+] Headless Browser starting...", flush=True)
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    batch_count = 1
    while True:
        emails = get_email_batch(BATCH_SIZE)
        if not emails:
            print("\n[-] All emails processed from list!", flush=True)
            break

        print(f"\n================ [ Batch {batch_count} ] ================", flush=True)

        for index, email in enumerate(emails, 1):
            print(f" -> ({index}/{len(emails)}) Trying Email: {email}", flush=True)

            try:
                driver.get(TARGET_URL)

                # 1. Hanapin at i-click ang main Follow button gamit ang XPath matching
                follow_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(text(), 'FOLLOW', 'follow'), 'follow')]"))
                )
                driver.execute_script("arguments[0].click();", follow_button)

                # 2. Hihintayin na lumitaw ang Email input field sa loob ng popup (max 10 sec)
                email_input = wait.until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@type='email' or contains(@placeholder, 'email')]"))
                )
                email_input.clear()
                email_input.send_keys(email)

                # 3. Hanapin ang submit Follow button sa loob ng popup at i-click
                submit_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'FOLLOW', 'follow'), 'follow')] | //div[contains(@class, 'modal') or contains(@class, 'popup')]//*[contains(text(), 'Follow')]"))
                )
                driver.execute_script("arguments[0].click();", submit_button)

                time.sleep(1)
                print(f"    [✓] Successfully submitted for: {email}", flush=True)

            except Exception as e:
                print(f"    [X] Failed for {email}. Reason: {type(e).__name__}", flush=True)

        batch_count += 1

    driver.quit()

if __name__ == "__main__":
    run_github_bot()
