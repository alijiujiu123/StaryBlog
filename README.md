# Stary's Blog

我的个人技术博客,分享技术洞察、架构设计与实践经验。

## 📝 内容

- **技术架构**: 深入剖析分布式系统、AI 架构等前沿技术
- **工程实践**: 分享项目开发中的实践经验与解决方案
- **学习笔记**: 记录技术学习历程与思考

## 🚀 技术栈

- HTML5
- Tailwind CSS
- JavaScript

## 📂 项目结构

```
StaryBlog/
├── index.html          # 首页
├── posts/              # 博客文章
│   └── openclaw-architecture.html
└── README.md           # 项目说明
```

## 🌐 在线访问

- **生产环境**: http://43.167.189.165

## 🛠️ 本地运行

1. 克隆仓库:
```bash
git clone https://github.com/YOUR_USERNAME/StaryBlog.git
cd StaryBlog
```

2. 直接打开 `index.html` 文件,或使用本地服务器:
```bash
# 使用 Python
python -m http.server 8000

# 或使用 Node.js
npx serve
```

3. 在浏览器中访问 `http://localhost:8000`

## 🚀 部署

部署到 dongjingTest 服务器:

```bash
# 方式一:使用部署脚本
./deploy.sh

# 方式二:手动部署
ssh root@43.167.189.165
cd /var/www/staryblog
git pull origin main
```

## 📄 许可证

MIT License

## 👤 作者

[Your Name](https://github.com/)

---

Built with ❤️ using Tailwind CSS
