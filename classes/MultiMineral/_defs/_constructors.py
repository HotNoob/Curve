# pylint: disable = not-callable
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from .. import MultiMineral

@classmethod
def newAnalysis(cls : Type['MultiMineral']) -> 'MultiMineral':
    new = cls()
    new.newSettingsMenu()
    return new