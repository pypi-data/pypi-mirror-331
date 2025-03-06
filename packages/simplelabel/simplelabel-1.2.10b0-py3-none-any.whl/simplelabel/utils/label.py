from typing import Union, List, Dict
from pandas import DataFrame, Series
import pandas as pd
import re

from simplelabel.core import Rule
from simplelabel.core import FieldMap
from simplelabel.core import RuleParser


class DataLabelEngine:
    """数据标注引擎"""

    def __init__(self, rules: Union[str, List[Rule], List[Dict[str, str]]], field_map: Union[Dict[str, str], FieldMap] = None):
        """初始化数据标注引擎"""
        self._data = None
        self._labels = None
        self._retype = None
        self._rules = self._parse_rules(rules, field_map)
        self._operation_map = {
            '为空': lambda value, keyword: pd.isna(value) or value == '',
            '不为空': lambda value, keyword: not pd.isna(value) and value != '',
            '等于': lambda value, keyword: value == keyword,
            '不等于': lambda value, keyword: value != keyword,
            '大于': lambda value, keyword: float(value) > float(keyword),
            '大于等于': lambda value, keyword: float(value) >= float(keyword),
            '小于': lambda value, keyword: float(value) < float(keyword),
            '小于等于': lambda value, keyword: float(value) <= float(keyword),
            '包含': lambda value, keyword: keyword in value,
            '不包含': lambda value, keyword: keyword not in value,
            '开头是': lambda value, keyword: value.startswith(keyword),
            '开头不是': lambda value, keyword: not value.startswith(keyword),
            '结尾是': lambda value, keyword: value.endswith(keyword),
            '结尾不是': lambda value, keyword: not value.endswith(keyword),
            '正则匹配': lambda value, keyword: bool(re.match(keyword, value)),
            '正则不匹配': lambda value, keyword: not bool(re.match(keyword, value))
        }

    @staticmethod
    def init(rules: Union[str, List[Rule], List[Dict[str, str]]], field_map: Union[Dict[str, str], FieldMap] = None):
        """初始化数据标注引擎"""
        return DataLabelEngine(rules, field_map)

    @staticmethod
    def _parse_rules(rules: Union[str, List[Rule], List[Dict[str, str]]], field_map: Union[Dict[str, str], FieldMap] = None) -> List[Rule]:
        if isinstance(rules, str):
            # 调用规则解析器进行解析
            return RuleParser(rules, field_map).parse()
        elif isinstance(rules, List):
            # 数据类型检查：List[Dict]
            if all(isinstance(rule, dict) for rule in rules):
                return RuleParser(rules, field_map).parse()
            # 数据类型检查：List[Rule]
            elif all(isinstance(rule, Rule) for rule in rules):
                return rules
            else:
                raise ValueError('Rules must be a list of Rule objects or a list of dictionaries.')
        else:
            raise ValueError('Rules must be a string or a list of Rule objects.')

    def label(self, data: Union[str, Dict[str, str], DataFrame, Series], output: str = None,
              only_label: bool = False) -> Union[DataFrame, Dict[str, str], str]:
        """
        核心标注函数
        :param data: 数据文件路径、字典(单条记录)、DataFrame
        :param output: 输出文件路径，默认为None
        :param only_label: 是否只返回标注结果，默认为False
        :return DataFrame, Dict[str, str], str
        """
        # 检查参数
        if output is not None and only_label:
            raise ValueError('Only one of output and only_label can be specified.')
        # 默认输出类型为DataFrame
        self._retype = 'DataFrame'
        # 数据类型检查
        if isinstance(data, str):
            """数据文件路径"""
            self._data = pd.read_csv(data, dtype=str).fillna('')
            self._retype = 'DataFrame'
        elif isinstance(data, dict):
            """字典(单行记录)数据"""
            self._data = pd.DataFrame([data]).fillna('').astype(str)
            self._retype = 'Dict'
        elif isinstance(data, DataFrame):
            """DataFrame类型数据"""
            self._data = data.fillna('').astype(str)
            self._retype = 'DataFrame'
        elif isinstance(data, Series):
            """Series类型数据"""
            self._data = pd.DataFrame([data]).fillna('').astype(str)
            self._retype = 'DataFrame'
        else:
            raise ValueError(f'Data must be a string, dict, or DataFrame, but fact is {type(data)}.')

        # 数据清洗
        self._data = self._data.fillna('')
        self._data = self._data.applymap(lambda x: str(x).strip())

        # 数据标注
        self._labels = []
        for _, row in self._data.iterrows():
            label = None
            for rule in self._rules:
                if self._verify_rule(row.to_dict(), rule):
                    label = rule.label
                    break
            # 若未匹配到规则，则默认为'未分类'
            self._labels.append(label if label else '未分类')

        self._data['账单类别'] = self._labels

        # 只返回标注结果
        if only_label:
            # 若输出为列表，则返回列表，否则返回字符串
            if len(self._labels) > 1:
                return self._data['账单类别']
            else:
                return ','.join(self._labels)

        # 对于单行的字典类型数据，直接返回字典类型数据
        if self._retype == 'Dict' and len(self._data) == 1:
            single_row = self._data.iloc[0]
            return {str(key): str(value) for key, value in single_row.items()}

        # 输出到文件
        if output is not None:
            self._data.to_csv(output, encoding='utf-8-sig', index=False)

        print(f"Labeled finished in {len(self._labels)} records.")
        return self._data

    def _verify_single_condition(self, data: Dict, field: str, condition: str, keyword: str) -> bool:
        """验证单个条件"""
        if not field or not condition or not keyword:
            """空条件视为成立"""
            return True

        # 获取字段值
        _value = str(data.get(field, '')).strip()
        _keyword = str(keyword).strip()

        # 若字段值由数字组成，则转换为数字类型进行比较
        if (_value.replace('.', '', 1).isdigit() and
                _keyword.replace('.', '', 1).isdigit()):
            _value = float(_value)
            _keyword = float(_keyword)

        # 逻辑验证
        if condition in self._operation_map:
            try:
                return self._operation_map[condition](_value, _keyword)
            except Exception as e:
                raise ValueError(f'Failed at [{field} {condition} {keyword}]: {e}')
        else:
            raise ValueError(f'Invalid condition: {condition} From [{field} {condition} {keyword}].')

    def _verify_rule(self, data: Dict, rule: Rule) -> bool:
        """验证单条规则"""
        if not rule.field1 and not rule.field2:
            """空规则视为不成立"""
            return False
        # 验证条件A
        condition_a = self._verify_single_condition(data, rule.field1, rule.condition1, rule.keyword1)
        # 验证条件B
        condition_b = self._verify_single_condition(data, rule.field2, rule.condition2, rule.keyword2)

        # 关联关系验证
        if rule.logic == '且':
            return condition_a and condition_b
        elif rule.logic == '或':
            return condition_a or condition_b
        elif rule.logic == '' or pd.isna(rule.logic):
            return condition_a and condition_b
        else:
            raise ValueError(f'Invalid logic: {rule.logic}')
