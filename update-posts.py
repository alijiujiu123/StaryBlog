#!/usr/bin/env python3
"""
自动更新首页文章列表 - 支持新的 posts/<slug>/ 结构
"""

import os
import re
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(SCRIPT_DIR, "posts")
INDEX_HTML = os.path.join(SCRIPT_DIR, "index.html")

# 颜色代码
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

print(f"{BLUE}=== StaryBlog 自动更新工具 ==={NC}")
print()

def get_color_class(color):
    """获取 Tailwind CSS 颜色类"""
    color_map = {
        'red': 'bg-red-100 text-red-800',
        'blue': 'bg-blue-100 text-blue-800',
        'green': 'bg-green-100 text-green-800',
        'yellow': 'bg-yellow-100 text-yellow-800',
        'purple': 'bg-purple-100 text-purple-800',
        'pink': 'bg-pink-100 text-pink-800',
        'indigo': 'bg-indigo-100 text-indigo-800',
        'gray': 'bg-gray-100 text-gray-800',
    }
    return color_map.get(color, 'bg-gray-100 text-gray-800')

def auto_category(filename, title):
    """根据标题自动分类（用于旧文件）"""
    if any(kw in title for kw in ['金融', '市场', '经济']):
        return '市场分析', 'red'
    elif any(kw in title for kw in ['架构', '技术', 'OpenClaw']):
        return 'AI 架构', 'blue'
    elif any(kw in title for kw in ['获客', '方法论', '商业']):
        return '方法论', 'green'
    elif any(kw in title for kw in ['学习', '笔记']):
        return '学习笔记', 'yellow'
    return '技术', 'blue'

def extract_metadata_from_md(filepath):
    """从 markdown 文件提取元数据（用于旧文件）"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取标题
    title_match = re.search(r'^#\s+([^\n]+)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(filepath)

    # 提取描述
    lines = content.split('\n')
    description = ""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '|' not in stripped and not re.match(r'^\d', stripped):
            description = stripped[:120]
            break

    return title, description

def extract_date(filename):
    """从文件名提取日期"""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    mtime = os.path.getmtime(os.path.join(POSTS_DIR, filename))
    return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

def load_articles_from_new_structure():
    """从新的 <slug>/ 结构加载文章"""
    articles = []

    for item in os.listdir(POSTS_DIR):
        item_path = os.path.join(POSTS_DIR, item)

        # 跳过非目录和 _legacy 目录
        if not os.path.isdir(item_path) or item == '_legacy' or item.startswith('.'):
            continue

        # 检查 meta.json
        meta_path = os.path.join(item_path, 'meta.json')
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)

                articles.append({
                    'slug': meta.get('slug', item),
                    'title': meta.get('title', ''),
                    'date': meta.get('date', ''),
                    'category': meta.get('category', '技术'),
                    'color': meta.get('categoryColor', 'blue'),
                    'description': meta.get('description', ''),
                    'hasMd': meta.get('hasMd', True),
                    'hasHtml': meta.get('hasHtml', False),
                    'isNew': True
                })
            except json.JSONDecodeError:
                print(f"{YELLOW}警告: {item}/meta.json 格式错误{NC}")

    return articles

def load_articles_from_old_structure():
    """从旧的 *.md 结构加载文章"""
    articles = []

    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith('.md') or filename.startswith('.'):
            continue

        filepath = os.path.join(POSTS_DIR, filename)
        title, description = extract_metadata_from_md(filepath)
        date = extract_date(filename)
        category, color = auto_category(filename, title)

        articles.append({
            'slug': filename,  # 旧格式使用文件名作为 slug
            'title': title,
            'date': date,
            'category': category,
            'color': color,
            'description': description,
            'hasMd': True,
            'hasHtml': False,
            'isNew': False
        })

    return articles

def generate_card_html(article):
    """生成文章卡片 HTML"""
    bg_class = get_color_class(article['color'])

    # 新结构使用 ?slug= 参数
    if article['isNew']:
        href = f"/post.html?slug={article['slug']}"
    else:
        href = f"/post.html?post={article['slug']}"

    # 添加模式标签（如果有 HTML 模式）
    mode_badge = ""
    if article['hasMd'] and article['hasHtml']:
        mode_badge = '<span class="ml-2 text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">双模式</span>'
    elif article['hasHtml']:
        mode_badge = '<span class="ml-2 text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded">可视化</span>'

    card = f'''            <a href="{href}" class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow cursor-pointer">
                <div class="p-6">
                    <div class="flex items-center text-sm text-gray-500 mb-2">
                        <span>{article['date']}</span>
                        <span class="mx-2">•</span>
                        <span class="{bg_class} px-2 py-1 rounded">{article['category']}</span>
                        {mode_badge}
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 mb-3">{article['title']}</h3>
                    <p class="text-gray-600 mb-4">
                        {article['description']}
                    </p>
                    <div class="flex items-center text-blue-600">
                        <span>阅读更多</span>
                        <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </div>
                </div>
            </a>'''

    return card

# 收集文章
print(f"{YELLOW}正在扫描文章目录...{NC}")

# 优先加载新结构，回退到旧结构
articles = load_articles_from_new_structure()

if not articles:
    print(f"{YELLOW}未找到新结构文章，尝试加载旧格式...{NC}")
    articles = load_articles_from_old_structure()

# 按日期排序
articles.sort(key=lambda x: x['date'], reverse=True)

print(f"{GREEN}找到 {len(articles)} 篇文章{NC}")
if articles:
    new_count = sum(1 for a in articles if a['isNew'])
    old_count = len(articles) - new_count
    if new_count:
        print(f"  新格式: {new_count} 篇")
    if old_count:
        print(f"  旧格式: {old_count} 篇 (建议运行 python scripts/migrate.py 迁移)")
print()

# 生成卡片 HTML
print(f"{YELLOW}正在生成文章卡片...{NC}")
cards_html = [generate_card_html(article) for article in articles]

# 更新 index.html
print(f"{YELLOW}正在更新 index.html...{NC}")

with open(INDEX_HTML, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换文章卡片区域
pattern = r'(<div class="grid md:grid-cols-2 gap-6">)(.*?)(</div>\s*</div>\s*\n\s*(<!-- About Section -->))'
replacement = f'\\1\n' + '\n'.join(cards_html) + '\n        </div>\n    </div>\n\n    <!-- About Section -->'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 检查是否成功替换
if new_content == content:
    print(f"{YELLOW}警告: 未找到文章卡片区域，可能 index.html 结构已改变{NC}")
else:
    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"{GREEN}✓ 首页已更新{NC}")

print()

# 询问是否部署
response = input("是否立即部署到服务器? (y/n): ")
if response.lower() == 'y':
    os.system(f"cd {SCRIPT_DIR} && ./deploy.sh")
else:
    print(f"{YELLOW}跳过部署。稍后可运行 ./deploy.sh 手动部署{NC}")
