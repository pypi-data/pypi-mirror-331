from typing import List, Dict, Union, Any
from abc import ABC, abstractmethod
from pathlib import Path

import csv
import json
import pandas as pd
from xml.etree import ElementTree
from tempfile import NamedTemporaryFile

from .rule import Rule
from .mapper import FieldMap, FieldMapper


class BaseParser(ABC):
    """解析器抽象基类"""
    @abstractmethod
    def parse(self, file_path: Path) -> List[Rule]:
        """解析文件"""
        pass


class CSVParser(BaseParser):
    """CSV解析器"""
    def parse(self, file_path: Path) -> List[Rule]:
        rules = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rule = Rule(
                    field1=row.get('field1'),
                    condition1=row.get('condition1'),
                    keyword1=row.get('keyword1'),
                    logic=row.get('logic'),
                    field2=row.get('field2'),
                    condition2=row.get('condition2'),
                    keyword2=row.get('keyword2'),
                    label=row.get('label')
                )
                if rule.is_valid():
                    rules.append(rule)
        return rules


class TxtParser(BaseParser):
    """TXT解析器"""
    def parse(self, file_path: Path) -> List[Rule]:
        rules = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('\t')
                if len(parts) != 8:
                    continue
                rule = Rule(
                    field1=parts[0],
                    condition1=parts[1],
                    keyword1=parts[2],
                    logic=parts[3],
                    field2=parts[4],
                    condition2=parts[5],
                    keyword2=parts[6],
                    label=parts[7]
                )
                if rule.is_valid():
                    rules.append(rule)
        return rules


class ExcelParser(BaseParser):
    """Excel解析器"""
    def parse(self, file_path: Path) -> List[Rule]:
        rules = []
        df = pd.read_excel(file_path, dtype=str).fillna('')
        for _, row in df.iterrows():
            rule = Rule(
                field1=row['field1'],
                condition1=row['condition1'],
                keyword1=row['keyword1'],
                logic=row['logic'],
                field2=row['field2'],
                condition2=row['condition2'],
                keyword2=row['keyword2'],
                label=row['label']
            )
            if rule.is_valid():
                rules.append(rule)
        return rules


class JSONParser(BaseParser):
    """JSON解析器"""
    def parse(self, file_path: Path) -> List[Rule]:
        rules = []
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                rule = Rule(
                    field1=item.get('field1'),
                    condition1=item.get('condition1'),
                    keyword1=item.get('keyword1'),
                    logic=item.get('logic'),
                    field2=item.get('field2'),
                    condition2=item.get('condition2'),
                    keyword2=item.get('keyword2'),
                    label=item.get('label')
                )
                if rule.is_valid():
                    rules.append(rule)
        return rules


class XMLParser(BaseParser):
    """XML解析器"""
    def parse(self, file_path: Path) -> List[Rule]:
        rules = []
        tree = ElementTree.parse(file_path)
        root = tree.getroot()

        for item in root.findall('rule'):
            rule = Rule(
                field1=item.find('field1').text,
                condition1=item.find('condition1').text,
                keyword1=item.find('keyword1').text,
                logic=item.find('logic').text,
                field2=item.find('field2').text,
                condition2=item.find('condition2').text,
                keyword2=item.find('keyword2').text,
                label=item.find('label').text
            )
            if rule.is_valid():
                rules.append(rule)
        return rules


class ListDictParser(BaseParser):
    """列表字典解析器"""
    def parse(self, data: List[Dict], field_map: FieldMapper = None) -> List[Rule]:
        # 字段映射 -> DataFrame
        if field_map is not None:
            data = field_map.map_df(pd.DataFrame(data))
        # 初始化规则列表
        rules = []
        for _, row in data.iterrows():
            rule = Rule(
                field1=row['field1'],
                condition1=row['condition1'],
                keyword1=row['keyword1'],
                logic=row['logic'],
                field2=row['field2'],
                condition2=row['condition2'],
                keyword2=row['keyword2'],
                label=row['label']
            )
            if rule.is_valid():
                rules.append(rule)
        return rules


class DataFrameParser(BaseParser):
    """DataFrame解析器"""
    def parse(self, data: pd.DataFrame, field_map: FieldMapper = None) -> List[Rule]:
        # 字段映射
        if field_map is not None:
            data = field_map.map_df(data)
        # 初始化规则列表
        rules = []
        for _, row in data.iterrows():
            rule = Rule(
                field1=row['field1'],
                condition1=row['condition1'],
                keyword1=row['keyword1'],
                logic=row['logic'],
                field2=row['field2'],
                condition2=row['condition2'],
                keyword2=row['keyword2'],
                label=row['label']
            )
            if rule.is_valid():
                rules.append(rule)
        return rules


class RuleParser:
    """规则解析器"""
    def __init__(self, data: Union[List[Dict[str, str]], pd.DataFrame, str], field_map: Union[Dict[str, str], FieldMap] = None):
        """初始化"""
        self._data = data
        self._parser = self._select_parser()
        self._field_map = FieldMapper(field_map) if field_map else FieldMapper()

    def _select_parser(self) -> BaseParser:
        """创建解析器"""
        if isinstance(self._data, List):
            return ListDictParser()
        elif isinstance(self._data, pd.DataFrame):
            return DataFrameParser()
        elif isinstance(self._data, str):
            if self._data.endswith('.csv'):
                return CSVParser()
            elif self._data.endswith('.txt'):
                return TxtParser()
            elif self._data.endswith('.xlsx'):
                return ExcelParser()
            elif self._data.endswith('.json'):
                return JSONParser()
            elif self._data.endswith('.xml'):
                return XMLParser()
            else:
                raise ValueError(f"不支持的文件格式: {self._data}")
        else:
            raise ValueError(f"不支持的数据类型: {type(self._data)}")

    def parse(self) -> Union[List[Any], List[Rule], None]:
        """规则文件解析"""
        try:
            if isinstance(self._parser, (ListDictParser, DataFrameParser)):
                return self._parser.parse(self._data, self._field_map)
            elif isinstance(self._parser, CSVParser):
                origin_df = pd.read_csv(self._data)
                mapped_df = self._field_map.map_df(origin_df)
                # 新建临时文件
                with NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as temp_file:
                    # print("temp_file:", temp_file.name)
                    mapped_df.to_csv(temp_file, index=False)
                    temp_file_path = temp_file.name
                # 解析临时文件
                try:
                    return self._parser.parse(Path(temp_file_path))
                except Exception as e:
                    print(f"Parse temp file {temp_file_path} failed: {e}")
                    return []
                finally:
                    # 安全删除临时文件
                    Path(temp_file_path).unlink(missing_ok=True)
            else:
                # 其他文件类型直接解析
                return self._parser.parse(Path(self._data))

        except Exception as e:
            print(f"Parse rules {self._data} failed: {e}")
            return []
