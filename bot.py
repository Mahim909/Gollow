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
    print("[+] Live Count Bot starting...", flush=True)
    
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

        # ১. একবার পেজ লোড করে সেশন চালু করা
        driver.get(TARGET_URL)
        time.sleep(5)

        for index, email in enumerate(emails, 1):
            print(f" -> ({index}/{len(emails)}) Processing: {email}", flush=True)

            try:
                # ২. ব্রাউজারের ভেতর থেকে অরিজিনাল UI ইভেন্ট ট্রিগার করা
                success = driver.execute_script("""
                    return (async function(userEmail) {
                        try {
                            // ১. মূল Follow বাটনটি খুঁজে বের করা
                            let allBtns = Array.from(document.querySelectorAll('button, div, span'));
                            let followBtn = allBtns.find(b => b.innerText && b.innerText.trim().toLowerCase().includes('follow'));
                            if (followBtn) followBtn.click();

                            await new Promise(r => setTimeout(r, 1000));

                            // ২. ইমেইল ইনপুট বক্সে ভ্যালু সেট করা
                            let input = document.querySelector('input[type="email"], input[placeholder*="email" i]');
                            if (!input) return "INPUT_NOT_FOUND";

                            input.value = userEmail;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));

                            await new Promise(r => setTimeout(r, 500));

                            // ৩. পপ-আপের ভেতরের ফাইনাল Follow বাটনটি ক্লিক করা
                            let modalBtns = Array.from(document.querySelectorAll('.modal button, .popup button, [role="dialog"] button, button'));
                            let submitBtn = modalBtns.find(b => b.innerText && b.innerText.trim().toLowerCase().includes('follow') && b !== followBtn);
                            
                            if (submitBtn) {
                                submitBtn.click();
                                return "SUCCESS";
                            } else {
                                // বিকল্প হিসেবে Enter key প্রেস ট্রিগার
                                input.dispatchEvent(new KeyboardEvent('keydown', {'key': 'Enter', 'keyCode': 13, 'bubbles': true}));
                                return "SUBMITTED_WITH_ENTER";
                            }
                        } catch(err) {
                            return err.toString();
                        }
                    })(arguments[0]);
                """, email)

                print(f"    [✓] Result for {email}: {success}", flush=True)
                time.sleep(1.5)

            except Exception as e:
                print(f"    [X] Failed for {email}. Reason: {e}", flush=True)

        batch_count += 1

    driver.quit()

if __name__ == "__main__":
    run_github_bot()
