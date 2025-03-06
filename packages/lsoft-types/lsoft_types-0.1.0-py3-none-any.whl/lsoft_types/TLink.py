from typing import Dict

from pydantic import BaseModel, Field


class TLink(BaseModel):
	url: Dict[str, str] | None = Field(default_factory=dict)
	caption: Dict[str, str] | None = Field(default_factory=dict)
