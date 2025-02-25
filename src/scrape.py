import logging
import random
import sys
import time

from playwright.sync_api import sync_playwright

from airtable import fetch_case_numbers
from utils import (fill_case_details,
                   solve_captcha_and_submit_form,
                   extract_case_status_and_update_airtable)
from constants import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger()


def process_case(page, visa_case_number, location=None, passport_number=None, surname=None, is_NIV=False):
    """General function to process a case, supporting both IV and NIV cases."""
    url = NIV_url if is_NIV else IV_url
    page.goto(url)
    time.sleep(random.uniform(3, 5))

    for attempt in range(3):
        logger.info(f"Attempt {attempt + 1} for case {visa_case_number}")
        fill_case_details(page, visa_case_number, passport_number, surname, location)
        solve_captcha_and_submit_form(page)

        try:
            extract_case_status_and_update_airtable(page, visa_case_number, is_NIV)
            break

        except Exception as e:
            logger.warning(f"Script failed to process case {visa_case_number}, retrying...\n {e}")
            if attempt < 2:
                page.reload(wait_until="domcontentloaded")
                time.sleep(random.uniform(3, 5))
    else:
        logger.error(f"Failed to process case {visa_case_number} after 3 attempts.")


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
            # process_case(page, visa, passport_number="123434355", location="KBL", surname="Hassan", is_NIV=True)
            process_case(page, visa)

        browser.close()


if __name__ == "__main__":
    main()
