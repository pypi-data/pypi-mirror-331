from dataclasses import dataclass, field
from typing import List

import numpy as np
from mag_tools.bean.common.base_data import BaseData
from mag_tools.bean.text_format import TextFormat

from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.array_utils import ArrayUtils
from mag_tools.utils.data.list_utils import ListUtils

from reservoir_info.model.mult_type import MultType


@dataclass
class Mult(BaseData):
    mult_type: MultType = field(metadata={"description": "油藏网格xyz方向传导率乘数，实数"})
    m: int = field(metadata={"description": "行或列数"})
    n: int = field(metadata={"description": "列或层数"})
    data: list = field(default_factory=list, metadata={"description": "数据"})

    def __post_init__(self):
        self._text_format = TextFormat(5, JustifyType.LEFT, '', 5, 1)

    @classmethod
    def from_block(cls, block_lines: List[str], m: int, n: int):
        if block_lines is None or len(block_lines) == 0:
            return None

        block_lines = ListUtils.trim(block_lines)
        mult_type = MultType.of_code(block_lines[0].strip())

        mult = cls(mult_type, m, n)
        mult.data = ArrayUtils.lines_to_array_2d(block_lines[1:], m, n, float)
        return mult

    def to_block(self):
        if self.data is None or len(self.data) == 0 or self.m is None or self.n is None:
            return []

        lines = [self.mult_type.code]
        lines.extend(ArrayUtils.array_2d_to_lines(self.data, self._text_format))

        return lines

    def __str__(self):
        return "\n".join(self.to_block())

# 示例用法
if __name__ == '__main__':
    x_str = '''
MULTX
1.0  1.0  1.0
1.2  1.2  1.2
1.0  1.0  1.0
1.5  1.5  1.5
1.0  1.0  1.0    
1.0  1.0  1.0
'''
    y_str ='''
MULTY
1.0  1.0  1.0
0.8  0.8  0.8
1.0  1.0  1.0
1.2  1.2  1.2
1.0  1.0  1.0    
    '''
    z_str = '''
MULTZ
1.0  1.0  1.0  1.0  1.0  1.0
1.0  1.5  1.5  1.5  1.0  1.0
1.0  1.0  1.0  1.0  1.0  1.0
1.0  1.0  1.0  1.0  1.0  1.0
1.0  1.5  1.5  1.5  1.0  1.0
'''

    _multx= Mult.from_block(x_str.split('\n'), 6,3)
    _multy = Mult.from_block(y_str.split('\n'), 5,3)
    _multz = Mult.from_block(z_str.split('\n'), 5, 6)

    print('\n'.join(_multx.to_block()))
    print('\n'.join(_multy.to_block()))
    print('\n'.join(_multz.to_block()))

    _m = Mult(mult_type=MultType.MULT_X, m=3,n=5)
    print('\n'.join(_m.to_block()))


