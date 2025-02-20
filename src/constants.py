
IV_url = "https://ceac.state.gov/CEACStatTracker/Status.aspx?App=IV"
NIV_url = "https://ceac.state.gov/CEACStatTracker/Status.aspx?App=NIV"

input_visa_case_number_xpath = '//input[@name="ctl00$ContentPlaceHolder1$Visa_Case_Number"]'
location_drop_down_xpath = '//select[@name="ctl00$ContentPlaceHolder1$Location_Dropdown"]'
input_passport_number_xpath = '//input[@name="ctl00$ContentPlaceHolder1$Passport_Number"]'
input_surname_xpath = '//input[@name="ctl00$ContentPlaceHolder1$Surname"]'

img_captcha_xpath = '//img[@id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage"]'
input_captcha_xpath = '//input[@name="ctl00$ContentPlaceHolder1$Captcha"]'

submit_btn_xpath = '//img[@id="ctl00_ContentPlaceHolder1_imgFolder" and @alt="submit"]'

visa_status_xpath = '//div[@class="status"]/span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus"]'
visa_last_updated_xpath = '//td//span[@id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatusDate"]'