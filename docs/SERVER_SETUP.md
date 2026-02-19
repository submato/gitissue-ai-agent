# 服务器自动化部署指南

本指南帮助你在服务器上部署 GitIssue AI Agent，实现 24/7 自动处理 GitHub issues。

## 🎯 部署方式选择

### 方式 1：Webhook 服务器（推荐）✨
- ✅ **实时响应** - Issue 创建后几秒内自动处理
- ✅ **资源高效** - 只在有事件时运行
- ✅ **适合生产环境**

### 方式 2：定时任务（Cron）
- ✅ **简单易用** - 无需配置 webhook
- ⚠️ **延迟响应** - 最快每分钟检查一次
- ✅ **适合测试环境**

---

## 🚀 方式 1：Webhook 服务器部署（推荐）

### 步骤 1：安装依赖

```bash
cd /home/mhyuser/gitissue-ai-agent
pip install -r requirements.txt
```

### 步骤 2：配置环境变量

编辑启动脚本或 systemd 服务文件，设置以下环境变量：

```bash
# 必需
export USE_LOCAL_PROXY=1                    # 使用本地 AI 代理
export GITHUB_TOKEN="your_github_token"     # GitHub Personal Access Token
export REPO_OWNER="submato"                 # 仓库所有者
export REPO_NAME="gitissue-ai-agent"        # 仓库名称

# 可选
export WEBHOOK_PORT=8080                    # Webhook 监听端口（默认 8080）
export GITHUB_WEBHOOK_SECRET="your_secret" # Webhook 签名密钥（推荐设置）
export ANTHROPIC_API_KEY="any_value"       # 使用本地代理时任意值即可
```

### 步骤 3：启动 Webhook 服务器

#### 方法 A：直接运行（测试用）

```bash
./start_webhook.sh
```

服务器启动后会显示 Webhook URL，例如：
```
Webhook URL: http://192.168.1.100:8080/webhook
```

#### 方法 B：使用 Systemd（生产环境推荐）

```bash
# 1. 编辑服务文件，填入你的 GITHUB_TOKEN
sudo nano systemd/gitissue-webhook.service

# 2. 复制服务文件到 systemd 目录
sudo cp systemd/gitissue-webhook.service /etc/systemd/system/

# 3. 重载 systemd 配置
sudo systemctl daemon-reload

# 4. 启动服务
sudo systemctl start gitissue-webhook

# 5. 设置开机自启
sudo systemctl enable gitissue-webhook

# 6. 查看状态
sudo systemctl status gitissue-webhook

# 7. 查看日志
sudo journalctl -u gitissue-webhook -f
```

### 步骤 4：配置 GitHub Webhook

1. **打开 GitHub 仓库设置**：
   ```
   https://github.com/submato/gitissue-ai-agent/settings/hooks
   ```

2. **点击 "Add webhook"**

3. **填写配置**：
   - **Payload URL**: `http://你的服务器IP:8080/webhook`
     - 例如：`http://192.168.1.100:8080/webhook`
     - 如果有域名：`http://yourdomain.com:8080/webhook`

   - **Content type**: `application/json`

   - **Secret**（可选但推荐）：
     - 填写一个随机字符串，例如：`my_webhook_secret_2024`
     - 必须与服务器环境变量 `GITHUB_WEBHOOK_SECRET` 一致

   - **Which events would you like to trigger this webhook?**
     - 选择 "Let me select individual events"
     - 勾选：
       - ✅ Issues
       - ✅ Issue comments

   - **Active**: ✅ 勾选

4. **点击 "Add webhook"**

### 步骤 5：测试

1. 在仓库创建一个新 issue
2. 添加 `bot` 标签
3. 几秒内应该看到 AI 自动回复

查看日志：
```bash
# 实时日志
tail -f logs/webhook.log

# 或者通过 systemd
sudo journalctl -u gitissue-webhook -f
```

---

## 📅 方式 2：Cron 定时任务

### 步骤 1：创建处理脚本

创建文件 `/home/mhyuser/gitissue-ai-agent/cron_process.sh`：

```bash
#!/bin/bash
cd /home/mhyuser/gitissue-ai-agent

export USE_LOCAL_PROXY=1
export GITHUB_TOKEN="your_github_token"
export REPO_OWNER="submato"
export REPO_NAME="gitissue-ai-agent"
export ANTHROPIC_API_KEY="any_value"

# 获取所有带 'bot' 标签且 open 状态的 issues
# 这里需要写一个简单的脚本来遍历 issues
python3 process_github_issue.py >> logs/cron.log 2>&1
```

### 步骤 2：设置 Cron

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每 5 分钟检查一次）
*/5 * * * * /home/mhyuser/gitissue-ai-agent/cron_process.sh

# 或者每分钟检查一次（更实时）
* * * * * /home/mhyuser/gitissue-ai-agent/cron_process.sh
```

---

## 🔒 安全建议

1. **使用 Webhook Secret**
   - 在 GitHub webhook 和服务器都设置相同的 secret
   - 防止未授权的请求

2. **使用防火墙**
   ```bash
   # 只允许 GitHub IP 访问 webhook 端口
   sudo ufw allow from 140.82.112.0/20 to any port 8080
   sudo ufw allow from 143.55.64.0/20 to any port 8080
   ```

3. **使用反向代理（生产环境推荐）**
   ```nginx
   # Nginx 配置
   location /webhook {
       proxy_pass http://localhost:8080/webhook;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

4. **使用 HTTPS**
   - GitHub webhook 支持 HTTPS
   - 使用 Let's Encrypt 免费证书

---

## 📊 监控和维护

### 查看运行状态

```bash
# Webhook 服务状态
sudo systemctl status gitissue-webhook

# 查看日志
tail -f logs/webhook.log
tail -f logs/webhook.error.log
```

### 重启服务

```bash
sudo systemctl restart gitissue-webhook
```

### 更新代码

```bash
cd /home/mhyuser/gitissue-ai-agent
git pull origin main
pip install -r requirements.txt
sudo systemctl restart gitissue-webhook
```

---

## 🐛 故障排查

### Webhook 服务无法启动

1. 检查端口是否被占用：
   ```bash
   sudo netstat -tulpn | grep 8080
   ```

2. 查看错误日志：
   ```bash
   sudo journalctl -u gitissue-webhook -n 50
   ```

3. 检查权限：
   ```bash
   ls -la /home/mhyuser/gitissue-ai-agent/
   ```

### GitHub Webhook 显示错误

1. 在 GitHub webhook 设置页面查看 "Recent Deliveries"
2. 点击具体请求查看响应
3. 检查服务器防火墙是否允许 GitHub IP

### Issue 没有被处理

1. 确认 issue 有 `bot` 标签
2. 查看 webhook 日志：`tail -f logs/webhook.log`
3. 查看处理日志：`tail -f logs/github_issue_*.log`
4. 检查本地 AI 代理是否运行：`curl http://localhost:8082`

---

## 📝 常见问题

**Q: 可以同时运行多个仓库的 webhook 吗？**

A: 可以。修改 webhook_server.py，从 payload 动态获取 repo_owner 和 repo_name。

**Q: 如何更改监听端口？**

A: 修改环境变量 `WEBHOOK_PORT`，然后重启服务。

**Q: 本地代理挂了怎么办？**

A: Webhook 服务会记录错误，但不会崩溃。修复代理后，可以手动重新处理 issue。

**Q: 可以处理私有仓库吗？**

A: 可以。确保 GITHUB_TOKEN 有访问私有仓库的权限。

---

## 🎉 完成！

现在你的服务器已经配置为 24/7 自动处理 GitHub issues！

创建一个带 `bot` 标签的 issue 来测试吧！🚀
