from dataclasses import dataclass, field

from mag_tools.bean.common.base_data import BaseData
from mag_tools.bean.data_format import DataFormat
from mag_tools.bean.text_format import TextFormat
from mag_tools.model.base_enum import BaseEnum

from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.list_utils import ListUtils
from mag_tools.utils.data.string_format import StringFormat
from mag_tools.utils.data.string_utils import StringUtils
from typing import List, Optional


@dataclass
class Swof(BaseData):
    """
    Sw 的饱和度函数函数
    """
    sw: Optional[float] = field(default=None, metadata={'description': '水饱和度'})
    krw: Optional[float] = field(default=None, metadata={'description': '水的相对渗透率'})
    krow: Optional[float] = field(default=None, metadata={'description': '油在水中的相对渗透率'})
    pcow: Optional[float] = field(default=None, metadata={'description': '毛管力 Pcow(=Po-Pw)'})

    def __post_init__(self):
        self._data_formats = {
            'sw': DataFormat(decimal_places=6, decimal_places_of_zero=4),
            'krw': DataFormat(decimal_places=9, decimal_places_of_zero=4),
            'krow': DataFormat(decimal_places=6, decimal_places_of_zero=4),
            'pcow': DataFormat(decimal_places=9, decimal_places_of_zero=4)
        }

    @classmethod
    def from_text(cls, text: str, titles: List[str]):
        items = text.split()
        values = {title.lower().replace('(=po-pw)', '').strip(): StringUtils.to_value(items[index], float) for index, title in enumerate(titles)}
        return cls(**values)

    def to_text(self, titles: List[str], pad_length: int) -> str:
        items = [StringFormat.format_number(getattr(self, title.lower().replace('(=po-pw)', '')), self._data_formats[title.lower().replace('(=po-pw)', '')]) for title in titles]
        return StringFormat.pad_values(items, pad_length, JustifyType.LEFT)

    @property
    def max_length(self) -> int:
        return max(len(str(value)) for value in [self.sw, self.krw, self.krow, self.pcow] if value is not None)

@dataclass
class SwofSet(BaseData):
    """
    油水共存时关于 Sw 的饱和度函数函数，用于黑油模型、油水模型和组分模型
    """
    titles: List[str] = field(default_factory=list, metadata={'description': '表格标题'})
    data: List[Swof] = field(default_factory=list, metadata={'description': 'SWOF列表'})

    @classmethod
    def from_block(cls, block_lines):
        # 处理标题行，为空则设置缺省值
        block_lines = ListUtils.trim(block_lines)
        if 'Sw' not in block_lines[1]:
            titles_text = 'Sw Krw Krow Pcow(=Po-Pw)'
        else:
            titles_text = block_lines[1].replace('#', '')
            if '(' not in titles_text:
                titles_text = titles_text.replace('Pc', 'Pcow(=Po-Pw)')
        titles = titles_text.split()

        data = []
        for line in block_lines[2:]:
            if line.strip() != '/':
                swof = Swof.from_text(line, titles)
                data.append(swof)

        return cls(titles=titles, data=data)

    def to_block(self):
        lines = ['SWOF']
        title_items = ['# Sw', 'Krw', 'Krow', 'Pcow(=Po-Pw)']
        lines.append(StringFormat.pad_values(title_items, self.__pad_length, JustifyType.LEFT))

        for swof in self.data:
            lines.append(swof.to_text(self.titles, self.__pad_length))
        lines.append('/')

        return lines

    @property
    def __pad_length(self):
        max_length = 0
        for d in self.data:
            max_length = max(max_length, d.max_length)
        return max_length+2

if __name__ == '__main__':
    _lines = ['SWOF',
'#           Sw         Krw       Krow       Pcow(=Po-Pw)',
       '0.15109           0           1         400',
       '0.15123           0     0.99997      359.19',
       '0.15174           0     0.99993      257.92',
       '0.15246           0     0.99991      186.31',
       '0.15647           0     0.99951       79.06',
       '0.16585           0     0.99629       40.01',
       '0.17835           0     0.99159       27.93',
       '0.20335      1e-005     0.97883        20.4']
    _swof_set = SwofSet.from_block(_lines)
    print('\n'.join(_swof_set.to_block()))
