from dataclasses import dataclass, field

import numpy as np
from mag_tools.bean.base_data import BaseData
from mag_tools.bean.text_format import TextFormat

from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.array_utils import ArrayUtils
from mag_tools.utils.data.list_utils import ListUtils

from reservoir_info.model.perm_type import PermType


@dataclass
class Perm(BaseData):
    perm_type: PermType = field(default=None, metadata={"description": "油藏网格xyz方向渗透率，实数"})
    nx: int = field(default=None, metadata={"description": "行数"})
    ny: int = field(default=None, metadata={"description": "列数"})
    nz: int = field(default=None, metadata={"description": "层数"})
    data: list = field(default_factory=list, metadata={"description": "数据"})

    def __post_init__(self):
        self._text_format = TextFormat(5, JustifyType.LEFT, '', 5, 1)

    @classmethod
    def from_block(cls, block_lines, nx, ny, nz):
        if block_lines is None or len(block_lines) == 0:
            return None

        block_lines = ListUtils.trim(block_lines)
        if len(block_lines) == 1:
            block_lines = block_lines[0].split()

        perm_type = PermType.of_code(block_lines[0])

        data = ArrayUtils.lines_to_array_3d(block_lines[1:], nx, ny, nz, float)
        return cls(perm_type=perm_type, nx=nx, ny=ny, nz=nz, data=data)

    def to_block(self):
        if self.data is None or len(self.data) == 0 or self.perm_type is None or self.nx is None or self.ny is None or self.nz is None:
            return []

        lines = [self.perm_type.code]
        lines.extend(ArrayUtils.array_3d_to_lines(self.data, self._text_format))

        return lines

# 示例用法
if __name__ == '__main__':
    x_lines = [
        'PERMX',
        '121*1.0 121*2.0 121*3.0 121*4.0 121*5.0'
        ]
    y_lines =[
        'PERMY',
        '49.29276 162.25308 438.45926 492.32336 791.32867',
        '704.17102 752.34912 622.96875 542.24493 471.45953',
        '246.12650 82.07828 82.87408 101.65224 57.53632',
        '47.73741 55.07134 24.33975 41.06571 76.64680',
        '158.22012 84.31137 98.32045 67.18009',
        '59.36459 32.75453 48.89822 78.56290 152.85838',
        '48.61450 45.90883 49.59706 87.95659 63.36467',
        '36.76624 22.82411 12.88787 7.30505 7.74248',
        '11.78211 23.77054 123.28667 618.79059 535.32922',
        '264.58759 387.70538 682.85431 823.64056',
        '390.34323 143.02039 110.37493 66.40274 26.82064',
        '41.63234 45.19296 44.07080 37.41025 25.15281',
        '42.34485 93.56773 142.41193 71.54111 66.90506',
        '100.64468 101.82140 50.54851 68.30826 103.03153',
        '120.99303 71.92981 59.36126 38.84483',
        '82.61102 86.39167 126.21329 36.41510 18.88533',
        '12.30760 10.19921 12.95491 14.53931 111.54144',
        '302.40686 343.12231 271.43484 319.10641 428.27557',
        '438.34317 161.91951 40.33082 51.97308 35.82761',
        '18.24838 30.81277 49.74974 42.04483',
        '39.99637 55.71049 63.62318 67.26822 73.98063',
        '45.19595 42.91018 75.42314 92.84066 123.21178',
        '104.16100 131.49677 77.80956 60.96303 34.25750',
        '34.32304 70.02726 74.91326 75.89129 57.44796',
        '18.24838 30.81277 49.74974 42.04483'
    ]

    _permx= Perm.from_block(x_lines, 11,11,5)
    _permy = Perm.from_block(y_lines, 4,6,5)

    print('\n'.join(_permx.to_block()))
    print('\n'.join(_permy.to_block()))

    p = Perm(perm_type=PermType.PERM_X, nx=3, ny=5, nz=21)
    print('\n'.join(p.to_block()))

