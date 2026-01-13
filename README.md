# AI-create-AI: AI 自我進化的多智能體框架

<p align="center">
<b>讓 AI 產生 AI Agent，並自行創造符合自身需求的工具</b>
</p>

<p align="center">
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
<a href="https://github.com/geekan/MetaGPT"><img src="https://img.shields.io/badge/Based%20on-MetaGPT-green.svg" alt="Based on MetaGPT"></a>
</p>

## 🌟 核心理念

**AI-create-AI** 是一個革命性的多智能體框架，致力於實現 AI 的自我進化能力：

1. **AI 產生 AI Agent**：透過自然語言描述，AI 可以自動產生具備特定能力的智能體
2. **工具自我創造**：AI Agent 能夠識別任務需求，自行設計、實作並註冊符合自身需求的工具
3. **持續自我優化**：Agent 在使用過程中不斷學習，創造更高效的工具來提升自身能力

### 核心特性

- 🤖 **Agent 自動產生**：只需描述需求，AI 即可產生完整的 Agent 程式碼
- 🛠️ **工具動態創造**：Agent 可以根據任務需求自動設計和實作新工具
- 🔄 **自我進化循環**：Agent → 識別需求 → 創造工具 → 增強能力 → 處理更複雜任務
- 📦 **工具註冊系統**：完善的工具註冊、發現和推薦機制
- 🎯 **智能工具推薦**：基於任務需求自動推薦最合適的工具

## 🚀 快速開始

### 安裝

> 確保系統已安裝 Python 3.9 或更高版本（但低於 3.12）。可以使用 `python --version` 檢查。  
> 可以使用 conda：`conda create -n ai-create-ai python=3.9 && conda activate ai-create-ai`

```bash
pip install --upgrade metagpt
# 或 `pip install --upgrade git+https://github.com/geekan/MetaGPT.git`
# 或 `git clone https://github.com/geekan/MetaGPT && cd MetaGPT && pip install --upgrade -e .`
```

**在實際使用前，請先安裝 [node](https://nodejs.org/en/download) 和 [pnpm](https://pnpm.io/installation#using-npm)。**

### 設定

執行以下指令初始化設定，或手動建立 `~/.metagpt/config2.yaml` 檔案：

```bash
metagpt --init-config  # 將建立 ~/.metagpt/config2.yaml，依需求修改即可
```

設定 `~/.metagpt/config2.yaml`：

```yaml
llm:
  api_type: "openai"  # 或 azure / ollama / groq 等
  model: "gpt-4-turbo"  # 或 gpt-3.5-turbo
  base_url: "https://api.openai.com/v1"  # 或轉發 URL / 其他 LLM URL
  api_key: "YOUR_API_KEY"
```

## 💡 使用範例

### 範例 1: AI 產生 AI Agent

讓 AI 根據您的需求自動建立一個新的 Agent：

```python
import asyncio
from examples.agent_creator import AgentCreator

async def main():
    creator = AgentCreator()
    
    # 描述您想要的 Agent 功能
    requirement = """
    建立一個名為 SimpleTester 的 Agent，它能夠：
    1. 接收任何程式碼片段（字串）
    2. 為給定程式碼撰寫測試程式碼，並將測試程式碼儲存為 .py 檔案
    3. 執行測試程式碼
    可以使用 pytest 作為測試框架。
    """
    
    await creator.run(requirement)
    # 產生的 Agent 程式碼將儲存在 workspace/agent_created_agent.py

asyncio.run(main())
```

### 範例 2: Agent 自行創造工具

Agent 可以根據任務需求自動建立並使用自訂工具：

```python
import asyncio
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.tool_registry import register_tool

# 定義自訂工具（Agent 也可以動態產生這些工具）
@register_tool()
def magic_function(arg1: str, arg2: int) -> dict:
    """
    執行某種魔法操作
    
    Args:
        arg1 (str): 第一個參數
        arg2 (int): 第二個參數
        
    Returns:
        dict: 處理結果
    """
    return {"arg1": arg1 * 3, "arg2": arg2 * 5}

async def main():
    # DataInterpreter 會自動發現並使用註冊的工具
    di = DataInterpreter(tools=["magic_function"])
    await di.run("使用 magic_function，arg1='A'，arg2=2，告訴我結果。")

asyncio.run(main())
```

### 範例 3: 建構自訂 Agent

建立具有特定能力的 Agent：

```python
import asyncio
from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.schema import Message

class SimpleWriteCode(Action):
    PROMPT_TEMPLATE: str = """
    撰寫一個 Python 函式，能夠 {instruction}，並提供兩個可執行的測試用例。
    回傳 ```python your_code_here ```，不要其他文字。
    """
    
    async def run(self, instruction: str):
        prompt = self.PROMPT_TEMPLATE.format(instruction=instruction)
        rsp = await self._aask(prompt)
        # 解析並回傳程式碼
        return self.parse_code(rsp)

class SimpleCoder(Role):
    name: str = "Alice"
    profile: str = "SimpleCoder"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteCode])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.get_memories(k=1)[0]
        code_text = await todo.run(msg.content)
        return Message(content=code_text, role=self.profile, cause_by=type(todo))

# 使用
async def main():
    coder = SimpleCoder()
    result = await coder.run("撰寫一個計算列表乘積的函式並執行它")
    print(result)

asyncio.run(main())
```

## 🏗️ 架構設計

### Agent 產生流程

```
使用者需求描述
    ↓
AgentCreator (AI)
    ↓
分析需求 → 設計 Agent 結構 → 產生程式碼
    ↓
新的 Agent 實例
```

### 工具創造流程

```
Agent 執行任務
    ↓
識別工具需求
    ↓
設計工具介面 → 實作工具程式碼 → 註冊工具
    ↓
使用新工具完成任務
```

### 核心元件

1. **AgentCreator**: 根據自然語言描述產生 Agent 程式碼
2. **ToolRegistry**: 工具註冊中心，管理所有可用工具
3. **ToolRecommender**: 智能工具推薦系統
4. **DataInterpreter**: 資料解釋器，能夠動態發現和使用工具
5. **RoleZero**: 基礎角色類別，支援工具動態載入

## 📚 文件與教學

- 📖 [線上文件](https://docs.deepwisdom.ai/main/en/)
- 🎓 [Agent 開發指南](https://docs.deepwisdom.ai/main/en/guide/tutorials/agent_101.html)
- 🔧 [工具開發指南](examples/di/custom_tool.py)
- 💻 [範例程式碼](examples/)

## 🎯 應用場景

- **自動化測試 Agent**：自動產生測試程式碼並執行
- **資料分析 Agent**：根據需求創造資料處理工具
- **程式碼產生 Agent**：自動產生符合規範的程式碼
- **工具鏈建構**：為特定領域自動建構專用工具集
- **自我優化系統**：Agent 持續改進自身能力

## 🤝 貢獻

我們歡迎所有形式的貢獻！請查看 [貢獻指南](docs/ROADMAP.md) 了解如何參與。

## 📄 授權

本專案基於 [MIT 授權](LICENSE) 開源。

## 🙏 致謝

本專案基於 [MetaGPT](https://github.com/geekan/MetaGPT) 框架建構，感謝 MetaGPT 團隊的開源貢獻。

## 📧 聯絡方式

如有任何問題或建議，歡迎透過以下方式聯絡：

- **GitHub Issues**: [建立 Issue](https://github.com/geekan/metagpt/issues)
- **Email**: alexanderwu@deepwisdom.ai

---

<p align="center">
<b>讓 AI 創造 AI，讓工具自我進化</b>
</p>
