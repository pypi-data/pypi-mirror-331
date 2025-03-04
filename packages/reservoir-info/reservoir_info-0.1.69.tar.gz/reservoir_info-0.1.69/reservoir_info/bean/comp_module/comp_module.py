import os
from dataclasses import dataclass, field
from typing import Any, Optional

from mag_tools.bean.common.base_data import BaseData
from mag_tools.utils.common.string_utils import StringUtils
from mag_tools.utils.data.list_utils import ListUtils

from reservoir_info.bean.comp_other.schedule import Schedule
from reservoir_info.bean.solution.solution import Solution
from reservoir_info.bean.comp_other.tune import Tune
from reservoir_info.bean.props.props import Props
from reservoir_info.bean.grid.grid import Grid
from reservoir_info.bean.general.general_info import General
from reservoir_info.bean.well.well_group import WellGroup


@dataclass
class CompModule(BaseData):
    name: Optional[str] = field(default=None, metadata={"description": "模型名称"})
    general: Optional[General] = field(default=None, metadata={"description": "通用信息"})
    grid: Optional[Grid] = field(default=None, metadata={"description": "油藏地质模型"})
    well: Optional[WellGroup] = field(default=None, metadata={"description": "井定义信息"})
    props: Optional[Props] = field(default=None, metadata={"description": "岩石、流体物性"})
    solution: Optional[WellGroup] = field(default=None, metadata={"description": "初始化信息 "})
    computing_ctl: Optional[Tune] = field(default=None, metadata={"description": "计算控制信息"})
    schedule: Optional[Schedule] = field(default=None, metadata={"description": "井与生产动态信息"})
    output_ctl: Optional[OutputCtl] = field(default=None, metadata={"description": "输出控制信息"})


    @classmethod
    def load_from_file(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]
            module = cls.from_block(lines)
            module.name = os.path.basename(file_path).replace('.dat', '')

        return module

    def save_to_file(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in self.to_block():
                file.write(line)
                file.write("\n")

    @classmethod
    def from_block(cls, block_lines):
        module = cls()

        block_lines = [line for line in block_lines if not line.startswith('###')]

        control_lines = ListUtils.pick_head(block_lines, 'GRID')
        module.control = General.from_block(control_lines)

        # 油藏地质模型
        grid_lines = ListUtils.pick_block(block_lines, 'GRID', 'WELL')
        grid_lines.pop(-1)
        module.grid = Grid.from_block(grid_lines)

        # 井定义信息
        well_lines = ListUtils.pick_block(block_lines, 'WELL', 'PROPS')
        well_lines.pop(-1)
        module.well = WellGroup.from_block(well_lines)

        # 岩石、流体物性
        props_lines = ListUtils.pick_block(block_lines, 'PROPS', 'SOLUTION')
        module.props = Props.from_block(props_lines)

        # 初始化信息
        solution_lines = ListUtils.pick_block(block_lines, 'SOLUTION', 'TUNE')
        module.solution = Solution.from_block(solution_lines)

        # 计算控制信息
        computing_lines = ListUtils.pick_block(block_lines, 'TUNE', '')
        module.tune = Tune.from_block(computing_lines)

        # 井与生产动态信息
        schedule_lines = ListUtils.pick_block(block_lines, 'SCHEDULE', '')
        module.schedule = Schedule.from_block(schedule_lines)

        # 输出控制信息
        output_lines = ListUtils.pick_block(block_lines, 'RPTSCHED', '')
        module.output_ctl = OutputCtl.from_block(output_lines)

        return module

    def to_block(self):
        lines = self.general.to_block()
        lines.extend(self.grid.to_block())
        lines.extend(self.well.to_block())
        lines.extend(self.props.to_block())
        lines.extend(self.solution.to_block())
        lines.extend(self.computing_ctl.to_block())
        lines.extend(self.schedule.to_block())
        lines.extend(self.output_ctl.to_block())
        return lines

    @property
    def key_parameter(self) -> dict[str, Any]:
        return {}

if __name__ == '__main__':
    # 示例用法
    data = """MODELTYPE BlackOil
FIELD

GRID
##################################################
DIMENS
 5 2 1

BOX FIPNUM 1 5 1 2 1 1 = 2

PERMX
49.29276      162.25308      438.45926      492.32336      791.32867
704.17102      752.34912      622.96875      542.24493      471.45953

COPY PERMX  PERMY  1 5 1 2 1 1 
COPY PERMX  PERMZ  1 5 1 2 1 1

BOX  PERMZ  1 5 1 2 1 1  '*' 0.01

PORO
 5*0.087
 5*0.097

TOPS 10*9000.00

BOX TOPS   1  1  1 2  1  1  '='  9000.00
BOX TOPS   2  2  1 2  1  1  '='  9052.90

DXV
 5*300.0

DYV
 2*300.0

DZV
 20

#GRID END#########################################

WELL
##################################################

TEMPLATE
'MARKER' 'I' 'J' 'K1' 'K2' 'OUTLET' 'WI' 'OS' 'SATMAP' 'HX' 'HY' 'HZ' 'REQ' 'SKIN' 'LENGTH' 'RW' 'DEV' 'ROUGH' 'DCJ' 'DCN' 'XNJ' 'YNJ' /
WELSPECS
NAME 'INJE1'
''  24  25  11  11  NA  NA  SHUT  NA  0  0  0  NA  NA  NA  0.5  NA  NA  NA  1268.16  NA  NA  
''  24  25  11  15  NA  NA  OPEN  NA  0  0  DZ  NA  NA  NA  0.5  NA  NA  NA  0  NA  NA  

NAME 'PROD2'
''  5  1  2  2  NA  NA  OPEN  NA  0  0  DZ  NA  0  NA  0.5  0  0  NA  NA  NA  NA  
''  5  1  3  3  NA  NA  OPEN  NA  0  0  DZ  NA  0  NA  0.5  0  0  NA  NA  NA  NA  
''  5  1  4  4  NA  NA  OPEN  NA  0  0  DZ  NA  0  NA  0.5  0  0  NA  NA  NA  NA 
#WELL END#########################################

PROPS
##################################################
SWOF
#           Sw         Krw       Krow       Pcow(=Po-Pw)
       0.15109           0           1         400
       0.15123           0     0.99997      359.19
       0.15174           0     0.99993      257.92

#PROPS END########################################

SOLUTION
##################################################

EQUILPAR
# Ref_dep    Ref_p    GWC/OWC  GWC_pc/OWC_pc   dh
  9035       3600      9950        0.0         2
# GOC       GOC_pc
  8800        0.0    
PBVD
   5000        3600
   9000        3600

#SOLUTION END######################################

TUNE
TSTART  1990-01-01 
MINDT  0.1  MAXDT  31  DTINC  2.0  DTCUT  0.5  CHECKDX  
MAXDP  200  MAXDS  0  MAXDC  0  MBEPC  1E-4  MBEAVG  1E-6   
SOLVER  1034


RESTART

RPTSCHED
BINOUT SEPARATE NETONLY GEOM RPTONLY RSTBIN SOLVD 
POIL SOIL SGAS SWAT RS NOSTU  TECPLOT 
 /

RPTSUM
POIL 1 2 1 /
POIL AVG Reg 2 /
"""

    # mod = CompModule.load_from_file(r"D:\HiSimPack\examples\Comp\spe9\SPE9.dat")
    _lines = data.split("\n")
    mod = CompModule.from_block(_lines)
    print(mod)
