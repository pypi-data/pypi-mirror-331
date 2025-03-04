from mag_tools.model.base_enum import BaseEnum


class NmatoptsType(BaseEnum):
    UNIFORM = ("UNIFORM", "基质体积均匀分配")
    GEOMETRIC = ("GEOMETRIC", "基质到裂缝的距离由外到内等比增长")
    DESIGNATED = ("DESIGNATED", "由用户指定")