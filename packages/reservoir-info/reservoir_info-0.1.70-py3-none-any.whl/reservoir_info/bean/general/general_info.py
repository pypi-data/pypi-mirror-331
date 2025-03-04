from dataclasses import dataclass, field
from typing import Optional

from mag_tools.bean.common.base_data import BaseData
from mag_tools.exception.app_exception import AppException
from mag_tools.model.common.unit_system import UnitSystem
from mag_tools.utils.data.list_utils import ListUtils

from reservoir_info.model.model_type import ModelType

@dataclass
class General(BaseData):
    """
    模型通用信息
    """
    module_type: ModelType = field(default=None, metadata={"description": "模型类型"})
    unit_system: Optional[UnitSystem] = field(default=None, metadata={"description": "单位制"})
    solnt: Optional[int] = field(default=None, metadata={"description": "OMP 并行线程数"})
    miscible: bool = field(default=False, metadata={"description": "是否打开混相相对渗透率模型"})
    diffuse: bool = field(default=False, metadata={"description": "是否启用组分扩散模型"})
    gravdr: bool = field(default=False, metadata={"description": "是否开启 gravity drainage 效应"})
    newton_chop: bool = field(default=False, metadata={"description": "是否开启牛顿迭代截断"})

    @classmethod
    def from_block(cls, block_lines):
        info = cls()

        block_lines = [line.strip().upper() for line in block_lines]

        type_line = ListUtils.pick_line_by_keyword(block_lines, "MODELTYPE")
        if type_line is None:
            raise AppException('模型类型不能为空')

        info.module_type = ModelType[type_line.split()[1].upper()]

        unit_line = ListUtils.pick_line_by_any_keyword(block_lines, ["METRIC", "FIELD", "LAB", "MESO"])
        info.unit_system = UnitSystem.of_code(unit_line) if unit_line is not None else None

        solnt_line = ListUtils.pick_line_by_keyword(block_lines, "SOLNT")
        info.solnt = int(solnt_line.split()[1]) if solnt_line is not None else None

        miscible_line = ListUtils.pick_line_by_keyword(block_lines, "MISCIBLE")
        info.miscible = miscible_line is not None

        diffuse_line = ListUtils.pick_line_by_keyword(block_lines, "DIFFUSE")
        info.diffuse = diffuse_line is not None

        gravdr_line = ListUtils.pick_line_by_keyword(block_lines, "GRAVDR")
        info.gravdr = gravdr_line is not None

        newton_chop_line = ListUtils.pick_line_by_keyword(block_lines, "NEWTONCHOP")
        info.newton_chop = newton_chop_line is not None

        return info

    def to_block(self):
        block_lines = [f'MODELTYPE {self.module_type.code}']

        if self.unit_system:
            block_lines.append(self.unit_system.name)
        if self.solnt is not None:
            block_lines.append(f'SOLNT {self.solnt}')
        if self.miscible:
            block_lines.append('MISCIBLE'.lower())
        if self.diffuse:
            block_lines.append('DIFFUSE')
        if self.gravdr:
            block_lines.append('GRAVDR')
        if self.newton_chop:
            block_lines.append('NEWTONCHOP')

        block_lines.append('')

        return block_lines

if __name__ == '__main__':
    _str = '''
MODELTYPE  COMP
SOLNT 2
METRIC
miscible    
    '''
    info_ = General.from_block(_str.split('\n'))
    print('\n'.join(info_.to_block()))