#!/bin/bash
# 自动同步 claude-knowledge 到 GitHub

cd /home/liyw16/Notes/claude-knowledge || exit 1

# 有变更才提交
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    git commit -m "vault backup: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送
git push origin master 2>&1
