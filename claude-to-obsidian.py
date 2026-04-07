#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude输出到Obsidian的快速导入工具

功能：
- 从粘贴板读取Claude输出
- 自动解析和分类内容
- 生成Obsidian格式的Markdown笔记
- 自动添加元数据和标签
- 保存到指定文件夹
- 可选：自动Git提交

使用方法：
    python claude-to-obsidian.py
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

try:
    import pyperclip
except ImportError:
    print("错误：需要安装 pyperclip")
    print("请运行：pip install pyperclip")
    sys.exit(1)


class ClaudeToObsidian:
    """Claude输出转Obsidian笔记转换器"""

    # 知识库根目录
    VAULT_ROOT = Path.home() / "Notes" / "claude-knowledge"

    # 内容分类规则
    CATEGORIES = {
        "代码": {
            "keywords": ["```", "import ", "def ", "class ", "function ", "const ", "let ", "var "],
            "path": "10-claude-outputs/代码片段"
        },
        "理论概念": {
            "keywords": ["解释", "什么是", "原理", "理解", "背景", "基础", "介绍"],
            "path": "10-claude-outputs/理论概念"
        },
        "工具库": {
            "keywords": ["库", "工具", "框架", "包", "package", "library", "framework", "npm", "pip"],
            "path": "10-claude-outputs/工具库"
        },
    }

    # 语言识别模式
    LANGUAGE_PATTERNS = {
        "Python": ["python", "py", ".py", "import ", "def "],
        "JavaScript": ["javascript", "js", ".js", "function ", "const ", "let ", "var "],
        "TypeScript": ["typescript", "ts", ".ts"],
        "Go": ["go", "golang", ".go", "package main"],
        "Rust": ["rust", "rs", ".rs", "fn "],
        "Java": ["java", ".java", "public class"],
        "C++": ["cpp", "c++", ".cpp", "#include"],
        "SQL": ["sql", "SELECT ", "INSERT ", "UPDATE"],
        "HTML": ["html", ".html", "<html>", "<div>"],
        "CSS": ["css", ".css", "selector {"],
    }

    def __init__(self):
        """初始化转换器"""
        if not self.VAULT_ROOT.exists():
            raise ValueError(f"知识库目录不存在：{self.VAULT_ROOT}")

    def get_clipboard(self) -> str:
        """从粘贴板读取内容"""
        try:
            content = pyperclip.paste()
            if not content.strip():
                raise ValueError("粘贴板为空")
            return content
        except Exception as e:
            raise ValueError(f"读取粘贴板失败：{e}")

    def extract_title(self, content: str) -> str:
        """从内容中提取标题"""
        # 优先使用第一个#标题
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                title = line.strip().lstrip('#').strip()
                return title[:100]  # 限制长度

        # 否则使用第一行
        first_line = lines[0].strip()[:100]
        return first_line if first_line else "未命名笔记"

    def extract_code_blocks(self, content: str) -> List[Tuple[str, str]]:
        """提取代码块（返回语言和代码）"""
        pattern = r'```(\w*)\n(.*?)\n```'
        blocks = re.findall(pattern, content, re.DOTALL)
        return blocks

    def detect_language(self, code: str) -> str:
        """检测代码所用语言"""
        code_lower = code.lower()

        for lang, keywords in self.LANGUAGE_PATTERNS.items():
            if any(kw in code_lower for kw in keywords):
                return lang

        return "code"

    def extract_links(self, content: str) -> List[str]:
        """提取URL链接"""
        url_pattern = r'https?://[^\s\)\]]*'
        return re.findall(url_pattern, content)

    def classify_content(self, content: str) -> str:
        """自动分类内容"""
        content_lower = content.lower()

        for category, config in self.CATEGORIES.items():
            if any(kw in content_lower for kw in config["keywords"]):
                return category

        return "其他"

    def extract_tags(self, content: str, category: str) -> List[str]:
        """提取或推断标签"""
        tags = ["claude-output", "待整理"]

        # 添加分类标签
        if category in self.CATEGORIES:
            tags.append(category)

        # 检测语言
        code_blocks = self.extract_code_blocks(content)
        if code_blocks:
            languages = set()
            for lang, code in code_blocks:
                if lang:
                    languages.add(lang)
                else:
                    detected = self.detect_language(code)
                    if detected != "code":
                        languages.add(detected)

            tags.extend(list(languages)[:3])  # 最多3个语言标签

        # 检测其他关键词
        if "问题" in content or "?" in content:
            tags.append("问题解答")
        elif "最佳实践" in content:
            tags.append("最佳实践")

        return list(set(tags))  # 去重

    def generate_markdown(self,
                          title: str,
                          content: str,
                          tags: List[str],
                          category: str) -> str:
        """生成Obsidian格式的Markdown"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M")

        # Frontmatter
        frontmatter = f"""---
date: {date_str}
tags: {json.dumps(tags)}
source: Claude AI
category: {category}
---

# {title}

## 📝 来源信息
- **来源**：Claude AI
- **导入日期**：{now.strftime("%Y-%m-%d")}
- **分类**：{category}

## 💡 核心内容

{content}

## 🏷️ 标签
{' '.join(f"#{tag}" for tag in tags)}

---

**创建时间**：{date_str}
**状态**：待整理
"""
        return frontmatter

    def save_note(self, title: str, markdown: str, category: str) -> Path:
        """保存笔记文件"""
        if category in self.CATEGORIES:
            folder = self.VAULT_ROOT / self.CATEGORIES[category]["path"]
        else:
            folder = self.VAULT_ROOT / "10-claude-outputs/其他"

        folder.mkdir(parents=True, exist_ok=True)

        # 生成安全的文件名
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = f"{safe_title}.md"

        # 处理重名
        filepath = folder / filename
        counter = 1
        while filepath.exists():
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{counter}{ext}"
            filepath = folder / filename
            counter += 1

        filepath.write_text(markdown, encoding='utf-8')
        return filepath

    def git_commit(self, filepath: Path, title: str, auto_commit: bool = False) -> bool:
        """提交到Git"""
        if not auto_commit:
            return False

        try:
            os.chdir(self.VAULT_ROOT)
            subprocess.run(["git", "add", str(filepath.relative_to(self.VAULT_ROOT))], check=True)
            subprocess.run([
                "git", "commit", "-m",
                f"feat: 添加笔记 - {title[:50]}\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
            ], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git提交失败：{e}")
            return False

    def run(self, auto_commit: bool = False) -> bool:
        """执行完整的转换流程"""
        try:
            print("📋 Claude输出导入工具 v1.0")
            print("-" * 50)

            # 1. 读取粘贴板
            print("📥 从粘贴板读取内容...")
            content = self.get_clipboard()
            print(f"✓ 读取成功 ({len(content)} 字符)")

            # 2. 提取标题
            print("\n📝 提取标题...")
            title = self.extract_title(content)
            print(f"✓ 标题：{title}")

            # 3. 分类
            print("\n🏷️  分类内容...")
            category = self.classify_content(content)
            print(f"✓ 分类：{category}")

            # 4. 提取标签
            print("\n🔖 提取标签...")
            tags = self.extract_tags(content, category)
            print(f"✓ 标签：{', '.join(tags)}")

            # 5. 生成Markdown
            print("\n✍️  生成Markdown...")
            markdown = self.generate_markdown(title, content, tags, category)

            # 6. 保存文件
            print("\n💾 保存笔记...")
            filepath = self.save_note(title, markdown, category)
            print(f"✓ 保存成功：{filepath.relative_to(self.VAULT_ROOT)}")

            # 7. Git提交（可选）
            if auto_commit:
                print("\n📤 提交到Git...")
                if self.git_commit(filepath, title, auto_commit=True):
                    print("✓ Git提交成功")
                else:
                    print("⚠️  Git提交失败，文件已保存")

            print("\n" + "=" * 50)
            print("✅ 导入完成！")
            print(f"📍 笔记已保存到：{filepath.relative_to(self.VAULT_ROOT)}")
            print("💡 在Obsidian中刷新即可看到新笔记")
            print("=" * 50)

            return True

        except Exception as e:
            print(f"\n❌ 错误：{e}")
            return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Claude输出到Obsidian快速导入工具")
    parser.add_argument("--auto-commit", "-a", action="store_true",
                        help="自动提交到Git")

    args = parser.parse_args()

    try:
        converter = ClaudeToObsidian()
        success = converter.run(auto_commit=args.auto_commit)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
