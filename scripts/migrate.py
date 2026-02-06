#!/usr/bin/env python3
"""
StaryBlog 文章迁移脚本
将现有的 posts/*.md 迁移到新的 posts/<slug>/ 结构

新结构:
posts/
├── <slug>/
│   ├── meta.json      # 元数据（必需）
│   ├── content.md     # Markdown 正文（可选）
│   └── visual.html    # 可视化 HTML（可选）
└── _legacy/           # 旧文件备份
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path

# 颜色代码
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
POSTS_DIR = os.path.join(PROJECT_DIR, "posts")
LEGACY_DIR = os.path.join(POSTS_DIR, "_legacy")

# 从 markdown 文件提取元数据
def extract_metadata(filepath, filename):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取标题（第一个 # 开头的行）
    title_match = re.search(r'^#\s+([^\n]+)', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filename.replace('.md', '').replace('-', ' ').title()

    # 提取描述（第一段非空、非#、非表格的内容）
    lines = content.split('\n')
    description = ""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '|' not in stripped and not re.match(r'^\d', stripped):
            # 清理 markdown 格式
            description = re.sub(r'\*\*([^*]+)\*\*', r'\1', stripped)  # 移除粗体
            description = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', description)  # 移除链接
            description = description[:200]
            break

    # 从文件名提取日期
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    date = date_match.group(1) if date_match else None

    # 如果文件名没有日期，使用文件修改时间
    if not date:
        mtime = os.path.getmtime(filepath)
        date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

    # 生成 slug
    slug = generate_slug(filename, title, date)

    # 自动分类
    category, color = auto_category(filename, title)

    # 提取纯文件名（不含日期）
    md_filename = filename
    if date_match:
        md_filename = filename[len(date)+1:] if len(filename) > len(date)+1 else filename

    return {
        "slug": slug,
        "title": title,
        "date": date,
        "category": category,
        "categoryColor": color,
        "description": description,
        "hasMd": True,
        "hasHtml": False,
        "mdFilename": md_filename,
        "created": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "updated": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%dT%H:%M:%SZ')
    }

def generate_slug(filename, title, date):
    """从文件名或标题生成 slug"""
    # 首先尝试从文件名提取（不含日期）
    base_name = filename.replace('.md', '')
    date_match = re.match(r'(\d{4}-\d{2}-\d{2}-)?(.+)', base_name)
    if date_match:
        slug = date_match.group(2) if date_match.group(2) else base_name
    else:
        slug = base_name

    # 转换为 kebab-case
    slug = slug.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # 移除特殊字符
    slug = re.sub(r'[\s_]+', '-', slug)   # 空格和下划线转连字符
    slug = slug.strip('-')

    # 如果为空，使用日期作为 slug
    if not slug:
        slug = date.replace('-', '')

    return slug

def auto_category(filename, title):
    """根据标题自动分类"""
    if any(kw in title for kw in ['金融', '市场', '经济', '暴跌', '股市']):
        return '市场分析', 'red'
    elif any(kw in title for kw in ['架构', '技术', 'OpenClaw', '系统', '架构']):
        return 'AI 架构', 'blue'
    elif any(kw in title for kw in ['获客', '方法论', '商业', '客户']):
        return '方法论', 'green'
    elif any(kw in title for kw in ['学习', '笔记', '研究']):
        return '学习笔记', 'yellow'
    return '技术', 'blue'

def migrate_post(filepath, filename):
    """迁移单篇文章到新结构"""
    metadata = extract_metadata(filepath, filename)
    slug = metadata['slug']

    # 创建文章目录
    article_dir = os.path.join(POSTS_DIR, slug)
    if os.path.exists(article_dir):
        print(f"  {YELLOW}⚠ 跳过: {slug} 目录已存在{NC}")
        return False

    os.makedirs(article_dir, exist_ok=True)

    # 创建 meta.json
    meta_path = os.path.join(article_dir, 'meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump({
            "slug": metadata['slug'],
            "title": metadata['title'],
            "date": metadata['date'],
            "category": metadata['category'],
            "categoryColor": metadata['categoryColor'],
            "description": metadata['description'],
            "hasMd": metadata['hasMd'],
            "hasHtml": metadata['hasHtml'],
            "created": metadata['created'],
            "updated": metadata['updated']
        }, f, ensure_ascii=False, indent=2)

    # 复制 markdown 内容为 content.md
    content_md_path = os.path.join(article_dir, 'content.md')
    shutil.copy2(filepath, content_md_path)

    print(f"  {GREEN}✓{NC} {slug}: {metadata['title']}")
    return True

def backup_old_posts():
    """备份旧文件到 _legacy 目录"""
    if not os.path.exists(LEGACY_DIR):
        os.makedirs(LEGACY_DIR)
        print(f"{BLUE}创建备份目录: {LEGACY_DIR}{NC}")

    # 找到所有 .md 文件
    md_files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')]

    if not md_files:
        print(f"{YELLOW}没有找到需要备份的 .md 文件{NC}")
        return []

    backed_up = []
    for filename in md_files:
        src = os.path.join(POSTS_DIR, filename)
        dst = os.path.join(LEGACY_DIR, filename)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            backed_up.append(filename)

    if backed_up:
        print(f"{GREEN}✓ 已备份 {len(backed_up)} 个文件到 _legacy/{NC}")

    return md_files

def main():
    print(f"{BLUE}=== StaryBlog 文章迁移工具 ==={NC}")
    print()

    # 检查是否已经迁移过
    existing_slugs = []
    for item in os.listdir(POSTS_DIR):
        item_path = os.path.join(POSTS_DIR, item)
        if os.path.isdir(item_path) and item != '_legacy':
            meta_path = os.path.join(item_path, 'meta.json')
            if os.path.exists(meta_path):
                existing_slugs.append(item)

    if existing_slugs:
        print(f"{YELLOW}检测到已迁移的文章: {', '.join(existing_slugs)}{NC}")
        response = input("是否继续迁移剩余文章? (y/n): ")
        if response.lower() != 'y':
            print(f"{YELLOW}取消迁移{NC}")
            return

    # 备份旧文件
    print(f"{BLUE}步骤 1: 备份旧文件{NC}")
    md_files = backup_old_posts()
    print()

    if not md_files:
        print(f"{YELLOW}没有需要迁移的文件{NC}")
        return

    # 迁移文章
    print(f"{BLUE}步骤 2: 迁移文章到新结构{NC}")
    migrated = 0
    skipped = 0

    for filename in md_files:
        filepath = os.path.join(POSTS_DIR, filename)
        if migrate_post(filepath, filename):
            migrated += 1
        else:
            skipped += 1

    print()
    print(f"{GREEN}=== 迁移完成 ==={NC}")
    print(f"  成功: {migrated} 篇")
    print(f"  跳过: {skipped} 篇")
    print()

    # 显示新结构
    print(f"{BLUE}新目录结构:{NC}")
    for item in sorted(os.listdir(POSTS_DIR)):
        if os.path.isdir(os.path.join(POSTS_DIR, item)) and item != '_legacy':
            meta_path = os.path.join(POSTS_DIR, item, 'meta.json')
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                print(f"  {item}/")
                print(f"    ├── meta.json ({meta['title']})")
                content_md = os.path.join(POSTS_DIR, item, 'content.md')
                if os.path.exists(content_md):
                    print(f"    ├── content.md")
                visual_html = os.path.join(POSTS_DIR, item, 'visual.html')
                if os.path.exists(visual_html):
                    print(f"    └── visual.html")
                else:
                    print(f"    └── visual.html (未创建)")

    print()
    print(f"{YELLOW}提示: 运行 python scripts/update-posts.py 更新首页{NC}")

if __name__ == '__main__':
    main()
