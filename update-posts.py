#!/usr/bin/env python3
"""自动更新首页文章列表"""

import os
import re
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

# 从 markdown 文件提取元数据
def extract_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取标题（第一个 # 开头的行）
    title_match = re.search(r'^#\s+([^\n]+)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(filepath)

    # 提取描述（第一段非空、非#、非表格的内容）
    lines = content.split('\n')
    description = ""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '|' not in stripped and not re.match(r'^\d', stripped):
            description = stripped[:120]
            break

    return title, description

# 从文件名提取日期
def extract_date(filename):
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    # 使用文件修改时间
    mtime = os.path.getmtime(os.path.join(POSTS_DIR, filename))
    return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

# 自动分类
def auto_category(filename, title):
    if any(kw in title for kw in ['金融', '市场', '经济']):
        return '市场分析', 'red'
    elif any(kw in title for kw in ['架构', '技术', 'OpenClaw']):
        return 'AI 架构', 'blue'
    elif any(kw in title for kw in ['获客', '方法论', '商业']):
        return '方法论', 'green'
    elif any(kw in title for kw in ['学习', '笔记']):
        return '学习笔记', 'yellow'
    return '技术', 'blue'

# 收集文章
print(f"{YELLOW}正在扫描文章目录...{NC}")
articles = []

for filename in os.listdir(POSTS_DIR):
    if filename.endswith('.md'):
        filepath = os.path.join(POSTS_DIR, filename)
        title, description = extract_metadata(filepath)
        date = extract_date(filename)
        category, color = auto_category(filename, title)
        articles.append((date, filename, title, description, category, color))

# 按日期排序
articles.sort(key=lambda x: x[0], reverse=True)

print(f"{GREEN}找到 {len(articles)} 篇文章{NC}")
print()

# 生成卡片 HTML
def get_color_class(color):
    color_map = {
        'red': 'bg-red-100 text-red-800',
        'blue': 'bg-blue-100 text-blue-800',
        'green': 'bg-green-100 text-green-800',
        'yellow': 'bg-yellow-100 text-yellow-800',
        'purple': 'bg-purple-100 text-purple-800',
    }
    return color_map.get(color, 'bg-gray-100 text-gray-800')

cards_html = []
for date, filename, title, description, category, color in articles:
    bg_class = get_color_class(color)
    card = f'''            <a href="/post.html?post={filename}" class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow cursor-pointer">
                <div class="p-6">
                    <div class="flex items-center text-sm text-gray-500 mb-2">
                        <span>{date}</span>
                        <span class="mx-2">•</span>
                        <span class="{bg_class} px-2 py-1 rounded">{category}</span>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 mb-3">{title}</h3>
                    <p class="text-gray-600 mb-4">
                        {description}
                    </p>
                    <div class="flex items-center text-blue-600">
                        <span>阅读更多</span>
                        <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </div>
                </div>
            </a>'''
    cards_html.append(card)

# 更新 index.html
print(f"{YELLOW}正在更新 index.html...{NC}")

with open(INDEX_HTML, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换文章卡片区域
pattern = r'(<div class="grid md:grid-cols-2 gap-6">)(.*?)(</div>\s*</div>\s*\n\s*(<!-- About Section -->))'
replacement = f'\\1\n' + '\n'.join(cards_html) + '\n        </div>\n    </div>\n\n    <!-- About Section -->'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

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
