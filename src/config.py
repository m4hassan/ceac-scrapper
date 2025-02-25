import os
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
TWO_CAPTCHA_KEY = os.getenv("TWO_CAPTCHA_KEY")
SLACK_AUTH_TOKEN = os.getenv("SLACK_AUTH_TOKEN")