#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具創造器：讓 AI Agent 能夠動態創造符合自身需求的工具
"""
import re
import ast
import importlib.util
from pathlib import Path
from typing import Optional

import sys
from pathlib import Path

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from metagpt.actions import Action
from metagpt.config2 import config
from metagpt.logs import logger
from metagpt.tools.tool_registry import TOOL_REGISTRY, register_tools_from_file


class CreateTool(Action):
    """創造新工具的 Action"""
    
    PROMPT_TEMPLATE: str = """
    您是一個工具設計專家。根據以下需求，設計並實作一個 Python 工具函式。

    ### 需求描述
    {requirement}

    ### 要求
    1. 函式必須有清晰的文檔字串（docstring），包含：
       - 函式功能描述
       - Args: 參數說明（類型和描述）
       - Returns: 返回值說明（類型和描述）
    2. 函式名稱應該清晰描述其功能
    3. 使用適當的類型提示（type hints）
    4. 確保程式碼可以正常執行
    5. 如果需要的話，可以導入必要的標準庫或第三方庫

    ### 範例格式
    ```python
    def example_tool(param1: str, param2: int) -> dict:
        \"\"\"
        工具功能描述
        
        Args:
            param1 (str): 第一個參數的說明
            param2 (int): 第二個參數的說明
            
        Returns:
            dict: 返回值的說明
        \"\"\"
        # 實作程式碼
        return {{"result": "some value"}}
    ```

    ### 您的任務
    請根據需求設計並實作工具函式。只回傳 Python 程式碼，使用 ```python 和 ``` 包圍程式碼。
    不要包含其他文字說明。
    """

    async def run(self, requirement: str) -> str:
        """根據需求創造工具程式碼"""
        prompt = self.PROMPT_TEMPLATE.format(requirement=requirement)
        rsp = await self._aask(prompt)
        code_text = self.parse_code(rsp)
        return code_text

    @staticmethod
    def parse_code(rsp: str) -> str:
        """從回應中解析 Python 程式碼"""
        pattern = r"```python(.*?)```"
        match = re.search(pattern, rsp, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 如果沒有找到程式碼塊，嘗試尋找函式定義
        pattern = r"def\s+\w+.*?(?=\n\n|\n```|$)"
        match = re.search(pattern, rsp, re.DOTALL)
        if match:
            return match.group(0).strip()
        
        return rsp.strip()


class RegisterTool(Action):
    """註冊工具到工具註冊中心的 Action"""
    
    async def run(self, tool_code: str, tool_name: Optional[str] = None) -> dict:
        """
        將工具程式碼註冊到工具註冊中心
        
        Args:
            tool_code: 工具的 Python 程式碼
            tool_name: 可選的工具名稱，如果不提供則從程式碼中解析
            
        Returns:
            dict: 註冊結果
        """
        try:
            # 解析工具名稱
            if not tool_name:
                tool_name = self._extract_function_name(tool_code)
            
            if not tool_name:
                return {"success": False, "error": "無法從程式碼中解析函式名稱"}
            
            # 將程式碼寫入臨時檔案
            tools_dir = config.workspace.path / "tools"
            tools_dir.mkdir(parents=True, exist_ok=True)
            
            tool_file = tools_dir / f"{tool_name}.py"
            tool_file.write_text(tool_code, encoding="utf-8")
            
            # 註冊工具
            registered_tools = register_tools_from_file(str(tool_file))
            
            if registered_tools:
                logger.info(f"工具 {tool_name} 已成功註冊")
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "tool_path": str(tool_file),
                    "registered_tools": list(registered_tools.keys())
                }
            else:
                return {"success": False, "error": "工具註冊失敗"}
                
        except Exception as e:
            logger.error(f"註冊工具時發生錯誤: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _extract_function_name(code: str) -> Optional[str]:
        """從程式碼中提取函式名稱"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    return node.name
        except Exception as e:
            logger.warning(f"解析函式名稱時發生錯誤: {e}")
        return None


class ToolCreator:
    """工具創造器：整合工具創造和註冊流程"""
    
    def __init__(self):
        self.create_tool_action = CreateTool()
        self.register_tool_action = RegisterTool()
    
    async def create_and_register_tool(self, requirement: str) -> dict:
        """
        根據需求創造並註冊工具
        
        Args:
            requirement: 工具需求描述
            
        Returns:
            dict: 包含創造和註冊結果的字典
        """
        # 步驟 1: 創造工具程式碼
        logger.info(f"開始創造工具，需求: {requirement}")
        tool_code = await self.create_tool_action.run(requirement)
        
        if not tool_code:
            return {"success": False, "error": "無法產生工具程式碼"}
        
        # 步驟 2: 註冊工具
        logger.info("開始註冊工具")
        register_result = await self.register_tool_action.run(tool_code)
        
        if register_result.get("success"):
            register_result["tool_code"] = tool_code
            return register_result
        else:
            return {
                "success": False,
                "error": register_result.get("error", "未知錯誤"),
                "tool_code": tool_code
            }

