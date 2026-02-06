const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs').promises;

const POSTS_DIR = path.join(__dirname, '../../posts');

// 辅助函数：确保文章目录存在
async function ensurePostDir(slug) {
    const dir = path.join(POSTS_DIR, slug);
    try {
        await fs.access(dir);
    } catch {
        await fs.mkdir(dir, { recursive: true });
    }
    return dir;
}

// 辅助函数：读取文章元数据
async function readMeta(slug) {
    const metaPath = path.join(POSTS_DIR, slug, 'meta.json');
    try {
        const content = await fs.readFile(metaPath, 'utf-8');
        return JSON.parse(content);
    } catch {
        return null;
    }
}

// 辅助函数：写入文章元数据
async function writeMeta(slug, meta) {
    const metaPath = path.join(POSTS_DIR, slug, 'meta.json');
    await fs.writeFile(metaPath, JSON.stringify(meta, null, 2), 'utf-8');
}

// 辅助函数：生成唯一 slug
async function generateSlug(baseSlug) {
    let slug = baseSlug.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    let counter = 1;
    let originalSlug = slug;

    while (true) {
        const dir = path.join(POSTS_DIR, slug);
        try {
            await fs.access(dir);
            slug = `${originalSlug}-${counter}`;
            counter++;
        } catch {
            break;
        }
    }

    return slug;
}

// GET /api/posts - 获取文章列表
router.get('/', async (req, res) => {
    try {
        const items = await fs.readdir(POSTS_DIR);
        const posts = [];

        for (const item of items) {
            if (item === '_legacy' || item.startsWith('.')) continue;

            const itemPath = path.join(POSTS_DIR, item);
            const stat = await fs.stat(itemPath);

            if (stat.isDirectory()) {
                const meta = await readMeta(item);
                if (meta) {
                    posts.push(meta);
                }
            }
        }

        // 按日期排序
        posts.sort((a, b) => new Date(b.date) - new Date(a.date));

        res.json(posts);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// GET /api/posts/:slug - 获取文章详情
router.get('/:slug', async (req, res) => {
    try {
        const { slug } = req.params;
        const meta = await readMeta(slug);

        if (!meta) {
            return res.status(404).json({ error: 'Post not found' });
        }

        // 读取内容
        const postDir = path.join(POSTS_DIR, slug);
        const result = { ...meta };

        // 读取 MD 内容
        if (meta.hasMd) {
            try {
                const contentPath = path.join(postDir, 'content.md');
                result.content = await fs.readFile(contentPath, 'utf-8');
            } catch {
                result.content = '';
            }
        }

        // 读取 HTML 内容
        if (meta.hasHtml) {
            try {
                const visualPath = path.join(postDir, 'visual.html');
                result.visualHtml = await fs.readFile(visualPath, 'utf-8');
            } catch {
                result.visualHtml = '';
            }
        }

        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// POST /api/posts - 创建新文章
router.post('/', async (req, res) => {
    try {
        const { title, date, category, categoryColor, description, content } = req.body;

        if (!title) {
            return res.status(400).json({ error: 'Title is required' });
        }

        // 生成 slug
        const baseSlug = title.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-');
        const slug = await generateSlug(baseSlug);

        // 创建文章目录
        const postDir = await ensurePostDir(slug);

        // 准备元数据
        const now = new Date().toISOString();
        const meta = {
            slug,
            title,
            date: date || new Date().toISOString().split('T')[0],
            category: category || '技术',
            categoryColor: categoryColor || 'blue',
            description: description || '',
            hasMd: !!content,
            hasHtml: false,
            created: now,
            updated: now
        };

        // 写入元数据
        await writeMeta(slug, meta);

        // 写入内容
        if (content) {
            const contentPath = path.join(postDir, 'content.md');
            await fs.writeFile(contentPath, content, 'utf-8');
        }

        res.status(201).json(meta);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// PUT /api/posts/:slug - 更新文章
router.put('/:slug', async (req, res) => {
    try {
        const { slug } = req.params;
        const meta = await readMeta(slug);

        if (!meta) {
            return res.status(404).json({ error: 'Post not found' });
        }

        // 更新元数据
        const updates = {};
        const allowedFields = ['title', 'date', 'category', 'categoryColor', 'description'];
        allowedFields.forEach(field => {
            if (req.body[field] !== undefined) {
                updates[field] = req.body[field];
            }
        });

        const newMeta = {
            ...meta,
            ...updates,
            updated: new Date().toISOString()
        };

        // 更新内容
        if (req.body.content !== undefined) {
            const postDir = path.join(POSTS_DIR, slug);
            const contentPath = path.join(postDir, 'content.md');

            if (req.body.content) {
                await fs.writeFile(contentPath, req.body.content, 'utf-8');
                newMeta.hasMd = true;
            } else {
                try {
                    await fs.unlink(contentPath);
                } catch {}
                newMeta.hasMd = false;
            }
        }

        await writeMeta(slug, newMeta);
        res.json(newMeta);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// DELETE /api/posts/:slug - 删除文章
router.delete('/:slug', async (req, res) => {
    try {
        const { slug } = req.params;
        const postDir = path.join(POSTS_DIR, slug);

        // 检查是否存在
        try {
            await fs.access(postDir);
        } catch {
            return res.status(404).json({ error: 'Post not found' });
        }

        // 递归删除目录
        await fs.rm(postDir, { recursive: true, force: true });

        res.json({ success: true, message: 'Post deleted' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// POST /api/posts/:slug/html - 上传 visual.html
router.post('/:slug/html', async (req, res) => {
    try {
        const { slug } = req.params;
        const { html } = req.body;

        if (!html) {
            return res.status(400).json({ error: 'HTML content is required' });
        }

        const meta = await readMeta(slug);
        if (!meta) {
            return res.status(404).json({ error: 'Post not found' });
        }

        // 写入 visual.html
        const postDir = path.join(POSTS_DIR, slug);
        const visualPath = path.join(postDir, 'visual.html');
        await fs.writeFile(visualPath, html, 'utf-8');

        // 更新元数据
        meta.hasHtml = true;
        meta.updated = new Date().toISOString();
        await writeMeta(slug, meta);

        res.json({ success: true, meta });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
