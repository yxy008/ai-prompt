# ai-prompt

> Prompt 工程完整实践项目 —— 配套《Prompt 工程完全指南：从原理到最佳实践》

## 项目简介

本项目是《Prompt 工程完全指南：从原理到最佳实践》技术文档的配套代码工程，涵盖了 Prompt 工程从基础到进阶再到工程化的完整知识体系的代码实现。

所有模块均可独立运行，每个文件都包含完整的文档字符串和可直接执行的 `__main__` 入口。

## 项目结构

```
ai-prompt/
├── config.py                          # 共享配置（API Key、模型、温度等）
├── requirements.txt                   # 项目依赖
│
├── ablation/                          # Prompt 基础结构五要素消融实验
│   ├── prompt_role_ablation.py        # 角色设定：无角色/职业角色/场景角色/复合角色
│   ├── prompt_task_ablation.py        # 任务指令：模糊→明确做什么→明确怎么做→明确做到什么程度
│   ├── prompt_context_ablation.py     # 上下文注入：领域知识/RAG文档/对话历史/当前问题
│   ├── prompt_format_ablation.py      # 输出格式控制：无格式/自然语言/JSON/JSON Schema
│   └── prompt_constraints.py          # 约束条件：硬约束/条件约束/软约束
│
├── reasoning/                         # 进阶推理技术
│   ├── prompt_few_shot.py             # 少样本提示 + 示例选择策略（相似度/多样性/难度）
│   ├── prompt_cot.py                  # 思维链：Zero-shot CoT / Few-shot CoT / Auto CoT
│   ├── prompt_self_consistency.py     # 自洽性：多次推理 + 投票机制
│   ├── prompt_tree_of_thoughts.py     # 思维树：束搜索探索最优推理路径
│   └── prompt_react.py               # ReAct：推理与行动交替，集成外部工具
│
├── output/                            # 结构化输出控制
│   ├── prompt_structured_output.py    # JSON 结构化输出 + JSON Schema 原生约束
│   ├── prompt_format_control.py       # Markdown 表格格式输出
│   ├── prompt_code_generation.py      # 代码生成 + 类型注解 + 测试用例
│   └── prompt_multimodal.py           # 多模态 Prompt（文本 + 图片）
│
└── engineering/                       # 工程化工具链
    ├── prompt_ab_test.py              # A/B 测试框架（延迟/Token/成本统计）
    ├── prompt_version_manager.py      # 版本管理（哈希标识 + 差异对比）
    ├── prompt_debugger.py             # 问题诊断（长度/关键元素/测试运行）
    ├── prompt_dspy.py                 # DSPy 自动化 Prompt 优化
    ├── prompt_template_engine.py      # 模板引擎（变量替换 + 完整性验证）
    ├── prompt_security.py             # 安全防护（注入检测 + System Prompt 加固）
    ├── prompt_llm_judge.py            # LLM-as-Judge 评估（多维度评分）
    ├── prompt_multi_model.py          # 多模型适配（GPT-4o / Claude / DeepSeek）
    ├── prompt_chinese.py              # 中文 Prompt 优化（分词/量词/标点/术语）
    ├── prompt_layered.py              # 分层 Prompt 架构（系统层/任务层/上下文层/格式层）
    └── prompt_monitor.py              # 生产监控（成功率/延迟/Token/告警）
```

## 快速开始

### 1. 环境准备

```bash
cd ai-prompt
pip install -r requirements.txt
```

### 2. 配置 API Key

设置环境变量：

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key"

# 可选：自定义 API 地址和模型
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_MODEL = "gpt-4o"
```

### 3. 运行示例

```bash
# 基础结构 —— 角色设定消融实验
python ablation/prompt_role_ablation.py

# 进阶推理 —— 思维链提示
python reasoning/prompt_cot.py

# 结构化输出 —— JSON Schema 约束
python output/prompt_structured_output.py

# 工程化 —— 分层 Prompt 架构
python engineering/prompt_layered.py
```

## 模块说明

### ablation/ —— 基础结构五要素

通过消融实验对比不同 Prompt 设计的效果差异，帮助理解每个要素的作用。

| 文件 | 对比维度 | 核心发现 |
|------|---------|---------|
| `prompt_role_ablation.py` | 无角色 vs 职业角色 vs 场景角色 vs 复合角色 | 角色设定显著改善回答的专业性和一致性 |
| `prompt_task_ablation.py` | 模糊任务 → 明确做什么 → 明确怎么做 → 明确做到什么程度 | 任务精确度直接决定输出质量 |
| `prompt_context_ablation.py` | 领域知识 + RAG文档 + 对话历史 + 当前问题 | 多层上下文注入提升事实准确性 |
| `prompt_format_ablation.py` | 无格式 vs 自然语言 vs JSON vs JSON Schema | JSON Schema 原生约束可靠性达 99%+ |
| `prompt_constraints.py` | 硬约束 + 条件约束 + 软约束 | 分层约束防止输出失控 |

### reasoning/ —— 进阶推理技术

引导 LLM 进行更深层次的推理，适用于数学、逻辑、规划等复杂任务。

| 文件 | 技术 | 适用场景 | API 成本 |
|------|------|---------|---------|
| `prompt_few_shot.py` | 少样本提示 | 格式控制、分类 | 低（1次调用） |
| `prompt_cot.py` | 思维链 | 数学、逻辑推理 | 低（1次调用） |
| `prompt_self_consistency.py` | 自洽性 | 需要高可靠性的推理 | 中（5-10次调用） |
| `prompt_tree_of_thoughts.py` | 思维树 | 创造性规划 | 高（10-50次调用） |
| `prompt_react.py` | ReAct | 需要外部知识的任务 | 中（3-10次调用） |

### output/ —— 结构化输出控制

确保 LLM 输出可被程序解析和下游系统使用。

| 文件 | 输出格式 | 可靠性 |
|------|---------|--------|
| `prompt_structured_output.py` | JSON（含 Schema 约束） | 95-99% |
| `prompt_format_control.py` | Markdown 表格 | 80-90% |
| `prompt_code_generation.py` | 代码（含类型注解和测试） | 85-95% |
| `prompt_multimodal.py` | 多模态（文本+图片） | 取决于模型 |

### engineering/ —— 工程化工具链

将 Prompt 从"手写字符串"提升为"可管理、可测试、可监控的工程资产"。

| 文件 | 功能 | 生产就绪度 |
|------|------|-----------|
| `prompt_ab_test.py` | A/B 测试框架 | 可直接使用 |
| `prompt_version_manager.py` | 版本管理 + 差异对比 | 可直接使用 |
| `prompt_debugger.py` | 问题诊断工具 | 可直接使用 |
| `prompt_dspy.py` | 自动化优化 | 需安装 dspy-ai |
| `prompt_template_engine.py` | 模板引擎 | 可直接使用 |
| `prompt_security.py` | 注入检测 + 加固 | 可直接使用 |
| `prompt_llm_judge.py` | LLM 评估 | 可直接使用 |
| `prompt_multi_model.py` | 多模型适配 | 可直接使用 |
| `prompt_chinese.py` | 中文优化 | 可直接使用 |
| `prompt_layered.py` | 分层架构 | 可直接使用 |
| `prompt_monitor.py` | 生产监控 | 需接入 Prometheus |

## 学习路径建议

```
第一阶段：基础结构（ablation/）
  → 按顺序运行 5 个消融实验，理解每个要素的作用

第二阶段：进阶技术（reasoning/）
  → 从 Few-shot 开始，逐步学习 CoT → Self-Consistency → ToT → ReAct

第三阶段：输出控制（output/）
  → 掌握 JSON Schema、表格、代码生成、多模态的输出控制

第四阶段：工程化（engineering/）
  → 学习 A/B 测试、版本管理、安全防护、评估体系、分层架构
```

## 依赖说明

| 依赖 | 版本 | 用途 |
|------|------|------|
| `openai` | >=1.0.0 | OpenAI API 调用（所有模块） |
| `dspy-ai` | >=2.0.0 | 自动化 Prompt 优化（仅 `prompt_dspy.py`） |

## 相关文档

- [Prompt 工程完全指南：从原理到最佳实践](../Prompt工程完全指南：从原理到最佳实践.md)
- [OpenAI 官方 Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/en/prompt-library)
- [PromptingGuide.ai](https://www.promptingguide.ai/zh)

## 声明

本项目为作者在学习 Prompt 工程过程中的实践总结，仅供学习参考。如有表述错误或遗漏，欢迎提出指正。