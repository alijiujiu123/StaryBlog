#!/bin/bash
# 自动更新首页文章列表并部署

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 调用 Python 脚本
python3 "${SCRIPT_DIR}/update-posts.py"
