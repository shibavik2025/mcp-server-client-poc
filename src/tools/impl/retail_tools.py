import json
from typing import Any, Dict, List

from src.core.logger import logger
from src.schemas.inventory import NoInput


class LoadInventoryTool:
    async def execute(self, _: NoInput) -> List[Dict[str, str]]:
        with open("data/inventory_data.json", "r") as f:
            inventory = json.load(f)
        logger.info("Loaded inventory data from JSON")
        return inventory


class ForecastedDemandTool:
    async def execute(self, _: NoInput) -> List[Dict[str, str]]:
        with open("data/inventory_data.json", "r") as f:
            inventory = json.load(f)
        logger.info("Calculating forecasted demand")
        return [
            {
                "product_id": item["product_id"],
                "location": item["location"],
                "forecasted_demand": str(item["forecasted_demand"])
            }
            for item in inventory
        ]


class ExpectedInventoryTool:
    async def execute(self, _: NoInput) -> List[Dict[str, str]]:
        with open("data/inventory_data.json", "r") as f:
            inventory = json.load(f)
        logger.info("Calculating expected inventory")
        return [
            {
                "product_id": item["product_id"],
                "location": item["location"],
                "expected_inventory": str(item["current_inventory"] - item["forecasted_demand"])
            }
            for item in inventory
        ]


class PromotionCandidateTool:
    async def execute(self, _: NoInput) -> List[Dict[str, str]]:
        with open("data/inventory_data.json", "r") as f:
            inventory = json.load(f)
        logger.info("Identifying promotion candidates")
        return [
            {
                "product_id": item["product_id"],
                "location": item["location"],
                "promotion_candidate": "Yes" if item.get("promotion_flag", False) else "No"
            }
            for item in inventory
        ]
