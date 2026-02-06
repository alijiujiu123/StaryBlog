const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const postsRouter = require('./routes/posts');

const app = express();
const PORT = process.env.PORT || 3001;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 静态文件服务（管理界面）
app.use('/admin', express.static(path.join(__dirname, 'public')));

// API 路由
app.use('/api/posts', postsRouter);

// 健康检查
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 错误处理
app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(500).json({ error: err.message || 'Internal server error' });
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`StaryBlog Admin Server running on port ${PORT}`);
    console.log(`Admin panel: http://localhost:${PORT}/admin/admin.html`);
    console.log(`API endpoint: http://localhost:${PORT}/api`);
});

module.exports = app;
