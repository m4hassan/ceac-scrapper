import scrapy
from scrapy.http import FormRequest
from scrapy_ceac.utils import solve_captcha, get_random_proxy, get_random_user_agent
from fetch_airtable import fetch_case_numbers
from update_airtable import update_airtable

class CEACSpider(scrapy.Spider):
    name = "ceac_spider"
    base_url = "https://ceac.state.gov/CEACStatTracker"
    start_urls = [f"{base_url}/Status.aspx?App=IV"]

    def parse(self, response):
        visa_case_numbers = fetch_case_numbers()
        for visa_case_number in visa_case_numbers:
            yield scrapy.Request(
                url=self.start_urls[0],
                callback=self.solve_captcha,
                meta={"visa_case_number": visa_case_number},
            )

    def solve_captcha(self, response):
        visa_case_number = response.meta["visa_case_number"]
        captcha_img_url = response.urljoin(response.css('img.LBD_CaptchaImage::attr(src)').get())
        print("######## CAPTCHA MEEEEE ##########", captcha_img_url)
        captcha_text = solve_captcha(captcha_img_url)
        if not captcha_text:
            self.logger.error(f"failed to solve captcha for {visa_case_number}")

        formdata = {
            'ctl00$ToolkitScriptManager1': 'ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$btnSubmit',
            'ctl00_ToolkitScriptManager1_HiddenField': response.xpath("//input[@id='ctl00_ToolkitScriptManager1_HiddenField']/@value").get(),
            'ctl00$ContentPlaceHolder1$Visa_Application_Type': 'IV',
            'ctl00$ContentPlaceHolder1$Visa_Case_Number': visa_case_number,
            'ctl00$ContentPlaceHolder1$Captcha': captcha_text,
            'LBD_VCID_c_status_ctl00_contentplaceholder1_defaultcaptcha': response.xpath("//input[@name='LBD_VCID_c_status_ctl00_contentplaceholder1_defaultcaptcha']/@value").get(),
            'LBD_BackWorkaround_c_status_ctl00_contentplaceholder1_defaultcaptcha': '0',
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnSubmit',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': response.xpath("//input[@name='__VIEWSTATE']/@value").get(),
            '__VIEWSTATEGENERATOR': response.xpath("//input[@name='__VIEWSTATEGENERATOR']/@value").get(),
            '__VIEWSTATEENCRYPTED': '',
            '__ASYNCPOST': 'true',
        }

        yield FormRequest.from_response(
            response,
            formdata=formdata,
            callback=self.parse_status,
            meta={"visa_case_number": visa_case_number},
        )

    def parse_status(self, response):
        visa_case_number = response.meta["visa_case_number"]
        ceac_last_updated = response.css('span#ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatusDate::text').get()
        case_status = response.css('span#ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus::text').get()
        print("####### CASE LAST UPDATED DATE #########", ceac_last_updated)
        print("####### CASE STATUS #########", case_status)
        if case_status and ceac_last_updated:
            # update_airtable(visa_case_number=visa_case_number, case_status=case_status, ceac_last_updated=ceac_last_updated)
            self.logger.info(f"Updated records for {visa_case_number}: {case_status}")
        else:
            self.logger.error(f"Failed to retrieve status for {visa_case_number}")