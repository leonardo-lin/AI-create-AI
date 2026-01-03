# metagpt/tools/libs/calculate_factorial.py
import math
from metagpt.tools.tool_registry import register_tool

# 使用装饰器注册工具
@register_tool()
def calculate_factorial(n):
    """
    计算非负整数的阶乘
    """
    if n < 0:
        raise ValueError("输入必须是非负整数")
    return math.factorial(n)