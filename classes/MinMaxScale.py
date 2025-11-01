

class MinMaxScale:
    def __init__(self, min : float, max : float, base : int):
        self.min : float = float(min)
        self.max : float = float(max)
        self.base : int = int(base)

    @classmethod
    def FromString(cls, scale : str) -> 'MinMaxScale':
        if ',' not in scale:
            return cls(0,0,0)

        scale.strip(' ')
        parts=scale.split(',')
        c_min=parts[0]
        c_max=parts[1]
        if len(parts)==3:
            c_base=parts[2]
        else:
            c_base=0

        return cls(c_min, c_max, c_base)

    def ToString(self : 'MinMaxScale') -> str:
        return f'{self.min:.9f},{self.max:.9f},{self.base}'