#!/bin/bash

# StaryBlog 部署脚本
# 部署到 dongjingTest 服务器

SERVER="root@43.167.189.165"
DEPLOY_PATH="/var/www/staryblog"

echo "🚀 开始部署 StaryBlog 到 dongjingTest..."

# 1. 连接到服务器并创建目录(如果不存在)
echo "📁 在服务器上创建部署目录..."
ssh ${SERVER} "mkdir -p ${DEPLOY_PATH}/posts ${DEPLOY_PATH}/admin/logs"

# 2. 使用 rsync 同步文件
echo "📥 同步代码到服务器..."
rsync -avz --delete \
    --exclude '.git' \
    --exclude 'node_modules' \
    --exclude '.DS_Store' \
    --exclude 'deploy.sh' \
    --exclude 'admin/logs' \
    /Users/geshishuai/Documents/learn/aiWorkspace/github/StaryBlog/ \
    ${SERVER}:${DEPLOY_PATH}/

# 3. 安装管理后端依赖
echo "📦 安装管理后端依赖..."
ssh ${SERVER} "
    if [ ! -d ${DEPLOY_PATH}/admin/node_modules ]; then
        cd ${DEPLOY_PATH}/admin && npm install --production
    fi
"

# 4. 检查并安装 PM2
echo "🔧 检查 PM2..."
ssh ${SERVER} "
    if ! command -v pm2 &> /dev/null; then
        npm install -g pm2
    fi
"

# 5. 启动/重启管理后端
echo "🔄 启动/重启管理后端..."
ssh ${SERVER} "
    cd ${DEPLOY_PATH}
    pm2 restart admin/ecosystem.config.js 2>/dev/null || pm2 start admin/ecosystem.config.js
    pm2 save
"

# 6. 设置 Nginx 配置
echo "⚙️  配置 Nginx..."
ssh ${SERVER} "
    cat > /etc/nginx/sites-available/staryblog << 'EOF'
server {
    listen 80;
    server_name _;

    root ${DEPLOY_PATH};
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control \"public, immutable\";
    }

    # API 代理到管理后端
    location /api/ {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_cache_bypass \$http_upgrade;
    }

    # 管理后台静态文件
    location /admin/ {
        alias ${DEPLOY_PATH}/admin/public/;
        index admin.html;
        try_files \$uri \$uri/ =404;
    }

    # HTML 文件
    location / {
        try_files \$uri \$uri/ \$uri.html =404;
    }

    # 安全头
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
}
EOF

    # 启用站点
    ln -sf /etc/nginx/sites-available/staryblog /etc/nginx/sites-enabled/

    # 测试 Nginx 配置
    nginx -t

    # 重启 Nginx
    systemctl reload nginx
"

echo ""
echo "✅ 部署完成!"
echo "🌐 博客地址: http://43.167.189.165"
echo "🔧 管理后台: http://43.167.189.165/admin/admin.html"
echo ""
echo "📝 PM2 状态 (服务器上运行):"
echo "   ssh ${SERVER} 'pm2 status'"
echo ""
