from typing import Optional, List

from pydantic import BaseModel, Field


class ContactModel(BaseModel):
	email: str | None = ""
	firstname: str
	lastname: str
	department: str | None = ""
	telephone1: str | None = ""
	telephone2: str | None = ""
	fax: str | None = ""
	password: str | None = ""
	language_code: str | None = ""
	origin_selling_platform: str | None = ""
	contact_type: str | None = ""
	title: str | None = ""
	contact_flags: List[str] | None = Field(default_factory=list)
	hashes: List[str] | None = []
	uid: str
