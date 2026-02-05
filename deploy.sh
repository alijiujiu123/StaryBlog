#!/bin/bash

# StaryBlog 部署脚本
# 部署到 dongjingTest 服务器

SERVER="root@43.167.189.165"
DEPLOY_PATH="/var/www/staryblog"
REPO_URL="https://github.com/alijiujiu123/StaryBlog.git"

echo "🚀 开始部署 StaryBlog 到 dongjingTest..."

# 1. 连接到服务器并创建目录(如果不存在)
echo "📁 在服务器上创建部署目录..."
ssh ${SERVER} "mkdir -p ${DEPLOY_PATH}"

# 2. 在服务器上克隆或更新仓库
echo "📥 同步代码到服务器..."
ssh ${SERVER} "
    if [ -d ${DEPLOY_PATH}/.git ]; then
        cd ${DEPLOY_PATH}
        git pull origin main
    else
        rm -rf ${DEPLOY_PATH}
        git clone ${REPO_URL} ${DEPLOY_PATH}
    fi
"

# 3. 设置 Nginx 配置
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
    location ~* \\.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control \"public, immutable\";
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

echo "✅ 部署完成!"
echo "🌐 访问地址: http://43.167.189.165"
