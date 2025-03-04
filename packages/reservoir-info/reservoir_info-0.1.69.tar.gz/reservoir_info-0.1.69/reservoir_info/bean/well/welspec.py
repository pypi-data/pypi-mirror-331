from dataclasses import dataclass, field

from mag_tools.bean.base_data import BaseData
from mag_tools.utils.data.list_utils import ListUtils

from reservoir_info.bean.well.well_segment import WellSegment
from reservoir_info.bean.well.template import Template

@dataclass
class Welspec(BaseData):
    """
    井资料
    """
    name: str = field(default=None, metadata={'description': '井名称'})
    segments: list = field(default_factory=list, metadata={'description': '井段列表'})
    template: Template = field(default=None, metadata={'description': '井信息列名'})

    @classmethod
    def from_block(cls, block_lines, template):
        if block_lines is None or len(block_lines) == 0:
            return None

        block_lines = ListUtils.trim(block_lines)

        well_name = block_lines[0].split()[1].replace("'", "")

        segments = []
        for line in block_lines[1:]:
            segment = WellSegment.from_text(line.strip(), template)
            segments.append(segment)

        return cls(name=well_name, segments=segments)

    def to_block(self):
        lines = [f"NAME '{self.name}'"]
        for segment in self.segments:
            lines.append(segment.to_text())

        return lines

if __name__ == '__main__':
    temp_lines = ["TEMPLATE",
            "'MARKER' 'I' 'J' 'K1' 'K2' 'OUTLET' 'WI' 'OS' 'SATMAP' 'HX' 'HY' 'HZ' 'REQ' 'SKIN' 'LENGTH' 'RW' 'DEV' 'ROUGH' 'DCJ' 'DCN' 'XNJ' 'YNJ' /"]
    temp = Template.from_block(temp_lines)

    well_lines =["NAME 'INJE1'",
        "''  24  25  11  11  NA  NA  SHUT  NA  0  0  0  NA  NA  NA  0.5  NA  NA  NA  1268.16  NA  NA",
        "''  24  25  11  15  NA  NA  OPEN  NA  0  0  DZ  NA  NA  NA  0.5  NA  NA  NA  0  NA  NA"]
    well_ = Welspec.from_block(well_lines, temp)
    print('\n'.join(well_.to_block()))
