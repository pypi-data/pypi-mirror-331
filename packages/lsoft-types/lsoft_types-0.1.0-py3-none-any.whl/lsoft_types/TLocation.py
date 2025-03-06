from typing import Optional, List

from pydantic import BaseModel


class LocationModel(BaseModel):
	addition: str = ""
	street: str = ""
	zipcode: str = ""
	city: str = ""
	country_code: str = ""
	pobox_number: str = ""
	location_type: str | None = ""
	uid: str = ""
