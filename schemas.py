from typing import List, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    url: str  = Field(...,description="The URL of the source")
    title: Optional[str] = Field(None, description="The title of the source")
    content_preview: Optional[str] = Field(None, description="Preview of the content")

class AgentResponse(BaseModel):
    answer: str = Field(..., description="The final answer to the user's question.")
    sources: List[Source] = Field(
        default_factory= list, 
        description="A list of sources used to generate the answer.")
    
    raw_data: Optional[str] = Field(None, description="Raw JSON data from the URL if requested")