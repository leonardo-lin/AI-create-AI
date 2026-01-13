# AI-create-AI 核心模組使用指南

本目錄包含實現「AI 產生 AI Agent 並自行創造工具」核心功能的模組。

## 📁 檔案結構

```
examples/ai_create_ai/
├── __init__.py                 # 模組初始化
├── enhanced_agent_creator.py   # 增強的 Agent 創造器（支援繁體中文）
├── tool_creator.py             # 工具創造器
├── self_evolving_agent.py      # 自我進化 Agent
├── example_usage.py            # 完整使用範例
└── README.md                   # 本檔案
```

## 🚀 核心功能

### 1. AgentCreatorEnhanced - AI 產生 AI Agent

讓 AI 根據自然語言描述自動產生具備特定能力的 Agent。

```python
from examples.ai_create_ai import AgentCreatorEnhanced

creator = AgentCreatorEnhanced()

requirement = """
建立一個名為 DataProcessor 的 Agent，它能夠：
1. 接收 CSV 檔案路徑
2. 讀取並分析資料
3. 產生資料統計報告
"""

result = await creator.run(requirement)
# 產生的 Agent 程式碼會儲存在 workspace/agent_created_agent.py
```

### 2. ToolCreator - 工具動態創造

讓 Agent 能夠根據需求自動設計、實作並註冊新工具。

```python
from examples.ai_create_ai import ToolCreator

tool_creator = ToolCreator()

requirement = """
創造一個工具函式，能夠計算斐波那契數列的第 n 項。
函式應該接收一個整數 n，回傳第 n 個斐波那契數。
"""

result = await tool_creator.create_and_register_tool(requirement)
if result.get("success"):
    print(f"工具 {result['tool_name']} 已成功註冊！")
```

### 3. SelfEvolvingAgent - 自我進化 Agent

實現完整的自我進化循環：識別需求 → 創造工具 → 增強能力。

```python
from examples.ai_create_ai import SelfEvolvingAgent

agent = SelfEvolvingAgent()

task = "我需要一個工具來判斷一個數字是否為質數"
result = await agent.run(task)

# Agent 會自動：
# 1. 分析任務需求
# 2. 判斷是否需要新工具
# 3. 如果需要，自動創造並註冊工具
# 4. 使用新工具完成任務
```

## 💡 使用範例

執行完整範例：

```bash
python examples/ai_create_ai/example_usage.py
```

這個腳本會展示：
1. AI 產生 AI Agent
2. Agent 自行創造工具
3. 使用 DataInterpreter 與自訂工具
4. 自我進化 Agent 的工作流程
5. 完整的工作流程整合

## 🔧 進階使用

### 自訂工具創造流程

```python
from examples.ai_create_ai import CreateTool, RegisterTool

# 步驟 1: 創造工具程式碼
create_action = CreateTool()
tool_code = await create_action.run("創造一個計算階乘的工具")

# 步驟 2: 註冊工具
register_action = RegisterTool()
result = await register_action.run(tool_code)
```

### 整合到現有 Agent

```python
from metagpt.roles import Role
from examples.ai_create_ai import ToolCreator

class MyCustomAgent(Role):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tool_creator = ToolCreator()
    
    async def _act(self):
        # 在執行任務時，如果需要新工具
        if self.need_new_tool():
            result = await self.tool_creator.create_and_register_tool(
                "工具需求描述"
            )
        # ... 繼續執行任務
```

## 📝 注意事項

1. **工具註冊**：創造的工具會自動註冊到 `TOOL_REGISTRY`，可以在後續任務中使用
2. **程式碼儲存**：產生的 Agent 程式碼會儲存在 `workspace/agent_created_agent.py`
3. **工具儲存**：創造的工具會儲存在 `workspace/tools/` 目錄
4. **錯誤處理**：所有操作都包含錯誤處理，會回傳詳細的錯誤訊息

## 🎯 應用場景

- **自動化測試 Agent**：自動產生測試程式碼並執行
- **資料分析 Agent**：根據需求創造資料處理工具
- **程式碼產生 Agent**：自動產生符合規範的程式碼
- **工具鏈建構**：為特定領域自動建構專用工具集
- **自我優化系統**：Agent 持續改進自身能力

## 📚 相關文件

- [主 README](../../README.md)
- [MetaGPT 文件](https://docs.deepwisdom.ai/main/en/)

