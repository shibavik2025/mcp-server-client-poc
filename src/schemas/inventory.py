from pydantic import BaseModel

class NoInput(BaseModel):
    """Empty schema for tools with no input"""
    pass
