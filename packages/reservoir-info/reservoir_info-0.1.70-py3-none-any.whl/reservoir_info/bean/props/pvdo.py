from dataclasses import dataclass, field
from typing import List

from mag_tools.bean.common.base_data import BaseData
from mag_tools.bean.data_format import DataFormat
from mag_tools.bean.text_format import TextFormat
from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.list_utils import ListUtils
from mag_tools.utils.data.string_format import StringFormat
from mag_tools.utils.data.string_utils import StringUtils


@dataclass
class Pvdo(BaseData):
    p: float = field(default=None, metadata={'description': '压力,单位：bar(米制)，psi(英制)，atm(lab)，Pa(MESO)'})
    bo: float = field(default=None, metadata={'description': '油的体积系数,单位：rm3/sm3(米制)，rb/stb(英制)，cm3/cm3(lab)，um3/um3(MESO)'})
    visc: float = field(default=None, metadata={'description': '油的粘度,单位：cP'})

    def __post_init__(self):
        self._data_formats = {
            'p': DataFormat(decimal_places=1, decimal_places_of_zero=1),
            'bo': DataFormat(decimal_places=4, decimal_places_of_zero=1),
            'visc': DataFormat(decimal_places=6, decimal_places_of_zero=1)
        }

    @classmethod
    def from_text(cls, text, titles: List[str]):
        items = text.split()
        values = {title.lower().strip(): StringUtils.to_value(items[index], float) for
                  index, title in enumerate(titles)}
        return cls(**values)

    def to_text(self, titles: List[str], pad_length: int) -> str:
        items = [StringFormat.format_number(getattr(self, title.lower()), self._data_formats[title.lower()]) for title in titles]
        return StringFormat.pad_values(items, pad_length, JustifyType.LEFT)

    @property
    def max_length(self):
        return max(len(str(value)) for value in [self.p, self.bo, self.visc] if value is not None)

@dataclass
class PvdoSet(BaseData):
    """
    油水共存时关于 Sw 的饱和度函数函数，用于黑油模型、油水模型和组分模型
    """
    titles: List[str] = field(default_factory=list, metadata={'description': '表格标题'})
    data: List[Pvdo] = field(default_factory=list, metadata={'description': 'PVDO列表'})

    @classmethod
    def from_block(cls, block_lines):
        block_lines = ListUtils.trim(block_lines)
        if '#' not in block_lines[1]:
            block_lines.index('# P(psi) BO(rb/stb) VISC(cP)', 1)

        titles_text = block_lines[1].replace('#', '').replace('(psi)', '').replace('(rb/stb)', '').replace('(cP)', '').replace('(um)', '')
        titles = titles_text.split()

        data = []
        for line in block_lines[2:]:
            pvdo = Pvdo.from_text(line, titles)
            data.append(pvdo)

        return cls(titles=titles, data=data)

    def to_block(self):
        lines = ['PVDO']
        title_items = ['# P(psi)', 'BO(rb/stb)', 'VISC(cP)']
        lines.append(StringFormat.pad_values(title_items, self.__pad_length, JustifyType.LEFT))

        for pvdo in self.data:
            lines.append('  ' + pvdo.to_text(self.titles, self.__pad_length))

        return lines

    @property
    def __pad_length(self):
        max_length = 0
        for pvdo in self.data:
            max_length = max(max_length, pvdo.max_length)
        return max_length+2

if __name__ == '__main__':
    str_ = '''
PVDO 
# P(psi) BO(rb/stb) VISC(cP) 
 14 1.03 1.2 
 1014.7 1.0106 1.2 
 2014.7 0.9916 1.2 
 3014.7 0.9729 1.200166 
 4014.7 0.9546 1.200222 
 5014.7 0.9367 1.200277 
 6014.7 0.9190 1.200333 
 7014.7 0.9017 1.200388     
    '''
    pvdo_ = PvdoSet.from_block(str_.splitlines())
    print('\n'.join(pvdo_.to_block()))