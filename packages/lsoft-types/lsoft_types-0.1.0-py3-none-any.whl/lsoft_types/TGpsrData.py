from pydantic import BaseModel

from lsoft_types.TAddress import TAddress
from lsoft_types.TLink import TLink


class TGpsrData(BaseModel, TAddress):
	link: TLink
