"""Schema for the example tool."""

from typing import Optional
from pydantic import BaseModel, Field


class ExampleToolInput(BaseModel):
    """
    Input schema model for the example tool.

    This example input schema has two required fields (query and workspace_id)
    and one optional field (workflow_id).

    Note: For optional fields you need to explicitly describe when and why to
    include it in the tool call request.
    """

    query: str = Field(..., description="The search query.")
    workspace_id: str = Field(..., description="The ID of the workspace to search.")
    workflow_id: Optional[str] = Field(
        None,
        description="""The ID of the workflow to search.
        If you know the workflow_id, provide it to include specific workflow information
        in the search results as well.""",
    )
