import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import config as config
from pyairtable import Table


def fetch_case_numbers():
    table = Table(
        config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.AIRTABLE_TABLE_NAME
    )

    all_records = []
    offset = None

    while True:
        records = table.all(fields=["Visa Case Number"], offset=offset)
        all_records.extend(
            record["fields"]["Visa Case Number"]
            for record in records
            if "Visa Case Number" in record["fields"]
        )

        # Airtable returns an 'offset' key in metadata if there's more data
        offset = records.offset if hasattr(records, 'offset') else None
        if not offset:
            break

    return all_records
