from typing import List, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    url: str  = Field(...,description="The URL of the source")

class AgentResponseMain(BaseModel):
    """Schema for agent response with answer and sources"""

    answer: str = Field(description="The agent's answer to the query")
    sources: List[Source] = Field(
        default_factory=list, description="List of sources used to generate the answer"
    )

class CryptoData(BaseModel):
    name: str
    symbol: str
    price: str
    change_24h: str
    market_cap: str
    volume_24h: str
    rank: int  # Change this from str to int



class AgentResponse(BaseModel):
    answer: str
    sources: List[str] = []
    crypto_data: List[CryptoData] = []
    raw_data: Optional[str] = None