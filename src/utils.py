import logging
import sys
import time
import random
import base64
import requests

import config

from airtable import update_airtable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger()


def fill_case_details(page, visa_case_number, passport_number=None, surname=None, location=None):
    """Fill in the case details in the form."""
    page.fill(
        '//input[@name="ctl00$ContentPlaceHolder1$Visa_Case_Number"]',
        visa_case_number)

    if location:
        page.select_option(
            '//select[@name="ctl00$ContentPlaceHolder1$Location_Dropdown"]',
            value=location)

    if passport_number:
        page.fill(
            '//input[@name="ctl00$ContentPlaceHolder1$Passport_Number"]',
            passport_number)

    if surname:
        page.fill(
            '//input[@name="ctl00$ContentPlaceHolder1$Surname"]',
            surname)


def solve_captcha_and_submit_form(page):
    """Solve the CAPTCHA and submit the form."""
    page.wait_for_selector(
        '//img[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage"]',
        timeout=60000)

    image_element = page.locator(
        '//img[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage"]'
    )
    image_data = image_element.screenshot()
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    captcha_solution = solve_captcha(image_base64)

    page.fill(
        '//input[@name="ctl00$ContentPlaceHolder1$Captcha"]',
        captcha_solution)

    time.sleep(random.uniform(5, 7))
    page.click(
        '//img[@id="ctl00_ContentPlaceHolder1_imgFolder" and @alt="submit"]'
    )


def extract_case_status_and_update_airtable(page, visa_case_number):
    """Extract case status and update Airtable."""
    try:
        page.wait_for_selector(
            '//div[@class="status"]/span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus"]',
            timeout=60000)

        status = page.locator(
            '//div[@class="status"]/span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus"]'
        ).inner_text()

        last_update_date = page.locator(
            '//td//span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatusDate"]'
        ).inner_text()

        logger.info(f"Case {visa_case_number} Status: {status} Updated Date: {last_update_date}")

        if not update_airtable(visa_case_number, status, last_update_date):
            logger.error(
                f"(in process_case) - Failed to update Airtable for case {visa_case_number}"
            )

    except Exception:
        logger.warning(f"Failed to retrieve status for case {visa_case_number}")


def solve_captcha(image_b64, max_wait_time=120, retry_delay=20):
    payload = {
        "clientKey": config.TWO_CAPTCHA_KEY,
        "task": {
            "type": "ImageToTextTask",
            "body": image_b64,
        },
        "languagePool": "en",
    }

    response = requests.post("https://api.2captcha.com/createTask", json=payload).json()
    task_id = response.get("taskId")

    elapsed_time = 0

    while elapsed_time < max_wait_time:
        time.sleep(retry_delay)
        elapsed_time += retry_delay
        payload = {
            "clientKey": config.TWO_CAPTCHA_KEY,
            "taskId": task_id,
        }
        result = requests.post(
            f"https://api.2captcha.com/getTaskResult", json=payload
        ).json()
        logger.info(f"#### CAPTCHA RESULT #### {result}")

        if result.get("status") == "ready":
            solved_text = result.get("solution").get("text")
            logger.info(f"✅ Captcha solved: {solved_text}")
            return solved_text
        elif result.get("status") == "processing":
            logger.info(f"⌛ Captcha not ready. Retrying in {retry_delay}s...")
            continue
        else:
            logger.error(f"❌ Error retrieving captcha result: {result}")
            return None

    logger.info("⏳ Max wait time reached. Captcha solving failed.")
    return None
