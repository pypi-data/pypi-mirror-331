from dataclasses import dataclass, field
import numpy as np

from mag_tools.bean.base_data import BaseData
from mag_tools.bean.text_format import TextFormat

from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.array_utils import ArrayUtils
from mag_tools.utils.data.list_utils import ListUtils


@dataclass
class Tops(BaseData):
    """
    第一层网格的顶面深度，用于结构网格
    实数，数据个数等于第一层网格的网格数
    单位：m (米制)，feet (英制)，cm (lab)，um(MESO)
    """
    nx: int = field(default=None, metadata={'description': '行数'})
    ny: int = field(default=None, metadata={'description': '列数'})
    data: list = field(default_factory=list, metadata={"description": "数据"})

    def __post_init__(self):
        self._text_format = TextFormat(5, JustifyType.RIGHT, ' ', 2, 2)

    @classmethod
    def from_block(cls, block_lines: list[str], nx: int, ny: int):
        """
        将文本行转为Tops
        :param block_lines: 文本块
        :param nx: 网络行数
        :param ny: 网络列数
        :return: Tops
        """
        if block_lines is None or len(block_lines) == 0:
            return None

        block_lines = ListUtils.trim(block_lines)
        if len(block_lines) == 1:
            block_lines = block_lines[0].split()

        data = ArrayUtils.lines_to_array_2d(block_lines[1:], nx, ny, float)
        return cls(nx=nx, ny=ny, data=data)

    def to_block(self):
        if self.data is None or len(self.data) == 0 or self.nx is None or self.ny is None:
            return []

        lines = ['TOPS']
        lines.extend(ArrayUtils.array_2d_to_lines(self.data, self._text_format))
        return lines

if __name__ == "__main__":
    txt = 'TOPS 600*9000.00'
    _tops = Tops.from_block(txt.split('\n'), 20, 30)
    print('\n'.join(_tops.to_block()))

    txt = 'TOPS\n 600*9000.00'
    _tops = Tops.from_block(txt.split('\n'), 20, 30)
    print('\n'.join(_tops.to_block()))

    _tops = Tops(nx=3, ny=5)
    print('\n'.join(_tops.to_block()))
