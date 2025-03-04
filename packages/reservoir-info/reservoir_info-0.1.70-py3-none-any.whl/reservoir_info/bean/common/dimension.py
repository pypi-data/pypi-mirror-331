from dataclasses import dataclass, field

from mag_tools.bean.base_data import BaseData
from mag_tools.utils.data.string_utils import StringUtils
from mag_tools.utils.data.list_utils import ListUtils


@dataclass
class Dimension(BaseData):
    nx: int = field(default=None, metadata={"description": "行数"})
    ny: int = field(default=None, metadata={"description": "列数"})
    nz: int = field(default=None, metadata={"description": "层数"})
    ngrid: int = field(default=None, metadata={"description": "总网格数"})

    @classmethod
    def from_block(cls, block_lines):
        if block_lines is None or len(block_lines) == 0:
            return None

        numbers = StringUtils.pick_numbers(ListUtils.trim(block_lines)[1])
        nx = numbers[0] if len(numbers) == 3 else None
        ny = numbers[1] if len(numbers) == 3 else None
        nz = numbers[2] if len(numbers) == 3 else None
        ngrid = numbers[0] if len(numbers) == 1 else None
        return cls(nx=nx, ny=ny, nz=nz, ngrid=ngrid)

    def to_block(self):
        if self.nx is not None and self.ny is not None and self.nz is not None and self.ngrid is not None:
            return []

        lines = ['DIMENS']
        if self.nx and self.ny and self.nz:
            lines.append(self.get_text(['nx', 'ny', 'nz']))
        elif self.ngrid:
            lines.append(f'{self.ngrid}')
        return lines