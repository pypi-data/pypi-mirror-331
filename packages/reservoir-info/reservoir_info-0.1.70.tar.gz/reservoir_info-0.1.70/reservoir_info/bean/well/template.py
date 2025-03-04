from dataclasses import dataclass, field
from typing import List

from mag_tools.bean.base_data import BaseData
from mag_tools.bean.text_format import TextFormat
from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.list_utils import ListUtils


@dataclass
class Template(BaseData):
    """
    MARKER：井段命名
    OUTLET：该组井段的前一个井段，即下游井段
    I/J/K1/K2: 网格编号,K1井射孔所在网格的起始层号,K2井射孔所在网格的终止层号
    SATNUM: well flow 的相渗区域
    WCON: 井与多重网格的连接模式
    OS: 设置初始时刻井射孔的开闭, OPEN--打开，SHUT--关闭。
    WI: 井指数
    TF: 井传导率系数
    HX/HY/HZ: 井射孔在网格 x/y/z 方向的投影长度
    REQ: 等效泄油半径
    KH：地层产能系数
    RW: 井半径
    DIAM：井直径
    LENGTH: 井段长度
    DEV: 井段与垂直方向的夹角
    ROUGH：井壁粗糙元特征长度
    DCJ：射孔深度减去网格中心深度
    DCN：射孔深度减去井段中点深度
    XNJ：井段中点 x 坐标减去网格中心 x 坐标
    YNJ：井段中点 y 坐标减去网格中心 x 坐标
    STAGE：整数，代表压裂段号
    UP：井段上部的测深，
    DOWN：井段底部的测深
    ICD_VER：整数，代表控流装置（ICD）的型号
    ICD_OS：设置初始时刻控流装置启动或关闭
    """
    _column_names: List[str] = field(default_factory=list, metadata={'description': '为 WELSPECS 定义每一列数据的含义'})

    def __post_init__(self):
        self._text_format.number_per_line=20

    @classmethod
    def from_block(cls, block_lines):
        """
        从文本块中生成Template
        """
        if block_lines is None or len(block_lines) < 2:
            return None

        text = "".join(block_lines[1:]).replace("/", "").strip()
        names = [name.replace("'", "") for name in text.split()]
        return cls(_column_names=names)

    def to_block(self):
        names_group = ListUtils.split(self._column_names, self._text_format.number_per_line)

        lines = ['TEMPLATE']
        for names in names_group:
            names = [f"'{name}'" for name in names]
            lines.append(" ".join(names))
        lines[-1] += '/'
        return lines

    def get_name(self, idx):
        return self._column_names[idx] if idx < len(self._column_names) else None

    def size(self):
        return len(self._column_names) if self._column_names else 0

    def __getitem__(self, idx):
        return self._column_names[idx] if idx < len(self._column_names) else None

if __name__ == "__main__":
    texts = ["TEMPLATE",
            "'MARKER' 'I' 'J' 'K1' 'K2' 'OUTLET' 'WI' 'OS' 'SATMAP' 'HX' 'HY' 'HZ' 'REQ' 'SKIN' 'LENGTH' 'RW' 'DEV' 'ROUGH' 'DCJ' 'DCN' 'XNJ' 'YNJ' /"]

    temp = Template.from_block(texts)
    print('\n'.join(temp.to_block()))