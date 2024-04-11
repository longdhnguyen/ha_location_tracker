import bigquery_wrapper
import json
import location_manager
import logging
import util
import schedule
import sys
import time

# Load Configuration from Home Assistant
CONFIG = {}
with open("/data/options.json", "r") as file:
    CONFIG.update(json.load(file))

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('bigquery_syncer')


def check_config() -> bool:
    required_keys = [
        "mysql_host", 
        "mysql_user", 
        "mysql_password", 
        "mysql_db", 
        "bigquery_project_id", 
        "bigquery_dataset_id" , 
        "bigquery_table_id", 
        "gcp_cred_file"
    ]
    return all(key in CONFIG for key in required_keys)


def sync_bigquery():
    locations = location_manager.LocationManager(
        CONFIG['mysql_host'], 
        CONFIG['mysql_user'], 
        CONFIG['mysql_password'], 
        CONFIG['mysql_db'])

    big_query_wrapper = bigquery_wrapper.BigQueryWrapper(CONFIG["bigquery_project_id"],
        CONFIG["bigquery_dataset_id"],
        CONFIG["bigquery_table_id"],
        CONFIG["gcp_cred_file"])
    
    bigquery_max_timestamp = big_query_wrapper.get_bigquery_max_timestamp()
    data = locations.retrieve_location_data(CONFIG['entity_id'], from_timestamp=bigquery_max_timestamp)
    data.sort(key=lambda row: row["timestamp"])
    timezone = CONFIG["timezone"]

    if data:
        debug_data = {
            "latest_bigquery_timestamp": util.to_local_full_format(bigquery_max_timestamp, timezone),
            "latest_unsynced_timestamp": util.to_local_full_format(data[-1]['timestamp'], timezone),
            "oldest_unsynced_timestamp": util.to_local_full_format(data[0]['timestamp'], timezone),
            "num_uploaded": len(data)
        }
        logger.info(debug_data)
        big_query_wrapper.upload_to_bigquery(data)
        logger.info("Upload completed.")
    else:
        logger.info("BigQuery location data is up-to-date.")

if __name__ == "__main__":
    if not check_config(): 
        logger.warning("BigQuery configuration not enabled. Program exiting.")
        sys.exit(0)

    sync_bigquery()
    schedule.every(3).hours.do(sync_bigquery)
    while True:
        schedule.run_pending()
        time.sleep(1)