# OpenDrSai 

由高能物理研究所Dr.Sai团队开发的智能体与多智能体协同系统快速开发框架，可快速地开发和部署自己的智能体与多智能体协作系统后端服务。

<div align="center">
  <p>
      <img width="80%" src="assets/drsai.png" alt="适配逻辑图">
  </p>
</div>

## 1.特色

- 1.可基于[HepAI平台](https://ai.ihep.ac.cn/)进行智能体基座模型的灵活切换。
- 2.为智能体设计了感知、思考、记忆、执行等行为功能，并进行了插件化设计，可灵活扩展，满足多种应用场景。
- 3.提供了智能体选择制和举手制等多种多智能体协同逻辑
- 4.为智能体和多智能体协作系统交互提供了兼容OpenAI Chat和OpenAI ASSISTANTS的标准后端接口，可与兼容OpenAI输出的前端进行无缝对接，从而可将智能体和多智能体协作系统作为模型或智能体服务进行部署。

## 2.快速开始

### 2.1.安装DrSai

#### pip 安装

```shell
conda create -n drsai python=>3.10
conda activate drsai
pip install DrSai -U
```

#### 从源码安装和配置DrSai运行环境

创建[code.ihep.ac.cn](https://code.ihep.ac.cn/)账号，克隆OpenDrSai仓库到本地：
```shell
git clone https://code.ihep.ac.cn/hepai/drsai.git drsai
cd drsai
```

配置conda环境，安装依赖包：
```shell
conda create -n drsai python>=3.10
conda activate drsai
pip install .
```

#### 配置HepAI平台的API访问密钥

配置[HepAI](https://ai.ihep.ac.cn)DDF2平台的API访问密钥等环境变量(Based on bash)：
```shell
vi ~/.bashrc
export HEPAI_API_KEY2=your_api_key
source ~/.bashrc
```

### 2.2.创建一个可以使用函数作为工具的简单智能体

```python
from DrSai import HepAIChatCompletionClient, AssistantAgent, run_console

# Define a model client.
model_client = HepAIChatCompletionClient(
    model="openai/gpt-4o",
    # api_key="YOUR_API_KEY",
)

# Define a simple function tool that the agent can use.
# For this example, we use a fake weather tool for demonstration purposes.
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."

# Define an AssistantAgent with the model, tool, system message, 
# The system message instructs the agent via natural language.
agent = AssistantAgent(
    name="weather_agent",
    model_client=model_client,
    tools=[get_weather],
    system_message="You are a helpful assistant.",
    model_client_stream=False,  # Enable streaming tokens from the model client.
)

# Yon can define mutliple AssistantAgents with different tools and behaviors. Just add them to the list.

# Start the run_console with the agent.
run_console(agent, task="What is the weather in New York?")
# run_backend(agent)
```

## 3.自定义智能体开发案例

### 3.1.使用简单的RAG函数作为智能体的记忆层

```python
from DrSai import HepAIChatCompletionClient, AssistantAgent, run_console

# Define a model client. 
model_client = HepAIChatCompletionClient(
    model="openai/gpt-4o",
    # api_key="YOUR_API_KEY",
)

# Define a simple function for RAG.
# Please note that the function must take a messages parameter,
#  which is a list of dictionaries representing the chat history. 
# You can modify the messages list in place and return it.
def rag_demo(messages_rag: List[Dict], **kwargs):
    query = messages_rag[-1]["content"] # 选择聊天记录最后一条消息作为RAG的查询语句
    retrieve_txt = "1.人类将于2050年被AI毁灭；\n2.人类被AI毁灭是因为人类的傲慢与自大"
    last_txt =f"""以下是一些参考资料，必须参考这些资料回答问题：\n{retrieve_txt}。我的问题是：{query}"""
    messages_rag[-1]["content"] = last_txt
    return messages_rag


# Define an AssistantAgent with the model, tool, system message, 
# The system message instructs the agent via natural language.
assistant = AssistantAgent(
    name="AssistantAgent", # 定义了智能体的名称
    model_client=model_client, # 定义了模型和api的配置
    memory_function = rag_demo, # 定义了访问记忆层函数
    system_message = "你是一个知识问答助手", # 定义了系统消息
    description="一个知识问答助手") # 定义了智能体的描述

# Start the run_console with the agent.
run_console(assistant, task="人类为什么会毁灭")
# run_backend(agent)
```

### 3.2.自定义智能体的回复逻辑

```python
from DrSai import HepAIChatCompletionClient, AssistantAgent, run_console

# Define a model client. 
model_client = HepAIChatCompletionClient(
    model="openai/gpt-4o",
    # api_key="YOUR_API_KEY",
)

# Adressing the messages and return the response. Must accept messages and return a string, a dictionary with content field, or a generator for streaming output.
def interface(messages: List[Dict], **kwargs) -> Union[Dict, str, Generator]:
    """adressing the messages and return the response"""
    return "test_worker reply"


# Create an AssistantAgent with your custom reply.
assistant = AssistantAgent(
    name="AssistantAgent", # 定义了智能体的名称
    model_client=model_client, # 定义了模型和api的配置
    system_message = "你是一个自定义的功能助手",  # 定义了LLM的系统消息
    description="一个自定义的功能助手", # 定义了智能体的描述
    reply_function = interface) # 传入自定义的回复函数

run_console(assistant, task="人类为什么会毁灭")
# run_backend(agent)
```

## 4.将DrSai部署为OpenAI格式的后端模型服务或者HepAI woker服务

### 4.1.部署为OpenAI格式的后端模型服务/HepAI worker服务
```python
from DrSai import run_backend, run_hepai_worker
run_backend([agent]) # 部署为OpenAI格式的后端模型服务
# run_hepai_worker([agent]) # 部署为HepAI worker服务
```

### 4.2.使用HepAI client访问的方式访问定制好的智能体

```python
from hepai import HepAI 
import os
import json
import requests
import sys

HEPAI_API_KEY = os.getenv("HEPAI_API_KEY2")
base_url = "http://localhost:42801/apiv2"


# 调用HepAI client接口
client = HepAI(api_key=HEPAI_API_KEY, base_url=base_url)
completion = client.chat.completions.create(
  model='hepai/Dr-Sai',
  messages=[
    {"role": "user", "content": "请使用百度搜索什么是Ptychography?"}
  ],
  stream=True
)
for chunk in completion:
  if chunk.choices[0].delta.content:
    print(chunk.choices[0].delta.content, end='', flush=True)
print('\n')
```

## 5.详细文档
见docs目录：
```shell
.
├── 1-Agent_components.md         # 智能体组件开发介绍
├── 2-Agent.md                    # 智能体开发介绍
├── 3-Multi-Agent_system.md       # 多智能体协作系统开发介绍
├── 4-backend.md                  # 后端服务开发介绍
├── developer.md                  # 开发者指南
└── 0-Re0:Dr.Sai.md               # Dr.Sai开发逻辑
```

## 6.联系我们

- 邮箱：hepai@ihep.ac.cn/xiongdb@ihep.ac.cn
- 微信：xiongdongbo_12138