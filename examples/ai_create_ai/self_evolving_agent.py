#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自我進化 Agent：能夠識別需求、創造工具、增強能力的智能體
"""
import asyncio
from typing import List, Dict, Optional

from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.logs import logger

import sys
from pathlib import Path

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.ai_create_ai.tool_creator import ToolCreator


class IdentifyToolNeed(Action):
    """識別工具需求的 Action"""
    
    PROMPT_TEMPLATE: str = """
    您正在執行以下任務：
    {task_description}

    當前可用的工具：
    {available_tools}

    ### 分析任務
    請分析執行此任務是否需要新的工具。考慮以下問題：
    1. 現有工具是否足以完成任務？
    2. 如果現有工具不足，需要什麼樣的新工具？
    3. 新工具應該具備什麼功能？
    4. 新工具的輸入輸出應該是什麼？

    ### 輸出格式
    如果不需要新工具，回傳：
    NEED_TOOL: false

    如果需要新工具，回傳：
    NEED_TOOL: true
    TOOL_REQUIREMENT: [詳細描述新工具的需求，包括功能、參數、返回值等]
    TOOL_NAME: [建議的工具名稱]
    """

    async def run(self, task_description: str, available_tools: List[str]) -> Dict:
        """識別是否需要新工具"""
        tools_str = "\n".join([f"- {tool}" for tool in available_tools])
        prompt = self.PROMPT_TEMPLATE.format(
            task_description=task_description,
            available_tools=tools_str
        )
        
        rsp = await self._aask(prompt)
        return self._parse_response(rsp)
    
    @staticmethod
    def _parse_response(rsp: str) -> Dict:
        """解析回應"""
        result = {
            "need_tool": False,
            "tool_requirement": "",
            "tool_name": ""
        }
        
        if "NEED_TOOL: true" in rsp:
            result["need_tool"] = True
            
            # 提取工具需求
            if "TOOL_REQUIREMENT:" in rsp:
                requirement_match = rsp.split("TOOL_REQUIREMENT:")[1]
                if "TOOL_NAME:" in requirement_match:
                    result["tool_requirement"] = requirement_match.split("TOOL_NAME:")[0].strip()
                else:
                    result["tool_requirement"] = requirement_match.strip()
            
            # 提取工具名稱
            if "TOOL_NAME:" in rsp:
                result["tool_name"] = rsp.split("TOOL_NAME:")[1].strip().split("\n")[0].strip()
        
        return result


class SelfEvolvingAgent(Role):
    """自我進化 Agent：能夠創造工具來增強自身能力"""
    
    name: str = "Evolver"
    profile: str = "SelfEvolvingAgent"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tool_creator = ToolCreator()
        self.identify_need_action = IdentifyToolNeed()
        self.created_tools: List[str] = []  # 記錄已創造的工具
        self.set_actions([IdentifyToolNeed])
    
    async def _act(self) -> Message:
        """執行自我進化循環"""
        logger.info(f"{self._setting}: 開始執行任務")
        
        # 獲取當前任務
        msg = self.get_memories(k=1)[0]
        task_description = msg.content
        
        # 步驟 1: 識別是否需要新工具
        available_tools = self._get_available_tools()
        need_analysis = await self.identify_need_action.run(
            task_description, 
            available_tools
        )
        
        # 步驟 2: 如果需要，創造新工具
        if need_analysis.get("need_tool"):
            logger.info("檢測到需要新工具，開始創造...")
            tool_result = await self.tool_creator.create_and_register_tool(
                need_analysis.get("tool_requirement", task_description)
            )
            
            if tool_result.get("success"):
                tool_name = tool_result.get("tool_name", "unknown")
                self.created_tools.append(tool_name)
                logger.info(f"成功創造並註冊工具: {tool_name}")
                
                # 更新可用工具列表
                available_tools = self._get_available_tools()
            else:
                logger.warning(f"創造工具失敗: {tool_result.get('error')}")
        
        # 步驟 3: 執行任務（這裡可以整合 DataInterpreter 或其他執行器）
        # 目前先回傳結果訊息
        result_msg = f"""
        任務分析完成。
        是否需要新工具: {need_analysis.get('need_tool', False)}
        已創造的工具: {', '.join(self.created_tools) if self.created_tools else '無'}
        可用工具: {', '.join(available_tools[:5])}...
        """
        
        return Message(
            content=result_msg,
            role=self.profile,
            cause_by=type(self.identify_need_action)
        )
    
    def _get_available_tools(self) -> List[str]:
        """獲取當前可用的工具列表"""
        from metagpt.tools.tool_registry import TOOL_REGISTRY
        return list(TOOL_REGISTRY.tools.keys())


async def main():
    """範例使用"""
    agent = SelfEvolvingAgent()
    
    # 測試任務：需要一個計算斐波那契數列的工具
    task = "計算前 10 個斐波那契數列的值"
    
    result = await agent.run(task)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

