import time
import base64
import requests
import random
import config as config


def solve_captcha(image_b64, max_wait_time=300, retry_delay=20):
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
        print("#### CAPTCHA RESULT ####", result)

        if result.get("status") == "ready":
            solved_text = result.get("solution").get("text")
            print("✅ Captcha solved:", solved_text)
            return solved_text
        elif result.get("status") == "processing":
            print(f"⌛ Captcha not ready. Retrying in {retry_delay}s...")
            continue
        else:
            print("❌ Error retrieving captcha result:", result)
            return None

    print("⏳ Max wait time reached. Captcha solving failed.")
    return None


def encode_image_to_base64(image_url):
    """Fetch an image from a URL and convert it to a Base64 string."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except requests.RequestException as e:
        print(f"❌ Error fetching image: {e}")
        return None


def get_random_proxy():
    return random.choice(config.PROXY_LIST)
