import logging
import random
import sys
import time

from playwright.sync_api import sync_playwright

from airtable import fetch_case_numbers
from utils import (fill_case_details,
                   solve_captcha_and_submit_form,
                   extract_case_status_and_update_airtable)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger()


def process_case(page, visa_case_number, location=None, passport_number=None, surname=None, is_NIV=False):
    """General function to process a case, supporting both IV and NIV cases."""
    url = "https://ceac.state.gov/CEACStatTracker/Status.aspx?App=NIV" if is_NIV else "https://ceac.state.gov/CEACStatTracker/Status.aspx?App=IV"
    page.goto(url)
    time.sleep(random.uniform(5, 7))

    for attempt in range(3):
        logger.info(f"Attempt {attempt + 1} for case {visa_case_number}")
        fill_case_details(page, visa_case_number, passport_number, surname, location)
        solve_captcha_and_submit_form(page)

        try:
            extract_case_status_and_update_airtable(page, visa_case_number)
            break  # Exit loop if successful

        except Exception:
            logger.warning(f"CAPTCHA failed for case {visa_case_number}, retrying...")
            if attempt < 2:
                page.reload(wait_until="domcontentloaded")
                time.sleep(random.uniform(3, 5))
    else:
        logger.error(f"Failed to solve CAPTCHA for case {visa_case_number} after 3 attempts.")


# def process_case(page, visa_case_number):
#     page.goto("https://ceac.state.gov/CEACStatTracker/Status.aspx?App=IV")
#     time.sleep(random.uniform(5, 7))
#     logger.info(page)
#
#     page.wait_for_selector(
#         '//input[@name="ctl00$ContentPlaceHolder1$Visa_Case_Number"]',
#         timeout=60000,
#     )
#
#     for attempt in range(3):
#         logger.info(f"Attempt {attempt + 1} for case {visa_case_number}")
#         page.fill(
#             '//input[@name="ctl00$ContentPlaceHolder1$Visa_Case_Number"]',
#             visa_case_number,
#         )
#
#         page.wait_for_selector(
#             '//img[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage"]',
#             timeout=60000,
#         )
#
#         image_element = page.locator(
#             '//img[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage"]'
#         )
#         image_data = image_element.screenshot()
#         image_base64 = base64.b64encode(image_data).decode("utf-8")
#
#         captcha_solution = base_solve_captcha(image_base64)
#
#         page.wait_for_selector('//input[@name="ctl00$ContentPlaceHolder1$Captcha"]')
#         page.fill(
#             '//input[@name="ctl00$ContentPlaceHolder1$Captcha"]', captcha_solution
#         )
#
#         time.sleep(random.uniform(5, 7))
#         page.click('//img[@id="ctl00_ContentPlaceHolder1_imgFolder" and @alt="submit"]')
#
#         try:
#             page.wait_for_selector(
#                 '//div[@class="status"]/span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus"]',
#                 timeout=60000,
#             )
#             status = page.locator(
#                 '//div[@class="status"]/span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus"]'
#             ).inner_text()
#             last_update_date = page.locator(
#                 '//td//span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatusDate"]'
#             ).inner_text()
#
#             logger.info(
#                 f"Case {visa_case_number} Status: {status} Updated Date: {last_update_date}"
#             )
#
#             if not update_airtable(visa_case_number, status, last_update_date):
#                 logger.error(
#                     f"(in process_case) - Failed to update Airtable for case {visa_case_number}"
#                 )
#
#             break
#         except Exception:
#             logger.warning(f"CAPTCHA failed for case {visa_case_number}, retrying...")
#
#             if attempt < 2:
#                 logger.info("Refreshing the page for a new CAPTCHA...")
#                 page.reload(wait_until="domcontentloaded")
#                 time.sleep(random.uniform(3, 5))
#
#                 page.wait_for_selector(
#                     '//img[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage"]',
#                     timeout=60000,
#                 )
#
#     else:
#         logger.error(
#             f"Failed to solve CAPTCHA for case {visa_case_number} after 3 attempts."
#         )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={
                "width": random.randint(1200, 1920),
                "height": random.randint(800, 1080),
            },
            geolocation={"latitude": 37.7749, "longitude": -122.4194},
            permissions=["geolocation"],
        )
        page = context.new_page()
        logger.info(f"Page => {page}")

        visa_case_numbers = fetch_case_numbers()
        logger.info(visa_case_numbers)
        for visa in visa_case_numbers:
            ## TODO: Implement logic to handle both IV and NIV cases
            process_case(page, visa, passport_number="123434355", location="KBL", surname="Hassan", is_NIV=True)

        browser.close()


if __name__ == "__main__":
    main()
