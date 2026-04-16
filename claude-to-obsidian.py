#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude输出到Obsidian的快速导入工具

功能：
- 从粘贴板读取Claude输出（优先读取HTML富文本，用markitdown精确转换）
- 自动解析和分类内容（关键词计分算法）
- 生成Obsidian格式的Markdown笔记
- 自动添加元数据和标签
- 保存到指定文件夹（安全文件名处理）
- 可选：自动Git提交

使用方法：
    python claude-to-obsidian.py
"""

import hashlib
import io
import os
import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def restore_markdown(text: str) -> str:
    """
    将 Claude Code 终端渲染的纯文本还原为 Markdown 格式。

    终端渲染规律：
    - 标题（## xxx）：缩进的短文字行，前后有空行，无代码语法
    - 代码块：缩进的多行文字，含代码语法特征（#、|、echo、$等）
    - ASCII 表格：┌─┬─┐ 样式
    - 列表（- item）：原样保留
    - 加粗（**text**）：原样保留
    - ● 符号：终端列表标记，还原为 -
    """
    # 先清理终端特有的 ● 列表标记
    text = re.sub(r'^●\s+', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*●\s+', '- ', text, flags=re.MULTILINE)

    lines = text.splitlines()
    result: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 检测 ASCII 表格（┌ 开头，允许有缩进）→ 转换为 Markdown 表格
        if line.lstrip().startswith('┌'):
            table_lines, consumed = _parse_ascii_table(lines, i)
            result.extend(table_lines)
            i += consumed
            continue

        # 检测缩进块：以2+空格开头，非列表项
        if re.match(r'^  \S', line) and not re.match(r'^  [-*+\d]', line):
            block_lines, consumed = _collect_indented_block(lines, i)
            converted = _convert_indented_block(block_lines)
            result.extend(converted)
            i += consumed
            continue

        result.append(line)
        i += 1

    return '\n'.join(result)


def _collect_indented_block(lines: List[str], start: int) -> Tuple[List[str], int]:
    """收集从 start 开始的连续缩进块（允许内部空行）"""
    block = []
    i = start

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            # 空行：向前看，若后续还有缩进行则保留
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and re.match(r'^  ', lines[j]):
                block.append('')
                i += 1
                continue
            else:
                break

        # 非缩进行 → 结束
        if not re.match(r'^  ', line):
            break

        block.append(line)
        i += 1

    # 去掉尾部空行
    while block and not block[-1].strip():
        block.pop()

    return block, i - start


def _is_code_line(line: str) -> bool:
    """判断一行是否含有代码特征"""
    stripped = line.strip()
    code_patterns = [
        r'^#',                          # 注释
        r'[|&;]',                       # 管道/分隔符
        r'\$\w+|\$\{',                  # shell 变量
        r"echo |curl |grep |awk |sed |cat |ls |cd |git |docker ", # 常用命令
        r"jq |python |pip |npm |go |cargo ",  # 工具命令
        r'^\w+\s*[=({]',               # 赋值/函数调用
        r'["\'].*["\']',               # 引号字符串
        r'^\s*\w+\(.*\)',              # 函数调用
        r'<\w+>|</\w+>',              # HTML 标签
        r'=>|->|\.\.\.',               # 箭头/省略号
        r'^\s*\w+:\s*\w',             # key: value
        r'\.\w{2,5}(\s|$)',           # 含文件扩展名（.json .yaml .txt 等）
        r'^(jd|ffmpeg|kubectl|helm|terraform|ansible|vault|aws|gcloud|az|gh|wget|tar|zip|unzip|chmod|chown|mkdir|rm|cp|mv)\s', # 常见 CLI 工具
        r'-{1,2}[a-zA-Z][\w-]*',      # 命令行选项（-f / --flag）
    ]
    return any(re.search(p, stripped) for p in code_patterns)


def _convert_indented_block(block: List[str]) -> List[str]:
    """
    将缩进块转换：
    - 纯文字短行（无代码特征）→ Markdown 标题
    - 含代码特征的多行 → 代码块
    - ASCII 表格行 → Markdown 表格
    """
    if not block:
        return []

    result: List[str] = []
    i = 0

    while i < len(block):
        line = block[i]
        stripped = line.strip()

        if not stripped:
            result.append('')
            i += 1
            continue

        # ASCII 表格
        if stripped.startswith('┌'):
            table_lines, consumed = _parse_ascii_table(
                [l.strip() for l in block], i  # 去缩进后传入
            )
            result.extend(table_lines)
            i += consumed
            continue

        # 判断这一行是否像"标题"：单行、无代码特征、长度适中
        is_heading_candidate = (
            len(stripped) < 60
            and not _is_code_line(line)
            and not stripped.startswith('-')
            and not stripped.startswith('```')
        )

        if is_heading_candidate:
            result.append(f'## {stripped}')
            i += 1
            continue

        # 否则，收集连续的代码行组成代码块
        code_segment: List[str] = []
        while i < len(block):
            l = block[i]
            s = l.strip()
            if not s:
                j = i + 1
                while j < len(block) and not block[j].strip():
                    j += 1
                if j < len(block) and _is_code_line(block[j]):
                    code_segment.append('')
                    i += 1
                    continue
                else:
                    break
            # 遇到标题候选行或表格 → 停止
            if s.startswith('┌'):
                break
            if len(s) < 60 and not _is_code_line(l) and not s.startswith('-'):
                break
            code_segment.append(l)
            i += 1

        # 去掉公共缩进
        non_empty = [l for l in code_segment if l.strip()]
        if non_empty:
            min_indent = min(len(l) - len(l.lstrip()) for l in non_empty)
            code_segment = [l[min_indent:] if l.strip() else '' for l in code_segment]

        # 去尾部空行
        while code_segment and not code_segment[-1].strip():
            code_segment.pop()

        if code_segment:
            lang = _guess_language(code_segment)
            result.append(f'```{lang}')
            result.extend(code_segment)
            result.append('```')

    return result


def _guess_language(code_lines: List[str]) -> str:
    """根据代码内容猜测语言"""
    code = '\n'.join(code_lines).lower()
    if re.search(r'\bjq\b|select\(|\.\[\]|jq \'', code):
        return 'bash'
    if re.search(r'^\s*(def |import |from .* import|class )', code, re.M):
        return 'python'
    if re.search(r'^\s*(function |const |let |var |=>)', code, re.M):
        return 'javascript'
    if re.search(r'^\s*(package |func |import ")', code, re.M):
        return 'go'
    if re.search(r'^\s*(#include|int main|std::)', code, re.M):
        return 'cpp'
    if re.search(r'\b(curl|echo|grep|awk|sed|bash|sh|apt|git|docker|kubectl)\b', code):
        return 'bash'
    if re.search(r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE)\b', code, re.M | re.I):
        return 'sql'
    return ''


def _parse_ascii_table(lines: List[str], start: int) -> Tuple[List[str], int]:
    """
    将 ASCII 框线表格转换为 Markdown 表格。
    支持格式：
      ┌───┬───┐
      │ A │ B │   ← 表头行
      ├───┼───┤   ← 第一个 ├ 表示表头结束
      │ a │ b │
      ├───┼───┤   ← 后续 ├ 忽略（Markdown 表格无需内部分隔）
      └───┴───┘
    """
    i = start
    data_rows: List[List[str]] = []
    header_separator_inserted = False

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            break
        # 数据行
        if line.startswith('│'):
            cells = [c.strip() for c in line.strip('│').split('│')]
            data_rows.append(cells)
        # 第一个 ├ → 在此处插入表头分隔（只插一次）
        elif line.startswith('├') and not header_separator_inserted:
            if data_rows:
                data_rows.append(None)  # type: ignore  # 占位符，后续转为 ---
                header_separator_inserted = True
        # ┌ └ 及后续 ├ → 跳过
        elif re.match(r'^[┌└├]', line):
            pass
        else:
            break
        i += 1

    if not data_rows:
        return [lines[start]], 1

    # 构建 Markdown 表格
    real_rows = [r for r in data_rows if r is not None]
    cols = len(real_rows[0]) if real_rows else 1
    separator = '| ' + ' | '.join(['---'] * cols) + ' |'

    md_rows: List[str] = []
    for row in data_rows:
        if row is None:
            md_rows.append(separator)
        else:
            md_rows.append('| ' + ' | '.join(row) + ' |')

    # 若没有 ├ 分隔行，默认在第一行后插入
    if not header_separator_inserted and len(md_rows) >= 1:
        md_rows.insert(1, separator)

    return md_rows, i - start

try:
    import pyperclip
except ImportError:
    print("错误：需要安装 pyperclip")
    print("请运行：pip install pyperclip")
    sys.exit(1)

try:
    from markitdown import MarkItDown, StreamInfo
    _MARKITDOWN_AVAILABLE = True
except ImportError:
    _MARKITDOWN_AVAILABLE = False


def _get_clipboard_html() -> Optional[bytes]:
    """
    尝试通过 xclip 获取剪贴板的 HTML 富文本格式内容。
    仅在 Linux/X11 环境可用；失败时返回 None。
    """
    try:
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "text/html", "-o"],
            capture_output=True,
            timeout=3,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def convert_html_to_markdown(html_bytes: bytes) -> Optional[str]:
    """
    使用 markitdown 将 HTML 字节流精确转换为 Markdown。
    返回转换后的字符串；失败时返回 None。
    """
    if not _MARKITDOWN_AVAILABLE:
        return None
    try:
        md_converter = MarkItDown()
        result = md_converter.convert(
            io.BytesIO(html_bytes),
            stream_info=StreamInfo(mimetype="text/html", charset="utf-8"),
        )
        text = result.text_content or ""
        return text.strip() if text.strip() else None
    except Exception:
        return None


class ClaudeToObsidian:
    """Claude输出转Obsidian笔记转换器"""

    # 知识库根目录
    VAULT_ROOT = Path.home() / "Notes" / "claude-knowledge"

    # 内容分类规则（关键词 + 权重）
    CATEGORIES: Dict[str, dict] = {
        "代码": {
            # 代码块权重降低，避免压制其他分类
            "keywords": {"```": 1, "import ": 2, "def ": 2, "class ": 2,
                         "function ": 2, "const ": 1, "let ": 1, "var ": 1,
                         "return ": 1, "if (": 1, "for (": 1},
            "path": "claude-outputs/代码片段"
        },
        "理论概念": {
            "keywords": {"解释": 2, "什么是": 3, "原理": 2, "理解": 1,
                         "背景": 1, "基础": 2, "介绍": 2, "概念": 3,
                         "定义": 2, "区别": 1},
            "path": "claude-outputs/理论概念"
        },
        "工具库": {
            "keywords": {"库": 2, "工具": 2, "框架": 2, "包": 1,
                         "package": 2, "library": 3, "framework": 3,
                         "npm": 3, "pip": 3, "安装": 1, "使用方法": 3,
                         "如何使用": 3, "用法": 2, "命令": 2, "教程": 2,
                         "参数": 1, "选项": 1, "示例": 1},
            "path": "claude-outputs/工具库"
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

    def get_clipboard(self) -> Tuple[str, str]:
        """
        从剪贴板读取内容，返回 (markdown文本, 来源描述)。

        优先级：
        1. HTML 富文本（Claude 网页端复制）→ markitdown 精确转换
        2. 纯文本（Claude Code 终端复制）→ restore_markdown 启发式还原
        """
        # --- 尝试读取 HTML 富文本 ---
        html_bytes = _get_clipboard_html()
        if html_bytes:
            md_text = convert_html_to_markdown(html_bytes)
            if md_text:
                return md_text, "HTML（markitdown转换）"

        # --- 回退：读取纯文本 ---
        try:
            content = pyperclip.paste()
            if not content.strip():
                raise ValueError("粘贴板为空")
            return content, "纯文本"
        except Exception as e:
            raise ValueError(f"读取粘贴板失败：{e}")

    def extract_title(self, content: str) -> str:
        """从内容中提取标题，优先取一级标题，跳过代码块内的行"""
        lines = content.split('\n')

        # 过滤掉代码块内的行，避免把代码注释当成标题
        non_code_lines: List[str] = []
        in_code_block = False
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if not in_code_block:
                non_code_lines.append(line)

        # 优先匹配一级标题（# 开头，且 # 后无更多 #）
        for line in non_code_lines:
            stripped = line.strip()
            if re.match(r'^#\s+\S', stripped):
                title = stripped.lstrip('#').strip()
                return title[:80]

        # 次选：代码块外第一个普通文字行（不以 # - * 等特殊符号开头）
        plain_skip = [
            r'^#',        # Markdown 标题 / 代码注释 / shebang
            r'^[-*+]',    # 列表项
            r'^>',        # 引用块
            r'^`',        # 行内代码
            r'^import ',
            r'^from ',
            r'^[-=]{3,}', # 分隔线
        ]
        for line in non_code_lines:
            stripped = line.strip()
            if stripped and not any(re.match(p, stripped) for p in plain_skip):
                return stripped[:80]

        # 最后回退到任意级别的 Markdown 标题（## ### 等）
        for line in non_code_lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                title = stripped.lstrip('#').strip()
                if title:
                    return title[:80]

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

    # 标题含这些词时强制归入工具库
    TOOL_TITLE_PATTERNS = [
        r'使用指南', r'如何使用', r'命令.*使用', r'使用.*命令',
        r'.*命令$', r'使用教程', r'快速上手', r'入门指南',
    ]

    def classify_content(self, content: str) -> str:
        """自动分类内容（关键词计分，取得分最高的分类）"""
        # 优先规则：标题含"使用指南/命令"类词语 → 强制归入工具库
        title = self.extract_title(content)
        for pattern in self.TOOL_TITLE_PATTERNS:
            if re.search(pattern, title):
                return "工具库"

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
        frontmatter = f"""# {title}

> 导入自 Claude AI · {now.strftime("%Y-%m-%d")} · {category}

{content}

---
*标签：{' '.join(f"#{tag}" for tag in tags)}*
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
            folder = self.VAULT_ROOT / "claude-outputs/其他"

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
            print("📋 Claude输出导入工具 v1.2")
            print("-" * 50)

            # 1. 读取粘贴板
            print("📥 从粘贴板读取内容...")
            content, source = self.get_clipboard()
            print(f"✓ 读取成功 ({len(content)} 字符) [{source}]")

            # 1.5 格式还原
            #   - HTML 路径：markitdown 已输出标准 Markdown，无需再处理
            #   - 纯文本路径：启发式还原终端渲染格式
            if "纯文本" in source:
                print("\n🔄 还原 Markdown 格式（纯文本模式）...")
                content = restore_markdown(content)
            else:
                print(f"\n✅ 已通过 markitdown 精确转换，跳过启发式还原")

            # 2. 提取标题
            print("\n📝 提取标题...")
            title = self.extract_title(content)
            print(f"✓ 标题：{title}")

            # 去掉 content 开头与标题重复的行
            lines = content.splitlines()
            while lines and lines[0].strip().lstrip('#').strip() == title:
                lines.pop(0)
            content = '\n'.join(lines).lstrip('\n')

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
