from enum import Enum

class Sweep(Enum):
    INCREASING = 1
    DECREASING = -1

    __inc_aliases_set = frozenset(('up', 'inc', 'increasing'))
    __dec_aliases_set = frozenset(('down', 'dec', 'decreasing'))

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.strip().lower()
            if value in cls.__inc_aliases_set:
                return cls.INCREASING
            elif value in cls.__dec_aliases_set:
                return cls.DECREASING
    
    def __eq__(self, other):
        if isinstance(other, str):
            other = self._missing_(other)
        return super().__eq__(other)
        

print(Sweep(1))
try:
    Sweep('a')
except ValueError as e:
    print(e)

print(Sweep('dec'))
print(Sweep(1) == Sweep(-1))
print(Sweep(1) == 'up')
print('u' == Sweep(1))