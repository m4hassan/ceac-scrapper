from pyairtable import Table
import config as config


def update_airtable(visa_case_number, case_status, ceac_last_updated):
    table = Table(
        config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.AIRTABLE_TABLE_NAME
    )

    records = table.all(formula=f"{{Visa Case Number}} = '{visa_case_number}'")

    if not records:
        print(f"No records found for {visa_case_number}")
        return False

    record_id = records[0]["id"]

    # table.update(record_id, {
    #     "CEAC Last Updated": ceac_last_updated,
    #     "CEAC Status": case_status,
    # })

    print(f"Updated records for {record_id} - {visa_case_number}: {case_status}")
    return True
