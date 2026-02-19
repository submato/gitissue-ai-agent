# 🚀 快速启动清单

## ✅ 你现在可以做的

### 选项 1：立即测试 Webhook 服务器

```bash
# 1. 安装 Flask（如果还没装）
pip install flask

# 2. 启动 webhook 服务器
cd /home/mhyuser/gitissue-ai-agent
./start_webhook.sh
```

服务器启动后会显示：
```
Webhook URL: http://192.168.x.x:8080/webhook
```

### 选项 2：配置 GitHub Webhook（实现自动化）

1. 打开浏览器访问：
   ```
   https://github.com/submato/gitissue-ai-agent/settings/hooks
   ```

2. 点击 **"Add webhook"**

3. 填写：
   - **Payload URL**: `http://你的服务器IP:8080/webhook`
   - **Content type**: `application/json`
   - **Events**: 勾选 "Issues" 和 "Issue comments"
   - **Active**: ✅

4. 点击 **"Add webhook"**

### 选项 3：配置开机自启（生产环境）

```bash
# 1. 编辑服务文件，填入你的 GITHUB_TOKEN
nano systemd/gitissue-webhook.service

# 2. 安装服务
sudo cp systemd/gitissue-webhook.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start gitissue-webhook
sudo systemctl enable gitissue-webhook

# 3. 查看状态
sudo systemctl status gitissue-webhook
```

## 🎯 测试自动化

1. 在 GitHub 创建新 issue
2. 添加 `bot` 标签
3. 几秒内看到 AI 自动回复！

## 📊 查看日志

```bash
# Webhook 日志
tail -f logs/webhook.log

# Issue 处理日志
tail -f logs/github_issue_*.log

# Systemd 日志（如果用了 systemd）
sudo journalctl -u gitissue-webhook -f
```

## 📝 所需环境变量

确保已设置：
```bash
export USE_LOCAL_PROXY=1                # ✅ 必需
export GITHUB_TOKEN="ghp_xxx"           # ✅ 必需（你的 GitHub token）
export REPO_OWNER="submato"             # ✅ 必需
export REPO_NAME="gitissue-ai-agent"    # ✅ 必需
export ANTHROPIC_API_KEY="any_value"    # ✅ 必需（使用本地代理时任意值）
export WEBHOOK_PORT=8080                # ⚠️ 可选（默认 8080）
export GITHUB_WEBHOOK_SECRET=""         # ⚠️ 可选（推荐设置）
```

## 🔧 故障排查

### 端口被占用
```bash
# 查看谁在用 8080
sudo netstat -tulpn | grep 8080

# 换个端口
export WEBHOOK_PORT=8888
./start_webhook.sh
```

### 本地代理连不上
```bash
# 测试代理
curl http://localhost:8082

# 如果不通，先启动你的本地 AI 代理服务
```

### GitHub Webhook 报错
1. 在 GitHub webhook 页面查看 "Recent Deliveries"
2. 点击具体请求查看详细错误
3. 检查服务器防火墙是否允许 GitHub IP 访问

## 📚 更多文档

- [完整服务器设置指南](docs/SERVER_SETUP.md)
- [功能完成状态](FEATURE_COMPLETION_STATUS.md)
- [项目 README](README.md)

## 🎉 完成！

所有功能已就绪，开始使用吧！ 🚀
