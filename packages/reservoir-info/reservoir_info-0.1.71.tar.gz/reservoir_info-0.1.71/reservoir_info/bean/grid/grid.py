from dataclasses import dataclass, field
from typing import Optional

from mag_tools.bean.common.base_data import BaseData
from mag_tools.utils.data.list_utils import ListUtils

from reservoir_info.bean.grid.mult import Mult

from reservoir_info.bean.grid.porv import Porv
from reservoir_info.bean.grid.nmatopts import Nmatopts
from reservoir_info.model.nmatopts_type import NmatoptsType
from reservoir_info.bean.grid.multiporo import Multiporo
from reservoir_info.bean.common.box import Box
from reservoir_info.bean.common.copy_grid import CopyGrid
from reservoir_info.bean.common.dimension import Dimension
from reservoir_info.bean.grid.dimension_value import DimensionValue
from reservoir_info.bean.grid.fipnum import FipNum
from reservoir_info.bean.grid.perm import Perm
from reservoir_info.bean.grid.poro import Poro
from reservoir_info.bean.grid.tops import Tops
from reservoir_info.model.perm_type import PermType


@dataclass
class Grid(BaseData):
    dimens: Optional[Dimension] = field(default=None, metadata={"description": "油藏网格数"})
    multiporo: Optional[Multiporo] = field(default=None, metadata={"description": "多重网格"})
    nmatopts: Optional[Nmatopts] = field(default=NmatoptsType.GEOMETRIC, metadata={"description": "各层基质的体积比例"})
    fipnum: Optional[FipNum] = field(default=None, metadata={"description": "区域编号"})
    permx: Optional[Perm] = field(default=None, metadata={"description": "油藏网格 x 方向渗透率"})
    permy: Optional[Perm] = field(default=None, metadata={"description": "油藏网格 y 方向渗透率"})
    permz: Optional[Perm] = field(default=None, metadata={"description": "油藏网格 z 方向渗透率"})
    multx: Optional[Mult] = field(default=None, metadata={"description": "油藏网格 x 方向传导率乘数"})
    multy: Optional[Mult] = field(default=None, metadata={"description": "油藏网格 y 方向传导率乘数"})
    multz: Optional[Mult] = field(default=None, metadata={"description": "油藏网格 z 方向传导率乘数"})
    poro: Optional[Poro] = field(default=None, metadata={"description": "指定参考压力下地层的孔隙度"})
    porv: Optional[Poro] = field(default=None, metadata={"description": "指定参考压力下网格的孔隙体积"})
    dxv: Optional[Perm] = field(default=None, metadata={"description": "指定网格 x 方向的长度"})
    dyv: Optional[Perm] = field(default=None, metadata={"description": "指定网格 y 方向的长度"})
    dzv: Optional[Perm] = field(default=None, metadata={"description": "指定网格 z 方向的长度"})
    tops: Optional[Perm] = field(default=None, metadata={"description": "顶面深度"})

    @classmethod
    def from_block(cls, block_lines):
        if block_lines is None or len(block_lines) == 0:
            return None

        grid = cls()
        dimens_lines = ListUtils.pick_block_by_keyword(block_lines, 'DIMENS', 2)
        grid.dimens = Dimension.from_block(dimens_lines)

        multiporo_lines = ListUtils.pick_block_by_keyword(block_lines, 'MULTIPORO', 2)
        grid.multiporo = Multiporo.from_block(multiporo_lines) if multiporo_lines else None

        nmatopts_line = ListUtils.pick_line_by_keyword(block_lines, 'NMATOPTS')
        grid.nmatopts = Nmatopts.from_block(nmatopts_line) if nmatopts_line else None

        # 根据网络数初始化fip_num和permx/permy/permz
        grid.fip_num = FipNum(grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)
        grid.permx = Perm(perm_type=PermType.PERM_X, nx=grid.dimens.nx, ny=grid.dimens.ny, nz=grid.dimens.nz)
        grid.permy = Perm(perm_type=PermType.PERM_Y, nx=grid.dimens.nx, ny=grid.dimens.ny, nz=grid.dimens.nz)
        grid.permz = Perm(perm_type=PermType.PERM_Z, nx=grid.dimens.nx, ny=grid.dimens.ny, nz=grid.dimens.nz)

        # FIP 区域编号
        fipnum_line = ListUtils.pick_block(block_lines, 'FIPNUM', '')
        grid.fipnum = FipNum.from_block(fipnum_line, grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)

        # 渗透率
        permx_lines = ListUtils.pick_block(block_lines, 'PERMX', '')
        grid.permx = Perm.from_block(permx_lines, grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)

        permy_lines = ListUtils.pick_block(block_lines, 'PERMY', '')
        grid.permy = Perm.from_block(permy_lines, grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)

        permz_lines = ListUtils.pick_block(block_lines, 'PERMZ', '')
        grid.permz = Perm.from_block(permz_lines, grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)

        # 传导率乘数
        multx_lines = ListUtils.pick_block(block_lines, 'MULTX', '')
        grid.multx = Mult.from_block(multx_lines, grid.dimens.ny, grid.dimens.nz)

        multy_lines = ListUtils.pick_block(block_lines, 'MULTY', '')
        grid.multy = Mult.from_block(multy_lines, grid.dimens.nx, grid.dimens.nz)

        multz_lines = ListUtils.pick_block(block_lines, 'MULTZ', '')
        grid.multz = Mult.from_block(multz_lines, grid.dimens.nx, grid.dimens.ny)

        # 孔隙度
        poro_line = ListUtils.pick_block(block_lines, 'PORO', '')
        grid.poro = Poro.from_block(poro_line, grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)

        # 孔隙体积
        porv_line = ListUtils.pick_block(block_lines, 'PORV', '')
        grid.porv = Porv.from_block(porv_line, grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)

        # xyz方向的长度
        dxv_lines = ListUtils.pick_block(block_lines, 'DXV', '')
        grid.dxv = DimensionValue.from_block(dxv_lines, grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)

        dyv_lines = ListUtils.pick_block(block_lines, 'DYV', '')
        grid.dyv = DimensionValue.from_block(dyv_lines, grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)

        dzv_lines = ListUtils.pick_block(block_lines, 'DZV', '')
        grid.dzv = DimensionValue.from_block(dzv_lines, grid.dimens.nx, grid.dimens.ny, grid.dimens.nz)

        # 顶面深度
        tops_lines = ListUtils.pick_block(block_lines, 'TOPS', '')
        grid.tops = Tops.from_block(tops_lines, grid.dimens.nx, grid.dimens.ny)

        for line in block_lines:
            if line.startswith('BOX'):
                box = Box.from_text(line)
                array = grid.get_array(box.var_name)
                grid.set_array(box.var_name, box.calculate(array))
            elif line.startswith('COPY'):
                copy = CopyGrid.from_text(line)
                source_array = grid.get_array(copy.source_name)
                target_array = grid.get_array(copy.target_name)
                grid.set_array(copy.target_name, copy.calculate(source_array, target_array))
        return grid

    def to_block(self) -> list[str]:
        lines = ['GRID','##################################################']
        lines.extend(self.dimens.to_block())
        lines.append("")

        if self.multiporo is not None:
            lines.extend(self.multiporo.to_block())
            lines.append("")

        if self.nmatopts is not None:
            lines.extend(self.nmatopts.to_block())
            lines.append("")

        if self.fipnum is not None:
            lines.extend(self.fipnum.to_block())
            lines.append("")

        if self.multx is not None:
            lines.extend(self.multx.to_block())
            lines.append("")
        if self.multy is not None:
            lines.extend(self.multy.to_block())
            lines.append("")
        if self.multz is not None:
            lines.extend(self.multz.to_block())
            lines.append("")

        if self.permx is not None:
            lines.extend(self.permx.to_block())
            lines.append("")
        if self.permy is not None:
            lines.extend(self.permy.to_block())
            lines.append("")
        if self.permz is not None:
            lines.extend(self.permz.to_block())
            lines.append("")

        if self.poro is not None:
            lines.extend(self.poro.to_block())
            lines.append("")

        if self.porv is not None:
            lines.extend(self.porv.to_block())
            lines.append("")

        if self.dxv is not None:
            lines.extend(self.dxv.to_block())
            lines.append("")

        if self.dyv is not None:
            lines.extend(self.dyv.to_block())
            lines.append("")

        if self.dzv is not None:
            lines.extend(self.dzv.to_block())
            lines.append("")

        if self.tops is not None:
            lines.extend(self.tops.to_block())
            lines.append("")

        lines.append('#GRID END#########################################')
        return lines

    def get_array(self, var_type):
        _var = None
        if var_type == 'PERMX':
            _var = self.permx.data
        elif var_type == 'PERMY':
            _var = self.permy.data
        elif var_type == 'PERMZ':
            _var = self.permz.data
        elif var_type == 'FIPNUM':
            _var = self.fipnum.data
        elif var_type == 'TOPS':
            _var = self.tops.data
        return _var

    def set_array(self, var_type, value):
        if var_type == 'PERMX':
            self.permx.data = value
        elif var_type == 'PERMY':
            self.permy.data = value
        elif var_type == 'PERMZ':
            self.permz.data = value
        elif var_type == 'FIPNUM':
            self.fipnum.data = value
        elif var_type == 'TOPS':
            self.tops.data = value

if __name__ == '__main__':
    str_ = '''
GRID
DIMENS
7 7 3

DXV
7*500

DYV
7*500

DZV
20 30 50

TOPS
49*8325

PORO
147*0.3

PERMX
49*500 49*50 49*200

PERMY
49*500 49*50 49*200

PERMZ
 49*50 49*50 49*25
    '''
    grid_ = Grid.from_block(str_.split('\n'))
    print('\n'.join(grid_.to_block()))