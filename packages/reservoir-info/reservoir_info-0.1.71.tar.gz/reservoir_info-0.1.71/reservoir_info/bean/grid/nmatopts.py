from dataclasses import dataclass,field
from typing import List

from mag_tools.bean.base_data import BaseData
from mag_tools.utils.data.string_utils import StringUtils
from mag_tools.utils.data.list_utils import ListUtils

from reservoir_info.model.nmatopts_type import NmatoptsType


@dataclass
class Nmatopts(BaseData):
    nmatopts_type: NmatoptsType = field(default=NmatoptsType.GEOMETRIC, metadata={"description": "体积比例类型"})
    proportions: List[float] = field(default_factory=list, metadata={"description": "各层基质的体积比例"})

    @classmethod
    def from_block(cls, block_lines):
        if block_lines is None or len(block_lines) == 0:
            return None

        block_lines = ListUtils.trim(block_lines)
        nmatopts_type = NmatoptsType.of_code(block_lines[1])
        nmatopts_type = NmatoptsType.DESIGNATED if nmatopts_type is None else nmatopts_type
        proportions = [StringUtils.to_value(value, float) for value in block_lines[1].split()] if nmatopts_type is None else None

        return cls(nmatopts_type=nmatopts_type, proportions=proportions)

    def to_block(self):
        lines = ['NMATOPTS']
        if self.nmatopts_type == NmatoptsType.DESIGNATED:
            lines.append(' '.join([str(value) for value in self.proportions]))
        else:
            lines.append(self.nmatopts_type.code)
        return lines

if __name__ == '__main__':
    value_str = '''
NMATOPTS
UNIFORM
'''
    data_ = Nmatopts.from_block(value_str.split('\n'))
    print('\n'.join(data_.to_block()))

    value_str = '''
NMATOPTS
0.2 0.3 0.5
    '''
    data_ = Nmatopts.from_block(value_str.split('\n'))
    print('\n'.join(data_.to_block()))
