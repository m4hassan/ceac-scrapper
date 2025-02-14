import base64
import logging
from playwright.sync_api import sync_playwright
from utils import solve_captcha as base_solve_captcha
from fetch_airtable import fetch_case_numbers
from update_airtable import update_airtable

# Configure logging
logging.basicConfig(
    filename="captcha_solver.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


def process_case(page, visa_case_number):
    page.goto("https://ceac.state.gov/CEACStatTracker/Status.aspx?App=IV")

    page.wait_for_selector(
        '//input[@name="ctl00$ContentPlaceHolder1$Visa_Case_Number"]',
        timeout=60000,
    )
    page.fill(
        '//input[@name="ctl00$ContentPlaceHolder1$Visa_Case_Number"]',
        visa_case_number,
    )

    for attempt in range(3):
        logger.info(f"Attempt {attempt + 1} for case {visa_case_number}")

        page.wait_for_selector(
            '//img[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage"]',
            timeout=60000,
        )

        image_element = page.locator(
            '//img[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage"]'
        )
        image_data = image_element.screenshot()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        captcha_solution = base_solve_captcha(image_base64)

        page.wait_for_selector('//input[@name="ctl00$ContentPlaceHolder1$Captcha"]')
        page.fill(
            '//input[@name="ctl00$ContentPlaceHolder1$Captcha"]', captcha_solution
        )

        page.click('//img[@id="ctl00_ContentPlaceHolder1_imgFolder" and @alt="submit"]')

        try:
            page.wait_for_selector(
                '//div[@class="status"]/span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus"]',
                timeout=60000,
            )
            status = page.locator(
                '//div[@class="status"]/span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus"]'
            ).inner_text()
            last_update_date = page.locator(
                '//td//span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatusDate"]'
            ).inner_text()

            logger.info(
                f"Case {visa_case_number} Status: {status} Updated Date: {last_update_date}"
            )
            break
        except Exception:
            logger.warning(f"CAPTCHA failed for case {visa_case_number}, retrying...")

            if attempt < 2:
                logger.info("Refreshing CAPTCHA...")
                page.click(
                    '//a[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_ReloadLink"]'
                )

                page.wait_for_selector(
                    '//img[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage"]',
                    timeout=60000,
                )

    else:
        logger.error(
            f"Failed to solve CAPTCHA for case {visa_case_number} after 3 attempts."
        )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        visa_case_numbers = fetch_case_numbers()
        for visa in visa_case_numbers:
            process_case(page, visa)

        browser.close()


if __name__ == "__main__":
    main()
