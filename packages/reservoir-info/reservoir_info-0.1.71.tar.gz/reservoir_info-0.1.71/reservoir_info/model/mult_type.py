from mag_tools.model.base_enum import BaseEnum


class MultType(BaseEnum):
    MULT_X=('MULTX', '油藏网格 x 方向传导率乘数')
    MULT_Y=('MULTY', '油藏网格 y 方向传导率乘数')
    MULT_Z=('MULTZ', '油藏网格 z 方向传导率乘数')