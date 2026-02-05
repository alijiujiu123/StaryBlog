#!/bin/bash

# 快速更新博客脚本
# 用途:快速提交更改并部署到服务器

echo "📝 StaryBlog 快速更新工具"
echo "================================"

# 1. 添加所有更改
echo "📦 添加更改..."
git add .

# 2. 提交
echo "💬 输入提交信息 (留空使用默认):"
read -r COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update blog content"
fi

git commit -m "$COMMIT_MSG"

# 3. 推送到 GitHub
echo "📤 推送到 GitHub..."
git push origin main

# 4. 部署到服务器
echo "🚀 部署到服务器..."
ssh root@43.167.189.165 "
    cd /var/www/staryblog
    git pull origin main
    echo '✅ 服务器更新完成'
"

echo "✅ 更新完成!"
echo "🌐 访问: http://43.167.189.165"
