import os
from typing import Any, Dict, Union
import json
import pandas as pd

from src.tools.meta.base import BaseTool
from src.schemas.inventory import NoInput  # You'll define this schema (empty model)
from src.core.logger import logger

# Define the absolute path to the Excel file
INVENTORY_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'inventory.xlsx')


def load_inventory():
    """Load inventory data from the Excel file."""
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(INVENTORY_FILE_PATH)
        logger.info("Inventory data loaded successfully.")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {INVENTORY_FILE_PATH}")
        raise
    except Exception as e:
        logger.error(f"Error loading inventory data: {str(e)}")
        raise

class LoadInventoryTool(BaseTool[NoInput]):
    @property
    def name(self) -> str:
        return "load_inventory"

    @property
    def description(self) -> str:
        return "Loads the inventory data from the Excel file."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, input_data: NoInput, *args: Any) -> Any:
        try:
            df = load_inventory()
            result = df.to_dict(orient="records")
            logger.info("Execute- Loaded inventory data from Excel")
            return json.dumps({"function": self.name, "data": result})
        except Exception as e:
            logger.error(f"Execution error: {str(e)}")
            raise
