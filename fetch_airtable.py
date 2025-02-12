import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import config
from pyairtable import Table

def fetch_case_numbers():
    table = Table(config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.AIRTABLE_TABLE_NAME)
    records = table.all(fields=["Visa Case Number"])

    return [record["fields"]["Visa Case Number"] for record in records if "Visa Case Number" in record["fields"]]
