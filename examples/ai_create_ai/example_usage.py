#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI-create-AI 使用範例
展示如何使用各種核心功能
"""
import sys
import asyncio
from pathlib import Path

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.tool_registry import register_tool

from examples.ai_create_ai.enhanced_agent_creator import AgentCreatorEnhanced
from examples.ai_create_ai.tool_creator import ToolCreator
from examples.ai_create_ai.self_evolving_agent import SelfEvolvingAgent


# ========== 範例 1: AI 產生 AI Agent ==========
async def example_1_create_agent():
    """範例 1: 使用 AI 產生 AI Agent"""
    print("=" * 60)
    print("範例 1: AI 產生 AI Agent")
    print("=" * 60)
    
    creator = AgentCreatorEnhanced()
    
    requirement = """
    建立一個名為 DataProcessor 的 Agent，它能夠：
    1. 接收 CSV 檔案路徑
    2. 讀取並分析資料
    3. 產生資料統計報告
    4. 將報告儲存為 Markdown 檔案
    """
    
    result = await creator.run(requirement)
    print(f"\n結果:\n{result.content}\n")


# ========== 範例 2: Agent 自行創造工具 ==========
async def example_2_create_tool():
    """範例 2: Agent 自行創造工具"""
    print("=" * 60)
    print("範例 2: Agent 自行創造工具")
    print("=" * 60)
    
    tool_creator = ToolCreator()
    
    # 需求：創造一個計算斐波那契數列的工具
    requirement = """
    創造一個工具函式，能夠計算斐波那契數列的第 n 項。
    函式應該：
    - 接收一個整數 n 作為參數
    - 回傳第 n 個斐波那契數
    - 使用高效算法（避免遞迴）
    """
    
    result = await tool_creator.create_and_register_tool(requirement)
    
    if result.get("success"):
        print(f"\n✓ 工具創造成功！")
        print(f"  工具名稱: {result.get('tool_name')}")
        print(f"  工具路徑: {result.get('tool_path')}")
        print(f"\n工具程式碼:\n{result.get('tool_code')}\n")
    else:
        print(f"\n✗ 工具創造失敗: {result.get('error')}\n")


# ========== 範例 3: 使用 DataInterpreter 與自訂工具 ==========
async def example_3_data_interpreter():
    """範例 3: 使用 DataInterpreter 與自訂工具"""
    print("=" * 60)
    print("範例 3: DataInterpreter 與自訂工具")
    print("=" * 60)
    
    # 定義一個簡單的自訂工具
    @register_tool()
    def calculate_factorial(n: int) -> int:
        """
        計算階乘
        
        Args:
            n (int): 要計算階乘的數字
            
        Returns:
            int: n 的階乘
        """
        if n < 0:
            raise ValueError("階乘只能計算非負整數")
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
    
    # 使用 DataInterpreter
    di = DataInterpreter(tools=["calculate_factorial"])
    task = "計算 5 的階乘，並告訴我結果"
    
    print(f"任務: {task}\n")
    result = await di.run(task)
    print(f"結果: {result}\n")


# ========== 範例 4: 自我進化 Agent ==========
async def example_4_self_evolving():
    """範例 4: 自我進化 Agent"""
    print("=" * 60)
    print("範例 4: 自我進化 Agent")
    print("=" * 60)
    
    agent = SelfEvolvingAgent()
    
    # 任務：需要一個計算質數的工具
    task = "我需要一個工具來判斷一個數字是否為質數，並列出 1 到 100 之間的所有質數"
    
    print(f"任務: {task}\n")
    result = await agent.run(task)
    print(f"結果:\n{result.content}\n")
    
    # 顯示已創造的工具
    if agent.created_tools:
        print(f"已創造的工具: {', '.join(agent.created_tools)}\n")


# ========== 範例 5: 完整工作流程 ==========
async def example_5_complete_workflow():
    """範例 5: 完整工作流程 - 從需求到工具創造"""
    print("=" * 60)
    print("範例 5: 完整工作流程")
    print("=" * 60)
    
    # 步驟 1: 創造一個專門處理資料的 Agent
    print("步驟 1: 創造資料處理 Agent...")
    creator = AgentCreatorEnhanced()
    agent_requirement = """
    建立一個名為 DataAnalyzer 的 Agent，它能夠：
    1. 讀取 CSV 檔案
    2. 進行基本統計分析
    3. 產生視覺化圖表
    """
    agent_result = await creator.run(agent_requirement)
    print("✓ Agent 創造完成\n")
    
    # 步驟 2: 創造需要的工具
    print("步驟 2: 創造資料分析工具...")
    tool_creator = ToolCreator()
    tool_requirement = """
    創造一個工具，能夠計算列表的統計資訊：
    - 平均值
    - 中位數
    - 標準差
    - 最大值和最小值
    """
    tool_result = await tool_creator.create_and_register_tool(tool_requirement)
    
    if tool_result.get("success"):
        print(f"✓ 工具創造成功: {tool_result.get('tool_name')}\n")
    else:
        print(f"✗ 工具創造失敗: {tool_result.get('error')}\n")
    
    print("完整工作流程執行完成！")


# ========== 主程式 ==========
async def main():
    """執行所有範例"""
    print("\n" + "=" * 60)
    print("AI-create-AI 功能展示")
    print("=" * 60 + "\n")
    
    try:
        # 執行各個範例
        await example_1_create_agent()
        await example_2_create_tool()
        await example_3_data_interpreter()
        await example_4_self_evolving()
        await example_5_complete_workflow()
        
        print("\n" + "=" * 60)
        print("所有範例執行完成！")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n執行範例時發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

