import logging
import time
import random
import base64
import requests
from constants import *
import config

from airtable import update_airtable
# from src.slack import Slack

logger = logging.getLogger(__name__)
# slack_client = Slack()

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


def solve_captcha_and_submit_form(page, max_attempts=3):
    """Solve the CAPTCHA and submit the form."""
    for attempt in range(max_attempts):
        logger.info(f"Attempt {attempt + 1} of {max_attempts} to solve CAPTCHA...")

        image_element = page.locator(
            img_captcha_xpath
        )
        image_element.wait_for(state="visible", timeout=50000)
        image_data = image_element.screenshot()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        captcha_solution = solve_captcha(image_base64)

        page.fill(
            input_captcha_xpath,
            captcha_solution
        )
        time.sleep(random.uniform(5, 7))
        page.click(
            submit_btn_xpath
        )
        time.sleep(3)
        # Check if the error message appears (incorrect CAPTCHA case)
        if page.locator(error_xpath).is_visible():
            logger.warning("Incorrect CAPTCHA entered, retrying...")
            continue

        logger.info(f"CAPTCHA solved and form submitted successfully...")
        return True

    logger.error("Failed to solve CAPTCHA after multiple attempts.")
    return False


def extract_case_status_and_update_airtable(page, visa_case_number, is_NIV=False):
    """Extract case status and update Airtable."""
    try:

        status = page.locator(
            visa_status_xpath,
        ).inner_text()

        last_update_date = page.locator(
            visa_last_updated_xpath,
        ).inner_text()

        logger.info(f"Case {visa_case_number} Status: {status} Updated Date: {last_update_date}")

        if not update_airtable(visa_case_number, status, last_update_date):
            logger.error(
                f"(in process_case) - Failed to update Airtable for case {visa_case_number}"
            )

    except Exception:
        ## TODO: Uncomment and test when slack auth info is available
        slack_payload = slack_client.create_slack_payload(visa_case_number, "NIV" if is_NIV else "IV")
        slack_client.send_message_to_channel(slack_payload)
        logger.warning(f"Invalid Visa Case number: {visa_case_number} - {'NIV' if is_NIV else 'IV'}")


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