import json
import os
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Update the DATA_FILE path to be relative to the current file's directory
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "retails-mockdata.json")

def read_data() -> List[Dict]:
    if not os.path.exists(DATA_FILE):
        logger.warning(f"Data file {DATA_FILE} does not exist.")
        return []
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            logger.info(f"Data read successfully from {DATA_FILE}.")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {DATA_FILE}: {e}")
        return []

def write_data(data: List[Dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
        logger.info(f"Data written successfully to {DATA_FILE}.")

class MockInventoryTool:
    async def list_items(self) -> List[Dict]:
        data = read_data()
        logger.info(f"Listing items: {len(data)} items found.")
        return data

    async def add_item(self, item: Dict) -> Dict:
        data = read_data()
        data.append(item)
        write_data(data)
        logger.info(f"Item added: {item}")
        return item

    async def update_item(self, item_id: int, item: Dict) -> Optional[Dict]:
        data = read_data()
        if 0 <= item_id < len(data):
            data[item_id] = item
            write_data(data)
            logger.info(f"Item updated at index {item_id}: {item}")
            return item
        logger.warning(f"Update failed: No item at index {item_id}.")
        return None

    async def delete_item(self, item_id: int) -> Optional[Dict]:
        data = read_data()
        if 0 <= item_id < len(data):
            removed = data.pop(item_id)
            write_data(data)
            logger.info(f"Item deleted at index {item_id}: {removed}")
            return removed
        logger.warning(f"Delete failed: No item at index {item_id}.")
        return None
