from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Union
from pandas import DataFrame
from pathlib import Path


@dataclass
class FieldMap:
    field1: str
    condition1: str
    keyword1: str
    logic: str
    field2: str
    condition2: str
    keyword2: str
    label: str


DEFAULT_FIELD_MAP = FieldMap(
    field1='筛选字段1',
    condition1='筛选条件1',
    keyword1='关键字1',
    logic='关联条件',
    field2='（可选）筛选字段2',
    condition2='（可选）筛选条件2',
    keyword2='（可选）关键字2',
    label='账单类别'
)


class BaseMapper(ABC):
    """字段映射器抽象基类"""

    def __init__(self, field_map: Union[Dict[str, str], FieldMap] = DEFAULT_FIELD_MAP):
        """
        :param field_map: 字段映射字典
        """
        if isinstance(field_map, Dict):
            self.field_map = FieldMap(**field_map)
        elif isinstance(field_map, FieldMap):
            self.field_map = field_map
        else:
            raise TypeError('Input type must be Dict or FieldMap')

    @abstractmethod
    def map_field(self, df: DataFrame, file: str = None) -> Union[DataFrame, Path]:
        pass


class CSVMapper(BaseMapper):
    """CSV映射器"""
    def map_field(self, df: DataFrame, file: str = None) -> Union[DataFrame, Path]:
        pass


class TXTMapper(BaseMapper):
    """TXT映射器"""
    def map_field(self, df: DataFrame, file: str = None) -> Union[DataFrame, Path]:
        pass


class ExcelMapper(BaseMapper):
    """Excel映射器"""
    def map_field(self, df: DataFrame, file: str = None) -> Union[DataFrame, Path]:
        pass


class JSONMapper(BaseMapper):
    """JSON映射器"""
    def map_field(self, df: DataFrame, file: str = None) -> Union[DataFrame, Path]:
        pass


class XMLMapper(BaseMapper):
    """XML映射器"""
    def map_field(self, df: DataFrame, file: str = None) -> Union[DataFrame, Path]:
        pass


class FieldMapper:
    """字段映射器"""
    def __init__(self, field_map: Union[Dict[str, str], FieldMap] = DEFAULT_FIELD_MAP):
        """
        :param field_map: 字段映射字典
        """
        if isinstance(field_map, Dict):
            self.field_map = FieldMap(**field_map)
        elif isinstance(field_map, FieldMap):
            self.field_map = field_map
        else:
            raise TypeError('Input type must be Dict or FieldMap')

    def _reverse_map(self):
        return {v: k for k, v in self.field_map.__dict__.items()}

    def map_df(self, df: DataFrame, file: str = None) -> DataFrame:
        mapped_df = DataFrame()
        for item in self.field_map.__dict__.items():
            if item[1] not in df.columns:
                raise ValueError(f'Field [{item[1]}] not in DataFrame')
            mapped_df[item[0]] = df[item[1]]

        if file is not None:
            mapped_df.to_csv(file, index=False)

        return mapped_df
