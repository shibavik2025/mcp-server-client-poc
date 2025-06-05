"""Version Schema"""

from typing import Optional

from pydantic import BaseModel


class VersionResponse(BaseModel):
    """version response"""

    name: str
    version: str
    commit: Optional[str] = ""
    branch: Optional[str] = ""
    buildTime: Optional[str] = ""
    tag: Optional[str] = ""
