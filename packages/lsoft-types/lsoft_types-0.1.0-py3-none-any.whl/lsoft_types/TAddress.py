# from pydantic import ConfigDict, BaseModel, Field
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class AddressTypeEnum(str, Enum):
	STANDARD = "STANDARD"
	DELIVERY = "DELIVERY"
	INVOICE = "INVOICE"
	SENDER = "SENDER"
	CREATOR = "CREATOR"
	QUOTE = "QUOTE"


class TAddress(BaseModel):
	firstname: str | None = ""
	lastname: str | None = ""
	company: str | None = ""
	department: str | None = ""
	addition: str | None = ""
	street: str | None = ""
	city: str | None = ""
	zipcode: str | None = ""
	country_code: str | None = ""
	pobox_number: str | None = ""
	address_types: List[AddressTypeEnum] = Field(default_factory=list)
	email: str | None = Field(None, nullable=True)
	uid: str | None = None
	model_config = ConfigDict(use_enum_values=True)

	telephone1: str | None = None
	telephone2: str | None = None
