from typing import Type

from dataclasses import dataclass

from classes.JsonObject import JsonObject

@dataclass
class FormationInfo(JsonObject):
    uwi : str = ''
    name : str = ''
    source : str = ''
    depth : float = ''


