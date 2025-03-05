from dataclasses import dataclass
from typing import Optional


@dataclass
class Rule:
    """
    规则数据模型
    field1: 筛选字段1
    condition1: 筛选条件1
    keyword1: 关键词1
    logic: 关联关系(且/或)
    field2: 筛选字段2
    condition2: 筛选条件2
    keyword2: 关键词2
    label: 标签
    """
    field1: Optional[str]
    condition1: Optional[str]
    keyword1: Optional[str]
    logic: Optional[str]
    field2: Optional[str]
    condition2: Optional[str]
    keyword2: Optional[str]
    label: str

    def is_valid(self) -> bool:
        """验证必填字段"""
        return bool(
            # 必填筛选条件1或筛选条件2 必填标签
            bool(self.field1 and self.condition1) or
            bool(self.field2 and self.condition2)
        ) and bool(self.label)
