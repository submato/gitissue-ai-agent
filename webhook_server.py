#!/usr/bin/env python3
"""
GitHub Webhook Server
接收 GitHub webhook 事件并自动处理 issue
"""

import os
import sys
import hmac
import hashlib
import subprocess
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', '')
REPO_OWNER = os.getenv('REPO_OWNER', 'submato')
REPO_NAME = os.getenv('REPO_NAME', 'gitissue-ai-agent')


def verify_signature(payload_body, signature_header):
    """验证 GitHub webhook 签名"""
    if not WEBHOOK_SECRET:
        logger.warning("No webhook secret configured, skipping signature verification")
        return True

    if not signature_header:
        return False

    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


@app.route('/webhook', methods=['POST'])
def webhook():
    """处理 GitHub webhook 事件"""

    # 验证签名
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        logger.error("Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 403

    # 获取事件类型
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    logger.info(f"Received {event} event")

    # 处理 issue 相关事件
    if event in ['issues', 'issue_comment']:
        issue = payload.get('issue', {})
        issue_number = issue.get('number')
        labels = [label['name'] for label in issue.get('labels', [])]

        # 只处理带 'bot' 标签的 issue
        if 'bot' not in labels:
            logger.info(f"Issue #{issue_number} doesn't have 'bot' label, skipping")
            return jsonify({'message': 'No bot label, skipped'}), 200

        logger.info(f"Processing issue #{issue_number} with labels: {labels}")

        # 异步运行处理脚本
        try:
            env = os.environ.copy()
            env['USE_LOCAL_PROXY'] = '1'
            env['ISSUE_NUMBER'] = str(issue_number)
            env['REPO_OWNER'] = REPO_OWNER
            env['REPO_NAME'] = REPO_NAME

            # 后台运行处理脚本
            subprocess.Popen(
                [sys.executable, 'process_github_issue.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            logger.info(f"Started processing issue #{issue_number}")
            return jsonify({'message': f'Processing issue #{issue_number}'}), 200

        except Exception as e:
            logger.error(f"Error starting process: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Event received'}), 200


@app.route('/health', methods=['GET'])
def health():
    """健康检查端点"""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    # 创建 logs 目录
    os.makedirs('logs', exist_ok=True)

    # 获取端口
    port = int(os.getenv('WEBHOOK_PORT', 8080))

    logger.info(f"Starting webhook server on port {port}")
    logger.info(f"Webhook URL: http://your-server-ip:{port}/webhook")

    # 运行服务器
    app.run(host='0.0.0.0', port=port, debug=False)
