#!/bin/sh

# 设置路径环境变量，确保脚本能找到 python3 和 git
export PATH="/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
# 指定 SSH 密钥以通过 GitHub 认证
export GIT_SSH_COMMAND='dbclient -i /root/.ssh/id_ed25519'

# 进入仓库目录
cd /root/Cloudflare-SpeedTest-BestIP-For-iStoreOS

# 1. 运行前先拉取远程更新，防止推送冲突
git pull --rebase origin main

# 2. 运行测速脚本
# 注意：请确保脚本文件名确实为 istoreos_cf_speedtest.py
python3 istoreos_cf_speedtest.py

# 3. 检查是否有文件更新并推送到 GitHub
if [ -n "$(git status --porcelain)" ]; then
    git add best_ip.txt result.csv
    git commit -m "chore: istoreos auto update $(date +'%Y-%m-%d %H:%M')"
    git push origin main
    echo "Update successful: $(date)"
else
    echo "No changes detected, skip push: $(date)"
fi