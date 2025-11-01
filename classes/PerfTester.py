import time

class PerfTester:
    def __init__(self) -> None:
        self.timers = {}

    def Start(self, name = ""):
        print("start : " + name)
        self.timers[name] = time.time()
        return

    def Clear(self, name = ""):
        del self.timers[name]
        return

    def Stop(self, name = ""):
        if(name not in self.timers):
            return
        
        result = time.time() - self.timers[name]
        print ("Stop : " + name)
        print(result)
        self.Clear(name)
        return