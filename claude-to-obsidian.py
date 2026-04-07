#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude输出到Obsidian的快速导入工具

功能：
- 从粘贴板读取Claude输出
- 自动解析和分类内容（关键词计分算法）
- 生成Obsidian格式的Markdown笔记
- 自动添加元数据和标签
- 保存到指定文件夹（安全文件名处理）
- 可选：自动Git提交

使用方法：
    python claude-to-obsidian.py
"""

import hashlib
import os
import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

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

    # 内容分类规则（关键词 + 权重）
    CATEGORIES: Dict[str, dict] = {
        "代码": {
            # 代码块标记权重高，单个代码块足以判定
            "keywords": {"```": 3, "import ": 2, "def ": 2, "class ": 2,
                         "function ": 2, "const ": 1, "let ": 1, "var ": 1,
                         "return ": 1, "if (": 1, "for (": 1},
            "path": "10-claude-outputs/代码片段"
        },
        "理论概念": {
            "keywords": {"解释": 2, "什么是": 3, "原理": 2, "理解": 1,
                         "背景": 1, "基础": 2, "介绍": 2, "概念": 3,
                         "定义": 2, "区别": 1},
            "path": "10-claude-outputs/理论概念"
        },
        "工具库": {
            "keywords": {"库": 2, "工具": 2, "框架": 2, "包": 1,
                         "package": 2, "library": 3, "framework": 3,
                         "npm": 3, "pip": 3, "安装": 1, "使用方法": 1},
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
        """从内容中提取标题，优先取一级标题"""
        lines = content.split('\n')

        # 优先匹配一级标题（# 开头，且 # 后无更多 #）
        for line in lines:
            stripped = line.strip()
            if re.match(r'^#\s+\S', stripped):
                title = stripped.lstrip('#').strip()
                return title[:80]

        # 退而取任意级别标题
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                title = stripped.lstrip('#').strip()
                if title:
                    return title[:80]

        # 最后用第一个非空行
        for line in lines:
            stripped = line.strip()
            if stripped:
                return stripped[:80]

        return "未命名笔记"

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
        """自动分类内容（关键词计分，取得分最高的分类）"""
        content_lower = content.lower()
        scores: Dict[str, int] = {}

        for category, config in self.CATEGORIES.items():
            score = sum(
                weight
                for kw, weight in config["keywords"].items()
                if kw in content_lower
            )
            if score > 0:
                scores[category] = score

        if not scores:
            return "其他"

        # 取得分最高的分类；同分时按 CATEGORIES 的声明顺序（稳定）
        return max(scores, key=lambda c: scores[c])

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

    # 文件名最大字节数（Linux/macOS 255 字节，留余量）
    MAX_FILENAME_BYTES = 200

    def _safe_filename(self, title: str) -> str:
        """
        将标题转换为安全的文件名。

        处理规则：
        1. 去除 Windows/Linux 保留字符
        2. 去除 . 开头（避免隐藏文件）
        3. 按字节截断（中文 3 字节/字符，避免超限）
        4. 空字符串回退到时间戳
        """
        # 去除路径分隔符和文件系统保留字符
        safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title)
        # 去除首尾空白和点，防止 .hidden 或 trailing dot
        safe = safe.strip('. ')

        # 按字节截断（中文等多字节字符不能简单按字数截）
        encoded = safe.encode('utf-8')
        if len(encoded) > self.MAX_FILENAME_BYTES:
            # 从截断点向前找合法的 UTF-8 边界
            truncated = encoded[:self.MAX_FILENAME_BYTES]
            safe = truncated.decode('utf-8', errors='ignore').rstrip()

        # 最终为空时用时间戳作为 fallback
        if not safe:
            safe = datetime.now().strftime("笔记-%Y%m%d-%H%M%S")

        return safe

    def save_note(self, title: str, markdown: str, category: str) -> Path:
        """保存笔记文件"""
        if category in self.CATEGORIES:
            folder = self.VAULT_ROOT / self.CATEGORIES[category]["path"]
        else:
            folder = self.VAULT_ROOT / "10-claude-outputs/其他"

        folder.mkdir(parents=True, exist_ok=True)

        # 使用安全文件名生成器
        safe_title = self._safe_filename(title)
        filename = f"{safe_title}.md"

        # 处理重名：后缀递增
        filepath = folder / filename
        counter = 1
        while filepath.exists():
            filename = f"{safe_title}_{counter}.md"
            filepath = folder / filename
            counter += 1

        filepath.write_text(markdown, encoding='utf-8')
        return filepath

    def git_commit(self, filepath: Path, title: str, auto_commit: bool = False) -> bool:
        """提交到Git（提交前验证Git用户配置，避免中间状态）"""
        if not auto_commit:
            return False

        try:
            os.chdir(self.VAULT_ROOT)

            # 验证 Git 配置，避免提交失败后留下已暂存但未提交的中间状态
            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True, text=True
            )
            if not result.stdout.strip():
                print("⚠️  Git user.name 未配置，跳过提交")
                print("   请运行：git config user.name '你的名字'")
                return False

            subprocess.run(
                ["git", "add", str(filepath.relative_to(self.VAULT_ROOT))],
                check=True
            )
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
            print("📋 Claude输出导入工具 v1.1")
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
