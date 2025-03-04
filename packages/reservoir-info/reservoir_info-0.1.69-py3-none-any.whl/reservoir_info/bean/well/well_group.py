from dataclasses import dataclass, field
from typing import List, Optional

from mag_tools.bean.common.base_data import BaseData
from mag_tools.utils.data.list_utils import ListUtils

from reservoir_info.bean.well.welspec import Welspec
from reservoir_info.bean.well.template import Template


@dataclass
class WellGroup(BaseData):
    """
    井资料，支持正交网格、角点网格、GPG 网格
    """
    template: Optional[Template] = field(default=None, metadata={'description': '模板'})
    welspecs: List[Welspec] = field(default_factory=list, metadata={'description': '井资料列表'})

    @classmethod
    def from_block(cls, block_lines):
        """
        从文本块中得到WellSpecs
        """
        if block_lines is None or len(block_lines) == 0:
            return None

        block_lines = ListUtils.trim(block_lines)

        template_lines = ListUtils.pick_block(block_lines, 'TEMPLATE', 'WELSPECS')
        template = Template.from_block(template_lines)

        welspecs = []
        specs_lines = ListUtils.pick_tail(block_lines, 'WELSPECS')
        if specs_lines:
            specs_lines.pop(0)
            welspec_blocks = ListUtils.split_by_empty_line(specs_lines)
            for welspec_block in welspec_blocks:
                welspec = Welspec.from_block(welspec_block, template)
                welspecs.append(welspec)

        return cls(template=template, welspecs=welspecs)

    def to_block(self):
        lines = ['WELL', '##################################################','']
        lines.extend(self.template.to_block())
        lines.append('WELSPECS')
        for spec in self.welspecs:
            lines.extend(spec.to_block())
            lines.append('')
        lines.append('#WELL END#########################################')
        return lines

if __name__ == '__main__':
    well_lines = ["WELL",
         "",
         "TEMPLATE",
         "'MARKER' 'I' 'J' 'K1' 'K2' 'OUTLET' 'WI' 'OS' 'SATMAP' 'HX' 'HY' 'HZ' 'REQ' 'SKIN' 'LENGTH' 'RW' 'DEV' 'ROUGH' 'DCJ' 'DCN' 'XNJ' 'YNJ' /",
         "WELSPECS",
         "NAME 'INJE1'",
         "''  24  25  11  11  NA  NA  SHUT  NA  0  0  0  NA  NA  NA  0.5  NA  NA  NA  1268.16  NA  NA",
         "''  24  25  11  15  NA  NA  OPEN  NA  0  0  DZ  NA  NA  NA  0.5  NA  NA  NA  0  NA  NA",
         "",
         "NAME 'PROD2'",
         "''  5  1  2  2  NA  NA  OPEN  NA  0  0  DZ  NA  0  NA  0.5  0  0  NA  NA  NA  NA",
         "''  5  1  3  3  NA  NA  OPEN  NA  0  0  DZ  NA  0  NA  0.5  0  0  NA  NA  NA  NA",
         "''  5  1  4  4  NA  NA  OPEN  NA  0  0  DZ  NA  0  NA  0.5  0  0  NA  NA  NA  NA"]
    well = WellGroup.from_block(well_lines)
    print('\n'.join(well.to_block()))