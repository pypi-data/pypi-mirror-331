from dataclasses import dataclass, field

import numpy as np
from mag_tools.bean.base_data import BaseData

from mag_tools.bean.text_format import TextFormat
from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.array_utils import ArrayUtils
from mag_tools.utils.data.list_utils import ListUtils


@dataclass
class Poro(BaseData):
    """
    指定参考压力下地层的孔隙度
    """
    nx: int = field(default=None, metadata={"description": "行数"})
    ny: int = field(default=None, metadata={"description": "列数"})
    nz: int = field(default=None, metadata={"description": "层数"})
    data: list = field(default_factory=list, metadata={"description": "数据"})

    def __post_init__(self):
        self._text_format = TextFormat(5, JustifyType.RIGHT, ' ', 3, 1)

    @classmethod
    def from_block(cls, block_lines, nx, ny, nz):
        """
        从一个文本块中生成 Poro
        :param nx: 网络的行数
        :param ny: 网络的列数
        :param nz: 网络的层数
        :param block_lines: 文本块，每行为一层的数值列表，如：600*0.087
        :return:
        """
        if block_lines is None or len(block_lines) == 0:
            return None

        block_lines = ListUtils.trim(block_lines)
        if len(block_lines) == 1:
            block_lines = block_lines[0].split()

        data = ArrayUtils.lines_to_array_3d(block_lines[1:], nx, ny, nz, float)
        return cls(nx=nx, ny=ny, nz=nz, data=data)

    def to_block(self):
        if self.data is None or len(self.data) == 0 or self.nx is None or self.ny is None or self.nz is None:
            return []

        lines = ['PORO']
        lines.extend(ArrayUtils.array_3d_to_lines(self.data, self._text_format))
        return lines

    def __str__(self):
        return "\n".join(self.to_block())

if __name__ == '__main__':
    _str = "PORO\n8*0.087\n8*0.097\n8*0.111"
    p = Poro.from_block(_str.split('\n'), 2,4, 3)
    print(p)

    _str = "PORO 8*0.087 8*0.097 8*0.111"
    p = Poro.from_block(_str.split('\n'), 2,4, 3)
    print(p)

    p = Poro(nx=3, ny=5, nz=21)
    print('\n'.join(p.to_block()))