from dataclasses import dataclass, field

from mag_tools.bean.base_data import BaseData
from mag_tools.utils.data.list_utils import ListUtils
from mag_tools.utils.data.string_utils import StringUtils


@dataclass
class Multiporo(BaseData):
    nl: int = field(default=None, metadata={"description": "总网格重数"})
    nwp: int = field(default=None, metadata={"description": "井与多重网格连接的控制参数"})
    np: int = field(default=None, metadata={"description": "可渗透的网格重数"})

    @classmethod
    def from_block(cls, block_lines):
        if block_lines is None or len(block_lines) == 0:
            return None

        clazz = cls()

        block_lines = ListUtils.trim(block_lines)
        if len(block_lines) == 2:
            numbers = StringUtils.pick_numbers(block_lines[1])
            clazz.nl = numbers[0]
            clazz.nwp = numbers[1]
            clazz.np = numbers[2]
        return clazz

    def to_block(self):
        if self.nl is None and self.nwp is None and self.np is None:
            return []

        return ['MULTIPORO', f'{self.nl} \t{self.nwp} \t{self.np}']

if __name__ == '__main__':
    str_ = '''
MULTIPORO 
2 1 1     
    '''
    poro = Multiporo.from_block(str_.split('\n'))
    print('\n'.join(poro.to_block()))

    poro = Multiporo()
    print('\n'.join(poro.to_block()))