# Issue 处理流程快速参考

## 🎯 一图看懂

```
用户创建 issue + 打 bot 标签
         ↓
    Agent 分析
         ↓
    ┌────┴────┐
    │         │
需要信息    可以处理    太复杂
    │         │         │
needs-info  in-progress cannot-fix
    │
用户回复评论
    │
❌ Agent 不处理（标签还在）
    │
✅ 用户移除 needs-info 标签
    │
Agent 重新处理
```

## 📌 核心规则（3 秒记住）

**用户回复后需要手动移除标签！**

- ✅ 有 `bot` 标签 + 无状态标签 = Agent 处理
- ❌ 有状态标签（needs-info/in-progress/cannot-fix/analyzing）= Agent 跳过

## 🔄 快速操作步骤

### 当收到 AI 询问时

1. **查看评论**
   ```
   👋 Hi! I need more info:
   1. Question 1
   2. Question 2

   📌 After you reply: Please remove the `needs-info` label
   ```

2. **回复补充信息**
   - 写评论回答所有问题

3. **移除标签触发重新处理**
   - 右侧 Labels
   - 点击 `needs-info` 旁的 ❌
   - 完成！

4. **等待 AI 重新分析**
   - 通常 3-5 分钟
   - Agent 会读取你的新评论

## 💡 为什么这样设计？

**场景对比：**

❌ **自动触发（不好）：**
```
AI: 请问版本？
用户: Python 3.8
AI: [立即处理] ← 太快了
用户: 还有... ← AI 已经走了
```

✅ **手动触发（好）：**
```
AI: 请问版本？
用户: Python 3.8
用户: Ubuntu 22.04
用户: 还有这些依赖...
用户: [移除标签] ← 我说完了
AI: [开始处理] ← 看到完整信息
```

## 🎮 GitHub UI 位置

```
┌─────────────────────────────┐
│ Issue #123                  │
│                             │
│ 描述...                      │
│                             │
│ 💬 Comment                  │
│ 📌 Please remove the        │
│    needs-info label         │
└─────────────────────────────┘
                         ┌────────────┐
                         │ Labels     │
                         │ • bot      │
                         │ • needs-   │
                         │   info  ❌ │ ← 点这里
                         └────────────┘
```

## ❓ FAQ 1 分钟版

**Q: 我回复了为啥不处理？**
A: 标签还在。去右边移除 `needs-info` 标签。

**Q: 等多久？**
A: 3-5 分钟（cron 任务间隔）。

**Q: 标签在哪？**
A: Issue 页面右侧 "Labels" 区域。

**Q: 能自动吗？**
A: 故意不自动，让你控制节奏。

## 📖 详细文档

完整说明请看：[ISSUE_STATE_MANAGEMENT.md](ISSUE_STATE_MANAGEMENT.md)
