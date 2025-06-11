import json
from typing import List, Dict, Optional

DATA_FILE = "data/retails-mockdata.json"

def read_data() -> List[Dict]:
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_data(data: List[Dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

class MockInventoryTool:
    async def list_items(self) -> List[Dict]:
        return read_data()

    async def add_item(self, item: Dict) -> Dict:
        data = read_data()
        data.append(item)
        write_data(data)
        return item

    async def update_item(self, item_id: int, item: Dict) -> Optional[Dict]:
        data = read_data()
        if 0 <= item_id < len(data):
            data[item_id] = item
            write_data(data)
            return item
        return None

    async def delete_item(self, item_id: int) -> Optional[Dict]:
        data = read_data()
        if 0 <= item_id < len(data):
            removed = data.pop(item_id)
            write_data(data)
            return removed
        return None