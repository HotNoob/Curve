from .Graphing import Graphing
from .Root import Root

class UI:
    def __init__(self) -> None:
        self.Root : Root = Root()
        self.Graphing : Graphing = None

    def Load(self):
        ''' init non-root UI objects '''
        self.Graphing = Graphing()