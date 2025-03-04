from dataclasses import dataclass, field

import numpy as np
from mag_tools.bean.common.base_data import BaseData

from mag_tools.bean.text_format import TextFormat
from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.array_utils import ArrayUtils
from mag_tools.utils.data.list_utils import ListUtils


@dataclass
class FipNum(BaseData):
    """
    指定 FIP 区域编号
    """
    nx: int = field(default=None, metadata={"description": "行数"})
    ny: int = field(default=None, metadata={"description": "列数"})
    nz: int = field(default=None, metadata={"description": "层数"})
    data: list = field(default_factory=list, metadata={"description": "数据"})

    def __post_init__(self):
        self.text_format = TextFormat(5, JustifyType.LEFT, '')

    @classmethod
    def from_block(cls, block_lines, nx, ny, nz):
        """
        从一个文本块中生成 FipNum
        :param nx: 网络的行数
        :param ny: 网络的列数
        :param nz: 网络的层数
        :param block_lines: 文本块
        :return:
        """
        if block_lines is None or len(block_lines) == 0:
            return None

        block_lines = ListUtils.trim(block_lines)
        if len(block_lines) == 1:
            block_lines = block_lines[0].split()

        data = ArrayUtils.lines_to_array_3d(block_lines[1:], nx, ny, nz, int)
        return cls(nx, ny, nz, data)

    def to_block(self):
        if self.data is None or len(self.data) == 0 or self.nx is None or self.ny is None or self.nz is None:
            return []

        lines = ['FIPNUM']
        lines.extend(ArrayUtils.array_3d_to_lines(self.data, self.text_format))
        return lines

    def __str__(self):
        return "\n".join(self.to_block())

if __name__ == '__main__':
    _str = "FIPNUM\n201 202 203\n204 205 206"
    p = FipNum.from_block(_str.split('\n'), 2, 3, 1)
    print(p)

    _str = "FIPNUM 201 202 203 204 205 206"
    p = FipNum.from_block(_str.split('\n'), 2, 3, 1)
    print(p)

    p = FipNum(nx=3, ny=5, nz=8)
    print(p)