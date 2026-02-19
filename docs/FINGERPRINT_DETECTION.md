# 指纹检测（Fingerprint Detection）详解

## 🎯 什么是指纹检测？

**指纹检测**是一种用来判断 issue 是否有变化的机制，避免 Agent 重复处理同一个 issue。

### 核心概念

**指纹（Fingerprint）** = 一个唯一标识 issue 当前状态的字符串

就像人的指纹一样，每个 issue 在特定状态下都有一个唯一的"指纹"。

---

## 🔍 工作原理

### 1. 生成指纹

每次 Agent 处理 issue 时，会根据 issue 的关键信息生成一个指纹：

```python
# 代码示例
fingerprint = f"{issue['title']}_{issue['body']}_{len(comments)}_{','.join(sorted(current_labels))}"
```

**包含的信息：**
- ✅ Issue 标题
- ✅ Issue 描述
- ✅ 评论数量
- ✅ 标签列表

**示例：**
```python
# Issue #123 的指纹
"增加docker部署_详细描述内容..._5_bot,needs-info"
```

### 2. 保存指纹

处理完 issue 后，Agent 会保存这个指纹：

```json
{
  "submato/gitissue-ai-agent#123": "增加docker部署_详细描述内容..._5_bot,needs-info"
}
```

文件位置：`logs/processed_issues.json`

### 3. 检查指纹

下次扫描时，Agent 会：
1. 重新生成当前指纹
2. 对比保存的旧指纹
3. 如果**完全相同** → 跳过（没有变化）
4. 如果**不同** → 处理（有新变化）

---

## 📊 指纹变化的场景

### 场景 1：用户添加了新评论

```python
# 第一次处理
fingerprint_old = "标题_描述_3_bot"  # 3 条评论

# 用户回复后
fingerprint_new = "标题_描述_4_bot"  # 4 条评论

# 对比：3 != 4 → 有变化 → 重新处理 ✅
```

### 场景 2：标签发生变化

```python
# AI 添加 needs-info 后
fingerprint_old = "标题_描述_4_bot,needs-info"

# 用户移除 needs-info 后
fingerprint_new = "标题_描述_4_bot"

# 对比：标签不同 → 有变化 → 重新处理 ✅
```

### 场景 3：没有任何变化

```python
# 第一次处理
fingerprint_old = "标题_描述_4_bot,needs-info"

# 再次扫描（用户还没回复）
fingerprint_new = "标题_描述_4_bot,needs-info"

# 对比：完全相同 → 跳过 ❌
```

---

## 🎮 实际运行示例

### 完整流程

**1. 用户创建 issue #123**
```
标题：增加 docker 部署
描述：需要添加 Dockerfile
标签：[bot]
评论数：0
```

**2. 第一次扫描（10:00）**
```python
# 生成指纹
fingerprint = "增加docker部署_需要添加Dockerfile_0_bot"

# 检查：没有保存的指纹 → 第一次处理
# 处理完成，保存指纹
{
  "submato/gitissue-ai-agent#123": "增加docker部署_需要添加Dockerfile_0_bot"
}
```

**3. AI 回复并添加标签**
```
评论数：1（bot 的评论）
标签：[bot, needs-info]
```

**4. 第二次扫描（10:03）**
```python
# 生成新指纹
fingerprint = "增加docker部署_需要添加Dockerfile_1_bot,needs-info"

# 检查标签：有 needs-info → 跳过 ❌
# 不会对比指纹，直接跳过
```

**5. 用户回复（10:05）**
```
评论数：2（bot 的评论 + 用户的评论）
标签：[bot, needs-info]（标签还在）
```

**6. 第三次扫描（10:06）**
```python
# 生成新指纹
fingerprint = "增加docker部署_需要添加Dockerfile_2_bot,needs-info"

# 检查标签：有 needs-info → 跳过 ❌
# 即使评论数变了，也不处理（标签优先）
```

**7. 用户移除 needs-info 标签（10:08）**
```
评论数：2
标签：[bot]（已移除 needs-info）
```

**8. 第四次扫描（10:09）**
```python
# 生成新指纹
fingerprint = "增加docker部署_需要添加Dockerfile_2_bot"

# 检查标签：没有状态标签 → 继续
# 对比指纹：
#   旧: "增加docker部署_需要添加Dockerfile_0_bot"
#   新: "增加docker部署_需要添加Dockerfile_2_bot"
# 不同 → 重新处理 ✅

# 处理完成，更新指纹
{
  "submato/gitissue-ai-agent#123": "增加docker部署_需要添加Dockerfile_2_bot"
}
```

---

## 💡 为什么需要指纹？

### 问题：没有指纹会怎样？

❌ **没有指纹机制：**
```
10:00 - AI 处理 issue #123 → 回复评论
10:03 - AI 再次扫描 → 又处理 issue #123 → 又回复评论
10:06 - AI 再次扫描 → 又处理 issue #123 → 又回复评论
...
无限循环！每 3 分钟就重复一次！
```

✅ **有指纹机制：**
```
10:00 - AI 处理 issue #123 → 保存指纹
10:03 - AI 扫描 → 指纹相同 → 跳过
10:06 - AI 扫描 → 指纹相同 → 跳过
...
直到 issue 有新变化（新评论、标签变化）
```

---

## 🔧 指纹 vs 标签过滤

两者配合使用：

| 机制 | 作用 | 优先级 |
|------|------|--------|
| **标签过滤** | 基于状态快速跳过 | 🥇 优先 |
| **指纹检测** | 检测是否有新变化 | 🥈 其次 |

**处理顺序：**
```python
if has_status_label:
    return  # 有状态标签 → 立即跳过

if fingerprint_same:
    return  # 指纹相同 → 没变化 → 跳过

# 否则处理
process_issue()
```

---

## 📝 指纹存储位置

### GitHub
```
logs/processed_issues.json           # 单仓库
logs/github_multi_repo_state.json    # 多仓库
```

### GitLab
```
state.json  # 配置文件中指定
```

### 文件格式
```json
{
  "submato/gitissue-ai-agent#123": "标题_描述_5_bot",
  "submato/gitissue-ai-agent#124": "标题_描述_2_bot,needs-info",
  "user/other-repo#456": "标题_描述_10_bot,in-progress"
}
```

---

## 🎯 实际效果

### 场景：用户多次回复

**用户操作：**
```
10:00 - 创建 issue
10:01 - AI 询问信息，添加 needs-info
10:05 - 用户回复："Python 3.8"
10:07 - 用户再回复："Ubuntu 22.04"
10:09 - 用户再回复："还有这些依赖..."
10:11 - 用户移除 needs-info 标签
```

**Agent 行为（没有指纹）：**
```
10:00 - 处理 ✅
10:03 - 处理 ✅
10:06 - 处理 ✅ → 但用户还在回复！
10:09 - 处理 ✅ → 又处理了一次！
10:12 - 处理 ✅ → 又又处理！
```

**Agent 行为（有指纹 + 标签）：**
```
10:00 - 处理 ✅ → 保存指纹
10:03 - 跳过（有 needs-info 标签）
10:06 - 跳过（有 needs-info 标签）
10:09 - 跳过（有 needs-info 标签）
10:12 - 处理 ✅ → 用户移除标签了，指纹不同
```

---

## 🔍 查看指纹记录

```bash
# 查看当前保存的指纹
cat logs/processed_issues.json

# 格式化输出
python3 -m json.tool logs/processed_issues.json

# 清空指纹（让 Agent 重新处理所有 issue）
rm logs/processed_issues.json
```

---

## ❓ 常见问题

**Q: 指纹文件丢失了怎么办？**

A: Agent 会重新处理所有 open issues（但会被标签过滤阻止重复处理）。

**Q: 可以手动修改指纹文件吗？**

A: 可以，但不推荐。通常通过移除标签来触发重新处理更安全。

**Q: 指纹包含评论内容吗？**

A: 不包含。只包含评论**数量**，不包含具体内容。这样更高效。

**Q: 如果我修改了 issue 标题会怎样？**

A: 指纹会变化，Agent 会重新处理。

**Q: 指纹文件会很大吗？**

A: 不会。每个 issue 只有一行，即使 1000 个 issues 也很小。

---

## 🚀 总结

**指纹检测 = 判断 issue 是否有变化的机制**

**核心逻辑：**
```
如果（issue 的指纹与上次保存的相同）：
    跳过（没有新变化）
否则：
    处理（有新变化）
    保存新指纹
```

**配合标签过滤：**
- 标签过滤：基于**状态**快速跳过
- 指纹检测：基于**内容变化**避免重复

两者结合，完美避免重复处理！🎉
