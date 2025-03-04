from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from mag_tools.bean.base_data import BaseData
from mag_tools.bean.text_format import TextFormat
from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.list_utils import ListUtils
from mag_tools.utils.data.array_utils import ArrayUtils


@dataclass
class DimensionValue(BaseData):
    dv_type: Optional[str] = field(default=None, metadata={"description": "维度数据类型"})
    nx: int = field(default=None, metadata={"description": "行数"})
    ny: int = field(default=None, metadata={"description": "列数"})
    nz: int = field(default=None, metadata={"description": "层数"})
    data: list = field(default_factory=list, metadata={"description": "数据"})

    def __post_init__(self):
        self.text_format = TextFormat(5, JustifyType.LEFT, ' ', 2, 0)

    @classmethod
    def from_block(cls, block_lines, nx: int, ny: int, nz: int):
        if block_lines is None or len(block_lines) == 0:
            return None

        block_lines = ListUtils.trim(block_lines)

        dv_type = block_lines[0].strip()
        data = ArrayUtils.lines_to_array_1d(block_lines[1:], int)
        return cls(dv_type=dv_type, nx=nx, ny=ny, nz=nz, data=data)

    def to_block(self):
        if self.data is None or len(self.data) == 0 or self.nx is None or self.ny is None or self.nz is None:
            return []

        lines = [self.dv_type]
        lines.extend(ArrayUtils.array_1d_to_lines(self.data, self.text_format))
        return lines


if __name__ == '__main__':
    # 示例用法
    _lines = [
        'DXV',
        ' 24*300'
    ]

    dv = DimensionValue.from_block(_lines, 2,3,4)
    print('\n'.join(dv.to_block()))
