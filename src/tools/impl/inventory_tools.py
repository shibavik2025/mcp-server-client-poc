from typing import Any, Dict, List, Union
import json
import pandas as pd

from src.tools.meta.base import BaseTool
from src.schemas.inventory import NoInput  # You'll define this schema (empty model)
from src.utils.auth import get_authorization_token
from src.utils.ent_headers import add_ent_headers
from src.core.logger import logger

INVENTORY_FILE_PATH = "inventory.xlsx"

# Load Excel data once (or load inside each tool if dynamic reload needed)

def load_inventory():
    return pd.read_excel("inventory.xlsx")


class LoadInventoryTool(BaseTool[NoInput]):
    @property
    def name(self) -> str:
        return "load_inventory"

    @property
    def description(self) -> str:
        return "Loads the inventory data."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, input_data: NoInput, *args: Any) -> Any:
        # Example mock response
        return [{"item_id": "ABC123", "quantity": 10}]



class ForecastedDemandTool(BaseTool[NoInput]):
    @property
    def name(self) -> str:
        return "forecasted_demand"

    @property
    def description(self) -> str:
        return "Returns demand forecast for all items."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    async def execute(
        self, input_data: Union[NoInput, Dict[str, Any]], *args: Any
    ) -> Any:
        request_headers = args[0] if args else {}

        df = load_inventory()
        result = df[["Product Category", "Item", "Forecasted Demand"]].to_dict(orient="records")

        logger.info(f"{self.name} executed successfully with result size: {len(result)}")
        return json.dumps({"function": self.name, "data": result})


class ExpectedInventoryTool(BaseTool[NoInput]):
    @property
    def name(self) -> str:
        return "expected_inventory"

    @property
    def description(self) -> str:
        return "Returns expected inventory by warehouse."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    async def execute(
        self, input_data: Union[NoInput, Dict[str, Any]], *args: Any
    ) -> Any:
        request_headers = args[0] if args else {}

        df = load_inventory()
        result = df[
            ["Product Category", "Item", 
             "Expected Inventory WH1", "Expected Inventory WH2", "Expected Inventory WH3"]
        ].to_dict(orient="records")

        logger.info(f"{self.name} executed successfully with result size: {len(result)}")
        return json.dumps({"function": self.name, "data": result})


class PromotionCandidateTool(BaseTool[NoInput]):
    @property
    def name(self) -> str:
        return "promotion_candidates"

    @property
    def description(self) -> str:
        return "Returns items with High DSI and Supplier Deal both Yes."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    async def execute(
        self, input_data: Union[NoInput, Dict[str, Any]], *args: Any
    ) -> Any:
        request_headers = args[0] if args else {}

        df = load_inventory()
        filtered = df[(df["High DSI"] == "Yes") & (df["Supplier Deal"] == "Yes")]
        result = filtered[["Product Category", "Item"]].to_dict(orient="records")

        logger.info(f"{self.name} executed successfully with result size: {len(result)}")
        return json.dumps({"function": self.name, "data": result})
