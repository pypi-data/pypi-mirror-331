from typing import Union, List, Dict

from simplelabel.core import Rule
from simplelabel.core import FieldMap
from simplelabel.core import RuleParser


class FieldsIdentifier:
    """数据表字段标识器"""
    def __init__(self, f_map: Dict[str, str], fields: List[str] = None, reverse: bool = False):
        """初始化数据字段标识实例"""
        self._fields = fields
        self._kwargs = self._to_reverse(f_map) if reverse else f_map

    def init(self):
        """转换为字段标识字典"""
        return self._to_dict()

    @staticmethod
    def _to_reverse(kwargs: Dict[str, str]) -> Dict[str, str]:
        return {value: key for key, value in kwargs.items()}

    def _to_dict(self) -> Union[Dict[str, str], None]:
        self._field_identifier = {}
        for key, value in self._kwargs.items():
            # 若提供字段列表，则只保留字段列表中的字段
            if self._fields and key not in self._fields:
                continue
            if isinstance(value, str):
                self._field_identifier[key] = value
            else:
                raise ValueError(f"Invalid value type: {value}")

        if self._field_identifier:
            return self._field_identifier
        return None


class SQLGenerator:
    """SQL语句生成器"""

    def __init__(self, rules: Union[str, List[Rule]], field_map: Union[Dict[str, str], FieldMap] = None):
        """初始化SQL语句生成器"""
        self._rules = self._parse_rules(rules, field_map)
        self._sql = "SELECT *, \nCASE \n{} \nELSE '未分类' END AS '账单类别' \nFROM TABLE_NAME"
        self._sql_case = "\tWHEN {} THEN '{}' "
        self._sql_condition_map = {
            '为空': lambda field: f"{field} IS NULL",
            '不为空': lambda field: f"{field} IS NOT NULL",
            '等于': lambda field, keyword: f"{field} = '{keyword}'",
            '不等于': lambda field, keyword: f"{field} != '{keyword}'",
            '大于': lambda field, keyword: f"{field} > {keyword}",
            '大于等于': lambda field, keyword: f"{field} >= {keyword}",
            '小于': lambda field, keyword: f"{field} < {keyword}",
            '小于等于': lambda field, keyword: f"{field} <= {keyword}",
            '包含': lambda field, keyword: f"{field} LIKE '%{keyword}%'",
            '不包含': lambda field, keyword: f"{field} NOT LIKE '%{keyword}%'",
            '开头是': lambda field, keyword: f"{field} LIKE '{keyword}%'",
            '开头不是': lambda field, keyword: f"{field} NOT LIKE '{keyword}%'",
            '结尾是': lambda field, keyword: f"{field} LIKE '%{keyword}'",
            '结尾不是': lambda field, keyword: f"{field} NOT LIKE '%{keyword}'",
            '正则匹配': lambda field, keyword: f"{field} REGEXP_LIKE('{keyword}')",
            '正则不匹配': lambda field, keyword: f"{field} NOT REGEXP_LIKE('{keyword}')"
        }
        self._sql_logic_map = {
            '且': lambda conditions: f"{' AND '.join(conditions)}",
            '或': lambda conditions: f"{' OR '.join(conditions)}",
            '': lambda conditions: f"{''.join(conditions)}"
        }

    @staticmethod
    def init(rules: Union[str, List[Rule]], field_map: Union[Dict[str, str], FieldMap] = None):
        """初始化SQL语句生成器"""
        return SQLGenerator(rules, field_map)

    @staticmethod
    def _parse_rules(rules: Union[str, List[Rule]], field_map: Union[Dict[str, str], FieldMap] = None) -> List[Rule]:
        if isinstance(rules, str):
            # 调用规则解析器进行解析
            return RuleParser(rules, field_map).parse()
        elif isinstance(rules, List):
            # 数据类型检查：List[Rule]
            for rule in rules:
                if not isinstance(rule, Rule):
                    raise ValueError('Rules must be a list of Rule objects.')
            return rules
        else:
            raise ValueError('Rules must be a string or a list of Rule objects.')

    def generate(self, output: str = None, field_identifier: Dict[str, str] = None) -> str:
        """
        核心SQL生成函数
        :param: field_identifier: 字段标识器
        :param: output: 输出文件路径
        :return: SQL语句
        """
        case_list = []
        for rule in self._rules:
            if field_identifier:
                # 字段标识器不为空，则替换字段名
                rule.field1 = field_identifier.get(rule.field1, rule.field1)
                rule.field2 = field_identifier.get(rule.field2, rule.field2)
            case_list.append(self._sql_case.format(self._generate_rule(rule), rule.label))

        if output is not None:
            # 输出到文件
            with open(output, 'w') as f:
                f.write(self._sql.format('\n'.join(case_list)))

        return self._sql.format('\n'.join(case_list))

    def _generate_rule(self, rule: Rule) -> str:
        """
        生成单个规则的SQL语句
        :param: rule: 规则对象
        :return: SQL语句
        """
        sql_conditions = []
        for field, condition, keyword in [
            (rule.field1, rule.condition1, rule.keyword1),
            (rule.field2, rule.condition2, rule.keyword2)
        ]:
            if condition in self._sql_condition_map:
                # 根据条件生成SQL条件
                if field and condition in ['为空', '不为空']:
                    sql_conditions.append(self._sql_condition_map[condition](field))
                elif field and keyword:
                    sql_conditions.append(self._sql_condition_map[condition](field, keyword))
                else:
                    raise ValueError(f"Invalid rule: {field} {condition} {keyword}")
            elif condition == '':
                continue
            else:
                raise ValueError(f"Invalid condition: {condition}")

        # 检查SQL条件合法性
        if 1 <= len(sql_conditions) <= 2:
            return self._sql_logic_map[rule.logic](sql_conditions)
        else:
            raise ValueError(f"Invalid rule: {rule}")
