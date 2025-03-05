# Seele SDK

Seele SDK 是一个用于与 Seele Agent 服务交互的 Python 工具包。它提供了一个简单的接口，用于与 AI 代理进行通信，包括思考、图像处理和自定义能力调用等功能。

## 安装

使用 pip 安装：

```bash
pip install seele-sdk
```

## 运行模式

SDK 有两种运行模式：

### 1. 平台模式
在 Seele 平台环境中运行时：
- Agent 信息会由平台自动注入
- 无需手动配置任何信息
- 必须在 Agent 配置面板中启用相应的能力才能调用
- 默认 base_url 为 http://127.0.0.1:8086

### 2. 本地开发模式
在本地开发和测试时：
- 需要手动提供 agent_info 字典（至少包含 id 字段）
- 确保调用的能力已在 Agent 配置面板中启用
- 可以根据需要覆盖 base_url

## 快速开始

以下是使用 SDK 的简单示例：

```python
from seele_sdk import AgentContext

# 本地开发：模拟 agent_info
agent_info = {
    "id": 53,  # 必需字段
    "name": "会议室302记录助手",  # 可选
    "description": "用于监控302会议室的助手",  # 可选
    "capabilities": {  # 可选
        "space_analysis": ["body_detection", "multimodal_vision"]
    }
}

# 使用上下文管理器（使用默认 base_url: http://127.0.0.1:8086）
with AgentContext(agent_info) as ctx:
    # 发送思考请求
    response = ctx.think("会议室现在是什么状态？")
    print(response)
    
    # 处理图片
    image_urls = ["http://example.com/image1.jpg"]
    response = ctx.look("描述一下这张图片中的内容", image_urls)
    print(response)
    
    # 调用自定义能力
    # 注意：必须在 Agent 配置面板中启用相应的能力才能调用
    result = ctx.call_ability("space_analysis", "body_detection", "image_url")
    print(result)
```

## 最简配置

在本地开发时，如果只需要基本功能，可以只提供 id：

```python
from seele_sdk import AgentContext

# 最简配置
with AgentContext({"id": 53}) as ctx:
    response = ctx.think("你好")
    print(response)
```

## 直接使用 AgentSDK

如果你不想使用上下文管理器，可以直接使用 SDK：

```python
from seele_sdk import AgentSDK

# 初始化 SDK（使用默认 base_url）
sdk = AgentSDK(base_url="http://127.0.0.1:8086", agent_id=53)

# 发送思考请求
response = sdk.think("当前状态如何？")

# 处理图片
response = sdk.look("描述这张图片", ["http://example.com/image1.jpg"])

# 调用能力（需要在 Agent 配置中启用）
result = sdk.call_ability("namespace", "ability_name", "arg1", "arg2")
```

### 关于能力的重要说明

1. **能力配置**
   - 必须在 Agent 配置面板中启用相应的能力才能调用
   - 调用未配置的能力会导致错误
   - 本地开发时可以在 agent_info 中列出能力，但这只是为了参考

2. **平台模式 vs 本地开发**
   - 平台模式：所有配置由平台自动注入，无需手动设置
   - 本地开发：只需提供必要的 agent_info（至少包含 id）

## 错误处理

SDK 内置了错误处理和日志记录功能：

```python
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

try:
    with AgentContext({"id": 53}) as ctx:
        response = ctx.think("你好")
except Exception as e:
    print(f"发生错误: {e}")
```

## 贡献

欢迎提交 Pull Request 来改进这个项目！

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。
