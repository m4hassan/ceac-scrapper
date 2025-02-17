import logging
import sys
import time

import requests

import config as config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger()


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
