# StaryBlog 双模式博客系统

支持 **Markdown 文章** 和 **可视化 HTML 页面** 双模式的静态博客。

## 目录结构

```
StaryBlog/
├── posts/
│   ├── <slug>/
│   │   ├── meta.json      # 元数据（必需）
│   │   ├── content.md     # Markdown 正文（可选）
│   │   └── visual.html    # 可视化 HTML（可选）
│   └── _legacy/           # 旧文件备份
│
├── admin/                  # 管理后端
│   ├── server.js          # Express 服务器
│   ├── routes/
│   │   └── posts.js       # 文章 CRUD API
│   ├── middleware/
│   │   └── auth.js        # JWT 认证
│   ├── public/
│   │   └── admin.html     # 管理界面
│   └── ecosystem.config.js # PM2 配置
│
├── scripts/
│   ├── migrate.py         # 迁移脚本
│   └── update-posts.py    # 更新首页
│
├── post.html              # 文章页面（支持双模式）
├── index.html             # 首页
└── deploy.sh              # 部署脚本
```

## meta.json 格式

```json
{
  "slug": "openclaw-architecture",
  "title": "OpenClaw 技术架构深度研究",
  "date": "2026-02-05",
  "category": "AI 架构",
  "categoryColor": "blue",
  "description": "文章描述...",
  "hasMd": true,
  "hasHtml": false,
  "created": "2026-02-05T10:00:00Z",
  "updated": "2026-02-05T10:00:00Z"
}
```

## 使用方法

### 创建新文章

1. **手动创建**
   ```bash
   mkdir posts/my-post
   cat > posts/my-post/meta.json << 'EOF'
   {
     "slug": "my-post",
     "title": "我的文章",
     "date": "2026-02-06",
     "category": "技术",
     "categoryColor": "blue",
     "description": "这是一篇技术文章",
     "hasMd": true,
     "hasHtml": false
   }
   EOF

   # 创建 markdown 内容
   echo "# 我的文章" > posts/my-post/content.md
   ```

2. **使用管理后台**
   ```bash
   # 启动管理后端
   cd admin
   npm install
   npm start

   # 访问 http://localhost:3001/admin/admin.html
   ```

### 更新首页

```bash
python3 update-posts.py
```

### 部署

```bash
./deploy.sh
```

## URL 格式

- **新格式**: `/post.html?slug=openclaw-architecture`
- **旧格式**: `/post.html?post=openclaw-architecture.md`（向后兼容）

## 模式切换

当文章同时拥有 `content.md` 和 `visual.html` 时，页面顶部会显示切换按钮：
- 📝 文章 - Markdown 渲染模式
- 🧠 可视化 - HTML iframe 模式

## 本地运行

```bash
# 使用 Python
python -m http.server 8000

# 或使用 Node.js
npx serve
```

## 在线访问

- **生产环境**: http://43.167.189.165
- **管理后台**: http://43.167.189.165/admin/admin.html

## 技术栈

- **前端**: HTML5, Tailwind CSS, JavaScript
- **管理后端**: Node.js, Express
- **部署**: Nginx, PM2
- **渲染**: Marked.js, Highlight.js
