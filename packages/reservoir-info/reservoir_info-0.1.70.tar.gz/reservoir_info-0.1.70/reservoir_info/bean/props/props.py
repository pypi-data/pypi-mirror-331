from dataclasses import dataclass, field
from types import ModuleType

from mag_tools.bean.common.base_data import BaseData
from mag_tools.utils.data.list_utils import ListUtils

from reservoir_info.bean.props.pvdo import PvdoSet
from reservoir_info.bean.props.density import Density
from reservoir_info.bean.props.pvtw import Pvtw
from reservoir_info.bean.props.rel_permeate_model import RelPermeateModel
from reservoir_info.bean.props.rock import Rock
from reservoir_info.bean.props.sgof import SgofSet
from reservoir_info.bean.props.swof import SwofSet
from typing import List, Optional


@dataclass
class Props(BaseData):
    swof: Optional[SwofSet] = field(default=None, metadata={'description': 'Sw 的饱和度函数函数'})
    sgof: Optional[SgofSet] = field(default=None, metadata={'description': 'Sg 的饱和度函数函数'})
    rel_permeate_model: Optional[RelPermeateModel] = field(default=None, metadata={'description': 'Rel Permeate Model'})
    pvdo: Optional[PvdoSet] = field(default=None, metadata={'description': '用表格定义dead oil的PVT属性'})
    pvtw: Optional[Pvtw] = field(default=None, metadata={'description': '水的PVT属性'})
    density: Optional[Density] = field(default=None, metadata={'description': '油、水、气的密度'})
    rock: Optional[Rock] = field(default=None, metadata={'description': '岩石的压缩属性'})
    module_type: Optional[ModuleType] = field(default=None, metadata={'description': '模型类型'})

    @classmethod
    def from_block(cls, block_lines : List[str], module_type : ModuleType = None):
        if block_lines is None or len(block_lines) == 0:
            return None

        swof_lines = ListUtils.pick_block(block_lines, 'SWOF', '')
        swof = SwofSet.from_block(swof_lines)

        sgof_lines = ListUtils.pick_block(block_lines, 'SGOF', '')
        sgof = SgofSet.from_block(sgof_lines)

        pvdo_lines = ListUtils.pick_block(block_lines, 'PVDO', '')
        pvdo = PvdoSet.from_block(pvdo_lines)

        pvtw_lines = ListUtils.pick_block(block_lines, 'PVTW', '')
        pvtw = Pvtw.from_block(pvtw_lines)


        keywords = {
            'SWOF':(None,None),
            'SGOF':(None,None),
            'STONEI':(None,None),
            'STONEII':(None,None),
            'SEGR':(None,None),
            'PVTW':(None,None),
            'DENSITY':(None,None),
            'ROCK':(None,None)
        }
        segments = ListUtils.split_by_boundary(block_lines, keywords)

        permeate_type = 'STONEI' if segments['STONEI'] else 'STONEII' if segments['STONEII'] else 'SEGR'
        permeate_model = RelPermeateModel.from_block(segments[permeate_type], module_type)

        values = {'swof': SwofSet.from_block(segments['SWOF']),
                  'sgof': SgofSet.from_block(segments['SGOF']),
                  'rel_permeate_model': permeate_model,
                  'pvtw': Pvtw.from_block(segments['PVTW']),
                  'density': Density.from_block(segments['DENSITY']),
                  'rock': Rock.from_block(segments['ROCK']),
                  "module_type": module_type}

        return cls(**values)

    def to_block(self):
        lines = []
        if self.swof:
            lines.extend(self.swof.to_block())
        if self.sgof:
            lines.extend(self.sgof.to_block())
        if self.rel_permeate_model:
            lines.extend(self.rel_permeate_model.to_block())
        if self.pvtw:
            lines.extend(self.pvtw.to_block())
        if self.density:
            lines.extend(self.density.to_block())
        if self.rock:
            lines.extend(self.rock.to_block())

        return lines

    def __str__(self):
        return '\n'.join(self.to_block())

if __name__ == '__main__':
    _text = """
    PROPS
##################################################
SWOF
#           Sw         Krw       Krow       Pcow(=Po-Pw)
       0.15109           0           1         400
       0.15123           0     0.99997      359.19
       0.15174           0     0.99993      257.92
       0.65693      0.2619     0.00594       -2.26
        0.7128     0.31865     0.00159       -2.38
       0.81111     0.43092      2e-005        -2.6
       0.88149        0.49           0       -2.75
 /

SGOF
#           Sg         Krg       Krog       Pcgo(=Pg-Po)
             0           0           1           0
          0.04           0         0.6         0.2
           0.5        0.42           0         2.5
           0.6         0.5           0           3
           0.7      0.8125           0         3.5
       0.84891           1           0         3.9
 /

STONEII
PVDG
#       Pres        Bg       Vis 
         400    5.4777     0.013
         800    2.7392    0.0135
PVTO
#        Rssat      Pres        Bo      Vis
         0.165       400     1.012      1.17 /
         0.985      2400     1.075      1.03 /
          1.13      2800     1.087         1 /
          1.27      3200    1.0985      0.98 /
          1.39      3600      1.11      0.95 /
           1.5      4000      1.12      0.94
                    5000    1.1189      0.94 /
/

PVTW
#       Pref     refBw        Cw   refVisw     Cvisw
        3600    1.0034    1e-006      0.96         0
  
DENSITY
#   Oil     Water       Gas
   44.98     63.01    0.0702

ROCK  
3600.0  1.0E-6

#PROPS END########################################
"""
    _lines = _text.split('\n')
    _props = Props.from_block(_lines)
    print(_props)