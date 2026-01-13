# AI-create-AI 快速開始指南

本指南將幫助您快速開始使用 AI-create-AI 的核心功能。

## 📋 前置需求

1. 已安裝 MetaGPT 框架
2. 已設定 `~/.metagpt/config2.yaml` 配置檔案
3. Python 3.9 或更高版本（但低於 3.12）

## 🚀 快速開始

### 1. 基本使用：AI 產生 AI Agent

```python
import asyncio
from examples.ai_create_ai import AgentCreatorEnhanced

async def main():
    creator = AgentCreatorEnhanced()
    
    requirement = """
    建立一個名為 SimpleTester 的 Agent，它能夠：
    1. 接收任何程式碼片段（字串）
    2. 為給定程式碼撰寫測試程式碼，並將測試程式碼儲存為 .py 檔案
    3. 執行測試程式碼
    可以使用 pytest 作為測試框架。
    """
    
    result = await creator.run(requirement)
    print(result.content)

asyncio.run(main())
```

### 2. 工具動態創造

```python
import asyncio
from examples.ai_create_ai import ToolCreator

async def main():
    tool_creator = ToolCreator()
    
    requirement = """
    創造一個工具函式，能夠計算斐波那契數列的第 n 項。
    函式應該接收一個整數 n，回傳第 n 個斐波那契數。
    """
    
    result = await tool_creator.create_and_register_tool(requirement)
    
    if result.get("success"):
        print(f"✓ 工具 {result['tool_name']} 已成功註冊！")
        print(f"  工具路徑: {result['tool_path']}")
    else:
        print(f"✗ 錯誤: {result.get('error')}")

asyncio.run(main())
```

### 3. 自我進化 Agent

```python
import asyncio
from examples.ai_create_ai import SelfEvolvingAgent

async def main():
    agent = SelfEvolvingAgent()
    
    task = "我需要一個工具來判斷一個數字是否為質數，並列出 1 到 100 之間的所有質數"
    
    result = await agent.run(task)
    print(result.content)
    
    # 查看已創造的工具
    print(f"已創造的工具: {agent.created_tools}")

asyncio.run(main())
```

## 📝 執行範例

執行完整範例程式碼：

```bash
# 從專案根目錄執行
python examples/ai_create_ai/example_usage.py
```

## 🔍 檢查結果

### Agent 程式碼
產生的 Agent 程式碼會儲存在：
```
workspace/agent_created_agent.py
```

### 工具程式碼
創造的工具會儲存在：
```
workspace/tools/{tool_name}.py
```

### 工具註冊
所有工具都會自動註冊到 `TOOL_REGISTRY`，可以在後續任務中使用。

## 💡 進階技巧

### 整合到現有專案

```python
from examples.ai_create_ai import ToolCreator
from metagpt.roles.di.data_interpreter import DataInterpreter

# 創造工具
tool_creator = ToolCreator()
result = await tool_creator.create_and_register_tool("工具需求")

# 在 DataInterpreter 中使用
if result.get("success"):
    tool_name = result["tool_name"]
    di = DataInterpreter(tools=[tool_name])
    await di.run("使用新工具執行任務")
```

### 批量創造工具

```python
async def create_multiple_tools():
    tool_creator = ToolCreator()
    requirements = [
        "計算階乘的工具",
        "計算斐波那契數列的工具",
        "判斷質數的工具"
    ]
    
    results = []
    for req in requirements:
        result = await tool_creator.create_and_register_tool(req)
        results.append(result)
    
    return results
```

## ⚠️ 常見問題

### Q: 工具創造失敗怎麼辦？
A: 檢查錯誤訊息，通常可能是：
- 需求描述不夠清晰
- 程式碼語法錯誤
- 工具名稱衝突

### Q: 如何查看已註冊的工具？
A: 
```python
from metagpt.tools.tool_registry import TOOL_REGISTRY
print(list(TOOL_REGISTRY.tools.keys()))
```

### Q: 產生的 Agent 如何執行？
A: 產生的 Agent 程式碼會儲存在 `workspace/agent_created_agent.py`，您可以：
1. 直接執行該檔案
2. 導入並使用該 Agent
3. 根據需求修改程式碼

## 📚 更多資源

- [完整使用指南](README.md)
- [主專案 README](../../README.md)
- [MetaGPT 文件](https://docs.deepwisdom.ai/main/en/)

