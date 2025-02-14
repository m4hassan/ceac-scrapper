import sys
import os
import config as config
from pyairtable import Table
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

logger = logging.getLogger(__name__)


def fetch_case_numbers():
    table = Table(
        config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.AIRTABLE_TABLE_NAME
    )

    all_records = set()
    offset = None

    while True:
        records = table.all(fields=["Visa Case Number"], offset=offset)
        all_records.update(
            record["fields"]["Visa Case Number"]
            for record in records
            if "Visa Case Number" in record["fields"]
        )

        # Airtable returns an 'offset' key in metadata if there's more data
        offset = records.offset if hasattr(records, 'offset') else None
        if not offset:
            break

    return list(all_records)


def update_airtable(visa_case_number, case_status, ceac_last_updated):
    table = Table(
        config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.AIRTABLE_TABLE_NAME
    )

    try:
        records = table.all(formula=f"{{Visa Case Number}} = '{visa_case_number}'")

        if not records:
            logger.warning(f"No records found for {visa_case_number}")
            return False

        record_id = records[0]["id"]

        table.update(record_id, {
            "CEAC Last Updated": ceac_last_updated,
            "CEAC Status": case_status,
        })

        logger.info(f"Updated record for {record_id} - {visa_case_number}: {case_status}")
        return True

    except Exception as e:
        logger.error(f"Failed to update Airtable for {visa_case_number}: {str(e)}")
        return False

