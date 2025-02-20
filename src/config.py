from environ import Env

env = Env()
env.read_env()

# AIRTABLE_API_KEY = env.str("AIRTABLE_API_KEY")
# AIRTABLE_BASE_ID = env.str("AIRTABLE_BASE_ID")
# AIRTABLE_TABLE_NAME = env.str("AIRTABLE_TABLE_NAME")
# TWO_CAPTCHA_KEY = env.str("TWO_CAPTCHA_KEY")
# SLACK_AUTH_TOKEN = env.str("SLACK_AUTH_TOKEN")