import os
import time
from selenium import webdriver
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
                time.sleep(4)  # Page full load er jonno delay

                # 1. Javascript diye main page er Follow button khunja & click
                clicked_first = driver.execute_script("""
                    let buttons = Array.from(document.querySelectorAll('button, div, a, span'));
                    let btn = buttons.find(b => b.innerText && b.innerText.toLowerCase().includes('follow'));
                    if (btn) {
                        btn.click();
                        return true;
                    }
                    return false;
                """)

                if not clicked_first:
                    raise Exception("First Follow button missing")

                time.sleep(2)  # Popup open haoar delay

                # 2. Email input box-e email type kora
                email_filled = driver.execute_script("""
                    let input = document.querySelector('input[type="email"], input[placeholder*="email" i]');
                    if (input) {
                        input.value = arguments[0];
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }
                    return false;
                """, email)

                if not email_filled:
                    raise Exception("Email input box missing")

                time.sleep(1)

                # 3. Popup modal er bhitorer final Follow button click
                submitted = driver.execute_script("""
                    let modal = document.querySelector('.modal, .popup, [role="dialog"]') || document.body;
                    let modalBtns = Array.from(modal.querySelectorAll('button, div, span'));
                    let followBtn = modalBtns.find(b => b.innerText && b.innerText.toLowerCase().includes('follow') && b.offsetWidth > 0);
                    if (followBtn) {
                        followBtn.click();
                        return true;
                    }
                    return false;
                """)

                if submitted:
                    print(f"    [✓] Submitted for: {email}", flush=True)
                else:
                    print(f"    [X] Could not click popup submit button for: {email}", flush=True)

            except Exception as e:
                print(f"    [X] Failed for {email}. Reason: {e}", flush=True)

        batch_count += 1

    driver.quit()

if __name__ == "__main__":
    run_github_bot()
