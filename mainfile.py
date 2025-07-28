'''
Your .env file should be in the format of
email="your_email"
password="your_neopwd"
lab_number="labnumber"
lab_name="Java Programming"
lab_type="Lab exercise"
gem_api_key="your_api_key"
'''

import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import time
from ai_part import get_ans
import re
load_dotenv()

def run(playwright):
    # Get email and password from environment variables
    email = os.environ.get('email')
    password = os.environ.get('password')
    lab_number = os.environ.get('lab_number')
    lab_name = os.environ.get('lab_name')
    lab_type = os.environ.get('lab_type')

    if not email or not password:
        raise ValueError("Please set the email and password environment variables in your .env file.")

    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=os.path.expanduser("~/Library/Application Support/Google/Chrome/Default"),
        headless=False,
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )
    page = browser.new_page()

    try:
        page.goto("https://vitvellore312.examly.io/login")
        time.sleep(5)
        # Fill in email and click next
        page.locator("input#email").fill(email)
        page.locator("button:has-text('Next')").click()
        time.sleep(5)
        # Wait for the password input to be visible
        page.wait_for_selector("input#password", timeout=10000)

        # Fill in password and click login
        page.locator("input#password").fill(password)
        page.locator("button:has-text('Login')").click()

        # Wait for navigation to complete (adjust as needed)
        #page.wait_for_load_state("networkidle")
        time.sleep(5)
        print("Login successful!")
        time.sleep(4)
        page.goto("https://vitvellore312.examly.io/mycourses?type=mylabs")
        print("Navigated")
        time.sleep(10)
        java_card = page.locator(f"div.card-hover:has-text('{lab_name}')")
        java_card.first.click()
        #page.locator(card_selector).first.click()
        time.sleep(5)

        # First, click on "Lab 1"
        page.locator("text=Lab 1").first.click()
        print("✅ Lab 1 clicked")
        time.sleep(2) # Adding a small delay for UI to update

        # Then, click on the lab number from the .env file
        dropdown_item = page.locator(f"text=Lab {lab_number}")
        dropdown_item.first.click()
        print(f"✅ Lab {lab_number} clicked")

        # This clicks the lab_type text (e.g., "Practice"), but ensures it's visible
        lab_type_button = page.locator(f"div.container:has-text('{lab_type}')")
        lab_type_button.first.scroll_into_view_if_needed()
        lab_type_button.first.click()

        # Now select the first visible dropdown option directly
        dropdown_options = page.locator("div.accEach1")
        # Wait for the first option to be visible before clicking
        first_option = dropdown_options.first
        first_option.wait_for(state='visible')
        first_option.click()
        print("✅ Clicked first lab option under lab type")
        time.sleep(3)
        test_button = page.locator("button:has-text('Take Test'), button:has-text('Resume Test')")

        # Ensure it is visible and click
        test_button.first.wait_for(state='visible')
        test_button.first.click()
        print("🚀 Test launched (Take/Resume)")
        time.sleep(3)
        agree_button = page.locator("button:has-text('Agree & Proceed')")
        agree_button.first.wait_for(state="visible")
        agree_button.first.click()
        print("✅ Clicked 'Agree & Proceed' button")
        time.sleep(15)
        time.sleep(25)
        print("Starting to answer in 10 seconds")
        time.sleep(10)
        print("Starting to answer questions...")
        # Step 2: Extract the question
        while True:  # Loop through all questions
            full_question = ""
            result_text = ""
            success = False

            for attempt in range(5):  # Retry 5 times max
                time.sleep(5)

                try:
                    # Step 1: Extract the full question
                    ans_size = 0
                    question_divs = page.locator("div[aria-labelledby='each-type-question']")
                    question_texts = [question_divs.nth(i).inner_text() for i in range(question_divs.count())]
                    full_question = "\n\n".join(question_texts)
                    print(f"📘 Attempt {attempt + 1} - Full Question:\n", full_question)

                    # Step 2: Get answer (include last error if retry)
                    answer_text = get_ans(full_question + "\n\n" + result_text if attempt > 0 else full_question)
                    ans_size = len(answer_text)
                    print("💡 Answer generated")

                    # Step 3: Paste into editor
                    editor = page.locator("div.ace_content")
                    editor.click()
                    if attempt > 0:
                        for _ in range(ans_size+100):
                            page.keyboard.press("Backspace")
                    page.keyboard.insert_text(answer_text)
                    print("✍️ Answer pasted")
                    time.sleep(5)

                    # Step 4: Compile
                    page.locator("button#programme-compile").click()
                    print("🛠 Compiling...")
                    time.sleep(7)

                    # Step 5: Read result
                    result_div = page.locator("div[aria-labelledby='sample-tc-container']")
                    result_text = result_div.inner_text()
                    print("🧪 Result:\n", result_text)

                    match = re.search(r'(\d+)\s*/\s*(\d+)', result_text)
                    if match:
                        passed = int(match.group(1))
                        total = int(match.group(2))
                        if passed == total:
                            print("✅ All test cases passed")

                            # Step 6: Submit and break retry loop
                            page.locator("button#tt-footer-submit-answer").click()
                            print("🚀 Submitted answer")
                            success = True
                            time.sleep(5)
                            break
                        else:
                            print(f"❌ Attempt {attempt+1} failed: Only {passed}/{total} passed")
                    else:
                        print("⚠️ Couldn't parse result properly.")

                except Exception as inner_error:
                    print(f"⚠️ Retry attempt {attempt+1} failed due to: {inner_error}")

            if not success:
                print("❌ Gave up after 5 attempts. Moving on...")

            # Step 7: Move to next question if exists
            try:
                next_button = page.locator("div.next-btn")
                if next_button.is_visible():
                    next_button.click()
                    print("➡️ Moved to next question")
                    time.sleep(5)
                else:
                    print("🎉 No more questions. Done!")
                    break
            except:
                print("✅ All questions attempted or no next button.")
                break


        time.sleep(5)
        time.sleep(15)
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close browser
        context.close()
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
