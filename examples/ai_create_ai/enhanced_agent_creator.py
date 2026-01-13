#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增強的 Agent 創造器：支援繁體中文提示，能夠產生更符合需求的 Agent
"""
import re
import asyncio
from pathlib import Path

import sys
from pathlib import Path

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from metagpt.actions import Action
from metagpt.config2 import config
from metagpt.const import METAGPT_ROOT
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message

EXAMPLE_CODE_FILE = METAGPT_ROOT / "examples/build_customized_agent.py"
MULTI_ACTION_AGENT_CODE_EXAMPLE = EXAMPLE_CODE_FILE.read_text()


class CreateAgentEnhanced(Action):
    """增強的 Agent 創造 Action，支援繁體中文"""
    
    PROMPT_TEMPLATE: str = """
    ### 背景說明
    您正在使用一個名為 MetaGPT 的 Agent 框架來撰寫具備不同能力的智能體。
    以下是一個使用範例，展示了如何使用 MetaGPT 框架：

    ### 範例程式碼開始
    {example}
    ### 範例程式碼結束

    ### 任務說明
    請根據以下需求，建立一個具備適當 Actions 的 Agent。請仔細考慮：
    1. 每個 Action 的 PROMPT_TEMPLATE 應該如何設計
    2. 何時應該呼叫 self._aask()
    3. 如何解析和處理回應
    4. Agent 應該具備哪些 Actions 才能完成需求

    ### 需求描述
    {instruction}

    ### 要求
    1. 程式碼必須完整且可執行
    2. 包含必要的 import 語句
    3. 每個 Action 都應該有清晰的 PROMPT_TEMPLATE
    4. Agent 類別應該正確繼承 Role 並設定 Actions
    5. 如果需要的話，可以包含多個 Actions 來完成複雜任務

    ### 輸出格式
    請只回傳 Python 程式碼，使用 ```python 和 ``` 包圍。
    不要包含其他文字說明。
    """

    async def run(self, example: str, instruction: str) -> str:
        """根據需求產生 Agent 程式碼"""
        prompt = self.PROMPT_TEMPLATE.format(example=example, instruction=instruction)
        rsp = await self._aask(prompt)
        code_text = self.parse_code(rsp)
        return code_text

    @staticmethod
    def parse_code(rsp: str) -> str:
        """從回應中解析 Python 程式碼"""
        pattern = r"```python(.*?)```"
        match = re.search(pattern, rsp, re.DOTALL)
        if match:
            code_text = match.group(1).strip()
        else:
            # 如果沒有找到程式碼塊，嘗試提取類別定義
            pattern = r"class\s+\w+.*?(?=\n\n|\n```|$)"
            match = re.search(pattern, rsp, re.DOTALL)
            if match:
                code_text = match.group(0).strip()
            else:
                code_text = rsp.strip()
        
        # 確保程式碼目錄存在
        config.workspace.path.mkdir(parents=True, exist_ok=True)
        return code_text


class AgentCreatorEnhanced(Role):
    """增強的 Agent 創造器"""
    
    name: str = "AgentCreator"
    profile: str = "EnhancedAgentCreator"
    agent_template: str = MULTI_ACTION_AGENT_CODE_EXAMPLE

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CreateAgentEnhanced])

    async def _act(self) -> Message:
        """執行 Agent 創造流程"""
        logger.info(f"{self._setting}: 開始創造 Agent")
        todo = self.rc.todo
        msg = self.rc.memory.get()[-1]

        instruction = msg.content
        code_text = await CreateAgentEnhanced().run(
            example=self.agent_template, 
            instruction=instruction
        )
        
        # 儲存產生的程式碼
        output_file = config.workspace.path / "agent_created_agent.py"
        output_file.write_text(code_text, encoding="utf-8")
        logger.info(f"Agent 程式碼已儲存至: {output_file}")
        
        msg = Message(
            content=f"Agent 已成功產生！\n程式碼已儲存至: {output_file}\n\n程式碼內容：\n{code_text[:500]}...",
            role=self.profile,
            cause_by=todo
        )

        return msg


async def main():
    """範例使用"""
    creator = AgentCreatorEnhanced()

    # 繁體中文需求描述
    requirement = """
    建立一個名為 SimpleTester 的 Agent，它能夠：
    1. 接收任何程式碼片段（字串）
    2. 為給定程式碼撰寫測試程式碼，並將測試程式碼儲存為 .py 檔案
    3. 執行測試程式碼
    可以使用 pytest 作為測試框架。
    """
    
    result = await creator.run(requirement)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

