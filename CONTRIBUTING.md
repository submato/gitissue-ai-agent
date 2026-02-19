# 贡献指南

感谢你考虑为 GitLab AI Agent 做出贡献！

## 如何贡献

### 报告 Bug

在 [GitHub Issues](https://github.com/YOUR_USERNAME/gitissue-ai-agent/issues) 中创建 issue，包括：

- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息（OS、Python 版本等）

### 提出新功能

1. 先在 Issues 中讨论你的想法
2. 等待维护者反馈
3. 开始实现

### 提交代码

1. **Fork 仓库**

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **编写代码**
   - 遵循现有代码风格
   - 添加必要的注释
   - 更新文档

4. **测试**
   ```bash
   python -m pytest tests/
   ```

5. **提交**
   ```bash
   git commit -m "Add: your feature description"
   ```

6. **推送**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**

## 代码规范

- 遵循 PEP 8
- 函数和类添加 docstring
- 变量名使用有意义的英文
- 注释使用中文或英文

## 提交信息规范

```
<type>: <subject>

<body>
```

**Type:**
- `Add`: 新功能
- `Fix`: Bug 修复
- `Update`: 更新现有功能
- `Refactor`: 重构
- `Docs`: 文档
- `Test`: 测试
- `Chore`: 构建/工具

**示例:**
```
Add: OpenAI provider support

- Implement OpenAIProvider class
- Add configuration in config.yaml
- Update README
```

## 添加新的 AI Provider

1. 在 `providers/` 目录创建新文件
2. 继承 `AIProvider` 基类
3. 实现 `analyze_issue` 和 `generate_fix_instructions` 方法
4. 在 `main.py` 中注册
5. 更新文档

示例：
```python
from providers.base import AIProvider

class MyProvider(AIProvider):
    def __init__(self, api_key: str, **kwargs):
        pass

    def analyze_issue(self, issue: Dict, project_info: Dict) -> Dict:
        # 实现分析逻辑
        pass

    def generate_fix_instructions(self, issue: Dict, project_info: Dict, plan: str) -> str:
        # 实现指令生成
        pass
```

## 开发环境设置

```bash
# 克隆
git clone https://github.com/YOUR_USERNAME/gitissue-ai-agent.git
cd gitissue-ai-agent

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 运行测试
pytest
```

## 问题？

有任何问题欢迎在 Issues 中提问！

---

再次感谢你的贡献！ ❤️
